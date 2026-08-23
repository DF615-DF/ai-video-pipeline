import time, sys, os, argparse

def main():
    parser = argparse.ArgumentParser(description='VoxCPM2 TTS - 语音合成')
    parser.add_argument('text', nargs='?', default='亲爱的晚上好',
                        help='合成文本。语音设计可在开头加 (描述)，如 "(御姐音)亲爱的晚上好"')
    parser.add_argument('-o', '--output', default=None,
                        help='输出文件路径')
    parser.add_argument('-c', '--cfg', type=float, default=2.0,
                        help='CFG引导比例 (default: 2.0)')
    parser.add_argument('-s', '--steps', type=int, default=10,
                        help='推理步数 (default: 10)')
    parser.add_argument('--ref', default=None,
                        help='参考音频路径（语音克隆）')
    parser.add_argument('--prompt-wav', default=None,
                        help='提示音频路径（终极克隆）')
    parser.add_argument('--prompt-text', default=None,
                        help='提示音频对应文本（终极克隆）')
    parser.add_argument('--model-path', default=os.environ.get('VOXCPM_MODEL_PATH', 'openbmb/VoxCPM2'),
                        help='模型路径或 HuggingFace 模型 ID，可用 VOXCPM_MODEL_PATH 环境变量')
    parser.add_argument('--no-denoiser', action='store_true',
                        help='关闭降噪器（加速加载）')
    args = parser.parse_args()

    if args.output is None:
        safe_text = args.text.replace('(', '_').replace(')', '_')[:20]
        args.output = 'E:\\AI\\工作\\' + safe_text + '.wav'

    t0 = time.time()
    from voxcpm import VoxCPM
    import soundfile as sf
    model = VoxCPM.from_pretrained(args.model_path,
                                   load_denoiser=not args.no_denoiser)
    print(f'Model ready in {time.time()-t0:.0f}s', flush=True)

    gen_kw = dict(text=args.text, cfg_value=args.cfg,
                  inference_timesteps=args.steps)
    if args.ref:
        gen_kw['reference_wav_path'] = args.ref
    if args.prompt_wav:
        gen_kw['prompt_wav_path'] = args.prompt_wav
    if args.prompt_text:
        gen_kw['prompt_text'] = args.prompt_text

    wav = model.generate(**gen_kw)
    sf.write(args.output, wav, 48000)
    print(f'Done! {args.output} ({time.time()-t0:.0f}s)', flush=True)

if __name__ == '__main__':
    main()
