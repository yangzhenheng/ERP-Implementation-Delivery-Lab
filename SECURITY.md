# Security Policy

This project is a local interview demonstration lab, not a production ERP system.

## Supported Use

- Local development and interview demonstration.
- Docker-based demo environment.
- Mock ERP business data only.

## Sensitive Data Rules

- Never commit `.env`.
- Never commit real customer data.
- Never commit database dumps or runtime logs.
- Use `.env.example` for configuration documentation.

## Reporting Issues

For this personal lab, record security or configuration issues in `troubleshooting/` or GitHub Issues with:

- symptom
- affected module
- reproduction steps
- root cause
- fix
- verification result

## Known Boundaries

Authentication, authorization and production-grade hardening are intentionally out of scope for the current interview lab. Do not deploy this repository as a real customer production ERP system without adding those controls.
