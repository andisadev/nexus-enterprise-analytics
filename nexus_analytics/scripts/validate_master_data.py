
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "generated"

customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")

errors = []

# Customer validation
required_customer_columns = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "customer_type",
    "industry",
    "customer_segment",
    "city",
    "state",
    "region",
    "signup_date",
    "customer_status"
]

for column in required_customer_columns:
    if customers[column].isna().any():
        errors.append(f"Customers: NULL values in {column}")

if customers["customer_id"].duplicated().any():
    errors.append("Customers: Duplicate customer IDs")

if not customers["customer_id"].str.match(
    r"^CUST-\d{4}$"
).all():
    errors.append("Customers: Invalid customer ID format")

if not customers["customer_type"].isin(
    ["Individual", "Business"]
).all():
    errors.append("Customers: Invalid customer type")

business_customers = customers[
    customers["customer_type"] == "Business"
]

if business_customers["company_name"].isna().any():
    errors.append("Business customers must have company names")

individual_customers = customers[
    customers["customer_type"] == "Individual"
]

if individual_customers["company_name"].notna().any():
    errors.append("Individual customers should not have company names")

# Product validation
required_product_columns = [
    "product_id",
    "product_name",
    "category",
    "subcategory",
    "list_price",
    "standard_cost",
    "product_status"
]

for column in required_product_columns:
    if products[column].isna().any():
        errors.append(f"Products: NULL values in {column}")

if products["product_id"].duplicated().any():
    errors.append("Products: Duplicate product IDs")

if not products["product_id"].str.match(
    r"^PROD-\d{3}$"
).all():
    errors.append("Products: Invalid product ID format")

if (products["list_price"] <= 0).any():
    errors.append("Products: Non-positive list prices")

if (products["standard_cost"] <= 0).any():
    errors.append("Products: Non-positive standard costs")

if (products["standard_cost"] >= products["list_price"]).any():
    errors.append("Products: Standard cost must be below list price")

# Results
if errors:
    print("MASTER DATA VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("MASTER DATA VALIDATION PASSED")
print(f"Customers validated: {len(customers)}")
print(f"Business customers: {len(business_customers)}")
print(f"Individual customers: {len(individual_customers)}")
print(f"Products validated: {len(products)}")
