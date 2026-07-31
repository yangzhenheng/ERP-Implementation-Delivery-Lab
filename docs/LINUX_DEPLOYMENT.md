# Linux Deployment Guide

This guide is for a local or interview demo Linux environment.

## Common Checks

```bash
uname -a
cat /etc/os-release
top
free -h
df -h
ps aux | grep uvicorn
ss -lntp
curl http://127.0.0.1:8000/health
ping -c 2 127.0.0.1
systemctl status nginx
journalctl -u nginx -n 100
tail -f logs/app.log
chmod +x deploy/linux/*.sh
chown -R appuser:appuser /opt/erp-lab
```

## Local Python Start

```bash
bash deploy/linux/environment_check.sh
bash deploy/linux/install.sh
bash deploy/linux/start.sh
bash deploy/linux/health_check.sh
```

Stop and restart:

```bash
bash deploy/linux/stop.sh
bash deploy/linux/restart.sh
```

## Docker Start

```bash
cp .env.example .env
docker compose up -d
docker compose ps
docker compose logs app
curl http://localhost/health
```

## MySQL Check

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo -e "SELECT COUNT(*) FROM customers;"
```

## Nginx Check

```bash
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
curl -I http://localhost/health
```
