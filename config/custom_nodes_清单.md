# ComfyUI 自定义节点清单

安装方式：git clone 到 <ComfyUI>/custom_nodes/ 后重启 ComfyUI。

| 目录名 | 来源 | 版本/commit | 作用 | 必需 |
|---|---|---|---|---|
| ComfyUI-H3-Multishot | https://github.com/jlucasmcrell/ComfyUI-H3-Multishot | v2.2.0 (f113565, 2026-08-12) | H3 多镜链式/无缝长镜头采样（H3MultishotSampler、H3ModelLoaderAny、H3ClipLoaderAny 等） | 是 |
| ComfyUI-MiniMaxH3-FirstBlockCache | https://github.com/duckyshell/ComfyUI-MiniMaxH3-FirstBlockCache | 725973c (2026-08-07) | 残差缓存加速（ApplyMiniMaxH3FirstBlockCache，Safe/Fast/Aggressive 三档），本机实测约 1.85x | 是（推荐） |
| example_node.py.example | ComfyUI 自带示例 | - | 忽略即可 | 否 |
| websocket_image_save.py | 本机遗留小工具 | - | 自定义节点样例（websocket 存图），忽略 | 否 |

## 注意

- FirstBlockCache 必须直接接在模型加载器之后，不能与 EasyCache / LazyCache / CacheDiT / T8 BlockCache 同时使用。
- H3-Multishot 的 FULL 工作流（H3_Seamless_Chain_v2.json）额外需要 ComfyUI-H3-Motion-Context、RES4LYF、ComfyUI-sol-attn、comfyui-minimax-h3-blockcache-T8、ComfyUI-Custom-Scripts；CORE 工作流不需要任何额外包，本机用 CORE。
- 模型为 .safetensors，不需要 ComfyUI-GGUF。
