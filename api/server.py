#!/usr/bin/env python3
"""
21点知识库查询API
提供 RESTful 接口查询知识库
"""

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

app = FastAPI(title="21点知识库 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent / "data"

# 启动时加载数据
data_store = {}

def load_data():
    """加载所有数据到内存"""
    global data_store
    
    # 加载规则
    rules_path = DATA_DIR / "rules.json"
    if rules_path.exists():
        with open(rules_path, 'r', encoding='utf-8') as f:
            data_store['rules'] = json.load(f)
    
    # 加载算牌系统
    counting_path = DATA_DIR / "card_counting_systems.json"
    if counting_path.exists():
        with open(counting_path, 'r', encoding='utf-8') as f:
            data_store['counting_systems'] = json.load(f)
    
    # 加载项目索引
    projects_path = DATA_DIR / "projects.json"
    if projects_path.exists():
        with open(projects_path, 'r', encoding='utf-8') as f:
            data_store['projects'] = json.load(f)
    
    # 加载策略表
    strategy_path = DATA_DIR / "basic_strategy_s17.csv"
    if strategy_path.exists():
        with open(strategy_path, 'r', encoding='utf-8') as f:
            data_store['strategy_s17'] = f.read()
    
    strategy_path_h17 = DATA_DIR / "basic_strategy_h17.csv"
    if strategy_path_h17.exists():
        with open(strategy_path_h17, 'r', encoding='utf-8') as f:
            data_store['strategy_h17'] = f.read()
    
    # 加载摘要
    summary_path = DATA_DIR / "summary.json"
    if summary_path.exists():
        with open(summary_path, 'r', encoding='utf-8') as f:
            data_store['summary'] = json.load(f)

load_data()

@app.get("/")
def root():
    return {
        "service": "21点知识库 API",
        "version": "1.0.0",
        "endpoints": [
            "/rules - 游戏规则和术语",
            "/strategy - 基本策略表",
            "/counting-systems - 算牌系统",
            "/projects - 开源项目索引",
            "/search?q=关键词 - 全局搜索",
            "/stats - 数据统计"
        ]
    }

@app.get("/rules")
def get_rules():
    """获取游戏规则"""
    if 'rules' not in data_store:
        raise HTTPException(404, "规则数据未找到")
    return data_store['rules']

@app.get("/strategy")
def get_strategy(variant: str = "s17"):
    """获取基本策略表"""
    key = f"strategy_{variant}"
    if key not in data_store:
        raise HTTPException(404, f"策略表 {variant} 未找到")
    return {
        "variant": variant,
        "data": data_store[key]
    }

@app.get("/strategy/table")
def get_strategy_table(variant: str = "s17"):
    """获取格式化的策略表格"""
    key = f"strategy_{variant}"
    if key not in data_store:
        raise HTTPException(404, f"策略表 {variant} 未找到")
    
    lines = data_store[key].strip().split('\n')
    table = []
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            table.append({
                "hand": parts[0].strip(),
                "actions": {parts[i+1].strip(): parts[i+2].strip() if i+2 < len(parts) else "" 
                           for i in range(1, min(len(parts)-1, 11))}
            })
    return {"variant": variant, "table": table}

@app.get("/counting-systems")
def get_counting_systems():
    """获取算牌系统列表"""
    if 'counting_systems' not in data_store:
        raise HTTPException(404, "算牌系统数据未找到")
    return data_store['counting_systems']

@app.get("/counting-systems/{name}")
def get_counting_system(name: str):
    """获取特定算牌系统详情"""
    if 'counting_systems' not in data_store:
        raise HTTPException(404, "算牌系统数据未找到")
    
    for system in data_store['counting_systems']:
        if system['name'].lower() == name.lower():
            return system
    
    raise HTTPException(404, f"算牌系统 {name} 未找到")

@app.get("/projects")
def get_projects():
    """获取开源项目索引"""
    if 'projects' not in data_store:
        raise HTTPException(404, "项目索引未找到")
    return data_store['projects']

@app.get("/projects/{name}")
def get_project(name: str):
    """获取特定项目详情"""
    if 'projects' not in data_store:
        raise HTTPException(404, "项目索引未找到")
    
    for project in data_store['projects'].get('projects', []):
        if project['name'].lower() == name.lower():
            return project
    
    raise HTTPException(404, f"项目 {name} 未找到")

@app.get("/search")
def search(query: str):
    """全局搜索"""
    results = {
        "rules": [],
        "strategies": [],
        "systems": [],
        "projects": []
    }
    
    q = query.lower()
    
    # 搜索规则
    if 'rules' in data_store:
        for term in data_store['rules'].get('terms', []):
            if q in term['en'].lower() or q in term['zh'].lower() or q in term['desc'].lower():
                results['rules'].append(term)
    
    # 搜索算牌系统
    if 'counting_systems' in data_store:
        for system in data_store['counting_systems']:
            if q in system['name'].lower() or q in system['description'].lower():
                results['systems'].append(system)
    
    # 搜索项目
    if 'projects' in data_store:
        for project in data_store['projects'].get('projects', []):
            if (q in project['name'].lower() or 
                q in project['description'].lower() or
                any(q in tag.lower() for tag in project.get('tags', []))):
                results['projects'].append(project)
    
    return {
        "query": query,
        "results": results,
        "total": sum(len(v) for v in results.values())
    }

@app.get("/stats")
def get_stats():
    """获取数据统计"""
    if 'summary' not in data_store:
        return {"error": "统计数据未找到"}
    return data_store['summary']

@app.get("/health")
def health_check():
    return {"status": "ok", "data_loaded": bool(data_store)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
