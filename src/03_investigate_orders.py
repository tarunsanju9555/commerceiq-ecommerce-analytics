
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# Find orders marked delivered without a delivery timestamp
mask = (
    orders["order_status"].eq("delivered")
    & orders["order_delivered_customer_date"].isna()
)

anomalies = orders.loc[mask].copy()

print("DELIVERED ORDERS WITH MISSING DELIVERY DATES")
print("=" * 60)
print("Number of records:", len(anomalies))

print(
    anomalies[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    ].to_string(index=False)
)

# Check whether the preceding order milestones are missing
print("\nMISSING MILESTONES IN THESE RECORDS")
print("=" * 60)
print(
    anomalies[
        [
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
        ]
    ].isna().sum()
)

# Save the anomalous records for investigation
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

anomalies.to_csv(
    OUTPUT_DIR / "delivered_orders_missing_dates.csv",
    index=False
)

print("\nAnomaly report saved successfully.")
