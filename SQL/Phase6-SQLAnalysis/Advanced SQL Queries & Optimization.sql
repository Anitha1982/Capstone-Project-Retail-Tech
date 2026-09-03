-- Advanced SQL Queries & Optimization 
-- Create Derived Tables for Modular Query Design
USE retailtech;

-- Example: Revenue by Customer
SELECT
    customer_id,
    total_revenue
FROM (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
) AS customer_sales
WHERE total_revenue > 10000
ORDER BY total_revenue DESC;

-- Category Performance
SELECT
    category_name,
    total_revenue
FROM (
    SELECT
        p.category_name,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p
        ON oi.product_id = p.product_id
    GROUP BY p.category_name
) AS category_sales
ORDER BY total_revenue DESC;

-- Use Stored Procedures to Automate Repeated Logic
DELIMITER //

CREATE PROCEDURE GetSegmentRevenue(IN segment_name VARCHAR(50))
BEGIN
    SELECT
        c.customer_segment,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.customer_id = o.customer_id
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
      AND c.customer_segment = segment_name
    GROUP BY c.customer_segment;
END //

DELIMITER ;

-- Execute the procedure
CALL GetSegmentRevenue('New');

-- Run it again for another segment without rewriting the entire query
CALL GetSegmentRevenue('Loyal');

-- Another example: Order Status Summary
DELIMITER //

CREATE PROCEDURE GetOrderStatusSummary()
BEGIN
    SELECT
        order_status,
        COUNT(*) AS total_orders
    FROM orders
    GROUP BY order_status
    ORDER BY total_orders DESC;
END //

DELIMITER ;

CALL GetOrderStatusSummary();

-- Implement Triggers for Controlled Database Actions
-- Example: Track Product Price Changes
-- create an audit table
CREATE TABLE product_price_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- create a trigger
DELIMITER //

CREATE TRIGGER after_product_price_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    IF OLD.selling_price <> NEW.selling_price THEN
        INSERT INTO product_price_audit (
            product_id,
            old_price,
            new_price
        )
        VALUES (
            OLD.product_id,
            OLD.selling_price,
            NEW.selling_price
        );
    END IF;
END //

DELIMITER ;

ALTER TABLE products
MODIFY product_id VARCHAR(50) NOT NULL;

ALTER TABLE products
ADD PRIMARY KEY (product_id);

-- Test the trigger
-- Update a product
UPDATE products
SET selling_price = 7500
WHERE product_id = 'P00001';

SELECT *
FROM product_price_audit;

-- Another trigger: Prevent Negative Stock
DELIMITER //

CREATE TRIGGER prevent_negative_stock
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.stock_availability < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock availability cannot be negative';
    END IF;
END //

DELIMITER ;

UPDATE products
SET stock_availability = -10
WHERE product_id = 'P00001';

-- Handle Exceptions for Reliable Query Execution
-- Example: Safely Update Product Price

DELIMITER //

DROP PROCEDURE IF EXISTS UpdateProductPrice //

CREATE PROCEDURE UpdateProductPrice(
    IN p_product_id VARCHAR(50),
    IN p_new_price DECIMAL(10,2)
)
BEGIN

    DECLARE v_product_count INT DEFAULT 0;

    -- Exception handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;

        SELECT
            'ERROR: Product price update failed.' AS message;
    END;

    -- Validate price
    IF p_new_price IS NULL OR p_new_price <= 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'ERROR: Selling price must be greater than zero';

    END IF;

    -- Check whether product exists
    SELECT COUNT(*)
    INTO v_product_count
    FROM products
    WHERE product_id = p_product_id;

    -- Throw exception if product does not exist
    IF v_product_count = 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'ERROR: Product ID does not exist';

    END IF;

    -- Start transaction
    START TRANSACTION;

    -- Update product price
    UPDATE products
    SET selling_price = p_new_price
    WHERE product_id = p_product_id;

    -- Commit successful transaction
    COMMIT;

    -- Success message
    SELECT
        'SUCCESS: Product price updated successfully.' AS message;

END //

DELIMITER ;

-- Execute the procedure
CALL UpdateProductPrice('P00001', 2860);
-- Test with a WRONG Product ID
CALL UpdateProductPrice('P001', 2860);
-- Test with an INVALID price
CALL UpdateProductPrice('P00001', -500);

