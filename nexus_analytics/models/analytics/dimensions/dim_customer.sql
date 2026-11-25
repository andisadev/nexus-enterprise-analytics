{{
    config(
        materialized='table'
    )
}}

WITH customers AS (

    SELECT *
    FROM {{ ref('stg_customers') }}

),

customer_dimension AS (

    SELECT
        MD5(TO_VARCHAR(customer_id)) AS customer_key,

        customer_id,

        first_name,
        last_name,
        email,
        company_name,

        customer_type,
        industry,
        customer_segment,

        city,
        state,
        region,

        signup_date,
        customer_status

    FROM customers

)

SELECT *
FROM customer_dimension