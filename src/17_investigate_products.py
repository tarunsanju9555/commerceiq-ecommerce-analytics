
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"

products_path = raw_dir / "olist_products_dataset.csv"
translation_path = raw_dir / "product_category_name_translation.csv"
items_path = raw_dir / "olist_order_items_dataset.csv"

products = pd.read_csv(products_path)
translations = pd.read_csv(translation_path)
items = pd.read_csv(items_path)

print("=" * 55)
print("PRODUCT DATA QUALITY INVESTIGATION")
print("=" * 55)

# 1. Missing metadata
metadata_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
]

print("\n1. MISSING METADATA")
print("Products with all four fields missing:",
      products[metadata_columns].isna().all(axis=1).sum())

print("Products with any metadata missing:",
      products[metadata_columns].isna().any(axis=1).sum())

dimension_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

print("Products with any dimension missing:",
      products[dimension_columns].isna().any(axis=1).sum())

print("\nRecords with missing dimensions:")
print(
    products.loc[
        products[dimension_columns].isna().any(axis=1),
        ["product_id"] + dimension_columns
    ].to_string(index=False)
)

# 2. Category translation coverage
print("\n2. CATEGORY TRANSLATION")
print("Translation rows:", len(translations))
print("Duplicate source category names:",
      translations["product_category_name"].duplicated().sum())

print("Products with a category:",
      products["product_category_name"].notna().sum())

category_names = set(
    products["product_category_name"].dropna()
)
translated_names = set(
    translations["product_category_name"].dropna()
)

print("Distinct product categories:", len(category_names))
print("Categories without translation:",
      len(category_names - translated_names))

print("Untranslated category examples:",
      sorted(category_names - translated_names)[:15])

# 3. Products referenced by order items
item_product_ids = set(items["product_id"])
product_ids = set(products["product_id"])

print("\n3. PRODUCT-ORDER ITEM RELATIONSHIPS")
print("Order-item rows:", len(items))
print("Distinct products referenced by items:",
      items["product_id"].nunique())
print("Distinct referenced IDs missing from product catalogue:",
      len(item_product_ids - product_ids))
print("Catalogue products never referenced by items:",
      len(product_ids - item_product_ids))

print("\nInvestigation complete.")
