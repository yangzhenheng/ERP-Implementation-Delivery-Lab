# V3.1 MySQL 备份恢复证据

时间：2026-08-04 12:58:47 +08:00

范围：只允许操作本项目 Demo 数据库 `erp_demo`。

## 本次真实状态

| 项目 | 真实结果 | 状态 |
|---|---|---|
| Docker CLI | `docker` 命令不存在 | BLOCKED |
| MySQL 容器 | 未启动，依赖 Docker Desktop | BLOCKED |
| 宿主机 `mysql` | 未找到 | BLOCKED |
| 宿主机 `mysqldump` | 未找到 | BLOCKED |
| 容器内 `mysqldump` | 未执行，Docker 不可用 | BLOCKED |
| 容器内 restore | 未执行，Docker 不可用 | BLOCKED |

## 已补齐脚本

- `scripts/backup_mysql_container.ps1`
- `scripts/restore_mysql_container.ps1`
- `scripts/backup_mysql.ps1`
- `scripts/restore_mysql.ps1`
- `scripts/backup_mysql.sh`
- `scripts/restore_mysql.sh`

## 规定流程状态

| 步骤 | 要求 | 当前状态 |
|---|---|---|
| 1 | 查询当前客户数量 | BLOCKED |
| 2 | 容器内 `mysqldump` 生成 `backups/erp_demo_<timestamp>.sql` | BLOCKED |
| 3 | 确认备份文件存在、大小大于 0、包含 `CREATE TABLE` 和 `INSERT INTO` | BLOCKED |
| 4 | 插入 `BACKUP-RESTORE-VERIFY-001` | BLOCKED |
| 5 | 确认记录存在 | BLOCKED |
| 6 | Drop/Create 仅本项目 Demo 数据库并恢复备份 | BLOCKED |
| 7 | 确认测试客户不存在，原数量恢复 | BLOCKED |
| 8 | `curl.exe http://localhost/health`、`/api/customers`、`/api/dashboard` | BLOCKED |

`.gitignore` 已包含 `backups/`，实际备份 SQL 不会提交。

结论：备份恢复脚本已准备好，但当前环境缺 Docker/MySQL，不能把 Backup/Restore 标为 PASS。
