# 阿里云Linux安装指南

## 🌐 适用系统
- **Alibaba Cloud Linux 3.2104 LTS 64位**
- **CentOS 7/8**
- **RHEL 7/8**

## 🚀 一键安装

### 在阿里云服务器上运行：

```bash
# 1. 上传项目文件到服务器
# 2. 运行安装脚本
chmod +x install_aliyun.sh
./install_aliyun.sh

# 3. 配置防火墙
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 4. 启动服务
./start_aliyun.sh background  # 后台运行
```

## 📱 阿里云安全组配置

在阿里云控制台：
1. 进入 **ECS管理控制台**
2. 选择 **网络与安全** > **安全组**  
3. 点击 **配置规则**
4. 添加入方向规则：
   - **协议类型**: TCP
   - **端口范围**: 5000/5000
   - **授权对象**: 0.0.0.0/0

## 🔧 常用命令

```bash
# 前台启动
./start_aliyun.sh

# 后台启动  
./start_aliyun.sh background

# 查看服务状态
ps aux | grep python

# 停止服务
pkill -f "python3 app.py"

# 查看日志
tail -f logs/app.log
```

## ⚡ 快速测试

```bash
# 本地测试
curl http://localhost:5000/api/config

# 外网测试（替换为您的公网IP）
curl http://your-server-ip:5000/api/config
```

## 🆘 常见问题

1. **编译错误**:
   ```bash
   sudo yum install -y gcc gcc-c++ python3-devel
   ```

2. **akshare安装失败**:
   ```bash
   # 系统会自动切换到模拟数据模式
   # 检查是否使用了 stock_minimal.py
   ```

3. **访问被拒绝**:
   ```bash
   # 检查防火墙和安全组设置
   sudo firewall-cmd --list-ports
   ```
