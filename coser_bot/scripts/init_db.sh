#!/bin/bash

# 等待MySQL服务就绪
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h"$MYSQL_HOST" --silent; do
    sleep 1
done

# 运行数据库迁移
echo "Running database migrations..."
alembic upgrade head

# 初始化Redis
echo "Initializing Redis..."
redis-cli -h $REDIS_HOST flushall

echo "Database initialization completed!"
