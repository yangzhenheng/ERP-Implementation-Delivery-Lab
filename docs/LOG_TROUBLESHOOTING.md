# 日志与端口排查

应用运行日志保存在 `logs/` 目录，接口响应中会返回 `x-request-id`，便于把用户反馈和服务端日志关联起来。

## 需要收集的信息

- 用户操作时间。
- 用户打开的页面或接口。
- 页面报错、HTTP 状态码或截图。
- 响应头中的 `x-request-id`。
- 应用日志、Nginx 日志、数据库连接错误。
- 当时服务状态和端口监听情况。

## 标准排查流程

1. 询问用户操作时间和报错现象。
2. 在测试环境复现同样操作。
3. 记录 `x-request-id`。
4. 搜索应用日志。
5. 查询 `operation_logs` 操作记录。
6. 检查端口、服务、网络和数据库。
7. 判断问题属于数据、配置、网络还是代码。
8. 修复后用接口和页面重新验证。
9. 记录原因、处理方案和验证结果。

## 常用命令

```bash
tail -f logs/app.log
grep "request_id=<id>" logs/app.log
docker compose ps
docker compose logs app
docker compose logs nginx
ss -lntp
curl http://127.0.0.1:8000/health
curl http://localhost/health
```

```sql
SELECT * FROM operation_logs WHERE request_id = '<id>';
```

面试讲解重点：实施工程师遇到“系统打不开”不能只转给开发，要能先把环境、端口、日志、数据库和操作记录查清楚。
