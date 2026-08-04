# V3.1 运行验证记录

时间：2026-08-04 12:58:47 +08:00

## Docker / MySQL / Redis / Nginx

| 命令 | 真实结果 | 状态 |
|---|---|---|
| `docker version` | `docker` 命令不存在 | BLOCKED |
| `docker compose version` | `docker` 命令不存在 | BLOCKED |
| `docker info` | `docker` 命令不存在 | BLOCKED |
| `docker compose config` | 未执行，Docker CLI 不存在 | BLOCKED |
| `docker compose down` | 未执行，Docker CLI 不存在 | BLOCKED |
| `docker compose build --no-cache` | 未执行，Docker CLI 不存在 | BLOCKED |
| `docker compose up -d` | 未执行，Docker CLI 不存在 | BLOCKED |
| `docker compose ps` | 未执行，Docker CLI 不存在 | BLOCKED |
| `curl.exe -i http://localhost/health` | 未执行 Nginx 入口验证，Docker/Nginx 不可用 | BLOCKED |
| MySQL `SHOW TABLES` / `SELECT COUNT(*)` | 未执行，Docker/MySQL 不可用 | BLOCKED |
| Redis `redis-cli ping` | 未执行，Docker/Redis 不可用 | BLOCKED |

结论：当前电脑没有 Docker CLI，不能真实验证 Docker、MySQL、Redis、Nginx。需要用户先安装并启动 Docker Desktop，再继续全栈实跑。

## 本地 FastAPI / SQLite

| 命令 | 真实结果 | 状态 |
|---|---|---|
| `python -m compileall app scripts tests` | 编译检查通过 | PASS |
| `pytest -q` | `24 passed` | PASS |
| `python scripts/verify_v3.py --base-url http://127.0.0.1:8000` | API 和前端页面均通过；Docker 端口为 SKIP；`default_exit=0` | PASS |
| `python scripts/verify_v3.py --base-url http://localhost --require-full-stack` | `localhost:80/3306/6379` 不可达；`strict_exit=1` | BLOCKED |
| `python scripts/network_check.py` | `localhost:8000` PASS；`localhost:80/3306/6379` FAIL；`network_exit=1` | BLOCKED |
| `pytest tests/e2e -q` | Playwright 未安装，`4 skipped` | NOT VERIFIED |

## .env 安全检查

| 命令 | 真实结果 | 状态 |
|---|---|---|
| `Test-Path .env` | 初始不存在，本次已生成本地 Demo `.env` | PASS |
| `git check-ignore .env` | 输出 `.env` | PASS |

`.env` 不会提交，报告不展示完整密码。
