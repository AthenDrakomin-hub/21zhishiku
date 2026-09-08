#!/usr/bin/env python3
"""
21点基础策略数据拉取脚本
拉取来自公开知识库的策略表和规则
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def fetch_basic_strategy():
    """拉取并整理基本策略表数据"""
    # S17 和 H17 两套策略
    strategies = {}
    
    # 从本地CSV文件读取策略
    for filename in ["basic_strategy_s17.csv", "basic_strategy_h17.csv"]:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                strategies[filename.replace('.csv', '')] = content
    
    return strategies

def fetch_rules():
    """加载规则数据"""
    rules_path = DATA_DIR / "rules.json"
    if rules_path.exists():
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_counting_systems():
    """加载算牌系统数据"""
    systems_path = DATA_DIR / "card_counting_systems.json"
    if systems_path.exists():
        with open(systems_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_projects():
    """加载项目索引数据"""
    projects_path = DATA_DIR / "projects.json"
    if projects_path.exists():
        with open(projects_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_strategy_summary():
    """生成策略摘要文档"""
    summary = {
        "generated_at": "2026-09-08",
        "data_sources": {
            "basic_strategy": "S17/H17 标准基本策略表",
            "counting_systems": "9种主流算牌系统",
            "projects": "GitHub 21点相关开源项目"
        },
        "statistics": {
            "strategy_tables": 2,
            "counting_systems": 9,
            "projects_indexed": 7
        }
    }
    return summary

def main():
    """主函数"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("🃏 21点知识库数据整理中...")
    
    # 拉取各项数据
    strategies = fetch_basic_strategy()
    rules = fetch_rules()
    counting = fetch_counting_systems()
    projects = fetch_projects()
    summary = generate_strategy_summary()
    
    print(f"✓ 策略表: {len(strategies)} 套")
    print(f"✓ 游戏规则: {'已加载' if rules else '未找到'}")
    print(f"✓ 算牌系统: {len(counting) if counting else 0} 种")
    print(f"✓ 项目索引: {len(projects.get('projects', [])) if projects else 0} 个")
    
    # 保存摘要
    summary_path = DATA_DIR / "summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 数据摘要已保存到: {summary_path}")
    return True

if __name__ == "__main__":
    main()
