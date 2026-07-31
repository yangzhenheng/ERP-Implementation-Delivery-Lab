# Contributing

This repository is primarily an interview demonstration lab, but it follows a small professional workflow so changes remain reviewable.

## Local Setup

```bash
python -m pip install -r requirements.txt
pytest -q
```

## Development Rules

- Keep demo data clearly marked as mock data.
- Do not commit `.env`, database files, dumps, runtime logs or personal files.
- Keep ERP behavior aligned with the documented implementation workflow.
- Update tests when changing API behavior.
- Update `EVIDENCE.md` and `FINAL_ACCEPTANCE_REPORT.md` when verification results change.

## Commit Style

Use concise conventional-style messages:

```text
feat: add inventory validation workflow
fix: handle redis degradation quickly
docs: update go-live checklist
test: cover data import endpoint
```
