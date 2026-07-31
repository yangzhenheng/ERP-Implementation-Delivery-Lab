# 数据迁移与 SQL 演练

## 导入前
- 确认字段字典、主键、唯一键、必填项、编码、日期格式、金额精度。
- 做数据库备份，记录导入批次和回滚方案。
- 先用 10-100 条样例数据跑通。

## 校验 SQL
```sql
SELECT COUNT(*) FROM orders;
SELECT status, COUNT(*), SUM(amount) FROM orders GROUP BY status;
SELECT sku,name,qty,safety_stock FROM inventory WHERE qty < safety_stock;
SELECT o.order_no,c.name,o.amount FROM orders o JOIN customers c ON c.id=o.customer_id;
```

## 事务原则
批量变更必须：BEGIN -> 校验 -> 写入 -> 再校验 -> COMMIT；任一步异常则 ROLLBACK。
