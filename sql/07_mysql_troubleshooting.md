# MySQL 排查笔记

## 无法连接

先检查 `.env` 中的主机、端口、用户名、密码和数据库名。

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p -e "SELECT 1"
ss -lntp | grep 3306
docker compose logs mysql
```

## 权限拒绝

确认用户和访问来源授权：

```sql
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'erp_user'@'%';
```

## 中文乱码

ERP 主数据和 CSV 导入文本建议使用 `utf8mb4`。

```sql
SHOW VARIABLES LIKE 'character_set%';
SHOW CREATE TABLE customers;
```

## 慢查询

先执行 `EXPLAIN`，确认 JOIN 字段和过滤字段，再根据真实查询场景增加索引。

```sql
EXPLAIN SELECT * FROM sales_orders WHERE status = 'confirmed';
```

面试讲解重点：数据库问题要先分清连接、权限、编码、表结构、索引和数据本身，不要一上来就猜代码错误。
