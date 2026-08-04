USE erp_demo_lab;
GO

-- 01 SELECT + TOP
SELECT TOP 2 customer_code, customer_name, ISNULL(contact, N'TBD') AS contact_name, created_at
FROM dbo.customers
ORDER BY created_at DESC;

-- 02 INNER JOIN
SELECT o.order_no, c.customer_name, o.status, o.total_amount
FROM dbo.sales_orders o
INNER JOIN dbo.customers c ON c.customer_id = o.customer_id;

-- 03 LEFT JOIN
SELECT c.customer_code, c.customer_name, COUNT(o.order_id) AS order_count
FROM dbo.customers c
LEFT JOIN dbo.sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name;

-- 04 GROUP BY + HAVING
SELECT c.customer_name, SUM(o.total_amount) AS total_amount
FROM dbo.customers c
INNER JOIN dbo.sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_name
HAVING SUM(o.total_amount) > 3000;

-- 05 OFFSET FETCH
SELECT order_no, order_date, status, total_amount
FROM dbo.sales_orders
ORDER BY order_date DESC, order_id DESC
OFFSET 0 ROWS FETCH NEXT 2 ROWS ONLY;

-- 06 ISNULL
SELECT customer_code, customer_name, ISNULL(contact, N'TBD') AS contact_name
FROM dbo.customers;

-- 07 GETDATE
SELECT order_no, order_date, status
FROM dbo.sales_orders
WHERE order_date >= DATEADD(day, -7, CAST(GETDATE() AS DATE));

-- 08 Inventory warning
SELECT p.product_code, p.product_name, i.warehouse_code, i.quantity, i.safety_stock
FROM dbo.inventory i
INNER JOIN dbo.products p ON p.product_id = i.product_id
WHERE i.quantity < i.safety_stock;

-- 09 UPDATE
UPDATE dbo.issues
SET status = N'closed', solution = N'Completed validation note and retest.'
WHERE title = N'Missing customer contact demo';

-- 10 DELETE
DELETE FROM dbo.sales_orders
WHERE order_no = N'SQL-SO-INVALID' AND status = N'draft';

-- 11 INSERT
INSERT INTO dbo.issues(title, module, severity, status)
VALUES(N'SQL Server pagination query demo', N'Database', N'P4', N'open');

-- 12 Counts
SELECT
    (SELECT COUNT(*) FROM dbo.customers) AS customer_count,
    (SELECT COUNT(*) FROM dbo.products) AS product_count,
    (SELECT COUNT(*) FROM dbo.inventory) AS inventory_count,
    (SELECT COUNT(*) FROM dbo.sales_orders) AS order_count,
    (SELECT COUNT(*) FROM dbo.issues) AS issue_count;
GO
