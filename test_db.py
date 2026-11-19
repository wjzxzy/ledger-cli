
from storage import load_data, save_data
import db
import pytest
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