import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(os.getenv("RUN_E2E") != "1", reason="Set RUN_E2E=1 to run browser E2E tests.")

ROOT_DIR = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT_DIR / "artifacts" / "e2e"
SQLITE_DB = ROOT_DIR / "data" / "e2e_test.db"
NAVIGATION_PATHS = ["/dashboard", "/customers", "/products", "/inventory", "/orders", "/issues", "/implementation", "/commercial", "/system"]


def api_get(base_url: str, path: str):
    with urllib.request.urlopen(f"{base_url}{path}", timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    assert payload["code"] == 0
    return payload["data"]


def wait_for_health(base_url: str, timeout: int = 45) -> None:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        try:
            data = api_get(base_url, "/health")
            if data["status"] == "ok":
                return
        except Exception as exc:
            last_error = str(exc)
        time.sleep(1)
    raise AssertionError(f"Timed out waiting for {base_url}/health: {last_error}")


@pytest.fixture(scope="session")
def live_server():
    base_url = os.getenv("E2E_BASE_URL")
    if base_url:
        wait_for_health(base_url, timeout=90)
        yield base_url.rstrip("/")
        return

    if SQLITE_DB.exists():
        SQLITE_DB.unlink()
    env = os.environ.copy()
    env["APP_ENV"] = "dev"
    env["ERP_DB_PATH"] = str(SQLITE_DB)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8010"],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_health("http://127.0.0.1:8010")
        yield "http://127.0.0.1:8010"
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def page_context():
    playwright = pytest.importorskip("playwright.sync_api")
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors: list[str] = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        yield page, errors
        browser.close()


def is_full_stack_mode() -> bool:
    return bool(os.getenv("E2E_BASE_URL"))


def customer_count_in_database(code: str) -> int:
    if is_full_stack_mode():
        pymysql = pytest.importorskip("pymysql")
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("DB_USER", "erp_user"),
            password=os.getenv("DB_PASSWORD", "erp_password_change_me"),
            database=os.getenv("DB_NAME", "erp_demo"),
            charset="utf8mb4",
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_code=%s", (code,))
                return int(cursor.fetchone()[0])
        finally:
            connection.close()

    with sqlite3.connect(SQLITE_DB) as connection:
        cursor = connection.execute("SELECT COUNT(*) FROM customers WHERE customer_code=?", (code,))
        return int(cursor.fetchone()[0])


def test_customer_page_creates_customer_and_persists_to_database(live_server, page_context):
    page, _ = page_context
    code = f"E2E-CUST-{int(time.time())}"
    page.goto(f"{live_server}/customers")
    page.locator('input[name="customer_code"]').fill(code)
    page.locator('input[name="customer_name"]').fill("Browser E2E Customer")
    page.locator('input[name="contact"]').fill("E2E")
    page.locator('input[name="phone"]').fill("13800008888")
    page.locator('input[name="address"]').fill("Browser validation")
    page.locator("#customer-form button").click()
    page.locator(".notice.good").wait_for(timeout=5000)
    page.wait_for_function("code => document.body.innerText.includes(code)", arg=code, timeout=8000)

    assert customer_count_in_database(code) == 1
    page.screenshot(path=ARTIFACT_DIR / "customers.png", full_page=True)


def test_order_page_handles_confirmed_and_insufficient_orders(live_server, page_context):
    page, _ = page_context
    customers = api_get(live_server, "/api/customers")
    products = api_get(live_server, "/api/products")
    inventory_before = api_get(live_server, "/api/inventory")
    issues_before = api_get(live_server, "/api/issues")

    customer_id = customers[0]["customer_id"]
    normal_product = next(row for row in products if row["product_code"] == "SKU-A100")
    shortage_product = next(row for row in products if row["product_code"] == "SKU-B220")
    normal_before = next(row for row in inventory_before if row["product_code"] == "SKU-A100")["quantity"]

    page.goto(f"{live_server}/orders")
    page.locator('select[name="customer_id"]').select_option(str(customer_id))
    page.locator('select[name="product_id"]').select_option(str(normal_product["product_id"]))
    page.locator('input[name="quantity"]').fill("1")
    page.locator("#order-form button").click()
    page.locator(".notice.good").wait_for(timeout=5000)

    inventory_after = api_get(live_server, "/api/inventory")
    normal_after = next(row for row in inventory_after if row["product_code"] == "SKU-A100")["quantity"]
    assert normal_after == normal_before - 1
    newest_order = api_get(live_server, "/api/orders")[0]
    assert newest_order["status"] == "confirmed"

    page.goto(f"{live_server}/orders")
    page.locator('select[name="customer_id"]').select_option(str(customer_id))
    page.locator('select[name="product_id"]').select_option(str(shortage_product["product_id"]))
    page.locator('input[name="quantity"]').fill("999")
    page.locator("#order-form button").click()
    page.locator(".notice.bad").wait_for(timeout=5000)

    newest_order = api_get(live_server, "/api/orders")[0]
    issues_after = api_get(live_server, "/api/issues")
    assert newest_order["status"] == "inventory_failed"
    assert len(issues_after) >= len(issues_before) + 1
    page.screenshot(path=ARTIFACT_DIR / "orders.png", full_page=True)


def test_commercial_page_shows_contract_and_milestones(live_server, page_context):
    page, _ = page_context
    page.goto(f"{live_server}/commercial")
    page.wait_for_selector(".milestone", timeout=5000)
    content = page.content()
    assert "100,000.00" in content
    assert len(page.locator(".milestone").all()) == 3
    page.screenshot(path=ARTIFACT_DIR / "commercial.png", full_page=True)


def test_all_navigation_pages_open_and_capture_evidence(live_server, page_context):
    page, errors = page_context
    for path in NAVIGATION_PATHS:
        page.goto(f"{live_server}{path}")
        page.wait_for_selector("#app .section, #app .grid", timeout=7000)
        page.screenshot(path=ARTIFACT_DIR / f"{path.strip('/')}.png", full_page=True)
    assert not errors
