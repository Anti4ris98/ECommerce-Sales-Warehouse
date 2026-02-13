-- Staging model: Clean fact_sales data
-- This is a foundation for marts



SELECT 
    f.sale_id,
    f.order_id,
    f.user_id,
    f.product_id,
    f.date_id,
    f.quantity,
    f.unit_price,
    f.revenue,
    f.created_at,
    
    -- Join dimension data for easier querying
    p.product_title,
    p.category,
    u.username,
    u.email,
    d.full_date,
    d.year,
    d.month,
    d.quarter
    
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_id = p.product_id
LEFT JOIN dim_user u ON f.user_id = u.user_id
LEFT JOIN dim_date d ON f.date_id = d.date_id
WHERE f.created_at IS NOT NULL