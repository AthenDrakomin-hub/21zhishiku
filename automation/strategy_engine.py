#!/usr/bin/env python3
"""
21点自动化玩家 - 策略决策引擎
基于SQLite知识库 + 算牌系统 + 偏差索引
"""

import sqlite3
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
    INSURANCE = "insurance"


@dataclass
class GameState:
    """游戏状态"""
    player_hand: list[int]      # 玩家手牌点数 [11, 5]
    dealer_upcard: int          # 庄家明牌 1-11
    is_soft: bool               # 是否软牌(A作为11)
    can_split: bool             # 可分牌
    can_surrender: bool         # 可投降
    rounds_remaining: int       # 剩余牌数(用于算牌)


class BlackjackBot:
    """21点自动化决策引擎"""
    
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or "api/knowledge_base.db")
        self.counting_system = "Hi-Lo"
        self.running_count = 0
        self.decks = 6  # 默认6副牌
    
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def get_strategy(self, state: GameState) -> Action:
        """获取基本策略"""
        hand_value = sum(state.player_hand)
        variant = "basic_strategy_s17"
        
        # 查询数据库
        conn = self._get_conn()
        cur = conn.cursor()
        
        # 硬牌策略
        if not state.is_soft:
            cur.execute("""
                SELECT action FROM strategy 
                WHERE variant = ? AND hand = ? AND dealer_card = ?
            """, (variant, str(hand_value), str(state.dealer_upcard)))
            row = cur.fetchone()
            if row:
                action = self._parse_action(row['action'])
                conn.close()
                return action
        
        # 软牌策略(使用H17表)
        else:
            variant = "basic_strategy_h17"
            # A,X 表示软牌
            ace_count = state.player_hand.count(1)
            if ace_count > 0:
                other_cards = [c for c in state.player_hand if c != 1]
                soft_total = 11 + sum(other_cards)
                cur.execute("""
                    SELECT action FROM strategy 
                    WHERE variant = ? AND hand = ? AND dealer_card = ?
                """, (variant, f'A,{sum(other_cards)}', str(state.dealer_upcard)))
                row = cur.fetchone()
                if row:
                    action = self._parse_action(row['action'])
                    conn.close()
                    return action
        
        conn.close()
        return Action.STAND  # 默认站立
    
    def get_deviation(self, state: GameState, true_count: float) -> Optional[Action]:
        """获取偏差调整"""
        hand_key = self._get_hand_key(state)
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 检查Illustrious 18
        cur.execute("""
            SELECT hand, `index`, deviation FROM deviations 
            WHERE hand = ? AND category = 'illustrious_18'
        """, (hand_key,))
        row = cur.fetchone()
        
        if row and abs(true_count) >= abs(row['index']):
            deviation = row['deviation']
            if 'stand' in deviation:
                return Action.STAND
            elif 'hit' in deviation:
                return Action.HIT
            elif 'split' in deviation:
                return Action.SPLIT
            elif 'double' in deviation:
                return Action.DOUBLE
        
        # 检查Fab 4
        cur.execute("""
            SELECT hand, `index`, deviation FROM deviations 
            WHERE hand = ? AND category = 'fab_4'
        """, (hand_key,))
        row = cur.fetchone()
        
        if row and abs(true_count) >= abs(row['index']):
            deviation = row['deviation']
            if 'surrender' in deviation:
                return Action.SURRENDER
            elif 'stand' in deviation:
                return Action.STAND
        
        conn.close()
        return None
    
    def update_count(self, card: int):
        """更新算牌计数(Hi-Lo系统)"""
        # Hi-Lo值: A=-1, 2-6=+1, 7-9=0, 10-A=-1
        values = {
            1: -1,   # A
            2: 1,    # 2-6
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 0,    # 7-9
            8: 0,
            9: 0,
            10: -1,  # 10-J-Q-K
            11: -1,
        }
        self.running_count += values.get(card, 0)
    
    def get_true_count(self) -> float:
        """计算真实计数"""
        if self.decks <= 0:
            return 0.0
        decks_remaining = max(self.decks, 0.5)
        return self.running_count / decks_remaining
    
    def should_take_insurance(self, true_count: float) -> bool:
        """是否买保险(偏差索引3)"""
        return true_count >= 3
    
    def should_double_reduced(self, state: GameState, true_count: float) -> bool:
        """偏离基本策略的加倍情况"""
        hand_key = self._get_hand_key(state)
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # A,8 vs 2 需要Stand而非Double(当true count >= 1)
        cur.execute("""
            SELECT index FROM deviations 
            WHERE hand = 'A,8_vs_2' AND category = 'illustrious_18'
        """)
        row = cur.fetchone()
        if row and true_count >= 1:
            conn.close()
            return False  # 不加倍，改为站立
        
        conn.close()
        return True
    
    def _get_hand_key(self, state: GameState) -> str:
        """生成手牌键"""
        hand = sorted(state.player_hand)
        if state.is_soft:
            ace_idx = hand.index(1) if 1 in hand else 0
            other = [c for c in hand if c != 1]
            return f"A,{sum(other)}_vs_{state.dealer_upcard}"
        else:
            return f"{sum(hand)}_vs_{state.dealer_upcard}"
    
    def _parse_action(self, action_str: str) -> Action:
        """解析动作字符串"""
        mapping = {
            'hit': Action.HIT,
            'stand': Action.STAND,
            'double': Action.DOUBLE,
            'split': Action.SPLIT,
            'surrender': Action.SURRENDER,
        }
        return mapping.get(action_str.lower(), Action.STAND)


def main():
    """测试示例"""
    bot = BlackjackBot()
    
    # 模拟游戏状态
    state = GameState(
        player_hand=[10, 5],  # 硬15
        dealer_upcard=10,
        is_soft=False,
        can_split=False,
        can_surrender=True,
        rounds_remaining=4
    )
    
    # 基本策略
    action = bot.get_strategy(state)
    print(f"基本策略: {action.value}")
    
    # 算牌
    bot.update_count(5)  # +1
    bot.update_count(3)  # +1
    true_count = bot.get_true_count()
    print(f"真实计数: {true_count:.2f}")
    
    # 偏差调整
    deviation = bot.get_deviation(state, true_count)
    if deviation:
        print(f"偏差调整: {deviation.value}")
    
    # 保险决策
    print(f"买保险: {bot.should_take_insurance(true_count)}")


if __name__ == "__main__":
    main()
