# Data Migration Guide

All files in `data/import/` are DEMO DATA / MOCK DATA. They are not real customer data.

## Workflow

1. Collect source Excel files from business users.
2. Confirm field mapping against ERP tables.
3. Clean required fields, duplicated codes, encoding and data types.
4. Save CSV files as UTF-8.
5. Run a test import in the demo environment.
6. Compare source counts and target counts.
7. Ask business users to confirm sample records.
8. Run formal import after backup.
9. Record import result and open issues for failed rows.

## Field Mapping

| Source CSV | Target Table | Key Fields |
|---|---|---|
| customers.csv | customers | customer_code, customer_name |
| products.csv | products | product_code, product_name, standard_price |
| inventory.csv | inventory | product_code, warehouse_code, quantity |
| orders.csv | sales_orders, sales_order_items | order_no, customer_code, product_code, quantity |

## Run

```bash
python scripts/import_data.py --folder data/import
```

The script checks required fields, duplicate codes, integer quantities, decimal prices and cross-file references. Results are written to stdout and `logs/import.log`.

## Reconciliation SQL

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory;
```
