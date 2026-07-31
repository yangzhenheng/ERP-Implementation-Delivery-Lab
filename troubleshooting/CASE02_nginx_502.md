# CASE02 Nginx 502

安全边界：仅用于本地演示。

## 现象

浏览器能打开 `http://localhost`，但 Nginx 返回 `502 Bad Gateway`。

## 日志

Nginx 错误日志提示 upstream connection failed。

## 检查命令

```bash
docker compose ps
docker compose logs nginx
docker compose logs app
curl http://127.0.0.1:8000/health
ss -lntp | grep 8000
```

## 根因

FastAPI 没有运行、应用健康检查失败，或 Nginx 上游主机/端口配置错误。

## 解决

修复上游配置并重启服务：

```bash
docker compose restart app nginx
curl http://localhost/health
```
