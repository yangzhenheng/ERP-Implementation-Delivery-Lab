import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.getenv("RUN_E2E") != "1", reason="Set RUN_E2E=1 to run browser smoke tests.")

ROOT_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def live_server():
    env = os.environ.copy()
    env["APP_ENV"] = "dev"
    env["ERP_DB_PATH"] = str(ROOT_DIR / "data" / "e2e_test.db")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8010"],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(5)
    yield "http://127.0.0.1:8010"
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def page_context():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_customer_management_smoke(live_server, page_context):
    page = page_context
    code = f"E2E-CUST-{int(time.time())}"
    page.goto(f"{live_server}/customers")
    page.get_by_label("客户编码").fill(code)
    page.get_by_label("客户名称").fill("浏览器E2E客户（模拟）")
    page.get_by_label("联系人").fill("E2E")
    page.get_by_label("电话").fill("13800008888")
    page.get_by_label("地址").fill("本地浏览器测试")
    page.get_by_role("button", name="保存客户").click()
    page.wait_for_timeout(900)
    assert code in page.content()


def test_sales_order_smoke(live_server, page_context):
    page = page_context
    page.goto(f"{live_server}/orders")
    page.get_by_label("数量").fill("1")
    page.get_by_role("button", name="创建订单").click()
    page.wait_for_timeout(900)
    content = page.content()
    assert "订单已创建并确认" in content or "库存不足，已生成问题工单" in content


def test_commercial_smoke(live_server, page_context):
    page = page_context
    page.goto(f"{live_server}/commercial")
    content = page.content()
    assert "100,000.00" in content
    assert "签约款" in content
    assert "上线款" in content
    assert "验收款" in content


def test_navigation_smoke(live_server, page_context):
    page = page_context
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    for path in ["/dashboard", "/customers", "/products", "/inventory", "/orders", "/issues", "/implementation", "/commercial", "/system"]:
        page.goto(f"{live_server}{path}")
        assert "制造业 ERP" in page.content()
    assert not errors
