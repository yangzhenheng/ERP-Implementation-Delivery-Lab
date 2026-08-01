# 数据库兼容实验室

定位：

- MySQL：项目主力数据库。
- SQL Server：实验数据库，用于补充国内项目常见数据库实施认知。
- Oracle / DB2：基础方言与实施认知，不声称精通。

## 常见方言对比

| 场景 | MySQL | SQL Server | Oracle | DB2 |
|---|---|---|---|---|
| 分页 | `LIMIT 10 OFFSET 20` | `OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` | `FETCH FIRST 10 ROWS ONLY` / `ROWNUM` | `FETCH FIRST 10 ROWS ONLY` |
| 取前 N 条 | `LIMIT 10` | `TOP 10` | `FETCH FIRST 10 ROWS ONLY` | `FETCH FIRST 10 ROWS ONLY` |
| 空值处理 | `IFNULL(a,b)` / `COALESCE` | `ISNULL(a,b)` / `COALESCE` | `NVL(a,b)` / `COALESCE` | `COALESCE` |
| 自增 | `AUTO_INCREMENT` | `IDENTITY(1,1)` | `SEQUENCE` / `IDENTITY` | `GENERATED AS IDENTITY` |
| 当前时间 | `NOW()` | `GETDATE()` | `SYSDATE` | `CURRENT TIMESTAMP` |
| 字符串拼接 | `CONCAT(a,b)` | `CONCAT(a,b)` / `a + b` | `a || b` | `a || b` |
| 日期加减 | `DATE_ADD()` | `DATEADD()` | `SYSDATE + 1` | `CURRENT DATE + 1 DAY` |
| 主键 | `PRIMARY KEY` | `PRIMARY KEY` | `PRIMARY KEY` | `PRIMARY KEY` |
| 常见文本类型 | `VARCHAR` / `TEXT` | `NVARCHAR` / `NVARCHAR(MAX)` | `VARCHAR2` / `CLOB` | `VARCHAR` / `CLOB` |

## 实施面试讲法

我在主项目中使用 MySQL / SQLite，能真实跑通本地开发和数据迁移。SQL Server 单独放在 `docker-compose.database-lab.yml` 和 `sql/sqlserver/` 中，用来练习国内项目中常见的 SQL Server 方言。

Oracle 和 DB2 我不说精通，但知道分页、自增、时间函数、空值函数和字符串拼接等常见差异。实施现场如果客户使用 Oracle/DB2，我会先确认版本、字符集、驱动、权限、分页写法、备份恢复方式和 SQL 方言差异，再做联调与迁移。
