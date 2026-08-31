USE retailtech;

-- Summary table creation
-- Create subsets of data focused on key metrics

-- 1. Create a Sales Summary Table
CREATE TABLE sales_summary AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.payment_type,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    oi.`discount(%)`,
    oi.shipping_cost,
    (oi.quantity * oi.unit_price) AS revenue
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id;
    
SELECT *
FROM sales_summary
LIMIT 10;

-- 2. Create a Customer Sales Summary
CREATE TABLE customer_sales_summary AS
SELECT
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.unit_price) AS avg_unit_price
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY o.customer_id;

SELECT *
FROM customer_sales_summary
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Create Category Summary
CREATE TABLE category_sales_summary AS
SELECT
    p.Category_name,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.unit_price) AS avg_unit_price
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
GROUP BY p.Category_name;

SELECT *
FROM category_sales_summary
ORDER BY total_revenue DESC;

-- 4. Create Order Status Summary
CREATE TABLE order_status_summary AS
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY order_status;

SELECT *
FROM order_status_summary
ORDER BY total_orders DESC;

-- 5. Create Payment Summary
CREATE TABLE payment_summary AS
SELECT
    payment_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY payment_type;

SELECT *
FROM payment_summary
ORDER BY total_revenue DESC;

-- SQL Views
-- 1. Create a Sales View
CREATE VIEW sales_view AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.payment_type,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    oi.`discount(%)`,
    oi.shipping_cost,
    (oi.quantity * oi.unit_price) AS revenue
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id;
    
SELECT *
FROM sales_view
LIMIT 10;

-- 2. Create a Payment Performance View
CREATE VIEW payment_performance_view AS
SELECT
    o.payment_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY o.payment_type;

SELECT *
FROM payment_performance_view
ORDER BY total_revenue DESC;

-- 3. Create a Category Revenue View
CREATE VIEW category_revenue_view AS
SELECT
    p.Category_name,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.unit_price) AS average_unit_price
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
GROUP BY p.Category_name;

SELECT *
FROM category_revenue_view
ORDER BY total_revenue DESC;

-- 4. Create an Order Status View
CREATE VIEW order_status_view AS
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY order_status;

SELECT *
FROM order_status_view
ORDER BY total_orders DESC;

-- 5. Create a Customer Revenue View
CREATE VIEW customer_revenue_view AS
SELECT
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.unit_price) AS average_unit_price
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY o.customer_id;

SELECT *
FROM customer_revenue_view
ORDER BY total_revenue DESC
LIMIT 10;

-- Check all views
SHOW FULL TABLES
WHERE Table_type = 'VIEW';

