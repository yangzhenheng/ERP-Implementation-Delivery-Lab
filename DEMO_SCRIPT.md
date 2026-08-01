# V3 面试演示脚本

目标时长：5-8 分钟。正常情况下优先通过 ERP UI 操作，Swagger 放在后面解释为“实施工程师联调接口时使用的工具”。

## 1 README + 项目边界

打开 `README.md`，先讲清楚：

- 这是个人独立搭建的 ERP 实施交付实验室。
- 数据全部是 Mock，不是真实客户生产数据。
- 真实验证状态以 README 和 V3 验收报告为准，Docker 未实跑就明确写 `NOT VERIFIED`。

## 2 Dashboard

访问：

```text
http://127.0.0.1:8000/dashboard
```

讲订单、销售金额、库存不足、未关闭问题、实施进度和系统状态。

## 3 UI 新增客户

进入：

```text
http://127.0.0.1:8000/customers
```

填写客户编码、客户名称、联系人、电话、地址并保存。

讲解重点：客户编码是订单、迁移和对账的关键字段，必须唯一。

## 4 UI 新增订单

进入：

```text
http://127.0.0.1:8000/orders
```

选择客户、产品和数量后创建订单。

## 5 库存扣减 / 库存不足

库存足够：订单状态为 `confirmed`，库存扣减。

库存不足：订单状态为 `inventory_failed`，页面提示：

```text
库存不足，已生成问题工单。
```

## 6 Issue 工单

进入：

```text
http://127.0.0.1:8000/issues
```

展示 P1-P4、open、investigating、resolved、closed，以及 root cause、solution、verification result。

## 7 MySQL 查询

如果 Docker/MySQL 可用，执行：

```sql
SHOW TABLES;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM inventory;
SELECT COUNT(*) FROM sales_orders;
```

当前本机无 Docker，因此这部分在 V3 报告中保持 `NOT VERIFIED`。

## 8 CSV migration

执行：

```bash
python scripts/import_data.py --folder data/import
```

讲字段校验、重复编码、关联客户/产品、错误日志和数量核对。

## 9 Docker ps

Docker 可用时：

```bash
docker compose ps
```

当前本机无 Docker 命令，不能伪造 Docker VERIFIED。

## 10 network_check

执行：

```bash
python scripts/network_check.py
```

讲 Host、DNS resolution、TCP port、HTTP endpoint。

## 11 Nginx 502

打开：

```text
docs/NGINX_TROUBLESHOOTING.md
network_lab/CASE04_nginx_502.md
```

说明 502 是 Nginx 可达但后端上游不可达或异常。

## 12 排障恢复

标准路径：

用户电脑 -> 网络 -> DNS/IP -> 80/443 -> Nginx -> FastAPI -> MySQL -> Redis -> 日志 -> 配置 -> 修复 -> 验证。

## 13 backup/restore

打开：

```text
docs/V3_BACKUP_RESTORE_EVIDENCE.md
scripts/backup_mysql.ps1
scripts/restore_mysql.ps1
```

当前本机没有真实 MySQL 服务，保持 `NOT VERIFIED`。

## 14 commercial milestone

进入：

```text
http://127.0.0.1:8000/commercial
```

讲合同总额、已收、待收、逾期，以及签约款、上线款、验收款。

强调：实施工程师通常不独立负责财务收款，但要配合确认上线和验收节点，推动项目满足回款条件。

## 15 培训

打开：

```text
docs/TRAINING_SCRIPT.md
```

说明如何给客户业务人员讲客户、产品、库存、订单、问题反馈路径。

## 16 上线验收

打开：

```text
docs/GO_LIVE_CHECKLIST.md
docs/V3_FINAL_ACCEPTANCE_REPORT.md
```

收尾话术：

> 这个项目不是商业客户案例，但它把实施工程师常见工作串成了一个可运行、可测试、可讲解的实验室。真实跑通的我写 VERIFIED，当前机器不能验证的 Docker/MySQL/Redis/Nginx/SQL Server/backup-restore 我写 NOT VERIFIED，不夸大。
