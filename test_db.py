import db
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """每个测试用一个独立的临时数据库，绝不碰真实 ledger.db"""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    return db

def test_add_and_list(temp_db):
    temp_db.add_record("2026-11-20", 25.5, "餐饮", "午饭")
    rows = temp_db.list_records()
    assert len(rows) == 1
    assert rows[0]["amount"] == 25.5



def test_filter_by_category(temp_db):
    temp_db.add_record("2026-11-20", 25.5, "餐饮")
    temp_db.add_record("2026-11-20", 100.0, "购物")
    assert len(temp_db.list_records("餐饮")) == 1
    assert len(temp_db.list_records()) == 2


def test_get_missing_returns_none(temp_db):
    assert temp_db.get_record(999) is None


def test_delete_returns_bool(temp_db):
    new_id = temp_db.add_record("2026-11-20", 10.0, "交通")
    assert temp_db.delete_record(new_id) is True
    assert temp_db.delete_record(new_id) is False        # 再删一次应该 False


def test_id_not_reused(temp_db):
    """核心：删掉后再新增，id 必须比删掉的更大"""
    a = temp_db.add_record("2026-11-20", 1.0, "餐饮")
    temp_db.delete_record(a)
    b = temp_db.add_record("2026-11-20", 2.0, "餐饮")
    assert b > a


def test_stats(temp_db):
    temp_db.add_record("2026-11-20", 25.5, "餐饮")
    temp_db.add_record("2026-11-20", 30.0, "餐饮")
    temp_db.add_record("2026-11-20", 100.0, "购物")
    result = temp_db.stats()
    assert result[0]["category"] == "购物"       # 按金额降序，购物最多
    assert result[0]["total"] == 100.0


def test_empty_db_returns_empty_list(temp_db):
    assert temp_db.list_records() == []

def test_update_record(temp_db):
    new_id = temp_db.add_record("2026-11-20", 10.0, "交通", "地铁")
    assert temp_db.update_record(new_id, "2026-11-20", 20.0, "餐饮", "午饭") is True

    updated = temp_db.get_record(new_id)
    assert updated["amount"] == 20.0
    assert updated["category"] == "餐饮"


def test_update_missing_returns_false(temp_db):
    assert temp_db.update_record(999, "2026-11-20", 1.0, "餐饮") is False


def test_summary(temp_db):
    temp_db.add_record("2026-11-20", 25.5, "餐饮")
    temp_db.add_record("2026-11-20", 30.0, "餐饮")
    temp_db.add_record("2026-11-20", 100.0, "购物")

    s = temp_db.summary()
    assert s["total_count"] == 3
    assert s["total_amount"] == 155.5
    assert s["by_category"][0]["category"] == "购物"     # 按金额降序


def test_summary_empty_db(temp_db):
    """空表时 SUM 返回 NULL，COALESCE 应该把它变成 0"""
    s = temp_db.summary()
    assert s["total_count"] == 0
    assert s["total_amount"] == 0        # ← 不能是 None

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    import app
    return TestClient(app.app)


def test_create_returns_201(client):
    r = client.post("/records", json={"date": "2026-11-20", "amount": 10.0, "category": "餐饮"})
    assert r.status_code == 201
    assert "id" in r.json()


def test_create_missing_field_returns_422(client):
    r = client.post("/records", json={"date": "2026-11-20", "category": "餐饮"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "amount"]    # ← 钉死参数来源


def test_put_updates(client):
    r = client.post("/records", json={"date": "2026-11-20", "amount": 10.0, "category": "餐饮"})
    rid = r.json()["id"]
    r = client.put(f"/records/{rid}", json={"date": "2026-11-20", "amount": 20.0,
                                            "category": "餐饮", "note": ""})
    assert r.status_code == 200
    assert client.get(f"/records/{rid}").json()["amount"] == 20.0


def test_stats_route_not_shadowed(client):
    """/records/stats 不能被 /records/{record_id} 抢走"""
    assert client.get("/records/stats").status_code == 200