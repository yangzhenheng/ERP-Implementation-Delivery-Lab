# 5-8 Minute Demo Script

1. Open README and explain the boundary: independent implementation lab, mock ERP data, no real customer claim.
2. Show architecture: Browser -> Nginx -> FastAPI -> MySQL/SQLite + Redis.
3. Open Dashboard: show orders, today orders, low stock, open issues and implementation progress.
4. Create a customer through Swagger `POST /api/customers`.
5. Create a sales order through `POST /api/orders`.
6. Explain inventory validation: enough stock deducts inventory; insufficient stock creates an issue.
7. Open `sql/03_queries.sql` and show low stock, customer amount, JOIN and GROUP BY queries.
8. Open Swagger `/docs` and show API structure.
9. Show Linux/Docker commands: `docker compose ps`, `docker compose logs app`, `curl /health`.
10. Show logs: `logs/app.log` and request_id idea.
11. Show troubleshooting case `troubleshooting/CASE02_nginx_502.md`.
12. Show backup command from `docs/BACKUP_RESTORE.md`.
13. Show data migration guide and `python scripts/import_data.py`.
14. Show go-live checklist.
15. Close with acceptance report and evidence file.

Keep the demo honest: explain that local pytest has passed, while Docker/MySQL/Nginx verification depends on Docker availability on the machine.
