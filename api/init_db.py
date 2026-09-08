#!/usr/bin/env python3
"""
21点知识库 - SQLite数据库初始化
将JSON/CSV数据导入SQLite，构建全文索引
"""

import json
import csv
import sqlite3
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = Path(__file__).parent / "knowledge_base.db"

def init_db():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 删除旧表（重建）
    cur.execute("DROP TABLE IF EXISTS rules")
    cur.execute("DROP TABLE IF EXISTS strategy")
    cur.execute("DROP TABLE IF EXISTS counting_systems")
    cur.execute("DROP TABLE IF EXISTS projects")
    cur.execute("DROP TABLE IF EXISTS deviations")
    cur.execute("DROP TABLE IF EXISTS history")
    cur.execute("DROP TABLE IF EXISTS probabilities")
    cur.execute("DROP TABLE IF EXISTS search_index")
    
    # 规则表
    cur.execute("""
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 策略表
    cur.execute("""
        CREATE TABLE strategy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant TEXT NOT NULL,
            hand TEXT NOT NULL,
            dealer_card TEXT NOT NULL,
            action TEXT NOT NULL,
            action_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 算牌系统表
    cur.execute("""
        CREATE TABLE counting_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            card_value TEXT NOT NULL,
            level INTEGER,
            type TEXT,
            description TEXT,
            difficulty TEXT,
            accuracy TEXT,
            use_case TEXT
        )
    """)
    
    # 项目索引表
    cur.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            author TEXT,
            stars INTEGER DEFAULT 0,
            url TEXT,
            language TEXT,
            tags TEXT,
            description TEXT,
            features TEXT,
            license TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 偏差索引表
    cur.execute("""
        CREATE TABLE deviations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            hand TEXT NOT NULL,
            `index` INTEGER NOT NULL,
            deviation TEXT NOT NULL
        )
    """)
    
    # 历史表
    cur.execute("""
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT,
            year INTEGER,
            event TEXT,
            contributor TEXT,
            contribution TEXT,
            location TEXT
        )
    """)
    
    # 概率表
    cur.execute("""
        CREATE TABLE probabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card TEXT,
            probability REAL,
            hand_total INTEGER,
            bust_probability REAL,
            blackjack_probability REAL,
            rule_variant TEXT
        )
    """)
    
    # 搜索索引表（普通表）
    cur.execute("""
        CREATE TABLE search_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    """)
    
    conn.commit()
    return conn

def load_rules(conn):
    """加载规则数据"""
    rules_path = DATA_DIR / "rules.json"
    if not rules_path.exists():
        return
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    # 加载基本规则
    basic = data.get('basic', {})
    cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)", 
                ("game_rules", "目标", basic.get('goal', '')))
    cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                ("game_rules", "牌面价值", f"A=1/11, 2-9=面值, 10/J/Q/K=10"))
    cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                ("game_rules", "Blackjack", basic.get('blackjack', '')))
    cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                ("game_rules", "爆牌", basic.get('bust', '')))
    cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                ("game_rules", "平局", basic.get('push', '')))
    
    # 加载操作
    for action, desc in data.get('actions', {}).items():
        cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                    ("actions", action, desc))
    
    # 加载变体规则
    for variation, desc in data.get('variations', {}).items():
        cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                    ("variations", variation, desc))
    
    # 加载术语
    for term in data.get('terms', []):
        cur.execute("INSERT INTO rules (category, name, description) VALUES (?, ?, ?)",
                    ("terms", f"{term['en']}/{term['zh']}", term['desc']))
    
    conn.commit()
    print(f"✓ 规则数据: {cur.execute('SELECT COUNT(*) FROM rules').fetchone()[0]} 条")

def load_strategy(conn):
    """加载策略表数据"""
    cur = conn.cursor()
    
    for filename in ["basic_strategy_s17.csv", "basic_strategy_h17.csv"]:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            continue
        
        variant = filename.replace('.csv', '')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or row[0].startswith('#'):
                    continue
                
                hand = row[0].strip()
                actions = row[1:]
                cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']
                
                for i, card in enumerate(cards):
                    if i < len(actions):
                        action = actions[i].strip()
                        action_type = 'hit' if action.lower() == 'hit' else \
                                     'stand' if action.lower() == 'stand' else \
                                     'double' if action.lower() == 'double' else \
                                     'split' if action.lower() == 'split' else 'other'
                        
                        cur.execute(
                            "INSERT INTO strategy (variant, hand, dealer_card, action, action_type) VALUES (?, ?, ?, ?, ?)",
                            (variant, hand, card, action, action_type)
                        )
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM strategy").fetchone()[0]
    print(f"✓ 策略数据: {count} 条")

def load_counting_systems(conn):
    """加载算牌系统"""
    systems_path = DATA_DIR / "card_counting_systems.json"
    if not systems_path.exists():
        return
    
    with open(systems_path, 'r', encoding='utf-8') as f:
        systems = json.load(f)
    
    cur = conn.cursor()
    for system in systems:
        cur.execute("""
            INSERT INTO counting_systems 
            (name, card_value, level, type, description, difficulty, accuracy, use_case)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system['name'],
            str(system['values']),
            system.get('type', '').replace('Level-', ''),
            system.get('type', ''),
            system.get('description', ''),
            system.get('difficulty', ''),
            system.get('accuracy', ''),
            system.get('use_case', '')
        ))
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM counting_systems").fetchone()[0]
    print(f"✓ 算牌系统: {count} 种")

def load_projects(conn):
    """加载项目索引"""
    projects_path = DATA_DIR / "projects.json"
    if not projects_path.exists():
        return
    
    with open(projects_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    for project in data.get('projects', []):
        cur.execute("""
            INSERT INTO projects 
            (name, author, stars, url, language, tags, description, features, license)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.get('name', ''),
            project.get('author', ''),
            project.get('stars', 0),
            project.get('url', ''),
            project.get('language', ''),
            ','.join(project.get('tags', [])),
            project.get('description', ''),
            ','.join(project.get('features', [])),
            project.get('license', '')
        ))
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    print(f"✓ 项目索引: {count} 个")

def load_deviations(conn):
    """加载偏差索引"""
    dev_path = DATA_DIR / "deviation_indexes.json"
    if not dev_path.exists():
        return
    
    with open(dev_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    # Illustrious 18
    for dev in data.get('illustrious_18', []):
        cur.execute(
            "INSERT INTO deviations (category, hand, `index`, deviation) VALUES (?, ?, ?, ?)",
            ("illustrious_18", dev['hand'], dev['index'], dev['deviation'])
        )
    
    # Fab 4
    for dev in data.get('fab_4', []):
        cur.execute(
            "INSERT INTO deviations (category, hand, `index`, deviation) VALUES (?, ?, ?, ?)",
            ("fab_4", dev['hand'], dev['index'], dev['deviation'])
        )
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM deviations").fetchone()[0]
    print(f"✓ 偏差索引: {count} 条")

def load_history(conn):
    """加载历史数据"""
    history_path = DATA_DIR / "history.json"
    if not history_path.exists():
        return
    
    with open(history_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    # 起源信息
    origin = data.get('history', {}).get('origin', {})
    cur.execute(
        "INSERT INTO history (period, event, location) VALUES (?, ?, ?)",
        (origin.get('period', ''), origin.get('location', ''), origin.get('original_name', ''))
    )
    
    # 里程碑
    for m in data.get('history', {}).get('milestones', []):
        cur.execute(
            "INSERT INTO history (year, event) VALUES (?, ?)",
            (m.get('year', 0), m.get('event', ''))
        )
    
    # 著名玩家
    for player in data.get('famous_players', []):
        cur.execute(
            "INSERT INTO history (contributor, contribution) VALUES (?, ?)",
            (player.get('name', ''), player.get('contribution', ''))
        )
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    print(f"✓ 历史数据: {count} 条")

def load_probabilities(conn):
    """加载概率数据"""
    prob_path = DATA_DIR / "probabilities.json"
    if not prob_path.exists():
        return
    
    with open(prob_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    # 单张牌概率
    for card, prob in data.get('card_probabilities', {}).items():
        cur.execute(
            "INSERT INTO probabilities (card, probability) VALUES (?, ?)",
            (card, prob)
        )
    
    # 爆牌概率
    for hand, prob in data.get('bust_probabilities', {}).items():
        cur.execute(
            "INSERT INTO probabilities (hand_total, bust_probability) VALUES (?, ?)",
            (int(hand), prob)
        )
    
    # Blackjack概率
    cur.execute(
        "INSERT INTO probabilities (blackjack_probability) VALUES (?)",
        (data.get('blackjack_probability', 0),)
    )
    
    # 期望值
    for variant, edge in data.get('expected_values', {}).items():
        cur.execute(
            "INSERT INTO probabilities (rule_variant, bust_probability) VALUES (?, ?)",
            (variant, edge)
        )
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM probabilities").fetchone()[0]
    print(f"✓ 概率数据: {count} 条")

def build_fulltext_index(conn):
    """构建搜索索引"""
    cur = conn.cursor()
    
    # 从各表构建搜索内容
    cur.execute("SELECT id, name || ' ' || description FROM rules")
    for row in cur.fetchall():
        cur.execute("INSERT INTO search_index (source, source_id, content) VALUES (?, ?, ?)",
                   ('rules', row[0], row[1]))
    
    cur.execute("SELECT id, name || ' ' || description || ' ' || tags FROM projects")
    for row in cur.fetchall():
        cur.execute("INSERT INTO search_index (source, source_id, content) VALUES (?, ?, ?)",
                   ('projects', row[0], row[1]))
    
    cur.execute("SELECT id, name || ' ' || description FROM counting_systems")
    for row in cur.fetchall():
        cur.execute("INSERT INTO search_index (source, source_id, content) VALUES (?, ?, ?)",
                   ('counting_systems', row[0], row[1]))
    
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM search_index").fetchone()[0]
    print(f"✓ 搜索索引: {count} 条")

def main():
    """主函数"""
    print("🃏 21点知识库数据库初始化...")
    print(f"数据库路径: {DB_PATH}\n")
    
    conn = init_db()
    
    load_rules(conn)
    load_strategy(conn)
    load_counting_systems(conn)
    load_projects(conn)
    load_deviations(conn)
    load_history(conn)
    load_probabilities(conn)
    build_fulltext_index(conn)
    
    # 显示统计
    cur = conn.cursor()
    print("\n=== 数据库统计 ===")
    tables = ['rules', 'strategy', 'counting_systems', 'projects', 
              'deviations', 'history', 'probabilities', 'search_index']
    for table in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} 条记录")
    
    conn.close()
    print(f"\n✅ 数据库初始化完成: {DB_PATH}")

if __name__ == "__main__":
    main()
