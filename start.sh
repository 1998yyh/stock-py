#!/bin/bash

# 股票筛选系统启动脚本

echo "🚀 启动股票筛选系统..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install Flask==2.3.3 Flask-CORS==4.0.0 pandas numpy akshare

# 启动服务
echo "🌐 启动Web服务..."
echo "访问地址: http://8.152.212.206:5000"
echo "按 Ctrl+C 停止服务"
python app.py
