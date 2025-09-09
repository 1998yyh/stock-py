#!/bin/bash

# 使用screen在后台运行股票筛选系统

echo "🚀 使用screen启动股票筛选系统..."

# 检查screen是否安装
if ! command -v screen &> /dev/null; then
    echo "📦 安装screen..."
    # Ubuntu/Debian
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y screen
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        sudo yum install -y screen
    else
        echo "❌ 请手动安装screen: sudo apt install screen 或 sudo yum install screen"
        exit 1
    fi
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 创建启动脚本
cat > start_app.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
pip install Flask==2.3.3 Flask-CORS==4.0.0 pandas numpy akshare
python app.py
EOF

chmod +x start_app.sh

# 杀死已存在的screen会话
screen -S stock-app -X quit 2>/dev/null || true

# 在screen中启动应用
echo "🌐 在screen会话中启动服务..."
screen -dmS stock-app bash -c './start_app.sh'

sleep 3

# 检查screen会话是否存在
if screen -list | grep -q "stock-app"; then
    echo "✅ 服务启动成功！"
    echo "Screen会话名: stock-app"
    echo "访问地址: http://8.152.212.206:5000"
    echo ""
    echo "📋 管理命令："
    echo "  查看会话: screen -r stock-app"
    echo "  分离会话: Ctrl+A, 然后按D"
    echo "  停止服务: screen -S stock-app -X quit"
    echo "  列出会话: screen -list"
else
    echo "❌ 服务启动失败"
fi
