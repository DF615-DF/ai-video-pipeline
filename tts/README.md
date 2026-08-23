# VoxCPM2 配音流程

> 本目录包含本机使用的 VoxCPM2 配音流程：CLI 合成、`speak.py` 封装、Codex MCP 接入、Web UI、结旁白克隆示例。

## 文件

| 文件 | 说明 |
|------|------|
| `gen_voice.py` | VoxCPM2 底层合成脚本，支持 TTS、音色描述、克隆 |
| `speak.py` | 命令行封装，支持 `--voice` / `--ref` / `--output` |
| `speak.mjs` | Codex MCP 服务器入口，工具名 `speak_text` |
| `web_app.py` | 可选 Gradio Web 界面，默认 `http://localhost:8808` |
| `examples/生成結旁白.py` | 结中文旁白克隆示例 |
| `examples/生成結旁白日语.py` | 结日语旁白克隆示例 |
| `examples/結-原视频音频.wav` | 结原声参考音频 |

## 环境（本机实测）

- Python 3.12.13（conda 环境 `voxcpm`）
- torch 2.6.0+cu124
- voxcpm 2.0.3
- soundfile 0.14.0
- gradio 6.20.0（仅 Web UI 需要）
- 模型：`E:\AI\voxcpm2_models`（约 4.6GB，未随包分发）

## 安装

```bash
conda create -n voxcpm python=3.12
conda activate voxcpm
python -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
python -m pip install -r config/requirements-tts.txt
```

模型二选一：

1. 从本机直接拷贝 `E:\AI\voxcpm2_models` 到目标电脑，然后设置 `VOXCPM_MODEL_PATH=<模型目录>`。
2. 不拷贝模型，让脚本从 HuggingFace 自动下载 `openbmb/VoxCPM2`。

## 用法

CLI 合成：

```bash
<voxcpm python> tts/gen_voice.py "(温柔女声)你好" -o out.wav -c 2.0 -s 10
```

命令行封装：

```bash
<voxcpm python> tts/speak.py --text "你好" --voice 温柔女声 --output out.wav
```

Codex MCP 接入：

```bash
codex mcp add speak --env GEN_VOICE="<包目录>\tts\gen_voice.py" --env VOXCPM_PYTHON="<voxcpm python>" -- node <包目录>\tts\speak.mjs
```

Web UI（可选）：

```bash
<voxcpm python> tts/web_app.py --port 8808
```

结旁白克隆示例：

```bash
set VOXCPM_MODEL_PATH=<模型目录>
set REF_AUDIO=<包目录>\tts\examples\結-原视频音频.wav
set OUTPUT_DIR=<包目录>\tts\outputs
<voxcpm python> tts/examples/生成結旁白.py
```

## 关键环境变量

| 变量 | 说明 |
|------|------|
| `VOXCPM_MODEL_PATH` | 本地模型目录，留空则用 `openbmb/VoxCPM2` |
| `VOXCPM_PYTHON` | VoxCPM Python 解释器路径 |
| `GEN_VOICE` | `gen_voice.py` 的绝对路径 |
| `REF_AUDIO` | 克隆参考音频路径 |
| `OUTPUT_DIR` | 示例脚本输出目录 |

## 注意

- 首次加载模型约需 60–90 秒。
- 语音克隆参考音频推荐 3–10 秒。
- `load_denoiser=False` 可加快加载并减少显存占用。
