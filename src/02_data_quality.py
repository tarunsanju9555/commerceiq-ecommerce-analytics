
from pathlib import Path
import pandas as pd

# 1. Locate the raw data
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

orders_path = RAW_DIR / "olist_orders_dataset.csv"

if not orders_path.exists():
    raise FileNotFoundError(f"File not found: {orders_path}")

# 2. Load the data
orders = pd.read_csv(orders_path)

# 3. Convert timestamp columns to datetime
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

# 4. Check missing values by order status
missing_delivery = (
    orders.groupby("order_status")[
        "order_delivered_customer_date"
    ]
    .agg(
        total_orders="size",
        missing_delivery_dates=lambda s: s.isna().sum()
    )
)

missing_delivery["missing_percentage"] = (
    missing_delivery["missing_delivery_dates"]
    / missing_delivery["total_orders"]
    * 100
).round(2)

print("\nMISSING DELIVERY DATES BY ORDER STATUS")
print("=" * 60)
print(missing_delivery)

# 5. Create a general data-quality summary
quality_report = pd.DataFrame({
    "data_type": orders.dtypes.astype(str),
    "missing_count": orders.isna().sum(),
    "missing_percentage": (
        orders.isna().mean() * 100
    ).round(2),
    "unique_values": orders.nunique(dropna=True),
})

print("\nGENERAL DATA QUALITY REPORT")
print("=" * 60)
print(quality_report)

# 6. Check for duplicate order IDs
print("\nDUPLICATE ORDER IDs")
print("=" * 60)
print(orders["order_id"].duplicated().sum())

# 7. Save the report, not the cleaned dataset yet
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

report_path = OUTPUT_DIR / "orders_quality_report.csv"
quality_report.to_csv(report_path, index=True, index_label="column")

print(f"\nQuality report saved to: {report_path}")
