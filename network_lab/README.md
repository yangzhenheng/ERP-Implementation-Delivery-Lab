# 网络排障实验室

本目录用于 ERP / 软件实施工程师面试中的网络排障演示。所有案例只针对本地演示环境，不用于真实客户生产环境。

标准流程：

用户电脑 -> 网络 -> DNS/IP -> 80/443 -> Nginx -> FastAPI -> MySQL -> Redis -> 日志 -> 配置 -> 修复 -> 验证。

推荐先执行：

```bash
python scripts/network_check.py
```

案例：

- `CASE01_erp_unreachable.md`：ERP 页面打不开。
- `CASE02_port_unreachable.md`：端口不可达。
- `CASE03_dns_failure.md`：DNS 解析失败。
- `CASE04_nginx_502.md`：Nginx 502。
- `CASE05_mysql_connection.md`：MySQL 连接失败。
