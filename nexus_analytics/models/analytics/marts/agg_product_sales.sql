{{
    config(
        materialized='table'
    )
}}

WITH product_orders AS (

    SELECT
        product_key,
        product_id,

        COUNT(DISTINCT order_id) AS total_orders,

        SUM(quantity) AS units_sold,

        SUM(gross_sales_amount) AS gross_sales,
        SUM(discount_amount) AS discounts,
        SUM(net_order_value) AS net_order_value,

        SUM(completed_sales_amount) AS completed_sales,

        COUNT_IF(order_status = 'Completed') AS completed_orders,
        COUNT_IF(order_status = 'Returned') AS returned_orders,
        COUNT_IF(order_status = 'Cancelled') AS cancelled_orders,
        COUNT_IF(order_status = 'Pending') AS pending_orders

    FROM {{ ref('fct_sales') }}

    GROUP BY
        product_key,
        product_id

),

product_attributes AS (

    SELECT *
    FROM {{ ref('dim_product') }}

)

SELECT
    product_orders.product_key,
    product_orders.product_id,

    product_attributes.product_name,
    product_attributes.category,
    product_attributes.subcategory,
    product_attributes.list_price,
    product_attributes.standard_cost,
    product_attributes.product_status,

    product_orders.total_orders,
    product_orders.units_sold,

    product_orders.gross_sales,
    product_orders.discounts,
    product_orders.net_order_value,
    product_orders.completed_sales,

    product_orders.completed_orders,
    product_orders.pending_orders,
    product_orders.returned_orders,
    product_orders.cancelled_orders,

    ROUND(
        product_orders.net_order_value
        / NULLIF(product_orders.units_sold, 0),
        2
    ) AS average_selling_price_per_unit,

    ROUND(
        product_orders.net_order_value
        - (product_orders.units_sold * product_attributes.standard_cost),
        2
    ) AS estimated_product_margin,

    ROUND(
        (
            product_orders.net_order_value
            - (product_orders.units_sold * product_attributes.standard_cost)
        ) * 100.0
        / NULLIF(product_orders.net_order_value, 0),
        2
    ) AS estimated_product_margin_pct

FROM product_orders

LEFT JOIN product_attributes
    ON product_orders.product_key = product_attributes.product_key