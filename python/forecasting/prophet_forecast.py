"""
Retail Sales Intelligence Platform — Meta Prophet Sales Forecasting Pipeline
Trains an additive univariate Prophet model on 20 clean historical months (Jan 2017 – Aug 2018),
evaluates using a 4-month time-based holdout backtest (May–Aug 2018),
and produces a 6-month forecast (Sep 2018 – Feb 2019) with 80% confidence bounds.
"""

import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from prophet import Prophet

def run_forecast(raw_dir='.', output_dir='powerbi_data'):
    print("=== Starting Meta Prophet Forecasting Pipeline ===")

    orders = pd.read_csv(os.path.join(raw_dir, 'olist_orders_dataset.csv'))
    order_items = pd.read_csv(os.path.join(raw_dir, 'olist_order_items_dataset.csv'))

    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M')

    merged = orders[['order_id', 'year_month']].merge(
        order_items[['order_id', 'price']], on='order_id', how='inner'
    )

    monthly_raw = merged.groupby('year_month')['price'].sum().reset_index()
    monthly_raw.columns = ['year_month', 'actual_sales']
    monthly_raw['year_month'] = monthly_raw['year_month'].astype(str)
    monthly_raw = monthly_raw.sort_values('year_month').reset_index(drop=True)

    # Exclude anomalous launch months (2016) and partial cut-off month (2018-09)
    monthly_clean = monthly_raw[
        (monthly_raw['year_month'] >= '2017-01') & 
        (monthly_raw['year_month'] <= '2018-08')
    ].copy().reset_index(drop=True)

    df_prophet = pd.DataFrame({
        'ds': pd.to_datetime(monthly_clean['year_month'] + '-01'),
        'y': monthly_clean['actual_sales']
    })

    # 1. Holdout Validation (16 Train / 4 Test)
    HOLDOUT_MONTHS = 4
    train_df = df_prophet.iloc[:-HOLDOUT_MONTHS].copy()
    test_df = df_prophet.iloc[-HOLDOUT_MONTHS:].copy()

    holdout_model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='additive',
        changepoint_prior_scale=0.3
    )
    holdout_model.fit(train_df)

    future_holdout = holdout_model.make_future_dataframe(periods=HOLDOUT_MONTHS, freq='MS')
    forecast_holdout = holdout_model.predict(future_holdout)

    test_pred = forecast_holdout[forecast_holdout['ds'].isin(test_df['ds'])][['ds', 'yhat']].merge(test_df, on='ds')

    mae = float(np.mean(np.abs(test_pred['y'] - test_pred['yhat'])))
    rmse = float(np.sqrt(np.mean((test_pred['y'] - test_pred['yhat'])**2)))
    mape = float(np.mean(np.abs((test_pred['y'] - test_pred['yhat']) / test_pred['y'])) * 100)
    acc_score = float(max(0.0, 100.0 - mape))

    print("Validation Metrics:")
    print(f"  MAE:               {mae:,.2f}")
    print(f"  RMSE:              {rmse:,.2f}")
    print(f"  MAPE:              {mape:.2f}%")
    print(f"  1 - MAPE Accuracy: {acc_score:.2f}%")

    # 2. Final Model (Trained on all 20 clean months)
    final_model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='additive',
        changepoint_prior_scale=0.3
    )
    final_model.fit(df_prophet)

    future_final = final_model.make_future_dataframe(periods=6, freq='MS')
    forecast_final = final_model.predict(future_final)

    last_actual_dt = pd.to_datetime('2018-08-01')
    forecast_future = forecast_final[forecast_final['ds'] > last_actual_dt][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

    # 3. Export Power BI Datasets
    historical_rows = [{
        'date': row['year_month'] + '-01',
        'actual_sales': round(row['actual_sales'], 2),
        'forecast_sales': None,
        'lower_bound': None,
        'upper_bound': None,
        'data_type': 'Actual'
    } for _, row in monthly_clean.iterrows()]

    forecast_rows = [{
        'date': row['ds'].strftime('%Y-%m-%d'),
        'actual_sales': None,
        'forecast_sales': round(row['yhat'], 2),
        'lower_bound': round(row['yhat_lower'], 2),
        'upper_bound': round(row['yhat_upper'], 2),
        'data_type': 'Forecast'
    } for _, row in forecast_future.iterrows()]

    export_df = pd.DataFrame(historical_rows + forecast_rows)
    os.makedirs(output_dir, exist_ok=True)
    export_df.to_csv(os.path.join(output_dir, 'forecast_sales.csv'), index=False)

    metrics_df = pd.DataFrame([
        {'metric': 'MAE', 'value': round(mae, 2), 'label': f"{mae:,.0f}"},
        {'metric': 'RMSE', 'value': round(rmse, 2), 'label': f"{rmse:,.0f}"},
        {'metric': 'MAPE', 'value': round(mape, 2), 'label': f"{mape:.2f}%"},
        {'metric': 'Forecast Accuracy Score', 'value': round(acc_score, 2), 'label': f"{acc_score:.2f}%"},
        {'metric': 'Historical Sales (Forecast)', 'value': round(monthly_clean['actual_sales'].sum(), 2), 'label': f"{monthly_clean['actual_sales'].sum()/1e6:.2f}M"},
        {'metric': 'Forecast Sales 6M', 'value': round(forecast_future['yhat'].sum(), 2), 'label': f"{forecast_future['yhat'].sum()/1e6:.2f}M"},
        {'metric': 'Forecast Horizon', 'value': 6, 'label': '6 Months'}
    ])
    metrics_df.to_csv(os.path.join(output_dir, 'forecast_metrics.csv'), index=False)

    print(f"Saved forecast datasets to '{output_dir}'.")
    print(f"6-Month Forecast Sum: {forecast_future['yhat'].sum():,.2f}")

if __name__ == '__main__':
    run_forecast()
