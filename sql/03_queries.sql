USE erp_demo;

-- 01 查询低于安全库存的产品。
SELECT p.product_code, p.product_name, w.warehouse_code, i.quantity, i.safety_stock
FROM inventory i
INNER JOIN products p ON p.product_id = i.product_id
INNER JOIN warehouses w ON w.warehouse_id = i.warehouse_id
WHERE i.quantity < i.safety_stock
ORDER BY i.quantity ASC;

-- 02 按客户统计订单金额。
SELECT c.customer_code, c.customer_name, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_amount
FROM customers c
LEFT JOIN sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name
ORDER BY total_amount DESC;

-- 03 查询最近 7 天订单。
SELECT order_no, order_date, status, total_amount
FROM sales_orders
WHERE order_date >= CURDATE() - INTERVAL 7 DAY
ORDER BY order_date DESC;

-- 04 查询未关闭的高优先级问题。
SELECT issue_id, title, module, severity, status, owner
FROM issues
WHERE status <> 'closed' AND severity IN ('P1','P2')
ORDER BY severity, created_at;

-- 05 统计实施任务完成率。
SELECT
  COUNT(*) AS total_tasks,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
  ROUND(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS completion_rate
FROM implementation_tasks;

-- 06 查询订单及客户名称。
SELECT o.order_no, c.customer_name, o.order_date, o.status, o.total_amount
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id;

-- 07 查询订单明细及产品信息。
SELECT o.order_no, p.product_code, p.product_name, oi.quantity, oi.unit_price, oi.amount
FROM sales_order_items oi
INNER JOIN sales_orders o ON o.order_id = oi.order_id
INNER JOIN products p ON p.product_id = oi.product_id
ORDER BY o.order_no;

-- 08 按仓库汇总库存。
SELECT w.warehouse_code, w.warehouse_name, SUM(i.quantity) AS total_quantity
FROM warehouses w
LEFT JOIN inventory i ON i.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_code, w.warehouse_name;

-- 09 查询销售金额前 5 的客户。
SELECT c.customer_code, c.customer_name, SUM(o.total_amount) AS sales_amount
FROM customers c
INNER JOIN sales_orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_code, c.customer_name
ORDER BY sales_amount DESC
LIMIT 5;

-- 10 查询库存流水。
SELECT t.created_at, p.product_code, w.warehouse_code, t.transaction_type, t.quantity, t.reference_no
FROM inventory_transactions t
INNER JOIN products p ON p.product_id = t.product_id
INNER JOIN warehouses w ON w.warehouse_id = t.warehouse_id
ORDER BY t.created_at DESC;

-- 11 查询重复客户名称。
SELECT customer_name, COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_name
HAVING COUNT(*) > 1;

-- 12 查询联系人或电话为空的客户。
SELECT customer_code, customer_name, contact, phone
FROM customers
WHERE contact IS NULL OR phone IS NULL;

-- 13 业务确认后更新订单状态。
UPDATE sales_orders
SET status = 'confirmed'
WHERE order_no = 'SO202607003' AND status = 'inventory_failed';

-- 14 批量关闭已修复的 P3 问题。
UPDATE issues
SET status = 'closed', resolved_at = NOW()
WHERE severity = 'P3' AND status <> 'closed';

-- 15 按日期统计订单。
SELECT order_date, COUNT(*) AS order_count, SUM(total_amount) AS day_amount
FROM sales_orders
GROUP BY order_date
ORDER BY order_date DESC;

-- 16 按月统计销售金额。
SELECT DATE_FORMAT(order_date, '%Y-%m') AS sales_month, COUNT(*) AS order_count, SUM(total_amount) AS amount
FROM sales_orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY sales_month DESC;

-- 17 多表 JOIN 查询订单交付检查信息。
SELECT o.order_no, c.customer_name, p.product_code, oi.quantity, i.quantity AS current_stock, o.delivery_date
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id
INNER JOIN sales_order_items oi ON oi.order_id = o.order_id
INNER JOIN products p ON p.product_id = oi.product_id
LEFT JOIN inventory i ON i.product_id = p.product_id;

-- 18 查询已确认金额大于 5000 的客户。
SELECT c.customer_code, c.customer_name, SUM(o.total_amount) AS confirmed_amount
FROM customers c
INNER JOIN sales_orders o ON o.customer_id = c.customer_id
WHERE o.status IN ('confirmed','completed')
GROUP BY c.customer_code, c.customer_name
HAVING SUM(o.total_amount) > 5000;

-- 19 新增模拟仓库示例。
INSERT INTO warehouses(warehouse_code, warehouse_name)
VALUES('WH-SPARE','备件仓');

-- 20 删除无效导入订单示例，必须按订单号限定范围。
DELETE FROM sales_orders
WHERE order_no = 'SO-INVALID-IMPORT' AND status = 'draft';
