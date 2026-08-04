import logging
import os
import socket
import uuid
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .db import (
    Customer,
    ImplementationTask,
    ImplementationProject,
    Inventory,
    InventoryTransaction,
    Issue,
    OperationLog,
    PaymentMilestone,
    Product,
    SalesOrder,
    SalesOrderItem,
    Warehouse,
    database_backend,
    get_session,
    init_db,
    now_utc,
)

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


class RequestLogDefaults(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "module"):
            record.module = "system"
        return True


logging.basicConfig(
    filename=LOG_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s request_id=%(request_id)s module=%(module)s %(message)s",
)
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestLogDefaults())
logger = logging.getLogger("erp_lab")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="制造业 ERP 实施交付实验室 V3.1",
    version="3.1.0",
    description="面向国内 ERP / 软件实施工程师面试的个人实施交付演示项目。业务数据均为模拟数据，不代表真实客户生产环境。",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


def api_ok(data=None, message: str = "success", status_code: int = 200):
    return JSONResponse(status_code=status_code, content={"code": 0, "message": message, "data": jsonable_encoder(data if data is not None else {})})


def api_error(message: str, status_code: int, code: int = 1):
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": {}})


def row_decimal(value) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return value


class CustomerCreate(BaseModel):
    customer_code: str = Field(min_length=2, max_length=32)
    customer_name: str = Field(min_length=2, max_length=128)
    contact: str | None = None
    phone: str | None = None
    address: str | None = None
    status: str = "active"


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    module: str = Field(min_length=2, max_length=64)
    severity: str = Field(default="P2", pattern="^(P1|P2|P3|P4)$")
    description: str | None = None
    owner: str = "implementation_engineer"


class IssueUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(open|investigating|resolved|closed)$")
    root_cause: str | None = None
    solution: str | None = None
    verification_result: str | None = None
    owner: str | None = None


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal | None = None


class SalesOrderCreate(BaseModel):
    order_no: str | None = Field(default=None, max_length=32)
    customer_id: int
    delivery_date: date | None = None
    items: list[OrderItemCreate] = Field(min_length=1)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
    except Exception as exc:
        logger.exception("Unhandled request error", extra={"request_id": request_id, "module": "api"})
        raise exc


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return api_error(str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return api_error("validation error: " + str(exc.errors()[0]["msg"]), 422)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return (BASE_DIR / "app" / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/customers", response_class=HTMLResponse)
@app.get("/products", response_class=HTMLResponse)
@app.get("/inventory", response_class=HTMLResponse)
@app.get("/orders", response_class=HTMLResponse)
@app.get("/issues", response_class=HTMLResponse)
@app.get("/implementation", response_class=HTMLResponse)
@app.get("/commercial", response_class=HTMLResponse)
@app.get("/system", response_class=HTMLResponse)
def erp_page():
    return (BASE_DIR / "app" / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health(db: Session = Depends(get_session)):
    db.execute(select(1)).scalar_one()
    return api_ok(
        {
            "status": "ok",
            "service": "制造业 ERP 实施交付实验室",
            "app_env": os.getenv("APP_ENV", "dev"),
            "database": database_backend(),
        }
    )


@app.get("/api/dashboard")
def api_dashboard(db: Session = Depends(get_session)):
    total_orders = db.scalar(select(func.count(SalesOrder.order_id))) or 0
    today_orders = db.scalar(select(func.count(SalesOrder.order_id)).where(SalesOrder.order_date == date.today())) or 0
    total_amount = db.scalar(select(func.coalesce(func.sum(SalesOrder.total_amount), 0))) or Decimal("0")
    low_stock = (
        db.query(Inventory)
        .filter(Inventory.quantity < Inventory.safety_stock)
        .count()
    )
    open_issues = db.scalar(select(func.count(Issue.issue_id)).where(Issue.status != "closed")) or 0
    task_total = db.scalar(select(func.count(ImplementationTask.task_id))) or 0
    task_done = db.scalar(select(func.count(ImplementationTask.task_id)).where(ImplementationTask.status == "completed")) or 0
    progress = round(task_done / task_total * 100) if task_total else 0
    return api_ok(
        {
            "order_count": total_orders,
            "today_orders": today_orders,
            "order_amount": row_decimal(total_amount),
            "low_stock_products": low_stock,
            "open_issues": open_issues,
            "implementation_progress": progress,
            "system_status": "degraded_without_redis" if not redis_available() else "ok",
        }
    )


@app.get("/api/customers")
def list_customers(db: Session = Depends(get_session)):
    rows = db.scalars(select(Customer).order_by(Customer.customer_id)).all()
    return api_ok(rows)


@app.post("/api/customers")
def create_customer(payload: CustomerCreate, request: Request, db: Session = Depends(get_session)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.flush()
        write_log(db, "demo_user", "create", "customers", "success", request.state.request_id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="customer_code already exists")
    return api_ok(customer, status_code=201)


@app.get("/api/products")
def list_products(db: Session = Depends(get_session)):
    rows = db.scalars(select(Product).order_by(Product.product_id)).all()
    return api_ok(rows)


@app.get("/api/inventory")
def list_inventory(db: Session = Depends(get_session)):
    rows = (
        db.query(Inventory, Product, Warehouse)
        .join(Product, Product.product_id == Inventory.product_id)
        .join(Warehouse, Warehouse.warehouse_id == Inventory.warehouse_id)
        .order_by(Product.product_code)
        .all()
    )
    data = [
        {
            "product_id": inv.product_id,
            "product_code": product.product_code,
            "product_name": product.product_name,
            "warehouse_code": warehouse.warehouse_code,
            "warehouse_name": warehouse.warehouse_name,
            "quantity": inv.quantity,
            "safety_stock": inv.safety_stock,
            "stock_status": "low_stock" if inv.quantity < inv.safety_stock else "normal",
            "updated_at": inv.updated_at,
        }
        for inv, product, warehouse in rows
    ]
    return api_ok(data)


@app.get("/api/orders")
def list_orders(status: str | None = None, db: Session = Depends(get_session)):
    query = db.query(SalesOrder, Customer).join(Customer, Customer.customer_id == SalesOrder.customer_id)
    if status:
        query = query.filter(SalesOrder.status == status)
    rows = query.order_by(SalesOrder.order_id.desc()).all()
    data = [
        {
            "order_id": order.order_id,
            "order_no": order.order_no,
            "customer_id": order.customer_id,
            "customer_name": customer.customer_name,
            "order_date": order.order_date,
            "delivery_date": order.delivery_date,
            "status": order.status,
            "total_amount": row_decimal(order.total_amount),
        }
        for order, customer in rows
    ]
    return api_ok(data)


@app.get("/api/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_session)):
    order = db.get(SalesOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return api_ok(
        {
            "order_id": order.order_id,
            "order_no": order.order_no,
            "customer": order.customer,
            "status": order.status,
            "total_amount": row_decimal(order.total_amount),
            "items": [
                {
                    "order_item_id": item.order_item_id,
                    "product_id": item.product_id,
                    "product_code": item.product.product_code,
                    "product_name": item.product.product_name,
                    "quantity": item.quantity,
                    "unit_price": row_decimal(item.unit_price),
                    "amount": row_decimal(item.amount),
                }
                for item in order.items
            ],
        }
    )


@app.post("/api/orders")
def create_order(payload: SalesOrderCreate, request: Request, db: Session = Depends(get_session)):
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    order_no = payload.order_no or f"SO{now_utc().strftime('%Y%m%d%H%M%S%f')}"
    if db.scalar(select(SalesOrder).where(SalesOrder.order_no == order_no)):
        raise HTTPException(status_code=409, detail="order_no already exists")

    total = Decimal("0")
    item_rows = []
    insufficient = []
    main_warehouse = db.scalar(select(Warehouse).order_by(Warehouse.warehouse_id))
    if not main_warehouse:
        raise HTTPException(status_code=500, detail="warehouse master data missing")

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"product {item.product_id} not found")
        unit_price = item.unit_price or product.standard_price
        amount = unit_price * item.quantity
        total += amount
        inv = db.scalar(
            select(Inventory).where(
                Inventory.product_id == product.product_id,
                Inventory.warehouse_id == main_warehouse.warehouse_id,
            )
        )
        available = inv.quantity if inv else 0
        if available < item.quantity:
            insufficient.append({"product_code": product.product_code, "required": item.quantity, "available": available})
        item_rows.append((product, item.quantity, unit_price, amount, inv))

    order = SalesOrder(
        order_no=order_no,
        customer_id=payload.customer_id,
        order_date=date.today(),
        delivery_date=payload.delivery_date,
        status="inventory_failed" if insufficient else "confirmed",
        total_amount=total,
    )
    db.add(order)
    db.flush()

    for product, qty, unit_price, amount, inv in item_rows:
        db.add(SalesOrderItem(order_id=order.order_id, product_id=product.product_id, quantity=qty, unit_price=unit_price, amount=amount))
        if not insufficient and inv:
            inv.quantity -= qty
            db.add(InventoryTransaction(product_id=product.product_id, warehouse_id=main_warehouse.warehouse_id, transaction_type="order_deduction", quantity=-qty, reference_no=order.order_no))

    if insufficient:
        db.add(
            Issue(
                title=f"订单 {order.order_no} 库存不足",
                module="库存管理",
                severity="P2",
                status="open",
                description=f"库存校验未通过：{insufficient}",
                owner="implementation_engineer",
            )
        )

    write_log(db, "demo_user", "create", "orders", "success", request.state.request_id)
    db.commit()
    return api_ok({"order_id": order.order_id, "order_no": order.order_no, "status": order.status, "insufficient": insufficient}, status_code=201)


@app.get("/api/issues")
def list_issues(db: Session = Depends(get_session)):
    rows = db.scalars(select(Issue).order_by(Issue.issue_id.desc())).all()
    return api_ok(rows)


@app.post("/api/issues")
def create_issue(payload: IssueCreate, request: Request, db: Session = Depends(get_session)):
    issue = Issue(**payload.model_dump(), status="open")
    db.add(issue)
    db.flush()
    write_log(db, payload.owner, "create", "issues", "success", request.state.request_id)
    db.commit()
    return api_ok(issue, status_code=201)


@app.put("/api/issues/{issue_id}")
def update_issue(issue_id: int, payload: IssueUpdate, request: Request, db: Session = Depends(get_session)):
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="issue not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)
    if issue.status == "closed" and issue.resolved_at is None:
        issue.resolved_at = now_utc()
    write_log(db, payload.owner or issue.owner, "update", "issues", "success", request.state.request_id)
    db.commit()
    return api_ok(issue)


@app.get("/api/implementation/tasks")
def list_implementation_tasks(db: Session = Depends(get_session)):
    rows = db.scalars(select(ImplementationTask).order_by(ImplementationTask.task_id)).all()
    return api_ok(rows)


@app.get("/api/implementation")
def implementation_summary(db: Session = Depends(get_session)):
    rows = db.scalars(select(ImplementationTask).order_by(ImplementationTask.task_id)).all()
    total = len(rows)
    completed = len([row for row in rows if row.status == "completed"])
    return api_ok({"total_tasks": total, "completed_tasks": completed, "tasks": rows})


@app.get("/api/projects")
def list_projects(db: Session = Depends(get_session)):
    rows = db.query(ImplementationProject, Customer).join(Customer, Customer.customer_id == ImplementationProject.customer_id).order_by(ImplementationProject.project_id).all()
    return api_ok(
        [
            {
                "project_id": project.project_id,
                "project_code": project.project_code,
                "project_name": project.project_name,
                "customer_id": project.customer_id,
                "customer_name": customer.customer_name,
                "contract_amount": row_decimal(project.contract_amount),
                "project_status": project.project_status,
                "start_date": project.start_date,
                "planned_go_live": project.planned_go_live,
                "actual_go_live": project.actual_go_live,
                "created_at": project.created_at,
            }
            for project, customer in rows
        ]
    )


@app.get("/api/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_session)):
    project = db.get(ImplementationProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return api_ok(
        {
            "project_id": project.project_id,
            "project_code": project.project_code,
            "project_name": project.project_name,
            "customer": project.customer,
            "contract_amount": row_decimal(project.contract_amount),
            "project_status": project.project_status,
            "start_date": project.start_date,
            "planned_go_live": project.planned_go_live,
            "actual_go_live": project.actual_go_live,
            "milestones": [
                {
                    "milestone_id": item.milestone_id,
                    "milestone_name": item.milestone_name,
                    "percentage": item.percentage,
                    "planned_amount": row_decimal(item.planned_amount),
                    "status": item.status,
                    "due_date": item.due_date,
                    "paid_date": item.paid_date,
                }
                for item in project.milestones
            ],
        }
    )


@app.get("/api/payment-milestones")
def list_payment_milestones(db: Session = Depends(get_session)):
    rows = db.query(PaymentMilestone, ImplementationProject).join(ImplementationProject, ImplementationProject.project_id == PaymentMilestone.project_id).order_by(PaymentMilestone.milestone_id).all()
    return api_ok(
        [
            {
                "milestone_id": milestone.milestone_id,
                "project_id": milestone.project_id,
                "project_code": project.project_code,
                "project_name": project.project_name,
                "milestone_name": milestone.milestone_name,
                "percentage": milestone.percentage,
                "planned_amount": row_decimal(milestone.planned_amount),
                "status": milestone.status,
                "due_date": milestone.due_date,
                "paid_date": milestone.paid_date,
            }
            for milestone, project in rows
        ]
    )


@app.get("/api/commercial/summary")
def commercial_summary(db: Session = Depends(get_session)):
    total_contract = db.scalar(select(func.coalesce(func.sum(ImplementationProject.contract_amount), 0))) or Decimal("0")
    paid_amount = db.scalar(select(func.coalesce(func.sum(PaymentMilestone.planned_amount), 0)).where(PaymentMilestone.status == "paid")) or Decimal("0")
    invoiced_amount = db.scalar(select(func.coalesce(func.sum(PaymentMilestone.planned_amount), 0)).where(PaymentMilestone.status == "invoiced")) or Decimal("0")
    overdue_amount = (
        db.scalar(
            select(func.coalesce(func.sum(PaymentMilestone.planned_amount), 0)).where(
                PaymentMilestone.status.in_(["pending", "invoiced"]),
                PaymentMilestone.due_date < date.today(),
            )
        )
        or Decimal("0")
    )
    return api_ok(
        {
            "mock_notice": "Mock commercial data only. 不接入真实支付。",
            "contract_amount": row_decimal(total_contract),
            "paid_amount": row_decimal(paid_amount),
            "pending_amount": row_decimal(total_contract - paid_amount),
            "invoiced_amount": row_decimal(invoiced_amount),
            "overdue_amount": row_decimal(overdue_amount),
        }
    )


@app.get("/api/commercial")
def commercial_overview(db: Session = Depends(get_session)):
    total_contract = db.scalar(select(func.coalesce(func.sum(ImplementationProject.contract_amount), 0))) or Decimal("0")
    paid_amount = db.scalar(select(func.coalesce(func.sum(PaymentMilestone.planned_amount), 0)).where(PaymentMilestone.status == "paid")) or Decimal("0")
    overdue_amount = (
        db.scalar(
            select(func.coalesce(func.sum(PaymentMilestone.planned_amount), 0)).where(
                PaymentMilestone.status.in_(["pending", "invoiced"]),
                PaymentMilestone.due_date < date.today(),
            )
        )
        or Decimal("0")
    )
    milestones = db.scalars(select(PaymentMilestone).order_by(PaymentMilestone.milestone_id)).all()
    return api_ok(
        {
            "summary": {
                "contract_amount": row_decimal(total_contract),
                "paid_amount": row_decimal(paid_amount),
                "pending_amount": row_decimal(total_contract - paid_amount),
                "overdue_amount": row_decimal(overdue_amount),
            },
            "milestones": milestones,
        }
    )


@app.post("/api/data/import")
def import_data_endpoint(request: Request, db: Session = Depends(get_session)):
    from scripts.import_data import import_csv_folder

    result = import_csv_folder(BASE_DIR / "data" / "import", db)
    write_log(db, "demo_user", "import", "data_migration", "success" if result["failed"] == 0 else "partial", request.state.request_id)
    db.commit()
    return api_ok(result)


@app.get("/api/system/status")
def system_status(db: Session = Depends(get_session)):
    db_status = "ok"
    try:
        db.execute(select(1)).scalar_one()
    except SQLAlchemyError:
        db_status = "fail"
    redis_status = "ok" if redis_available() else "unavailable_degraded"
    return api_ok(
        {
            "app": "ok",
            "database": db_status,
            "redis": redis_status,
            "redis_note": "Redis 在本项目中用于状态检查/缓存演示；Redis 不可用时，核心 ERP 业务接口应尽量保持可用。",
            "log_file": str(LOG_DIR / "app.log"),
        }
    )


def redis_available() -> bool:
    try:
        host = os.getenv("REDIS_HOST", "127.0.0.1")
        port = int(os.getenv("REDIS_PORT", "6379"))
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except Exception:
        return False


def write_log(db: Session, username: str, action: str, module: str, result: str, request_id: str | None) -> None:
    db.add(OperationLog(username=username, action=action, module=module, result=result, request_id=request_id))
