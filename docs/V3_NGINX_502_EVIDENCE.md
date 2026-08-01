# V3 Nginx 502 故障恢复证据

时间：2026-08-01 16:02:27 +08:00

## 已补齐脚本

- `scripts/fault_lab/create_nginx_502.ps1`
- `scripts/fault_lab/verify_nginx_502.ps1`
- `scripts/fault_lab/fix_nginx_502.ps1`

## 本次真实状态

| 项目 | 真实结果 | 状态 |
|---|---|---|
| Docker CLI | `docker` 命令不存在 | BLOCKED |
| Nginx 容器 | 未启动，依赖 Docker Desktop | BLOCKED |
| 故障注入 | 未执行，Docker 不可用 | BLOCKED |
| `curl.exe -i http://localhost/health` 返回 502 | 未执行，Nginx 不可用 | BLOCKED |
| Nginx 日志摘要 | 未获取，Nginx 不可用 | BLOCKED |
| FastAPI 直连 200 | 未在故障场景执行 | BLOCKED |
| 修复恢复 HTTP 200 | 未执行，Docker 不可用 | BLOCKED |

## 设计的安全流程

1. 备份 `deploy/nginx/erp.conf`。
2. 临时把 `proxy_pass http://app:8000;` 改为 `proxy_pass http://app:8999;`。
3. 重启 Nginx。
4. 验证 Nginx 入口返回 502。
5. 验证 FastAPI 直连 `http://localhost:8000/health` 仍为 200。
6. 恢复原配置。
7. 重启 Nginx。
8. 验证 `http://localhost/health` 恢复 200。
9. 确认 `git diff -- deploy/nginx/erp.conf` 没有遗留错误配置。

结论：故障恢复脚本已准备好，但当前环境不能真实验证 Nginx 502 注入与恢复，因此状态为 `BLOCKED`。
