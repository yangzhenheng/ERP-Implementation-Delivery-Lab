# 备份与恢复

在上线切换、数据迁移、版本升级和故障处理前，必须先完成可恢复的数据库备份。

## MySQL 备份

```bash
bash scripts/backup_mysql.sh
```

等价命令：

```bash
mysqldump -h 127.0.0.1 -P 3306 -u erp_user -p --single-transaction erp_demo > backups/erp_demo.sql
```

## MySQL 恢复

```bash
bash scripts/restore_mysql.sh backups/erp_demo.sql
```

等价命令：

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo < backups/erp_demo.sql
```

## Windows 说明

如果在 Windows 上演示，建议使用 Git Bash 或 WSL 执行上述命令，并确认 `mysqldump`、`mysql` 已加入 `PATH`。

## 恢复后验证

```bash
python scripts/verify_deployment.py --base-url http://127.0.0.1:8000
```

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory;
```

面试讲解时重点说明：备份不是把文件导出来就结束，还要能恢复、能核对数量、能证明核心接口和业务流程恢复正常。
