import json
from storage import load_data, save_data

def test_load_missing_file(tmp_path):
    """文件不存在 → 返回空列表"""
    assert load_data(tmp_path / "nope.json") == []

def test_save_then_load(tmp_path):
    """存进去再读出来，内容一样"""
    path = tmp_path / "data.json"
    records = [{"date": "2026-11-12", "amount": 25.5, "category": "餐饮", "note": ""}]
    save_data(records, path)
    assert load_data(path) == records

def test_load_broken_json(tmp_path):
    """内容不是合法 JSON → 返回空列表，不崩溃"""
    path = tmp_path / "bad.json"
    path.write_text("{这不是json", encoding="utf-8")
    assert load_data(path) == []