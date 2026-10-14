
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"

sellers = pd.read_csv(raw_dir / "olist_sellers_dataset.csv")
items = pd.read_csv(raw_dir / "olist_order_items_dataset.csv")

print("=" * 55)
print("SELLER DATA QUALITY VALIDATION")
print("=" * 55)

# 1. Seller key validation
print("\n1. SELLER KEYS")
print("Seller records:", len(sellers))
print("Unique seller IDs:", sellers["seller_id"].nunique())

# 2. Seller-to-order-item relationships
seller_ids = set(sellers["seller_id"])
item_seller_ids = set(items["seller_id"])

print("\n2. ORDER ITEM RELATIONSHIPS")
print("Order-item rows:", len(items))
print("Distinct sellers referenced by items:",
      items["seller_id"].nunique())
print("Item records with known sellers:",
      items["seller_id"].isin(seller_ids).sum())
print("Item records with unknown sellers:",
      (~items["seller_id"].isin(seller_ids)).sum())
print("Distinct referenced seller IDs missing from catalogue:",
      len(item_seller_ids - seller_ids))
print("Catalogue sellers never referenced by items:",
      len(seller_ids - item_seller_ids))

# 3. Seller geographic coverage
print("\n3. GEOGRAPHIC COVERAGE")
print("Distinct states:", sellers["seller_state"].nunique())
print("Distinct cities:", sellers["seller_city"].nunique())
print("Distinct ZIP prefixes:",
      sellers["seller_zip_code_prefix"].nunique())

print("\nValidation complete.")
