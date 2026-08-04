# V3.1 Linux Runtime Evidence

时间：2026-08-04 12:58:47 +08:00

## Windows / WSL 检查

| 命令 | 真实结果 | 状态 |
|---|---|---|
| `wsl --status` | 返回非 0，输出为 WSL 帮助/乱码文本，未能取得可用状态 | BLOCKED |
| `wsl -l -v` | 返回非 0，未列出已安装可运行发行版 | BLOCKED |
| `wsl --version` | 返回非 0，输出为 WSL 帮助/乱码文本 | BLOCKED |
| `wsl --list --online` | 能列出可安装发行版，如 Ubuntu、Debian、Kali、Oracle Linux、SUSE | PASS |

结论：当前 Windows 主机存在 `wsl.exe`，但没有确认到可运行的本地 Ubuntu/WSL 发行版，因此不能执行 `cat /etc/os-release`、`uname -a`、`free -h`、`df -h`、`ip addr`、`ss -lntp` 等 Linux 主机命令。

## Docker 容器 Linux 检查

| 命令 | 真实结果 | 状态 |
|---|---|---|
| `docker version` | `docker` 命令不存在 | BLOCKED |
| `docker compose ps` | 未执行，Docker CLI 不存在 | BLOCKED |
| `docker compose exec app sh -lc "cat /etc/os-release; uname -a; df -h; ps; python --version"` | 未执行，容器不可用 | BLOCKED |
| `docker compose exec nginx sh -lc "cat /etc/os-release; nginx -v; nginx -t; ps"` | 未执行，容器不可用 | BLOCKED |

## 未验证声明

未验证 systemd、journalctl、Linux 容器内 Nginx 配置检查和 Docker 容器进程状态。原因是 Docker CLI / Docker Desktop 当前不可用。
