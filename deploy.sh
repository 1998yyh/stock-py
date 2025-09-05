#!/bin/bash

# 股票筛选系统服务器部署脚本
# 适用于 Ubuntu/Debian 和 CentOS/RHEL 系统

echo "🚀 开始部署股票筛选系统..."

# 检测操作系统
if [ -f /etc/debian_version ]; then
    OS="debian"
    echo "📋 检测到 Debian/Ubuntu 系统"
elif [ -f /etc/redhat-release ]; then
    OS="redhat"
    echo "📋 检测到 RedHat/CentOS 系统"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 更新系统包
echo "📦 更新系统包..."
if [ "$OS" = "debian" ]; then
    sudo apt update && sudo apt upgrade -y
elif [ "$OS" = "redhat" ]; then
    sudo yum update -y
fi

# 安装 Python3 和 pip
echo "🐍 安装 Python3 和相关工具..."
if [ "$OS" = "debian" ]; then
    sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential
    sudo apt install -y libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
elif [ "$OS" = "redhat" ]; then
    sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make
    sudo yum install -y openssl-devel libffi-devel libxml2-devel libxslt-devel zlib-devel
fi

# 检查 Python3 版本
python3_version=$(python3 --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 1,2)
echo "🔍 Python3 版本: $python3_version"

if [ "$(echo "$python3_version >= 3.8" | bc -l 2>/dev/null)" != "1" ]; then
    echo "⚠️ Python 版本可能较低，建议使用 Python 3.8+"
fi

# 创建虚拟环境
echo "📁 创建虚拟环境..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ 虚拟环境创建成功"
else
    echo "ℹ️ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装 Python 依赖包..."
pip install -r requirements.txt

# 创建必要的目录
echo "📂 创建必要目录..."
mkdir -p data
mkdir -p logs
mkdir -p templates

# 设置权限
echo "🔐 设置文件权限..."
chmod +x start.sh
chmod +x deploy.sh

# 创建系统服务文件（可选）
if command -v systemctl >/dev/null 2>&1; then
    echo "🔧 创建系统服务配置..."
    cat > stock-filter.service << EOF
[Unit]
Description=Stock Filter Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/.venv/bin/python $(pwd)/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo "📋 系统服务配置已创建: stock-filter.service"
    echo "   要安装服务，请运行："
    echo "   sudo cp stock-filter.service /etc/systemd/system/"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable stock-filter"
    echo "   sudo systemctl start stock-filter"
fi

# 检查防火墙设置
echo "🔥 检查防火墙设置..."
if command -v ufw >/dev/null 2>&1; then
    echo "   Ubuntu/Debian 防火墙配置:"
    echo "   sudo ufw allow 5000"
elif command -v firewall-cmd >/dev/null 2>&1; then
    echo "   CentOS/RHEL 防火墙配置:"
    echo "   sudo firewall-cmd --permanent --add-port=5000/tcp"
    echo "   sudo firewall-cmd --reload"
fi

# 测试安装
echo "🧪 测试安装..."
python3 -c "
try:
    import flask, pandas, numpy, akshare
    print('✅ 所有依赖包安装成功')
except ImportError as e:
    print(f'❌ 依赖包安装失败: {e}')
"

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 启动服务: ./start.sh 或 python3 app.py"
echo "2. 访问地址: http://服务器IP:5000"
echo "3. 如需后台运行: nohup python3 app.py > logs/app.log 2>&1 &"
echo ""
echo "📝 注意事项："
echo "- 确保服务器的 5000 端口已开放"
echo "- 如果遇到网络问题，可能需要配置代理"
echo "- 建议使用 nginx 作为反向代理"
echo ""
