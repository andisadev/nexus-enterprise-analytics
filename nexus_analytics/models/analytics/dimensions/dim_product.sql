{{
    config(
        materialized='table'
    )
}}

WITH products AS (

    SELECT *
    FROM {{ ref('stg_products') }}

),

product_dimension AS (

    SELECT
        MD5(TO_VARCHAR(product_id)) AS product_key,

        product_id,

        product_name,
        category,
        subcategory,

        list_price,
        standard_cost,

        product_status

    FROM products

)

SELECT *
FROM product_dimension