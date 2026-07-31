USE erp_demo;

CREATE OR REPLACE VIEW vw_low_stock AS
SELECT p.product_code, p.product_name, w.warehouse_code, i.quantity, i.safety_stock
FROM inventory i
INNER JOIN products p ON p.product_id = i.product_id
INNER JOIN warehouses w ON w.warehouse_id = i.warehouse_id
WHERE i.quantity < i.safety_stock;

CREATE OR REPLACE VIEW vw_order_summary AS
SELECT o.order_id, o.order_no, c.customer_code, c.customer_name, o.order_date, o.delivery_date, o.status, o.total_amount
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id;

CREATE OR REPLACE VIEW vw_implementation_progress AS
SELECT project_name, task_type, owner, status, priority, planned_date, completed_date
FROM implementation_tasks;
