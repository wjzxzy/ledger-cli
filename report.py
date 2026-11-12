"""
report.py —— 展示层（打印表格和统计）
============================================
这一层的函数只做一件事：把 records 变成屏幕上的文字。
它们不修改 records，也不写文件 —— 传进来什么就打印什么。
"""


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
