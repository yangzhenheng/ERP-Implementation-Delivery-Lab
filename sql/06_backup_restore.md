# MySQL Backup And Restore

This lab uses mock ERP business data. The backup process is real MySQL practice, but it does not contain production customer data.

## Backup

```bash
mysqldump -h 127.0.0.1 -P 3306 -u erp_user -p --single-transaction --routines --triggers erp_demo > backups/erp_demo_$(date +%Y%m%d_%H%M%S).sql
```

Use `--single-transaction` for InnoDB tables so the backup is consistent without locking normal reads.

## Restore

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo < backups/erp_demo_20260731_100000.sql
```

## Verification

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory_transactions;
```

After restore, verify `/health`, `/api/dashboard`, and one order detail API.
