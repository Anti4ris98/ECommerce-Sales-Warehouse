# Grafana Dashboard SQL Queries

Use these SQL queries to create dashboard panels in Grafana.

## Panel 1: Total Revenue (Stat)
Show total revenue across all sales.

```sql
SELECT 
    SUM(revenue) as total_revenue
FROM fact_sales;
```

**Visualization:** Stat
**Unit:** Currency (USD)

---

## Panel 2: Total Orders (Stat)
Show total number of orders.

```sql
SELECT 
    COUNT(DISTINCT order_id) as total_orders
FROM fact_sales;
```

**Visualization:** Stat

---

## Panel 3: Average Order Value (Stat)
Show average revenue per order.

```sql
SELECT 
    ROUND(AVG(revenue)::numeric, 2) as avg_order_value
FROM fact_sales;
```

**Visualization:** Stat
**Unit:** Currency (USD)

---

## Panel 4: Revenue by Category (Pie Chart)
Show revenue distribution across categories.

```sql
SELECT 
    c.category_name,
    SUM(f.revenue) as revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_category c ON p.category = c.category_name
GROUP BY c.category_name
ORDER BY revenue DESC;
```

**Visualization:** Pie chart
**Legend:** Category name
**Value:** Revenue

---

## Panel 5: Top 10 Products by Revenue (Bar Chart)
Show best-selling products.

```sql
SELECT 
    p.product_title,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_title
ORDER BY total_revenue DESC
LIMIT 10;
```

**Visualization:** Bar chart (horizontal)
**X-axis:** Revenue
**Y-axis:** Product title

---

## Panel 6: Revenue Over Time (Time Series)
Show revenue trends over time.

```sql
SELECT 
    DATE_TRUNC('minute', f.created_at) as time,
    SUM(f.revenue) as revenue
FROM fact_sales f
GROUP BY DATE_TRUNC('minute', f.created_at)
ORDER BY time;
```

**Visualization:** Time series
**X-axis:** Time
**Y-axis:** Revenue
**Note:** Uses `created_at` timestamp for real-time data, grouped by minute

---

## Panel 7: Orders by Category (Bar Chart)
Show order volume by category.

```sql
SELECT 
    c.category_name,
    COUNT(DISTINCT f.order_id) as order_count
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_category c ON p.category = c.category_name
GROUP BY c.category_name
ORDER BY order_count DESC;
```

**Visualization:** Bar chart
**X-axis:** Category
**Y-axis:** Order count

---

## Panel 8: Top 5 Customers by Revenue (Table)
Show top customers.

```sql
SELECT 
    u.username,
    u.email,
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_user u ON f.user_id = u.user_id
GROUP BY u.user_id, u.username, u.email
ORDER BY total_revenue DESC
LIMIT 5;
```

**Visualization:** Table

---

## How to Create Dashboard

1. **Create Dashboard:**
   - Grafana → Dashboards → New → New Dashboard
   - Click "Add visualization"

2. **For Each Panel:**
   - Select data source: `ecommerce_warehouse`
   - Switch to "Code" mode (SQL editor)
   - Paste the SQL query
   - Configure visualization type (Stat, Pie, Bar, Time series, Table)
   - Set panel title
   - Click "Apply"

3. **Save Dashboard:**
   - Click "Save dashboard" icon (top right)
   - Name: `E-Commerce Sales Analytics`
   - Click "Save"

4. **Arrange Panels:**
   - Use first row for stats (Total Revenue, Total Orders, Avg Order Value)
   - Second row for charts (Revenue by Category, Top Products)
   - Third row for time series and customer table

---

# Advanced Analytics (dbt Marts)

These queries use **dbt data marts** for faster, cleaner analytics. Create a separate dashboard called `Business Intelligence` to showcase analytical capabilities.

---

## Panel 9: Customer Segmentation (Pie Chart)
Show distribution of customers by segment (VIP/Regular/Casual).

```sql
SELECT 
    customer_segment,
    COUNT(*) as customer_count
FROM customer_ltv
GROUP BY customer_segment
ORDER BY customer_count DESC;
```

**Visualization:** Pie chart
**Legend:** Customer segment
**Value:** Customer count

---

## Panel 10: Top 10 Customers by LTV (Table)
Show most valuable customers with lifetime metrics.

```sql
SELECT 
    username,
    email,
    lifetime_orders,
    lifetime_value,
    avg_order_value,
    customer_segment,
    customer_tenure_days
FROM customer_ltv
ORDER BY lifetime_value DESC
LIMIT 10;
```

**Visualization:** Table
**Columns:** Username, Email, Orders, LTV, Avg Order, Segment, Tenure (days)

---

## Panel 11: Product Performance Rankings (Table)
Show top products with rankings and revenue percentage.

```sql
SELECT 
    product_title,
    category,
    total_revenue,
    total_units_sold,
    revenue_rank,
    category_rank,
    pct_of_total_revenue
FROM product_performance
ORDER BY revenue_rank
LIMIT 15;
```

**Visualization:** Table
**Highlight:** Top 5 by revenue

---

## Panel 12: Daily Sales Trends (Time Series)
Show daily business metrics over time.

```sql
SELECT 
    full_date as time,
    total_revenue,
    total_orders,
    unique_customers,
    avg_order_value
FROM daily_sales
ORDER BY full_date;
```

**Visualization:** Time series (multiple lines)
**Lines:** 
- Total Revenue (left Y-axis)
- Total Orders (right Y-axis)
- Unique Customers (right Y-axis)

---

## Panel 13: VIP Customer Revenue Contribution (Stat)
Show percentage of revenue from VIP customers.

```sql
SELECT 
    ROUND(
        100.0 * SUM(CASE WHEN customer_segment = 'VIP' THEN lifetime_value ELSE 0 END) / 
        SUM(lifetime_value), 
        2
    ) as vip_revenue_pct
FROM customer_ltv;
```

**Visualization:** Stat
**Unit:** Percent (%)
**Description:** "VIP Customer Revenue %"

---

## Panel 14: Category Performance Comparison (Bar Chart)
Compare categories by total revenue using product performance.

```sql
SELECT 
    category,
    SUM(total_revenue) as category_revenue,
    SUM(total_units_sold) as units_sold,
    COUNT(*) as product_count
FROM product_performance
GROUP BY category
ORDER BY category_revenue DESC;
```

**Visualization:** Bar chart (grouped)
**X-axis:** Category
**Bars:** Revenue, Units Sold

---

## Panel 15: Average Customer Metrics (Stats Row)
Show key customer metrics in a row.

**Avg Lifetime Value:**
```sql
SELECT ROUND(AVG(lifetime_value)::numeric, 2) as avg_ltv
FROM customer_ltv;
```

**Avg Orders per Customer:**
```sql
SELECT ROUND(AVG(lifetime_orders)::numeric, 2) as avg_orders
FROM customer_ltv;
```

**Avg Customer Tenure:**
```sql
SELECT ROUND(AVG(customer_tenure_days)::numeric, 0) as avg_tenure_days
FROM customer_ltv;
```

**Visualization:** 3 Stat panels in one row

---

## Comparison: Raw Queries vs dbt Marts

### Example: Top Customers

**❌ Without dbt (complex):**
```sql
SELECT 
    u.username,
    u.email,
    COUNT(DISTINCT f.order_id) as lifetime_orders,
    SUM(f.revenue) as lifetime_value,
    AVG(f.revenue) as avg_order_value,
    MIN(d.full_date) as first_order_date,
    MAX(d.full_date) as last_order_date
FROM fact_sales f
JOIN dim_user u ON f.user_id = u.user_id
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY u.user_id, u.username, u.email
ORDER BY lifetime_value DESC
LIMIT 10;
```

**✅ With dbt marts (simple):**
```sql
SELECT 
    username,
    email,
    lifetime_orders,
    lifetime_value,
    avg_order_value,
    first_order_date,
    last_order_date,
    customer_segment
FROM customer_ltv
ORDER BY lifetime_value DESC
LIMIT 10;
```

**Benefits:**
- 🚀 **Faster** - pre-aggregated data
- 📖 **Cleaner** - no complex JOINs
- 🎯 **Enhanced** - additional metrics (segment, tenure)
- ♻️ **Reusable** - same logic across all dashboards

---

## Dashboard Organization

### Dashboard 1: "Real-Time Operations"
**Purpose:** Monitor live pipeline activity
- Total Revenue (fact_sales)
- Orders count (fact_sales)
- Revenue over time (fact_sales real-time)
- Category breakdown (live)

**Update frequency:** 5 seconds

### Dashboard 2: "Business Intelligence" 
**Purpose:** Strategic business insights
- Customer segmentation (customer_ltv)
- Product rankings (product_performance)
- Daily trends (daily_sales)
- LTV metrics (customer_ltv)

**Update frequency:** 1 minute (marts refresh with dbt)

---

## Running dbt to Update Marts

To refresh analytics data:

```bash
cd dbt_project
dbt run --profiles-dir .
```

For production, schedule this with cron or Airflow to run hourly/daily.
