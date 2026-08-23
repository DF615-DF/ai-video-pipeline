import os
import sys
import pathlib
import gradio as gr
import numpy as np
import tempfile
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Model loading (first Generate request triggers load)
# ---------------------------------------------------------------------------
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# Local model path (downloaded via ModelScope)
_LOCAL_MODEL_PATH = os.environ.get("VOXCPM_MODEL_PATH", "")
_DEFAULT_MODEL_ID = os.environ.get("VOXCPM_MODEL_ID", "openbmb/VoxCPM2")

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading VoxCPM2 model (this may take a while the first time)...", file=sys.stderr)
        from voxcpm import VoxCPM
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        if _LOCAL_MODEL_PATH and pathlib.Path(_LOCAL_MODEL_PATH).joinpath("config.json").exists():
            print(f"Loading model from local path: {_LOCAL_MODEL_PATH}", file=sys.stderr)
            _model = VoxCPM.from_pretrained(_LOCAL_MODEL_PATH, load_denoiser=False)
        else:
            print(f"Local model not found, downloading from HuggingFace: {_DEFAULT_MODEL_ID}", file=sys.stderr)
            _model = VoxCPM.from_pretrained(_DEFAULT_MODEL_ID, load_denoiser=False)
        print("Model loaded successfully!", file=sys.stderr)
    return _model


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def synthesize(text, voice_description, reference_audio, clone_mode, progress=gr.Progress()):
    import torch
    torch.manual_seed(42)
    if not text or not text.strip():
        return None, "请输入文本内容"

    try:
        progress(0.1, desc="加载模型中...")
        model = get_model()

        final_text = text
        if voice_description and voice_description.strip():
            final_text = f"({voice_description.strip()}){text}"

        progress(0.3, desc="生成语音中...")

        kwargs = dict(text=final_text, cfg_value=2.0, inference_timesteps=10)

        if clone_mode == "语音克隆" and reference_audio is not None:
            kwargs["reference_wav_path"] = reference_audio
        elif clone_mode == "终极克隆" and reference_audio is not None:
            kwargs["reference_wav_path"] = reference_audio
            kwargs["prompt_wav_path"] = reference_audio
            kwargs["prompt_text"] = ""

        progress(0.6, desc="合成中...")
        wav = model.generate(**kwargs)

        progress(0.9, desc="保存音频...")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_path = tmp.name
        tmp.close()
        sf.write(tmp_path, wav, model.tts_model.sample_rate)

        return tmp_path, f"生成成功! 采样率: {model.tts_model.sample_rate}Hz, 时长: {len(wav)/model.tts_model.sample_rate:.1f}s"
    except Exception as e:
        return None, f"生成失败: {str(e)}"


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="VoxCPM2 语音合成") as demo:
    gr.Markdown(
        """# 语音合成

多语言、高质量语音合成，支持**语音设计**、**语音克隆**和**终极克隆**。"""
    )

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(label="输入文本", placeholder="请输入要合成的文本，支持30种语言...", lines=4, value="欢迎使用 VoxCPM2 语音合成系统。")
            voice_desc = gr.Textbox(label="语音设计描述（可选）", placeholder='例如: "A young woman, gentle and sweet voice"', lines=2)
            clone_mode = gr.Radio(choices=["语音设计（无需参考音频）", "语音克隆", "终极克隆"], value="语音设计（无需参考音频）", label="模式")
            ref_audio = gr.Audio(label="参考音频（克隆模式用）", type="filepath", visible=False)

            def toggle_ref_audio(mode):
                return gr.update(visible=mode != "语音设计（无需参考音频）")

            clone_mode.change(fn=toggle_ref_audio, inputs=clone_mode, outputs=ref_audio)
            generate_btn = gr.Button("生成语音", variant="primary", size="lg")

        with gr.Column(scale=2):
            audio_output = gr.Audio(label="生成的语音", type="filepath")
            status = gr.Textbox(label="状态", interactive=False)

    generate_btn.click(fn=synthesize, inputs=[text_input, voice_desc, ref_audio, clone_mode], outputs=[audio_output, status])

    gr.Markdown("""---""")
    gr.Markdown("""首次生成需等待约 60-90 秒（模型加载）。30 种语言自动识别。""")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8808)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    print(f"Starting VoxCPM2 web demo at http://{args.host}:{args.port}")
    demo.queue().launch(server_name=args.host, server_port=args.port, share=False, theme=gr.themes.Soft())
