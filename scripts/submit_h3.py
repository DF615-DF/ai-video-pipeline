#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Submit a MiniMax H3 video job to a local ComfyUI via the /prompt API.

Usage examples:
  python submit_h3.py "a butterfly flies away from a hand" --frames 243 --prefix Butterfly --wait
  python submit_h3.py shots.txt --shots 3 --refs ref_a.jpg,ref_b.jpg --start-image first.png --prefix My_Clip --wait
  python submit_h3.py "text prompt" --frames 124 --width 832 --height 480 --steps 24 --seed 2026 --prefix Demo

Edit CONFIG below to match the target machine. Paths are ComfyUI-relative
(names inside <ComfyUI>/input and <ComfyUI>/models).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

CONFIG = {
    "comfy_url": "http://127.0.0.1:8188",
    "model": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    "clip": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    "video_vae": "minimax_h3_video_vae_fp16.safetensors",
    "audio_vae": "minimax_h3_audio_vae_fp32.safetensors",
    "sampler": "res_multistep",
    "scheduler": "simple",
    "use_firstblock_cache": True,   # apply ApplyMiniMaxH3FirstBlockCache (Fast)
}


def build_prompt(args):
    base = {
        "1": {"class_type": "H3ModelLoaderAny",
              "inputs": {"model_name": CONFIG["model"]}},
        "2": {"class_type": "H3ClipLoaderAny",
              "inputs": {"clip_name": CONFIG["clip"], "type": "minimax"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": CONFIG["video_vae"]}},
        "4": {"class_type": "VAELoader",
              "inputs": {"vae_name": CONFIG["audio_vae"]}},
    }
    if CONFIG["use_firstblock_cache"]:
        base["5"] = {"class_type": "ApplyMiniMaxH3FirstBlockCache",
                     "inputs": {"model": ["1", 0],
                                "mode": "H3 Fast \u2014 0.10 / max 2",
                                "threshold": 0.10, "start_percent": 0.10,
                                "end_percent": 0.95,
                                "max_consecutive_hits": 2,
                                "temporal_guard": False}}
        model_link = ["5", 0]
    else:
        model_link = ["1", 0]

    # start image (I2V first frame)
    if args.start_image:
        base["10"] = {"class_type": "LoadImage",
                      "inputs": {"image": args.start_image}}
        start_link = ["10", 0]
    else:
        start_link = None

    # reference images (<Picture 1>, <Picture 2>, ...)
    ref_link = None
    if args.refs:
        names = [r.strip() for r in args.refs.split(",") if r.strip()]
        for i, name in enumerate(names):
            base[str(20 + i)] = {"class_type": "LoadImage",
                                 "inputs": {"image": name}}
        if len(names) == 1:
            ref_link = ["20", 0]
        else:
            # chain ImageBatch nodes for N > 2 references
            cur = ["20", 0]
            for i in range(1, len(names)):
                nid = str(30 + i)
                base[nid] = {"class_type": "ImageBatch",
                             "inputs": {"image1": cur,
                                        "image2": [str(20 + i), 0]}}
                cur = [nid, 0]
            ref_link = cur

    sam_in = {
        "model": model_link, "clip": ["2", 0],
        "video_vae": ["3", 0], "audio_vae": ["4", 0],
        "script": args.script_text, "shot_count": args.shots,
        "width": args.width, "height": args.height,
        "frames_per_shot": args.frames, "seed": args.seed,
        "steps": args.steps, "seed_per_shot": True,
        "sampler_name": CONFIG["sampler"],
        "scheduler": CONFIG["scheduler"],
    }
    if start_link:
        sam_in["start_image"] = start_link
    if ref_link:
        sam_in["reference_images"] = ref_link
    base["50"] = {"class_type": "H3MultishotSampler", "inputs": sam_in}
    base["51"] = {"class_type": "CreateVideo",
                  "inputs": {"images": ["50", 0], "fps": args.fps,
                             "audio": ["50", 1], "bit_depth": 8}}
    base["52"] = {"class_type": "SaveVideo",
                  "inputs": {"video": ["51", 0],
                             "filename_prefix": args.prefix,
                             "format": "mp4", "codec": "auto"}}
    base["53"] = {"class_type": "SaveAudio",
                  "inputs": {"audio": ["50", 1],
                             "filename_prefix": args.prefix}}
    return base


def post(payload):
    req = urllib.request.Request(
        CONFIG["comfy_url"] + "/prompt",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def wait(prompt_id, timeout_min=120):
    t0 = time.time()
    url = CONFIG["comfy_url"] + "/history/" + prompt_id
    while time.time() - t0 < timeout_min * 60:
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("poll error:", e, flush=True)
            time.sleep(20)
            continue
        if prompt_id in data:
            st = data[prompt_id].get("status", {})
            status = st.get("status_str")
            if status == "success":
                files = []
                for nid, out in data[prompt_id].get("outputs", {}).items():
                    for k, v in out.items():
                        if isinstance(v, list):
                            for f in v:
                                if isinstance(f, dict) and "filename" in f:
                                    files.append(f["filename"])
                print("SUCCESS in %dm%02ds" % (int(time.time() - t0) // 60,
                                               int(time.time() - t0) % 60))
                for f in files:
                    print("  output:", f)
                return True
            if status == "error":
                print("ERROR:", json.dumps(st, ensure_ascii=False)[:2000])
                return False
        time.sleep(20)
    print("TIMEOUT")
    return False


def main():
    ap = argparse.ArgumentParser(description="MiniMax H3 ComfyUI submitter")
    ap.add_argument("script", help="inline prompt text, or path to a .txt "
                                   "file (shots separated by '---')")
    ap.add_argument("--shots", type=int, default=0,
                    help="0 = one shot per prompt, 1-8 = force count")
    ap.add_argument("--frames", type=int, default=243,
                    help="frames per shot (17k+5 grid: 56/73/90/107/124/141/"
                         "158/175/192/209/226/243...)")
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--start-image", default=None,
                    help="filename inside <ComfyUI>/input")
    ap.add_argument("--refs", default=None,
                    help="comma-separated reference images in <ComfyUI>/input")
    ap.add_argument("--prefix", default="ComfyUI")
    ap.add_argument("--wait", action="store_true",
                    help="poll until the job finishes")
    args = ap.parse_args()

    if args.script.strip().endswith((".txt", ".md")) and \
            args.script.strip()[0] != "{":
        with open(args.script, "r", encoding="utf-8") as f:
            args.script_text = f.read()
    else:
        args.script_text = args.script

    payload = {"prompt": build_prompt(args), "client_id": "h3-submitter"}
    try:
        out = post(payload)
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode("utf-8", "replace"))
        sys.exit(1)
    print(json.dumps(out, ensure_ascii=False))
    pid = out.get("prompt_id")
    if args.wait and pid:
        sys.exit(0 if wait(pid) else 2)


if __name__ == "__main__":
    main()
