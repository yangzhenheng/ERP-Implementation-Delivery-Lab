import os
import sys
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test.db"
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.environ["APP_ENV"] = "dev"
os.environ["ERP_DB_PATH"] = str(TEST_DB)

from fastapi.testclient import TestClient

import app.db as db_module
import app.main as main_module
from app.db import Base, SalesOrder, SessionLocal, engine, seed_demo_data
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
        assert data["database"] == "sqlite"


def test_mysql_url_preserves_special_character_password(monkeypatch):
    password = "A@b:c/d?e#f%2026"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv("DB_USER", "erp_user")
    monkeypatch.setenv("DB_PASSWORD", password)
    monkeypatch.setenv("DB_HOST", "mysql")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_NAME", "erp_demo")

    url = db_module._database_url()

    assert url.drivername == "mysql+pymysql"
    assert url.username == "erp_user"
    assert url.password == password
    assert url.host == "mysql"
    assert url.database == "erp_demo"
    assert url.query["charset"] == "utf8mb4"


def test_explicit_database_url_remains_compatible(monkeypatch):
    explicit_url = "sqlite:///explicit-test.db"
    monkeypatch.setenv("DATABASE_URL", explicit_url)

    assert db_module._database_url() == explicit_url


def test_dashboard_metrics():
    with TestClient(app) as client:
        data = unwrap(client.get("/api/dashboard"))
        assert data["order_count"] == 3
        assert data["low_stock_products"] == 1
        assert 0 <= data["implementation_progress"] <= 100


def test_customers_list():
    with TestClient(app) as client:
        customers = unwrap(client.get("/api/customers"))
        assert len(customers) >= 3
        assert customers[0]["customer_code"] == "CUST-001"


def test_customer_create():
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


def test_duplicate_customer():
    with TestClient(app) as client:
        response = client.post("/api/customers", json={"customer_code": "CUST-001", "customer_name": "重复客户"})
        assert response.status_code == 409
        assert response.json()["code"] == 1


def test_products():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        assert len(products) >= 4
        assert any(row["product_code"] == "SKU-A100" for row in products)


def test_inventory():
    with TestClient(app) as client:
        inventory = unwrap(client.get("/api/inventory"))
        assert any(row["stock_status"] == "low_stock" for row in inventory)


def test_order_confirmed():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-A100")
        result = unwrap(client.post("/api/orders", json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 1}]}))
        assert result["status"] == "confirmed"


def test_generated_order_numbers_are_unique_for_rapid_requests():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-A100")
        payload = {"customer_id": 1, "items": [{"product_id": product_id, "quantity": 1}]}
        first = unwrap(client.post("/api/orders", json=payload))
        second = unwrap(client.post("/api/orders", json=payload))
        assert first["order_no"] != second["order_no"]


def test_order_confirmed_deducts_inventory():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-A100")
        unwrap(client.post("/api/orders", json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 1}]}))
        inventory = unwrap(client.get("/api/inventory"))
        sku = next(row for row in inventory if row["product_code"] == "SKU-A100")
        assert sku["quantity"] == 31


def test_order_insufficient_stock():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-B220")
        result = unwrap(client.post("/api/orders", json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 999}]}))
        assert result["status"] == "inventory_failed"
        assert result["insufficient"]


def test_issue_creation_from_shortage():
    with TestClient(app) as client:
        products = unwrap(client.get("/api/products"))
        product_id = next(row["product_id"] for row in products if row["product_code"] == "SKU-B220")
        unwrap(client.post("/api/orders", json={"customer_id": 1, "items": [{"product_id": product_id, "quantity": 999}]}))
        issues = unwrap(client.get("/api/issues"))
        assert any("库存不足" in row["title"] for row in issues)


def test_issue_update():
    with TestClient(app) as client:
        issue = unwrap(client.post("/api/issues", json={"title": "接口字段映射异常", "module": "接口", "severity": "P2"}))
        updated = unwrap(
            client.put(
                f"/api/issues/{issue['issue_id']}",
                json={"status": "resolved", "root_cause": "字段名不一致", "solution": "统一映射", "verification_result": "复测通过"},
            )
        )
        assert updated["status"] == "resolved"
        assert updated["verification_result"] == "复测通过"


def test_implementation_tasks():
    with TestClient(app) as client:
        tasks = unwrap(client.get("/api/implementation/tasks"))
        assert len(tasks) == 8
        assert any(row["task_type"] == "go_live" for row in tasks)
        summary = unwrap(client.get("/api/implementation"))
        assert summary["total_tasks"] == 8


def test_commercial_summary():
    with TestClient(app) as client:
        summary = unwrap(client.get("/api/commercial/summary"))
        assert summary["contract_amount"] == 100000.0
        assert summary["paid_amount"] == 30000.0
        assert "Mock commercial data" in summary["mock_notice"]
        overview = unwrap(client.get("/api/commercial"))
        assert len(overview["milestones"]) == 3


def test_payment_milestones():
    with TestClient(app) as client:
        milestones = unwrap(client.get("/api/payment-milestones"))
        assert [row["milestone_name"] for row in milestones] == ["签约款", "上线款", "验收款"]


def test_projects_detail():
    with TestClient(app) as client:
        projects = unwrap(client.get("/api/projects"))
        detail = unwrap(client.get(f"/api/projects/{projects[0]['project_id']}"))
        assert detail["project_code"] == "ERP-DEMO-2026-001"
        assert len(detail["milestones"]) == 3


def test_system_status():
    with TestClient(app) as client:
        status = unwrap(client.get("/api/system/status"))
        assert status["database"] == "ok"
        assert status["redis"] in {"ok", "unavailable_degraded"}


def test_csv_import():
    with TestClient(app) as client:
        result = unwrap(client.post("/api/data/import"))
        assert result["failed"] == 0
        assert result["success"] >= 1


def test_invalid_order():
    with TestClient(app) as client:
        response = client.post("/api/orders", json={"customer_id": 99999, "items": [{"product_id": 1, "quantity": 1}]})
        assert response.status_code == 404
        assert "customer not found" in response.text


def test_request_id():
    with TestClient(app) as client:
        response = client.get("/health", headers={"x-request-id": "REQ-V3-001"})
        assert response.headers["x-request-id"] == "REQ-V3-001"


def test_redis_fallback_dashboard():
    with TestClient(app) as client:
        data = unwrap(client.get("/api/dashboard"))
        assert data["system_status"] in {"ok", "degraded_without_redis"}


def test_core_apis_continue_when_redis_is_unavailable(monkeypatch):
    monkeypatch.setattr(main_module, "redis_available", lambda: False)
    with TestClient(app) as client:
        dashboard = unwrap(client.get("/api/dashboard"))
        assert dashboard["system_status"] == "degraded_without_redis"
        assert client.get("/api/customers").status_code == 200
        assert client.get("/api/orders").status_code == 200
        status = unwrap(client.get("/api/system/status"))
        assert status["redis"] == "unavailable_degraded"


def test_system_status_reports_redis_recovery(monkeypatch):
    monkeypatch.setattr(main_module, "redis_available", lambda: True)
    with TestClient(app) as client:
        status = unwrap(client.get("/api/system/status"))
        assert status["redis"] == "ok"


def test_database_transaction_on_invalid_product():
    with SessionLocal() as db:
        before = db.query(SalesOrder).count()
    with TestClient(app) as client:
        response = client.post("/api/orders", json={"customer_id": 1, "items": [{"product_id": 99999, "quantity": 1}]})
        assert response.status_code == 404
    with SessionLocal() as db:
        after = db.query(SalesOrder).count()
    assert after == before


def test_frontend_customers():
    with TestClient(app) as client:
        response = client.get("/customers")
        assert response.status_code == 200
        assert "客户管理" in response.text
        assert "新增客户" in response.text


def test_frontend_orders():
    with TestClient(app) as client:
        response = client.get("/orders")
        assert response.status_code == 200
        assert "销售订单" in response.text
        assert "新增销售订单" in response.text
