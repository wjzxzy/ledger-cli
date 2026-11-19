import sqlite3
DB_PATH = "ledger.db"
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # 让查询结果能按字段名取值
    return conn

def init_db():
    """建表 + 建索引（已存在则跳过）"""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            date     TEXT    NOT NULL,
            amount   REAL    NOT NULL,
            category TEXT    NOT NULL,
            note     TEXT    NOT NULL DEFAULT ''
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON records(category)")
    conn.commit()
    conn.close()

def list_records(category=None):
    """查全部；给了 category 就按类别过滤"""
    conn = get_conn()
    if category:
        rows = conn.execute(
            "SELECT * FROM records WHERE category = ? ORDER BY id", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM records ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_record(record_id):
    """查一条，没有就返回 None"""
    conn = get_conn()
    row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_record(date, amount, category, note=""):
    """新增，返回新记录的 id"""
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO records (date, amount, category, note) VALUES (?, ?, ?, ?)",
        (date, amount, category, note),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id

def delete_record(record_id):
    """删除，返回是否真的删掉了"""
    conn = get_conn()
    cur = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def stats():
    """按类别统计：笔数 + 金额，按金额降序"""
    conn = get_conn()
    rows = conn.execute("""
        SELECT category, COUNT(*) AS cnt, SUM(amount) AS total
        FROM records
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
