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

# 检查依赖是否已安装
echo "🔍 检查依赖包..."
python3 -c "
import sys
try:
    import flask, pandas, numpy, akshare
    print('✅ 依赖包检查通过')
except ImportError as e:
    print(f'❌ 缺少依赖包: {e}')
    print('正在安装依赖包...')
    sys.exit(1)
" || {
    echo "📥 安装依赖包..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# 创建必要目录
mkdir -p data logs

# 启动服务
echo "🌐 启动Web服务..."
echo "访问地址: http://localhost:5000"
echo "日志文件: logs/app.log"
echo "按 Ctrl+C 停止服务"
echo ""

# 检查是否在服务器环境（有DISPLAY变量说明是桌面环境）
if [ -z "$DISPLAY" ] && [ "$1" = "production" ]; then
    echo "🔧 生产环境模式启动..."
    nohup python3 app.py > logs/app.log 2>&1 &
    echo "✅ 服务已在后台启动"
    echo "📋 查看日志: tail -f logs/app.log"
    echo "📋 停止服务: pkill -f 'python3 app.py'"
else
    echo "🔧 开发环境模式启动..."
    python3 app.py
fi
