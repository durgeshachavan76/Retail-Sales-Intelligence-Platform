# Dimensional Data Model Architecture

The data architecture is structured as an analytical **Star Schema** optimized for high-performance Power BI DAX queries and dimensional slicing.

## Star Schema Overview

```
                      ┌────────────────────────┐
                      │      dim_date          │
                      │  (1 row per day)       │
                      └──────────┬─────────────┘
                                 │ 1:N
                                 ▼
┌──────────────────┐    ┌────────────────────────┐    ┌──────────────────┐
│   dim_customer   │    │    fact_order_items    │    │   dim_product    │
│ (1 row / cust)   ├───►│ (1 row per order item) │◄───┤ (1 row / product)│
└──────────────────┘1:N └──────────▲─────────────┘ 1:N└──────────────────┘
                                   │ 1:N
                        ┌──────────┴─────────────┐
                        │       dim_seller       │
                        │   (1 row per seller)   │
                        └────────────────────────┘

Auxiliary Tables:
- fact_payments (Grain: 1 row per payment sequence per order)
- customer_rfm (Grain: 1 row per unique customer, 93,358 records)
- forecast_sales (Standalone time series: 20 actuals + 6 forecast months)
```

## Table Specifications

### 1. `fact_order_items` (Fact Table)
* **Grain:** 1 record per order item (112,650 rows total).
* **Key Columns:** `order_id`, `order_item_id`, `customer_id`, `product_id`, `seller_id`, `order_purchase_timestamp`, `price`, `freight_value`.
* **Degenerate Dimensions:** `order_status`, `customer_city`, `customer_state`, `product_category_name`.

### 2. `fact_payments` (Fact Table)
* **Grain:** 1 record per payment sequence per order (103,886 rows).
* **Key Columns:** `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`.

### 3. `dim_customer` (Dimension Table)
* **Grain:** 1 record per customer ID (99,441 rows mapped to 96,096 unique customer identifiers).
* **Key Columns:** `customer_id`, `customer_unique_id`, `customer_city`, `customer_state`.

### 4. `dim_product` (Dimension Table)
* **Grain:** 1 record per product ID (32,951 products).
* **Key Columns:** `product_id`, `product_category_name`, physical specs.

### 5. `dim_seller` (Dimension Table)
* **Grain:** 1 record per marketplace seller (3,095 sellers).
* **Key Columns:** `seller_id`, `seller_city`, `seller_state`.

### 6. `dim_date` (Dimension Table)
* **Grain:** Continuous daily calendar spanning September 2016 through October 2018 (773 days).
* **Key Columns:** `date`, `year`, `month_number`, `month_name`, `year_month`.

### 7. `customer_rfm` (Analytical Dimension)
* **Grain:** 1 record per unique customer (93,358 customers with delivered orders).
* **Key Columns:** `customer_unique_id`, `recency`, `frequency`, `monetary`, `R_score`, `F_score`, `M_score`, `segment`.

### 8. `forecast_sales` (Predictive Table)
* **Grain:** 1 record per calendar month (26 months: 20 historical actuals + 6 future projections).
* **Key Columns:** `date`, `actual_sales`, `forecast_sales`, `lower_bound`, `upper_bound`, `data_type`.
