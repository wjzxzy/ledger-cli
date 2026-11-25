# 记账服务 Ledger API

一个用 **Python + FastAPI + SQLite** 写的记账服务：命令行能用，HTTP API 能用，已部署在公网。

**在线演示** → **http://47.94.199.221/docs**

> 打开就是 Swagger UI，可以直接点 "Try it out" 调每一个接口。

---

## 目录

- [功能](#功能)
- [架构](#架构)
- [接口](#接口)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [测试](#测试)
- [部署](#部署)
- [项目结构](#项目结构)
- [设计取舍](#设计取舍)
- [已知局限](#已知局限)
- [演进过程](#演进过程)

---

## 功能

**HTTP API（7 个接口）**

- 新增 / 查询 / 修改 / 删除一笔支出
- 按类别筛选
- 统计：总笔数、总金额、按类别分组并按金额降序

**命令行（保留）**

- 菜单式增删查改 + 统计表格
- 与 API **共用同一个数据访问层**，数据源一致

---

## 架构

```
客户端（浏览器 / curl / 后续的 Agent）
   │  HTTP :80
   ▼
Nginx  反向代理
   │  proxy_pass → 127.0.0.1:8000
   ▼
uvicorn + FastAPI（7 个路由）
   │
   ▼
db.py   数据访问层
   │  sqlite3 参数化查询
   ▼
ledger.db   SQLite（自增主键 + 类别索引）
```

**关键设计：uvicorn 只监听 `127.0.0.1`，不直接暴露公网。** 唯一入口是 Nginx 的 80 端口，这样后端可以安全地假定"请求都来自可信代理"。

同一份 `db.py` 被 API 和 CLI 同时复用：

```
app.py ──┐
         ├──→ db.py ──→ ledger.db
main.py ─┘
```

---

## 接口

| 方法 | 路径 | 说明 | 成功状态码 |
|---|---|---|---|
| `GET` | `/` | 健康检查 | 200 |
| `GET` | `/records` | 查询全部，支持 `?category=餐饮` 筛选 | 200 |
| `GET` | `/records/stats` | 统计（总数 / 总额 / 按类别分组） | 200 |
| `GET` | `/records/{record_id}` | 查询单条，不存在返回 **404** | 200 |
| `POST` | `/records` | 新增一笔 | **201** |
| `PUT` | `/records/{record_id}` | 全量修改，不存在返回 **404** | 200 |
| `DELETE` | `/records/{record_id}` | 删除，不存在返回 **404** | **204** |

**请求体示例**

```json
{
  "date": "2026-11-22",
  "amount": 25.5,
  "category": "餐饮",
  "note": "午饭"
}
```

字段校验由 Pydantic 负责，缺字段返回 **422**：

```json
{"detail":[{"type":"missing","loc":["body","amount"],"msg":"Field required"}]}
```

**统计响应示例**

```json
{
  "total_count": 23,
  "total_amount": 1662.5,
  "by_category": [
    {"category": "购物", "cnt": 4, "amount": 844.0},
    {"category": "餐饮", "cnt": 8, "amount": 420.5},
    {"category": "娱乐", "cnt": 3, "amount": 233.0}
  ]
}
```

---

## 技术栈

| 层 | 选型 |
|---|---|
| Web 框架 | FastAPI（自动生成 OpenAPI 3.1 文档） |
| 数据校验 | Pydantic v2 |
| 数据库 | SQLite（标准库 `sqlite3`，参数化查询） |
| ASGI 服务器 | uvicorn |
| 反向代理 | Nginx |
| 进程管理 | systemd |
| 容器化 | Docker |
| 测试 | pytest（30 个测试） |
| 运行环境 | Python 3.12 / Ubuntu 24.04 |

---

## 快速开始

### 本地运行

```bash
git clone https://github.com/wjzxzy/ledger-cli.git
cd ledger-cli

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**启动 API：**

```bash
uvicorn app:app --reload
```

打开 **http://127.0.0.1:8000/docs**

**启动命令行版：**

```bash
python main.py
```

**灌一批演示数据（可选）：**

```bash
python seed.py --reset
```

### 只想用命令行跑（不装依赖也行）

核心逻辑只用标准库，`main.py` 不需要 FastAPI：

```bash
python main.py
```

---

## 测试

```bash
pytest -v
```

```
test_db.py  11 passed   数据层：增删改查、筛选、统计、ID 不复用、空库
test_api.py 15 passed   接口层：状态码、404/422、PUT 全量替换、路由顺序
```

**两层的分工：**

- `test_db.py` 直接用 `monkeypatch` 把 `DB_PATH` 指到临时文件，测 SQL 逻辑
- `test_api.py` 用 `TestClient` 不起服务就调接口，**专门钉住契约**（比如"422 的 `loc` 必须是 `["body", ...]` 而不是 `["query", ...]`"）

> 为什么两层都要：数据层测试测不到"参数从哪来"。曾经因为函数签名漏了 `: RecordIn` 类型注解，`POST` 从 201 变成 422，而 `test_db.py` 全绿——只有接口层测试能抓到。

---

## 部署

当前部署：阿里云轻量应用服务器（Ubuntu 24.04）+ Nginx + systemd，无 HTTPS（需要域名备案）。

### systemd

```ini
[Unit]
Description=Ledger API
After=network.target

[Service]
User=root
WorkingDirectory=/opt/ledger-cli
ExecStart=/opt/ledger-cli/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now ledger
```

### Nginx

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
nginx -t && systemctl reload nginx
```

**四个 `proxy_set_header` 不能省**：不传 `X-Real-IP`，后端日志里所有请求都来自 `127.0.0.1`，出问题无法定位真实客户端。

### Docker

```bash
docker build -t ledger-api .
docker run -d --name ledger \
  -p 8001:8000 \
  -e DB_PATH=/app/data/ledger.db \
  -v /opt/ledger-cli/data:/app/data \
  ledger-api
```

**为什么用卷挂载**：容器应保持无状态，数据通过 volume 落在宿主机，容器可以随时删除重建。`DB_PATH` 通过环境变量注入，代码里不写死路径。

### 备份

```bash
# 用 SQLite 的 backup API，不能直接 cp（正在写入时拷到的可能是损坏副本）
python3 -c "import sqlite3; s=sqlite3.connect('/opt/ledger-cli/ledger.db'); d=sqlite3.connect('/opt/backup/ledger-$(date +%F).db'); s.backup(d)"
```

配合 cron 每天执行，保留最近 7 份，并做过**恢复演练**（恢复出的条数与总额和线上一致）。

---

## 项目结构

```
ledger/
├── app.py            FastAPI 服务（7 个路由）
├── db.py             数据访问层（SQLite，唯一的 SQL 所在地）
├── config.py         常量与路径
│
├── main.py           命令行入口
├── inputs.py         命令行输入校验
├── report.py         命令行表格与统计（零依赖）
│
├── migrate.py        JSON → SQLite 的一次性迁移脚本
├── seed.py           演示数据生成
│
├── test_db.py        数据层测试（15 个）
├── test_api.py       接口层测试（15 个）
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── 代码详解.md        8 层代码通读材料
└── README.md
```

**依赖方向严格单向：**

```
app.py / main.py  →  db.py
main.py           →  inputs.py / report.py
                        ↓
                   config.py
```

没有循环依赖，`db.py` 不知道 api 的存在，`report.py` 不知道数据库的存在。

---

## 设计取舍

这几条是面试最常被问到的，每条都能对应到具体代码。

### 1. GET 绝不修改数据

HTTP 规定 GET 是**安全方法**，浏览器预加载、爬虫、CDN 都会随意 GET。最初的删除接口把 `records.pop()` 写进了 GET 里，这是事故隐患，后来拆成独立的 `DELETE`，返回 204。

### 2. PUT 是全量替换，不是部分更新

`RecordIn` 里除 `note` 外所有字段都必填。客户端要修改就必须传完整对象——这是 PUT 的语义。部分更新应该用 `PATCH`。

### 3. 静态路由必须写在动态路由前面

```python
@app.get("/records/stats")        # 必须在前
@app.get("/records/{record_id}")  # 必须在后
```

写反了，访问 `/records/stats` 时 `"stats"` 会被当成 id 去转 int，返回 422。FastAPI 按声明顺序匹配路由。

### 4. 类型注解是接口契约，不是注释

```python
def add_record(record: RecordIn):    # ✅ 从请求体取
def add_record(record):              # ❌ 变成必填的 query 参数
```

少了注解，FastAPI 会把 `record` 当成 URL 查询参数，请求体完全失效。判断依据是 422 响应里的 `loc` 字段：`["body", ...]` 才对，`["query", ...]` 说明注解丢了。

### 5. 空表的 SUM 必须用 COALESCE

```sql
SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM records
```

`SUM()` 在空表上返回 `NULL`，直接序列化给前端是 `null`，一参与运算就崩。所有聚合查询都要考虑"表是空的"。

### 6. 用 rowcount 判断"改没改到"

```python
cur = conn.execute("UPDATE records SET ... WHERE id = ?", (...))
return cur.rowcount > 0
```

`UPDATE` / `DELETE` 对不存在的 id 不报错，只是影响 0 行。必须靠 `rowcount` 才能返回正确的 404。

### 7. 金额用 float 是已知缺陷

```python
0.1 + 0.2 == 0.30000000000000004   # True
```

账本场景正确做法是用 `Decimal`，或者**以"分"为单位存整数**。当前版本为了教学简化用了 `float`，这是明确的技术债。

### 8. 为什么 SQLite 而不是 PostgreSQL

单机、单用户、写入量极小，SQLite 完全够用且零运维。**如果哪天要支持多实例部署，就必须换 PostgreSQL**——SQLite 的写锁是库级的，多进程并发写会锁竞争。

---

## 已知局限

| 局限 | 影响 | 后续方案 |
|---|---|---|
| **无 HTTPS** | 浏览器提示"不安全" | 需先有域名（国内要备案 2–3 周） |
| **SQLite 单写者** | 不适合多实例 | 换 PostgreSQL |
| **金额用 float** | 极端情况精度丢失 | `Decimal` 或存整数分 |
| **无鉴权** | 任何人可读写 | 加 API Key / JWT |
| **无分页** | 数据量大时 `/records` 全量返回 | 加 `limit` / `offset` |
| **单机部署** | 机器挂了服务就停 | 多实例 + 负载均衡 |
| 中文表格对齐 | CLI 输出略有错位 | 全角字符宽度计算 |

**这些都是明确的技术债，不是没想到。**

---

## 演进过程

这个项目是一步步长出来的，每个阶段解决一个具体问题：

| 阶段 | 做了什么 | 解决的问题 |
|---|---|---|
| 1 | 233 行单文件 CLI | 先让它能跑 |
| 2 | 拆成 5 个模块 | 改一个地方不用翻 233 行 |
| 3 | JSON → SQLite | 文件读写的并发与查询能力不足 |
| 4 | 加 HTTP API | CLI 只能在本地用 |
| 5 | 加测试（30 个） | 重构时无法确认有没有改坏 |
| 6 | systemd + Nginx + Docker | 让别人也能访问 |

**每一步都是被上一个阶段的问题逼出来的，不是为了用技术而用技术。**

---

## License

MIT
