
from pathlib import Path
import os
import snowflake.connector

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "generated"

FILES = {
    "CUSTOMERS": DATA_DIR / "customers.csv",
    "PRODUCTS": DATA_DIR / "products.csv"
}

DATABASE = "NEXUS_ANALYTICS"
SCHEMA = "RAW"

# --------------------------------------------------
# Connection
# --------------------------------------------------

password = os.environ.get("DBT_ENV_SECRET_PASSWORD")

if not password:
    raise RuntimeError(
        "DBT_ENV_SECRET_PASSWORD is not set."
    )

conn = snowflake.connector.connect(
    account="EDDWQVI-NE45410",
    user="TITA26",
    password=password,
    role="NEXUS_ROLE",
    warehouse="NEXUS_WH",
    database=DATABASE,
    schema=SCHEMA
)

# --------------------------------------------------
# Load datasets
# --------------------------------------------------

try:
    cursor = conn.cursor()

    cursor.execute("""
        CREATE FILE FORMAT IF NOT EXISTS MASTER_CSV_FORMAT
        TYPE = CSV
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        NULL_IF = ('', 'NULL', 'null')
    """)

    cursor.execute("""
        CREATE STAGE IF NOT EXISTS MASTER_DATA_STAGE
    """)

    for table_name, file_path in FILES.items():

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        print(f"\nLoading {table_name}...")

        # Upload file to internal stage.
        cursor.execute(
            f"""
            PUT file://{file_path.as_posix()}
            @MASTER_DATA_STAGE
            AUTO_COMPRESS=TRUE
            OVERWRITE=TRUE
            """
        )

        # Create target table from CSV structure.
        # Column types are explicitly defined.
        if table_name == "CUSTOMERS":
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS RAW.CUSTOMERS (
                    CUSTOMER_ID VARCHAR(20),
                    FIRST_NAME VARCHAR(100),
                    LAST_NAME VARCHAR(100),
                    EMAIL VARCHAR(255),
                    COMPANY_NAME VARCHAR(255),
                    CUSTOMER_TYPE VARCHAR(30),
                    INDUSTRY VARCHAR(100),
                    CUSTOMER_SEGMENT VARCHAR(50),
                    CITY VARCHAR(100),
                    STATE VARCHAR(100),
                    REGION VARCHAR(50),
                    SIGNUP_DATE DATE,
                    CUSTOMER_STATUS VARCHAR(30)
                )
            """
        else:
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS RAW.PRODUCTS (
                    PRODUCT_ID VARCHAR(20),
                    PRODUCT_NAME VARCHAR(150),
                    CATEGORY VARCHAR(100),
                    SUBCATEGORY VARCHAR(100),
                    LIST_PRICE NUMBER(10,2),
                    STANDARD_COST NUMBER(10,2),
                    PRODUCT_STATUS VARCHAR(30)
                )
            """

        cursor.execute(create_table_sql)

        # Replace existing contents to make reruns safe.
        cursor.execute(
            f"TRUNCATE TABLE RAW.{table_name}"
        )

        cursor.execute(
            f"""
            COPY INTO RAW.{table_name}
            FROM @MASTER_DATA_STAGE/{file_path.name}.gz
            FILE_FORMAT = (FORMAT_NAME = 'MASTER_CSV_FORMAT')
            ON_ERROR = 'ABORT_STATEMENT'
            PURGE = TRUE
            """
        )

        for result in cursor.fetchall():
            print(result)

        cursor.execute(
            f"SELECT COUNT(*) FROM RAW.{table_name}"
        )

        count = cursor.fetchone()[0]

        print(f"{table_name}: {count} records loaded.")

finally:
    cursor.close()
    conn.close()

print("\nMaster data ingestion completed.")
