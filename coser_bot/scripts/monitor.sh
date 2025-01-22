#!/bin/bash

# 监控脚本

# 检查容器状态
echo "检查容器状态..."
docker-compose ps

# 检查容器资源使用情况
echo -e "\n容器资源使用情况:"
docker stats --no-stream

# 检查日志文件大小
echo -e "\n日志文件大小:"
du -sh logs/*

# 检查数据库大小
echo -e "\nMySQL数据库大小:"
docker-compose exec mysql mysql -u root -p${MYSQL_PASSWORD} -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables GROUP BY table_schema;"

# 检查Redis内存使用
echo -e "\nRedis内存使用情况:"
docker-compose exec redis redis-cli info memory | grep "used_memory_human"

# 检查MongoDB数据库大小
echo -e "\nMongoDB数据库大小:"
docker-compose exec mongodb mongo --eval "db.stats()"

# 检查系统资源
echo -e "\n系统资源使用情况:"
echo "CPU使用率:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
echo "内存使用率:"
free -m | awk 'NR==2{printf "%.2f%%\n", $3*100/$2}'
echo "磁盘使用率:"
df -h | grep -v "tmpfs"
