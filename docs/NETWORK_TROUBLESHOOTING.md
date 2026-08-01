# 网络排障说明

核心场景：客户说“ERP 打不开”。

标准排查路径：

用户电脑 -> 网络 -> DNS/IP -> 80/443 -> Nginx -> FastAPI -> MySQL -> Redis -> 日志 -> 配置 -> 修复 -> 验证。

## 基础概念

- IP：设备在网络中的地址。
- 子网掩码：判断目标地址是否在同一网段。
- 网关：访问其他网段时经过的出口。
- DNS：把域名解析为 IP。
- TCP：面向连接的传输协议，端口可达性通常先看 TCP。
- HTTP：应用层协议，ERP 页面和接口通常通过 HTTP/HTTPS 访问。
- 端口：服务监听入口，例如 80、443、8000、3306、6379。
- `127.0.0.1`：本机回环地址。
- `0.0.0.0`：服务监听所有网卡地址。
- `localhost`：通常解析到本机。
- 内网：企业内部网络。
- 公网：互联网可访问网络。
- 防火墙：可能拦截端口访问。

## Windows 常用命令

```powershell
ipconfig
ping localhost
tracert localhost
nslookup localhost
netstat -ano
Test-NetConnection localhost -Port 8000
curl http://localhost/health
```

## Linux 常用命令

```bash
ip addr
ping localhost
traceroute localhost
dig localhost
ss -lntp
nc -vz localhost 8000
curl http://localhost/health
```

## 本项目检查脚本

```bash
python scripts/network_check.py
```

脚本检查：

- Host
- DNS resolution
- TCP port
- HTTP endpoint

示例输出：

```text
[PASS] DNS localhost -> 127.0.0.1
[PASS] TCP localhost:80
[PASS] HTTP /health
[FAIL] TCP localhost:3306
```

面试讲解重点：实施工程师不要直接说“让开发看”，应先证明用户电脑、网络、域名、端口、Nginx、应用、数据库和日志分别是什么状态。
