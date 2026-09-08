#!/bin/bash
# 21点知识库部署脚本

set -e

echo "🃏 21点知识库部署脚本"
echo "====================="

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q fastapi uvicorn httpx

# 初始化数据库
echo "🗄️  初始化SQLite数据库..."
python3 api/init_db.py

# 启动服务
echo "🚀 启动API服务..."
echo "API地址: http://localhost:8000"
echo "数据库: knowledge_base.db"
echo ""
python3 api/server.py
