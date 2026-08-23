#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ffmpeg -> GLM 视频分析：用 ffmpeg 抽帧，交给 GLM 4.6V Flash 分析视频内容与风格。"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from glm_vision import load_config as load_glm_config
from glm_vision import call_glm

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_cfg():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    cfg["ffmpeg_path"] = os.environ.get("FFMPEG_PATH") or cfg.get("ffmpeg_path") or "ffmpeg"
    cfg["ffprobe_path"] = os.environ.get("FFPROBE_PATH") or cfg.get("ffprobe_path") or "ffprobe"
    return cfg


def get_duration(ffprobe, video):
    out = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        return float(out.stdout.strip().splitlines()[0])
    except Exception:
        return 0.0


def extract_frames(ffmpeg, video, outdir, count):
    dur = get_duration(ffmpeg.replace("ffmpeg.exe", "ffprobe.exe"), video)
    if dur <= 0:
        dur = 3.0
    paths = []
    for i in range(count):
        t = dur * (i + 0.5) / count
        p = os.path.join(outdir, "frame_%03d.jpg" % i)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-ss",
                "%.3f" % t,
                "-i",
                video,
                "-frames:v",
                "1",
                "-vf",
                "scale=1024:-2",
                "-q:v",
                "3",
                p,
            ],
            capture_output=True,
            timeout=120,
        )
        if os.path.exists(p):
            paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(description="ffmpeg 抽帧 + GLM 视频分析")
    ap.add_argument("video", help="视频路径")
    ap.add_argument("-n", "--frames", type=int, default=5, help="抽帧数量（默认 5）")
    ap.add_argument(
        "-p",
        "--prompt",
        default=(
            "这些是同一段视频的按时间抽帧。请分析：1) 画面内容（人物/场景/动作）；"
            "2) 画面风格（构图、色彩、光影、笔触质感）；3) 情绪基调；"
            "4) 总结成可用于 AI 视频生成提示词的风格锚点。"
        ),
    )
    ap.add_argument("--max-tokens", type=int, default=1500)
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print("视频文件不存在: %s" % args.video, file=sys.stderr)
        sys.exit(2)

    cfg = load_cfg()
    glm_cfg = load_glm_config()
    with tempfile.TemporaryDirectory(prefix="glm_video_") as tmp:
        frames = extract_frames(cfg["ffmpeg_path"], args.video, tmp, args.frames)
        if not frames:
            print("抽帧失败，请检查 ffmpeg 路径：%s" % cfg["ffmpeg_path"], file=sys.stderr)
            sys.exit(1)
        print("抽帧 %d 张" % len(frames), file=sys.stderr)

        # GLM 每次最多 3 张图，分批
        for i in range(0, len(frames), 3):
            batch = frames[i : i + 3]
            try:
                resp = call_glm(glm_cfg, batch, args.prompt, max_tokens=args.max_tokens)
            except Exception as e:
                print("GLM 调用失败: %s" % e, file=sys.stderr)
                sys.exit(1)
            print("---- 批次 %d/%d ----" % (i // 3 + 1, (len(frames) + 2) // 3))
            print(resp["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
