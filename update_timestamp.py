import json
from pathlib import Path
from datetime import datetime

projects_path = Path(__file__).parent / "data" / "projects.json"
if projects_path.exists():
    data = json.loads(projects_path.read_text(encoding="utf-8"))
    data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    projects_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"更新时间戳: {data['last_updated']}")
else:
    print("projects.json 不存在")
