USE erp_demo_lab;
GO

INSERT INTO dbo.customers(customer_code, customer_name, contact, phone) VALUES
(N'CUST-SQL-001', N'上海精密装配有限公司（模拟）', N'刘经理', N'13820000001'),
(N'CUST-SQL-002', N'南京智能制造工厂（模拟）', N'孙主管', N'13820000002'),
(N'CUST-SQL-003', N'武汉零部件贸易有限公司（模拟）', NULL, NULL);

INSERT INTO dbo.products(product_code, product_name, category, unit, standard_price) VALUES
(N'SQL-A100', N'工业网关', N'设备', N'台', 1800.00),
(N'SQL-B200', N'采集终端', N'设备', N'台', 960.00),
(N'SQL-C300', N'传感器线束', N'物料', N'根', 28.00);

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
(N'SQL Server 库存不足演示', N'库存管理', N'P2', N'open', NULL, NULL),
(N'客户联系人为空', N'客户管理', N'P4', N'investigating', N'历史数据缺失', N'联系业务补齐');
GO
