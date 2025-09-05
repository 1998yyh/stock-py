#!/bin/bash

# 阿里云 Linux 3.2104 LTS 专用安装脚本
# 解决依赖安装问题

echo "🌐 阿里云 Linux 3.2104 LTS 环境配置..."

# 检查系统版本
echo "📋 系统信息:"
cat /etc/os-release

# 更新系统包
echo "📦 更新系统包..."
sudo yum update -y

# 安装开发工具和必要依赖
echo "🔧 安装开发工具..."
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip python3-devel
sudo yum install -y openssl-devel libffi-devel zlib-devel
sudo yum install -y libxml2-devel libxslt-devel
sudo yum install -y gcc gcc-c++ make cmake

# 安装额外的开发库（akshare需要）
echo "📚 安装额外开发库..."
sudo yum install -y bzip2-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel

# 升级pip到最新版本
echo "⬆️ 升级pip..."
python3 -m pip install --upgrade pip --user
export PATH=$HOME/.local/bin:$PATH

# 配置阿里云pip镜像源
echo "🔧 配置阿里云pip源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
EOF

# 安装基础Python包
echo "📥 安装基础Python包..."
pip3 install --user setuptools wheel --upgrade

# 方法1: 尝试直接安装所有依赖
echo "🎯 方法1: 尝试直接安装..."
pip3 install --user Flask==2.0.3 Flask-CORS==3.0.10 pandas

# 尝试安装akshare（可能需要较长时间）
echo "📈 安装akshare (可能需要几分钟)..."
pip3 install --user akshare || {
    echo "❌ akshare安装失败，尝试替代方案..."
    
    # 方法2: 先安装akshare的依赖
    echo "📦 安装akshare依赖..."
    pip3 install --user requests beautifulsoup4 lxml pandas numpy
    pip3 install --user demjson
    pip3 install --user multitasking
    
    # 再次尝试安装akshare
    pip3 install --user akshare || {
        echo "❌ akshare仍然安装失败"
        echo "💡 将使用模拟数据模式"
        AKSHARE_FAILED=1
    }
}

# 创建虚拟环境（推荐方式）
echo "🐍 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 在虚拟环境中安装依赖
echo "📦 在虚拟环境中安装依赖..."
pip install --upgrade pip
pip install Flask==2.0.3 Flask-CORS==3.0.10 pandas

# 尝试在虚拟环境中安装akshare
pip install akshare || {
    echo "⚠️ 虚拟环境中akshare安装也失败"
    echo "💡 创建不依赖akshare的版本..."
    
    # 创建简化版requirements
    cat > requirements_aliyun.txt << EOF
Flask==2.0.3
Flask-CORS==3.0.10
pandas>=1.3.0
requests>=2.25.0
EOF
    
    pip install -r requirements_aliyun.txt
    AKSHARE_FAILED=1
}

# 测试安装结果
echo "🧪 测试安装结果..."
python3 -c "
import sys
success = True
try:
    import flask
    print('✅ Flask: ', flask.__version__)
except ImportError as e:
    print('❌ Flask导入失败:', e)
    success = False

try:
    import flask_cors
    print('✅ Flask-CORS 导入成功')
except ImportError as e:
    print('❌ Flask-CORS导入失败:', e)
    success = False

try:
    import pandas as pd
    print('✅ pandas: ', pd.__version__)
except ImportError as e:
    print('❌ pandas导入失败:', e)
    success = False

try:
    import akshare as ak
    print('✅ akshare 导入成功')
except ImportError as e:
    print('⚠️ akshare导入失败，将使用模拟数据:', e)

if success:
    print('🎉 基础依赖安装成功！')
else:
    print('❌ 部分依赖安装失败')
    sys.exit(1)
"

# 如果akshare安装失败，设置模拟模式
if [ "$AKSHARE_FAILED" = "1" ]; then
    echo "🎭 配置模拟数据模式..."
    if [ -f "stock.py" ]; then
        cp stock.py stock_original.py
    fi
    if [ -f "stock_minimal.py" ]; then
        cp stock_minimal.py stock.py
    fi
fi

# 创建启动脚本
echo "📝 创建阿里云启动脚本..."
cat > start_aliyun.sh << 'EOF'
#!/bin/bash
echo "🚀 在阿里云环境启动股票筛选系统..."

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
    echo "❌ 依赖检查失败，请重新运行安装脚本"
    exit 1
fi

# 启动服务
echo "🌐 启动服务..."
echo "访问地址: http://$(curl -s ifconfig.me):5000"
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
EOF

chmod +x start_aliyun.sh

echo ""
echo "🎉 阿里云环境配置完成！"
echo ""
echo "📋 使用说明:"
echo "1. 前台启动: ./start_aliyun.sh"
echo "2. 后台启动: ./start_aliyun.sh background"
echo "3. 查看日志: tail -f logs/app.log"
echo "4. 停止服务: pkill -f 'python3 app.py'"
echo ""
echo "🔧 防火墙配置:"
echo "sudo firewall-cmd --permanent --add-port=5000/tcp"
echo "sudo firewall-cmd --reload"
echo ""
echo "📱 安全组配置:"
echo "在阿里云控制台添加安全组规则，开放5000端口"
echo ""
