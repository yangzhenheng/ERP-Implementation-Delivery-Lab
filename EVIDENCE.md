# Evidence

Date: 2026-08-01

## Verified Locally

- Python dependencies installed with `python -m pip install -r requirements.txt`.
- Automated API tests executed with `pytest -q`.
- Result: `9 passed`.
- CSV import verified with isolated SQLite database.
- Import result: `{'success': 8, 'failed': 0, 'skipped': 0, 'errors': []}`.
- Local HTTP verification executed with `python scripts/verify_deployment.py --base-url http://127.0.0.1:8000`.
- HTTP result: health, dashboard, customers and system status all `[PASS]`.
- Python compile check passed with `python -m compileall app scripts tests`.
- Docker Compose YAML parsed successfully with services: app, mysql, nginx, redis.
- FastAPI lifespan startup verified through local HTTP checks.
- GitHub Actions CI workflow added for Python 3.11 and 3.12 test runs.
- Project governance files added: `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`, `.gitattributes`, `pyproject.toml`.
- Docker Desktop installation was attempted through winget. The installer downloaded and hash verification succeeded, then failed because Administrator/UAC permission was required. Exit code: `4294967291`.

## Real Technical Chain

- FastAPI application: real code.
- SQLAlchemy models: real code.
- SQLite dev database: real local database.
- API validation and error handling: real code.
- CSV import script: real code.
- SQL scripts: real MySQL syntax artifacts.
- Docker Compose, Nginx, MySQL and Redis configuration: real configuration files.
- Linux scripts: real shell scripts for demo Linux environment.

## Mock / Demo Boundary

- ERP business data: mock data.
- Commercial customer: none.
- Production go-live: none.
- User training and acceptance documents: demo documents for interview explanation.

## Not Yet Verified In This Environment

- Docker Compose full stack.
- MySQL container initialization.
- Redis container health.
- Nginx reverse proxy from `http://localhost`.
- MySQL backup/restore against a running MySQL service.

Reason: `docker` command is not available on this machine. Docker Desktop installation requires Administrator/UAC permission. Compose syntax was checked, but containers were not started.
