{{
    config(
        materialized='table'
    )
}}

WITH regional_sales AS (

    SELECT
        region,

        COUNT(DISTINCT order_id) AS total_orders,

        COUNT_IF(order_status = 'Completed') AS completed_orders,
        COUNT_IF(order_status = 'Pending') AS pending_orders,
        COUNT_IF(order_status = 'Returned') AS returned_orders,
        COUNT_IF(order_status = 'Cancelled') AS cancelled_orders,

        COUNT(DISTINCT customer_id) AS unique_customers,

        SUM(quantity) AS units_sold,

        SUM(gross_sales_amount) AS gross_sales,
        SUM(discount_amount) AS discounts,
        SUM(net_order_value) AS net_order_value,
        SUM(completed_sales_amount) AS completed_sales

    FROM {{ ref('fct_sales') }}

    GROUP BY region

)

SELECT
    region,

    total_orders,
    unique_customers,
    units_sold,

    gross_sales,
    discounts,
    net_order_value,
    completed_sales,

    completed_orders,
    pending_orders,
    returned_orders,
    cancelled_orders,

    ROUND(
        net_order_value / NULLIF(total_orders, 0),
        2
    ) AS average_order_value,

    ROUND(
        completed_orders * 100.0 / NULLIF(total_orders, 0),
        2
    ) AS completion_rate_pct,

    ROUND(
        returned_orders * 100.0 / NULLIF(total_orders, 0),
        2
    ) AS return_rate_pct,

    ROUND(
        cancelled_orders * 100.0 / NULLIF(total_orders, 0),
        2
    ) AS cancellation_rate_pct,

    ROUND(
        net_order_value / NULLIF(unique_customers, 0),
        2
    ) AS sales_per_customer

FROM regional_sales