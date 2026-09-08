#!/usr/bin/env python3
"""
Calculate 21点概率数据
基于数学模型计算各种情况下的概率
"""

import json
from pathlib import Path
from itertools import combinations
from typing import List, Tuple, Dict

def calculate_card_probabilities(num_decks: int = 6) -> Dict:
    """计算单张牌的抽到概率"""
    cards_per_deck = 52
    total_cards = num_decks * cards_per_deck
    
    # 牌面价值分布
    card_values = {
        'A': 4 * num_decks,
        '2': 4 * num_decks, '3': 4 * num_decks, '4': 4 * num_decks,
        '5': 4 * num_decks, '6': 4 * num_decks, '7': 4 * num_decks,
        '8': 4 * num_decks, '9': 4 * num_decks,
        '10': 16 * num_decks,  # 10, J, Q, K
    }
    
    probabilities = {}
    for card, count in card_values.items():
        probabilities[card] = count / total_cards
    
    return probabilities

def calculate_bust_probabilities() -> Dict:
    """计算爆牌概率（针对硬牌）"""
    # 硬牌情况下，再抽一张牌爆牌的概率
    bust_probs = {}
    for hand_total in range(12, 21):
        # 需要大于21才爆，所以抽到 (22-total) 及以上的牌会爆
        bust_cards = 22 - hand_total
        # 10点牌有16种(A,10,J,Q,K各4张)
        tens = 16  # 10, J, Q, K各4张 = 16张
        if bust_cards <= 10:
            bust_probs[hand_total] = tens / 52
        elif bust_cards <= 11:
            bust_probs[hand_total] = (tens + 4) / 52  # 加上A
        else:
            bust_probs[hand_total] = 1.0  # 必爆
    return bust_probs

def calculate_blackjack_probability(num_decks: int = 6) -> float:
    """计算首两张牌是Blackjack的概率"""
    aces = 4 * num_decks
    tens = 16 * num_decks
    total = 52 * num_decks
    
    # P(blackjack) = P(A then 10) + P(10 then A)
    prob = (aces / total) * (tens / (total - 1)) + \
           (tens / total) * (aces / (total - 1))
    return prob

def calculate_expected_value() -> Dict:
    """计算基本策略下的期望值"""
    # 不同规则下的 house edge
    edges = {
        "s17_das_ls": -0.42,  # 庄家Stand软17, DAS, 允许Surrender
        "s17_no_das": -0.62,  # 不允许分牌后加倍
        "h17_das_ls": -0.54,  # 庄家Hit软17
        "h17_no_das": -0.76,
        "single_deck_s17": -0.17,
        "single_deck_h17": -0.26
    }
    return edges

def main():
    """主函数"""
    data = {
        "card_probabilities": calculate_card_probabilities(),
        "bust_probabilities": calculate_bust_probabilities(),
        "blackjack_probability": calculate_blackjack_probability(),
        "expected_values": calculate_expected_value()
    }
    
    output_path = Path(__file__).parent.parent / "data" / "probabilities.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 概率数据已保存到: {output_path}")
    return data

if __name__ == "__main__":
    main()
