# 全自动 AI 视频生产线 · 作品集案例

本地部署 MiniMax H3（开源权重）+ ComfyUI + VoxCPM2 本地配音，用 Codex 编排，把"剧本 → 生成 → 配音 → 合成"串成可复用、可迁移、可复现的全自动 AI 视频工作流。

## 亮点
- **真·本地推理**：MiniMax H3 开源权重（INT8 ~59GB）在消费级显卡 RTX 4070S 12GB 上实跑，数据不出机、按次零成本，不依赖任何云端额度。
- **全自动编排**：Codex 调度 + `scripts/submit_h3.py` 一键提交整条链，多镜无缝衔接（H3_Seamless_Chain）。
- **画面+声音闭环**：VoxCPM2 本地声音克隆补足台词/旁白，H3 自带场景声，后期合成即完整成片。

## 仓库内容
- `index.html` — 作品集案例页（架构图 / 四步流程 / 审美体系 / 成片展示 / 复现）。
- `samples/` — 成片样例（6 支短视频 + 1 配音参考音频）。《缘结守》完整正片约 170MB，单独走 CloudStudio 部署托管，不随本仓库分发。
- `config/ prompts/ scripts/ tts/ workflows/` — 工程资产：需求 / 节点 / 模型清单、提示词规范与剧本、提交脚本、VoxCPM2 配音、5 套工作流 JSON。
- `WORKFLOW.md` — 原导出包 README：11 步安装 + 报错对照表 + 诚实的缺失项。

## 线上 demo
https://48b9bf0e2a2f4b2493efc650426e0b7b.app.workbuddy.link

## 复现
1. 按 `WORKFLOW.md` 第 1–11 步装环境 / 下模型（H3 ~59GB、VoxCPM2 ~4.6GB 需自行准备，不随包分发）。
2. 启动 ComfyUI → 跑 `scripts/submit_h3.py` 与 tts 脚本。
3. 详见 `index.html`「工程素养与如何复现」一节。

> 本仓库仅含代码与轻量样例，模型权重与密钥不随包分发。
