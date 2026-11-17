from fastapi import FastAPI,HTTPException
from storage import load_data,save_data
from pydantic import BaseModel 
app=FastAPI()
@app.get("/")
def read_root():
    return {"message": "记账本服务已启动"}

@app.get("/record/{index}")
def get_one(index:int):
    records=load_data()
    if index < 0 or index >= len(records):
        raise HTTPException(status_code=404, detail=f"没有第 {index} 条记录")
    return records[index]

@app.delete("/records/{index}", status_code=204)
def delete_one(index: int):
    records = load_data()
    if index < 0 or index >= len(records):
        raise HTTPException(status_code=404, detail=f"没有第 {index} 条记录")
    records.pop(index)
    save_data(records)
    return None                  # 204 不返回 body

@app.get('/records')
def list_records():
    return load_data()



class RecordIn(BaseModel):           # ← 定义"body 必须长什么样"
    date: str
    amount: float
    category: str
    note: str = ""                   # 有默认值 → 可以不传


@app.post("/records", status_code=201)      # 201 = 已创建
def add_record(record: RecordIn):
    records = load_data()
    records.append(record.model_dump())      # Pydantic 模型 → dict
    save_data(records)
    return record