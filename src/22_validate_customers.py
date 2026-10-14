
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

raw_dir = project_root / "data" / "raw"
processed_dir = project_root / "data" / "processed"

customers_path = raw_dir / "olist_customers_dataset.csv"
orders_path = processed_dir / "orders_validated.csv"

customers = pd.read_csv(customers_path)
orders = pd.read_csv(orders_path)

print("=" * 55)
print("CUSTOMER DATA QUALITY VALIDATION")
print("=" * 55)

# 1. Customer key validation
print("\n1. CUSTOMER KEYS")
print("Customer records:", len(customers))
print("Unique customer IDs:", customers["customer_id"].nunique())
print("Unique underlying customers:",
      customers["customer_unique_id"].nunique())

# 2. Repeated underlying customers
records_per_unique_customer = (
    customers.groupby("customer_unique_id")["customer_id"].nunique()
)

print("\n2. REPEATED CUSTOMERS")
print("Unique customers with multiple customer IDs:",
      (records_per_unique_customer > 1).sum())
print("Maximum customer IDs for one unique customer:",
      records_per_unique_customer.max())

# 3. Check customer-order relationship
customer_ids = set(customers["customer_id"])
order_customer_ids = set(orders["customer_id"])

print("\n3. ORDER RELATIONSHIPS")
print("Orders referencing known customer IDs:",
      orders["customer_id"].isin(customer_ids).sum())
print("Orders referencing unknown customer IDs:",
      (~orders["customer_id"].isin(customer_ids)).sum())
print("Customer IDs with no order record:",
      len(customer_ids - order_customer_ids))

# 4. Geographic data quality
print("\n4. GEOGRAPHIC FIELDS")
print("Distinct states:", customers["customer_state"].nunique())
print("Distinct cities:", customers["customer_city"].nunique())
print("Distinct ZIP prefixes:",
      customers["customer_zip_code_prefix"].nunique())

print("\nCustomer state totals:")
print(customers["customer_state"].value_counts().to_string())

print("\nValidation complete.")
