-- Product Performance Analytics
-- Product-level metrics



SELECT 
    product_id,
    product_title,
    category,
    
    COUNT(DISTINCT order_id) as times_ordered,
    SUM(quantity) as total_units_sold,
    SUM(revenue) as total_revenue,
    AVG(unit_price) as avg_sale_price,
    
    -- Performance metrics
    RANK() OVER (ORDER BY SUM(revenue) DESC) as revenue_rank,
    RANK() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) as category_rank,
    
    -- Calculate what % of total revenue
    ROUND(
        100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (),
        2
    ) as pct_of_total_revenue
    
FROM "ecommerce_dw"."public"."stg_sales"
GROUP BY product_id, product_title, category
ORDER BY total_revenue DESC