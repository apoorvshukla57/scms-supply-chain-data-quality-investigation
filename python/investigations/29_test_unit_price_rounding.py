
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(r"C:\Project_03")
SOURCE_FILE = PROJECT_DIR / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT_DIR = PROJECT_DIR / "publication" / "execution" / "outputs"
TOLERANCE = 0.02

df = pd.read_csv(SOURCE_FILE, low_memory=False)

lookup = {
    str(c).replace("\ufeff", "").strip().lower(): c
    for c in df.columns
}

def col(name):
    key = name.strip().lower()
    if key not in lookup:
        raise KeyError(f"Required column not found: {name}")
    return lookup[key]

work = pd.DataFrame({
    "id": df[col("id")],
    "product_group": df[col("product group")],
    "vendor": df[col("vendor")],
    "uom": pd.to_numeric(
        df[col("unit of measure (per pack)")], errors="coerce"
    ),
    "unit_price": pd.to_numeric(
        df[col("unit price")], errors="coerce"
    ),
    "pack_price": pd.to_numeric(
        df[col("pack price")], errors="coerce"
    ),
})

work["product_group"] = (
    work["product_group"].astype("string").str.strip()
    .fillna("[Missing]").replace("", "[Missing]")
)

work["comparable"] = (
    work["uom"].notna()
    & work["uom"].gt(0)
    & work["unit_price"].notna()
    & work["pack_price"].notna()
)

work["expected_pack_price"] = work["uom"] * work["unit_price"]
work["absolute_difference"] = (
    work["pack_price"] - work["expected_pack_price"]
).abs()

work["mismatch"] = (
    work["comparable"]
    & work["absolute_difference"].gt(TOLERANCE)
)

# Hypothesis: unit price may be the pack price divided by UOM,
# rounded to two decimal places.
work["implied_unit_price"] = (
    work["pack_price"].div(work["uom"].where(work["uom"].gt(0)))
)

work["implied_unit_price_rounded_2dp"] = (
    work["implied_unit_price"].round(2)
)

work["unit_price_matches_rounded_implied"] = (
    work["comparable"]
    & work["implied_unit_price_rounded_2dp"].eq(
        work["unit_price"].round(2)
    )
)

# Same test for records flagged by the original formula.
work["rounding_match_among_mismatches"] = (
    work["mismatch"]
    & work["unit_price_matches_rounded_implied"]
)

# --------------------------------------------------
# Overall summary
# --------------------------------------------------
overall = pd.DataFrame([{
    "source_records": len(work),
    "comparable_records": int(work["comparable"].sum()),
    "formula_mismatches": int(work["mismatch"].sum()),
    "all_comparable_records_matching_rounded_implied_unit_price": int(
        work["unit_price_matches_rounded_implied"].sum()
    ),
    "flagged_records_matching_rounded_implied_unit_price": int(
        work["rounding_match_among_mismatches"].sum()
    ),
}])

overall["pct_of_flagged_records_matching_rounding_test"] = (
    overall["flagged_records_matching_rounded_implied_unit_price"]
    / overall["formula_mismatches"] * 100
)

# --------------------------------------------------
# Breakdown by product group and original flag status
# --------------------------------------------------
group_summary = (
    work[work["comparable"]]
    .groupby(["product_group", "mismatch"], dropna=False)
    .agg(
        records=("id", "size"),
        rounding_matches=("unit_price_matches_rounded_implied", "sum"),
    )
    .reset_index()
)

group_summary["rounding_match_rate_pct"] = (
    group_summary["rounding_matches"] / group_summary["records"] * 100
)

# --------------------------------------------------
# Inspect representative flagged records
# --------------------------------------------------
examples = work[work["mismatch"]].copy()

examples["rounding_test_result"] = (
    examples["unit_price_matches_rounded_implied"]
    .map({True: "Matches 2dp rounding hypothesis",
          False: "Does not match 2dp rounding hypothesis"})
)

examples = examples[[
    "id", "product_group", "vendor", "uom",
    "unit_price", "pack_price", "expected_pack_price",
    "absolute_difference", "implied_unit_price",
    "implied_unit_price_rounded_2dp", "rounding_test_result",
]]

# Show both matching and nonmatching examples.
matching_examples = examples[
    examples["rounding_test_result"] == "Matches 2dp rounding hypothesis"
].head(15)

nonmatching_examples = examples[
    examples["rounding_test_result"] == "Does not match 2dp rounding hypothesis"
].head(15)

overall.to_csv(
    OUTPUT_DIR / "pricing_rounding_hypothesis_overall.csv",
    index=False, encoding="utf-8-sig"
)

group_summary.to_csv(
    OUTPUT_DIR / "pricing_rounding_hypothesis_by_group.csv",
    index=False, encoding="utf-8-sig"
)

examples.to_csv(
    OUTPUT_DIR / "pricing_rounding_hypothesis_record_checks.csv",
    index=False, encoding="utf-8-sig"
)

assert len(work) == 10324
assert int(work["mismatch"].sum()) == 7774

print("\nROUNDING HYPOTHESIS: OVERALL")
print("=" * 85)
print(overall.to_string(index=False))

print("\nROUNDING MATCH RATE BY PRODUCT GROUP AND ORIGINAL FLAG STATUS")
print("=" * 85)
print(group_summary.to_string(index=False))

print("\nEXAMPLES: FLAGGED RECORDS THAT MATCH THE ROUNDING HYPOTHESIS")
print("=" * 85)
print(matching_examples.to_string(index=False))

print("\nEXAMPLES: FLAGGED RECORDS THAT DO NOT MATCH THE ROUNDING HYPOTHESIS")
print("=" * 85)
print(nonmatching_examples.to_string(index=False))

print("\nValidation: source row count and original mismatch count reconciled.")
print(f"Outputs saved to: {OUTPUT_DIR}")
print("Important: a rounding match supports a hypothesis; it does not prove the source's calculation method.")
