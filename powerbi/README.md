# Power BI Dashboard Implementation

This folder contains the production Power BI report file (`.pbix`) and the global corporate UI/UX JSON theme.

## Files
* `Retail_Sales_Intelligence_Platform.pbix`: Master 6-page interactive business intelligence dashboard.
* `AnalyticsPro_Theme.json`: Global theme file configuring colors, card elevations, visual borders, and typography.

## Dashboard Architecture (6 Pages)

| Page | Title | Core Objective |
|:---:|---|---|
| **1** | **Executive Overview** | Macro business health, revenue run-rate, volume KPIs, core delivery SLAs |
| **2** | **Sales & Regional Geography Analysis** | Geographic concentration matrix, state sales shares (SP/RJ/MG = 63.37%) |
| **3** | **Product & Seller Performance** | Category revenue leaders (Beleza Saúde #1) and seller partner distribution |
| **4** | **Customer & RFM Analysis** | Behavioral customer segmentation across 7 strategic tiers (93.36K customers) |
| **5** | **Delivery & Payment Performance** | Logistics SLA fulfillment (91.89% on-time) and credit card installment dynamics |
| **6** | **Sales Forecasting & Demand Planning** | Meta Prophet predictive forecasting (₹5.38M 6M forward) and holdout backtest |

## Design System & Palette
* **Executive Navy:** `#1A2B4A` (Headers, KPI callouts, actual series)
* **Cyber Teal:** `#00B4D8` (Primary analytical bars, volume callouts)
* **Warm Coral:** `#FF6B35` (Forecast projections, payment shares)
* **Emerald Green:** `#28A745` (On-time delivery SLA, high accuracy)
* **Crimson Red:** `#DC3545` (Late delivery SLA, at-risk alerts)
* **Canvas Background:** `#F4F6F9` (0% transparency Slate Neutral)
* **Cards & Containers:** `#FFFFFF` with 8px rounded corners and subtle drop shadows.

## Refreshing Data
1. Open `Retail_Sales_Intelligence_Platform.pbix` in Power BI Desktop.
2. If updating the underlying CSV data sources, go to **Home → Transform data → Data source settings** and update file paths to point to your local `powerbi_data/` folder.
3. Click **Home → Refresh**.
