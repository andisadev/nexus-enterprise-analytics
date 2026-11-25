
{{
    config(
        materialized='table'
    )
}}

WITH staging_sales AS (

    SELECT *
    FROM {{ ref('stg_sales_orders') }}

),
sales_with_dimensions AS (

    SELECT
        sales.*,

        customer.customer_key,
        product.product_key

    FROM staging_sales AS sales

    LEFT JOIN {{ ref('dim_customer') }} AS customer
        ON sales.customer_id = customer.customer_id

    LEFT JOIN {{ ref('dim_product') }} AS product
        ON sales.product_id = product.product_id

),

sales_measures AS (

    SELECT
        order_id,
        customer_id,
        customer_key,
        product_id,
        product_key,
        sales_rep_id,
        order_date,
	    TO_NUMBER(TO_CHAR(order_date, 'YYYYMMDD')) AS order_date_key,
        region,
        order_status,

        quantity,
        unit_price,
        discount_pct,

        gross_sales_amount,
        discount_amount,
        net_sales_amount AS net_order_value,

        CASE
            WHEN order_status = 'Completed'
                THEN net_sales_amount
            ELSE 0
        END AS completed_sales_amount,

        CASE
            WHEN order_status = 'Pending'
                THEN net_sales_amount
            ELSE 0
        END AS pending_order_value,

        CASE
            WHEN order_status = 'Returned'
                THEN net_sales_amount
            ELSE 0
        END AS returned_order_value,

        CASE
            WHEN order_status = 'Cancelled'
                THEN net_sales_amount
            ELSE 0
        END AS cancelled_order_value

    FROM sales_with_dimensions

)

SELECT *
FROM sales_measures
