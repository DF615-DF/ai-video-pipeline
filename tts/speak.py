# speak.py — 实际调用本地 VoxCPM2 合成语音。
# 由 speak.mjs 作为子进程调用；也可单独运行：
#   python speak.py --text "你好" --voice 御姐音 --output out.wav
#
# 底层调用 VoxCPM2 的 gen_voice.py（参见 04-工作备忘/2026-07-31_VoxCPM2语音合成配置.md）。

import argparse
import os
import subprocess
import sys

GEN_VOICE = os.environ.get(
    'GEN_VOICE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen_voice.py')
)
VOXCPM_PY = os.environ.get('VOXCPM_PYTHON', 'python')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--text', required=True, help='要朗读的文字')
    p.add_argument('--voice', default='', help='音色描述，如 御姐音 / 温柔女声')
    p.add_argument('--output', default='', help='输出 wav 路径')
    p.add_argument('--cfg', default='2.0', help='CFG 引导比例')
    p.add_argument('--steps', default='10', help='推理步数')
    p.add_argument('--ref', default='', help='参考音频路径(语音克隆)')
    p.add_argument('--no-denoiser', action='store_true', help='关闭降噪器')
    args = p.parse_args()

    text = args.text
    if args.voice:
        text = f'({args.voice}){text}'

    if not os.path.exists(VOXCPM_PY):
        print('未找到 voxcpm python: ' + VOXCPM_PY, file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(GEN_VOICE):
        print('未找到 gen_voice.py: ' + GEN_VOICE, file=sys.stderr)
        sys.exit(1)

    out_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'tts_output.wav'
    )

    cmd = [
        VOXCPM_PY, GEN_VOICE, text,
        '-o', out_path,
        '-c', str(args.cfg),
        '-s', str(args.steps),
    ]
    if args.ref:
        cmd += ['--ref', args.ref]
    if args.no_denoiser:
        cmd.append('--no-denoiser')

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('TTS 失败:\n' + r.stderr, file=sys.stderr)
        sys.exit(1)
    print(out_path)


if __name__ == '__main__':
    main()
