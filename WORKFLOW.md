# 本地 AI 视频生产工作流导出包（ComfyUI + MiniMax H3 + VoxCPM2 配音）

> 导出日期：2026-08-23。本包用于把「ComfyUI + MiniMax H3 视频生成 + VoxCPM2 配音」流程迁移到另一台电脑。
> 路径约定：全文使用占位符，请替换为你的实际路径。
>   - <ComfyUI目录>：ComfyUI 根目录（迁移时替换为目标机实际路径）
>   - <模型目录>：<ComfyUI目录>\models
>   - <Python环境>：Python 解释器或虚拟环境（迁移时替换为目标机实际路径）
>   - <VoxCPM Python环境>：VoxCPM2 配音用的 Python 解释器
>   - <TTS模型目录>：VoxCPM2 模型目录，可用 VOXCPM_MODEL_PATH 指定
>   - <FFmpeg目录>：ffmpeg 可执行文件所在目录

## 一、包内容

| 目录 | 内容 |
|---|---|
| workflows/ | ComfyUI 工作流 JSON（H3 Seamless Chain CORE/v2/Keyframes + 缘结守 2 个自定义工作流） |
| scripts/ | submit_h3.py（H3 API 提交脚本）、环境搭建脚本、GLM 识图脚本 |
| prompts/ | 缘结守 H3 各幕提示词、H3 提示词规范、审美速查、奥特曼速查、三笠 AOT 模板 |
| config/ | requirements.txt、requirements-tts.txt、额外安装说明、自定义节点清单、模型清单 |
| samples/ | 代表性输出视频与音频样例（不含全部） |
| tts/ | VoxCPM2 配音脚本、Web UI、克隆示例与安装说明 |

## 二、目标机器硬件要求

- NVIDIA 显卡，显存 >= 12GB（本机 RTX 4070 SUPER 12GB 实测：832x480 / 243 帧 / 24 步可跑）
- 磁盘空间：ComfyUI + 模型共需约 70GB（模型约 59GB）
- Windows 10/11，支持 CUDA 12.8

## 三、安装顺序（另一台电脑照此执行）

1. 安装 Python 3.13（>= 3.10 即可）。可参考 scripts/安装Python到D盘.ps1。
2. 安装 Git（可选，用于拉取自定义节点）。
3. 安装 FFmpeg（放 <FFmpeg目录>，把 bin 加入 PATH；或直接在 config.json 里写全路径）。
4. 下载并解压 ComfyUI 0.30.0（ComfyUI 官方仓库，版本 0.30.0 起原生支持 MiniMax H3）。
5. 安装 torch（CUDA 12.8）与 ComfyUI 依赖，见 config/requirements-额外安装说明.txt：
   python -m pip install torch==2.11.0 torchvision==0.26.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu128
   python -m pip install -r <包目录>\config\requirements.txt
6. 安装自定义节点（git clone 到 <ComfyUI目录>\custom_nodes\）：
   - https://github.com/jlucasmcrell/ComfyUI-H3-Multishot  （v2.2.0）
   - https://github.com/duckyshell/ComfyUI-MiniMaxH3-FirstBlockCache
   清单与说明见 config/custom_nodes_清单.md。装完重启 ComfyUI。
7. 下载模型（不随包分发，按 config/模型清单.md 下载，约 59GB）：
   - diffusion_models：minimax_h3_ref2va_pruned_int8_convrot.safetensors、minimax_h3_fl2va_pruned_int8_convrot.safetensors
   - text_encoders：qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
   - vae：minimax_h3_video_vae_fp16.safetensors、minimax_h3_audio_vae_fp32.safetensors
   来源：HuggingFace Comfy-Org/MiniMax-H3（国内可用 hf-mirror.com 镜像）。
   参考图放在 <ComfyUI目录>\input\。
8. 启动 ComfyUI：
   用 PowerShell 以 <Python环境> 运行 <ComfyUI目录>\main.py，参数 --port 8188，工作目录设为 <ComfyUI目录>，隐藏窗口。
   浏览器打开 http://127.0.0.1:8188 验证。
   注意：不要给启动参数加 --use-sage-attention（本环境缺 sageattention 包，加了会直接报错）。
9. 安装配音环境（可选但推荐）：按 tts/README.md，使用 Python 3.12 + voxcpm 2.0.3 + torch 2.6.0+cu124，依赖见 config/requirements-tts.txt。
10. 准备配音模型：从本机拷贝 E:\AI\voxcpm2_models，或用 openbmb/VoxCPM2 自动下载；通过 VOXCPM_MODEL_PATH 指向模型目录。
11. 验证流程：先按上方 8 启动 ComfyUI，再按 tts/README.md 跑一次配音，确认两边都正常。

## 四、使用方式

### A. 浏览器手动方式
把 workflows/ 里的 JSON 拖入 ComfyUI 画布。推荐从 H3_Seamless_Chain_CORE.json 开始（零额外依赖）。
在采样器的 script 框里写每镜提示词，用 --- 分隔；MASTER CONTROLS 里把分辨率改为 832x480、帧数按需（见下）。

### B. API 脚本方式（推荐，可复用）
scripts/submit_h3.py 封装了模型加载 → FirstBlockCache → H3MultishotSampler → CreateVideo → SaveVideo/SaveAudio 整条链路：
   python scripts/submit_h3.py "提示词" --frames 124 --prefix My_Shot --wait
支持：--shots 多镜、--start-image 首帧（I2V）、--refs 参考图（<Picture 1> 等）、--wait 等待完成。
使用前编辑脚本顶部 CONFIG 里的模型文件名与 ComfyUI 地址。

### 帧数网格（17k+5，必须取这些值）
56=2.3s / 73=3s / 90=3.75s / 107=4.5s / 124=5.2s / 141=5.9s / 158=6.6s / 175=7.3s / 192=8s / 209=8.7s / 226=9.4s / 243=10.1s（24fps）

## 五、FFmpeg 常用命令（<FFmpeg目录>\ffmpeg.exe / ffprobe.exe）

- 验证视频参数：ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 <视频>
- 抽帧（每隔 N 秒一帧）：ffmpeg -i <视频> -vf "fps=1/1.5,scale=640:-1" -q:v 3 frame_%02d.jpg
- 抽指定时间点单帧：ffmpeg -ss <秒> -i <视频> -frames:v 1 -q:v 2 out.jpg
- 抽尾帧（做下一镜 I2V 首帧）：ffmpeg -sseof -0.08 -i <视频> -frames:v 1 -q:v 2 last.jpg
- 拼接多段（同参数 mp4，先写 list.txt 每行 file '路径'，再）：ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 160k out.mp4

## 六、常见报错与修复

| 报错 | 原因 / 处理 |
|---|---|
| SaveVideo.execute() missing 1 required positional argument: 'codec' | API 提交漏传 codec，补 "codec":"auto"（submit_h3.py 已内置） |
| value_not_in_list: mode 校验失败 | FirstBlockCache 的 mode 字符串里 em dash 需用 \u2014 转义（submit_h3.py 已内置） |
| sage-attention 相关报错 | 启动参数不要加 --use-sage-attention |
| The value 1 for reference_image_size is not available | 旧版节点 widget 错位；更新 H3-Multishot 或重新拖节点 |
| OOM（显存不足） | 降低帧数（73→56）或换 fl2va 模型；单镜别超 243 帧 |
| 429/1305 GLM 限流 | GLM 识图接口繁忙，等 1-2 分钟重试或减少每批图片数 |
| H3ModelLoaderAny 里看不到模型 | 检查模型是否在 <模型目录>\diffusion_models\，重启 ComfyUI |

## 七、配音说明（重要）

- 本包已包含 VoxCPM2 配音流程，目录为 tts/，安装与用法见 tts/README.md。
- 本机生成的视频已自带 H3 场景声（风声/环境/动作音效等，无 BGM），样例见 samples/Butterfly_FlyAway_10s_v1.flac 与各 mp4 内音轨。
- 需要角色台词/对白时，用 tts/ 里的 VoxCPM2 脚本生成音频后，与本包产出的视频在后期合成。
- 提示词中的台词（如缘结守日语台词、奥特曼中文台词）仍由 H3 生成语音，供粗剪参考，最终语音以 VoxCPM2 配音为准。

## 八、缺失项与说明（如实列出）

1. 模型权重文件（约 59GB）：不导出，按 config/模型清单.md 下载。
2. 配音模型权重（约 4.6GB）：不随包分发，可从本机 E:\AI\voxcpm2_models 拷贝，或按 tts/README.md 下载 openbmb/VoxCPM2。
3. ComfyUI 程序本体：请下载官方 ComfyUI 0.30.0（本机 ComfyUI 由官方包安装，版本号见 pyproject.toml）。
4. GLM API Key：scripts/glm-vision/config.json 中已留空，需在目标电脑填入自己的 key（key 属私密信息，不随包分发）。
5. 原机的「奥特曼 / 三笠AOT」提示词此前只存在于对话记录中，本次已整理落盘到 prompts/（奥特曼-角色锁定与分镜速查.md、三笠AOT-提示词模板.md）。
6. 原机的视频提交此前以临时脚本方式执行，本次已固化为 scripts/submit_h3.py。
7. 自定义工作流仅导出可用的 JSON（H3 包 3 个 + 缘结守 2 个）；浏览器历史工作流未落盘的不在包内。

## 九、目录树速览

AI-workflow-export/
  README.md
  workflows/    5 个 JSON
  scripts/      submit_h3.py、环境搭建脚本、glm-vision/
  prompts/      缘结守各幕 + 规范 + 速查 + 模板
  config/       requirements、requirements-tts、节点清单、模型清单
  samples/      代表性视频 6 段 + 音频 1 个
  tts/          VoxCPM2 配音脚本、Web UI、克隆示例、README
