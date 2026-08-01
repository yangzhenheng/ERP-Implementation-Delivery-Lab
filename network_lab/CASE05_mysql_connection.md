# CASE05 MySQL 连接失败

## 现象

应用可启动，但 `/health` 或业务接口提示数据库连接失败。

## 检查

```powershell
Test-NetConnection localhost -Port 3306
docker compose logs mysql
```

```bash
ss -lntp | grep 3306
mysql -h 127.0.0.1 -P 3306 -u erp_user -p -e "SELECT 1"
docker compose logs mysql
```

## 判断

常见原因是 MySQL 未启动、端口冲突、账号密码错误、库名错误或容器健康检查未通过。

## 修复后验证

执行 `SELECT COUNT(*) FROM customers;`，再访问 `/health`。
