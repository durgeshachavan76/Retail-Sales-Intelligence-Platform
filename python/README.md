# Python Data Processing & Forecasting Pipeline

This directory contains modularized Python scripts powering the ETL star schema creation, RFM customer segmentation, and Meta Prophet time-series sales forecasting.

## Architecture
```
python/
├── data_preparation/
│   └── build_star_schema.py    # Merges raw datasets, cleans anomalies, builds dimensional tables
├── rfm_analysis/
│   └── rfm_segmentation.py     # Calculates R/F/M quintiles and assigns 7 behavioral segments
└── forecasting/
    └── prophet_forecast.py     # Meta Prophet 6M forecasting with 4-month holdout backtesting
```

## Running the Pipeline
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build star schema dimensional tables
python python/data_preparation/build_star_schema.py

# 3. Perform RFM customer segmentation
python python/rfm_analysis/rfm_segmentation.py

# 4. Train Prophet forecasting model and evaluate holdout backtest
python python/forecasting/prophet_forecast.py
```
