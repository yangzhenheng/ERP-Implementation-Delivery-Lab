# V3 最终验收报告

时间：2026-08-01 16:02:27 +08:00

版本：3.0.0

项目：制造业 ERP 实施交付实验室 V3

## 验收结果

| 项目 | 状态 | 实际命令 | 关键输出摘要 |
|---|---|---|---|
| FastAPI | PASS | `python scripts/verify_v3.py --base-url http://127.0.0.1:8000` | `/health` HTTP 200 |
| pytest | PASS | `pytest -q` | `24 passed` |
| ERP frontend | PASS | `python scripts/verify_v3.py --base-url http://127.0.0.1:8000` | `/dashboard`、`/customers`、`/orders`、`/commercial` HTTP 200 |
| SQLite | PASS | `pytest -q` | 本地测试库可创建、写入、查询 |
| Docker | BLOCKED | `docker version` / `docker compose version` / `docker info` | `docker` 命令不存在 |
| MySQL | BLOCKED | Docker/MySQL 查询命令未执行 | Docker CLI 不存在 |
| Redis | BLOCKED | `docker compose exec redis redis-cli ping` 未执行 | Docker CLI 不存在 |
| Nginx | BLOCKED | `curl.exe -i http://localhost/health` 未执行 Nginx 链路 | Docker/Nginx 不可用 |
| CSV migration | PASS | `python scripts/import_data.py --folder data/import` | 干净临时库 `success=8, failed=0, skipped=0` |
| Backup | BLOCKED | `scripts/backup_mysql_container.ps1` 未执行 | Docker/MySQL 不可用 |
| Restore | BLOCKED | `scripts/restore_mysql_container.ps1` 未执行 | Docker/MySQL 不可用 |
| Network lab | PASS | `python scripts/network_check.py` | 脚本可运行，并真实报告端口状态 |
| SQL Server | BLOCKED | `docker compose -f docker-compose.database-lab.yml config` 未执行 | Docker CLI 不存在 |
| Oracle/DB2 docs | PASS | 文档检查 | 已覆盖基础方言认知，不声称精通 |
| Commercial module | PASS | `pytest -q` / `verify_v3.py` | 商务 API 和 `/commercial` 页面通过 |
| Nginx 502 recovery | BLOCKED | 故障脚本未执行 | Docker/Nginx 不可用 |
| E2E smoke test | NOT VERIFIED | 未安装/运行 Playwright | 已生成 `docs/SCREENSHOT_CHECKLIST.md` |

## V3 默认验证输出

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

## 严格全栈验证

命令：

```bash
python scripts/verify_v3.py --base-url http://localhost --require-full-stack
```

状态：`BLOCKED`

真实输出摘要：

```text
[FAIL] /health - [WinError 10061] 由于目标计算机积极拒绝，无法连接。
[FAIL] TCP Nginx Docker - localhost:80 unavailable: timed out
[FAIL] TCP MySQL Docker - localhost:3306 unavailable: timed out
[FAIL] TCP Redis Docker - localhost:6379 unavailable: timed out
strict_exit=1
```

原因：严格模式要求 80、3306、6379 均可达。当前 Docker CLI 不存在，Nginx/MySQL/Redis 无法启动，因此不能运行出 PASS。

## 已知限制

- 当前 Windows 环境没有 Docker CLI。
- 当前环境没有宿主机 `mysql` / `mysqldump`。
- SQL Server lab 依赖 Docker，尚未实跑。
- Nginx 502 故障恢复依赖 Docker/Nginx，尚未实跑。
- Playwright E2E 未安装和运行，改为截图清单。

## 最终结论

结论：**B. 可作为初级 ERP / 软件实施工程师面试项目**。

理由：本地 FastAPI、SQLite、ERP UI、CSV 迁移、商务模块、网络排障脚本、SQL/数据库认知和 24 个 pytest 测试均已通过；但 Docker/MySQL/Redis/Nginx/Backup/Restore/SQL Server/Nginx 502 恢复仍被当前环境阻塞，尚不能评为“较强初级”。
