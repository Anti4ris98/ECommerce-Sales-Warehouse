# dbt Data Marts

This directory contains dbt models for the e-commerce data warehouse analytics layer.

## Structure

```
dbt_project/
├── dbt_project.yml      # Project configuration
├── profiles.yml         # Database connection
└── models/
    ├── staging/
    │   └── stg_sales.sql    # Cleaned sales with dimensions
    └── marts/
        ├── daily_sales.sql          # Daily aggregations
        ├── customer_ltv.sql         # Customer lifetime value
        └── product_performance.sql  # Product metrics
```

## Setup

### 1. Install dbt

```bash
pip install dbt-postgres
```

### 2. Configure Profile

The `profiles.yml` is already configured for local PostgreSQL. Update if needed:
- Host: `localhost`
- Port: `5432`
- Database: `ecommerce_dw`
- User: `user`
- Password: `password`

### 3. Test Connection

```bash
cd dbt_project
dbt debug
```

### 4. Run Models

```bash
# Run all models
dbt run

# Run specific model
dbt run --models daily_sales

# Run marts only
dbt run --models marts.*
```

## Models

### Staging Layer

**`stg_sales`** - Foundation view
- Joins `fact_sales` with all dimensions
- Clean, denormalized data
- Used by all marts

### Mart Layer

**`daily_sales`** - Daily business metrics
- Total orders, revenue, customers
- Average order value
- Aggregated by day

**`customer_ltv`** - Customer analytics
- Lifetime value per customer
- Order frequency
- Customer segmentation (VIP/Regular/Casual)
- Tenure tracking

**`product_performance`** - Product metrics
- Revenue and unit sales
- Rankings (overall and by category)
- Percentage of total revenue

## Usage

Query the marts directly:

```sql
-- Top customers by lifetime value
SELECT * FROM customer_ltv
ORDER BY lifetime_value DESC
LIMIT 10;

-- Best performing products
SELECT * FROM product_performance
WHERE revenue_rank <= 5;

-- Sales trend over time
SELECT * FROM daily_sales
ORDER BY full_date DESC;
```

## Adding to Grafana

Create new panels using these marts for advanced analytics!
