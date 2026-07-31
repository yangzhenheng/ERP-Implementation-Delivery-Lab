# 面试演示主流程

这份脚本按 8-12 分钟准备，用来展示“会做 ERP 实施交付”，而不是只会打开一个页面。演示时可以根据面试官追问缩短或展开。

## 1. 打开 ERP

打开首页：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

浏览器访问：

```text
http://127.0.0.1:8000
```

讲解重点：这是一个制造业 ERP 实施交付实验室，覆盖客户、产品、订单、库存、问题、实施任务、部署、数据迁移、日志排查、备份恢复、培训和验收。

## 2. 新增客户

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

调用 `POST /api/customers`：

```json
{
  "customer_code": "CUST-900",
  "customer_name": "杭州智能装备有限公司（模拟）",
  "contact": "周经理",
  "phone": "13890000000",
  "address": "浙江省杭州市模拟产业园",
  "status": "active"
}
```

讲解重点：客户编码是订单、迁移、对账的关键字段，实施时必须先保证主数据编码规则清晰。

## 3. 创建订单

调用 `POST /api/orders`，选择已有客户和产品：

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

讲解重点：ERP 订单不是简单保存表单，必须联动库存、金额、状态和后续问题处理。

## 4. 库存校验

再创建一个超过库存的订单，例如标签打印机当前库存不足：

```json
{
  "customer_id": 2,
  "items": [
    {
      "product_id": 2,
      "quantity": 999
    }
  ]
}
```

讲解重点：库存充足时订单确认并扣减库存；库存不足时订单进入“库存校验失败”，同时生成问题记录，方便实施人员跟进。

## 5. SQL 查数据库

打开 `sql/03_queries.sql`，重点演示：

```sql
SELECT p.product_code, p.product_name, w.warehouse_code, i.quantity, i.safety_stock
FROM inventory i
INNER JOIN products p ON p.product_id = i.product_id
INNER JOIN warehouses w ON w.warehouse_id = i.warehouse_id
WHERE i.quantity < i.safety_stock;
```

讲解重点：实施顾问需要能用 SQL 直接核对客户、订单、库存、问题和迁移结果，尤其是 JOIN、GROUP BY、HAVING 和异常数据查询。

## 6. CSV 迁移客户历史数据

查看示例文件：

```text
data/import/customers.csv
data/import/products.csv
data/import/inventory.csv
data/import/orders.csv
```

执行导入：

```bash
python scripts/import_data.py --folder data/import
```

讲解重点：迁移不是直接导入，还要做必填字段、重复编码、数据类型、关联客户/产品、导入日志和数量核对。

## 7. Docker 查看服务

如果本机已安装 Docker Desktop：

```bash
docker compose up -d --build
docker compose ps
docker compose logs app
docker compose logs mysql
docker compose logs nginx
```

讲解重点：完整环境包含 FastAPI、MySQL、Redis 和 Nginx，实施时要会看服务状态、端口和日志。

## 8. 故意制造 Nginx 502

仅在本地演示环境操作。可以把 `deploy/nginx/erp.conf` 中上游端口临时改错，例如从 `8000` 改成 `8999`，然后重启 Nginx：

```bash
docker compose restart nginx
curl -I http://localhost/health
```

讲解重点：502 代表 Nginx 能访问，但后端上游不可达或返回异常。

## 9. 检查日志和端口

```bash
docker compose ps
docker compose logs nginx
docker compose logs app
ss -lntp | grep -E ':80|:8000'
curl http://127.0.0.1:8000/health
curl http://localhost/health
```

讲解重点：排障顺序是复现现象、看服务、看端口、看日志、验证上游、定位配置。

## 10. 修复

把 Nginx 上游恢复为：

```nginx
proxy_pass http://app:8000;
```

重启并验证：

```bash
docker compose restart app nginx
curl http://localhost/health
```

讲解重点：修复后必须用健康检查和业务接口验证结果，并记录原因、处理方式和验证结果。

## 11. MySQL 备份恢复

备份：

```bash
bash scripts/backup_mysql.sh
```

恢复：

```bash
bash scripts/restore_mysql.sh backups/erp_demo.sql
```

验证：

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory;
```

讲解重点：上线、迁移、升级前必须备份，备份后要能恢复，恢复后要能核对数据。

## 12. 展示培训手册

打开：

```text
docs/TRAINING_SCRIPT.md
docs/implementation/09_用户培训手册.md
```

讲解重点：实施交付不仅是部署，还要让客户业务人员知道怎么操作、怎么反馈问题、找谁处理。

## 13. 展示上线与验收清单

打开：

```text
docs/GO_LIVE_CHECKLIST.md
docs/implementation/11_项目验收清单.md
FINAL_ACCEPTANCE_REPORT.md
```

讲解重点：上线前确认环境、备份、迁移、接口、培训和支持；上线后持续看日志和问题；验收时按清单确认交付边界。

## 收尾话术

这个项目不是我参与过的真实客户生产系统，而是我独立搭建的 ERP 实施交付实验室。模拟数据是假的，但部署、接口、SQL、迁移、库存校验、问题闭环、日志排查、备份恢复、培训和验收材料都是我实际整理和验证的内容。它证明我理解国内实施岗位从“系统能跑”到“客户能用、问题能闭环、结果能验收”的完整过程。
