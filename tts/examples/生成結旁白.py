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
        "結-旁白-1-妈妈离开.wav",
        "妈妈是在我上小学那年离开的。她说要回城里工作，以后会按时寄生活费回来。",
    ),
    (
        "結-旁白-2-家里冷清.wav",
        "从那以后，爸爸好像一直没醒过来。我不太会交朋友，学校里的声音，也总是一句一句落在我身后。",
    ),
    (
        "結-旁白-3-想找人说话.wav",
        "后来我才发现，我只是想找一个人，能好好听我说完一句话。",
    ),
]

for filename, text in clips:
    wav = model.generate(text=text, reference_wav_path=ref, cfg_value=2.0, inference_timesteps=10)
    out = os.path.join(base, filename)
    sf.write(out, wav, model.tts_model.sample_rate)
    print(out)
    print(len(wav) / model.tts_model.sample_rate)
