# 制造业 ERP 实施交付实验室 V3.1

[![CI](https://github.com/yangzhenheng/ERP-Implementation-Delivery-Lab/actions/workflows/ci.yml/badge.svg)](https://github.com/yangzhenheng/ERP-Implementation-Delivery-Lab/actions/workflows/ci.yml)

ERP实施｜MySQL｜SQL Server｜Linux｜Docker｜Nginx｜Redis｜数据迁移｜故障排查｜培训｜上线验收

这是面向国内 ERP / 软件实施工程师岗位面试的个人实战项目。项目数据均为模拟数据，不代表真实客户生产系统。

## 当前真实验证状态

| 项目 | 状态 | 说明 |
|---|---|---|
| FastAPI | VERIFIED | 本地启动并通过 API 验证 |
| SQLite | VERIFIED | 本地开发数据库真实运行 |
| pytest | VERIFIED | `24 passed, 4 skipped`；E2E 因 Playwright 安装受限跳过 |
| CSV migration | VERIFIED | `success=8, failed=0` |
| ERP frontend | VERIFIED | `/customers`、`/orders` 等页面由测试覆盖 |
| Network lab | VERIFIED | `scripts/network_check.py` 可在 Windows 运行 |
| Commercial module | VERIFIED | 商务里程碑 API 和页面已测试 |
| Docker | BLOCKED | 当前本机无 `docker` 命令，Docker Desktop 程序也未找到 |
| MySQL | BLOCKED | Docker/MySQL 运行环境不可用 |
| Redis | BLOCKED | Docker/Redis 运行环境不可用 |
| Nginx | BLOCKED | Docker/Nginx 运行环境不可用 |
| Backup/Restore | BLOCKED | 当前无 Docker/MySQL/mysqldump |
| SQL Server | BLOCKED | 当前本机无 Docker，SQL Server lab 未实跑 |
| E2E smoke test | NOT VERIFIED | Playwright 安装被网络/镜像阻塞 |
| Oracle/DB2 docs | VERIFIED | 仅基础方言认知，不声称精通 |

## V3.1 验证重点

- 轻量 ERP 后台 UI：客户、产品、库存、订单、问题、实施任务、项目商务、系统状态。
- 订单可通过 UI 创建，库存不足时提示“库存不足，已生成问题工单”。
- 商务模块：模拟合同金额、签约款、上线款、验收款和回款状态。
- SQL Server 实验室：`docker-compose.database-lab.yml` 与 `sql/sqlserver/`。
- 数据库兼容说明：MySQL、SQL Server、Oracle、DB2 常见方言差异。
- 网络排障实验室：Windows / Linux 命令、端口、DNS、Nginx、数据库连接案例。
- V3 验证脚本严格模式：`scripts/verify_v3.py --require-full-stack`。
- Playwright E2E 冒烟测试文件：`tests/e2e/test_erp_ui.py`，当前环境未能安装浏览器依赖。

## 快速启动

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

访问：

- ERP 后台：`http://127.0.0.1:8000/`
- 客户管理：`http://127.0.0.1:8000/customers`
- 销售订单：`http://127.0.0.1:8000/orders`
- 项目商务：`http://127.0.0.1:8000/commercial`
- Swagger：`http://127.0.0.1:8000/docs`

Swagger 保留用于实施工程师 API 联调；5-8 分钟主演示优先通过 ERP UI 操作。

## 核心业务闭环

客户 -> 销售订单 -> 库存校验 -> 库存足够 -> 订单确认 -> 库存扣减 -> 库存流水。

库存不足时：

订单进入 `inventory_failed`，系统生成 Issue 工单，实施人员继续记录根因、解决方案和验证结果。

## API

- `GET /api/dashboard`
- `GET/POST /api/customers`
- `GET /api/products`
- `GET /api/inventory`
- `GET/POST /api/orders`
- `GET/POST/PUT /api/issues`
- `GET /api/implementation/tasks`
- `GET /api/projects`
- `GET /api/projects/{id}`
- `GET /api/commercial/summary`
- `GET /api/payment-milestones`
- `POST /api/data/import`
- `GET /api/system/status`

## Docker 全栈

当前本机未安装或未暴露 Docker CLI，不能真实验证 Docker/MySQL/Redis/Nginx。Docker Desktop 启动后执行：

```bash
cp .env.example .env
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose ps
curl http://localhost/health
curl http://localhost/api/dashboard
docker compose exec redis redis-cli ping
```

MySQL 检查：

```bash
docker compose exec mysql mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}
SHOW TABLES;
SELECT COUNT(*) FROM customers;
```

## SQL Server 实验室

Docker 可用后：

```bash
docker compose -f docker-compose.database-lab.yml up -d
```

脚本位置：

- `sql/sqlserver/01_schema.sql`
- `sql/sqlserver/02_seed.sql`
- `sql/sqlserver/03_queries.sql`

## 网络排障

```bash
python scripts/network_check.py
```

核心路径：用户电脑 -> 网络 -> DNS/IP -> 80/443 -> Nginx -> FastAPI -> MySQL -> Redis -> 日志 -> 配置 -> 修复 -> 验证。

## 质量门禁

```bash
python -m compileall app scripts tests
pytest -q
python scripts/verify_v3.py
python scripts/verify_v3.py --base-url http://localhost --require-full-stack
```

严格模式要求 80、3306、6379 均可达；当前环境因 Docker 不可用会阻塞，不可写成 PASS。

## 重点文档

- `DEMO_SCRIPT.md`
- `docs/V3_RUNTIME_VERIFICATION.md`
- `docs/V3_BACKUP_RESTORE_EVIDENCE.md`
- `docs/V3_FINAL_ACCEPTANCE_REPORT.md`
- `docs/DATABASE_COMPATIBILITY_LAB.md`
- `docs/NETWORK_TROUBLESHOOTING.md`
- `docs/PROJECT_COMMERCIAL_PROCESS.md`
