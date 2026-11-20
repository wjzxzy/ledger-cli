import pytest
import db
from fastapi.testclient import TestClient

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    import app                  # ← 在 fixture 内部 import
    db.init_db()                # ← 必须显式再调一次
    return TestClient(app.app)

# ---------- 读 ----------

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200


def test_list_empty(client):
    r = client.get("/records")
    assert r.status_code == 200
    assert r.json() == []


def test_create_then_list(client):
    client.post("/records", json={"date": "2026-11-20", "amount": 25.5,
                                  "category": "餐饮", "note": "午饭"})
    r = client.get("/records")
    assert len(r.json()) == 1
    assert r.json()[0]["amount"] == 25.5


def test_filter_by_category(client):
    client.post("/records", json={"date": "2026-11-20", "amount": 1.0, "category": "餐饮"})
    client.post("/records", json={"date": "2026-11-20", "amount": 2.0, "category": "购物"})
    r = client.get("/records", params={"category": "餐饮"})
    assert len(r.json()) == 1


def test_get_missing_returns_404(client):
    r = client.get("/records/999")
    assert r.status_code == 404
    assert "没有 id=999" in r.json()["detail"]


# ---------- 增（含契约断言）----------

def test_create_returns_201_and_id(client):
    r = client.post("/records", json={"date": "2026-11-20", "amount": 10.0, "category": "交通"})
    assert r.status_code == 201
    assert "id" in r.json()


def test_create_missing_field_returns_422(client):
    """缺 amount → 422，而且错误位置必须是 body 不是 query"""
    r = client.post("/records", json={"date": "2026-11-20", "category": "交通"})
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert detail[0]["loc"] == ["body", "amount"]      # ← 这条钉死"参数来自 body"


# ---------- 改 ----------

def test_put_updates(client):
    rid = client.post("/records", json={"date": "2026-11-20", "amount": 10.0,
                                        "category": "餐饮"}).json()["id"]
    r = client.put(f"/records/{rid}", json={"date": "2026-11-20", "amount": 20.0,
                                            "category": "餐饮", "note": ""})
    assert r.status_code == 200
    assert client.get(f"/records/{rid}").json()["amount"] == 20.0


def test_put_missing_returns_404(client):
    r = client.put("/records/999", json={"date": "2026-11-20", "amount": 1.0, "category": "餐饮"})
    assert r.status_code == 404


def test_put_missing_field_returns_422(client):
    r = client.put("/records/1", json={"date": "2026-11-20"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "amount"]


# ---------- 删 ----------

def test_delete_returns_204(client):
    rid = client.post("/records", json={"date": "2026-11-20", "amount": 1.0,
                                        "category": "餐饮"}).json()["id"]
    r = client.delete(f"/records/{rid}")
    assert r.status_code == 204
    assert r.text == ""                    # 204 不能有 body


def test_delete_twice_returns_404(client):
    rid = client.post("/records", json={"date": "2026-11-20", "amount": 1.0,
                                        "category": "餐饮"}).json()["id"]
    client.delete(f"/records/{rid}")
    assert client.delete(f"/records/{rid}").status_code == 404


# ---------- 统计 & 路由顺序 ----------

def test_stats(client):
    client.post("/records", json={"date": "2026-11-20", "amount": 25.0, "category": "餐饮"})
    client.post("/records", json={"date": "2026-11-20", "amount": 100.0, "category": "购物"})
    s = client.get("/records/stats").json()
    assert s["total_count"] == 2
    assert s["total_amount"] == 125.0
    assert s["by_category"][0]["category"] == "购物"      # 按金额降序


def test_stats_route_not_shadowed_by_id(client):
    """/records/stats 不能被 /records/{record_id} 抢走"""
    r = client.get("/records/stats")
    assert r.status_code == 200                 # 如果是 422，说明路由顺序反了
    assert "total_count" in r.json()


def test_stats_empty_db_returns_zero(client):
    """COALESCE：空表时 total_amount 必须是 0，不能是 null"""
    s = client.get("/records/stats").json()
    assert s["total_count"] == 0
    assert s["total_amount"] == 0