# 股票筛选系统服务器部署指南

## 🚀 快速部署

### 方法一：使用自动部署脚本（推荐）

```bash
# 1. 上传项目文件到服务器
scp -r /path/to/pz/ user@server:/path/to/deployment/

# 2. 登录服务器
ssh user@server

# 3. 进入项目目录
cd /path/to/deployment/pz/

# 4. 给脚本执行权限
chmod +x deploy.sh start.sh

# 5. 运行部署脚本
./deploy.sh

# 6. 启动服务
./start.sh production  # 生产环境（后台运行）
# 或
./start.sh             # 开发环境（前台运行）
```

### 方法二：手动部署

#### 1. 系统环境准备

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y libxml2-dev libxslt1-dev zlib1g-dev
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel
sudo yum install -y gcc gcc-c++ make openssl-devel libffi-devel
sudo yum install -y libxml2-devel libxslt-devel zlib-devel
```

#### 2. 项目部署

```bash
# 创建项目目录
mkdir -p /opt/stock-filter
cd /opt/stock-filter

# 上传项目文件
# (使用scp, rsync或git clone)

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要目录
mkdir -p data logs

# 测试启动
python3 app.py
```

## 🔧 配置说明

### 环境变量配置

可以通过环境变量自定义配置：

```bash
export FLASK_HOST=0.0.0.0        # 监听地址
export FLASK_PORT=5000           # 监听端口  
export FLASK_DEBUG=False         # 生产环境关闭调试
export DATA_DIR=/opt/data        # 数据目录
```

### 防火墙配置

**Ubuntu/Debian (ufw):**
```bash
sudo ufw allow 5000
sudo ufw reload
```

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 🔧 系统服务配置

### 创建 systemd 服务

```bash
# 创建服务文件
sudo vim /etc/systemd/system/stock-filter.service
```

服务文件内容：
```ini
[Unit]
Description=Stock Filter Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/stock-filter
ExecStart=/opt/stock-filter/.venv/bin/python /opt/stock-filter/app.py
Restart=always
RestartSec=10
Environment=FLASK_HOST=0.0.0.0
Environment=FLASK_PORT=5000
Environment=FLASK_DEBUG=False

[Install]
WantedBy=multi-user.target
```

### 启用和管理服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable stock-filter

# 启动服务
sudo systemctl start stock-filter

# 查看状态
sudo systemctl status stock-filter

# 查看日志
sudo journalctl -u stock-filter -f

# 停止服务
sudo systemctl stop stock-filter

# 重启服务
sudo systemctl restart stock-filter
```

## 🌐 Nginx 反向代理配置（推荐）

### 安装 Nginx

**Ubuntu/Debian:**
```bash
sudo apt install -y nginx
```

**CentOS/RHEL:**
```bash
sudo yum install -y nginx
```

### 配置反向代理

创建配置文件：
```bash
sudo vim /etc/nginx/sites-available/stock-filter
```

配置内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location /static {
        alias /opt/stock-filter/static;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用配置：
```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/stock-filter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# CentOS/RHEL  
sudo cp /etc/nginx/sites-available/stock-filter /etc/nginx/conf.d/stock-filter.conf
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 监控和日志

### 日志文件位置
- 应用日志: `/opt/stock-filter/logs/app.log`
- Nginx日志: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- 系统日志: `sudo journalctl -u stock-filter`

### 实时监控
```bash
# 查看应用日志
tail -f /opt/stock-filter/logs/app.log

# 查看系统服务状态
watch -n 2 'systemctl status stock-filter'

# 查看端口占用
netstat -tlnp | grep :5000
```

## 🔐 安全建议

1. **使用非root用户运行**
2. **配置防火墙，只开放必要端口**
3. **使用Nginx反向代理**
4. **定期更新依赖包**
5. **配置SSL证书（HTTPS）**
6. **设置日志轮转**

### SSL证书配置（Let's Encrypt）

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 🚨 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **依赖包安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt -v
   ```

3. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /opt/stock-filter
   sudo chmod -R 755 /opt/stock-filter
   ```

4. **网络连接问题**
   - 检查防火墙设置
   - 检查代理配置
   - 验证DNS解析

### 性能优化

1. **使用 Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **配置缓存**
   - 启用数据缓存
   - 配置Redis（可选）

3. **数据库优化**
   - 定期清理老旧缓存文件
   - 配置数据备份

## 📞 技术支持

如遇到问题，请检查：
1. 系统日志：`sudo journalctl -u stock-filter`
2. 应用日志：`tail -f logs/app.log`
3. 网络连接：`curl http://localhost:5000`
4. 端口状态：`netstat -tlnp | grep :5000`
