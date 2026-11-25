
from pathlib import Path
import random
import pandas as pd
from faker import Faker

# --------------------------------------------------
# Configuration
# --------------------------------------------------

fake = Faker()
Faker.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Customer master data
# --------------------------------------------------

NUM_CUSTOMERS = 500

industries = [
    "Manufacturing",
    "Healthcare",
    "Financial Services",
    "Technology",
    "Retail",
    "Education",
    "Professional Services",
    "Transportation"
]

customer_segments = [
    "Enterprise",
    "Mid-Market",
    "Small Business"
]

regions = {
    "Northeast": {
        "states": ["New York", "Massachusetts", "Pennsylvania"],
        "cities": ["New York", "Boston", "Philadelphia"]
    },
    "Southeast": {
        "states": ["Florida", "Georgia", "North Carolina"],
        "cities": ["Orlando", "Atlanta", "Charlotte"]
    },
    "Midwest": {
        "states": ["Illinois", "Ohio", "Michigan"],
        "cities": ["Chicago", "Columbus", "Detroit"]
    },
    "Southwest": {
        "states": ["Texas", "Arizona", "New Mexico"],
        "cities": ["Dallas", "Phoenix", "Albuquerque"]
    },
    "West": {
        "states": ["California", "Colorado", "Washington"],
        "cities": ["Los Angeles", "Denver", "Seattle"]
    }
}

customers = []

for i in range(1, NUM_CUSTOMERS + 1):

    region = random.choice(list(regions.keys()))
    geography = regions[region]

    first_name = fake.first_name()
    last_name = fake.last_name()

    customer_type = random.choices(
        ["Individual", "Business"],
        weights=[0.35, 0.65],
        k=1
    )[0]

    if customer_type == "Business":
        company_name = fake.company()
        email = fake.company_email()
    else:
        company_name = None
        email = fake.email()

    customers.append({
        "customer_id": f"CUST-{i:04d}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "company_name": company_name,
        "customer_type": customer_type,
        "industry": random.choice(industries),
        "customer_segment": random.choice(customer_segments),
        "city": random.choice(geography["cities"]),
        "state": random.choice(geography["states"]),
        "region": region,
        "signup_date": fake.date_between(
            start_date="-5y",
            end_date="today"
        ),
        "customer_status": random.choices(
            ["Active", "Inactive"],
            weights=[0.85, 0.15],
            k=1
        )[0]
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    OUTPUT_DIR / "customers.csv",
    index=False
)

# --------------------------------------------------
# Product master data
# --------------------------------------------------

product_definitions = [
    ("Essential Product", "Accessories", 0.50),
    ("Business Product", "Accessories", 0.48),
    ("Professional Product", "Software", 0.42),
    ("Advanced Product", "Software", 0.45),
    ("Premium Product", "Hardware", 0.55),
    ("Enterprise Product", "Hardware", 0.52),
    ("Performance Product", "Hardware", 0.50),
    ("Professional Suite", "Software", 0.40),
    ("Enterprise Suite", "Software", 0.38),
    ("Executive Suite", "Software", 0.35)
]

list_prices = [
    29.99,
    49.99,
    79.99,
    119.99,
    199.99,
    249.99,
    349.99,
    499.99,
    699.99,
    999.99
]

products = []

for i, (definition, price) in enumerate(
    zip(product_definitions, list_prices),
    start=1
):

    product_name, subcategory, cost_ratio = definition

    category = (
        "Technology"
        if subcategory in ["Hardware", "Software"]
        else "Accessories"
    )

    products.append({
        "product_id": f"PROD-{i:03d}",
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "list_price": price,
        "standard_cost": round(price * cost_ratio, 2),
        "product_status": "Active"
    })

products_df = pd.DataFrame(products)

products_df.to_csv(
    OUTPUT_DIR / "products.csv",
    index=False
)

# --------------------------------------------------
# Summary
# --------------------------------------------------

print("Master data generation completed.")
print(f"Customers generated: {len(customers_df)}")
print(f"Products generated: {len(products_df)}")
print(f"Customer IDs: {customers_df['customer_id'].min()} to "
      f"{customers_df['customer_id'].max()}")
print(f"Product IDs: {products_df['product_id'].min()} to "
      f"{products_df['product_id'].max()}")
print(f"Output directory: {OUTPUT_DIR}")
