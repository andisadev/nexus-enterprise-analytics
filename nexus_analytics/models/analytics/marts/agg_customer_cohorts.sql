{{
    config(
        materialized='table'
    )
}}

WITH customer_first_orders AS (

    SELECT
        customer_key,
        customer_id,
        MIN(order_date) AS first_order_date

    FROM {{ ref('fct_sales') }}

    GROUP BY
        customer_key,
        customer_id

),

customer_cohorts AS (

    SELECT
        customer_key,
        customer_id,
        first_order_date,

        DATE_TRUNC('month', first_order_date)::DATE
            AS cohort_month

    FROM customer_first_orders

),

customer_activity AS (

    SELECT
        f.customer_key,
        f.customer_id,

        c.cohort_month,

        DATE_TRUNC('month', f.order_date)::DATE
            AS activity_month,

        COUNT(DISTINCT f.order_id) AS order_count,

        SUM(f.net_order_value) AS net_order_value,

        SUM(f.completed_sales_amount) AS completed_sales

    FROM {{ ref('fct_sales') }} f

    INNER JOIN customer_cohorts c
        ON f.customer_key = c.customer_key

    GROUP BY
        f.customer_key,
        f.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', f.order_date)::DATE

)

SELECT
    cohort_month,
    activity_month,

    DATEDIFF(
        month,
        cohort_month,
        activity_month
    ) AS cohort_age_months,

    COUNT(DISTINCT customer_key) AS active_customers,

    SUM(order_count) AS order_count,

    SUM(net_order_value) AS net_order_value,

    SUM(completed_sales) AS completed_sales

FROM customer_activity

GROUP BY
    cohort_month,
    activity_month,
    DATEDIFF(month, cohort_month, activity_month)