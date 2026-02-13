-- E-Commerce Data Warehouse Schema
-- Star Schema Design: Fact table + Dimension tables

-- Dimension: Products
CREATE TABLE IF NOT EXISTS dim_product (
    product_id SERIAL PRIMARY KEY,
    product_title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Users
CREATE TABLE IF NOT EXISTS dim_user (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    address_city VARCHAR(100),
    address_street VARCHAR(255),
    address_zipcode VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Time/Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INT NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN DEFAULT FALSE,
    is_holiday BOOLEAN DEFAULT FALSE
);

-- Dimension: Category (denormalized from product for easier aggregation)
CREATE TABLE IF NOT EXISTS dim_category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact Table: Sales
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT REFERENCES dim_user(user_id),
    product_id INT REFERENCES dim_product(product_id),
    date_id INT REFERENCES dim_date(date_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    revenue DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_id, product_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_sales_user ON fact_sales(user_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order ON fact_sales(order_id);
CREATE INDEX IF NOT EXISTS idx_dim_product_category ON dim_product(category);

-- View: Sales Summary by Category
CREATE OR REPLACE VIEW vw_sales_by_category AS
SELECT 
    p.category,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.quantity) as total_quantity,
    SUM(f.revenue) as total_revenue,
    AVG(f.revenue) as avg_order_value
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category;

-- View: Sales Summary by Date
CREATE OR REPLACE VIEW vw_sales_by_date AS
SELECT 
    d.full_date,
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.full_date, d.year, d.month, d.month_name
ORDER BY d.full_date DESC;

-- View: Top Products
CREATE OR REPLACE VIEW vw_top_products AS
SELECT 
    p.product_id,
    p.product_title,
    p.category,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.quantity) as quantity_sold,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_title, p.category
ORDER BY total_revenue DESC
LIMIT 100;
