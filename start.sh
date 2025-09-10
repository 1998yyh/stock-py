#!/bin/bash

# 股票筛选系统本地开发启动脚本

# 显示使用说明
show_help() {
    echo "🚀 股票筛选系统 - 本地开发启动脚本"
    echo "========================================="
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -b, --background   后台运行模式"
    echo "  -f, --foreground   前台运行模式（默认）"
    echo ""
    echo "示例:"
    echo "  $0              # 前台运行"
    echo "  $0 -b           # 后台运行"
    echo "  $0 --background # 后台运行"
    echo ""
}

# 参数解析
BACKGROUND=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--background)
            BACKGROUND=true
            shift
            ;;
        -f|--foreground)
            BACKGROUND=false
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🚀 股票筛选系统 - 本地开发环境"
echo "=================================="

# 设置本地环境变量
export DEPLOY_ENV=local

# 创建必要目录
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

if [ "$BACKGROUND" = true ]; then
    # 后台运行模式
    echo "🌐 启动本地后台服务..."
    
    # 停止之前的进程（如果存在）
    echo "🔄 检查并停止旧进程..."
    PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PID" ]; then
        echo "停止旧进程: $PID"
        kill $PID
        sleep 2
    fi
    
    # 使用nohup后台运行
    DEPLOY_ENV=local nohup python app.py > logs/app_local.log 2>&1 &
    
    # 获取新进程PID
    sleep 2
    NEW_PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$NEW_PID" ]; then
        echo "✅ 本地服务启动成功！"
        echo "进程ID: $NEW_PID"
        echo "访问地址: http://localhost:5000"
        echo "日志文件: logs/app_local.log"
        echo ""
        echo "📋 管理命令："
        echo "  查看日志: tail -f logs/app_local.log"
        echo "  停止服务: kill $NEW_PID"
        echo "  查看进程: ps aux | grep app.py"
    else
        echo "❌ 服务启动失败，请检查日志: logs/app_local.log"
    fi
else
    # 前台运行模式
    echo "🌐 启动本地开发服务..."
    echo "访问地址: http://localhost:5000"
    echo "按 Ctrl+C 停止服务"
    echo ""
    python app.py
fi
