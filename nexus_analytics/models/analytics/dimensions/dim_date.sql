
{{
    config(
        materialized='table'
    )
}}

WITH RECURSIVE date_spine (date_day, max_date) AS (

    -- Anchor: establish the date range from sales data
    SELECT
        MIN(order_date)::DATE AS date_day,
        MAX(order_date)::DATE AS max_date
    FROM {{ ref('fct_sales') }}

    UNION ALL

    -- Recursive member: generate every calendar day
    SELECT
        DATEADD(day, 1, date_day)::DATE,
        max_date
    FROM date_spine
    WHERE date_day < max_date

),

date_attributes AS (

    SELECT
        date_day,

        TO_NUMBER(TO_CHAR(date_day, 'YYYYMMDD')) AS date_key,

        YEAR(date_day) AS year,
        QUARTER(date_day) AS quarter,
        MONTH(date_day) AS month_number,
        TO_CHAR(date_day, 'MMMM') AS month_name,

        TO_CHAR(date_day, 'YYYY-MM') AS year_month,

        WEEKISO(date_day) AS week_number,
        YEAROFWEEKISO(date_day) AS iso_week_year,

        DAYOFMONTH(date_day) AS day_of_month,
        DAYOFWEEKISO(date_day) AS day_of_week_number,
        TO_CHAR(date_day, 'DY') AS day_name,

        DATE_TRUNC('month', date_day)::DATE AS month_start_date,

        LAST_DAY(date_day, 'month')::DATE AS month_end_date,

        DATEADD(
            day,
            1 - DAYOFWEEKISO(date_day),
            date_day
        )::DATE AS week_start_date,

        DAYOFWEEKISO(date_day) IN (6, 7) AS is_weekend

    FROM date_spine

)

SELECT *
FROM date_attributes
