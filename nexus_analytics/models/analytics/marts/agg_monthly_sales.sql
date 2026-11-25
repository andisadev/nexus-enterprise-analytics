{{
    config(
        materialized='table'
    )
}}

WITH sales AS (

    SELECT *
    FROM {{ ref('fct_sales') }}

),

monthly_sales AS (

    SELECT
        DATE_TRUNC('month', order_date)::DATE AS month_start_date,

        YEAR(order_date) AS sales_year,
        MONTH(order_date) AS sales_month,

        region,

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

    GROUP BY
        DATE_TRUNC('month', order_date)::DATE,
        YEAR(order_date),
        MONTH(order_date),
        region

)

SELECT
    *,

    ROUND(
        net_order_value / NULLIF(order_count, 0),
        2
    ) AS average_order_value,

    ROUND(
        completed_orders * 100.0 / NULLIF(order_count, 0),
        2
    ) AS completion_rate_pct

FROM monthly_sales