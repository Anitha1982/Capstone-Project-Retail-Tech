USE retailtech;
-- Joins and Sub-Queries 
-- Apply Inner, left, right joins to integrate related tables
-- 1. INNER JOIN — matching records only
-- Use INNER JOIN when we want records that exist in both tables.
-- Get customer details for each order
SELECT
    o.order_id,
    o.customer_id,
    c.gender,
    c.age_group,
    c.customer_segment,
    o.order_status,
    o.payment_type
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id;
    
-- Business use:
-- Understand which customer segments are associated with different orders.
    
-- 2. LEFT JOIN — keep all records from the left table
-- Use LEFT JOIN when we want all orders, even if customer information is missing.
-- Keep every order and attach customer information
SELECT
    o.order_id,
    o.customer_id,
    c.customer_segment,
    c.gender,
    o.order_status
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id;
    
-- Business use:
-- Check whether every order has a corresponding customer record.
    
-- Identify Unmatched Customers
SELECT
    o.order_id,
    o.customer_id
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 3. RIGHT JOIN — keep all records from the right table
-- RIGHT JOIN keeps all records from the right-side table.
-- Keep every customer and show their orders when available
SELECT
    c.customer_id,
    c.customer_segment,
    o.order_id,
    o.order_status
FROM orders AS o
RIGHT JOIN customers AS c
    ON o.customer_id = c.customer_id;
    
-- Business use:
-- Identify customers who may not have placed an order.
    
SELECT
    c.customer_id,
    c.customer_segment
FROM orders AS o
RIGHT JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- 4. JOIN multiple tables
-- This is especially important for your project because Orders and Order Items contain different parts of the sales information.
-- Combine orders, order items and products
SELECT
    o.order_id,
    o.customer_id,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    oi.`discount(%)`,
    p.category_name,
    p.brand
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
INNER JOIN products AS p
    ON oi.product_id = p.product_id;

-- This creates an analytical dataset containing:
-- Customer → Order → Product → Sales details

-- 5. JOIN + calculated revenue
SELECT
    o.order_id,
    oi.product_id,
    p.category_name,
    oi.quantity,
    oi.unit_price,
    oi.`discount(%)`,
    oi.quantity * oi.unit_price AS gross_revenue
FROM orders AS o
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
INNER JOIN products AS p
    ON oi.product_id = p.product_id;
    
-- 6. JOIN + GROUP BY
-- Which category generates the highest revenue?

SELECT
    p.category_name,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
GROUP BY p.category_name
ORDER BY total_revenue DESC;

-- Insight: Identifies which product categories generate the highest revenue.

-- Revenue by Customer Segment
SELECT
    c.customer_segment,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- Insight: Shows which customer segment contributes the most revenue.

-- Revenue By Brand
SELECT
    p.brand,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
GROUP BY p.brand
ORDER BY total_revenue DESC;

-- Insight: Identifies the highest-revenue brands.

-- Category Performance — Revenue and Quantity
SELECT
    p.category_name,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    ROUND(AVG(oi.unit_price), 2) AS avg_unit_price
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
GROUP BY p.category_name
ORDER BY total_revenue DESC;

-- Orders by Status and Customer Segment
SELECT
    c.customer_segment,
    o.order_status,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_segment,
    o.order_status
ORDER BY
    c.customer_segment,
    total_orders DESC;
    
-- Insight: Shows how order outcomes differ across customer segments.

-- Revenue and order performance by customer segment
SELECT
    c.customer_segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price) /
        COUNT(DISTINCT o.order_id),
        2
    ) AS avg_order_value
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- 7. SUBQUERY
-- A subquery is a query inside another query.
-- Example: Orders with above-average order value
-- First calculate each order's value:

SELECT
    order_id,
    SUM(quantity * unit_price) AS order_value
FROM order_items
GROUP BY order_id;

-- use a subquery to find orders above the average:
SELECT
    order_id,
    order_value
FROM
(
    SELECT
        order_id,
        SUM(quantity * unit_price) AS order_value
    FROM order_items
    GROUP BY order_id
) AS order_summary
WHERE order_value >
(
    SELECT AVG(order_value)
    FROM
    (
        SELECT
            order_id,
            SUM(quantity * unit_price) AS order_value
        FROM order_items
        GROUP BY order_id
    ) AS order_values
);

-- 8. Another useful subquery 
-- Find products whose selling price is above the average selling price

SELECT
    product_id,
    category_name,
    selling_price
FROM products
WHERE selling_price >
(
    SELECT AVG(selling_price)
    FROM products
)
ORDER BY selling_price DESC;
-- Business question:
-- Which products are priced above the overall average selling price?

-- 1. CTE – Customer Spending Segmentation
-- Purpose: Calculate each customer's total spending and classify them into High, Medium, and Low-value customers.

WITH customer_spending AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS total_spending
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    total_spending,
    CASE
        WHEN total_spending >= 50000 THEN 'High Value'
        WHEN total_spending >= 20000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_value_segment
FROM customer_spending
ORDER BY total_spending DESC;

-- Business insight: Identifies customers who contribute the most revenue.
-- Action: Target high-value customers with loyalty programs and personalized offers.

-- 2. CTE – Category Revenue Ranking
-- Purpose: Calculate revenue by product category and rank categories from highest to lowest revenue.

WITH category_revenue AS (
    SELECT
        p.Category_name,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p
        ON oi.product_id = p.product_id
    INNER JOIN orders AS o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.Category_name
)
SELECT
    Category_name,
    total_revenue,
    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM category_revenue
ORDER BY revenue_rank;

-- Furniture generated the highest revenue among product categories, making it a key contributor to overall sales performance.
-- Action: Maintain sufficient inventory and consider targeted promotions for high-performing categories

-- 3. CTE – Repeat Purchase Analysis
-- Purpose: Identify customers who have placed multiple orders and calculate their total revenue contribution.

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
),
customer_revenue AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT
    co.customer_id,
    co.total_orders,
    cr.total_revenue,
    CASE
        WHEN co.total_orders > 1 THEN 'Repeat Customer'
        ELSE 'One-Time Customer'
    END AS customer_type
FROM customer_orders AS co
INNER JOIN customer_revenue AS cr
    ON co.customer_id = cr.customer_id
ORDER BY co.total_orders DESC, cr.total_revenue DESC;

-- Customers with multiple purchases were identified using order-history data, allowing repeat-purchase behaviour to be compared with revenue contribution.
-- Action: Develop retention campaigns and personalized offers to encourage one-time customers to make additional purchases.

-- a monthly cumulative revenue analysis
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_month,
        SUM(oi.quantity * oi.unit_price) AS monthly_revenue
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT
    order_month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (
        ORDER BY order_month
    ) AS running_total_revenue
FROM monthly_revenue
ORDER BY order_month;

-- The running total keeps adding each month's revenue to the previous months.
-- Running totals were calculated using the SUM() OVER() window function to track cumulative revenue over time. This helps identify how revenue accumulates across the analysis period and supports evaluation of overall sales growth.