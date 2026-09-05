@echo off
chcp 65001 >nul
echo =====================================================
echo  🚀 正在启动 智慧牧场 AI Agent 诊断服务...
echo =====================================================

if not exist venv (
    echo 📦 正在创建 Python venv 虚拟环境...
    python -m venv venv
)

echo ⚡ 正在检查并安装项目依赖...
.\venv\Scripts\pip.exe install -q -r requirements.txt

echo 🧪 正在运行自动单元测试...
set PYTHONPATH=.
.\venv\Scripts\pytest.exe -q
if %errorlevel% neq 0 (
    echo ❌ 单元测试未通过！
    pause
    exit /b 1
)

echo 🌟 启动 FastAPI REST 服务 (端口 8000)...
echo 👉 API 文档地址: http://127.0.0.1:8000/docs
.\venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
