
from pathlib import Path
import pandas as pd

file_path = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "generated"
    / "sales_orders.csv"
)

df = pd.read_csv(file_path)

expected_columns = [
    "order_id",
    "customer_id",
    "product_id",
    "sales_rep_id",
    "order_date",
    "quantity",
    "unit_price",
    "discount_pct",
    "region",
    "order_status"
]

# 1. Validate structure
assert list(df.columns) == expected_columns, "Unexpected columns"

# 2. Validate record count
assert len(df) == 5000, f"Expected 5000 rows; found {len(df)}"

# 3. Validate primary key
assert df["order_id"].is_unique, "Duplicate order IDs found"
assert df["order_id"].notna().all(), "Missing order IDs"

# 4. Validate missing values
assert not df.isnull().any().any(), "Missing values found"

# 5. Validate numeric fields
assert (df["quantity"] > 0).all(), "Invalid quantity"
assert (df["unit_price"] > 0).all(), "Invalid unit price"
assert df["discount_pct"].between(0, 100).all(), "Invalid discount"

# 6. Validate dates
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="raise"
)

assert df["order_date"].between(
    "2025-01-01", "2026-11-20"
).all(), "Dates outside expected range"

# 7. Validate categorical values
valid_statuses = {
    "Completed", "Pending", "Cancelled", "Returned"
}

assert set(df["order_status"].unique()).issubset(
    valid_statuses
), "Unexpected order status"

valid_regions = {
    "Northeast", "Southeast", "Midwest",
    "Southwest", "West"
}

assert set(df["region"].unique()).issubset(
    valid_regions
), "Unexpected region"

# Results
print("SALES DATA VALIDATION PASSED")
print("--------------------------------")
print(f"Rows:             {len(df):,}")
print(f"Unique orders:    {df['order_id'].nunique():,}")
print(f"Customers:        {df['customer_id'].nunique():,}")
print(f"Products:         {df['product_id'].nunique():,}")
print(f"Sales reps:       {df['sales_rep_id'].nunique():,}")
print(f"Missing values:   {df.isnull().sum().sum()}")
print(f"Duplicate orders: {df['order_id'].duplicated().sum()}")
print(f"Date range:       {df['order_date'].min().date()} to "
      f"{df['order_date'].max().date()}")

print("\nOrder status distribution:")
print(df["order_status"].value_counts().to_string())
