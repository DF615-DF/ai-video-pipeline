#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GLM 4.6V Flash 识图工具：把本地图片发送给 GLM 视觉模型，返回中文分析。"""
import argparse
import base64
import json
import os
import sys
import time

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
DEFAULT_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def load_config():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    cfg["api_key"] = os.environ.get("GLM_API_KEY") or cfg.get("api_key")
    cfg["model"] = os.environ.get("GLM_MODEL") or cfg.get("model") or "glm-4.6v-flash"
    cfg["endpoint"] = os.environ.get("GLM_ENDPOINT") or cfg.get("endpoint") or DEFAULT_ENDPOINT
    if not cfg["api_key"]:
        print("缺少 API key：请在 scripts/config.json 配置 api_key，或设置环境变量 GLM_API_KEY", file=sys.stderr)
        sys.exit(2)
    return cfg


def encode_image(path):
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
        "bmp": "image/bmp",
    }.get(ext, "image/png")
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())


def call_glm(cfg, images, prompt, max_tokens=2000):
    import urllib.request
    import urllib.error

    content = [{"type": "text", "text": prompt}]
    for img in images:
        content.append({"type": "image_url", "image_url": {"url": encode_image(img)}})
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.6,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        cfg["endpoint"],
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + cfg["api_key"]},
    )
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.loads(r.read().decode("utf-8"))
            return resp
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            last_err = RuntimeError("HTTP %s: %s" % (e.code, body[:300]))
            # 1305/1304: 模型繁忙/限流，退避重试
            if e.code == 429 and ('1305' in body or '1304' in body):
                wait = 15 * (attempt + 1)
                print("模型繁忙，%.0f 秒后重试 (%d/6)..." % (wait, attempt + 1), file=sys.stderr)
                time.sleep(wait)
                continue
            raise last_err
    raise last_err
    return resp


def main():
    ap = argparse.ArgumentParser(description="用 GLM 视觉模型分析本地图片")
    ap.add_argument("images", nargs="+", help="图片路径（可多个）")
    ap.add_argument(
        "-p",
        "--prompt",
        default=(
            "请用中文详细分析这张参考图的画面风格：构图、色彩（饱和度/冷暖）、光影、笔触质感、"
            "情绪基调，并总结成可用于 AI 视频生成提示词的风格锚点（正向/负向词表）。"
        ),
    )
    ap.add_argument("--max-tokens", type=int, default=2000)
    args = ap.parse_args()

    for img in args.images:
        if not os.path.exists(img):
            print("文件不存在: %s" % img, file=sys.stderr)
            sys.exit(2)
    cfg = load_config()
    try:
        resp = call_glm(cfg, args.images, args.prompt, max_tokens=args.max_tokens)
    except Exception as e:
        print("调用 GLM API 失败: %s" % e, file=sys.stderr)
        sys.exit(1)
    if "choices" in resp and resp["choices"]:
        print(resp["choices"][0]["message"]["content"])
    else:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
