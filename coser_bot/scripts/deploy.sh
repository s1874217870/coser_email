#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查Docker和Docker Compose是否安装
echo -e "${YELLOW}检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose未安装，正在安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 检查环境文件
echo -e "${YELLOW}检查环境配置...${NC}"
if [ ! -f .env.prod ]; then
    echo -e "${RED}未找到.env.prod文件${NC}"
    exit 1
fi

# 创建必要的目录
echo -e "${YELLOW}创建必要的目录...${NC}"
mkdir -p logs
mkdir -p backup

# 停止并删除旧容器
echo -e "${YELLOW}清理旧容器...${NC}"
docker-compose down --remove-orphans

# 构建新镜像
echo -e "${YELLOW}构建Docker镜像...${NC}"
docker-compose build --no-cache

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待数据库服务就绪
echo -e "${YELLOW}等待数据库服务就绪...${NC}"
sleep 10

# 执行数据库迁移
echo -e "${YELLOW}执行数据库迁移...${NC}"
docker-compose exec -T app alembic upgrade head

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose ps

# 输出访问信息
echo -e "${GREEN}部署完成！${NC}"
echo -e "管理后台: http://localhost:8000/admin"
echo -e "API文档: http://localhost:8000/docs"
echo -e "监控面板: http://localhost:9090"
echo -e "Grafana: http://localhost:3000"
echo -e "RabbitMQ管理界面: http://localhost:15672"

# 输出日志访问方式
echo -e "\n${YELLOW}查看服务日志:${NC}"
echo "docker-compose logs -f app"

# 设置脚本权限
chmod +x scripts/*.sh
