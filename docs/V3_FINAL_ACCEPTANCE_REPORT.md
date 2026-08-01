# V3 最终验收报告

时间：2026-08-01 15:35:43 +08:00

版本：3.0.0

项目：制造业 ERP 实施交付实验室 V3

## 验收结果

| 项目 | 状态 | 证据 |
|---|---|---|
| FastAPI | PASS | `python scripts/verify_v3.py`，`/health` HTTP 200 |
| pytest | PASS | `pytest -q` -> `24 passed` |
| ERP frontend | PASS | `/dashboard`、`/customers`、`/orders`、`/commercial` HTTP 200 |
| SQLite | PASS | 本地测试库和开发库可运行 |
| MySQL | NOT VERIFIED | 当前本机无 Docker/MySQL 运行环境 |
| Redis | NOT VERIFIED | 当前本机无 Docker/Redis 运行环境 |
| Nginx | NOT VERIFIED | 当前本机无 Docker/Nginx 运行环境 |
| Docker | NOT VERIFIED | `docker` 命令不存在 |
| CSV migration | PASS | `python scripts/import_data.py --folder data/import` -> `success=8, failed=0`；API 测试覆盖 |
| Backup | NOT VERIFIED | 缺 `mysqldump` 和 MySQL 服务 |
| Restore | NOT VERIFIED | 缺 `mysql` 和 MySQL 服务 |
| Network lab | PASS | `scripts/network_check.py` 已运行并真实报告端口状态 |
| SQL Server | NOT VERIFIED | 当前本机无 Docker，未启动 SQL Server lab |
| Oracle/DB2 docs | PASS | `docs/DATABASE_COMPATIBILITY_LAB.md` 已覆盖基础方言认知 |
| Commercial module | PASS | `GET /api/commercial/summary`、`GET /api/payment-milestones` 和 `/commercial` 已测试 |
| Fault recovery | NOT VERIFIED | Docker/Nginx 502 故障注入依赖 Docker 环境 |

## V3 API 验证输出

```text
== HTTP API ==
[PASS] /health - HTTP 200
[PASS] /api/dashboard - HTTP 200
[PASS] /api/customers - HTTP 200
[PASS] /api/products - HTTP 200
[PASS] /api/inventory - HTTP 200
[PASS] /api/orders - HTTP 200
[PASS] /api/issues - HTTP 200
[PASS] /api/implementation - HTTP 200
[PASS] /api/implementation/tasks - HTTP 200
[PASS] /api/commercial - HTTP 200
[PASS] /api/commercial/summary - HTTP 200
[PASS] /api/system/status - HTTP 200
== Frontend ==
[PASS] /dashboard - HTTP 200
[PASS] /customers - HTTP 200
[PASS] /orders - HTTP 200
[PASS] /commercial - HTTP 200
== TCP ==
[PASS] TCP FastAPI local - localhost:8000
[SKIP] TCP Nginx Docker - localhost:80 unavailable
[SKIP] TCP MySQL Docker - localhost:3306 unavailable
[SKIP] TCP Redis Docker - localhost:6379 unavailable
```

## 网络检查输出

```text
[PASS] DNS localhost -> 127.0.0.1
[FAIL] TCP localhost:80 timed out
[PASS] TCP localhost:8000
[FAIL] TCP localhost:3306 timed out
[FAIL] TCP localhost:6379 timed out
[FAIL] HTTP http://localhost/health timed out
[PASS] HTTP http://localhost:8000/health HTTP 200
```

解释：80、3306、6379 依赖 Docker/Nginx/MySQL/Redis，当前本机没有 Docker 环境，因此失败是预期真实结果，不应写成通过。

## 当前可面试演示范围

- ERP UI 打开和 Dashboard 查看。
- UI 新增客户。
- UI 创建订单。
- 库存充足扣减库存。
- 库存不足生成 Issue。
- Issue 状态流转。
- CSV 数据迁移。
- 商务里程碑展示。
- 网络排障脚本演示。
- SQL Server / Oracle / DB2 方言认知讲解。
- Swagger 作为接口联调工具说明。

## 当前未验证内容

- Docker Compose 全栈真实运行。
- MySQL 容器表结构和数据量查询。
- Redis `PONG`。
- Nginx 经 `http://localhost` 转发。
- MySQL backup/restore 实跑。
- SQL Server 容器启动和 `sqlcmd` 执行。
- Nginx 502 故障注入和恢复。

结论：V3 已适合初级 ERP / 软件实施工程师面试投递，用于展示实施流程、SQL、数据迁移、后台操作、问题闭环、商务节点、网络排障和诚实的验证边界。
