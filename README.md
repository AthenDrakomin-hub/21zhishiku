# 21点知识库 (Blackjack Knowledge Base)

🃏 21点（Blackjack）综合知识库 — 规则、策略、算法、开源项目索引

## 目录结构

```
data/               # 种子数据（规则、策略表、算牌系统）
projects/           # GitHub项目索引表
api/                # 查询接口（HTTP）
scrape/             # 数据爬取脚本
config/             # 配置文件
```

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/AthenDrakomin-hub/21zhishiku.git
cd 21zhishiku

# 安装依赖
pip install -r requirements.txt

# 启动API服务
python api/server.py
# 访问: http://localhost:8000

# 或者使用uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

## API端点

| 端点 | 描述 |
|------|------|
| `GET /` | 服务信息 |
| `GET /rules` | 游戏规则和术语 |
| `GET /strategy?variant=s17` | 基本策略表 (s17/h17) |
| `GET /counting-systems` | 算牌系统列表 |
| `GET /counting-systems/{name}` | 特定算牌系统详情 |
| `GET /projects` | 开源项目索引 |
| `GET /projects/{name}` | 特定项目详情 |
| `GET /search?q=关键词` | 全局搜索 |
| `GET /stats` | 数据统计 |
| `GET /probabilities` | 概率数据 |
| `GET /history` | 历史资料 |
| `GET /deviations` | 偏差索引 (Illustrious 18 + Fab 4) |
| `GET /health` | 健康检查 |

## 数据来源

- 百度百科 21点词条
- GitHub 开源项目索引
- Wizard of Odds 策略计算
- Blackjack Apprenticeship 策略图表
- "Blackjack Attack" by Don Schlesinger

## 数据文件

| 文件 | 内容 |
|------|------|
| `data/rules.json` | 游戏规则、术语定义 |
| `data/basic_strategy_s17.csv` | S17基本策略表 |
| `data/basic_strategy_h17.csv` | H17基本策略表 |
| `data/card_counting_systems.json` | 9种算牌系统 |
| `data/deviation_indexes.json` | Illustrious 18 + Fab 4偏差索引 |
| `data/history.json` | 21点历史资料 |
| `data/probabilities.json` | 数学概率计算 |
| `data/projects.json` | GitHub项目索引 |

## 每日自动更新

已通过GitHub Actions配置每日自动更新：
- 定时：UTC 09:00 (北京时间 17:00)
- 功能：更新项目索引时间戳
- 手动触发：Workflow Dispatch

## License

MIT
