# Current State Audit

Audit date: 2026-07-31

## Implemented Before Upgrade

- FastAPI application with health check, dashboard, orders, inventory, implementation tasks and ticket APIs.
- SQLite demo database initialization scripts.
- Basic static dashboard page.
- Basic deployment examples for Nginx and systemd.
- Initial implementation documents.

## Issues Found

- Several Chinese strings were mojibake and not suitable for interview demonstration.
- Original data model was too small for ERP implementation discussion.
- API responses were not unified.
- MySQL, Redis, Docker Compose and Nginx reverse proxy were not integrated as a complete demo profile.
- CSV migration, backup/restore, Linux scripts and troubleshooting cases were incomplete.
- Tests covered only a small part of the intended business flow.

## Current Technology Stack

- FastAPI, Pydantic, SQLAlchemy
- SQLite for local dev demo
- MySQL 8 profile through environment variables
- Redis for optional status/cache check
- Docker Compose with app, mysql, redis and nginx
- pytest and FastAPI TestClient

## Current Database Model

Tables now include customers, products, warehouses, inventory, sales_orders, sales_order_items, inventory_transactions, implementation_tasks, issues and operation_logs.

## Current APIs

- `GET /health`
- `GET /api/dashboard`
- `GET /api/customers`
- `POST /api/customers`
- `GET /api/products`
- `GET /api/inventory`
- `GET /api/orders`
- `POST /api/orders`
- `GET /api/orders/{id}`
- `GET /api/issues`
- `POST /api/issues`
- `PUT /api/issues/{id}`
- `GET /api/implementation/tasks`
- `POST /api/data/import`
- `GET /api/system/status`

## Upgrade Scope

This project is now positioned as an independently built interview demonstration lab. ERP business data is mock data. The technical chain is real code and is tested locally with SQLite; Docker/MySQL/Nginx verification depends on the local Docker environment.
