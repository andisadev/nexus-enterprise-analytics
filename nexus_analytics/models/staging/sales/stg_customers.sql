
{{
    config(
        materialized='view'
    )
}}

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'customers') }}

),

standardized AS (

    SELECT
        CAST(CUSTOMER_ID AS VARCHAR(20)) AS customer_id,

        INITCAP(TRIM(FIRST_NAME)) AS first_name,
        INITCAP(TRIM(LAST_NAME)) AS last_name,

        LOWER(TRIM(EMAIL)) AS email,

        NULLIF(TRIM(COMPANY_NAME), '') AS company_name,

        INITCAP(TRIM(CUSTOMER_TYPE)) AS customer_type,
        INITCAP(TRIM(INDUSTRY)) AS industry,
        INITCAP(TRIM(CUSTOMER_SEGMENT)) AS customer_segment,

        INITCAP(TRIM(CITY)) AS city,
        INITCAP(TRIM(STATE)) AS state,
        INITCAP(TRIM(REGION)) AS region,

        CAST(SIGNUP_DATE AS DATE) AS signup_date,

        INITCAP(TRIM(CUSTOMER_STATUS)) AS customer_status

    FROM source_data

)

SELECT *
FROM standardized
