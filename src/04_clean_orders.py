
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load the original data
orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

original_rows = len(orders)

# 2. Convert timestamp columns safely
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

# Remember which date values were originally missing
original_missing = orders[date_columns].isna().copy()

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# 3. Detect parsing failures separately from original missing values
parse_failures = {}

for column in date_columns:
    parse_failures[column] = (
        orders[column].isna() & ~original_missing[column]
    ).sum()

print("DATE PARSING FAILURES")
print("=" * 50)

for column, count in parse_failures.items():
    print(f"{column}: {count}")

# 4. Check primary-key candidate
duplicate_order_ids = orders["order_id"].duplicated().sum()

print("\nDUPLICATE ORDER IDs:", duplicate_order_ids)

if duplicate_order_ids > 0:
    raise ValueError(
        "Duplicate order IDs found. Investigate before proceeding."
    )

# 5. Flag delivered orders missing delivery timestamps
orders["quality_flag_missing_delivery_date"] = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_customer_date"].isna()
)

orders["quality_flag_missing_carrier_date"] = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_carrier_date"].isna()
)

# 6. Validate chronological order milestones
orders["quality_flag_invalid_date_order"] = (
    (
        orders["order_approved_at"].notna()
        & (
            orders["order_approved_at"]
            < orders["order_purchase_timestamp"]
        )
    )
    |
    (
        orders["order_delivered_carrier_date"].notna()
        & orders["order_approved_at"].notna()
        & (
            orders["order_delivered_carrier_date"]
            < orders["order_approved_at"]
        )
    )
    |
    (
        orders["order_delivered_customer_date"].notna()
        & orders["order_delivered_carrier_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_delivered_carrier_date"]
        )
    )
)

# 7. Confirm that the row count is unchanged
assert len(orders) == original_rows

# 8. Save the validated dataset
output_path = OUTPUT_DIR / "orders_cleaned.csv"
orders.to_csv(output_path, index=False)

print("\nCLEANING SUMMARY")
print("=" * 50)
print("Original rows:", original_rows)
print("Output rows:", len(orders))
print("Duplicate order IDs:", duplicate_order_ids)
print(
    "Delivered orders missing delivery date:",
    orders["quality_flag_missing_delivery_date"].sum()
)
print(
    "Delivered orders missing carrier date:",
    orders["quality_flag_missing_carrier_date"].sum()
)
print(
    "Invalid chronological sequences:",
    orders["quality_flag_invalid_date_order"].sum()
)
print("Saved to:", output_path)
