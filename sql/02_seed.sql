USE erp_demo;

INSERT INTO customers(customer_code, customer_name, contact, phone, address, status) VALUES
('CUST-001','华南精密制造有限公司（模拟）','陈经理','13800000001','广东省广州市模拟工业园 A 区','active'),
('CUST-002','苏州装配工厂（模拟）','李主管','13800000002','江苏省苏州市模拟产业园 B 栋','active'),
('CUST-003','成都零部件贸易有限公司（模拟）','王经理','13800000003','四川省成都市模拟供应链园区','active');

INSERT INTO products(product_code, product_name, category, unit, standard_price, status) VALUES
('SKU-A100','工业扫码枪','设备','台',1280.00,'active'),
('SKU-B220','标签打印机','设备','台',860.00,'active'),
('SKU-C310','PDA 手持终端','设备','台',2360.00,'active'),
('SKU-D450','条码标签纸','耗材','卷',35.00,'active');

INSERT INTO warehouses(warehouse_code, warehouse_name) VALUES
('WH-MAIN','主仓库'),
('WH-QC','质检暂存仓');

INSERT INTO inventory(product_id, warehouse_id, quantity, safety_stock) VALUES
(1,1,32,10),
(2,1,6,15),
(3,1,12,8),
(4,1,120,50);

INSERT INTO sales_orders(order_no, customer_id, order_date, delivery_date, status, total_amount) VALUES
('SO202607001',1,CURDATE() - INTERVAL 2 DAY,CURDATE() + INTERVAL 5 DAY,'completed',5820.00),
('SO202607002',2,CURDATE() - INTERVAL 1 DAY,CURDATE() + INTERVAL 3 DAY,'confirmed',4720.00),
('SO202607003',3,CURDATE(),CURDATE() + INTERVAL 7 DAY,'inventory_failed',8600.00);

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
('制造业 ERP 实施交付实验室','requirements','implementation_engineer','completed','P1',CURDATE(),CURDATE()),
('制造业 ERP 实施交付实验室','installation','implementation_engineer','completed','P1',CURDATE(),CURDATE()),
('制造业 ERP 实施交付实验室','configuration','implementation_engineer','completed','P2',CURDATE(),CURDATE()),
('制造业 ERP 实施交付实验室','data_migration','implementation_engineer','in_progress','P1',CURDATE(),NULL),
('制造业 ERP 实施交付实验室','testing','implementation_engineer','in_progress','P1',CURDATE(),NULL),
('制造业 ERP 实施交付实验室','training','implementation_engineer','not_started','P2',CURDATE(),NULL),
('制造业 ERP 实施交付实验室','go_live','implementation_engineer','not_started','P1',CURDATE(),NULL),
('制造业 ERP 实施交付实验室','acceptance','implementation_engineer','not_started','P1',CURDATE(),NULL);

INSERT INTO issues(title, module, severity, status, description, owner) VALUES
('销售订单库存不足，暂不能确认','库存管理','P2','open','由演示库存校验流程生成的模拟问题。','implementation_engineer'),
('CSV 导入模板日期格式不一致','数据迁移','P3','open','用于演示数据迁移校验和错误行记录。','implementation_engineer');
