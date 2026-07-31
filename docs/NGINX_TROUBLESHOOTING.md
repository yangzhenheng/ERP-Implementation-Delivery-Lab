# Nginx 502 排查

## 现象

浏览器能访问 `http://localhost`，但页面或接口返回 `502 Bad Gateway`。

## 含义

Nginx 自己是可访问的，但它转发到后端 FastAPI 时失败。常见原因是后端服务没有启动、端口错误、容器网络不通，或 `proxy_pass` 指向了错误上游。

## 故意制造 502

仅在本地演示环境操作。把 `deploy/nginx/erp.conf` 中上游端口临时改错，例如：

```nginx
proxy_pass http://app:8999;
```

重启 Nginx：

```bash
docker compose restart nginx
curl -I http://localhost/health
```

## 检查命令

```bash
nginx -t
systemctl status nginx
docker compose ps
docker compose logs nginx
docker compose logs app
ss -lntp | grep -E ':80|:8000'
curl http://127.0.0.1:8000/health
curl http://localhost/health
```

## 排查顺序

1. 先确认 Nginx 配置语法是否正确。
2. 再确认 FastAPI 服务是否运行。
3. 检查 80 和 8000 端口是否监听。
4. 查看 Nginx 错误日志和应用日志。
5. 直接访问后端 `/health` 判断问题在 Nginx 还是应用。
6. 修复 `proxy_pass` 或后端服务后重新验证。

## 修复

Docker Compose 环境中应使用：

```nginx
proxy_pass http://app:8000;
```

重启服务并验证：

```bash
docker compose restart app nginx
curl http://localhost/health
```

面试讲解重点：不要只背“502 是网关错误”，要能讲清楚 Nginx、后端服务、端口、容器网络和日志之间的排查关系。
