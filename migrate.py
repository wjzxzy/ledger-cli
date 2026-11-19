import json
import db

db.init_db()

with open("data.json", "r", encoding="utf-8") as f:
    records = json.load(f)

for r in records:
    db.add_record(r["date"], r["amount"], r["category"], r.get("note", ""))

print(f"迁移完成，共 {len(records)} 条")
print("数据库现状：", db.list_records())