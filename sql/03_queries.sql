USE erp_demo;

-- 01 Products below safety stock.
SELECT p.product_code, p.product_name, w.warehouse_code, i.quantity, i.safety_stock
FROM inventory i
INNER JOIN products p ON p.product_id = i.product_id
INNER JOIN warehouses w ON w.warehouse_id = i.warehouse_id
WHERE i.quantity < i.safety_stock
ORDER BY i.quantity ASC;

-- 02 Total order amount by customer.
SELECT c.customer_code, c.customer_name, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_amount
FROM customers c
LEFT JOIN sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name
ORDER BY total_amount DESC;

-- 03 Orders in the last 7 days.
SELECT order_no, order_date, status, total_amount
FROM sales_orders
WHERE order_date >= CURDATE() - INTERVAL 7 DAY
ORDER BY order_date DESC;

-- 04 Open serious issues.
SELECT issue_id, title, module, severity, status, owner
FROM issues
WHERE status <> 'closed' AND severity IN ('P1','P2')
ORDER BY severity, created_at;

-- 05 Implementation task completion rate.
SELECT
  COUNT(*) AS total_tasks,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
  ROUND(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS completion_rate
FROM implementation_tasks;

-- 06 Orders with customer names.
SELECT o.order_no, c.customer_name, o.order_date, o.status, o.total_amount
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id;

-- 07 Order lines with products.
SELECT o.order_no, p.product_code, p.product_name, oi.quantity, oi.unit_price, oi.amount
FROM sales_order_items oi
INNER JOIN sales_orders o ON o.order_id = oi.order_id
INNER JOIN products p ON p.product_id = oi.product_id
ORDER BY o.order_no;

-- 08 Inventory by warehouse.
SELECT w.warehouse_code, w.warehouse_name, SUM(i.quantity) AS total_quantity
FROM warehouses w
LEFT JOIN inventory i ON i.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_code, w.warehouse_name;

-- 09 Top 5 customers by sales amount.
SELECT c.customer_code, c.customer_name, SUM(o.total_amount) AS sales_amount
FROM customers c
INNER JOIN sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name
ORDER BY sales_amount DESC
LIMIT 5;

-- 10 Inventory transaction history.
SELECT t.created_at, p.product_code, w.warehouse_code, t.transaction_type, t.quantity, t.reference_no
FROM inventory_transactions t
INNER JOIN products p ON p.product_id = t.product_id
INNER JOIN warehouses w ON w.warehouse_id = t.warehouse_id
ORDER BY t.created_at DESC;

-- 11 Duplicate customer names.
SELECT customer_name, COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_name
HAVING COUNT(*) > 1;

-- 12 NULL contact fields.
SELECT customer_code, customer_name, contact, phone
FROM customers
WHERE contact IS NULL OR phone IS NULL;

-- 13 Update order status after business confirmation.
UPDATE sales_orders
SET status = 'confirmed'
WHERE order_no = 'SO202607003' AND status = 'inventory_failed';

-- 14 Batch close fixed P3 issues.
UPDATE issues
SET status = 'closed', resolved_at = NOW()
WHERE severity = 'P3' AND status <> 'closed';

-- 15 Order count by date.
SELECT order_date, COUNT(*) AS order_count, SUM(total_amount) AS day_amount
FROM sales_orders
GROUP BY order_date
ORDER BY order_date DESC;

-- 16 Monthly sales.
SELECT DATE_FORMAT(order_date, '%Y-%m') AS sales_month, COUNT(*) AS order_count, SUM(total_amount) AS amount
FROM sales_orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY sales_month DESC;

-- 17 Multi-table join for order delivery check.
SELECT o.order_no, c.customer_name, p.product_code, oi.quantity, i.quantity AS current_stock, o.delivery_date
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id
INNER JOIN sales_order_items oi ON oi.order_id = o.order_id
INNER JOIN products p ON p.product_id = oi.product_id
LEFT JOIN inventory i ON i.product_id = p.product_id;

-- 18 Customers whose confirmed amount is greater than 5000.
SELECT c.customer_code, c.customer_name, SUM(o.total_amount) AS confirmed_amount
FROM customers c
INNER JOIN sales_orders o ON o.customer_id = c.customer_id
WHERE o.status IN ('confirmed','completed')
GROUP BY c.customer_code, c.customer_name
HAVING SUM(o.total_amount) > 5000;

-- 19 INSERT example for a new mock warehouse.
INSERT INTO warehouses(warehouse_code, warehouse_name)
VALUES('WH-SPARE','Spare Parts Warehouse');

-- 20 DELETE example for an invalid imported order, scoped by order_no.
DELETE FROM sales_orders
WHERE order_no = 'SO-INVALID-IMPORT' AND status = 'draft';
