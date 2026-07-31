# 当前状态审计

审计日期：2026-08-01

## 升级前已有内容

- FastAPI 应用基础接口。
- SQLite 本地演示数据库。
- 简单驾驶舱页面。
- 初始部署示例和实施文档。
- 基础 pytest 测试。

## 审计发现

- 原项目业务模型较轻，无法充分支撑 ERP 实施面试讲解。
- 部分中文内容曾出现编码异常，不适合直接用于面试展示。
- 原 API 返回结构不统一。
- MySQL、Redis、Docker Compose、Nginx 没有形成完整部署链路。
- 数据迁移、备份恢复、Linux 脚本、故障演练和验收材料不完整。
- 测试覆盖范围较窄，缺少订单、库存、问题、数据导入等关键流程。

## 当前技术栈

- FastAPI
- Pydantic
- SQLAlchemy
- SQLite 本地演示模式
- MySQL 8 演示部署模式
- Redis 可降级状态检查
- Docker Compose
- Nginx
- pytest

## 当前数据库模型

核心表包括：

- `customers`
- `products`
- `warehouses`
- `inventory`
- `sales_orders`
- `sales_order_items`
- `inventory_transactions`
- `implementation_tasks`
- `issues`
- `operation_logs`

## 当前 API

- `GET /health`
- `GET /api/dashboard`
- `GET /api/customers`
- `POST /api/customers`
- `GET /api/products`
- `GET /api/inventory`
- `GET /api/orders`
- `POST /api/orders`
- `GET /api/orders/{id}`
- `GET /api/issues`
- `POST /api/issues`
- `PUT /api/issues/{id}`
- `GET /api/implementation/tasks`
- `POST /api/data/import`
- `GET /api/system/status`

## 当前验证结果

- `pytest -q`：`9 passed`
- Python 编译检查：PASS
- 本地 HTTP 验证：PASS
- CSV 导入：PASS
- Docker Compose YAML：PASS
- Docker 容器运行：NOT VERIFIED，原因是当前电脑没有可用 Docker 环境

## 项目边界

本项目定位为个人实施实验室。ERP 业务数据为模拟数据，不代表真实客户数据；项目可用于面试展示实施流程、技术链路和交付文档能力，但不能描述为真实客户生产项目。
