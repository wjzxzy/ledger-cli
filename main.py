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
import db
import report
from inputs import ask_amount, ask_category, ask_date
from report import show_all, show_stats
from storage import load_data, save_data

# ============================================================
# 第一部分：业务组装
# ============================================================
db.init_db()          # 确保表存在
def add_record():
    print("\n--- 添加一笔 ---")
    d = ask_date()
    amount = ask_amount()
    category = ask_category()
    note = input("备注（可留空）：").strip()

    new_id = db.add_record(d, amount, category, note)
    print(f"[已记录] id={new_id}  {d}  {category}  {amount:.2f} 元")

def show_all():
    report.show_all(db.list_records())

def delete_last():
    print("\n--- 删除最后一笔 ---")
    records = db.list_records()
    if not records:
        print("（账本是空的）")
        return

    last = records[-1]
    print(f"最后一条：{last['date']}  {last['category']}  {last['amount']:.2f} 元")
    if input("确认删除？(y/n)：").strip().lower() != "y":
        print("已取消")
        return

    db.delete_record(last["id"])        # ← 用 id 删，不是 pop
    print("[已删除]")

def show_by_category():
    if not db.list_records():
        print("（还没有任何记录）")
        return
    category = ask_category()
    rows = db.list_records(category)     # ← 用 SQL 的 WHERE，不是 Python 的 for-if
    if not rows:
        print(f"（没有「{category}」类别的记录）")
        return
    report.show_all(rows)

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
    db.init_db()
    print(f"已加载 {len(db.list_records())} 条记录")
    while True:
        print(MENU)
        choice = input("请选择：").strip()

        if choice == "1":
            add_record()
        elif choice == "2":
            show_all()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            delete_last()
        elif choice == "5":
            show_by_category()
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选项，请输入 0-5 的数字")
if __name__ == "__main__":
    main()
