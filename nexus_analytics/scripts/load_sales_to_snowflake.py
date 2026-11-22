
import os
from pathlib import Path

import snowflake.connector


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

ACCOUNT = "EDDWQVI-NE45410"
USER = "TITA26"
ROLE = "NEXUS_ROLE"
WAREHOUSE = "NEXUS_WH"
DATABASE = "NEXUS_ANALYTICS"
SCHEMA = "RAW"

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_FILE = BASE_DIR / "data" / "generated" / "sales_orders.csv"

STAGE = "SALES_ORDERS_STAGE"
FILE_FORMAT = "SALES_CSV_FORMAT"
TABLE = "SALES_ORDERS"

password = os.environ.get("DBT_ENV_SECRET_PASSWORD")

if not password:
    raise RuntimeError(
        "Snowflake password not found in DBT_ENV_SECRET_PASSWORD. "
        "Set it in this PowerShell session before running the script."
    )

if not CSV_FILE.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")


# --------------------------------------------------
# 2. Connect to Snowflake
# --------------------------------------------------

print("Connecting to Snowflake...")

conn = snowflake.connector.connect(
    account=ACCOUNT,
    user=USER,
    password=password,
    role=ROLE,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA
)

cursor = conn.cursor()

try:
    print("Connection successful.")

    # --------------------------------------------------
    # 3. Create CSV file format
    # --------------------------------------------------

    print("Creating CSV file format...")

    cursor.execute(f"""
        CREATE FILE FORMAT IF NOT EXISTS {FILE_FORMAT}
            TYPE = CSV
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            EMPTY_FIELD_AS_NULL = TRUE
            NULL_IF = ('')
    """)

    # --------------------------------------------------
    # 4. Create internal stage
    # --------------------------------------------------

    print("Creating internal stage...")

    cursor.execute(f"""
        CREATE STAGE IF NOT EXISTS {STAGE}
            FILE_FORMAT = {FILE_FORMAT}
    """)

    # --------------------------------------------------
    # 5. Create raw destination table
    # --------------------------------------------------

    print("Creating RAW table...")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            ORDER_ID VARCHAR(20),
            CUSTOMER_ID VARCHAR(20),
            PRODUCT_ID VARCHAR(20),
            SALES_REP_ID VARCHAR(20),
            ORDER_DATE DATE,
            QUANTITY NUMBER(10, 0),
            UNIT_PRICE NUMBER(10, 2),
            DISCOUNT_PCT NUMBER(5, 2),
            REGION VARCHAR(30),
            ORDER_STATUS VARCHAR(20)
        )
    """)

    # --------------------------------------------------
    # 6. Upload CSV to Snowflake stage
    # --------------------------------------------------

    print("Uploading CSV to Snowflake stage...")

    local_file = CSV_FILE.as_posix()

    put_command = (
        f"PUT 'file://{local_file}' "
        f"@{STAGE} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
    )

    cursor.execute(put_command)

    upload_results = cursor.fetchall()

    for result in upload_results:
        print("Upload result:", result)

    # --------------------------------------------------
    # 7. Load staged file into RAW table
    # --------------------------------------------------

    print("Loading data into RAW.SALES_ORDERS...")

    cursor.execute(f"""
        COPY INTO {TABLE}
        FROM @{STAGE}
        FILE_FORMAT = (FORMAT_NAME = '{FILE_FORMAT}')
        FILES = ('sales_orders.csv.gz')
        ON_ERROR = 'ABORT_STATEMENT'
    """)

    copy_results = cursor.fetchall()

    for result in copy_results:
        print("COPY result:", result)

    # --------------------------------------------------
    # 8. Verify loaded records
    # --------------------------------------------------

    cursor.execute(f"""
        SELECT
            COUNT(*) AS TOTAL_ORDERS,
            COUNT(DISTINCT ORDER_ID) AS UNIQUE_ORDERS,
            MIN(ORDER_DATE) AS FIRST_ORDER_DATE,
            MAX(ORDER_DATE) AS LAST_ORDER_DATE
        FROM {TABLE}
    """)

    verification = cursor.fetchone()

    print("\nSNOWFLAKE LOAD VERIFICATION")
    print("--------------------------------")
    print(f"Total orders:       {verification[0]:,}")
    print(f"Unique orders:      {verification[1]:,}")
    print(f"First order date:   {verification[2]}")
    print(f"Last order date:    {verification[3]}")

    if verification[0] != 5000:
        raise RuntimeError(
            f"Expected 5,000 records, found {verification[0]}"
        )

    if verification[1] != 5000:
        raise RuntimeError("Duplicate order IDs detected.")

    print("\nSALES DATA SUCCESSFULLY LOADED INTO SNOWFLAKE.")

finally:
    cursor.close()
    conn.close()
    print("\nSnowflake connection closed.")
