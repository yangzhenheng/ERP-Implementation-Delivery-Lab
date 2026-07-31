# Go-Live Checklist

## Before Go-Live

- Confirm server, CPU, memory, disk and network.
- Confirm `.env` database, Redis and application settings.
- Confirm MySQL backup can be created and restored.
- Import master data and opening inventory.
- Reconcile source and target counts.
- Complete key API and business tests.
- Confirm training and support contact.

## During Go-Live

- Freeze business data changes.
- Run final backup.
- Run final migration import.
- Start MySQL, Redis, FastAPI and Nginx.
- Check `/health`, `/api/dashboard` and Swagger.
- Verify customer, product, inventory and order business flow.

## After Go-Live

- Monitor logs and service status.
- Collect user feedback.
- Record issues and owners.
- Close blocking issues.
- Prepare acceptance checklist.

## Interview Answer

For ERP go-live, I first confirm the environment and backup, then migrate and reconcile data, start services, verify APIs and core business flow, support users during the first operations, and finally record issues and complete acceptance.
