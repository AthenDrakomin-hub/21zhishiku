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
pip install -r requirements.txt

# 拉取数据
echo "🔄 拉取种子数据..."
python3 scrape/pull_basics.py

# 启动服务
echo "🚀 启动API服务..."
python3 api/server.py
