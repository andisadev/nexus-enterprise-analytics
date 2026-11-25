{{
    config(
        materialized='table'
    )
}}

WITH sales AS (

    SELECT *
    FROM {{ ref('fct_sales') }}

),

sales_aggregated AS (

    SELECT
        COUNT(DISTINCT order_id) AS order_count,

        SUM(gross_sales_amount) AS gross_sales,
        SUM(discount_amount) AS discounts,
        SUM(net_order_value) AS net_order_value,

        SUM(completed_sales_amount) AS completed_sales,

        COUNT_IF(order_status = 'Completed') AS completed_orders,
        COUNT_IF(order_status = 'Pending') AS pending_orders,
        COUNT_IF(order_status = 'Returned') AS returned_orders,
        COUNT_IF(order_status = 'Cancelled') AS cancelled_orders

    FROM sales

)

SELECT
    order_count,

    gross_sales,
    discounts,
    net_order_value,
    completed_sales,

    completed_orders,
    pending_orders,
    returned_orders,
    cancelled_orders,

    ROUND(
        net_order_value / NULLIF(order_count, 0),
        2
    ) AS average_order_value,

    ROUND(
        completed_orders * 100.0 / NULLIF(order_count, 0),
        2
    ) AS completion_rate_pct,

    ROUND(
        returned_orders * 100.0 / NULLIF(order_count, 0),
        2
    ) AS return_rate_pct,

    ROUND(
        cancelled_orders * 100.0 / NULLIF(order_count, 0),
        2
    ) AS cancellation_rate_pct

FROM sales_aggregated