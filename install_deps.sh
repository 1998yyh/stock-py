#!/bin/bash

# 股票筛选系统依赖安装脚本
# 解决 akshare 安装问题

echo "🔧 解决 akshare 安装问题..."

# 方法1: 更换pip源到国内镜像
echo "📦 配置国内pip源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF

echo "✅ pip源配置完成"

# 方法2: 升级pip和setuptools
echo "⬆️ 升级pip和相关工具..."
python3 -m pip install --upgrade pip
pip install --upgrade setuptools wheel

# 方法3: 分步安装依赖
echo "📥 开始安装依赖包..."

echo "1/4 安装 Flask..."
pip install Flask==2.0.3 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "2/4 安装 Flask-CORS..."
pip install Flask-CORS==3.0.10 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "3/4 安装 pandas..."
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "4/4 安装 akshare..."
# 尝试多个源
pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple/ || \
pip install akshare -i https://mirrors.aliyun.com/pypi/simple/ || \
pip install akshare -i https://pypi.douban.com/simple/ || \
pip install akshare --index-url https://pypi.org/simple/

# 验证安装
echo "🧪 验证安装结果..."
python3 -c "
try:
    import flask
    print('✅ Flask 安装成功')
    import flask_cors
    print('✅ Flask-CORS 安装成功')
    import pandas
    print('✅ pandas 安装成功')
    import akshare
    print('✅ akshare 安装成功')
    print('🎉 所有依赖安装成功！')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装验证通过"
else
    echo "❌ 依赖安装验证失败，尝试备用方案..."
    
    # 备用方案：使用conda
    if command -v conda >/dev/null 2>&1; then
        echo "🐍 检测到conda，尝试使用conda安装..."
        conda install -c conda-forge pandas flask flask-cors -y
        pip install akshare
    else
        echo "💡 建议安装方案："
        echo "1. 检查网络连接"
        echo "2. 尝试使用代理"
        echo "3. 手动下载wheel文件安装"
    fi
fi
