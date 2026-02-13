
  
    

  create  table "ecommerce_dw"."public"."daily_sales__dbt_tmp"
  
  
    as
  
  (
    -- Daily Sales Aggregations
-- Business metrics aggregated by day



SELECT 
    full_date,
    year,
    month,
    quarter,
    
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT user_id) as unique_customers,
    SUM(quantity) as total_items_sold,
    SUM(revenue) as total_revenue,
    AVG(revenue) as avg_order_value,
    MAX(revenue) as max_order_value,
    MIN(revenue) as min_order_value
    
FROM "ecommerce_dw"."public"."stg_sales"
GROUP BY full_date, year, month, quarter
ORDER BY full_date DESC
  );
  