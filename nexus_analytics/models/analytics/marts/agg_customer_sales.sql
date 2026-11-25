{{
    config(
        materialized='table'
    )
}}

WITH customer_orders AS (

    SELECT
        customer_key,
        customer_id,

        COUNT(DISTINCT order_id) AS total_orders,

        COUNT_IF(order_status = 'Completed') AS completed_orders,
        COUNT_IF(order_status = 'Returned') AS returned_orders,
        COUNT_IF(order_status = 'Cancelled') AS cancelled_orders,
        COUNT_IF(order_status = 'Pending') AS pending_orders,

        SUM(gross_sales_amount) AS gross_sales,
        SUM(discount_amount) AS discounts,
        SUM(net_order_value) AS net_order_value,
        SUM(completed_sales_amount) AS completed_sales,

        MIN(order_date) AS first_order_date,
        MAX(order_date) AS most_recent_order_date

    FROM {{ ref('fct_sales') }}

    GROUP BY
        customer_key,
        customer_id

),

customer_attributes AS (

    SELECT *
    FROM {{ ref('dim_customer') }}

)

SELECT
    customer_orders.customer_key,
    customer_orders.customer_id,

    customer_attributes.first_name,
    customer_attributes.last_name,
    customer_attributes.customer_type,
    customer_attributes.industry,
    customer_attributes.customer_segment,
    customer_attributes.region,
    customer_attributes.signup_date,
    customer_attributes.customer_status,

    customer_orders.total_orders,
    customer_orders.completed_orders,
    customer_orders.returned_orders,
    customer_orders.cancelled_orders,
    customer_orders.pending_orders,

    customer_orders.gross_sales,
    customer_orders.discounts,
    customer_orders.net_order_value,
    customer_orders.completed_sales,

    ROUND(
        customer_orders.net_order_value
        / NULLIF(customer_orders.total_orders, 0),
        2
    ) AS average_order_value,

    customer_orders.first_order_date,
    customer_orders.most_recent_order_date,

    DATEDIFF(
        day,
        customer_orders.first_order_date,
        customer_orders.most_recent_order_date
    ) AS customer_relationship_days

FROM customer_orders

LEFT JOIN customer_attributes
    ON customer_orders.customer_key = customer_attributes.customer_key