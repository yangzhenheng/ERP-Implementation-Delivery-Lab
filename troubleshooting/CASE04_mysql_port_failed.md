# CASE04 MySQL 端口不可达

安全边界：仅用于本地演示。

## 现象

数据库客户端无法连接 3306 端口。

## 日志

Docker MySQL 日志可能出现启动失败、初始化失败或健康检查未通过。

## 检查命令

```bash
docker compose ps mysql
docker compose logs mysql
ss -lntp | grep 3306
mysqladmin ping -h 127.0.0.1 -P 3306 -u erp_user -p
```

## 根因

MySQL 容器未启动、端口冲突，或健康检查尚未通过。

## 解决

检查端口占用后重启 MySQL：

```bash
docker compose restart mysql
docker compose ps
```
