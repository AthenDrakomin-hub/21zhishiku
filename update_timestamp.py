import json
from pathlib import Path
from datetime import datetime

projects_path = Path("data/projects.json")
if projects_path.exists():
    with open(projects_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    with open(projects_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"更新时间戳: {data['last_updated']}")
else:
    print("projects.json 不存在")
