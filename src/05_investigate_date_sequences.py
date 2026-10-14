
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data" / "processed" / "orders_cleaned.csv"

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
        orders[column],
        errors="coerce"
    )

# Test each chronological relationship separately
checks = {
    "approval_before_purchase": (
        orders["order_approved_at"].notna()
        & (
            orders["order_approved_at"]
            < orders["order_purchase_timestamp"]
        )
    ),
    "carrier_before_approval": (
        orders["order_delivered_carrier_date"].notna()
        & orders["order_approved_at"].notna()
        & (
            orders["order_delivered_carrier_date"]
            < orders["order_approved_at"]
        )
    ),
    "delivery_before_carrier": (
        orders["order_delivered_customer_date"].notna()
        & orders["order_delivered_carrier_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_delivered_carrier_date"]
        )
    ),
}

print("DATE SEQUENCE INVESTIGATION")
print("=" * 60)

for name, condition in checks.items():
    print(f"{name}: {condition.sum()}")

# Count records that violate at least one relationship
any_violation = pd.Series(False, index=orders.index)

for condition in checks.values():
    any_violation |= condition

print("\nOrders with at least one violation:", any_violation.sum())

# Show examples for investigation
for name, condition in checks.items():
    print(f"\nEXAMPLES: {name}")
    print("-" * 60)

    columns_to_show = [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]

    print(
        orders.loc[condition, columns_to_show]
        .head(10)
        .to_string(index=False)
    )
