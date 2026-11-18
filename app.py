from fastapi import FastAPI,HTTPException
from storage import load_data,save_data
from pydantic import BaseModel 
app=FastAPI()
@app.get("/")
def read_root():
    return {"message": "记账本服务已启动"}

@app.get("/record/{index}")
def get_one(index:int):
    record=load_data()
    if index < 0 or index >= len(record):
        raise HTTPException(status_code=404, detail=f"没有第 {index} 条记录")
    return record[index]

@app.delete("/record/{index}", status_code=204)
def delete_one(index: int):
    record = load_data()
    if index < 0 or index >= len(record):
        raise HTTPException(status_code=404, detail=f"没有第 {index} 条记录")
    record.pop(index)
    save_data(record)
    return None                  # 204 不返回 body

@app.get('/record')
def list_record():
    return load_data()



class RecordIn(BaseModel):           # ← 定义"body 必须长什么样"
    date: str
    amount: float
    category: str
    note: str = ""                   # 有默认值 → 可以不传


@app.post("/record", status_code=201)      # 201 = 已创建
def add_record(record: RecordIn):
    records = load_data()                   # ← 局部变量叫 records，别叫 record，否则覆盖上面的参数
    new = record.model_dump()               # Pydantic 模型 → dict
    records.append(new)
    save_data(records)
    return new                              # 返回刚创建的那一条