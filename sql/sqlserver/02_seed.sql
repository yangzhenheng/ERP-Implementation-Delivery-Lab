USE erp_demo_lab;
GO

INSERT INTO dbo.customers(customer_code, customer_name, contact, phone) VALUES
(N'CUST-SQL-001', N'Shanghai Precision Assembly Demo', N'Liu Manager', N'13820000001'),
(N'CUST-SQL-002', N'Nanjing Smart Manufacturing Demo', N'Sun Lead', N'13820000002'),
(N'CUST-SQL-003', N'Wuhan Components Trading Demo', NULL, NULL);

INSERT INTO dbo.products(product_code, product_name, category, unit, standard_price) VALUES
(N'SQL-A100', N'Industrial Gateway', N'Equipment', N'pcs', 1800.00),
(N'SQL-B200', N'Data Collection Terminal', N'Equipment', N'pcs', 960.00),
(N'SQL-C300', N'Sensor Cable', N'Material', N'roll', 28.00);

INSERT INTO dbo.inventory(product_id, warehouse_code, quantity, safety_stock) VALUES
(1, N'WH-SH', 18, 8),
(2, N'WH-SH', 5, 12),
(3, N'WH-NJ', 260, 100);

INSERT INTO dbo.sales_orders(order_no, customer_id, order_date, status, total_amount) VALUES
(N'SQL-SO-001', 1, DATEADD(day, -3, CAST(GETDATE() AS DATE)), N'confirmed', 3600.00),
(N'SQL-SO-002', 2, DATEADD(day, -1, CAST(GETDATE() AS DATE)), N'inventory_failed', 9600.00),
(N'SQL-SO-003', 1, CAST(GETDATE() AS DATE), N'completed', 2800.00);

INSERT INTO dbo.sales_order_items(order_id, product_id, quantity, unit_price, amount) VALUES
(1, 1, 2, 1800.00, 3600.00),
(2, 2, 10, 960.00, 9600.00),
(3, 3, 100, 28.00, 2800.00);

INSERT INTO dbo.issues(title, module, severity, status, root_cause, solution) VALUES
(N'SQL Server inventory shortage demo', N'Inventory', N'P2', N'open', NULL, NULL),
(N'Missing customer contact demo', N'Customer', N'P4', N'investigating', N'Legacy data missing contact', N'Ask business owner to complete master data');
GO
