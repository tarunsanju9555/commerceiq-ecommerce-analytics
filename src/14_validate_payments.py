
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

payments_path = (
    project_root
    / "data"
    / "raw"
    / "olist_order_payments_dataset.csv"
)

orders_path = (
    project_root
    / "data"
    / "processed"
    / "orders_validated.csv"
)

items_path = (
    project_root
    / "data"
    / "raw"
    / "olist_order_items_dataset.csv"
)

payments = pd.read_csv(payments_path)
orders = pd.read_csv(orders_path)
items = pd.read_csv(items_path)

print("=" * 55)
print("PAYMENTS DATA QUALITY VALIDATION")
print("=" * 55)

# 1. Payment-to-order relationship
order_ids = set(orders["order_id"])

print("\n1. ORDER RELATIONSHIPS")
print("Payment records:", len(payments))
print("Unique orders with payments:", payments["order_id"].nunique())
print(
    "Payments with unknown order IDs:",
    (~payments["order_id"].isin(order_ids)).sum()
)

print(
    "Orders without payment records:",
    len(order_ids - set(payments["order_id"]))
)

# 2. Unusual numerical values
print("\n2. NUMERIC VALIDATION")
print("Zero installments:", (payments["payment_installments"] == 0).sum())
print("Negative installments:", (payments["payment_installments"] < 0).sum())
print("Zero payment values:", (payments["payment_value"] == 0).sum())
print("Negative payment values:", (payments["payment_value"] < 0).sum())

# 3. Payment type investigation
print("\n3. PAYMENT TYPE VALIDATION")
print(payments["payment_type"].value_counts(dropna=False))

# 4. Orders with multiple payment records
payments_per_order = payments.groupby("order_id").size()

print("\n4. PAYMENTS PER ORDER")
print("Minimum:", payments_per_order.min())
print("Median:", payments_per_order.median())
print("Maximum:", payments_per_order.max())
print("Orders with multiple payment records:", (payments_per_order > 1).sum())

# 5. Compare order-level totals without multiplying item rows.
payment_totals = payments.groupby("order_id")["payment_value"].sum()
item_totals = items.groupby("order_id").agg(
    item_price_total=("price", "sum"),
    freight_total=("freight_value", "sum"),
)

comparison = item_totals.join(payment_totals.rename("payment_total"), how="outer")

comparison["payment_minus_items_and_freight"] = (
    comparison["payment_total"]
    - comparison["item_price_total"]
    - comparison["freight_total"]
)

print("\n5. PAYMENT VS ITEM TOTALS")
print("Orders in comparison:", len(comparison))
print("Orders with payment records:", comparison["payment_total"].notna().sum())
print("Orders with item records:", comparison["item_price_total"].notna().sum())
print(
    "Orders with absolute difference > 0.01:",
    (
        comparison["payment_minus_items_and_freight"].abs() > 0.01
    ).sum()
)

print("\nLargest absolute differences:")
print(
    comparison.loc[
        comparison["payment_minus_items_and_freight"].abs().nlargest(10).index,
        [
            "item_price_total",
            "freight_total",
            "payment_total",
            "payment_minus_items_and_freight",
        ],
    ].to_string()
)

print("\nValidation complete.")
