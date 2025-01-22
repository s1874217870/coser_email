#!/bin/bash

# 备份脚本

# 设置备份目录
BACKUP_DIR="/backup/coser_bot"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份MySQL数据
echo "备份MySQL数据..."
docker-compose exec -T mysql mysqldump -u root -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > $BACKUP_DIR/mysql_${DATE}.sql

# 备份MongoDB数据
echo "备份MongoDB数据..."
docker-compose exec -T mongodb mongodump --out /dump
docker cp $(docker-compose ps -q mongodb):/dump $BACKUP_DIR/mongodb_${DATE}

# 备份Redis数据
echo "备份Redis数据..."
docker-compose exec -T redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_DIR/redis_${DATE}.rdb

# 压缩备份文件
echo "压缩备份文件..."
cd $BACKUP_DIR
tar czf backup_${DATE}.tar.gz mysql_${DATE}.sql mongodb_${DATE} redis_${DATE}.rdb

# 清理临时文件
rm -rf mysql_${DATE}.sql mongodb_${DATE} redis_${DATE}.rdb

echo "备份完成！文件保存在: $BACKUP_DIR/backup_${DATE}.tar.gz"
