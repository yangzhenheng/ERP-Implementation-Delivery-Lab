# 项目验证证据

日期：2026-08-01

## 已在本地真实验证

- 已执行依赖安装：`python -m pip install -r requirements.txt`
- 已执行自动化测试：`pytest -q`
- 测试结果：`9 passed`
- 已执行 Python 编译检查：`python -m compileall app scripts tests`
- 已执行本地 HTTP 验证：`python scripts/verify_deployment.py --base-url http://127.0.0.1:8000`
- HTTP 验证结果：`/health`、`/api/dashboard`、`/api/customers`、`/api/system/status` 均为 `[通过]`
- 已验证 CSV 导入脚本，结果为 `success=8, failed=0, skipped=0`
- 已检查 Docker Compose YAML，确认包含 `app`、`mysql`、`redis`、`nginx` 四个服务
- 已验证 FastAPI lifespan 启动流程
- 已新增 GitHub Actions CI，用于 Python 3.11 / 3.12 自动测试

## 真实技术链路

- FastAPI 应用：真实代码
- SQLAlchemy 数据模型：真实代码
- SQLite 本地数据库：真实可运行
- MySQL 8 建表脚本：真实 SQL 脚本
- Redis：可降级状态检查配置
- Nginx：反向代理配置
- Docker Compose：完整服务编排配置
- CSV 数据导入：真实导入脚本
- Linux 部署脚本：真实 Shell 脚本
- 自动化测试：真实 pytest 测试

## 模拟数据边界

- ERP 业务数据：模拟数据
- 商业客户：无
- 真实生产上线：无
- 培训、验收、上线文档：面试演示文档

## 当前未验证项

- Docker Compose 全栈运行
- MySQL 容器初始化
- Redis 容器健康检查
- Nginx 通过 `http://localhost` 反向代理访问
- MySQL 备份恢复脚本连接真实 MySQL 服务执行

原因：当前电脑未安装可用 Docker Desktop。已尝试通过 winget 安装 Docker Desktop，安装器下载和哈希校验成功，但安装阶段需要管理员/UAC 权限，退出码为 `4294967291`。因此报告中保持 `NOT VERIFIED`，不伪造容器运行结果。
