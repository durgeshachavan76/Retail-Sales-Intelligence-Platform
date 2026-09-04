"""
Retail Sales Intelligence Platform — RFM Customer Segmentation
Calculates Recency, Frequency, and Monetary metrics for 93,358 customers,
computes R, F, M quintiles, and segments customers into 7 strategic behavioral tiers.
"""

import os
import pandas as pd
import numpy as np

def run_rfm(raw_dir='.', output_dir='powerbi_data'):
    print("=== Starting RFM Customer Segmentation Pipeline ===")
    orders = pd.read_csv(os.path.join(raw_dir, 'olist_orders_dataset.csv'))
    order_items = pd.read_csv(os.path.join(raw_dir, 'olist_order_items_dataset.csv'))
    customers = pd.read_csv(os.path.join(raw_dir, 'olist_customers_dataset.csv'))

    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

    # Merge delivered orders only for customer transaction analysis
    delivered = orders[orders['order_status'] == 'delivered'].merge(
        customers[['customer_id', 'customer_unique_id']], on='customer_id', how='inner'
    ).merge(
        order_items[['order_id', 'price']], on='order_id', how='inner'
    )

    # Order level aggregation
    order_level = delivered.groupby(['order_id', 'customer_unique_id', 'order_purchase_timestamp'])['price'].sum().reset_index()

    snapshot_date = order_level['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    # RFM Aggregation per Unique Customer
    rfm = order_level.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum')
    ).reset_index()

    # Recency Score (1-5, lower recency days = higher score)
    rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)

    # Frequency Score (Discrete binning matching notebook)
    def frequency_score(x):
        if x == 1:
            return 1
        elif x == 2:
            return 2
        elif x == 3:
            return 3
        elif x == 4:
            return 4
        else:
            return 5

    rfm['F_score'] = rfm['frequency'].apply(frequency_score)

    # Monetary Score (1-5, higher spend = higher score)
    rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Combined RFM Score
    rfm['RFM_score'] = (
        rfm['R_score'].astype(str) + 
        rfm['F_score'].astype(str) + 
        rfm['M_score'].astype(str)
    ).astype(int)

    # Strategic Segment Mapping (Exact match to exploratory notebook)
    def rfm_segment(row):
        r = row['R_score']
        f = row['F_score']
        m = row['M_score']

        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 2 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f >= 2:
            return 'Potential Loyalists'
        elif r >= 3 and m >= 4:
            return 'Big Spenders'
        elif r >= 4 and f == 1:
            return 'New Customers'
        elif r <= 2 and f >= 2:
            return 'At Risk'
        else:
            return 'Lost Customers'

    rfm['segment'] = rfm.apply(rfm_segment, axis=1)

    os.makedirs(output_dir, exist_ok=True)
    rfm.to_csv(os.path.join(output_dir, 'customer_rfm.csv'), index=False)

    print(f"RFM Complete: Segmented {len(rfm):,} unique customers.")
    print(f"Total Monetary: {rfm['monetary'].sum():,.2f}")
    print("\nSegment Distribution:")
    summary = rfm.groupby('segment').agg(
        customers=('customer_unique_id', 'count'),
        monetary=('monetary', 'sum')
    ).reset_index()
    summary['sales_pct'] = summary['monetary'] / rfm['monetary'].sum() * 100
    print(summary.to_string(index=False))

if __name__ == '__main__':
    run_rfm()
