1.环境准备
# 安装必要软件
apt-get update
apt-get install -y docker docker-compose git

# 克隆代码
git clone [项目仓库]
cd coser_bot
2.配置环境变量
cp .env.prod .env
# 修改以下配置：
- TELEGRAM_BOT_TOKEN
- TELEGRAM_ADMIN_ID
- SMTP_USERNAME
- SMTP_PASSWORD
- MYSQL_PASSWORD
3.数据库初始化
# 创建数据库
docker-compose up -d mysql
./scripts/init_db.sh

# 执行数据库迁移
alembic upgrade head
4.启动服务
# 启动所有服务
docker-compose up -d

# 检查服务状态
docker-compose ps
5.验证部署
访问 http://localhost:8000/health 检查API状态
访问 http://localhost:3000 查看Grafana监控
访问 http://localhost:9090 检查Prometheus指标
使用Telegram测试机器人响应
6.监控和维护
使用 ./scripts/monitor.sh 检查系统状态
使用 ./scripts/backup.sh 执行数据备份
查看 ./logs 目录下的日志文件
