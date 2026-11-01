
from pathlib import Path

import pandas as pd


# ============================================================
# 30 | Investigate Quantity × Pack Price vs Line Item Value
# ============================================================

BASE_DIR = Path(r"C:\Project_03")
DATA_FILE = BASE_DIR / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT_DIR = BASE_DIR / "publication" / "execution" / "outputs"

TOLERANCE = 0.02
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 1. Load source data without modifying the original CSV
# ------------------------------------------------------------

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Source CSV not found: {DATA_FILE}")

try:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
except UnicodeDecodeError:
    df = pd.read_csv(DATA_FILE, encoding="cp1252", low_memory=False)


# Normalize headers for matching only.
# The original column names and source file remain unchanged.
def normalize_header(name):
    return " ".join(
        str(name)
        .replace("\ufeff", "")
        .strip()
        .lower()
        .replace("_", " ")
        .split()
    )


normalized_columns = {
    normalize_header(column): column
    for column in df.columns
}


def find_column(aliases, required=True):
    for alias in aliases:
        normalized_alias = normalize_header(alias)
        if normalized_alias in normalized_columns:
            return normalized_columns[normalized_alias]

    if required:
        raise KeyError(
            f"Could not identify a required column.\n"
            f"Tried aliases: {aliases}\n"
            f"Actual CSV columns:\n"
            + "\n".join(repr(column) for column in df.columns)
        )

    return None


# ------------------------------------------------------------
# 2. Identify the actual source columns
# ------------------------------------------------------------

column_map = {
    "quantity": find_column([
        "line item quantity",
        "quantity",
        "line quantity",
        "qty",
    ]),
    "pack_price": find_column([
        "pack price",
        "pack_price",
        "price per pack",
    ]),
    "line_value": find_column([
        "line item value",
        "line_item_value",
        "line value",
        "total line value",
    ]),
    "id": find_column([
        "id",
        "record id",
    ], required=False),
    "product_group": find_column([
        "product group",
        "product_group",
        "product group code",
    ], required=False),
    "vendor": find_column([
        "vendor",
        "vendor name",
    ], required=False),
    "item_description": find_column([
        "item description",
        "item_description",
        "product description",
    ], required=False),
}

print("\nSource file loaded successfully.")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")

print("\nResolved source columns:")
for field, source_column in column_map.items():
    print(f"  {field}: {source_column!r}")


# ------------------------------------------------------------
# 3. Prepare analysis fields
# ------------------------------------------------------------

analysis = pd.DataFrame(index=df.index)

for field in ["id", "product_group", "vendor", "item_description"]:
    source_column = column_map[field]

    if source_column is not None:
        analysis[field] = df[source_column]
    else:
        analysis[field] = pd.NA

for field in ["quantity", "pack_price", "line_value"]:
    analysis[field] = pd.to_numeric(
        df[column_map[field]],
        errors="coerce"
    )

analysis["expected_value"] = (
    analysis["quantity"] * analysis["pack_price"]
)

# Positive difference: recorded line value is higher.
# Negative difference: recorded line value is lower.
analysis["value_difference"] = (
    analysis["line_value"] - analysis["expected_value"]
)

analysis["absolute_difference"] = (
    analysis["value_difference"].abs()
)

analysis["comparable"] = analysis[
    ["quantity", "pack_price", "line_value"]
].notna().all(axis=1)

analysis["exceeds_tolerance"] = (
    analysis["comparable"]
    & (analysis["absolute_difference"] > TOLERANCE)
)

analysis["difference_direction"] = "Within tolerance"

analysis.loc[
    analysis["value_difference"] > TOLERANCE,
    "difference_direction"
] = "Recorded value above expected"

analysis.loc[
    analysis["value_difference"] < -TOLERANCE,
    "difference_direction"
] = "Recorded value below expected"

analysis.loc[
    ~analysis["comparable"],
    "difference_direction"
] = "Not comparable"


# ------------------------------------------------------------
# 4. Overall summary
# ------------------------------------------------------------

total_rows = len(analysis)
comparable_count = int(analysis["comparable"].sum())
not_comparable_count = total_rows - comparable_count
exception_count = int(analysis["exceeds_tolerance"].sum())

overall = pd.DataFrame([{
    "total_records": total_rows,
    "comparable_records": comparable_count,
    "not_comparable_records": not_comparable_count,
    "tolerance_dollars": TOLERANCE,
    "records_exceeding_tolerance": exception_count,
    "exception_rate_of_comparable_records": (
        exception_count / comparable_count
        if comparable_count else None
    ),
    "median_absolute_difference": (
        analysis.loc[
            analysis["comparable"], "absolute_difference"
        ].median()
        if comparable_count else None
    ),
    "maximum_absolute_difference": (
        analysis.loc[
            analysis["comparable"], "absolute_difference"
        ].max()
        if comparable_count else None
    ),
}])

overall.to_csv(
    OUTPUT_DIR / "line_value_relationship_overall.csv",
    index=False
)

print("\n" + "=" * 65)
print("OVERALL RESULTS")
print("=" * 65)
print(f"Total records:              {total_rows:,}")
print(f"Comparable records:         {comparable_count:,}")
print(f"Not comparable:             {not_comparable_count:,}")
print(f"Tolerance:                  ${TOLERANCE:.2f}")
print(f"Records exceeding tolerance:{exception_count:>7,}")

if comparable_count:
    print(
        "Exception rate:             "
        f"{exception_count / comparable_count:.2%}"
    )
    print(
        "Median absolute difference: "
        f"${analysis.loc[analysis['comparable'], 'absolute_difference'].median():.2f}"
    )
    print(
        "Maximum absolute difference:"
        f" ${analysis.loc[analysis['comparable'], 'absolute_difference'].max():.2f}"
    )


# ------------------------------------------------------------
# 5. Results by product group
# ------------------------------------------------------------

group_data = analysis.loc[analysis["comparable"]].copy()

group_summary = (
    group_data.groupby("product_group", dropna=False)
    .agg(
        comparable_records=("comparable", "size"),
        exceptions=("exceeds_tolerance", "sum"),
        median_absolute_difference=("absolute_difference", "median"),
        maximum_absolute_difference=("absolute_difference", "max"),
    )
    .reset_index()
)

group_summary["exception_rate"] = (
    group_summary["exceptions"]
    / group_summary["comparable_records"]
)

group_summary = group_summary.sort_values(
    ["exceptions", "exception_rate"],
    ascending=[False, False]
)

group_summary.to_csv(
    OUTPUT_DIR / "line_value_relationship_by_group.csv",
    index=False
)

print("\n" + "=" * 65)
print("RESULTS BY PRODUCT GROUP")
print("=" * 65)

if not group_summary.empty:
    print(group_summary.to_string(index=False))
else:
    print("No comparable records available for group analysis.")


# ------------------------------------------------------------
# 6. Exception register
# ------------------------------------------------------------

exception_columns = [
    "id",
    "product_group",
    "vendor",
    "item_description",
    "quantity",
    "pack_price",
    "line_value",
    "expected_value",
    "value_difference",
    "absolute_difference",
    "difference_direction",
]

exceptions = analysis.loc[
    analysis["exceeds_tolerance"],
    exception_columns
].copy()

exceptions = exceptions.sort_values(
    "absolute_difference",
    ascending=False
)

exceptions.to_csv(
    OUTPUT_DIR / "line_value_relationship_exceptions.csv",
    index=False
)

# Keep a separate, convenient view of the 20 largest differences.
exceptions.head(20).to_csv(
    OUTPUT_DIR / "line_value_relationship_largest_differences.csv",
    index=False
)


# ------------------------------------------------------------
# 7. Direction and magnitude of differences
# ------------------------------------------------------------

comparable_data = analysis.loc[analysis["comparable"]].copy()

direction_summary = (
    comparable_data.groupby("difference_direction", dropna=False)
    .agg(
        record_count=("difference_direction", "size"),
        median_absolute_difference=("absolute_difference", "median"),
        maximum_absolute_difference=("absolute_difference", "max"),
    )
    .reset_index()
)

direction_summary["share_of_comparable_records"] = (
    direction_summary["record_count"] / comparable_count
    if comparable_count else 0
)

direction_summary.to_csv(
    OUTPUT_DIR / "line_value_relationship_direction.csv",
    index=False
)

print("\n" + "=" * 65)
print("DIFFERENCE DIRECTION")
print("=" * 65)

if not direction_summary.empty:
    print(direction_summary.to_string(index=False))


# ------------------------------------------------------------
# 8. Reconciliation checks
# ------------------------------------------------------------

assert len(analysis) == total_rows, (
    "Row count changed unexpectedly during analysis."
)

assert comparable_count + not_comparable_count == total_rows, (
    "Comparable and non-comparable counts do not reconcile."
)

assert exception_count == len(exceptions), (
    "Exception count does not match the exception register."
)

assert (
    int(group_summary["comparable_records"].sum())
    == comparable_count
), "Product-group counts do not reconcile."

assert (
    int(group_summary["exceptions"].sum())
    == exception_count
), "Product-group exception counts do not reconcile."

print("\n" + "=" * 65)
print("RECONCILIATION CHECKS")
print("=" * 65)
print("PASS: Total row count reconciles.")
print("PASS: Comparable and non-comparable counts reconcile.")
print("PASS: Exception register count reconciles.")
print("PASS: Product-group record and exception counts reconcile.")

print("\nOutput files saved to:")
print(OUTPUT_DIR)
print("\nInvestigation completed.")
print(
    "Reminder: exceeding the arithmetic tolerance identifies an "
    "exception to the tested relationship, not a confirmed data error."
)
