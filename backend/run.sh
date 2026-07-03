#!/bin/bash
echo "启动 AI 行业情报系统后端服务..."

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装/更新依赖..."
pip install -r requirements.txt

echo "启动服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload