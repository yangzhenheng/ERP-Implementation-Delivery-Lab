# CASE03 DNS 解析失败

## 现象

IP 可以访问，但域名访问失败。

## 检查

```powershell
nslookup erp.example.local
ping erp.example.local
tracert erp.example.local
```

```bash
dig erp.example.local
ping erp.example.local
traceroute erp.example.local
```

## 判断

DNS 记录、hosts 配置、内网 DNS 服务器或 VPN 路由都可能影响解析。

## 修复后验证

确认域名解析到正确 IP，再访问 `http://域名/health`。
