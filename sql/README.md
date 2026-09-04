# SQL Data Warehouse & Analytical Queries

This directory contains production-grade SQL scripts for modeling the Olist e-commerce data in a MySQL / Relational Data Warehouse and querying key business metrics.

## Files
1. `01_schema_ddl.sql`: Creates database schema `olist_dwh`, dimensional tables, fact tables, foreign key constraints, and performance indexes.
2. `02_analytical_queries.sql`: Analytical queries validating all core business metrics:
   - Macro KPIs (Sales, Orders, Items, AOV, Repeat Rate)
   - Geographic concentration (Top 10 States & Top 3 States Share)
   - Category and Seller contribution
   - Logistics SLA fulfillment (On-Time / Early %, Late %, Average Delivery Days)
   - Payment method breakdown & installment dynamics
   - RFM segment revenue distribution

## Running Scripts in MySQL
```bash
mysql -u root -p < sql/01_schema_ddl.sql
mysql -u root -p olist_dwh < sql/02_analytical_queries.sql
```
