import os
import sys
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test.db"
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.environ["APP_ENV"] = "dev"
os.environ["ERP_DB_PATH"] = str(TEST_DB)

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine, seed_demo_data
from app.main import app


def setup_function():
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)
        db.commit()


def teardown_module():
    engine.dispose()


def unwrap(response):
    assert response.status_code < 400, response.text
    body = response.json()
    assert body["code"] == 0
    return body["data"]


def test_health():
    with TestClient(app) as client:
        data = unwrap(client.get("/health"))
        assert data["status"] == "ok"


def test_dashboard_metrics():
    with TestClient(app) as client:
        data = unwrap(client.get("/api/dashboard"))
        assert data["order_count"] == 3
        assert data["low_stock_products"] == 1
        assert 0 <= data["implementation_progress"] <= 100


def test_customers_create_and_list():
    with TestClient(app) as client:
        created = unwrap(
            client.post(
                "/api/customers",
                json={
                    "customer_code": "CUST-T100",
                    "customer_name": "模拟测试客户",
                    "contact": "Tester",
                    "phone": "13900000000",
                },
            )
        )
        assert created["customer_code"] == "CUST-T100"
        customers = unwrap(client.get("/api/customers"))
        assert any(row["customer_code"] == "CUST-T100" for row in customers)


def test_products_inventory_and_orders():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        assert len(products) >= 4
        inventory = unwrap(client.get("/api/inventory"))
        assert any(row["stock_status"] == "low_stock" for row in inventory)
        orders = unwrap(client.get("/api/orders"))
        assert orders[0]["customer_name"]
        detail = unwrap(client.get(f"/api/orders/{orders[0]['order_id']}"))
        assert detail["items"]


def test_create_order_success_deducts_inventory():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-A100")
        result = unwrap(
            client.post(
                "/api/orders",
                json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 1}]},
            )
        )
        assert result["status"] == "confirmed"
        inventory = unwrap(client.get("/api/inventory"))
        sku = next(row for row in inventory if row["product_code"] == "SKU-A100")
        assert sku["quantity"] == 31


def test_create_order_shortage_generates_issue():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-B220")
        result = unwrap(
            client.post(
                "/api/orders",
                json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 999}]},
            )
        )
        assert result["status"] == "inventory_failed"
        issues = unwrap(client.get("/api/issues"))
        assert any("库存不足" in row["title"] for row in issues)


def test_issues_create_update():
    with TestClient(app) as client:
        issue = unwrap(client.post("/api/issues", json={"title": "API field mismatch", "module": "api", "severity": "P2"}))
        updated = unwrap(client.put(f"/api/issues/{issue['issue_id']}", json={"status": "closed", "solution": "Aligned field mapping"}))
        assert updated["status"] == "closed"
        assert updated["resolved_at"]


def test_dashboard_and_system_status():
    with TestClient(app) as client:
        assert "system_status" in unwrap(client.get("/api/dashboard"))
        status = unwrap(client.get("/api/system/status"))
        assert status["database"] == "ok"


def test_data_import_endpoint():
    with TestClient(app) as client:
        result = unwrap(client.post("/api/data/import"))
        assert result["failed"] == 0
        assert result["success"] >= 1
