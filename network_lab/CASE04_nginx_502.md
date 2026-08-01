# CASE04 Nginx 502

## 现象

Nginx 可访问，但返回 `502 Bad Gateway`。

## 检查

```bash
docker compose ps
docker compose logs nginx
docker compose logs app
curl http://127.0.0.1:8000/health
curl http://localhost/health
```

## 判断

常见根因是 FastAPI 未启动、上游端口错误、容器网络不通或健康检查失败。

## 修复后验证

恢复 `proxy_pass http://app:8000;` 后重启 Nginx，并验证 `/health`。
