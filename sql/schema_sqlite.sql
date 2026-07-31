PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
  customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_code TEXT NOT NULL UNIQUE,
  customer_name TEXT NOT NULL,
  contact TEXT,
  phone TEXT,
  address TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_code TEXT NOT NULL UNIQUE,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit TEXT NOT NULL,
  standard_price NUMERIC NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS warehouses (
  warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
  warehouse_code TEXT NOT NULL UNIQUE,
  warehouse_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
  inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  warehouse_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0,
  safety_stock INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(product_id, warehouse_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id),
  FOREIGN KEY(warehouse_id) REFERENCES warehouses(warehouse_id)
);

CREATE TABLE IF NOT EXISTS sales_orders (
  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_no TEXT NOT NULL UNIQUE,
  customer_id INTEGER NOT NULL,
  order_date TEXT NOT NULL,
  delivery_date TEXT,
  status TEXT NOT NULL,
  total_amount NUMERIC NOT NULL DEFAULT 0,
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS sales_order_items (
  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price NUMERIC NOT NULL,
  amount NUMERIC NOT NULL,
  FOREIGN KEY(order_id) REFERENCES sales_orders(order_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  warehouse_id INTEGER NOT NULL,
  transaction_type TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  reference_no TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(product_id) REFERENCES products(product_id),
  FOREIGN KEY(warehouse_id) REFERENCES warehouses(warehouse_id)
);

CREATE TABLE IF NOT EXISTS implementation_tasks (
  task_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,
  task_type TEXT NOT NULL,
  owner TEXT NOT NULL,
  status TEXT NOT NULL,
  priority TEXT NOT NULL,
  planned_date TEXT,
  completed_date TEXT
);

CREATE TABLE IF NOT EXISTS issues (
  issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  module TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  description TEXT,
  root_cause TEXT,
  solution TEXT,
  owner TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS operation_logs (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  action TEXT NOT NULL,
  module TEXT NOT NULL,
  result TEXT NOT NULL,
  request_id TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_orders_status ON sales_orders(status);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_operation_logs_request ON operation_logs(request_id);
