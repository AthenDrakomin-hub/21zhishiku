#!/usr/bin/env python3
"""
21点自动化浏览器玩家 - Playwright实现
基于策略引擎 + 计算机视觉辅助
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser

from strategy_engine import BlackjackBot, GameState, Action


@dataclass
class GameResult:
    """游戏结果"""
    result: str  # win/loss/push/blackjack
    payout: float
    hand_value: int


class BlackjackBrowserBot:
    """21点浏览器自动化玩家"""
    
    def __init__(self, db_path: str = None):
        self.bot = BlackjackBot(db_path)
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.game_log: list[dict] = []
        
    async def start(self, headless: bool = False):
        """启动浏览器"""
        self.browser = await async_playwright().start()
        self.page = await self.browser.new_page(
            viewport={'width': 1280, 'height': 800}
        )
        # 反检测配置
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        print("✓ 浏览器已启动")
    
    async def navigate_to_game(self, url: str):
        """导航到游戏页面"""
        await self.page.goto(url, wait_until='networkidle')
        print(f"✓ 已导航到: {url}")
    
    async def detect_game_state(self) -> Optional[GameState]:
        """检测游戏状态(通过DOM分析)"""
        try:
            # 获取玩家手牌
            player_cards = await self.page.locator('.player-cards, [class*="player-card"]').all()
            player_hand = []
            for card in player_cards[:2]:  # 只看前两张
                card_text = await card.text_content()
                # 解析牌面: A=1/11, 2-10, J/Q/K=10
                if 'A' in card_text.upper():
                    player_hand.append(11)
                elif any(c in card_text for c in 'JQK'):
                    player_hand.append(10)
                else:
                    try:
                        player_hand.append(int(card_text[:2]))
                    except:
                        pass
            
            # 获取庄家明牌
            dealer_card = await self.page.locator('.dealer-card, [class*="dealer-card"]').first.text_content()
            dealer_upcard = 10  # 默认
            if dealer_card:
                if 'A' in dealer_card.upper():
                    dealer_upcard = 11
                elif any(c in dealer_card for c in 'JQK'):
                    dealer_upcard = 10
                else:
                    try:
                        dealer_upcard = int(dealer_card[:2])
                    except:
                        pass
            
            # 检测是否软牌
            is_soft = player_hand.count(11) > 0 and sum(player_hand) > 21
            
            state = GameState(
                player_hand=player_hand,
                dealer_upcard=dealer_upcard,
                is_soft=is_soft,
                can_split=len(player_hand) == 2 and player_hand[0] == player_hand[1],
                can_surrender=True,
                rounds_remaining=4
            )
            
            print(f"✓ 检测到: 手牌{player_hand}, 庄家明牌{dealer_upcard}")
            return state
            
        except Exception as e:
            print(f"⚠ 检测失败: {e}")
            return None
    
    async def get_recommendation(self, state: GameState) -> Action:
        """获取策略推荐"""
        true_count = self.bot.get_true_count()
        
        # 基本策略
        action = self.bot.get_strategy(state)
        
        # 偏差调整
        deviation = self.bot.get_deviation(state, true_count)
        if deviation:
            print(f"  → 偏差调整: {action.value} → {deviation.value} (True Count: {true_count:.1f})")
            action = deviation
        
        return action
    
    async def execute_action(self, action: Action):
        """执行动作"""
        buttons = {
            Action.HIT: ['Hit', 'Hit me', '打'],
            Action.STAND: ['Stand', 'Stay', '停'],
            Action.DOUBLE: ['Double', 'Double down', '加倍'],
            Action.SPLIT: ['Split', '分牌'],
            Action.SURRENDER: ['Surrender', '投降'],
            Action.INSURANCE: ['Insurance', '保险'],
        }
        
        for btn_text in buttons[action]:
            try:
                await self.page.get_by_text(btn_text, exact=True).click()
                print(f"✓ 执行: {action.value}")
                return
            except:
                continue
        
        print(f"⚠ 未找到按钮: {action.value}")
    
    async def wait_for_result(self, timeout: int = 10) -> Optional[GameResult]:
        """等待游戏结果"""
        start = time.time()
        
        while time.time() - start < timeout:
            # 检查结果元素
            for selector in ['.result', '[class*="result"]', '[class*="win"]', '[class*="lose"]']:
                try:
                    element = await self.page.locator(selector).first
                    if await element.is_visible():
                        text = await element.text_content()
                        result = self._parse_result(text)
                        if result:
                            return result
                except:
                    pass
            await asyncio.sleep(0.5)
        
        return None
    
    def _parse_result(self, text: str) -> Optional[GameResult]:
        """解析结果文本"""
        text = text.lower()
        
        if 'win' in text or 'you win' in text:
            payout = 1.0
            if 'blackjack' in text:
                payout = 1.5
            return GameResult('win', payout, 0)
        elif 'lose' in text or 'you lose' in text:
            return GameResult('loss', -1.0, 0)
        elif 'push' in text or 'tie' in text:
            return GameResult('push', 0.0, 0)
        
        return None
    
    async def play_round(self, url: str):
        """玩一手牌"""
        # 导航
        await self.navigate_to_game(url)
        
        # 等待游戏加载
        await asyncio.sleep(2)
        
        # 检测状态
        state = await self.detect_game_state()
        if not state:
            print("⚠ 无法检测游戏状态")
            return
        
        # 获取策略
        action = await self.get_recommendation(state)
        
        # 执行动作
        await self.execute_action(action)
        
        # 等待结果
        result = await self.wait_for_result()
        if result:
            print(f"结果: {result.result}, 赔付: {result.payout}")
            self.game_log.append({
                'timestamp': datetime.now().isoformat(),
                'state': vars(state),
                'action': action.value,
                'result': result.result,
                'payout': result.payout
            })
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("✓ 浏览器已关闭")
    
    def export_log(self, path: str = "game_log.json"):
        """导出游戏日志"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, ensure_ascii=False, indent=2)
        print(f"✓ 日志已保存: {path}")


async def main():
    """主函数"""
    bot = BlackjackBrowserBot()
    
    try:
        await bot.start(headless=False)  # 显示浏览器便于调试
        
        # 测试游戏URL (替换为实际游戏地址)
        game_url = "https://example.com/blackjack"
        
        # 玩10手牌
        for i in range(10):
            print(f"\n=== 第 {i+1} 手 ===")
            await bot.play_round(game_url)
            await asyncio.sleep(1)
        
        # 导出日志
        bot.export_log()
        
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
