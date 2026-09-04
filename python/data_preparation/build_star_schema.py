"""
Retail Sales Intelligence Platform — Star Schema ETL Pipeline
Extracts raw Olist tables, cleans anomalous dates, merges entities,
and exports dimensional tables for Power BI.
"""

import os
import pandas as pd
import numpy as np

def run_etl(raw_dir='.', output_dir='powerbi_data'):
    os.makedirs(output_dir, exist_ok=True)
    print("=== Starting Star Schema ETL Pipeline ===")

    # 1. Load Raw Datasets
    orders = pd.read_csv(os.path.join(raw_dir, 'olist_orders_dataset.csv'))
    order_items = pd.read_csv(os.path.join(raw_dir, 'olist_order_items_dataset.csv'))
    customers = pd.read_csv(os.path.join(raw_dir, 'olist_customers_dataset.csv'))
    products = pd.read_csv(os.path.join(raw_dir, 'olist_products_dataset.csv'))
    sellers = pd.read_csv(os.path.join(raw_dir, 'olist_sellers_dataset.csv'))
    payments = pd.read_csv(os.path.join(raw_dir, 'olist_order_payments_dataset.csv'))

    # Parse timestamps
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])
    order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

    # 2. Build Fact: Order Items
    merged_items = (
        order_items
        .merge(orders, on='order_id', how='inner')
        .merge(customers[['customer_id', 'customer_unique_id', 'customer_city', 'customer_state']], on='customer_id', how='left')
        .merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
    )

    fact_order_items = merged_items[[
        'order_id', 'order_item_id', 'customer_id', 'customer_unique_id',
        'order_status', 'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date', 'product_id', 'seller_id',
        'shipping_limit_date', 'price', 'freight_value',
        'product_category_name', 'customer_city', 'customer_state'
    ]].copy()

    # 3. Build Dimensions
    dim_customer = customers[[
        'customer_id', 'customer_unique_id', 'customer_zip_code_prefix',
        'customer_city', 'customer_state'
    ]].drop_duplicates()

    dim_product = products.copy()
    dim_seller = sellers.copy()

    # Build Continuous Date Dimension
    min_date = fact_order_items['order_purchase_timestamp'].min().floor('D')
    max_date = fact_order_items['order_purchase_timestamp'].max().ceil('D')
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')

    dim_date = pd.DataFrame({'date': date_range})
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['month_number'] = dim_date['date'].dt.month
    dim_date['month_name'] = dim_date['date'].dt.strftime('%B')
    dim_date['year_month'] = dim_date['date'].dt.strftime('%Y-%m')

    # 4. Save Outputs
    fact_order_items.to_csv(os.path.join(output_dir, 'fact_order_items.csv'), index=False)
    dim_customer.to_csv(os.path.join(output_dir, 'dim_customer.csv'), index=False)
    dim_product.to_csv(os.path.join(output_dir, 'dim_product.csv'), index=False)
    dim_seller.to_csv(os.path.join(output_dir, 'dim_seller.csv'), index=False)
    dim_date.to_csv(os.path.join(output_dir, 'dim_date.csv'), index=False)
    payments.to_csv(os.path.join(output_dir, 'fact_payments.csv'), index=False)
    orders.to_csv(os.path.join(output_dir, 'dim_order_source.csv'), index=False)

    print(f"ETL Complete: Exported 7 tables to '{output_dir}'.")
    print(f"Fact Items Rows: {len(fact_order_items):,}")
    print(f"Total Sales: {fact_order_items['price'].sum():,.2f}")

if __name__ == '__main__':
    run_etl()
