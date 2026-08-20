# Case Study: Analyze E-Commerce Sales to Improve Customer Conversion & Retention (RetailTech)

## Case Description
This case study analyzes end-to-end e-commerce data to uncover key factors that influence **customer conversion** and **repeat purchases** across different product categories and customer segments. The goal is to provide insights for optimizing marketing strategies, pricing, inventory, and overall customer experience.

---

## Data Overview
The dataset simulates a comprehensive Indian e-commerce ecosystem between **April 2021 and September 2025**, covering customers, products, orders, reviews, and geolocations.

| Table Name | Description | Total Records |
|-------------|--------------|----------------|
| **Customers_dataset** | Contains demographic and segmentation information for customers across India. | 90,000 |
| **Geolocation_dataset** | Lists city-wise postal codes, latitude, longitude, and region mappings across Indian states. | 155,545 |
| **Products_dataset** | Provides details about products sold, including pricing, category, subcategory, and stock availability. | 32,951 |
| **Orders_dataset** | Contains transactional details of customer orders with timestamps and payment modes. | 99,999 |
| **Order_items_dataset** | Line-item level details for each order, including product quantity, discounts, and shipping cost. | 150,000 |
| **Order_reviews_dataset** | Customer feedback dataset containing review scores, comments, and review dates. | 97,019 |

---

## Data Dictionary

### 1. Customers_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `customer_id` | Unique identifier for each customer | C00001 |
| `customer_zip_code` | Customer’s postal code | 690511 |
| `gender` | Gender of customer (`Male` / `Female`) | Female |
| `age_group` | Age bracket of customer | 36-45 |
| `customer_segment` | Customer loyalty group (`New`, `Returning`, `Loyal`) | Loyal |

---

### 2. Geolocation_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `geolocation_zip_code` | Postal code | 744301 |
| `geolocation_city` | City or town name | Carnicobar |
| `geolocation_state` | Indian state name | Andaman & Nicobar Islands |
| `geolocation_lat` | Latitude coordinate | 9.1833 |
| `geolocation_lng` | Longitude coordinate | 92.7667 |
| `region` | Regional classification (`North`, `South`, `East`, `West`, `Central`) | East |

---

### 3. Products_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `product_id` | Unique product identifier | P00001 |
| `Category_name` | Main product category | perfumery |
| `sub_category_name` | Sub-category or product type | Fragrances |
| `product_weight_g` | Product weight (in grams) | 225 |
| `brand` | Brand name | Nivea |
| `cost_price` | Product cost price (₹) | 2200 |
| `selling_price` | Product selling price (₹) | 2860 |
| `stock_availability` | Inventory status (`In Stock`, `Low Stock`, `Preorder`, etc.) | In Stock |

---

### 4. Orders_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `order_id` | Unique order identifier | O00001 |
| `customer_id` | Customer reference ID | C60210 |
| `order_status` | Order stage (`delivered`, `shipped`, `returned`, `cancelled`) | delivered |
| `payment_type` | Payment method used | Net Banking |
| `order_purchase_timestamp` | Date of order placement | 04/11/2024 |
| `order_approved_at` | Date order was approved | 04/11/2024 |
| `order_delivered_shipping_date` | Date item was shipped | 01/12/2024 |
| `order_delivered_customer_date` | Date order was delivered to customer | 04/03/2025 |
| `order_estimated_delivery_date` | Expected delivery date | 03/01/2025 |

---

### 5. Order_items_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `order_item_id` | Unique order-item identifier | OI000001 |
| `order_id` | Reference to order ID | O00001 |
| `quantity` | Number of product units | 1 |
| `product_id` | Product reference ID | P28355 |
| `unit_price` | Selling price of the product (₹) | 7020 |
| `discount(%)` | Discount applied on product | 6.54 |
| `shipping_cost` | Shipping cost for the product | 713.72 |

---

### 6. Order_reviews_dataset
| Column | Description | Example |
|---------|--------------|----------|
| `review_id` | Unique review identifier | R00001 |
| `order_id` | Reference to order ID | O41195 |
| `review_score` | Customer rating (1–5) | 5 |
| `review_comment_message` | Text feedback from customer | Very satisfied with the purchase. |
| `review_date` | Date of review submission | 06/07/2025 |

---

## Notes

- All datasets are interlinked by **primary/foreign keys** (e.g., `order_id`, `product_id`, `customer_id`).
- Dates are stored in **DD/MM/YYYY** format without timestamps.
- Product, customer, and order volumes are designed to simulate **realistic Indian e-commerce behavior** (with seasonality and loyalty trends).
- Geolocation data covers **all Indian states and major cities**, ensuring regional diversity for analysis.

---

## Use Case Summary
This dataset can be used to perform:
- **Customer segmentation and retention analysis**  
- **Sales and profitability insights** across categories and demographics  
- **Product performance and pricing strategy optimization**  
- **Shipping and logistics cost analysis**  
- **Customer satisfaction and review sentiment analysis**