# Docker 全栈验证

本项目提供 Docker Compose 演示环境，包含 FastAPI 应用、MySQL 8、Redis 和 Nginx。面试中可用它证明自己理解 ERP 实施中的服务编排、日志查看、端口检查和反向代理验证。

## 当前电脑状态

2026-07-31 曾尝试安装 Docker Desktop：

```powershell
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements --silent
```

结果：安装包已下载并校验，但安装阶段需要管理员/UAC 权限，返回退出码 `4294967291`。因此当前仓库保留完整 Docker 配置和验证脚本，实际全栈运行需要先完成 Docker Desktop 安装。

## 安装 Docker Desktop

用管理员权限打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_docker_windows.ps1
```

安装完成后按 Docker 提示重启 Windows。

## 验证 Docker

```powershell
docker --version
docker compose version
```

## 启动服务

```powershell
docker compose up -d --build
docker compose ps
```

应看到 `app`、`mysql`、`redis`、`nginx` 等服务。

## 查看日志

```powershell
docker compose logs app
docker compose logs mysql
docker compose logs redis
docker compose logs nginx
```

## 一键全栈验证

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_full_stack.ps1
```

脚本会验证：

- Docker CLI 和 Compose 是否可用
- `docker compose up -d --build` 是否成功
- Nginx 经 `http://localhost` 转发是否正常
- FastAPI `/health` 和 `/api/dashboard` 是否正常
- MySQL 查询是否成功
- Redis `PING` 是否成功
- MySQL 备份文件是否可以生成

## 停止服务

```powershell
docker compose down
```

面试讲解重点：Docker 不是为了“看起来高级”，而是为了把应用、数据库、缓存、反向代理放到可重复启动、可检查、可排障的环境里。
