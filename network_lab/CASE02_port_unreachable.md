# CASE02 端口不可达

## 现象

IP 能 ping 通，但 ERP 端口访问失败。

## 检查

```powershell
netstat -ano | findstr ":80"
netstat -ano | findstr ":8000"
Test-NetConnection localhost -Port 8000
```

```bash
ss -lntp | grep -E ':80|:8000'
nc -vz localhost 8000
```

## 判断

端口不可达通常是服务没启动、防火墙拦截、监听地址错误，或端口被占用。

## 修复后验证

重新启动服务后再次检查端口和 HTTP 接口。
