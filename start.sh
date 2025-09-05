#!/bin/bash

# 阿里云Linux专用启动脚本

echo "🌐 在阿里云环境启动股票筛选系统..."

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️ 虚拟环境不存在，使用系统Python"
    export PATH=$HOME/.local/bin:$PATH
fi

# 创建必要目录
mkdir -p data logs

# 检查依赖
python3 -c "
try:
    import flask, pandas
    print('✅ 核心依赖检查通过')
except ImportError as e:
    print('❌ 核心依赖缺失:', e)
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 依赖检查失败，请重新运行: ./install_aliyun.sh"
    exit 1
fi

# 启动服务
echo "🌐 启动服务..."
echo "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip'):5000"
echo "内网地址: http://$(hostname -I | awk '{print $1}'):5000"
echo "本地地址: http://localhost:5000"

if [ "$1" = "background" ]; then
    echo "🔧 后台模式启动..."
    nohup python3 app.py > logs/app.log 2>&1 &
    echo "✅ 服务已在后台启动"
    echo "📋 查看日志: tail -f logs/app.log"
    echo "📋 停止服务: pkill -f 'python3 app.py'"
else
    echo "🔧 前台模式启动..."
    python3 app.py
fi
