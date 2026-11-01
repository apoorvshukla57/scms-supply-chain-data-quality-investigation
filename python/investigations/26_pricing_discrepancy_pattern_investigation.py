
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. Paths and source loading
# --------------------------------------------------
PROJECT_DIR = Path(r"C:\Project_03")
SOURCE_FILE = PROJECT_DIR / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT_DIR = PROJECT_DIR / "publication" / "execution" / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not SOURCE_FILE.exists():
    raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

df = pd.read_csv(SOURCE_FILE, low_memory=False)

# Normalize headers for reliable column selection.
column_lookup = {
    str(column).replace("\ufeff", "").strip().lower(): column
    for column in df.columns
}

def get_column(name):
    key = name.strip().lower()
    if key not in column_lookup:
        raise KeyError(
            f"Required column not found: {name}\n"
            f"Available columns: {list(df.columns)}"
        )
    return column_lookup[key]

required_columns = [
    "id",
    "product group",
    "vendor",
    "unit of measure (per pack)",
    "unit price",
    "pack price",
]

for column in required_columns:
    get_column(column)

# --------------------------------------------------
# 2. Prepare the pricing comparison
# --------------------------------------------------
work = pd.DataFrame({
    "source_id": df[get_column("id")],
    "product_group": df[get_column("product group")],
    "vendor": df[get_column("vendor")],
    "uom": pd.to_numeric(
        df[get_column("unit of measure (per pack)")],
        errors="coerce",
    ),
    "unit_price": pd.to_numeric(
        df[get_column("unit price")],
        errors="coerce",
    ),
    "pack_price": pd.to_numeric(
        df[get_column("pack price")],
        errors="coerce",
    ),
})

# Keep original category labels but make missing groups explicit.
for column in ["product_group", "vendor"]:
    work[column] = (
        work[column]
        .astype("string")
        .str.strip()
        .fillna("[Missing]")
        .replace("", "[Missing]")
    )

work["uom_valid"] = work["uom"].notna() & work["uom"].gt(0)

work["comparable"] = (
    work["uom_valid"]
    & work["unit_price"].notna()
    & work["pack_price"].notna()
)

work["expected_pack_price"] = (
    work["unit_price"] * work["uom"]
)

work["signed_difference"] = (
    work["pack_price"] - work["expected_pack_price"]
)

work["absolute_difference"] = work["signed_difference"].abs()

TOLERANCE = 0.02

work["mismatch"] = (
    work["comparable"]
    & work["absolute_difference"].gt(TOLERANCE)
)

# Relative difference uses recorded pack price as the denominator.
# It is undefined when recorded pack price is zero.
work["relative_difference_pct"] = (
    work["absolute_difference"]
    .div(work["pack_price"].abs().where(work["pack_price"].ne(0)))
    .mul(100)
)

work["uom_group"] = work["uom"].map(
    lambda value: str(value) if pd.notna(value) else "[Invalid or missing]"
)

# --------------------------------------------------
# 3. Reusable grouped summary
# --------------------------------------------------
def summarize_by(group_column):
    summary = (
        work.groupby(group_column, dropna=False)
        .agg(
            total_records=("source_id", "size"),
            comparable_records=("comparable", "sum"),
            mismatch_records=("mismatch", "sum"),
            median_absolute_difference=("absolute_difference", "median"),
            median_relative_difference_pct=("relative_difference_pct", "median"),
        )
        .reset_index()
    )

    summary["mismatch_rate_pct"] = (
        summary["mismatch_records"]
        .div(summary["comparable_records"].where(
            summary["comparable_records"].ne(0)
        ))
        .mul(100)
    )

    return summary.sort_values(
        ["mismatch_records", "comparable_records"],
        ascending=False,
    )

# --------------------------------------------------
# 4. Overall reconciliation
# --------------------------------------------------
total_records = len(work)
comparable_records = int(work["comparable"].sum())
mismatch_records = int(work["mismatch"].sum())
excluded_records = total_records - comparable_records

overall = pd.DataFrame([{
    "source_records": total_records,
    "comparable_records": comparable_records,
    "excluded_from_formula_test": excluded_records,
    "mismatch_records": mismatch_records,
    "matching_records_within_tolerance": comparable_records - mismatch_records,
    "mismatch_rate_pct_of_comparable": (
        mismatch_records / comparable_records * 100
        if comparable_records else 0
    ),
    "tolerance": TOLERANCE,
    "formula_status": "Investigative hypothesis; not a confirmed business rule",
}])

# --------------------------------------------------
# 5. Summaries by product, vendor and pack size
# --------------------------------------------------
by_product = summarize_by("product_group")
by_vendor = summarize_by("vendor")
by_uom = summarize_by("uom_group")

# Save complete results, not just the terminal's top rows.
overall.to_csv(
    OUTPUT_DIR / "pricing_discrepancy_overall.csv",
    index=False,
    encoding="utf-8-sig",
)

by_product.to_csv(
    OUTPUT_DIR / "pricing_discrepancy_by_product_group.csv",
    index=False,
    encoding="utf-8-sig",
)

by_vendor.to_csv(
    OUTPUT_DIR / "pricing_discrepancy_by_vendor.csv",
    index=False,
    encoding="utf-8-sig",
)

by_uom.to_csv(
    OUTPUT_DIR / "pricing_discrepancy_by_uom.csv",
    index=False,
    encoding="utf-8-sig",
)

# Record-level exceptions with original IDs for traceability.
exceptions = work.loc[work["mismatch"]].copy()

exceptions = exceptions[[
    "source_id",
    "product_group",
    "vendor",
    "uom",
    "unit_price",
    "pack_price",
    "expected_pack_price",
    "signed_difference",
    "absolute_difference",
    "relative_difference_pct",
]]

exceptions.to_csv(
    OUTPUT_DIR / "pricing_discrepancy_records.csv",
    index=False,
    encoding="utf-8-sig",
)

# --------------------------------------------------
# 6. Basic output validation
# --------------------------------------------------
assert total_records == len(df)
assert comparable_records + excluded_records == total_records
assert mismatch_records <= comparable_records
assert len(exceptions) == mismatch_records
assert exceptions["source_id"].notna().all()

print("\nPRICING DISCREPANCY INVESTIGATION")
print("=" * 72)
print(f"Source records: {total_records:,}")
print(f"Comparable records: {comparable_records:,}")
print(f"Excluded from formula test: {excluded_records:,}")
print(f"Discrepancies above ${TOLERANCE:.2f}: {mismatch_records:,}")
print(
    "Mismatch rate among comparable records: "
    f"{overall.loc[0, 'mismatch_rate_pct_of_comparable']:.2f}%"
)

print("\nBY PRODUCT GROUP")
print(by_product.head(10).to_string(index=False))

print("\nTOP 10 VENDORS BY DISCREPANCY COUNT")
print(by_vendor.head(10).to_string(index=False))

print("\nTOP 10 PACK SIZES BY DISCREPANCY COUNT")
print(by_uom.head(10).to_string(index=False))

print("\nOUTPUT VALIDATION")
print(f"Exception rows: {len(exceptions):,}")
print("Record counts reconcile: PASSED")
print("Exception count reconciles: PASSED")
print(f"Output folder: {OUTPUT_DIR}")
print("Reminder: discrepancies are not confirmed pricing errors.")
