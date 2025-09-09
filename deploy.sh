#!/bin/bash

# 股票筛选系统生产环境部署脚本

echo "🚀 股票筛选系统 - 生产环境部署"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

# 获取当前目录
CURRENT_DIR=$(pwd)
APP_DIR="/opt/stock-app"

echo -e "${YELLOW}1. 创建应用目录...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs

echo -e "${YELLOW}2. 复制应用文件...${NC}"
cp app.py $APP_DIR/
cp stock.py $APP_DIR/
cp requirements.txt $APP_DIR/
cp -r templates $APP_DIR/
cp -r data $APP_DIR/ 2>/dev/null || mkdir -p $APP_DIR/data

echo -e "${YELLOW}3. 创建虚拟环境...${NC}"
cd $APP_DIR
python3 -m venv .venv
source .venv/bin/activate

echo -e "${YELLOW}4. 安装Python依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}5. 创建systemd服务...${NC}"
cat > /etc/systemd/system/stock-service.service << EOF
[Unit]
Description=Stock Screening System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/.venv/bin
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=stock-service

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}6. 配置防火墙...${NC}"
# Ubuntu/Debian
if command -v ufw &> /dev/null; then
    ufw allow 5000
    echo "防火墙规则已添加 (UFW)"
# CentOS/RHEL
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=5000/tcp
    firewall-cmd --reload
    echo "防火墙规则已添加 (firewalld)"
else
    echo "请手动配置防火墙开放5000端口"
fi

echo -e "${YELLOW}7. 启用并启动服务...${NC}"
systemctl daemon-reload
systemctl enable stock-service
systemctl start stock-service

# 等待服务启动
sleep 3

echo -e "${YELLOW}8. 检查服务状态...${NC}"
if systemctl is-active --quiet stock-service; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo ""
    echo "📋 服务信息："
    echo "  服务名称: stock-service"
    echo "  访问地址: http://8.152.212.206:5000"
    echo "  应用目录: $APP_DIR"
    echo "  日志目录: $APP_DIR/logs"
    echo ""
    echo "📋 管理命令："
    echo "  查看状态: systemctl status stock-service"
    echo "  查看日志: journalctl -u stock-service -f"
    echo "  重启服务: systemctl restart stock-service"
    echo "  停止服务: systemctl stop stock-service"
    echo "  开机启动: systemctl enable stock-service"
    echo ""
    echo -e "${GREEN}🎉 部署完成！${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看错误日志: journalctl -u stock-service"
    exit 1
fi
