# CASE01 ERP 页面打不开

## 现象

客户反馈浏览器打不开 ERP。

## 检查

```powershell
ipconfig
ping localhost
Test-NetConnection localhost -Port 80
curl http://localhost/health
```

```bash
ip addr
ping localhost
ss -lntp
curl http://localhost/health
```

## 判断

先确认用户电脑网络，再确认 DNS/IP，再确认 80/443 端口和 Nginx 是否可达。

## 修复后验证

浏览器打开首页，执行 `/health` 和 `/api/dashboard`。
