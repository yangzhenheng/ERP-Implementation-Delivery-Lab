# V3 MySQL 备份恢复证据

时间：2026-08-01 15:35:43 +08:00

范围：只允许操作本项目 demo 数据库 `erp_demo`。

## 工具检查

| 命令 | 结果 | 状态 |
|---|---|---|
| `Get-Command mysql` | 未找到 `mysql` | FAIL |
| `Get-Command mysqldump` | 未找到 `mysqldump` | FAIL |
| `docker --version` | 未找到 `docker` | FAIL |

## 规定流程状态

| 步骤 | 要求 | 当前结果 | 状态 |
|---|---|---|---|
| 1 | `SELECT COUNT(*) FROM customers;` 记录原数量 | 未执行，缺 MySQL 运行环境 | NOT VERIFIED |
| 2 | 执行 `mysqldump` 到 `backups/erp_demo_<timestamp>.sql` | 未执行，缺 `mysqldump` | NOT VERIFIED |
| 3 | 插入 `BACKUP-TEST-001` | 未执行，缺 MySQL 运行环境 | NOT VERIFIED |
| 4 | 确认记录存在 | 未执行 | NOT VERIFIED |
| 5 | 恢复 backup | 未执行 | NOT VERIFIED |
| 6 | 确认 `BACKUP-TEST-001` 不存在且数量恢复 | 未执行 | NOT VERIFIED |
| 7 | `curl http://localhost/health` 和 `/api/customers` | 未执行 Docker/Nginx/MySQL 链路 | NOT VERIFIED |

## 已完成脚本

- `scripts/backup_mysql.sh`
- `scripts/restore_mysql.sh`
- `scripts/backup_mysql.ps1`
- `scripts/restore_mysql.ps1`

`.gitignore` 已包含 `backups/*.sql`，备份文件不会提交。

结论：备份恢复脚本已补齐，但当前机器缺 Docker/MySQL 客户端，不能真实执行 backup/restore。因此状态必须保持 `NOT VERIFIED`。
