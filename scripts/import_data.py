import argparse
import csv
import logging
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import Customer, Inventory, Product, SalesOrder, SalesOrderItem, Warehouse, init_db, SessionLocal

LOG_FILE = BASE_DIR / "logs" / "import.log"
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@dataclass
class ImportStats:
    success: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def as_dict(self):
        return {"success": self.success, "failed": self.failed, "skipped": self.skipped, "errors": self.errors}


def require_columns(row: dict, required: list[str], file_name: str, line_no: int) -> list[str]:
    return [f"{file_name}:{line_no} 缺少必填字段 {name}" for name in required if not str(row.get(name, "")).strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def import_csv_folder(folder: Path, db) -> dict:
    stats = ImportStats()
    folder = Path(folder)
    if not folder.exists():
        return {"success": 0, "failed": 1, "skipped": 0, "errors": [f"导入目录不存在: {folder}"]}

    try:
        import_customers(folder / "customers.csv", db, stats)
        import_products(folder / "products.csv", db, stats)
        import_inventory(folder / "inventory.csv", db, stats)
        import_orders(folder / "orders.csv", db, stats)
        logging.info("CSV 导入完成: %s", stats.as_dict())
    except Exception as exc:
        db.rollback()
        logging.exception("CSV 导入失败，事务已回滚: %s", exc)
        raise
    return stats.as_dict()


def import_customers(path: Path, db, stats: ImportStats):
    if not path.exists():
        stats.skipped += 1
        stats.errors.append(f"跳过缺失文件 {path.name}")
        return
    seen = set()
    for line_no, row in enumerate(read_csv(path), start=2):
        errors = require_columns(row, ["customer_code", "customer_name"], path.name, line_no)
        code = row.get("customer_code", "").strip()
        if code in seen:
            errors.append(f"{path.name}:{line_no} 文件内 customer_code 重复")
        seen.add(code)
        if db.query(Customer).filter_by(customer_code=code).first():
            stats.skipped += 1
            continue
        if errors:
            stats.failed += 1
            stats.errors.extend(errors)
            continue
        db.add(Customer(customer_code=code, customer_name=row["customer_name"].strip(), contact=row.get("contact"), phone=row.get("phone"), address=row.get("address"), status=row.get("status") or "active"))
        stats.success += 1


def import_products(path: Path, db, stats: ImportStats):
    if not path.exists():
        stats.skipped += 1
        stats.errors.append(f"跳过缺失文件 {path.name}")
        return
    for line_no, row in enumerate(read_csv(path), start=2):
        errors = require_columns(row, ["product_code", "product_name", "standard_price"], path.name, line_no)
        try:
            price = Decimal(str(row.get("standard_price", "0")))
        except InvalidOperation:
            errors.append(f"{path.name}:{line_no} standard_price 格式无效")
            price = Decimal("0")
        code = row.get("product_code", "").strip()
        if db.query(Product).filter_by(product_code=code).first():
            stats.skipped += 1
            continue
        if errors:
            stats.failed += 1
            stats.errors.extend(errors)
            continue
        db.add(Product(product_code=code, product_name=row["product_name"].strip(), category=row.get("category") or "finished_goods", unit=row.get("unit") or "pcs", standard_price=price, status=row.get("status") or "active"))
        stats.success += 1


def import_inventory(path: Path, db, stats: ImportStats):
    if not path.exists():
        stats.skipped += 1
        stats.errors.append(f"跳过缺失文件 {path.name}")
        return
    db.flush()
    for line_no, row in enumerate(read_csv(path), start=2):
        errors = require_columns(row, ["product_code", "warehouse_code", "quantity", "safety_stock"], path.name, line_no)
        product = db.query(Product).filter_by(product_code=row.get("product_code", "").strip()).first()
        warehouse = db.query(Warehouse).filter_by(warehouse_code=row.get("warehouse_code", "").strip()).first()
        if not product:
            errors.append(f"{path.name}:{line_no} 产品编码不存在")
        if not warehouse:
            warehouse = Warehouse(warehouse_code=row.get("warehouse_code", "").strip(), warehouse_name=row.get("warehouse_name") or row.get("warehouse_code", "").strip())
            db.add(warehouse)
            db.flush()
        try:
            quantity = int(row.get("quantity", "0"))
            safety_stock = int(row.get("safety_stock", "0"))
        except ValueError:
            errors.append(f"{path.name}:{line_no} quantity/safety_stock 必须是整数")
            quantity = 0
            safety_stock = 0
        if errors:
            stats.failed += 1
            stats.errors.extend(errors)
            continue
        existing = db.query(Inventory).filter_by(product_id=product.product_id, warehouse_id=warehouse.warehouse_id).first()
        if existing:
            existing.quantity = quantity
            existing.safety_stock = safety_stock
            stats.success += 1
        else:
            db.add(Inventory(product_id=product.product_id, warehouse_id=warehouse.warehouse_id, quantity=quantity, safety_stock=safety_stock))
            stats.success += 1


def import_orders(path: Path, db, stats: ImportStats):
    if not path.exists():
        stats.skipped += 1
        stats.errors.append(f"跳过缺失文件 {path.name}")
        return
    db.flush()
    for line_no, row in enumerate(read_csv(path), start=2):
        errors = require_columns(row, ["order_no", "customer_code", "product_code", "quantity"], path.name, line_no)
        if db.query(SalesOrder).filter_by(order_no=row.get("order_no", "").strip()).first():
            stats.skipped += 1
            continue
        customer = db.query(Customer).filter_by(customer_code=row.get("customer_code", "").strip()).first()
        product = db.query(Product).filter_by(product_code=row.get("product_code", "").strip()).first()
        if not customer:
            errors.append(f"{path.name}:{line_no} 客户编码不存在")
        if not product:
            errors.append(f"{path.name}:{line_no} 产品编码不存在")
        try:
            quantity = int(row.get("quantity", "0"))
        except ValueError:
            errors.append(f"{path.name}:{line_no} quantity 必须是整数")
            quantity = 0
        if errors:
            stats.failed += 1
            stats.errors.extend(errors)
            continue
        amount = product.standard_price * quantity
        order = SalesOrder(order_no=row["order_no"].strip(), customer_id=customer.customer_id, status=row.get("status") or "draft", total_amount=amount)
        db.add(order)
        db.flush()
        db.add(SalesOrderItem(order_id=order.order_id, product_id=product.product_id, quantity=quantity, unit_price=product.standard_price, amount=amount))
        stats.success += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="将模拟 CSV 数据导入 ERP 实施实验室数据库。")
    parser.add_argument("--folder", default=str(BASE_DIR / "data" / "import"))
    args = parser.parse_args()
    init_db()
    with SessionLocal() as db:
        result = import_csv_folder(Path(args.folder), db)
        db.commit()
    print(result)
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
