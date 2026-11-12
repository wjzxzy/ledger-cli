"""
inputs.py —— 输入校验
============================================
三个函数，各自负责"拿到一个合法的输入"。
共同套路：while True → 试 → 不合法就 continue → 合法就 return

和你写的 get_number() 是同一个模式，只是多了 float 和列表选择。
这些函数只管"问"，不负责存盘、不负责打印表格。
"""

from datetime import date

from config import CATEGORIES


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
