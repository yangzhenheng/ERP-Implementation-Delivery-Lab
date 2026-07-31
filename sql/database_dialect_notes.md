# 常见数据库差异速查（面试/实施现场）

| 场景 | MySQL | Oracle | SQL Server | DB2 |
|---|---|---|---|---|
| 分页 | `LIMIT 20 OFFSET 0` | 12c+: `OFFSET ... FETCH` | `OFFSET ... FETCH` | `OFFSET ... FETCH` |
| 当前时间 | `NOW()` | `SYSDATE` / `SYSTIMESTAMP` | `GETDATE()` | `CURRENT TIMESTAMP` |
| 自增 | `AUTO_INCREMENT` | Identity/Sequence | `IDENTITY` | `GENERATED ... AS IDENTITY` |
| 空值替换 | `IFNULL/COALESCE` | `NVL/COALESCE` | `ISNULL/COALESCE` | `COALESCE` |
| 字符串连接 | `CONCAT` | `||` | `+` / `CONCAT` | `||` |

实施原则：先确认数据库版本、字符集/排序规则、账号权限、端口、时区、备份恢复方式，再执行 DDL/DML。不要把某一数据库方言直接复制到另一套数据库执行。
