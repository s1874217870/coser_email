#!/bin/bash

# 恢复脚本

if [ -z "$1" ]; then
    echo "请提供备份文件路径"
    echo "用法: ./restore.sh /path/to/backup_file.tar.gz"
    exit 1
fi

BACKUP_FILE=$1
TEMP_DIR="/tmp/coser_bot_restore"

# 创建临时目录
mkdir -p $TEMP_DIR

# 解压备份文件
echo "解压备份文件..."
tar xzf $BACKUP_FILE -C $TEMP_DIR

# 恢复MySQL数据
echo "恢复MySQL数据..."
cat $TEMP_DIR/mysql_*.sql | docker-compose exec -T mysql mysql -u root -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}

# 恢复MongoDB数据
echo "恢复MongoDB数据..."
docker cp $TEMP_DIR/mongodb_* $(docker-compose ps -q mongodb):/dump
docker-compose exec -T mongodb mongorestore /dump

# 恢复Redis数据
echo "恢复Redis数据..."
docker-compose stop redis
docker cp $TEMP_DIR/redis_*.rdb $(docker-compose ps -q redis):/data/dump.rdb
docker-compose start redis

# 清理临时文件
rm -rf $TEMP_DIR

echo "恢复完成！"
