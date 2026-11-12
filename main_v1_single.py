"""
命令行记账本 v1
============================================
功能：添加一笔 / 查看全部 / 查看统计
数据：保存到 data.json（JSON 格式）

运行：python main.py

【读代码前先看这三条设计】
1. 所有记录放在一个 list 里，每条记录是一个 dict：
   [{"date": "2026-11-12", "amount": 25.5, "category": "餐饮", "note": "午饭"}, ...]
   这个"列表套字典"就是以后接口返回的 JSON 结构
2. 程序启动时把数据读进内存（records 变量），之后都在内存里操作
3. 每次改动后立刻写回文件（防止程序崩溃丢数据）
"""

import json
from datetime import date

DATA_FILE = "data.json"

# 固定类别。想加类别只改这一处
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "其他"]


# ============================================================
# 第一部分：数据读写
# ============================================================

def load_data():
    """从 data.json 读出所有记录，返回列表。

    要处理两种情况：
    - 文件不存在：第一次运行就是这样 → 返回空列表
    - 文件内容坏了：比如手动改错了 → 返回空列表并提醒
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 第一次运行，还没有文件，这本账是空的
        return []
    except json.JSONDecodeError:
        # 文件在，但内容不是合法 JSON
        print(f"[警告] {DATA_FILE} 内容损坏，本次从空账本开始")
        return []


def save_data(records):
    """把记录列表写回 data.json。

    ensure_ascii=False → 中文正常显示，不变成 \u9910\u996e 这种编码
    indent=2          → 文件有缩进，人能看懂（不加的话全挤在一行）
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ============================================================
# 第二部分：输入校验
# ------------------------------------------------------------
# 三个函数，各自负责"拿到一个合法的输入"
# 共同套路：while True → 试 → 不合法就 continue → 合法就 return
# 和你写的 get_number() 是同一个模式
# ============================================================

def ask_amount():
    """反复询问，直到拿到一个合法的正数金额"""
    while True:
        raw = input("金额：").strip()

        # 第一步：能不能转成数字？（格式检查 → 用 try）
        try:
            amount = float(raw)
        except ValueError:
            print(f"  「{raw}」不是数字，请重新输入")
            continue

        # 第二步：数字合法吗？（值域检查 → 用 if）
        if amount <= 0:
            print("  金额必须大于 0")
            continue

        return round(amount, 2)   # 只保留两位小数


def ask_category():
    """从固定列表里选一个类别，返回类别名"""
    # 先把选项摆出来
    print("  类别：", end="")
    for i, name in enumerate(CATEGORIES, start=1):
        print(f"{i}.{name}", end="  ")
    print()

    while True:
        raw = input("  请选择类别编号：").strip()
        try:
            idx = int(raw)
        except ValueError:
            print("  请输入数字编号")
            continue

        if 1 <= idx <= len(CATEGORIES):
            return CATEGORIES[idx - 1]   # 用户看到 1 开始，列表是 0 开始
        print(f"  编号要在 1 到 {len(CATEGORIES)} 之间")


def ask_date():
    """输入日期；直接回车就用今天"""
    today = str(date.today())          # 例如 2026-11-12
    raw = input(f"日期（直接回车用今天 {today}）：").strip()
    return raw if raw else today


# ============================================================
# 第三部分：三个功能
# ============================================================

def add_record(records):
    """添加一笔"""
    print("\n--- 添加一笔 ---")
    d = ask_date()
    amount = ask_amount()
    category = ask_category()
    note = input("备注（可留空）：").strip()

    record = {
        "date": d,
        "amount": amount,
        "category": category,
        "note": note,
    }
    records.append(record)

    save_data(records)      # 立刻存盘，不等退出
    print(f"[已记录] {d}  {category}  {amount:.2f} 元")


def show_all(records):
    """打印所有记录"""
    print("\n--- 全部记录 ---")

    if not records:                 # 空列表就提前返回，别让下面的代码报错
        print("（还没有任何记录）")
        return

    print(f"{'日期':<12}{'类别':<8}{'金额':>10}  备注")
    print("-" * 48)

    total = 0
    for r in records:
        total += r["amount"]
        print(f"{r['date']:<12}{r['category']:<8}{r['amount']:>10.2f}  {r['note']}")

    print("-" * 48)
    print(f"共 {len(records)} 笔，合计 {total:.2f} 元")


def show_stats(records):
    """统计：总额 + 每个类别各多少、占比多少"""
    print("\n--- 统计 ---")

    if not records:
        print("（还没有任何记录）")
        return

    # 一次遍历同时算两件事：总额、各类别小计
    # by_category 就是"类别 → 金额"的字典，和 wordcount.py 的写法一模一样
    total = 0
    by_category = {}
    for r in records:
        total += r["amount"]
        c = r["category"]
        if c in by_category:
            by_category[c] += r["amount"]
        else:
            by_category[c] = r["amount"]

    if total <= 0:                  # 防御：避免下面除以 0
        print("总金额为 0，无法计算占比")
        return

    # 按金额从高到低排序
    # .items() 把字典变成 [(键, 值), ...] 这样的列表
    # key=lambda kv: kv[1] 意思是"用每对的第 2 个元素（金额）来排序"
    items = list(by_category.items())
    items.sort(key=lambda kv: kv[1], reverse=True)

    print(f"总支出：{total:.2f} 元\n")
    print(f"{'类别':<8}{'金额':>10}{'占比':>8}")
    print("-" * 30)
    for name, amount in items:
        percent = amount / total * 100
        print(f"{name:<8}{amount:>10.2f}{percent:>7.1f}%")


# ============================================================
# 第四部分：菜单与主循环
# ============================================================

MENU = """
========== 记账本 ==========
  1. 添加一笔
  2. 查看全部
  3. 查看统计
  0. 退出
=========================="""


def main():
    # 启动时读一次，整个程序都在内存里的 records 上操作
    records = load_data()
    print(f"已加载 {len(records)} 条记录")

    while True:
        print(MENU)
        choice = input("请选择：").strip()

        if choice == "1":
            add_record(records)
        elif choice == "2":
            show_all(records)
        elif choice == "3":
            show_stats(records)
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选项，请输入 0-3 的数字")


if __name__ == "__main__":
    main()
