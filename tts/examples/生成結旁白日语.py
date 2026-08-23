import os
from voxcpm import VoxCPM
import soundfile as sf


model_path = os.environ.get("VOXCPM_MODEL_PATH", "openbmb/VoxCPM2")
ref = os.environ.get(
    "REF_AUDIO",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "結-原视频音频.wav"),
)
base = os.environ.get(
    "OUTPUT_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs"),
)

model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
os.makedirs(base, exist_ok=True)

clips = [
    (
        "結-旁白-1-妈妈离开-日语.wav",
        "お母さんは、私が小学校に上がった年に出て行った。お金はちゃんと送るからって、そう言って出て行った。",
    ),
    (
        "結-旁白-2-家里冷清-日语.wav",
        "それから父は、ずっと眠ったままみたいだった。私は友達を作るのも上手じゃなくて、学校で聞こえる声も、いつも私の後ろに落ちていった。",
    ),
    (
        "結-旁白-3-想找人说话-日语.wav",
        "あとから分かったけど、私はただ、ちゃんと最後まで話を聞いてくれる人が欲しかっただけなんだ。",
    ),
]

for filename, text in clips:
    wav = model.generate(text=text, reference_wav_path=ref, cfg_value=2.0, inference_timesteps=10)
    out = os.path.join(base, filename)
    sf.write(out, wav, model.tts_model.sample_rate)
    print(out)
    print(len(wav) / model.tts_model.sample_rate)
