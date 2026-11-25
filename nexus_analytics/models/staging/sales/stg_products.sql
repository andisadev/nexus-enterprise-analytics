
{{
    config(
        materialized='view'
    )
}}

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'products') }}

),

standardized AS (

    SELECT
        CAST(PRODUCT_ID AS VARCHAR(20)) AS product_id,

        INITCAP(TRIM(PRODUCT_NAME)) AS product_name,
        INITCAP(TRIM(CATEGORY)) AS category,
        INITCAP(TRIM(SUBCATEGORY)) AS subcategory,

        CAST(LIST_PRICE AS NUMBER(10,2)) AS list_price,
        CAST(STANDARD_COST AS NUMBER(10,2)) AS standard_cost,

        INITCAP(TRIM(PRODUCT_STATUS)) AS product_status

    FROM source_data

)

SELECT *
FROM standardized
