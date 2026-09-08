# 21点自动化玩家 (Blackjack Browser Bot)

🃏 基于知识库策略的21点浏览器自动化玩家

## 架构

```
automation/
├── strategy_engine.py    # 策略决策引擎
├── browser_bot.py        # 浏览器自动化主程序
├── requirements.txt      # 依赖
└── deploy.sh            # 部署脚本
```

## 核心功能

### 1. 策略引擎 (strategy_engine.py)
- **基本策略表**: 从SQLite数据库查询S17/H17策略
- **算牌系统**: Hi-Lo等9种主流系统
- **偏差索引**: Illustrious 18 + Fab 4
- **保险决策**: True Count >= 3时买保险

### 2. 浏览器自动化 (browser_bot.py)
- **Playwright驱动**: 现代浏览器自动化
- **DOM解析**: 自动识别手牌和庄家明牌
- **策略执行**: 点击对应按钮
- **结果记录**: 自动记录每手牌数据

## 快速开始

```bash
# 部署
cd automation && bash deploy.sh

# 运行
python3 browser_bot.py
```

## 配置

编辑 `browser_bot.py`:
```python
game_url = "https://your-blackjack-site.com"  # 替换为实际游戏地址
headless = False  # True=无头模式
```

## 策略说明

| 组件 | 数据来源 | 功能 |
|------|----------|------|
| 基本策略 | strategy表(590条) | 硬/软牌标准决策 |
| 算牌计数 | Hi-Lo系统 | 跟踪牌池优势 |
| 偏差调整 | deviations表(22条) | True Count触发调整 |
| 保险 | Illustrious 18 | TC>=3时买保险 |

## 注意事项

1. **反检测**: 已配置navigator.webdriver隐藏
2. **延迟**: 随机延迟模拟人类行为
3. **错误处理**: 自动重试和日志记录
4. **法律**: 仅用于学习和研究，请遵守当地法律

## 扩展

- 添加图像识别(vision_bot.py)
- 添加多标签页管理
- 添加资金管理系统
- 添加统计分析面板

## GitHub仓库

https://github.com/AthenDrakomin-hub/21zhishiku.git
