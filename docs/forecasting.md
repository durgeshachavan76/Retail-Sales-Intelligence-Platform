# Sales Forecasting & Demand Planning Methodology

## 1. Problem Statement
Descriptive reporting analyzes historical transactions. To support proactive demand planning, inventory allocation, and sales targets, this project implements a **predictive time-series forecasting model** using Meta's Prophet library.

## 2. Dataset Preparation & Cleaning
* **Grain:** Monthly aggregate sales (`price` column across all orders).
* **Raw Period:** September 2016 – September 2018 (24 months).
* **Data Cleaning & Exclusions:**
  * `2016-09`, `2016-10`, `2016-12`: Excluded due to platform launch ramp-up and missing data anomalies (< ₹500 total).
  * `2018-09`: Excluded due to mid-month dataset cutoff (only ₹145 recorded).
  * **Clean Modeling Window:** **20 continuous months** (January 2017 – August 2018), totaling **₹13,541,712.78**.

## 3. Prophet Model Architecture
```python
from prophet import Prophet

model = Prophet(
    yearly_seasonality=False,      # < 2 full years of data; avoids trend overfitting
    weekly_seasonality=False,      # Monthly data grain
    daily_seasonality=False,       # Monthly data grain
    seasonality_mode='additive',   # Additive variance over growth regime
    changepoint_prior_scale=0.3    # Captures transition from 2017 surge to 2018 plateau
)
```

### Rationale for Hyperparameters
* **`yearly_seasonality=False`:** Fitting annual Fourier series requires at least 2 complete cycles (24+ months). Enforcing yearly seasonality on 20 months creates unstable overfitted oscillations.
* **`changepoint_prior_scale=0.3`:** Balances trend flexibility against sudden noise, accurately modeling the transition from rapid 2017 platform growth to the mature 2018 plateau.

## 4. Time-Based Holdout Backtesting (Evaluation)
To evaluate out-of-sample predictive validity without data leakage, we employed a strict chronological split:
* **Training Set:** January 2017 – April 2018 (16 months).
* **Test Holdout Set:** May 2018 – August 2018 (4 unseen months).

### Validation Results
| Holdout Month | Actual Sales | Predicted Sales | Absolute Error | Percentage Error |
|:---:|---:|---:|---:|---:|
| **2018-05** | ₹9,96,518 | ₹1,078,256 | ₹81,738 | 8.20% |
| **2018-06** | ₹8,65,124 | ₹1,130,417 | ₹2,65,293 | 30.67% |
| **2018-07** | ₹8,95,507 | ₹1,180,895 | ₹2,85,388 | 31.87% |
| **2018-08** | ₹8,54,686 | ₹1,233,055 | ₹3,78,369 | 44.27% |

### Out-of-Sample Error Metrics
* **MAE (Mean Absolute Error):** **₹252,696.96** (`₹252.70K`)
* **RMSE (Root Mean Squared Error):** **₹274,622.76** (`₹274.62K`)
* **MAPE (Mean Absolute Percentage Error):** **28.75%**
* **1 − MAPE Accuracy Score:** **71.25%**

## 5. 6-Month Forward Forecast (Sep 2018 – Feb 2019)
Trained on all 20 clean historical months:

| Forecast Month | Point Forecast ($\hat{y}$) | 80% Lower Bound | 80% Upper Bound |
|:---|---:|---:|---:|
| **Sep 2018** | ₹9,08,587.82 | ₹8,07,547.98 | ₹9,98,995.51 |
| **Oct 2018** | ₹9,03,888.30 | ₹8,11,838.22 | ₹10,05,911.99 |
| **Nov 2018** | ₹8,99,032.12 | ₹7,94,636.47 | ₹9,94,536.42 |
| **Dec 2018** | ₹8,94,332.60 | ₹7,86,899.33 | ₹9,92,362.51 |
| **Jan 2019** | ₹8,89,476.42 | ₹7,85,219.47 | ₹9,94,513.55 |
| **Feb 2019** | ₹8,84,620.25 | ₹7,79,159.24 | ₹9,90,951.18 |
| **Total 6M** | **₹53,79,937.51** | **₹47,65,300.71** | **₹59,77,271.16** |

## 6. Analytical Limitations & Future Scope
1. **Univariate Limitation:** The model relies solely on historical sales signals. Adding external regressors (marketing spend, promotional calendars, Brazilian holiday dates) would reduce over-prediction bias during market regime shifts.
2. **Horizon Length:** Limited historical depth restricts reliable long-range forecasting beyond 6 months.
