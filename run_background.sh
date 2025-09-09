#!/bin/bash

# 股票筛选系统后台运行脚本

echo "🚀 启动股票筛选系统后台服务..."

# 创建logs目录
mkdir -p logs

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

# 停止之前的进程（如果存在）
echo "🔄 检查并停止旧进程..."
PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "停止旧进程: $PID"
    kill $PID
    sleep 2
fi

# 使用nohup后台运行
echo "🌐 启动后台服务..."
nohup python app.py > logs/app.log 2>&1 &

# 获取新进程PID
sleep 2
NEW_PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$NEW_PID" ]; then
    echo "✅ 服务启动成功！"
    echo "进程ID: $NEW_PID"
    echo "访问地址: http://8.152.212.206:5000"
    echo "日志文件: logs/app.log"
    echo ""
    echo "📋 管理命令："
    echo "  查看日志: tail -f logs/app.log"
    echo "  停止服务: kill $NEW_PID"
    echo "  查看进程: ps aux | grep app.py"
else
    echo "❌ 服务启动失败，请检查日志: logs/app.log"
fi
