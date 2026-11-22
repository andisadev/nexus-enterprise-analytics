
{{
    config(
        materialized='view'
    )
}}

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'sales_orders') }}

),

standardized AS (

    SELECT
        CAST(ORDER_ID AS VARCHAR(20)) AS order_id,
        CAST(CUSTOMER_ID AS VARCHAR(20)) AS customer_id,
        CAST(PRODUCT_ID AS VARCHAR(20)) AS product_id,
        CAST(SALES_REP_ID AS VARCHAR(20)) AS sales_rep_id,

        CAST(ORDER_DATE AS DATE) AS order_date,
        CAST(QUANTITY AS NUMBER(10,0)) AS quantity,
        CAST(UNIT_PRICE AS NUMBER(10,2)) AS unit_price,
        CAST(DISCOUNT_PCT AS NUMBER(5,2)) AS discount_pct,

        INITCAP(TRIM(REGION)) AS region,
        INITCAP(TRIM(ORDER_STATUS)) AS order_status

    FROM source_data

),

calculated AS (

    SELECT
        *,

        ROUND(
            quantity * unit_price,
            2
        ) AS gross_sales_amount,

        ROUND(
            quantity * unit_price * discount_pct / 100.0,
            2
        ) AS discount_amount,

        ROUND(
            quantity * unit_price *
            (1 - discount_pct / 100.0),
            2
        ) AS net_sales_amount

    FROM standardized

)

SELECT *
FROM calculated
