# 快速安装指南

## 🚀 一键部署命令

### 在服务器上运行以下命令：

```bash
# 1. 下载项目（如果使用git）
git clone <your-repo-url> stock-filter
cd stock-filter

# 2. 一键部署
chmod +x deploy.sh && ./deploy.sh

# 3. 启动服务
./start.sh production  # 生产环境
```

## 📋 手动安装步骤

### 1. 系统要求
- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- **Python**: 3.8+
- **内存**: 最少 512MB
- **磁盘**: 最少 1GB

### 2. 安装 Python 环境

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3 python3-pip
```

### 3. 部署项目

```bash
# 创建项目目录
mkdir -p ~/stock-filter
cd ~/stock-filter

# 复制项目文件到此目录

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 app.py
```

### 4. 访问服务

打开浏览器访问：`http://服务器IP:5000`

## 🔧 常用命令

```bash
# 启动服务（前台）
./start.sh

# 启动服务（后台）
./start.sh production

# 查看服务状态
ps aux | grep python

# 停止服务
pkill -f "python3 app.py"

# 查看日志
tail -f logs/app.log
```

## ⚡ 快速测试

部署完成后，可以运行以下命令测试：

```bash
curl http://localhost:5000/api/config
```

如果返回JSON数据，说明服务正常运行。

## 🆘 遇到问题？

1. **检查端口是否被占用**:
   ```bash
   netstat -tlnp | grep :5000
   ```

2. **检查防火墙设置**:
   ```bash
   sudo ufw status  # Ubuntu
   sudo firewall-cmd --list-ports  # CentOS
   ```

3. **查看详细日志**:
   ```bash
   tail -f logs/app.log
   ```
