#!/usr/bin/env python3
"""21点知识库 API 全面测试"""
import httpx, json

base = "http://localhost:8000"

def get(path):
    r = httpx.get(f"{base}{path}")
    return r.status_code, r.json() if r.text else None

print("=" * 55)
print("  21点知识库 API 服务测试")
print("=" * 55)

# 1. 健康检查
print("\n[1] 健康检查 /health")
code, data = get("/health")
print(f"    状态: {code} | {data}")

# 2. 服务信息
print("\n[2] 服务信息 /")
code, data = get("/")
print(f"    版本: {data.get('version')}")
print(f"    端点数: {len(data.get('endpoints', []))}")

# 3. 数据统计
print("\n[3] 数据统计 /stats")
code, data = get("/stats")
stats = data.get("statistics", {})
print(f"    总记录数: {data.get('total_records')}")
for table, count in stats.items():
    print(f"      {table:20s} {count:>4} 条")

# 4. 规则
print("\n[4] 规则 /rules")
code, data = get("/rules")
rules = data.get("rules", [])
print(f"    共 {data['total']} 条规则")
for r in rules[:4]:
    print(f"      [{r['category']}] {r['name']}")

# 5. 策略 - 修复后应该能用 s17
print("\n[5] 基本策略 /strategy?variant=s17")
code, data = get("/strategy?variant=s17")
print(f"    变体 s17: {data.get('total')} 条")
if data.get("strategy"):
    s = data["strategy"][0]
    print(f"      示例: hand={s['hand']} vs dealer={s['dealer_card']} → {s['action']}")
print(f"    变体 h17:", end=" ")
code2, data2 = get("/strategy?variant=h17")
print(f"{data2.get('total')} 条")

# 6. 算牌系统
print("\n[6] 算牌系统 /counting-systems")
code, data = get("/counting-systems")
print(f"    共 {data['total']} 种")
for s in data["systems"]:
    print(f"      {s['name']:20s} — {s.get('description','')[:40]}")

# 7. 项目索引
print("\n[7] 项目索引 /projects")
code, data = get("/projects")
print(f"    共 {data['total']} 个项目")
for p in data["projects"][:5]:
    print(f"      ★{p['stars']:>3} {p['name']} ({p['language']}) — {p['description'][:35]}")

# 8. 偏差索引 - 修复后应正常工作
print("\n[8] 偏差索引 /deviations (已修复)")
code, data = get("/deviations")
print(f"    状态码: {code}")
if data:
    devs = data.get("deviations", [])
    print(f"    共 {data.get('total', len(devs))} 条偏差")
    for d in devs[:5]:
        print(f"      [{d['category']}] hand={d['hand']}, index={d['index']} → {d['deviation']}")
else:
    print("    响应为空!")

# 9. 概率数据
print("\n[9] 概率数据 /probabilities")
code, data = get("/probabilities")
probs = data.get("probabilities", [])
print(f"    共 {data['total']} 条")
for p in probs[:4]:
    print(f"      {p['card']}: bust={p.get('bust_probability','?')}, bj={p.get('blackjack_probability','?')}")

# 10. 历史
print("\n[10] 历史资料 /history")
code, data = get("/history")
hist = data.get("history", [])
print(f"    共 {data['total']} 条")
for h in hist[:4]:
    print(f"      {h.get('year','?'):>6} — {h['title']}")

# 11. 搜索
print("\n[11] 搜索 /search?q=strategy")
code, data = get("/search?q=strategy")
print(f"    共找到 {data['total']} 条结果")
if data.get("projects"):
    for p in data["projects"][:2]:
        print(f"      ★{p['stars']} {p['name']}")
if data.get("systems"):
    for s in data["systems"][:2]:
        print(f"      [系统] {s['name']}")

print("\n" + "=" * 55)
print("  测试完成！")
print("=" * 55)
