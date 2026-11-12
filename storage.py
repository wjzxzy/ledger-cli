"""
storage.py —— 数据读写层
============================================
只负责和 data.json 打交道：文件 → list，list → 文件。

这一层里没有一句 print 的业务输出，也没有一句 input()。
好处：以后想把 JSON 换成 CSV / SQLite / 数据库，
只改这个文件，其他文件一行都不用动。
"""

import json

from config import DATA_FILE


def load_data(path=DATA_FILE):
    """从 data.json 读出所有记录，返回列表。

    要处理三种情况：
    - 文件不存在：第一次运行就是这样 → 返回空列表
    - 文件内容坏了（不是合法 JSON）：返回空列表并提醒
    - 文件内容不是列表（比如被改成了 {...}）：返回空列表并提醒
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        # 第一次运行，还没有文件，这本账是空的
        return []
    except json.JSONDecodeError:
        # 文件在，但内容不是合法 JSON
        print(f"[警告] {path.name} 内容损坏，本次从空账本开始")
        return []

    # 防御：合法 JSON 也可能不是列表，后面 records.append 会崩
    if not isinstance(data, list):
        print(f"[警告] {path.name} 里不是记录列表，本次从空账本开始")
        return []

    return data


def save_data(records, path=DATA_FILE):
    """把记录列表写回 data.json。

    ensure_ascii=False → 中文正常显示，不变成 \u9910\u996e 这种编码
    indent=2          → 文件有缩进，人能看懂（不加的话全挤在一行）
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
