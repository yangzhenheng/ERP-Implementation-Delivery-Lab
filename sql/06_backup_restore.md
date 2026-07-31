# MySQL 备份与恢复练习

本实验室只使用模拟 ERP 业务数据。备份恢复流程是真实 MySQL 操作练习，但不包含任何生产客户数据。

## 备份

```bash
mysqldump -h 127.0.0.1 -P 3306 -u erp_user -p --single-transaction --routines --triggers erp_demo > backups/erp_demo_$(date +%Y%m%d_%H%M%S).sql
```

`--single-transaction` 适用于 InnoDB 表，可在不锁定正常读取的情况下获得一致性备份。

## 恢复

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo < backups/erp_demo_20260731_100000.sql
```

## 恢复后验证

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory_transactions;
```

恢复后还要验证 `/health`、`/api/dashboard` 和至少一个订单详情接口，确认系统不仅数据回来了，业务接口也能正常工作。
