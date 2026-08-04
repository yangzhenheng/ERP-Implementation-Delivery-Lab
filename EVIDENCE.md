# 项目验证证据

## V3.1 CI Verified Evidence

Status: **CI VERIFIED**

- Date: 2026-08-04
- PR: [#1](https://github.com/yangzhenheng/ERP-Implementation-Delivery-Lab/pull/1)
- Commit: `6222b6049924cdbd218ff5b58555bb9158522db3`
- CI run: [30896543782](https://github.com/yangzhenheng/ERP-Implementation-Delivery-Lab/actions/runs/30896543782)
- Full-stack run: [30896543839](https://github.com/yangzhenheng/ERP-Implementation-Delivery-Lab/actions/runs/30896543839)

Passed jobs: `Python tests (3.11)`, `Python tests (3.12)`, `unit-tests (3.11)`, `unit-tests (3.12)`, `e2e-sqlite`, `erp-full-stack`, and `sqlserver-lab`.

Verified evidence includes SQLite E2E (`4 passed`), per-service Docker health, MySQL backup/restore plus three application HTTP checks, strict Nginx 502/200 recovery, full-stack E2E (`4 passed`), SQL Server imports/queries/mutations, and Linux runtime.

Artifacts: `erp-full-stack-artifacts`, `e2e-sqlite-screenshots`, `sqlserver-lab-artifacts`.

Credential values are masked as `***` in successful Actions logs. No `.env`, backup SQL, token, or password is uploaded.

Local Windows remains **BLOCKED** because Docker is unavailable. The older local evidence below is retained for traceability and does not override CI VERIFIED.

日期：2026-08-04

版本：3.1.0

## 已在本地真实验证

- 已执行自动化测试：`pytest -q`
- 测试结果：`24 passed, 4 skipped`
- 已执行 Python 编译检查：`python -m compileall app scripts tests`
- 已执行 V3 本地 HTTP 验证：`python scripts/verify_v3.py --base-url http://127.0.0.1:8000`
- V3 API 验证结果：`/health`、`/api/dashboard`、`/api/customers`、`/api/products`、`/api/inventory`、`/api/orders`、`/api/issues`、`/api/implementation`、`/api/implementation/tasks`、`/api/commercial`、`/api/commercial/summary`、`/api/system/status` 均为 `PASS`
- V3 前端验证结果：`/dashboard`、`/customers`、`/orders`、`/commercial` 均为 `PASS`
- 已验证 CSV 导入脚本，结果为 `success=8, failed=0, skipped=0`
- 已执行 `scripts/network_check.py`，脚本真实报告本机 80/3306/6379 不可达，8000 可达
- 已执行严格验证：`python scripts/verify_v3.py --base-url http://localhost --require-full-stack`，结果 `strict_exit=1`，原因是 80/3306/6379 不可达
- 已执行 `pytest tests/e2e -q`，结果 `4 skipped`，原因是 Playwright 安装失败

## 未验证项

- Docker Compose 全栈运行：`BLOCKED`
- MySQL 容器初始化和查询：`BLOCKED`
- Redis `PONG`：`BLOCKED`
- Nginx `http://localhost/health`：`BLOCKED`
- MySQL backup/restore 实跑：`BLOCKED`
- SQL Server 容器和 `sqlcmd` 执行：`BLOCKED`
- Nginx 502 故障注入和恢复：`BLOCKED`

原因：当前电脑无 `docker`、`mysql`、`mysqldump` 命令。所有未实跑内容均保持 `BLOCKED`，不伪造 PASS。
