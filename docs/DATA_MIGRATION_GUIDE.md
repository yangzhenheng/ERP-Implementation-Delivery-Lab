# 数据迁移指南

`data/import/` 目录中的 CSV 文件均为模拟数据，不是真实客户资料。

## 迁移流程

1. 向业务方收集客户、产品、库存、订单等 Excel 数据。
2. 确认字段映射关系。
3. 清洗必填字段、重复编码、日期格式、数值类型和中文编码。
4. 将文件保存为 UTF-8 CSV。
5. 在测试环境执行试导入。
6. 核对源数据数量与目标库数量。
7. 抽查关键客户、产品、库存和订单。
8. 业务方确认后执行正式导入。
9. 记录导入结果和失败行原因。

## 字段映射

| CSV 文件 | 目标表 | 关键字段 |
|---|---|---|
| `customers.csv` | `customers` | `customer_code`, `customer_name` |
| `products.csv` | `products` | `product_code`, `product_name`, `standard_price` |
| `inventory.csv` | `inventory` | `product_code`, `warehouse_code`, `quantity` |
| `orders.csv` | `sales_orders`, `sales_order_items` | `order_no`, `customer_code`, `product_code`, `quantity` |

## 执行命令

```bash
python scripts/import_data.py --folder data/import
```

脚本会检查：

- 必填字段
- 重复编码
- 数值类型
- 外键引用
- 错误行原因
- 成功、失败、跳过数量

## 核对 SQL

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales_orders;
SELECT COUNT(*) FROM inventory;
```

## 面试讲解重点

数据迁移不是简单导入文件，而是要先确认字段映射、清洗规则和业务口径，再做试导入、数量核对、抽样检查和业务确认。正式导入前必须备份数据库。
