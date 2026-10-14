
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data" / "processed" / "orders_cleaned.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

orders = pd.read_csv(DATA_PATH)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column], errors="coerce"
    )

# Create separate, explicit anomaly flags
orders["flag_carrier_before_approval"] = (
    orders["order_delivered_carrier_date"].notna()
    & orders["order_approved_at"].notna()
    & (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )
)

orders["flag_delivery_before_carrier"] = (
    orders["order_delivered_customer_date"].notna()
    & orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )
)

orders["flag_delivered_missing_delivery_date"] = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_customer_date"].isna()
)

# Preserve records; do not delete or invent timestamps
print("ORDERS VALIDATION SUMMARY")
print("=" * 50)
print("Total rows:", len(orders))
print("Unique order IDs:", orders["order_id"].nunique())
print(
    "Carrier before approval:",
    orders["flag_carrier_before_approval"].sum()
)
print(
    "Delivery before carrier:",
    orders["flag_delivery_before_carrier"].sum()
)
print(
    "Delivered but missing delivery date:",
    orders["flag_delivered_missing_delivery_date"].sum()
)

# Save a separate validated copy
output_path = OUTPUT_DIR / "orders_validated.csv"
orders.to_csv(output_path, index=False)

print("\nValidated file saved:", output_path)
