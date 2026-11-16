"""
命令行记账本 v2（拆分版）
============================================
功能：添加一笔 / 查看全部 / 查看统计
数据：保存到 data.json（JSON 格式）

运行：python main.py      （在任意目录下都能运行）

文件分工：
    config.py    常量（数据文件路径、类别列表）
    storage.py   读 / 写 data.json
    inputs.py    三个 ask_ 函数（输入校验）
    report.py    打印表格和统计
    main.py      本文件：业务组装（add_record）+ 菜单 + 主循环

【读代码前先看这三条设计】
1. 所有记录放在一个 list 里，每条记录是一个 dict：
   [{"date": "2026-11-12", "amount": 25.5, "category": "餐饮", "note": "午饭"}, ...]
   这个"列表套字典"就是以后接口返回的 JSON 结构
2. 程序启动时把数据读进内存（records 变量），之后都在内存里操作
3. 每次改动后立刻写回文件（防止程序崩溃丢数据）

想对照"拆分前长什么样"：看同目录的 main_v1_single.py。
"""

from inputs import ask_amount, ask_category, ask_date
from report import show_all, show_stats
from storage import load_data, save_data

# ============================================================
# 第一部分：业务组装
# ============================================================

def add_record(records):
    """添加一笔。

    注意：这个函数里没有一句 input()，全交给 inputs.py 的 ask_ 函数。
    这叫"职责分离"—— 它只关心"问到了什么"，不关心"怎么问"。
    """
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
def delete_last(records):
    """删除最后一笔"""
    print("\n--- 删除最后一笔 ---")

    if not records:                          # 空账本不能删
        print("（账本是空的，没有可删除的记录）")
        return

    last = records[-1]                       # 取最后一条给它看
    print(f"最后一条：{last['date']}  {last['category']}  "
          f"{last['amount']:.2f} 元  {last['note']}")

    confirm = input("确认删除？(y/n)：").strip().lower()
    if confirm != "y":
        print("已取消")
        return

    records.pop()                            # 删最后一个
    save_data(records)                       # 立刻存盘
    print("[已删除]")

def show_by_category(records):
    """按类别筛选查看"""
    print("\n--- 按类别筛选 ---")
    if not records:
        print("（还没有任何记录）")
        return

    category = ask_category()          # ← 复用 inputs.py 里现成的

    filtered = []                      # 造一个新列表，不动原数据
    for r in records:
        if r["category"] == category:
            filtered.append(r)

    if not filtered:
        print(f"（没有「{category}」类别的记录）")
        return

    show_all(filtered)                 # ← 复用 report.py 里现成的

# ============================================================
# 第二部分：菜单与主循环
# ============================================================

MENU = """
========== 记账本 ==========
  1. 添加一笔
  2. 查看全部
  3. 查看统计
  4. 删除最后一笔
  5. 按类别筛选
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
        elif choice == "4":
            delete_last(records)
        elif choice == "5":
            show_by_category(records)
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选项，请输入 0-5 的数字")
if __name__ == "__main__":
    main()
