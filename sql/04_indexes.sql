USE erp_demo;

CREATE INDEX idx_customers_code ON customers(customer_code);
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_sales_orders_status ON sales_orders(status);
CREATE INDEX idx_sales_orders_customer ON sales_orders(customer_id);
CREATE INDEX idx_sales_orders_date ON sales_orders(order_date);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_warehouse ON inventory(warehouse_id);
CREATE INDEX idx_issues_status_severity ON issues(status, severity);
CREATE INDEX idx_operation_logs_request ON operation_logs(request_id);

EXPLAIN
SELECT o.order_no, c.customer_name, o.total_amount
FROM sales_orders o
INNER JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'confirmed'
ORDER BY o.order_date DESC;
