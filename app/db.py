import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _database_url() -> str:
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    app_env = os.getenv("APP_ENV", "dev").lower()
    if app_env in {"production", "demo", "prod"}:
        user = os.getenv("DB_USER", "erp_user")
        password = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "3306")
        name = os.getenv("DB_NAME", "erp_demo")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

    db_path = Path(os.getenv("ERP_DB_PATH", BASE_DIR / "data" / "erp_demo.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


DATABASE_URL = _database_url()
engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    orders: Mapped[list["SalesOrder"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="finished_goods", nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="pcs", nullable=False)
    standard_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(128), nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("product_id", "warehouse_id", name="uq_inventory_product_warehouse"),)

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.warehouse_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)

    product: Mapped[Product] = relationship()
    warehouse: Mapped[Warehouse] = relationship()


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    delivery_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="orders")
    items: Mapped[list["SalesOrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped[SalesOrder] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.warehouse_id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_no: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    product: Mapped[Product] = relationship()
    warehouse: Mapped[Warehouse] = relationship()


class ImplementationTask(Base):
    __tablename__ = "implementation_tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(128), nullable=False)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    owner: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="not_started", nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="P2", nullable=False)
    planned_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)


class Issue(Base):
    __tablename__ = "issues"

    issue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="P2", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text)
    solution: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(64), default="implementation_engineer", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OperationLog(Base):
    __tablename__ = "operation_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), default="demo_user", nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


Index("idx_sales_orders_status", SalesOrder.status)
Index("idx_sales_orders_customer", SalesOrder.customer_id)
Index("idx_inventory_product", Inventory.product_id)
Index("idx_issues_status", Issue.status)
Index("idx_operation_logs_request", OperationLog.request_id)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count(Customer.customer_id))) == 0:
            seed_demo_data(db)
            db.commit()


def seed_demo_data(db: Session) -> None:
    customers = [
        Customer(customer_code="CUST-001", customer_name="Demo Precision Manufacturing", contact="Ms. Chen", phone="13800000001", address="Mock address A"),
        Customer(customer_code="CUST-002", customer_name="Demo Assembly Factory", contact="Mr. Li", phone="13800000002", address="Mock address B"),
        Customer(customer_code="CUST-003", customer_name="Demo Components Trading", contact="Ms. Wang", phone="13800000003", address="Mock address C"),
    ]
    products = [
        Product(product_code="SKU-A100", product_name="Industrial Scanner", category="device", unit="pcs", standard_price=Decimal("1280.00")),
        Product(product_code="SKU-B220", product_name="Label Printer", category="device", unit="pcs", standard_price=Decimal("860.00")),
        Product(product_code="SKU-C310", product_name="Handheld PDA", category="device", unit="pcs", standard_price=Decimal("2360.00")),
        Product(product_code="SKU-D450", product_name="Barcode Label", category="consumable", unit="roll", standard_price=Decimal("35.00")),
    ]
    warehouses = [
        Warehouse(warehouse_code="WH-MAIN", warehouse_name="Main Warehouse"),
        Warehouse(warehouse_code="WH-QC", warehouse_name="Quality Hold Warehouse"),
    ]
    db.add_all(customers + products + warehouses)
    db.flush()

    db.add_all(
        [
            Inventory(product_id=products[0].product_id, warehouse_id=warehouses[0].warehouse_id, quantity=32, safety_stock=10),
            Inventory(product_id=products[1].product_id, warehouse_id=warehouses[0].warehouse_id, quantity=6, safety_stock=15),
            Inventory(product_id=products[2].product_id, warehouse_id=warehouses[0].warehouse_id, quantity=12, safety_stock=8),
            Inventory(product_id=products[3].product_id, warehouse_id=warehouses[0].warehouse_id, quantity=120, safety_stock=50),
        ]
    )

    order1 = SalesOrder(order_no="SO202607001", customer_id=customers[0].customer_id, order_date=date.today() - timedelta(days=2), delivery_date=date.today() + timedelta(days=5), status="completed")
    order1.items = [
        SalesOrderItem(product_id=products[0].product_id, quantity=4, unit_price=products[0].standard_price, amount=Decimal("5120.00")),
        SalesOrderItem(product_id=products[3].product_id, quantity=20, unit_price=products[3].standard_price, amount=Decimal("700.00")),
    ]
    order1.total_amount = Decimal("5820.00")
    order2 = SalesOrder(order_no="SO202607002", customer_id=customers[1].customer_id, order_date=date.today() - timedelta(days=1), delivery_date=date.today() + timedelta(days=3), status="confirmed")
    order2.items = [SalesOrderItem(product_id=products[2].product_id, quantity=2, unit_price=products[2].standard_price, amount=Decimal("4720.00"))]
    order2.total_amount = Decimal("4720.00")
    order3 = SalesOrder(order_no="SO202607003", customer_id=customers[2].customer_id, order_date=date.today(), delivery_date=date.today() + timedelta(days=7), status="inventory_failed")
    order3.items = [SalesOrderItem(product_id=products[1].product_id, quantity=10, unit_price=products[1].standard_price, amount=Decimal("8600.00"))]
    order3.total_amount = Decimal("8600.00")
    db.add_all([order1, order2, order3])

    db.add_all(
        [
            InventoryTransaction(product_id=products[0].product_id, warehouse_id=warehouses[0].warehouse_id, transaction_type="outbound", quantity=-4, reference_no="SO202607001"),
            InventoryTransaction(product_id=products[3].product_id, warehouse_id=warehouses[0].warehouse_id, transaction_type="outbound", quantity=-20, reference_no="SO202607001"),
            InventoryTransaction(product_id=products[1].product_id, warehouse_id=warehouses[0].warehouse_id, transaction_type="adjustment", quantity=6, reference_no="INIT"),
        ]
    )

    task_types = ["requirements", "installation", "configuration", "data_migration", "testing", "training", "go_live", "acceptance"]
    statuses = ["completed", "completed", "completed", "in_progress", "in_progress", "not_started", "not_started", "not_started"]
    priorities = ["P1", "P1", "P2", "P1", "P1", "P2", "P1", "P1"]
    for i, task_type in enumerate(task_types):
        db.add(
            ImplementationTask(
                project_name="Manufacturing ERP Implementation Delivery Lab",
                task_type=task_type,
                owner="implementation_engineer",
                status=statuses[i],
                priority=priorities[i],
                planned_date=date.today() + timedelta(days=i),
                completed_date=date.today() if statuses[i] == "completed" else None,
            )
        )

    db.add_all(
        [
            Issue(title="Low stock blocks sales order confirmation", module="inventory", severity="P2", status="open", description="Mock issue generated from demo stock check.", owner="implementation_engineer"),
            Issue(title="CSV template date format mismatch", module="data_import", severity="P3", status="open", description="Training example for data migration validation.", owner="implementation_engineer"),
            Issue(title="Nginx reverse proxy path verified", module="deployment", severity="P2", status="closed", root_cause="Nginx config needed upstream path check.", solution="Updated reverse proxy location and health check.", owner="implementation_engineer", resolved_at=now_utc()),
        ]
    )
