
from pathlib import Path
import random
import pandas as pd
from faker import Faker

# Reproducible synthetic data
fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_ORDERS = 5000

regions = [
    "Northeast",
    "Southeast",
    "Midwest",
    "Southwest",
    "West"
]

products = {
    "PROD-001": 29.99,
    "PROD-002": 49.99,
    "PROD-003": 79.99,
    "PROD-004": 119.99,
    "PROD-005": 199.99,
    "PROD-006": 249.99,
    "PROD-007": 349.99,
    "PROD-008": 499.99,
    "PROD-009": 699.99,
    "PROD-010": 999.99
}

customers = [f"CUST-{i:04d}" for i in range(1, 501)]
sales_reps = [f"REP-{i:03d}" for i in range(1, 31)]

statuses = ["Completed", "Pending", "Cancelled", "Returned"]
status_weights = [0.78, 0.12, 0.06, 0.04]

orders = []

for i in range(1, NUM_ORDERS + 1):
    product_id = random.choice(list(products.keys()))
    unit_price = products[product_id]

    order = {
        "order_id": f"ORD-{i:06d}",
        "customer_id": random.choice(customers),
        "product_id": product_id,
        "sales_rep_id": random.choice(sales_reps),
        "order_date": fake.date_between(
            start_date=pd.Timestamp("2025-01-01").date(),
            end_date=pd.Timestamp("2026-11-20").date()
        ).isoformat(),
        "quantity": random.randint(1, 25),
        "unit_price": unit_price,
        "discount_pct": random.choices(
            [0, 5, 10, 15, 20, 25],
            weights=[30, 15, 25, 15, 10, 5]
        )[0],
        "region": random.choice(regions),
        "order_status": random.choices(
            statuses,
            weights=status_weights
        )[0]
    }

    orders.append(order)

df = pd.DataFrame(orders)

output_path = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "generated"
    / "sales_orders.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print(f"Generated {len(df):,} sales orders.")
print(f"Output file: {output_path}")
print(f"Unique orders: {df['order_id'].nunique():,}")
print(f"Date range: {df['order_date'].min()} to {df['order_date'].max()}")
print(f"Total gross sales: ${(
    df['quantity'] * df['unit_price']
).sum():,.2f}")

print("\nOrder status distribution:")
print(df["order_status"].value_counts())

print("\nSample records:")
print(df.head())
