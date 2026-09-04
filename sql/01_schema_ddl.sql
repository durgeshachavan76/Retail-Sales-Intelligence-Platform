-- ====================================================================
-- RETAIL SALES INTELLIGENCE PLATFORM — STAR SCHEMA DDL (MySQL)
-- Database: olist_dwh
-- ====================================================================

CREATE DATABASE IF NOT EXISTS olist_dwh;
USE olist_dwh;

-- --------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- --------------------------------------------------------------------

-- Customer Dimension
DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state CHAR(2) NOT NULL,
    INDEX idx_customer_state (customer_state),
    INDEX idx_customer_unique (customer_unique_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Product Dimension
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    product_id VARCHAR(32) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    INDEX idx_product_category (product_category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seller Dimension
DROP TABLE IF EXISTS dim_seller;
CREATE TABLE dim_seller (
    seller_id VARCHAR(32) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state CHAR(2) NOT NULL,
    INDEX idx_seller_state (seller_state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Date Dimension
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INT NOT NULL,
    month_number INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month CHAR(7) NOT NULL,
    INDEX idx_year (year),
    INDEX idx_year_month (year_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------------------
-- 2. FACT TABLES
-- --------------------------------------------------------------------

-- Fact: Order Items (Grain: 1 row per order item)
DROP TABLE IF EXISTS fact_order_items;
CREATE TABLE fact_order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp DATETIME NOT NULL,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    shipping_limit_date DATETIME,
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    product_category_name VARCHAR(100),
    customer_city VARCHAR(100),
    customer_state CHAR(2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    INDEX idx_order_purchase_dt (order_purchase_timestamp),
    INDEX idx_fact_customer (customer_id),
    INDEX idx_fact_product (product_id),
    INDEX idx_fact_seller (seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fact: Payments (Grain: 1 row per payment sequence per order)
DROP TABLE IF EXISTS fact_payments;
CREATE TABLE fact_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    INDEX idx_payment_type (payment_type),
    INDEX idx_payment_installments (payment_installments)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dimension / Fact: Customer RFM Segmentation
DROP TABLE IF EXISTS customer_rfm;
CREATE TABLE customer_rfm (
    customer_unique_id VARCHAR(32) PRIMARY KEY,
    recency INT NOT NULL,
    frequency INT NOT NULL,
    monetary DECIMAL(12, 2) NOT NULL,
    R_score INT NOT NULL,
    F_score INT NOT NULL,
    M_score INT NOT NULL,
    RFM_score INT NOT NULL,
    segment VARCHAR(50) NOT NULL,
    INDEX idx_rfm_segment (segment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
