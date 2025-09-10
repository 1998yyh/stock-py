# 部署说明文档

## 🚀 简化部署方案

现在系统只有两个启动脚本，支持自动区分本地开发环境和生产环境。

### 📋 环境类型

| 环境 | 脚本 | 主机地址 | 访问地址 | 调试模式 |
|------|------|----------|----------|----------|
| 本地开发 | `start.sh` | `127.0.0.1:5000` | `http://localhost:5000` | ✅ 开启 |
| 生产环境 | `deploy.sh` | `0.0.0.0:5000` | `http://8.152.212.206:5000` | ❌ 关闭 |

---

## 🛠️ 本地开发

### 启动脚本：`start.sh`

```bash
# 前台运行（默认）
./start.sh

# 后台运行
./start.sh -b
./start.sh --background

# 查看帮助
./start.sh -h
```

### 特点
- 🔧 使用 `localhost:5000`
- 🐛 调试模式开启，代码修改自动重启
- 💛 页面右上角显示"本地开发环境"标识
- 📝 后台模式日志：`logs/app_local.log`

---

## 🌐 生产环境部署

### 部署脚本：`deploy.sh`

```bash
# 系统服务模式（推荐，需要root权限）
sudo ./deploy.sh -s
sudo ./deploy.sh --service

# 后台运行模式
./deploy.sh -b
./deploy.sh --background

# 前台运行模式
./deploy.sh -f
./deploy.sh --foreground

# 查看帮助
./deploy.sh -h
```

### 三种部署模式

#### 1. 系统服务模式（推荐）
- ✅ 开机自启动
- ✅ 自动重启
- ✅ 系统级管理
- ✅ 独立运行目录 `/opt/stock-app`

#### 2. 后台运行模式
- ✅ 在当前目录运行
- ✅ nohup后台执行
- ✅ 日志文件：`logs/app_production.log`

#### 3. 前台运行模式
- ✅ 实时查看输出
- ✅ 适合调试部署问题

---

## 📁 核心文件

- `config.py` - 环境配置管理
- `app.py` - Flask应用主文件
- `start.sh` - 本地开发启动脚本
- `deploy.sh` - 生产环境部署脚本
- `templates/index.html` - 前端页面（支持动态配置）

---

## 🔍 环境识别

### 自动识别
- 前端页面右上角显示环境标识
- 启动时控制台输出环境信息
- API端点: `/api/config/env`

### 手动设置（可选）
```bash
# 本地环境
export DEPLOY_ENV=local

# 生产环境
export DEPLOY_ENV=production
```

---

## 📊 监控和管理

### 系统服务管理
```bash
# 查看状态
sudo systemctl status stock-service

# 查看日志
sudo journalctl -u stock-service -f

# 重启服务
sudo systemctl restart stock-service

# 停止服务
sudo systemctl stop stock-service
```

### 后台进程管理
```bash
# 查看进程
ps aux | grep app.py

# 查看日志
tail -f logs/app_*.log

# 停止进程
kill <进程ID>
```

---

## 🚨 使用示例

### 本地开发
```bash
# 前台运行，适合开发调试
./start.sh

# 后台运行，适合长期测试
./start.sh -b
```

### 生产部署
```bash
# 一键部署为系统服务（推荐）
sudo ./deploy.sh

# 简单后台运行
./deploy.sh -b

# 临时前台运行
./deploy.sh -f
```

---

## 🆘 故障排除

### 常见问题
1. **端口被占用**: `netstat -tlnp | grep 5000`
2. **防火墙阻拦**: `ufw allow 5000` 或配置云服务器安全组
3. **权限不足**: 系统服务模式需要 `sudo` 权限
4. **文件缺失**: 确保在项目根目录运行脚本

### 查看日志
```bash
# 本地开发
tail -f logs/app_local.log

# 生产后台
tail -f logs/app_production.log

# 系统服务
sudo journalctl -u stock-service -f
```
