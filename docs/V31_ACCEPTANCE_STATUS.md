# V3.1 Acceptance Status

Date: 2026-08-04

Version: 3.1.0

## Local Windows Verification

Status: LOCAL WINDOWS BLOCKED

Verified locally:

- `python -m compileall app scripts tests`: PASS
- `pytest -q`: PASS, 28 passed and 4 E2E tests skipped
- `.env` safety: PASS, `.env` is ignored and not present in git status
- `python scripts/run_v31_acceptance.py --local`: non-zero by design because Docker is unavailable

Blocked locally:

- Docker CLI is not present in PATH.
- Docker Compose, MySQL, Redis, Nginx, SQL Server, backup/restore, Nginx 502 recovery, full-stack E2E, and Linux container runtime cannot be truthfully marked PASS on this machine.
- Playwright installation from official PyPI failed with a TLS EOF error; HTTPS mirror installation returned HTTP 403. No insecure `trusted-host` workaround was used.

Local artifact output:

- `artifacts/v31/acceptance.json`
- `artifacts/v31/acceptance.log`
- `artifacts/v31/V31_ACCEPTANCE_REPORT.md`

These files are intentionally ignored by git because they are machine-local run artifacts.

## CI Verification

Status: NOT VERIFIED until GitHub Actions runs.

The workflow `.github/workflows/full-stack-acceptance.yml` adds separate jobs for:

- unit tests on Python 3.11 and 3.12
- SQLite browser E2E
- Docker Compose full-stack ERP acceptance
- SQL Server lab

CI evidence must be recorded as CI VERIFIED only after those jobs pass. CI output must not be described as LOCAL WINDOWS VERIFIED.

## Current Final Grade

Current grade: B. Suitable as a junior ERP/software implementation engineer project, but not yet upgraded to C until full-stack Docker/CI evidence passes.
