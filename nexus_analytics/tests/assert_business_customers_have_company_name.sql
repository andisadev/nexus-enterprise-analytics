SELECT
    customer_id,
    customer_type,
    company_name
FROM {{ ref('stg_customers') }}
WHERE customer_type = 'Business'
  AND company_name IS NULL