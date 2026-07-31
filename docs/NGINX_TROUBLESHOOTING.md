# Nginx Troubleshooting

## 502 Bad Gateway

Meaning: Nginx is reachable, but its upstream FastAPI service is not reachable or returns an invalid response.

## Checks

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

## Root Cause Examples

- FastAPI container is not healthy.
- Upstream name in Nginx config is wrong.
- App port is not listening.
- Docker network cannot resolve the `app` service.

## Fix

Confirm `deploy/nginx/erp.conf` uses `proxy_pass http://app:8000;` in Docker Compose. Restart:

```bash
docker compose restart app nginx
```
