# 更新日志

## 3.0.0 - 2026-08-01

- 增加轻量 ERP 后台页面，主演示可通过 UI 完成客户新增、订单创建、库存校验、问题工单和项目商务查看。
- 增加项目商务与回款里程碑模块，包含模拟合同金额、签约款、上线款和验收款。
- 增加 SQL Server 数据库实验室，以及 MySQL / SQL Server / Oracle / DB2 方言对比文档。
- 增加网络排障实验室和 Windows/Linux 网络检查脚本。
- 增加 V3 验证脚本、V3 运行验证记录、备份恢复证据和最终验收报告。
- 将测试扩展到 24 个用例，覆盖 health、dashboard、客户、产品、库存、订单、Issue、实施任务、商务、CSV、前端、request id、Redis fallback 和事务边界。
- 当前本机无 Docker 命令，因此 Docker/MySQL/Redis/Nginx/SQL Server/backup-restore 真实运行保持 NOT VERIFIED。

## 2.2.0 - 2026-08-01

- 将项目展示语言统一为简体中文，适配国内 ERP / 软件实施岗位面试。
- 重写面试演示主流程，覆盖打开 ERP、新增客户、创建订单、库存校验、SQL 查询、CSV 迁移、Docker 服务查看、Nginx 502 排障、日志端口检查、修复、MySQL 备份恢复、培训和上线验收。
- 优化 README、培训、上线、验收、排障、备份恢复、数据迁移等交付文档。
- 将演示页面、种子数据和问题样例替换为更贴近国内制造业场景的模拟数据。

## 2.1.0 - 2026-08-01

- 增加 GitHub Actions CI，用于运行 Python 测试和 Docker Compose 语法验证。
- 增加 `pyproject.toml` 项目元数据和 pytest 配置。
- 将 FastAPI 启动初始化改为 lifespan 方式。
- 将 UTC 时间处理改为时区感知写法。
- 增加贡献说明、安全边界和发布说明。
- 增加 Git 换行规则，覆盖 shell、Python、SQL 和 Windows 脚本。

## 2.0.0 - 2026-07-31

- 将项目升级为“制造业 ERP 实施交付实验室”。
- 增加 ERP 数据模型、驾驶舱 API、订单库存校验和问题闭环。
- 增加 CSV 数据迁移、SQL 练习脚本、Docker Compose、Nginx 和 Linux 部署脚本。
- 增加实施、排障、上线、培训、面试和验收文档。
