# SQL Server 实验验证记录

日期：2026-08-01

## 配置

- Compose 文件：`docker-compose.database-lab.yml`
- 官方镜像：`mcr.microsoft.com/mssql/server:2022-latest`
- 密码来源：`.env` 中的 `SQLSERVER_SA_PASSWORD`
- SQL 文件：`sql/sqlserver/01_schema.sql`、`02_seed.sql`、`03_queries.sql`

## 本机真实状态

| 项目 | 状态 | 证据 |
|---|---|---|
| Docker CLI | NOT VERIFIED | 当前本机 `docker` 命令不存在 |
| SQL Server 容器启动 | NOT VERIFIED | 依赖 Docker Desktop |
| `sqlcmd` 导入 schema | NOT VERIFIED | 依赖 SQL Server 容器 |
| 10 条以上 SQL 执行 | NOT VERIFIED | 依赖 SQL Server 容器 |

## 可执行命令

Docker Desktop 可用后执行：

```powershell
docker compose -f docker-compose.database-lab.yml up -d
docker compose -f docker-compose.database-lab.yml ps
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/01_schema.sql
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/02_seed.sql
docker compose -f docker-compose.database-lab.yml exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:SQLSERVER_SA_PASSWORD -C -i /sqlserver-lab/03_queries.sql
```

结论：SQL Server 实验材料已准备好，但当前电脑不能真实验证，因此状态保持 `NOT VERIFIED`。
