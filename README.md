# 21点知识库 (Blackjack Knowledge Base)

🃏 21点（Blackjack）综合知识库 — 规则、策略、算法、开源项目索引

**GitHub**: https://github.com/AthenDrakomin-hub/21zhishiku.git

## 目录结构

```
data/               # 种子数据（规则、策略表、算牌系统）
api/                # 查询接口（HTTP）
scrape/             # 数据爬取脚本
config/             # 配置文件
```

## 快速开始

```bash
# 启动API服务
python3 api/server.py
# 访问: http://localhost:8000
```

## API端点

| 端点 | 描述 |
|------|------|
| `GET /` | 服务信息 |
| `GET /rules` | 游戏规则和术语 |
| `GET /strategy?variant=s17` | 基本策略表 (s17/h17) |
| `GET /counting-systems` | 算牌系统列表 |
| `GET /projects` | 45个开源项目索引 |
| `GET /search?q=关键词` | 全局搜索 |
| `GET /stats` | 数据统计 |
| `GET /probabilities` | 概率数据 |
| `GET /history` | 历史资料 |
| `GET /deviations` | 偏差索引 (Illustrious 18 + Fab 4) |

## 项目索引 (45个)

### 🏆 顶级项目 (⭐10+)

| 项目 | Stars | 语言 | 核心功能 |
|------|-------|------|----------|
| [BlackJack-Simulator](https://github.com/seblau/BlackJack-Simulator) | 201 | Python | Omega II算牌系统 |
| [Blackjack-Strategy-Simulator](https://github.com/AttackingOrDefending/Blackjack-Strategy-Simulator) | 97 | Python | 策略生成+EV+蒙特卡洛 |
| [blackjack-simulator](https://github.com/mhluska/blackjack-simulator) | 70 | TypeScript | Hi-Lo练习+EV计算 |
| [blackjack](https://github.com/1andDone/blackjack) | 16 | Python | Back Counting+Wonging |
| [blackjack-simulator](https://github.com/jgayda/blackjack-simulator) | 16 | Python | 策略对资金影响分析 |
| [blackjack-gui](https://github.com/tukiains/blackjack-gui) | 16 | Python | GUI+AI训练+偏差索引 |
| [blackjack-tracker](https://github.com/martinabeleda/blackjack-tracker) | 7 | Python | OpenCV实时检测 |
| [cardsharp](https://github.com/mmichie/cardsharp) | 10 | Python | 可扩展卡牌模拟框架 |
| [Blackjack-Simulation](https://github.com/shikanchen/Blackjack-Simulation) | 10 | Python | Q-Learning AI |

### 🔢 算牌系统

| 项目 | 功能 |
|------|------|
| [Card_Counting](https://github.com/jackedison/Card_Counting) | 9种系统蒙特卡洛模拟 |
| [BlackJack-Card-Counter](https://github.com/Lif28/BlackJack-Card-Counter) | Hi-Lo/Zen/Omega II + Illustrious 18 |
| [Blackjack](https://github.com/5igor99/Blackjack) | Hi-Lo算牌+偏差训练桌面应用 |
| [CardCounter](https://github.com/Hydrovolter/CardCounter) | JS算牌训练器 |
| [edge-card-counter](https://github.com/LMLK-seal/edge-card-counter) | 交互式算牌模拟器 |
| [card-counting-trainer](https://github.com/varunmc/card-counting-trainer) | Java算牌速度训练 |

### 🤖 AI/强化学习

| 项目 | 技术 |
|------|------|
| [black-jack-black-belt](https://github.com/mattbarrett98/black-jack-black-belt) | RL+Tableau可视化 |
| [blackjack-AI](https://github.com/GitanElyon/blackjack-AI) | Q-Learning+算牌 |
| [blackjack-AI](https://github.com/sakshampandey27/blackjack-AI) | 策略对比AI分析 |
| [blackjack-coach](https://github.com/phil9922/blackjack-coach) | LLM AI教练 |

### 🎯 计算机视觉

| 项目 | 技术 |
|------|------|
| [blackjack-basic-strategy](https://github.com/roboflow/blackjack-basic-strategy) | YOLO卡牌检测 |
| [CV-CardCounting](https://github.com/tomalmog/CV-CardCounting) | YOLOv8实时算牌 |
| [OpenCV-Augmented-Reality-Black-Jack-Counter](https://github.com/Jackb-03/OpenCV-Augmented-Reality-Black-Jack-Counter) | AR+Webcam |
| [BlackJack-Bot](https://github.com/wasifijaz/BlackJack-Bot) | YOLOv8+PaddleOCR+DQN |
| [TakeBacktheHouse](https://github.com/kai405/TakeBacktheHouse) | 视觉+触觉反馈 |

### 📊 模拟与EV计算

| 项目 | 功能 |
|------|------|
| [blackjack-team-sim](https://github.com/ludem525/blackjack-team-sim) | 团队作战+ROR+置信区间 |
| [BlackjackStrategyTester](https://github.com/RochesterinNYC/BlackjackStrategyTester) | MATLAB策略测试 |
| [blackjack-engine](https://github.com/lukedunwoody/blackjack-engine) | C实时EV计算 |
| [valtrain](https://github.com/dootss/valtrain) | C++高精度EV计算 |
| [calculator-blackjack-21](https://github.com/martacbijjn1727865/calculator-blackjack-21) | 概率分析工具 |

## 数据来源

- 百度百科 21点词条
- GitHub 开源项目索引 (45个项目)
- Wizard of Odds 策略计算
- "Blackjack Attack" by Don Schlesinger
- Blackjack Apprenticeship 策略图表

## 每日自动更新

GitHub Actions 每日 UTC 09:00 (北京时间 17:00) 运行：
- 更新项目索引时间戳
- 手动触发：Workflow Dispatch
