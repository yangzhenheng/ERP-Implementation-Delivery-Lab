CREATE DATABASE IF NOT EXISTS erp_demo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE erp_demo;

CREATE TABLE IF NOT EXISTS customers (
  customer_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_code VARCHAR(32) NOT NULL UNIQUE,
  customer_name VARCHAR(128) NOT NULL,
  contact VARCHAR(64),
  phone VARCHAR(32),
  address VARCHAR(255),
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
  product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_code VARCHAR(32) NOT NULL UNIQUE,
  product_name VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL,
  unit VARCHAR(16) NOT NULL,
  standard_price DECIMAL(14,2) NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'active'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS warehouses (
  warehouse_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  warehouse_code VARCHAR(32) NOT NULL UNIQUE,
  warehouse_name VARCHAR(128) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventory (
  inventory_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  warehouse_id BIGINT NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  safety_stock INT NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_inventory_product_warehouse(product_id, warehouse_id),
  CONSTRAINT fk_inventory_product FOREIGN KEY(product_id) REFERENCES products(product_id),
  CONSTRAINT fk_inventory_warehouse FOREIGN KEY(warehouse_id) REFERENCES warehouses(warehouse_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sales_orders (
  order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(32) NOT NULL UNIQUE,
  customer_id BIGINT NOT NULL,
  order_date DATE NOT NULL,
  delivery_date DATE,
  status VARCHAR(32) NOT NULL,
  total_amount DECIMAL(14,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_order_customer FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sales_order_items (
  order_item_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(14,2) NOT NULL,
  amount DECIMAL(14,2) NOT NULL,
  CONSTRAINT fk_item_order FOREIGN KEY(order_id) REFERENCES sales_orders(order_id),
  CONSTRAINT fk_item_product FOREIGN KEY(product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventory_transactions (
  transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  warehouse_id BIGINT NOT NULL,
  transaction_type VARCHAR(32) NOT NULL,
  quantity INT NOT NULL,
  reference_no VARCHAR(64),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_tx_product FOREIGN KEY(product_id) REFERENCES products(product_id),
  CONSTRAINT fk_tx_warehouse FOREIGN KEY(warehouse_id) REFERENCES warehouses(warehouse_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS implementation_tasks (
  task_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_name VARCHAR(128) NOT NULL,
  task_type VARCHAR(64) NOT NULL,
  owner VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  priority VARCHAR(16) NOT NULL,
  planned_date DATE,
  completed_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS issues (
  issue_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(160) NOT NULL,
  module VARCHAR(64) NOT NULL,
  severity VARCHAR(16) NOT NULL,
  status VARCHAR(32) NOT NULL,
  description TEXT,
  root_cause TEXT,
  solution TEXT,
  owner VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at DATETIME
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS operation_logs (
  log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL,
  action VARCHAR(64) NOT NULL,
  module VARCHAR(64) NOT NULL,
  result VARCHAR(32) NOT NULL,
  request_id VARCHAR(64),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
