
import pandas as pd
from pathlib import Path

# ============================================================
# 1. PATHS
# ============================================================

PROJECT_DIR = Path(r"C:\Project_03")
DATA_PATH = (
    PROJECT_DIR
    / "dataset"
    / "Suppy_Chain_Shipment_Data.csv"
)
OUTPUT_DIR = PROJECT_DIR / "publication" / "execution" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. LOAD AND VALIDATE SOURCE
# ============================================================

df = pd.read_csv(DATA_PATH, low_memory=False)

required = [
    "id",
    "product group",
    "vendor",
    "item description",
    "country",
    "line item quantity",
    "unit price",
    "pack price",
    "line item value",
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Required columns missing: {missing}")

# Numeric working copies; original columns remain unchanged.
numeric_cols = [
    "line item quantity",
    "unit price",
    "pack price",
    "line item value",
]

for col in numeric_cols:
    df[f"{col}_numeric"] = pd.to_numeric(
        df[col], errors="coerce"
    )

zero_unit = df["unit price_numeric"].eq(0)
zero_pack = df["pack price_numeric"].eq(0)
zero_line = df["line item value_numeric"].eq(0)

# ============================================================
# 3. OVERALL ZERO-PRICE RELATIONSHIPS
# ============================================================

print("=" * 65)
print("ZERO UNIT-PRICE INVESTIGATION")
print("=" * 65)
print(f"Source records: {len(df):,}")
print(f"Zero unit price: {zero_unit.sum():,}")
print(f"Zero pack price: {zero_pack.sum():,}")
print(f"Zero line-item value: {zero_line.sum():,}")

print("\nZero-price overlap:")
print(f"Zero unit AND zero pack: {(zero_unit & zero_pack).sum():,}")
print(
    "Zero unit AND zero line value: "
    f"{(zero_unit & zero_line).sum():,}"
)
print(
    "Zero unit, positive pack: "
    f"{(zero_unit & df['pack price_numeric'].gt(0)).sum():,}"
)
print(
    "Zero unit, positive line value: "
    f"{(zero_unit & df['line item value_numeric'].gt(0)).sum():,}"
)

# ============================================================
# 4. EXPORT RECORD-LEVEL EVIDENCE
# ============================================================

detail_cols = [
    "id",
    "product group",
    "vendor",
    "item description",
    "country",
    "line item quantity",
    "unit price",
    "pack price",
    "line item value",
]

zero_unit_records = df.loc[zero_unit, detail_cols].copy()

detail_path = OUTPUT_DIR / "zero_unit_price_records.csv"
zero_unit_records.to_csv(detail_path, index=False)

# ============================================================
# 5. PRODUCT-LEVEL PATTERNS
# ============================================================

product_summary = (
    df.assign(zero_unit_price=zero_unit)
    .groupby(
        ["product group", "item description"],
        dropna=False,
    )
    .agg(
        total_records=("id", "size"),
        zero_unit_price_records=("zero_unit_price", "sum"),
        distinct_vendors=("vendor", "nunique"),
        distinct_countries=("country", "nunique"),
    )
    .reset_index()
)

product_summary["zero_unit_price_pct"] = (
    product_summary["zero_unit_price_records"]
    / product_summary["total_records"]
    * 100
).round(2)

product_summary = product_summary[
    product_summary["zero_unit_price_records"] > 0
].sort_values(
    ["zero_unit_price_records", "total_records"],
    ascending=[False, False],
)

product_path = OUTPUT_DIR / "zero_unit_price_by_product.csv"
product_summary.to_csv(product_path, index=False)

# ============================================================
# 6. PRODUCT GROUP SUMMARY
# ============================================================

group_summary = (
    df.assign(zero_unit_price=zero_unit)
    .groupby("product group", dropna=False)
    .agg(
        total_records=("id", "size"),
        zero_unit_price_records=("zero_unit_price", "sum"),
        distinct_countries=("country", "nunique"),
        distinct_vendors=("vendor", "nunique"),
    )
    .reset_index()
)

group_summary["zero_unit_price_pct"] = (
    group_summary["zero_unit_price_records"]
    / group_summary["total_records"]
    * 100
).round(2)

group_path = OUTPUT_DIR / "zero_unit_price_by_group.csv"
group_summary.to_csv(group_path, index=False)

# ============================================================
# 7. COMPARABLE POSITIVE-PRICE RECORDS
# ============================================================

# Compare records within the same product description.
# This identifies variation, not proof of an error.
positive_unit = df["unit price_numeric"].gt(0)

positive_summary = (
    df.loc[positive_unit]
    .groupby(
        ["product group", "item description"],
        dropna=False,
    )
    .agg(
        positive_price_records=("id", "size"),
        minimum_positive_unit_price=("unit price_numeric", "min"),
        median_positive_unit_price=("unit price_numeric", "median"),
        maximum_positive_unit_price=("unit price_numeric", "max"),
        positive_price_vendors=("vendor", "nunique"),
    )
    .reset_index()
)

comparison = product_summary.merge(
    positive_summary,
    on=["product group", "item description"],
    how="left",
)

comparison_path = (
    OUTPUT_DIR / "zero_unit_price_positive_comparison.csv"
)
comparison.to_csv(comparison_path, index=False)

# ============================================================
# 8. REPORT
# ============================================================

print("\nZero-unit-price records by product group:")
print(
    group_summary.loc[
        group_summary["zero_unit_price_records"] > 0
    ].to_string(index=False)
)

print("\nProducts with the most zero-unit-price records:")
print(product_summary.head(15).to_string(index=False))

print("\nRecords exported:")
print(f"Detail: {detail_path}")
print(f"Product summary: {product_path}")
print(f"Group summary: {group_path}")
print(f"Positive-price comparison: {comparison_path}")

print("\nInvestigation complete. Raw source remains unchanged.")
