#!/bin/bash

# 股票筛选系统生产环境部署脚本

# 显示使用说明
show_help() {
    echo "🚀 股票筛选系统 - 生产环境部署脚本"
    echo "====================================="
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help         显示此帮助信息"
    echo "  -s, --service      安装为系统服务（推荐）"
    echo "  -b, --background   后台运行模式"
    echo "  -f, --foreground   前台运行模式"
    echo ""
    echo "示例:"
    echo "  $0 -s            # 安装为系统服务"
    echo "  $0 -b            # 后台运行"
    echo "  $0 -f            # 前台运行"
    echo ""
    echo "注意: 系统服务模式需要root权限"
    echo ""
}

# 参数解析
MODE="service"  # 默认模式
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--service)
            MODE="service"
            shift
            ;;
        -b|--background)
            MODE="background"
            shift
            ;;
        -f|--foreground)
            MODE="foreground"
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🚀 股票筛选系统 - 生产环境部署"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 设置生产环境变量
export DEPLOY_ENV=production

# 获取当前目录
CURRENT_DIR=$(pwd)

# 根据模式设置应用目录和用户权限
if [ "$MODE" = "service" ]; then
    # 系统服务模式 - 需要root权限
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}系统服务模式需要root权限，请使用 sudo 运行${NC}"
        exit 1
    fi
    APP_DIR="/opt/stock-app"
else
    # 简单部署模式 - 在当前目录
    APP_DIR="$CURRENT_DIR"
fi

echo -e "${YELLOW}1. 准备应用环境...${NC}"
mkdir -p $APP_DIR/logs

if [ "$MODE" = "service" ]; then
    # 系统服务模式 - 复制文件到独立目录
    echo -e "${YELLOW}2. 复制应用文件到 $APP_DIR ...${NC}"
    cp app.py $APP_DIR/
    cp stock.py $APP_DIR/
    cp config.py $APP_DIR/
    cp requirements.txt $APP_DIR/
    cp -r templates $APP_DIR/
    cp -r data $APP_DIR/ 2>/dev/null || mkdir -p $APP_DIR/data
else
    # 简单部署模式 - 在当前目录运行
    echo -e "${YELLOW}2. 检查应用文件...${NC}"
    if [ ! -f "app.py" ] || [ ! -f "config.py" ]; then
        echo -e "${RED}缺少必要文件，请在项目根目录运行此脚本${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}3. 创建虚拟环境...${NC}"
cd $APP_DIR
python3 -m venv .venv
source .venv/bin/activate

echo -e "${YELLOW}4. 安装Python依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

if [ "$MODE" = "service" ]; then
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
Environment=DEPLOY_ENV=production
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=stock-service

[Install]
WantedBy=multi-user.target
EOF
fi

# 根据运行模式执行相应操作
if [ "$MODE" = "service" ]; then
    # 系统服务模式
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
        echo -e "${GREEN}🎉 系统服务部署完成！${NC}"
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        echo "查看错误日志: journalctl -u stock-service"
        exit 1
    fi

elif [ "$MODE" = "background" ]; then
    # 后台运行模式
    echo -e "${YELLOW}6. 启动后台服务...${NC}"
    
    # 停止之前的进程（如果存在）
    echo "🔄 检查并停止旧进程..."
    PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PID" ]; then
        echo "停止旧进程: $PID"
        kill $PID
        sleep 2
    fi
    
    # 使用nohup后台运行
    DEPLOY_ENV=production nohup python app.py > logs/app_production.log 2>&1 &
    
    # 获取新进程PID
    sleep 2
    NEW_PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$NEW_PID" ]; then
        echo -e "${GREEN}✅ 生产环境服务启动成功！${NC}"
        echo "进程ID: $NEW_PID"
        echo "访问地址: http://8.152.212.206:5000"
        echo "日志文件: $APP_DIR/logs/app_production.log"
        echo ""
        echo "📋 管理命令："
        echo "  查看日志: tail -f $APP_DIR/logs/app_production.log"
        echo "  停止服务: kill $NEW_PID"
        echo "  查看进程: ps aux | grep app.py"
        echo ""
        echo -e "${GREEN}🎉 后台部署完成！${NC}"
    else
        echo -e "${RED}❌ 服务启动失败，请检查日志: $APP_DIR/logs/app_production.log${NC}"
        exit 1
    fi

else
    # 前台运行模式
    echo -e "${YELLOW}6. 启动生产环境服务...${NC}"
    echo "访问地址: http://8.152.212.206:5000"
    echo "按 Ctrl+C 停止服务"
    echo ""
    echo -e "${GREEN}🎉 开始运行...${NC}"
    python app.py
fi
