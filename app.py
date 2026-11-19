from fastapi import FastAPI, HTTPException
import db                                  
from pydantic import BaseModel
app=FastAPI()
db.init_db()
@app.get("/")
def read_root():
    return {"message": "记账本服务已启动"}

@app.get("/records")
def list_records(category: str | None = None):     # ← 顺便加个筛选参数
    return db.list_records(category)


@app.get("/records/{record_id}")
def get_one(record_id: int):
    record = db.get_record(record_id)                   # ← index 现在指的是 id，不是下标
    if record is None:
        raise HTTPException(status_code=404, detail=f"没有 id={record_id} 的记录")
    return record


class RecordIn(BaseModel):
    date: str
    amount: float
    category: str
    note: str = ""


@app.post("/records", status_code=201)
def add_record(record: RecordIn):
    new_id = db.add_record(record.date, record.amount, record.category, record.note)
    return {"id": new_id, **record.model_dump()}    # ← 返回带 id 的完整记录


@app.delete("/records/{index}", status_code=204)
def delete_one(index: int):
    if not db.delete_record(index):
        raise HTTPException(status_code=404, detail=f"没有 id={index} 的记录")
    return None