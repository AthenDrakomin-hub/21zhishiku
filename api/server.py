#!/usr/bin/env python3
"""
21点知识库查询API - SQLite版
提供RESTful接口查询知识库
"""

import json
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = Path(__file__).parent / "knowledge_base.db"

class KnowledgeBaseHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            if path == '/':
                response = self.get_root()
            elif path == '/health':
                response = {"status": "ok", "db_exists": DB_PATH.exists()}
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
        
        self.wfile.write(json.dumps(dict(response), ensure_ascii=False, indent=2).encode())
    
    def get_root(self):
        return {
            "service": "21点知识库 API (SQLite版)",
            "version": "2.0.0",
            "database": str(DB_PATH),
            "endpoints": [
                "/rules - 游戏规则和术语",
                "/strategy?variant=s17 - 基本策略表",
                "/counting-systems - 算牌系统",
                "/projects - 45个开源项目索引",
                "/search?q=关键词 - 全文搜索",
                "/stats - 数据统计",
                "/probabilities - 概率数据",
                "/history - 历史资料",
                "/deviations - 偏差索引"
            ]
        }
    
    def get_rules(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM rules ORDER BY category, name")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "rules": rows}
    
    def get_strategy(self, variant):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT variant, hand, dealer_card, action, action_type 
            FROM strategy 
            WHERE variant = ?
            ORDER BY 
                CASE hand 
                    WHEN '17' THEN 1 WHEN '16' THEN 2 WHEN '15' THEN 3 
                    WHEN '14' THEN 4 WHEN '13' THEN 5 WHEN '12' THEN 6
                    WHEN '11' THEN 7 WHEN '10' THEN 8 WHEN '9' THEN 9
                    WHEN '8' THEN 10 ELSE 11
                END,
                dealer_card
        """, (variant,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"variant": variant, "total": len(rows), "strategy": rows}
    
    def get_counting_systems(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM counting_systems ORDER BY name")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "systems": rows}
    
    def get_counting_system(self, name):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM counting_systems WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {"error": f"算牌系统 {name} 未找到"}
    
    def get_projects(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM projects 
            ORDER BY stars DESC, name ASC
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "projects": rows}
    
    def get_project(self, name):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM projects WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {"error": f"项目 {name} 未找到"}
    
    def search(self, query):
        conn = self.get_conn()
        cur = conn.cursor()
        
        results = {"rules": [], "projects": [], "systems": [], "total": 0}
        
        # 各表搜索
        cur.execute("SELECT * FROM rules WHERE name LIKE ? OR description LIKE ?", 
                   (f'%{query}%', f'%{query}%'))
        results['rules'] = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT * FROM projects WHERE name LIKE ? OR description LIKE ?",
                   (f'%{query}%', f'%{query}%'))
        results['projects'] = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT * FROM counting_systems WHERE name LIKE ? OR description LIKE ?",
                   (f'%{query}%', f'%{query}%'))
        results['systems'] = [dict(r) for r in cur.fetchall()]
        
        results['total'] = sum(len(v) for v in results.values())
        conn.close()
        return results
    
    def get_stats(self):
        conn = self.get_conn()
        cur = conn.cursor()
        
        stats = {}
        for table in ['rules', 'strategy', 'counting_systems', 'projects', 
                     'deviations', 'history', 'probabilities', 'search_index']:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            stats[table] = count
        
        conn.close()
        return {
            "database": str(DB_PATH),
            "generated_at": "2026-09-08",
            "statistics": stats,
            "total_records": sum(stats.values())
        }
    
    def get_probabilities(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM probabilities ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "probabilities": rows}
    
    def get_history(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM history ORDER BY year ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "history": rows}
    
    def get_deviations(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM deviations ORDER BY category, index DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total": len(rows), "deviations": rows}
    
    def log_message(self, format, *args):
        """静默日志"""
        pass

def main():
    """主函数"""
    if not DB_PATH.exists():
        print("❌ 数据库不存在，请先运行 init_db.py")
        return
    
    server = HTTPServer(('0.0.0.0', 8000), KnowledgeBaseHandler)
    print(f"🃏 21点知识库API已启动: http://localhost:8000")
    print(f"📊 数据库: {DB_PATH}")
    print("API端点: /rules, /strategy, /projects, /search?q=xxx, /stats")
    server.serve_forever()

if __name__ == "__main__":
    main()
