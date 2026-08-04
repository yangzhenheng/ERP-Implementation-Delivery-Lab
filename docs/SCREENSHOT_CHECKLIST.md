# V3 截图清单

当前环境未能自动生成全栈截图，因为本机无 Docker CLI，Docker/MySQL/Redis/Nginx/SQL Server 页面和命令无法真实运行。

Docker Desktop 可用并完成全栈验证后，建议保存以下截图到 `docs/screenshots/`：

- `dashboard.png`：`http://localhost/dashboard`
- `customers.png`：客户管理页面，包含新增验证客户
- `orders.png`：销售订单页面，包含创建订单结果
- `issues.png`：问题工单页面
- `commercial.png`：项目商务页面，包含 100000、签约款、上线款、验收款
- `system_status.png`：系统状态页面，Redis 为 ok
- `docker_ps.png`：`docker compose ps`，显示 mysql/redis/app/nginx healthy
- `mysql_query.png`：MySQL 查询 customers/products/inventory/orders 数量
- `redis_pong.png`：`docker compose exec redis redis-cli ping` 返回 PONG
- `nginx_health.png`：`curl.exe -i http://localhost/health` 返回 HTTP 200
- `backup_restore.png`：备份恢复验证结果
- `sqlserver_query.png`：SQL Server 查询结果
- `nginx_502.png`：故障注入后 Nginx 返回 HTTP 502
- `nginx_recovered.png`：修复后 Nginx 恢复 HTTP 200

截图不得包含：

- `.env`
- 密码
- Token
- 完整数据库连接串
- 个人隐私信息
