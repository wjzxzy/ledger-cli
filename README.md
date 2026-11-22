## 🔗 在线演示


- **API 文档**：http://47.94.199.221/docs
- 架构：Nginx 反向代理（80）→ uvicorn（127.0.0.1:8000）→ SQLite
- 部署环境：阿里云轻量应用服务器（Ubuntu 24.04）+ systemd 常驻
- 免费/低成本实例，如遇无法访问请稍后重试

## 技术栈

Python 3.12 · FastAPI · SQLite · pytest（26 个测试）
# 命令行记账本

用 Python 标准库写的命令行记账工具：记录支出、查看明细、按类别统计占比。数据存本地 JSON，无需数据库、无需第三方库。

这是一个**重构练习项目**：v1 是 233 行单文件，v2 拆成 5 个模块。两个版本都保留，可以对照阅读。

运行效果：

```
========== 记账本 ==========
  1. 添加一笔
  2. 查看全部
  3. 查看统计
  0. 退出
==========================

--- 统计 ---
总支出：157.50 元

类别          金额     占比
------------------------------
购物        128.00   81.3%
餐饮         25.50   16.2%
交通          4.00    2.5%
```

## 怎么运行

```powershell
cd C:\Users\ASUS\Desktop\工作2\命令行记账本 v1
python main.py
```

第一次运行会看到「已加载 0 条记录」，添加一笔后会自动生成 `data.json`。

在别的目录下运行也可以，`data.json` 会固定生成在这个文件夹里：

```powershell
python "C:\Users\ASUS\Desktop\工作2\命令行记账本 v1\main.py"
```

不需要装任何第三方库，只用 Python 标准库（`json` / `datetime` / `pathlib`）。

---

## 文件

| 文件 | 说明 |
|---|---|
| `main.py` | **入口**：`add_record()` + 菜单 + 主循环。`python main.py` 跑的就是它 |
| `config.py` | 常量：`DATA_FILE` 路径、`CATEGORIES` 类别列表 |
| `storage.py` | 数据读写：`load_data()` / `save_data()`，只和 `data.json` 打交道 |
| `inputs.py` | 输入校验：`ask_amount()` / `ask_category()` / `ask_date()` |
| `report.py` | 展示层：`show_all()` / `show_stats()`，只打印，不改数据 |
| `main_v1_single.py` | **拆分前的原始单文件**（233 行），一个字没改，留着对照和复习 |
| `data.json` | 运行时自动生成，你的数据 |

## 模块之间怎么连的

```
main.py ──┬─→ config.py          拿 DATA_FILE、CATEGORIES
          ├─→ storage.py ───────→ config.py
          ├─→ inputs.py ────────→ config.py（拿 CATEGORIES）
          └─→ report.py
```

三条规矩，这就是拆文件的意义：

- `storage.py` / `inputs.py` / `report.py` **谁都不 import `main.py`** → 单独测一个文件不用拉起整个程序
- 想改类别、加类别 → 只改 `config.py`
- 想改打印格式 → 只改 `report.py`
- 想换存储方式（CSV / SQLite）→ 只改 `storage.py`，其他文件一行不动

一句话：**改一个地方，不用在 233 行里翻。**

---

## 怎么读这份代码（重要）

**不要从第 1 行读到最后 1 行。** 按下面顺序读，每读完一块，回去看菜单里对应的功能。

> 下面的行号都指 `main_v1_single.py`（拆分前的原始单文件）。它是完整的一整块，最适合按顺序读。
> 读完再对照拆分版，就知道每一块该住在哪个文件里：
> `main()` / `add_record()` → `main.py`；`ask_*` → `inputs.py`；`show_*` → `report.py`；`load_data` / `save_data` → `storage.py`；常量 → `config.py`。

### 第 1 步：读 `main()`（第 210–233 行）

先看程序怎么转起来的。你会发现它只有 6 个分支，每个分支调一个函数。

**这一块要理解的事**：
- `records = load_data()` 为什么写在 `while True` **外面**？
  → 因为只在启动时读一次，之后都在内存里操作
- 为什么 `0` 是 `break`，其他是 `continue` 式的分支？

### 第 2 步：读 `add_record()`（第 119–137 行）

最短的一个功能函数，把三个 `ask_` 函数串起来。

**要理解**：它自己没有一句 `input()`，全交给 `ask_` 函数。这叫"职责分离"。

### 第 3 步：读三个 `ask_` 函数（第 67–112 行）

三个函数是同一个套路：

```python
while True:
    try:
        x = 转换(input(...))
    except ValueError:
        continue        # 格式错 → try 接住
    if 不合法:
        continue        # 值域错 → if 判断
    return x            # 合法 → 返回
```

**这就是你 `guess.py` 里 `get_number()` 的模式，只是多了 `float` 和列表选择。**

### 第 4 步：读 `show_all()`（第 139–157 行）

**要理解的三处**：
- `if not records: return` —— 空列表提前返回，避免后面报错
- `{r['date']:<12}` —— 左对齐占 12 格；`{r['amount']:>10.2f}` —— 右对齐占 10 格保留 2 位小数
- `total += r["amount"]` —— 边打印边累加，一次遍历干两件事

### 第 5 步：读 `show_stats()`（第 159–194 行）

**这一块最有价值，是 `wordcount.py` 的进阶版**：

```python
by_category = {}
for r in records:
    c = r["category"]
    if c in by_category:
        by_category[c] += r["amount"]     # 已有 → 累加
    else:
        by_category[c] = r["amount"]      # 没有 → 建键
```

然后是排序：

```python
items = list(by_category.items())          # [('餐饮', 25.5), ('交通', 4.0)]
items.sort(key=lambda kv: kv[1], reverse=True)
```

`lambda kv: kv[1]` 的意思是"**用每对的第 2 个元素来排序**"。
`kv` 是任意起的名字，代表一个元组，`kv[0]` 是类别名，`kv[1]` 是金额。

### 第 6 步：最后读 `load_data()` / `save_data()`（第 30–56 行）

**两个参数的作用（必须记住）**：

```python
json.dump(records, f, ensure_ascii=False, indent=2)
#                     ↑ 中文正常显示    ↑ 有缩进，人能看懂

json.load(f)   # 读回来就是 list/dict，不用自己解析
```

---

## 5 个关键设计决策（面试能讲的）

| 决策 | 为什么 |
|---|---|
| **用 JSON 不用 CSV** | 备注里可能有逗号；JSON 原生支持嵌套结构；**接口返回的就是 JSON** |
| **列表套字典** | 一条记录 = 一个 dict；整个账本 = list。这个结构以后每天都在用 |
| **每次改动立刻存盘** | 程序崩溃也不丢数据。代价是多写几次文件，但账本数据量小，无所谓 |
| **输入校验单独成函数** | `add_record` 不用关心"怎么问"，只关心"问到了什么" |
| **`if not records: return`** | 防御性编程：空数据不进入后续逻辑 |

---

## 4 个练习（改需求，检验是否真懂）

按难度排，每做完一个就 `git commit` 一次。

### 练习 1：加"删除最后一笔"（简单）
在菜单加 `4. 删除最后一笔`，删掉后 `save_data()`。
- 涉及：`records.pop()`、`len(records) == 0` 的判断
- 拆分后加在哪：菜单分支加 `main.py`，`pop` + 存盘可以写成一个新函数放 `main.py`

### 练习 2：加"按类别筛选"（中等）
选类别后只显示这个类别的记录和小计。
- 涉及：列表推导式或 `for` + `if` 过滤
- 拆分后加在哪：过滤逻辑放 `report.py`，类别选择复用 `inputs.ask_category()`

### 练习 3：加"按月份筛选"（中等）
输入 `2026-11`，只看这个月的记录。
- 涉及：`r["date"].startswith("2026-11")`

### 练习 4：加"修改某一笔"（较难）
显示所有记录的**编号**，输入编号后重新填写金额和备注。
- 涉及：`enumerate(records, start=1)`、按编号改

---

## 两个已知局限（还没处理）

**1. 中文对齐会差一点**

`{name:<8}` 里，Python 把「餐饮」算作 **2 个字符**，但屏幕上占 **4 个字符宽**（中文是全角）。所以表格会略微错位。

> 真实项目里要么用等宽全角字符对齐函数，要么干脆输出 JSON 给前端排版。**知道有这回事就行。**

**2. 金额用 `float`，有精度问题**

```python
0.1 + 0.2 == 0.30000000000000004    # True
```

账本这种场景，正确做法是用 `Decimal` 或者**以"分"为单位存整数**（25.5 元存成 2550）。

> 这道题面试真的会问："为什么金额不能用 float？"答案就是精度丢失。**现在先知道，等做支付类功能时再改。**

> 拆分文件**没有**动这两处逻辑，行为和 v1 完全一致。

---

## v2 进度

- [x] **拆文件**：`config.py`（常量）/ `storage.py`（读写）/ `inputs.py`（输入校验）/ `report.py`（打印统计）/ `main.py`（菜单入口）
      —— 比原计划多拆了 `config.py` 和 `inputs.py`，因为"常量"和"输入校验"也不该塞在入口文件里
- [ ] 加上练习 1 和 2 的功能
- [ ] 加 `pytest` 测试：`tests/test_storage.py`（读写、坏文件）、`tests/test_report.py`（统计、占比）
      拆分之后这些函数可以直接 import 进来测，不用再模拟整个菜单

> **先让它跑起来，再让它整洁。** 这个顺序不能反。
