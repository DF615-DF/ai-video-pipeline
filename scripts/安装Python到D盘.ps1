# =============================================================
#  通用 Python 3.13 检查 / 安装（H3 + ComfyUI 使用）
#  用法：右键此文件 -> 使用 PowerShell 运行
# =============================================================
$ErrorActionPreference = 'Stop'

$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    Write-Host '检测到 Python：' -ForegroundColor Cyan
    & python --version
} else {
    Write-Host '未检测到 python，尝试用 winget 安装 Python 3.13 ...' -ForegroundColor Yellow
    winget install --id Python.Python.3.13 --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'winget 安装失败，请手动到 https://www.python.org/downloads/ 安装 Python 3.13，并勾选 Add to PATH' -ForegroundColor Red
        exit 1
    }
}

Write-Host ''
Write-Host '安装/检测完成。后续建议创建独立虚拟环境：' -ForegroundColor Green
Write-Host '  python -m venv <Python环境>'
Write-Host '  <Python环境>\Scripts\python.exe -m pip install -r config\requirements.txt'
Read-Host '按回车退出'
