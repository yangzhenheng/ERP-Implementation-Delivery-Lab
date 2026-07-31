# CASE05 CSV Import Field Error

Safety: local mock CSV only.

## Symptom

`python scripts/import_data.py` reports failed rows.

## Logs

`logs/import.log` records file name, line number and error reason.

## Commands

```bash
python scripts/import_data.py --folder data/import
tail -n 100 logs/import.log
```

## Root Cause

Required field missing, duplicated code, invalid number, wrong encoding or missing referenced customer/product.

## Solution

Fix the CSV source, save as UTF-8, rerun import, and reconcile counts:

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales_orders;
```
