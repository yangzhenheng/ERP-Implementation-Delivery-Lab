# 项目验证证据

日期：2026-08-01

版本：3.0.0

## 已在本地真实验证

- 已执行自动化测试：`pytest -q`
- 测试结果：`24 passed`
- 已执行 Python 编译检查：`python -m compileall app scripts tests`
- 已执行 V3 本地 HTTP 验证：`python scripts/verify_v3.py --base-url http://127.0.0.1:8000`
- V3 API 验证结果：`/health`、`/api/dashboard`、`/api/customers`、`/api/products`、`/api/inventory`、`/api/orders`、`/api/issues`、`/api/implementation`、`/api/implementation/tasks`、`/api/commercial`、`/api/commercial/summary`、`/api/system/status` 均为 `PASS`
- V3 前端验证结果：`/dashboard`、`/customers`、`/orders`、`/commercial` 均为 `PASS`
- 已验证 CSV 导入脚本，结果为 `success=8, failed=0, skipped=0`
- 已执行 `scripts/network_check.py`，脚本真实报告本机 80/3306/6379 不可达，8000 可达
- 已执行严格验证：`python scripts/verify_v3.py --base-url http://localhost --require-full-stack`，结果 `strict_exit=1`，原因是 80/3306/6379 不可达

## 未验证项

- Docker Compose 全栈运行：`BLOCKED`
- MySQL 容器初始化和查询：`BLOCKED`
- Redis `PONG`：`BLOCKED`
- Nginx `http://localhost/health`：`BLOCKED`
- MySQL backup/restore 实跑：`BLOCKED`
- SQL Server 容器和 `sqlcmd` 执行：`BLOCKED`
- Nginx 502 故障注入和恢复：`BLOCKED`

原因：当前电脑无 `docker`、`mysql`、`mysqldump` 命令。所有未实跑内容均保持 `BLOCKED`，不伪造 PASS。
