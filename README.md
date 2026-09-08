# 21点知识库 (Blackjack Knowledge Base)

🃏 21点（Blackjack）综合知识库 — 规则、策略、算法、开源项目索引

## 目录结构

```
data/               # 种子数据（规则、策略表、算牌系统）
projects/           # GitHub项目索引表
api/                # 查询接口（FastAPI）
scrape/             # 数据爬取脚本
config/             # 配置文件
```

## 快速开始

```bash
pip install -r requirements.txt
python api/server.py          # 启动查询服务
python scrape/pull_basics.py  # 拉取基础策略数据
```

## 数据来源

- 百度百科 21点词条
- GitHub 开源项目
- Wizard of Odds 策略计算
- blackjack-gui / Blackjack-Strategy-Simulator
