USE erp_demo_lab;
GO

-- 01 SELECT + TOP：查看最新客户。
SELECT TOP 2 customer_code, customer_name, ISNULL(contact, N'待补充') AS contact_name, created_at
FROM dbo.customers
ORDER BY created_at DESC;

-- 02 INNER JOIN：订单关联客户。
SELECT o.order_no, c.customer_name, o.status, o.total_amount
FROM dbo.sales_orders o
INNER JOIN dbo.customers c ON c.customer_id = o.customer_id;

-- 03 LEFT JOIN：客户及其订单数量。
SELECT c.customer_code, c.customer_name, COUNT(o.order_id) AS order_count
FROM dbo.customers c
LEFT JOIN dbo.sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name;

-- 04 GROUP BY + HAVING：筛选订单金额超过 3000 的客户。
SELECT c.customer_name, SUM(o.total_amount) AS total_amount
FROM dbo.customers c
INNER JOIN dbo.sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_name
HAVING SUM(o.total_amount) > 3000;

-- 05 OFFSET FETCH：分页查询订单。
SELECT order_no, order_date, status, total_amount
FROM dbo.sales_orders
ORDER BY order_date DESC, order_id DESC
OFFSET 0 ROWS FETCH NEXT 2 ROWS ONLY;

-- 06 ISNULL：处理空联系人字段。
SELECT customer_code, customer_name, ISNULL(contact, N'待业务补充') AS contact_name
FROM dbo.customers;

-- 07 GETDATE：查询最近 7 天订单。
SELECT order_no, order_date, status
FROM dbo.sales_orders
WHERE order_date >= DATEADD(day, -7, CAST(GETDATE() AS DATE));

-- 08 库存预警。
SELECT p.product_code, p.product_name, i.warehouse_code, i.quantity, i.safety_stock
FROM dbo.inventory i
INNER JOIN dbo.products p ON p.product_id = i.product_id
WHERE i.quantity < i.safety_stock;

-- 09 UPDATE：关闭已解决问题。
UPDATE dbo.issues
SET status = N'closed', solution = N'已补充排查记录并验证。'
WHERE title = N'客户联系人为空';

-- 10 DELETE：删除无效草稿订单示例，必须限定条件。
DELETE FROM dbo.sales_orders
WHERE order_no = N'SQL-SO-INVALID' AND status = N'draft';

-- 11 INSERT：新增模拟问题。
INSERT INTO dbo.issues(title, module, severity, status)
VALUES(N'SQL Server 分页查询演示', N'数据库', N'P4', N'open');

-- 12 验证数据量。
SELECT
    (SELECT COUNT(*) FROM dbo.customers) AS customer_count,
    (SELECT COUNT(*) FROM dbo.products) AS product_count,
    (SELECT COUNT(*) FROM dbo.inventory) AS inventory_count,
    (SELECT COUNT(*) FROM dbo.sales_orders) AS order_count,
    (SELECT COUNT(*) FROM dbo.issues) AS issue_count;
GO
