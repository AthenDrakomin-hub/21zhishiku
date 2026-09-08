# 21点知识库 (Blackjack Knowledge Base)

🃏 21点（Blackjack）综合知识库 — SQLite数据库 + REST API

**GitHub**: https://github.com/AthenDrakomin-hub/21zhishiku.git

## 数据库结构

```
knowledge_base.db
├── rules            # 游戏规则、术语 (~30条)
├── strategy         # 基本策略表 S17/H17 (220+条)
├── counting_systems # 算牌系统 (9种)
├── projects         # 开源项目索引 (45个)
├── deviations       # 偏差索引 Illustrious18+F4 (22条)
├── history          # 历史资料 (里程碑、名人)
├── probabilities    # 概率数据
└── search_index     # FTS5全文搜索
```

## 快速开始

```bash
# 初始化数据库
python3 api/init_db.py

# 启动API
python3 api/server.py
# 访问: http://localhost:8000
```

## API端点

| 端点 | 描述 |
|------|------|
| `GET /` | 服务信息 |
| `GET /health` | 健康检查 |
| `GET /rules` | 所有规则术语 |
| `GET /strategy?variant=s17` | 基本策略表 |
| `GET /counting-systems` | 算牌系统列表 |
| `GET /projects` | 45个项目索引 |
| `GET /search?q=关键词` | 全文搜索 |
| `GET /stats` | 数据统计 |
| `GET /deviations` | 偏差索引 |

## 示例查询

```bash
# 查看策略
curl http://localhost:8000/strategy?variant=s17

# 搜索项目
curl "http://localhost:8000/search?q=simulator"

# 查看统计
curl http://localhost:8000/stats

# 查看偏差索引
curl http://localhost:8000/deviations
```

## 项目索引 (45个)

### 🏆 顶级项目 (⭐10+)

| 项目 | Stars | 语言 | 功能 |
|------|-------|------|------|
| [BlackJack-Simulator](https://github.com/seblau/BlackJack-Simulator) | 201 | Python | Omega II算牌 |
| [Blackjack-Strategy-Simulator](https://github.com/AttackingOrDefending/Blackjack-Strategy-Simulator) | 97 | Python | 策略生成+EV |
| [blackjack-simulator](https://github.com/mhluska/blackjack-simulator) | 70 | TypeScript | Hi-Lo练习 |
| [blackjack](https://github.com/1andDone/blackjack) | 16 | Python | Back Counting |
| [blackjack-gui](https://github.com/tukiains/blackjack-gui) | 16 | Python | AI训练+偏差 |

### 按类型分类

- **算牌系统**: 9种 (Hi-Lo, KO, Zen, Omega II等)
- **模拟器**: 12个 (蒙特卡洛、EV计算)
- **训练器**: 6个 (终端/图形界面)
- **AI/ML**: 5个 (Q-Learning、强化学习)
- **计算机视觉**: 5个 (YOLO卡牌检测)
- **其他工具**: 8个

## 每日自动更新

GitHub Actions 每日 UTC 09:00 (北京时间 17:00) 运行，更新项目索引时间戳。
