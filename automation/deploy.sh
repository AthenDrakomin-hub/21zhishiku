#!/bin/bash
# 21点自动化玩家部署脚本

set -e

echo "🃏 21点自动化玩家部署"
echo "======================"

cd "$(dirname "$0")"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install

echo "✅ 部署完成"
echo ""
echo "使用方法:"
echo "  python3 browser_bot.py"
echo ""
