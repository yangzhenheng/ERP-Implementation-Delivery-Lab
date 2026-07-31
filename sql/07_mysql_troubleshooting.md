# MySQL Troubleshooting Notes

## Cannot connect

Check host, port, username, password, and database name from `.env`.

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p -e "SELECT 1"
ss -lntp | grep 3306
docker compose logs mysql
```

## Access denied

Confirm the user and host grant:

```sql
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'erp_user'@'%';
```

## Character encoding

Use `utf8mb4` for ERP master data and imported CSV text.

```sql
SHOW VARIABLES LIKE 'character_set%';
SHOW CREATE TABLE customers;
```

## Slow query

Run `EXPLAIN`, check join columns, and add targeted indexes only after confirming the query pattern.

```sql
EXPLAIN SELECT * FROM sales_orders WHERE status = 'confirmed';
```
