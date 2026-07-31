# Backup And Restore

Backups are required before go-live, data migration, upgrade and troubleshooting changes.

## MySQL Backup

```bash
bash scripts/backup_mysql.sh
```

Equivalent command:

```bash
mysqldump -h 127.0.0.1 -P 3306 -u erp_user -p --single-transaction erp_demo > backups/erp_demo.sql
```

## Restore

```bash
bash scripts/restore_mysql.sh backups/erp_demo.sql
```

Equivalent command:

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo < backups/erp_demo.sql
```

## Windows Notes

On Windows, run the same commands in Git Bash or WSL if `mysqldump` and `mysql` are installed and in PATH.

## Verification

```bash
python scripts/verify_deployment.py --base-url http://127.0.0.1:8000
```

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory;
```
