-- ====================================================================
-- RETAIL SALES INTELLIGENCE PLATFORM — ANALYTICAL BENCHMARK QUERIES
-- Database: olist_dwh
-- ====================================================================

USE olist_dwh;

-- --------------------------------------------------------------------
-- 1. EXECUTIVE MACRO KPIs (Page 1 Baseline)
-- --------------------------------------------------------------------
SELECT 
    ROUND(SUM(price), 2) AS total_sales,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_unique_id) AS total_customers,
    COUNT(*) AS total_items,
    ROUND(SUM(price) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(SUM(price) / COUNT(*), 2) AS average_item_price
FROM fact_order_items;

-- --------------------------------------------------------------------
-- 2. REPEAT CUSTOMER RATE (Page 1)
-- --------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        customer_unique_id,
        COUNT(DISTINCT order_id) AS order_cnt
    FROM fact_order_items
    GROUP BY customer_unique_id
)
SELECT 
    COUNT(CASE WHEN order_cnt > 1 THEN 1 END) AS repeat_customers,
    COUNT(*) AS total_unique_customers,
    ROUND(COUNT(CASE WHEN order_cnt > 1 THEN 1 END) * 100.0 / COUNT(*), 2) AS repeat_customer_rate_pct
FROM customer_order_counts;

-- --------------------------------------------------------------------
-- 3. GEOGRAPHIC CONCENTRATION & TOP 3 STATES SHARE (Page 2)
-- --------------------------------------------------------------------
WITH state_sales AS (
    SELECT 
        customer_state,
        SUM(price) AS state_revenue,
        COUNT(DISTINCT order_id) AS state_orders,
        COUNT(*) AS state_items,
        ROUND(SUM(price) * 100.0 / (SELECT SUM(price) FROM fact_order_items), 2) AS revenue_share_pct,
        RANK() OVER (ORDER BY SUM(price) DESC) AS state_rank
    FROM fact_order_items
    GROUP BY customer_state
)
SELECT 
    customer_state,
    state_revenue,
    state_orders,
    state_items,
    revenue_share_pct,
    state_rank
FROM state_sales
WHERE state_rank <= 10
ORDER BY state_rank;

-- Top 3 States Share (SP, RJ, MG)
WITH state_sales AS (
    SELECT 
        customer_state,
        SUM(price) AS state_revenue,
        RANK() OVER (ORDER BY SUM(price) DESC) AS state_rank
    FROM fact_order_items
    GROUP BY customer_state
)
SELECT 
    ROUND(SUM(state_revenue) * 100.0 / (SELECT SUM(price) FROM fact_order_items), 2) AS top_3_states_share_pct
FROM state_sales
WHERE state_rank <= 3;

-- --------------------------------------------------------------------
-- 4. TOP PRODUCT CATEGORIES & SELLER PERFORMANCE (Page 3)
-- --------------------------------------------------------------------
-- Top 10 Product Categories by Revenue
SELECT 
    COALESCE(product_category_name, 'Uncategorized') AS category_name,
    ROUND(SUM(price), 2) AS total_revenue,
    COUNT(*) AS items_sold,
    ROUND(AVG(price), 2) AS avg_item_price
FROM fact_order_items
GROUP BY product_category_name
ORDER BY total_revenue DESC
LIMIT 10;

-- Top 10 Sellers by Revenue
SELECT 
    seller_id,
    ROUND(SUM(price), 2) AS total_sales,
    COUNT(DISTINCT order_id) AS seller_orders,
    COUNT(*) AS total_items,
    ROUND(AVG(price), 2) AS avg_item_price
FROM fact_order_items
GROUP BY seller_id
ORDER BY total_sales DESC
LIMIT 10;

-- --------------------------------------------------------------------
-- 5. LOGISTICS & DELIVERY SLA PERFORMANCE (Page 5)
-- --------------------------------------------------------------------
WITH delivered_orders AS (
    SELECT 
        order_id,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        order_purchase_timestamp,
        DATEDIFF(order_delivered_customer_date, order_purchase_timestamp) AS delivery_days,
        CASE 
            WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 'On Time / Early'
            ELSE 'Late'
        END AS sla_status
    FROM fact_order_items
    WHERE order_status = 'delivered' 
      AND order_delivered_customer_date IS NOT NULL
    GROUP BY order_id, order_delivered_customer_date, order_estimated_delivery_date, order_purchase_timestamp
)
SELECT 
    ROUND(AVG(delivery_days), 2) AS average_delivery_days,
    ROUND(COUNT(CASE WHEN sla_status = 'On Time / Early' THEN 1 END) * 100.0 / COUNT(*), 2) AS on_time_early_pct,
    ROUND(COUNT(CASE WHEN sla_status = 'Late' THEN 1 END) * 100.0 / COUNT(*), 2) AS late_pct,
    COUNT(*) AS delivered_order_count
FROM delivered_orders;

-- --------------------------------------------------------------------
-- 6. PAYMENT DYNAMICS & INSTALLMENT DISTRIBUTION (Page 5)
-- --------------------------------------------------------------------
SELECT 
    payment_type,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(SUM(payment_value) * 100.0 / (SELECT SUM(payment_value) FROM fact_payments), 2) AS payment_value_share_pct,
    COUNT(*) AS transaction_count
FROM fact_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;

-- Credit Card Installments Breakdown
SELECT 
    payment_installments,
    ROUND(SUM(payment_value), 2) AS installment_sales,
    COUNT(*) AS payment_count
FROM fact_payments
WHERE payment_type = 'credit_card'
GROUP BY payment_installments
ORDER BY payment_installments;

-- --------------------------------------------------------------------
-- 7. RFM SEGMENT REVENUE CONTRIBUTION (Page 4)
-- --------------------------------------------------------------------
SELECT 
    segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_rfm), 2) AS customer_share_pct,
    ROUND(SUM(monetary), 2) AS segment_revenue,
    ROUND(SUM(monetary) * 100.0 / (SELECT SUM(monetary) FROM customer_rfm), 2) AS revenue_share_pct,
    ROUND(AVG(monetary), 2) AS avg_monetary_per_customer
FROM customer_rfm
GROUP BY segment
ORDER BY segment_revenue DESC;
