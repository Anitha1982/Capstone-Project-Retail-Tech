-- =====================================================
-- PHASE 6: SQL ANALYSIS
-- DATASET READINESS VALIDATION
-- =====================================================

USE retailtech;

-- 1. Verify required tables
SHOW TABLES;

-- 2. Validate row counts
-- Check number of records in each table

SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers

UNION ALL

SELECT 'geolocation', COUNT(*)
FROM geolocation

UNION ALL

SELECT 'order_items', COUNT(*)
FROM order_items

UNION ALL

SELECT 'order_reviews', COUNT(*)
FROM order_reviews

UNION ALL

SELECT 'orders', COUNT(*)
FROM orders

UNION ALL

SELECT 'products', COUNT(*)
FROM products;

-- 3. Validate table structures
-- Validate Customers structure
DESCRIBE customers;

-- Validate Orders structure
DESCRIBE orders;

-- Validate Order Items structure
DESCRIBE order_items;

-- Validate Products structure
DESCRIBE products;

SHOW COLUMNS FROM orders;
-- 4. Check NULL values

-- Check NULL values in important order fields

SELECT
    COUNT(*) AS total_rows,
    SUM(customer_id IS NULL) AS null_customer_id,
    SUM(order_status IS NULL) AS null_order_status,
    SUM(payment_type IS NULL) AS null_payment_type,
    SUM(order_purchase_timestamp IS NULL) AS null_purchase_date
FROM orders;

SELECT
    COUNT(*) AS total_rows,
    SUM(order_id IS NULL) AS null_order_id,
    SUM(product_id IS NULL) AS null_product_id,
    SUM(quantity IS NULL) AS null_quantity,
    SUM(unit_price IS NULL) AS null_unit_price
FROM order_items;

-- 5. Check duplicate keys
-- Check duplicate order IDs

SELECT
    order_id,
    COUNT(*) AS duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Check duplicate product IDs

SELECT
    product_id,
    COUNT(*) AS duplicate_count
FROM products
GROUP BY product_id
HAVING COUNT(*) > 1;

-- 6. Validate table relationships
-- Find orders without a matching customer

SELECT COUNT(*) AS unmatched_orders
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Find order items without a matching order

SELECT COUNT(*) AS unmatched_order_items
FROM order_items oi
LEFT JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- Find order items without a matching product

SELECT COUNT(*) AS unmatched_products
FROM order_items oi
LEFT JOIN products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 7. Check numeric data quality
-- Check for invalid quantities and prices

SELECT
    COUNT(*) AS invalid_records
FROM order_items
WHERE quantity <= 0
   OR unit_price <= 0;
   
-- Check for invalid product prices

SELECT
    COUNT(*) AS invalid_records
FROM products
WHERE selling_price <= 0
   OR cost_price <= 0;
  
-- 9. Validate date range
-- Validate order purchase date range

SELECT
    MIN(order_purchase_timestamp) AS earliest_order,
    MAX(order_purchase_timestamp) AS latest_order
FROM orders;

-- SQL Query Foundations – Filtering, Sorting & Grouping

-- 1. Filtering with WHERE

-- Example 1: Find delivered orders
SELECT *
FROM orders
WHERE order_status = 'delivered';

-- Business interpretation:
-- This retrieves only successfully delivered orders.

-- Example 2: Find UPI orders
SELECT
    order_id,
    customer_id,
    payment_type
FROM orders
WHERE payment_type = 'UPI';

-- Interpretation:
-- Identifies customers who used UPI for their purchases.

-- Example 3: Find products above a certain selling price
SELECT
    product_id,
    Category_name,
    selling_price
FROM products
WHERE selling_price > 10000;

-- Interpretation:
-- Identifies higher-priced products that may contribute significantly to revenue.

-- 2. Multiple conditions with AND / OR

-- Example 4: Delivered orders paid using UPI
SELECT
    order_id,
    customer_id,
    payment_type,
    order_status
FROM orders
WHERE order_status = 'delivered'
  AND payment_type = 'UPI';
  

  
-- Example 5: Products from selected categories
SELECT
    product_id,
    Category_name,
    selling_price
FROM products
WHERE Category_name = 'art'
   OR Category_name = 'Electronics';
   
-- 3. Sorting with ORDER BY
-- Sorting arranges the result from highest to lowest or lowest to highest.
-- Example 6: Most expensive products
SELECT
    product_id,
    Category_name,
    selling_price
FROM products
ORDER BY selling_price DESC;

-- Example 7: Cheapest products first
SELECT
    product_id,
    Category_name,
    selling_price
FROM products
ORDER BY selling_price ASC;

-- 4. Limiting the results

-- Example 8: Top 10 highest-priced products
SELECT
    product_id,
    Category_name,
    selling_price
FROM products
ORDER BY selling_price DESC
LIMIT 10;

-- Interpretation:
-- Shows the 10 highest-priced products in the catalogue.

-- 5. Grouping with GROUP BY
-- GROUP BY is used to summarize records by a category.
-- Example 9: Number of orders by status
SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status;

-- This can show how many orders are:
-- delivered
-- shipped
-- cancelled
-- returned

-- Example 10: Orders by payment method
SELECT
    payment_type,
    COUNT(*) AS order_count
FROM orders
GROUP BY payment_type
ORDER BY order_count DESC;

-- Interpretation:
-- This identifies the most commonly used payment methods. You can use this to support your earlier observation that UPI is mostly used.

-- Example 11: Revenue by product category
SELECT
    p.Category_name,
    SUM(oi.unit_price * oi.quantity) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.Category_name
ORDER BY total_revenue DESC;

-- Interpretation:
-- This ranks product categories based on their total revenue contribution.


-- 6. Using HAVING
-- WHERE filters individual rows, while HAVING filters groups after aggregation.
-- Example 12: Categories generating more than ₹10 lakh
SELECT
    p.Category_name,
    SUM(oi.unit_price * oi.quantity) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.Category_name
HAVING SUM(oi.unit_price * oi.quantity) > 1000000
ORDER BY total_revenue DESC;

-- This identifies categories whose total revenue exceeds the selected threshold.