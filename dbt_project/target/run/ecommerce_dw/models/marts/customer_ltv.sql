
  
    

  create  table "ecommerce_dw"."public"."customer_ltv__dbt_tmp"
  
  
    as
  
  (
    -- Customer Lifetime Value
-- Aggregated customer metrics



SELECT 
    user_id,
    username,
    email,
    
    COUNT(DISTINCT order_id) as lifetime_orders,
    SUM(revenue) as lifetime_value,
    AVG(revenue) as avg_order_value,
    SUM(quantity) as total_items_purchased,
    
    MIN(created_at) as first_order_date,
    MAX(created_at) as last_order_date,
    
    -- Calculate days between first and last order
    EXTRACT(DAY FROM (MAX(created_at) - MIN(created_at))) as customer_tenure_days,
    
    -- Categorize customers
    CASE 
        WHEN COUNT(DISTINCT order_id) >= 20 THEN 'VIP'
        WHEN COUNT(DISTINCT order_id) >= 10 THEN 'Regular'
        ELSE 'Casual'
    END as customer_segment
    
FROM "ecommerce_dw"."public"."stg_sales"
GROUP BY user_id, username, email
ORDER BY lifetime_value DESC
  );
  