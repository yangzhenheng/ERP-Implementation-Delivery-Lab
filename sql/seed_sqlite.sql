INSERT INTO customers(customer_code, customer_name, contact, phone, address, status) VALUES
('CUST-001','Demo Precision Manufacturing','Ms. Chen','13800000001','Mock address A','active'),
('CUST-002','Demo Assembly Factory','Mr. Li','13800000002','Mock address B','active'),
('CUST-003','Demo Components Trading','Ms. Wang','13800000003','Mock address C','active');

INSERT INTO products(product_code, product_name, category, unit, standard_price, status) VALUES
('SKU-A100','Industrial Scanner','device','pcs',1280.00,'active'),
('SKU-B220','Label Printer','device','pcs',860.00,'active'),
('SKU-C310','Handheld PDA','device','pcs',2360.00,'active'),
('SKU-D450','Barcode Label','consumable','roll',35.00,'active');

INSERT INTO warehouses(warehouse_code, warehouse_name) VALUES
('WH-MAIN','Main Warehouse'),
('WH-QC','Quality Hold Warehouse');

INSERT INTO inventory(product_id, warehouse_id, quantity, safety_stock) VALUES
(1,1,32,10),
(2,1,6,15),
(3,1,12,8),
(4,1,120,50);

INSERT INTO sales_orders(order_no, customer_id, order_date, delivery_date, status, total_amount) VALUES
('SO202607001',1,DATE('now','-2 day'),DATE('now','+5 day'),'completed',5820.00),
('SO202607002',2,DATE('now','-1 day'),DATE('now','+3 day'),'confirmed',4720.00),
('SO202607003',3,DATE('now'),DATE('now','+7 day'),'inventory_failed',8600.00);

INSERT INTO sales_order_items(order_id, product_id, quantity, unit_price, amount) VALUES
(1,1,4,1280.00,5120.00),
(1,4,20,35.00,700.00),
(2,3,2,2360.00,4720.00),
(3,2,10,860.00,8600.00);

INSERT INTO inventory_transactions(product_id, warehouse_id, transaction_type, quantity, reference_no) VALUES
(1,1,'outbound',-4,'SO202607001'),
(4,1,'outbound',-20,'SO202607001'),
(2,1,'adjustment',6,'INIT');

INSERT INTO implementation_tasks(project_name, task_type, owner, status, priority, planned_date, completed_date) VALUES
('Manufacturing ERP Implementation Delivery Lab','requirements','implementation_engineer','completed','P1',DATE('now'),DATE('now')),
('Manufacturing ERP Implementation Delivery Lab','installation','implementation_engineer','completed','P1',DATE('now'),DATE('now')),
('Manufacturing ERP Implementation Delivery Lab','configuration','implementation_engineer','completed','P2',DATE('now'),DATE('now')),
('Manufacturing ERP Implementation Delivery Lab','data_migration','implementation_engineer','in_progress','P1',DATE('now'),NULL),
('Manufacturing ERP Implementation Delivery Lab','testing','implementation_engineer','in_progress','P1',DATE('now'),NULL),
('Manufacturing ERP Implementation Delivery Lab','training','implementation_engineer','not_started','P2',DATE('now'),NULL),
('Manufacturing ERP Implementation Delivery Lab','go_live','implementation_engineer','not_started','P1',DATE('now'),NULL),
('Manufacturing ERP Implementation Delivery Lab','acceptance','implementation_engineer','not_started','P1',DATE('now'),NULL);

INSERT INTO issues(title, module, severity, status, description, owner) VALUES
('Low stock blocks sales order confirmation','inventory','P2','open','Mock issue generated from demo stock check.','implementation_engineer'),
('CSV template date format mismatch','data_import','P3','open','Training example for data migration validation.','implementation_engineer');
