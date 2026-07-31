# 故障排查手册

本手册用于本地演示环境的故障演练，所有操作都必须可恢复，不用于真实客户生产系统。

## 通用排查链路

用户反馈 -> 复现问题 -> 检查服务 -> 检查端口 -> 检查网络 -> 检查日志 -> 检查数据库 -> 判断根因 -> 修复 -> 验证 -> 记录。

## 常用命令

```bash
docker compose ps
docker compose logs app
docker compose logs mysql
docker compose logs nginx
ss -lntp
curl http://localhost/health
curl http://127.0.0.1:8000/health
tail -f logs/app.log
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo
```

## 演示案例

- `troubleshooting/CASE01_mysql_connection_failed.md`：MySQL 连接失败。
- `troubleshooting/CASE02_nginx_502.md`：Nginx 502。
- `troubleshooting/CASE03_fastapi_not_started.md`：FastAPI 未启动。
- `troubleshooting/CASE04_mysql_port_failed.md`：MySQL 端口不可达。
- `troubleshooting/CASE05_csv_field_error.md`：CSV 字段错误。

## 安全边界

- 只在本地演示环境制造故障。
- 不在真实客户系统上做破坏性测试。
- 每个故障都要有恢复方式。
- 记录修改内容、恢复方式和验证结果。

面试讲解重点：排障能力不是记命令，而是形成清晰路径，把“现象、证据、根因、修复、验证”串起来。
