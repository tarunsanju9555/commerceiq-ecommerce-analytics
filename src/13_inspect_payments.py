
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "olist_order_payments_dataset.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("PAYMENTS DATA INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate order-payment keys:")
print(
    df.duplicated(
        subset=["order_id", "payment_sequential"]
    ).sum()
)

print("\nPayment types:")
print(df["payment_type"].value_counts(dropna=False))

print("\nPayment installments:")
print(df["payment_installments"].describe())

print("\nPayment value:")
print(df["payment_value"].describe())

print("\nSample records:")
print(df.head())
