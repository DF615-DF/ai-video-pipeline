// speak MCP server — 让 Codex 能调用本地 VoxCPM2 语音合成，把文字念出来(输出 wav)。
// 零依赖：仅用 Node 内置模块，stdio JSON-RPC (NDJSON)，与 Codex 官方 MCP 客户端兼容。
// 实际合成由 speak.py 调用 VoxCPM2 的 gen_voice.py 完成。

import { createInterface } from 'node:readline';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pythonExe = process.env.SPEAK_PYTHON || 'python';
const speakScript = path.join(__dirname, 'speak.py');

const tools = [
  {
    name: 'speak_text',
    description:
      '把一段文字合成为语音并保存为 wav 文件，返回音频路径。' +
      '用于让 Codex "开口说话"：朗读回复、生成语音备忘录、做语音播报等。' +
      '底层为本地 VoxCPM2 模型(需 voxcpm conda 环境)。',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: '要朗读的文字内容' },
        voice: { type: 'string', description: '可选音色描述，如 御姐音 / 温柔女声 / 活泼少女音 / 普通男声' },
        output: { type: 'string', description: '可选，输出 wav 路径，默认生成在服务器目录 tts_output.wav' },
        cfg: { type: 'string', description: '可选，CFG 引导比例，越高越遵循语音描述，默认 2.0' },
        steps: { type: 'string', description: '可选，推理步数，越高越精细，默认 10' },
        ref: { type: 'string', description: '可选，参考音频路径(语音克隆)' },
        no_denoiser: { type: 'boolean', description: '可选，true 则关闭降噪器以加速加载' },
      },
      required: ['text'],
    },
  },
];

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

const rl = createInterface({ input: process.stdin, terminal: false });
let buf = '';
rl.on('line', (line) => {
  const text = (buf + line).trim();
  buf = '';
  if (!text) return;
  let msg;
  try {
    msg = JSON.parse(text);
  } catch {
    return;
  }

  if (msg.method === 'initialize') {
    send({
      jsonrpc: '2.0',
      id: msg.id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'speak', version: '1.0.0' },
      },
    });
  } else if (msg.method === 'notifications/initialized') {
    // 通知无需回复
  } else if (msg.method === 'tools/list') {
    send({ jsonrpc: '2.0', id: msg.id, result: { tools } });
  } else if (msg.method === 'tools/call') {
    const args = msg.params?.arguments || {};
    if (!args.text) {
      send({
        jsonrpc: '2.0',
        id: msg.id,
        result: { content: [{ type: 'text', text: '缺少参数 text' }], isError: true },
      });
      return;
    }
    const py = [speakScript, '--text', String(args.text)];
    if (args.voice) py.push('--voice', String(args.voice));
    if (args.output) py.push('--output', String(args.output));
    if (args.cfg) py.push('--cfg', String(args.cfg));
    if (args.steps) py.push('--steps', String(args.steps));
    if (args.ref) py.push('--ref', String(args.ref));
    if (args.no_denoiser) py.push('--no-denoiser');
    const child = spawn(pythonExe, py, { env: process.env });
    let out = '';
    let err = '';
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (err += d));
    child.on('close', (code) => {
      if (code !== 0) {
        send({
          jsonrpc: '2.0',
          id: msg.id,
          result: { content: [{ type: 'text', text: '语音合成失败:\n' + err }], isError: true },
        });
      } else {
        send({
          jsonrpc: '2.0',
          id: msg.id,
          result: { content: [{ type: 'text', text: '已生成语音: ' + out.trim() }] },
        });
      }
    });
  } else if (msg.id) {
    send({ jsonrpc: '2.0', id: msg.id, result: {} });
  }
});
