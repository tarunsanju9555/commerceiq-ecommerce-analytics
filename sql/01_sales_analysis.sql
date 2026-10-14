
USE CustomerSalesIntelligence;
GO

-- Overall sales performance
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customer_accounts,
    COUNT(DISTINCT oi.product_id) AS distinct_products,
    SUM(oi.price) AS total_item_sales,
    SUM(oi.freight_value) AS total_freight
FROM dbo.Orders AS o
JOIN dbo.OrderItems AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';
GO
