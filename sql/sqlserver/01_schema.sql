IF DB_ID(N'erp_demo_lab') IS NULL
BEGIN
    CREATE DATABASE erp_demo_lab;
END;
GO

USE erp_demo_lab;
GO

IF OBJECT_ID(N'dbo.sales_order_items', N'U') IS NOT NULL DROP TABLE dbo.sales_order_items;
IF OBJECT_ID(N'dbo.sales_orders', N'U') IS NOT NULL DROP TABLE dbo.sales_orders;
IF OBJECT_ID(N'dbo.inventory', N'U') IS NOT NULL DROP TABLE dbo.inventory;
IF OBJECT_ID(N'dbo.issues', N'U') IS NOT NULL DROP TABLE dbo.issues;
IF OBJECT_ID(N'dbo.products', N'U') IS NOT NULL DROP TABLE dbo.products;
IF OBJECT_ID(N'dbo.customers', N'U') IS NOT NULL DROP TABLE dbo.customers;
GO

CREATE TABLE dbo.customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(32) NOT NULL UNIQUE,
    customer_name NVARCHAR(128) NOT NULL,
    contact NVARCHAR(64) NULL,
    phone NVARCHAR(32) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT N'active',
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

CREATE TABLE dbo.products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    product_code NVARCHAR(32) NOT NULL UNIQUE,
    product_name NVARCHAR(128) NOT NULL,
    category NVARCHAR(64) NOT NULL,
    unit NVARCHAR(16) NOT NULL,
    standard_price DECIMAL(14,2) NOT NULL DEFAULT 0,
    status NVARCHAR(20) NOT NULL DEFAULT N'active'
);

CREATE TABLE dbo.inventory (
    inventory_id INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_code NVARCHAR(32) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    safety_stock INT NOT NULL DEFAULT 0,
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT fk_inventory_product FOREIGN KEY(product_id) REFERENCES dbo.products(product_id)
);

CREATE TABLE dbo.sales_orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    order_no NVARCHAR(32) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    status NVARCHAR(32) NOT NULL,
    total_amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_order_customer FOREIGN KEY(customer_id) REFERENCES dbo.customers(customer_id)
);

CREATE TABLE dbo.sales_order_items (
    order_item_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(14,2) NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    CONSTRAINT fk_item_order FOREIGN KEY(order_id) REFERENCES dbo.sales_orders(order_id),
    CONSTRAINT fk_item_product FOREIGN KEY(product_id) REFERENCES dbo.products(product_id)
);

CREATE TABLE dbo.issues (
    issue_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(160) NOT NULL,
    module NVARCHAR(64) NOT NULL,
    severity NVARCHAR(16) NOT NULL,
    status NVARCHAR(32) NOT NULL,
    root_cause NVARCHAR(MAX) NULL,
    solution NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO
