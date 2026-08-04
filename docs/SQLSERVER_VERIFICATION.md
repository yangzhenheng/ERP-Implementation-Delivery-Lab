# SQL Server 实验验证记录

时间：2026-08-04 12:58:47 +08:00

## 配置

- Compose 文件：`docker-compose.database-lab.yml`
- 官方镜像：`mcr.microsoft.com/mssql/server:2022-latest`
- 密码来源：`.env` 中的 `SQLSERVER_SA_PASSWORD`
- SQL 文件：`sql/sqlserver/01_schema.sql`、`02_seed.sql`、`03_queries.sql`

## 本次真实状态

| 项目 | 真实结果 | 状态 |
|---|---|---|
| `docker version` | `docker` 命令不存在 | BLOCKED |
| `docker compose -f docker-compose.database-lab.yml config` | 未执行，Docker CLI 不存在 | BLOCKED |
| SQL Server 容器启动 | 未执行，依赖 Docker Desktop | BLOCKED |
| SQL Server healthy | 未执行，依赖 Docker Desktop | BLOCKED |
| `sqlcmd` 导入 schema | 未执行，依赖 SQL Server 容器 | BLOCKED |
| 10 条以上 SQL 执行 | 未执行，依赖 SQL Server 容器 | BLOCKED |

## Docker 可用后执行

```powershell
docker compose -f docker-compose.database-lab.yml config
docker compose -f docker-compose.database-lab.yml up -d
docker compose -f docker-compose.database-lab.yml ps
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/01_schema.sql
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/02_seed.sql
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/03_queries.sql
```

结论：SQL Server 实验材料已准备好，但当前电脑无 Docker，不能把 SQL Server 标为 VERIFIED/PASS。
