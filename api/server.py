#!/usr/bin/env python3
"""
21点知识库查询API - 纯Python实现(无需FastAPI)
提供RESTful接口查询知识库
"""

import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class KnowledgeBaseHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    DATA_DIR = Path(__file__).parent.parent / "data"
    data_store = {}
    
    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 路由分发
        try:
            if path == '/':
                response = self.get_root()
            elif path == '/health':
                response = {"status": "ok", "data_loaded": bool(self.data_store)}
            elif path == '/rules':
                response = self.get_rules()
            elif path.startswith('/strategy'):
                variant = params.get('variant', ['s17'])[0]
                response = self.get_strategy(variant)
            elif path == '/counting-systems':
                response = self.get_counting_systems()
            elif path.startswith('/counting-systems/'):
                name = path.split('/')[-1]
                response = self.get_counting_system(name)
            elif path == '/projects':
                response = self.get_projects()
            elif path.startswith('/projects/'):
                name = path.split('/')[-1]
                response = self.get_project(name)
            elif path == '/search':
                query = params.get('q', [''])[0]
                response = self.search(query)
            elif path == '/stats':
                response = self.get_stats()
            elif path == '/probabilities':
                response = self.get_probabilities()
            elif path == '/history':
                response = self.get_history()
            elif path == '/deviations':
                response = self.get_deviations()
            else:
                response = {"error": "Not found", "path": path}
        except Exception as e:
            response = {"error": str(e)}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode())
    
    def get_root(self):
        return {
            "service": "21点知识库 API",
            "version": "1.0.0",
            "endpoints": [
                "/rules - 游戏规则和术语",
                "/strategy?variant=s17 - 基本策略表",
                "/counting-systems - 算牌系统",
                "/projects - 开源项目索引",
                "/search?q=关键词 - 全局搜索",
                "/stats - 数据统计",
                "/probabilities - 概率数据",
                "/history - 历史资料",
                "/deviations - 偏差索引"
            ]
        }
    
    def get_rules(self):
        rules_path = self.DATA_DIR / "rules.json"
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "规则数据未找到"}
    
    def get_strategy(self, variant):
        strategy_path = self.DATA_DIR / f"basic_strategy_{variant}.csv"
        if not strategy_path.exists():
            return {"error": f"策略表 {variant} 未找到"}
        
        with open(strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析CSV
        lines = content.strip().split('\n')
        table = []
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                entry = {"hand": parts[0].strip()}
                for i, card in enumerate(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']):
                    if i + 1 < len(parts):
                        entry[card] = parts[i + 1].strip()
                table.append(entry)
        
        return {
            "variant": variant,
            "data": content,
            "table": table
        }
    
    def get_counting_systems(self):
        systems_path = self.DATA_DIR / "card_counting_systems.json"
        if systems_path.exists():
            with open(systems_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "算牌系统数据未找到"}
    
    def get_counting_system(self, name):
        systems_path = self.DATA_DIR / "card_counting_systems.json"
        if systems_path.exists():
            with open(systems_path, 'r', encoding='utf-8') as f:
                systems = json.load(f)
            for system in systems:
                if system['name'].lower() == name.lower():
                    return system
        return {"error": f"算牌系统 {name} 未找到"}
    
    def get_projects(self):
        projects_path = self.DATA_DIR / "projects.json"
        if projects_path.exists():
            with open(projects_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "项目索引未找到"}
    
    def get_project(self, name):
        projects_path = self.DATA_DIR / "projects.json"
        if projects_path.exists():
            with open(projects_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for project in data.get('projects', []):
                if project['name'].lower() == name.lower():
                    return project
        return {"error": f"项目 {name} 未找到"}
    
    def search(self, query):
        results = {"rules": [], "strategies": [], "systems": [], "projects": [], "history": []}
        q = query.lower()
        
        # 搜索规则
        rules_path = self.DATA_DIR / "rules.json"
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            for term in rules.get('terms', []):
                if q in term['en'].lower() or q in term['zh'].lower() or q in term['desc'].lower():
                    results['rules'].append(term)
        
        # 搜索算牌系统
        systems_path = self.DATA_DIR / "card_counting_systems.json"
        if systems_path.exists():
            with open(systems_path, 'r', encoding='utf-8') as f:
                systems = json.load(f)
            for system in systems:
                if q in system['name'].lower() or q in system['description'].lower():
                    results['systems'].append(system)
        
        # 搜索项目
        projects_path = self.DATA_DIR / "projects.json"
        if projects_path.exists():
            with open(projects_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for project in data.get('projects', []):
                if (q in project['name'].lower() or 
                    q in project['description'].lower() or
                    any(q in tag.lower() for tag in project.get('tags', []))):
                    results['projects'].append(project)
        
        # 搜索历史
        history_path = self.DATA_DIR / "history.json"
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            if q in json.dumps(history, ensure_ascii=False).lower():
                results['history'].append(history)
        
        return {
            "query": query,
            "results": results,
            "total": sum(len(v) for v in results.values())
        }
    
    def get_stats(self):
        summary = {
            "generated_at": "2026-09-08",
            "data_sources": {
                "basic_strategy": "S17/H17 标准基本策略表",
                "counting_systems": "9种主流算牌系统",
                "projects": "GitHub 21点相关开源项目",
                "history": "21点历史资料",
                "deviations": "Illustrious 18 + Fab 4 偏差索引"
            },
            "statistics": {
                "strategy_tables": 2,
                "counting_systems": 9,
                "projects_indexed": 7,
                "deviation_indexes": 22
            }
        }
        return summary
    
    def get_probabilities(self):
        prob_path = self.DATA_DIR / "probabilities.json"
        if prob_path.exists():
            with open(prob_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "概率数据未找到"}
    
    def get_history(self):
        history_path = self.DATA_DIR / "history.json"
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "历史数据未找到"}
    
    def get_deviations(self):
        dev_path = self.DATA_DIR / "deviation_indexes.json"
        if dev_path.exists():
            with open(dev_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"error": "偏差索引未找到"}
    
    def log_message(self, format, *args):
        """静默日志"""
        pass

def load_data():
    """加载数据到内存"""
    # 预加载数据供未来使用
    pass

if __name__ == "__main__":
    load_data()
    server = HTTPServer(('0.0.0.0', 8000), KnowledgeBaseHandler)
    print("🃏 21点知识库API已启动: http://localhost:8000")
    server.serve_forever()
