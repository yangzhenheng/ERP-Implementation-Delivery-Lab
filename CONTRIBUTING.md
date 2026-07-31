# 贡献说明

本仓库主要用于个人面试展示，但仍按小型专业项目方式维护，保证每次改动可读、可测、可回溯。

## 本地检查

```bash
python -m pip install -r requirements.txt
pytest -q
```

## 开发规则

- 演示数据必须明确标记为模拟数据。
- 不提交 `.env`、数据库文件、备份文件、运行日志或个人文件。
- ERP 行为要与实施流程文档保持一致。
- 修改 API 行为时同步更新测试。
- 验证结果变化时同步更新 `EVIDENCE.md` 和 `FINAL_ACCEPTANCE_REPORT.md`。

## 提交信息

使用简洁的 conventional-style 信息：

```text
feat: add inventory validation workflow
fix: handle redis degradation quickly
docs: update go-live checklist
test: cover data import endpoint
```

面试讲解重点：即使是个人项目，也要体现版本管理、测试验证、文档同步和边界意识。
