# Data Dictionary & Ingestion Guide

This project analyzes the public Brazilian E-Commerce dataset provided by Olist on Kaggle.

## Source Dataset Overview
The raw dataset contains ~100k real anonymized orders placed between September 2016 and September 2018 on the Olist marketplace.

| Raw File Name | Description | Key Fields |
|---|---|---|
| `olist_orders_dataset.csv` | Order timestamps and status | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp` |
| `olist_order_items_dataset.csv` | Item-level transaction details | `order_id`, `order_item_id`, `product_id`, `seller_id`, `price`, `freight_value` |
| `olist_customers_dataset.csv` | Customer location and unique IDs | `customer_id`, `customer_unique_id`, `customer_city`, `customer_state` |
| `olist_products_dataset.csv` | Product category and specifications | `product_id`, `product_category_name`, `product_weight_g` |
| `olist_sellers_dataset.csv` | Seller location data | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` |
| `olist_order_payments_dataset.csv` | Payment transaction records | `order_id`, `payment_type`, `payment_installments`, `payment_value` |
| `olist_order_reviews_dataset.csv` | Customer review ratings | `order_id`, `review_score`, `review_comment_message` |
| `olist_geolocation_dataset.csv` | Zip code coordinates | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng` |

## How to Obtain and Setup Data
1. Download the dataset from [Kaggle: Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
2. Place the raw CSV files in the project root directory.
3. Run the ETL pipeline:
   ```bash
   python python/data_preparation/build_star_schema.py
   python python/rfm_analysis/rfm_segmentation.py
   python python/forecasting/prophet_forecast.py
   ```
4. Transformed dimensional tables will be populated inside `powerbi_data/`. Schema samples are provided in `data/sample/`.
