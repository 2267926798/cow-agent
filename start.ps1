# -------------------------------------------------------------------
# 智慧牧场 AI Agent 诊断服务 - PowerShell 一键启动脚本
# 1. 检查并自动创建 venv 虚拟环境
# 2. 自动安装/更新 requirements.txt 依赖
# 3. 启动 FastAPI REST & SSE 服务
# -------------------------------------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Green
Write-Host " 🚀 正在启动 智慧牧场 AI Agent 诊断服务..." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# 1. 检查 Python 环境
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 错误: 未检测到 Python 命令，请先安装 Python 3.10+。" -ForegroundColor Red
    exit 1
}

# 2. 检查并创建 venv 虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "📦 首次运行，正在创建 Python venv 虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ 虚拟环境 venv 创建完成！" -ForegroundColor Green
}

# 3. 安装依赖
Write-Host "⚡ 正在检查并安装项目依赖项 (requirements.txt)..." -ForegroundColor Cyan
.\venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.\venv\Scripts\pip.exe install --quiet -r requirements.txt
Write-Host "✅ 依赖项检查完成！" -ForegroundColor Green

# 4. 执行单元测试
Write-Host "🧪 正在运行自动单元测试..." -ForegroundColor Cyan
$env:PYTHONPATH = "."
.\venv\Scripts\pytest.exe --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 单元测试未通过，请检查代码变更！" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 单元测试通过！" -ForegroundColor Green

# 5. 启动 FastAPI 服务
Write-Host "-----------------------------------------------------" -ForegroundColor Yellow
Write-Host "🌟 服务启动成功！访问地址:" -ForegroundColor Green
Write-Host "👉 Swagger API 文档: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "👉 健康检查接口: http://127.0.0.1:8000/health" -ForegroundColor Yellow
Write-Host "-----------------------------------------------------" -ForegroundColor Yellow

.\venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
