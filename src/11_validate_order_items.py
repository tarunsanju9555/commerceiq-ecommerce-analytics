
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

items_path = (
    project_root
    / "data"
    / "raw"
    / "olist_order_items_dataset.csv"
)

orders_path = (
    project_root
    / "data"
    / "processed"
    / "orders_validated.csv"
)

items = pd.read_csv(items_path)
orders = pd.read_csv(orders_path)

print("=" * 55)
print("ORDER ITEMS DATA QUALITY VALIDATION")
print("=" * 55)

# 1. Verify the composite key.
print("\n1. KEY VALIDATION")
print("Rows:", len(items))
print("Unique order-item keys:",
      items[["order_id", "order_item_id"]]
      .drop_duplicates().shape[0])
print("Order IDs in item data:", items["order_id"].nunique())

# 2. Check relationships with the orders dataset.
order_ids = set(orders["order_id"])
item_order_ids = set(items["order_id"])

print("\n2. ORDER RELATIONSHIPS")
print("Item records whose order exists:",
      items["order_id"].isin(order_ids).sum())
print("Item records with unknown order:",
      (~items["order_id"].isin(order_ids)).sum())
print("Orders with items:", len(item_order_ids))
print("Orders without items:", len(order_ids - item_order_ids))

# 3. Validate numeric values.
print("\n3. NUMERIC VALIDATION")
print("Price <= 0:", (items["price"] <= 0).sum())
print("Freight < 0:", (items["freight_value"] < 0).sum())
print("Missing prices:", items["price"].isna().sum())
print("Missing freight:", items["freight_value"].isna().sum())

# 4. Inspect item counts per order.
items_per_order = items.groupby("order_id").size()

print("\n4. ITEMS PER ORDER")
print("Minimum:", items_per_order.min())
print("Median:", items_per_order.median())
print("Maximum:", items_per_order.max())
print("Orders with multiple items:",
      (items_per_order > 1).sum())

# 5. Check the sequence of item numbers.
sequence_check = items.groupby("order_id")["order_item_id"].agg(
    ["min", "max", "nunique", "count"]
)

sequence_check["sequence_mismatch"] = (
    (sequence_check["min"] != 1)
    | (sequence_check["max"] != sequence_check["count"])
    | (sequence_check["nunique"] != sequence_check["count"])
)

print("\n5. ITEM NUMBER SEQUENCE")
print("Orders with non-contiguous or unusual item numbering:",
      sequence_check["sequence_mismatch"].sum())

print("\nValidation complete.")
