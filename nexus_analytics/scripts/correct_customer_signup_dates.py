from pathlib import Path
import random
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "generated"

customers_file = DATA_DIR / "customers.csv"
sales_file = DATA_DIR / "sales_orders.csv"

# Load existing synthetic data
customers = pd.read_csv(customers_file)
sales = pd.read_csv(sales_file)

customers["signup_date"] = pd.to_datetime(customers["signup_date"])
sales["order_date"] = pd.to_datetime(sales["order_date"])

# Find each customer's first order date
first_orders = (
    sales.groupby("customer_id")["order_date"]
    .min()
    .rename("first_order_date")
)

customers = customers.merge(
    first_orders,
    on="customer_id",
    how="left",
    validate="one_to_one"
)

# Correct only impossible signup dates
rng = random.Random(42)
corrected_count = 0

for index, row in customers.iterrows():

    if pd.isna(row["first_order_date"]):
        raise ValueError(
            f"No sales order found for {row['customer_id']}"
        )

    if row["signup_date"] > row["first_order_date"]:

        days_before = rng.randint(30, 1825)

        customers.at[index, "signup_date"] = (
            row["first_order_date"]
            - pd.Timedelta(days=days_before)
        )

        corrected_count += 1

# Validate corrected data
invalid_dates = (
    customers["signup_date"] > customers["first_order_date"]
).sum()

if invalid_dates > 0:
    raise ValueError(
        f"Validation failed: {invalid_dates} invalid signup dates"
    )

# Save only the original customer columns
customers = customers.drop(columns=["first_order_date"])

customers["signup_date"] = (
    customers["signup_date"].dt.strftime("%Y-%m-%d")
)

customers.to_csv(customers_file, index=False)

print("CUSTOMER DATE CORRECTION COMPLETE")
print(f"Customers processed: {len(customers)}")
print(f"Signup dates corrected: {corrected_count}")
print(f"Invalid signup dates remaining: {invalid_dates}")