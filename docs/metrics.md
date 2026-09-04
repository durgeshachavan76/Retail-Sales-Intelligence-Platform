# Business Glossary & DAX Measures Reference

All calculations across the 6 dashboard pages are formalized in explicit DAX measures.

---

## 1. Executive Overview & Sales Metrics (Pages 1–3)

### Total Sales
```dax
Total Sales = 
SUM(fact_order_items[price])
```
* **Validated Benchmark:** ₹13,591,643.70 (₹13.59M)
* **Description:** Sum of item prices across all orders.

### Total Orders
```dax
Total Orders = 
DISTINCTCOUNT(fact_order_items[order_id])
```
* **Validated Benchmark:** 99,441 (99.44K)

### Total Customers
```dax
Total Customers = 
DISTINCTCOUNT(dim_customer[customer_unique_id])
```
* **Validated Benchmark:** 96,096 (96.10K)

### Total Items
```dax
Total Items = 
COUNTROWS(fact_order_items)
```
* **Validated Benchmark:** 112,650 (112.65K)

### Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE([Total Sales], [Total Orders], 0)
```
* **Validated Benchmark:** ₹137.75

### Average Item Price
```dax
Average Item Price = 
DIVIDE([Total Sales], [Total Items], 0)
```
* **Validated Benchmark:** ₹120.65

### Repeat Customer Rate
```dax
Repeat Customer Rate = 
VAR CustomerOrders =
    ADDCOLUMNS(
        VALUES(dim_customer[customer_unique_id]),
        "OrderCount", CALCULATE(DISTINCTCOUNT(fact_order_items[order_id]))
    )
VAR RepeatCount =
    COUNTROWS(FILTER(CustomerOrders, [OrderCount] > 1))
VAR TotalUnique =
    COUNTROWS(CustomerOrders)
RETURN
    DIVIDE(RepeatCount, TotalUnique, 0)
```
* **Validated Benchmark:** 3.12% (2,997 repeat buyers out of 96,096 unique customers)

### Top 3 States Share
```dax
Top 3 States Share = 
VAR Top3Sales =
    CALCULATE(
        [Total Sales],
        TOPN(3, ALL(dim_customer[customer_state]), [Total Sales], DESC)
    )
VAR OverallSales =
    CALCULATE([Total Sales], ALL(dim_customer))
RETURN
    DIVIDE(Top3Sales, OverallSales, 0)
```
* **Validated Benchmark:** 63.37% (São Paulo `SP` 38.28%, Rio de Janeiro `RJ` 13.42%, Minas Gerais `MG` 11.66%)

### Seller Orders (Row-Context Safe)
```dax
Seller Orders = 
DISTINCTCOUNT(fact_order_items[order_id])
```
* **Usage:** Prevents global measure context bleed inside seller performance summary tables.

---

## 2. Logistics & Delivery SLA Metrics (Page 5)

### Average Delivery Days
```dax
Average Delivery Days = 
AVERAGEX(
    FILTER(
        fact_order_items,
        fact_order_items[order_status] = "delivered" &&
        NOT(ISBLANK(fact_order_items[order_delivered_customer_date]))
    ),
    DATEDIFF(
        fact_order_items[order_purchase_timestamp],
        fact_order_items[order_delivered_customer_date],
        DAY
    )
)
```
* **Validated Benchmark:** 12.56 Days

### On Time / Early %
```dax
On Time Early % = 
VAR DeliveredOrders =
    FILTER(
        fact_order_items,
        fact_order_items[order_status] = "delivered" &&
        NOT(ISBLANK(fact_order_items[order_delivered_customer_date]))
    )
VAR OnTimeCount =
    COUNTROWS(
        FILTER(
            DeliveredOrders,
            fact_order_items[order_delivered_customer_date] <= fact_order_items[order_estimated_delivery_date]
        )
    )
VAR TotalDelivered = COUNTROWS(DeliveredOrders)
RETURN
    DIVIDE(OnTimeCount, TotalDelivered, 0)
```
* **Validated Benchmark:** 91.89%

### Late %
```dax
Late % = 1 - [On Time Early %]
```
* **Validated Benchmark:** 8.11%

---

## 3. Payment Dynamics Metrics (Page 5)

### Total Payment Value
```dax
Total Payment Value = 
SUM(fact_payments[payment_value])
```
* **Validated Benchmark:** ₹16,008,872.12 (₹16.01M)

### Credit Card Payment %
```dax
Credit Card Payment % = 
DIVIDE(
    CALCULATE(SUM(fact_payments[payment_value]), fact_payments[payment_type] = "credit_card"),
    [Total Payment Value],
    0
)
```
* **Validated Benchmark:** 78.34%

### Credit Card Installment Usage %
```dax
Credit Card Installment Usage % = 
VAR CCPayments = FILTER(fact_payments, fact_payments[payment_type] = "credit_card")
VAR MultiInstallment = FILTER(CCPayments, fact_payments[payment_installments] > 1)
RETURN
    DIVIDE(COUNTROWS(MultiInstallment), COUNTROWS(CCPayments), 0)
```
* **Validated Benchmark:** 66.85%

### Installment Payment Value Share
```dax
Installment Payment Value Share = 
VAR MultiValue = CALCULATE(SUM(fact_payments[payment_value]), fact_payments[payment_type] = "credit_card", fact_payments[payment_installments] > 1)
VAR TotalCCValue = CALCULATE(SUM(fact_payments[payment_value]), fact_payments[payment_type] = "credit_card")
RETURN
    DIVIDE(MultiValue, TotalCCValue, 0)
```
* **Validated Benchmark:** 80.54%

---

## 4. Customer RFM Metrics (Page 4)

* **RFM Customer Count:** `93,358` unique delivered buyers.
* **RFM Monetary Sales:** `₹13,221,498.11` (`₹13.22M`).
* **Segment Distribution:**
  * *Lost Customers:* 47,569 customers (50.95% count, 43.11% sales)
  * *Big Spenders:* 21,308 customers (22.82% count, 42.25% sales)
  * *New Customers:* 21,726 customers (23.27% count, 9.15% sales)
  * *Loyal Customers:* 1,613 customers (1.73% count, 3.40% sales)
  * *At Risk:* 996 customers (1.07% count, 1.87% sales)
  * *Potential Loyalists:* 114 customers (0.12% count, 0.04% sales)
  * *Champions:* 32 customers (0.03% count, 0.18% sales)
