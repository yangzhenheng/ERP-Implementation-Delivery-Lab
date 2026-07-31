# Linux 部署与环境检查

本文件用于面试演示 Linux 实施基础能力，适用于本地或测试环境，不用于真实客户生产环境。

## 常用检查命令

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

## 本地 Python 启动

```bash
bash deploy/linux/environment_check.sh
bash deploy/linux/install.sh
bash deploy/linux/start.sh
bash deploy/linux/health_check.sh
```

停止和重启：

```bash
bash deploy/linux/stop.sh
bash deploy/linux/restart.sh
```

## Docker 启动

```bash
cp .env.example .env
docker compose up -d
docker compose ps
docker compose logs app
curl http://localhost/health
```

## MySQL 检查

```bash
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo -e "SELECT COUNT(*) FROM customers;"
```

## Nginx 检查

```bash
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
curl -I http://localhost/health
```

## 面试讲解重点

实施工程师到现场后，不能只说“系统打不开”，要按环境、服务、端口、网络、日志、数据库逐层排查，并把检查命令和结果记录下来。
