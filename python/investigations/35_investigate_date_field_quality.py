
import pandas as pd
from pathlib import Path

# ============================================================
# 1. PATHS AND CONFIGURATION
# ============================================================

PROJECT_DIR = Path(r"C:\Project_03")
DATA_PATH = (
    PROJECT_DIR
    / "dataset"
    / "Suppy_Chain_Shipment_Data.csv"
)
OUTPUT_DIR = PROJECT_DIR / "publication" / "execution" / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATE_COLUMNS = [
    "pq first sent to client date",
    "po sent to vendor date",
    "scheduled delivery date",
    "delivered to client date",
    "delivery recorded date",
]

WORKFLOW_LABELS = {
    "pre-pq process": "Workflow status: Pre-PQ Process",
    "n/a - from rdc": "Workflow status: N/A - From RDC",
}

UNAVAILABLE_LABELS = {
    "n/a",
    "na",
    "n.a.",
    "unknown",
    "not captured",
    "date not captured",
    "unavailable",
}

# ============================================================
# 2. LOAD SOURCE DATA
# ============================================================

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Source CSV not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH, low_memory=False)

missing_columns = [
    col for col in DATE_COLUMNS
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required date columns not found: {missing_columns}"
    )

print("=" * 65)
print("DATE FIELD QUALITY INVESTIGATION")
print("=" * 65)
print(f"Source rows: {len(df):,}")
print(f"Source columns: {len(df.columns):,}")
print("Raw source will not be modified.")

summary_rows = []
exception_rows = []

# ============================================================
# 3. CLASSIFY EACH DATE FIELD
# ============================================================

for col in DATE_COLUMNS:
    raw = df[col].astype("string").str.strip()
    normalized = raw.str.casefold()

    is_missing = raw.isna() | raw.eq("")

    is_unavailable = (
        ~is_missing
        & normalized.isin(UNAVAILABLE_LABELS)
    )

    workflow_category = normalized.map(WORKFLOW_LABELS)
    is_workflow = workflow_category.notna()

    eligible = ~(
        is_missing
        | is_unavailable
        | is_workflow
    )

    parsed = pd.to_datetime(
        raw.where(eligible),
        format="mixed",
        errors="coerce",
    )

    is_valid_date = eligible & parsed.notna()
    is_unparseable = eligible & parsed.isna()

    classifications = [
        ("Valid date", is_valid_date),
        ("Missing/blank", is_missing),
        ("Explicitly unavailable", is_unavailable),
        ("Recognized workflow status", is_workflow),
        ("Other unparseable text", is_unparseable),
    ]

    print(f"\n{'-' * 65}")
    print(col)
    print("-" * 65)

    for category, mask in classifications:
        count = int(mask.sum())
        percentage = (
            count / len(df) * 100
            if len(df) > 0
            else 0
        )

        print(
            f"{category}: {count:,} "
            f"({percentage:.2f}%)"
        )

        summary_rows.append({
            "date_field": col,
            "classification": category,
            "record_count": count,
            "percentage": round(percentage, 2),
            "total_records": len(df),
        })

    if is_valid_date.any():
        print(
            "Earliest valid date: "
            f"{parsed[is_valid_date].min()}"
        )
        print(
            "Latest valid date:   "
            f"{parsed[is_valid_date].max()}"
        )
    else:
        print("Earliest valid date: None")
        print("Latest valid date:   None")

    # --------------------------------------------------------
    # Build exception records with aligned classifications.
    # This avoids Boolean-mask assignment length errors.
    # --------------------------------------------------------

    exception_mask = ~is_valid_date
    exception_indices = df.index[exception_mask]

    if len(exception_indices) > 0:
        labels = pd.Series(
            "Other unparseable text",
            index=exception_indices,
            dtype="string",
        )

        labels.loc[is_missing.loc[exception_indices]] = (
            "Missing/blank"
        )

        labels.loc[is_unavailable.loc[exception_indices]] = (
            "Explicitly unavailable"
        )

        labels.loc[is_workflow.loc[exception_indices]] = (
            workflow_category.loc[exception_indices]
        )

        exception_data = pd.DataFrame({
            "source_row_number": exception_indices + 2,
            "id": (
                df.loc[exception_indices, "id"].astype("string").values
                if "id" in df.columns
                else [pd.NA] * len(exception_indices)
            ),
            "date_field": col,
            "raw_value": raw.loc[exception_indices].values,
            "classification": labels.values,
        })

        exception_rows.append(exception_data)

# ============================================================
# 4. EXPORT SUMMARY AND EXCEPTION EVIDENCE
# ============================================================

summary = pd.DataFrame(summary_rows)

summary_path = (
    OUTPUT_DIR / "date_field_quality_summary.csv"
)
summary.to_csv(summary_path, index=False)

exception_columns = [
    "source_row_number",
    "id",
    "date_field",
    "raw_value",
    "classification",
]

if exception_rows:
    exceptions = pd.concat(
        exception_rows,
        ignore_index=True,
    )
else:
    exceptions = pd.DataFrame(
        columns=exception_columns
    )

exceptions_path = (
    OUTPUT_DIR / "date_field_quality_exceptions.csv"
)
exceptions.to_csv(exceptions_path, index=False)

print(f"\n{'=' * 65}")
print("INVESTIGATION COMPLETE")
print("=" * 65)
print(f"Summary file:    {summary_path}")
print(f"Exceptions file: {exceptions_path}")
print("Original CSV was not modified.")
