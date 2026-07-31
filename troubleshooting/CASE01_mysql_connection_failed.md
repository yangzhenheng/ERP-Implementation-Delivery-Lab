# CASE01 MySQL 连接失败

安全边界：仅用于本地演示，可通过恢复 `.env` 回到正常状态。

## 现象

`APP_ENV=demo` 时，`/health` 返回数据库连接错误。

## 日志

应用日志中出现 access denied、unknown host、connection refused 等信息。

## 检查命令

```bash
cat .env
docker compose ps
docker compose logs mysql
mysql -h 127.0.0.1 -P 3306 -u erp_user -p -e "SELECT 1"
```

## 根因

DB 主机、端口、用户名、密码或数据库名配置错误。

## 解决

修复 `.env`，重启应用并验证：

```bash
docker compose restart app
curl http://localhost/health
```
