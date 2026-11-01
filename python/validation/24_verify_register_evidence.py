
from pathlib import Path
import re
import sys

import pandas as pd


# ------------------------------------------------------------
# 1. PATHS AND SETTINGS
# ------------------------------------------------------------

PROJECT_DIR = Path(r"C:\Project_03")
PUBLICATION_DIR = PROJECT_DIR / "publication"

SOURCE_FILE = (
    PROJECT_DIR / "dataset" / "Suppy_Chain_Shipment_Data.csv"
)

EVIDENCE_DIR = PUBLICATION_DIR / "evidence"

OUTPUT_DIR = PUBLICATION_DIR / "execution" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "register_evidence_verification.csv"

EXPECTED_ROWS = 10324
EXPECTED_COLUMNS = 33

REFERENCE_FIELDS = [
    "weight (kilograms)",
    "freight cost (usd)",
]

REFERENCE_PATTERN = re.compile(
    r"\bSee\s+(?:DN|ASN)\b.*\bID\s*#?\s*:\s*\d+",
    flags=re.IGNORECASE,
)


# ------------------------------------------------------------
# 2. LOAD AND VALIDATE SOURCE
# ------------------------------------------------------------

def load_source():
    df = pd.read_csv(SOURCE_FILE, low_memory=False)

    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"Unexpected source row count: {len(df)}"
        )

    if len(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected source column count: {len(df.columns)}"
        )

    if "id" not in df.columns:
        raise ValueError("Required source ID column is missing.")

    if df["id"].isna().any():
        raise ValueError("Source IDs contain missing values.")

    if df["id"].duplicated().any():
        raise ValueError("Source IDs are not unique.")

    return df


def load_evidence(filename):
    path = EVIDENCE_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(
            f"Required evidence file not found: {path}"
        )

    return pd.read_csv(path, low_memory=False)


# ------------------------------------------------------------
# 3. CHECK HELPERS
# ------------------------------------------------------------

checks = []


def add_check(finding, metric, observed, expected):
    checks.append({
        "finding": finding,
        "metric": metric,
        "previous_result": expected,
        "source_result": observed,
        "status": "MATCH" if observed == expected else "REVIEW",
    })


def missing_count(series):
    text = series.astype("string").str.strip()
    return int((series.isna() | text.eq("")).sum())


def numeric_series(series):
    return pd.to_numeric(series, errors="coerce")


def normalized_id(value):
    return str(int(value)) if pd.notna(value) else ""


# ------------------------------------------------------------
# 4. DQ-01: MISSING DOSAGE
# ------------------------------------------------------------

def check_dq01(df):
    dosage = df["dosage"]

    add_check(
        "DQ-01",
        "Missing dosage",
        missing_count(dosage),
        1736,
    )


# ------------------------------------------------------------
# 5. DQ-02: DATE-FIELD TEXT PATTERNS
# ------------------------------------------------------------

def check_dq02(df):
    pq_date = df["pq first sent to client date"]
    po_date = df["po sent to vendor date"]

    pq_text = pq_date.astype("string").str.strip()
    po_text = po_date.astype("string").str.strip()

    add_check(
        "DQ-02",
        "PQ date: Pre-PQ Process",
        int(pq_text.eq("Pre-PQ Process").sum()),
        2476,
    )

    add_check(
        "DQ-02",
        "PO date: N/A - From RDC",
        int(po_text.eq("N/A - From RDC").sum()),
        5404,
    )


# ------------------------------------------------------------
# 6. DQ-03: PRICING RELATIONSHIP
# ------------------------------------------------------------

def check_dq03(df):
    unit_price = numeric_series(df["unit price"])
    uom = numeric_series(df["unit of measure (per pack)"])
    pack_price = numeric_series(df["pack price"])

    comparable = (
        unit_price.notna()
        & uom.notna()
        & pack_price.notna()
    )

    difference = (pack_price - unit_price * uom).abs()

    count = int(
        (comparable & difference.gt(0.02)).sum()
    )

    add_check(
        "DQ-03",
        "Price differences greater than $0.02",
        count,
        7774,
    )


# ------------------------------------------------------------
# 7. DQ-04: ZERO UNIT PRICES
# ------------------------------------------------------------

def check_dq04(df):
    unit_price = numeric_series(df["unit price"])

    add_check(
        "DQ-04",
        "Zero unit prices",
        int(unit_price.eq(0).sum()),
        103,
    )


# ------------------------------------------------------------
# 8. DQ-05: POTENTIAL DUPLICATE RECORDS
# ------------------------------------------------------------

def check_dq05(df):
    evidence_groups = load_evidence(
        "potential_duplicate_groups.csv"
    )

    evidence_records = load_evidence(
        "potential_duplicate_records.csv"
    )

    compare_cols = [
        column for column in df.columns
        if column != "id"
    ]

    duplicate_mask = df.duplicated(
        subset=compare_cols,
        keep=False,
    )

    candidates = df.loc[duplicate_mask].copy()

    if candidates.empty:
        actual_groups = {}
    else:
        signatures = candidates[compare_cols].copy()

        group_codes, _ = pd.factorize(
            pd.MultiIndex.from_frame(signatures),
            sort=True,
        )

        candidates["_candidate_group"] = group_codes + 1

        actual_groups = {}

        for group_id, group in candidates.groupby(
            "_candidate_group",
            sort=True,
        ):
            ids = frozenset(
                group["id"].map(normalized_id)
            )
            actual_groups[ids] = len(compare_cols)

    expected_groups = {}

    for _, group in evidence_records.groupby(
        "candidate_group"
    ):
        ids = frozenset(
            group["id"].map(normalized_id)
        )

        expected_groups[ids] = len(compare_cols)

    add_check(
        "DQ-05",
        "Candidate duplicate groups",
        len(actual_groups),
        4,
    )

    add_check(
        "DQ-05",
        "Candidate duplicate records",
        len(candidates),
        8,
    )

    add_check(
        "DQ-05",
        "Candidate group membership matches evidence",
        actual_groups == expected_groups,
        True,
    )

    evidence_field_counts = set(
        pd.to_numeric(
            evidence_groups["matching_fields_count"],
            errors="coerce",
        ).dropna().astype(int)
    )

    add_check(
        "DQ-05",
        "Matching non-ID fields per candidate group",
        evidence_field_counts == {32}
        and len(compare_cols) == 32,
        True,
    )


# ------------------------------------------------------------
# 9. DQ-06: NUMERIC WEIGHT AND FREIGHT COVERAGE
# ------------------------------------------------------------

def check_dq06(df):
    weight = numeric_series(df["weight (kilograms)"])
    freight = numeric_series(df["freight cost (usd)"])

    add_check(
        "DQ-06",
        "Numeric weight records",
        int(weight.notna().sum()),
        6372,
    )

    add_check(
        "DQ-06",
        "Numeric freight records",
        int(freight.notna().sum()),
        6198,
    )


# ------------------------------------------------------------
# 10. DQ-07: CROSS-RECORD REFERENCES
# ------------------------------------------------------------

def check_dq07(df):
    evidence = load_evidence(
        "weight_freight_reference_examples.csv"
    )

    required_columns = {
        "source_id",
        "field",
        "original_value",
        "reference_id",
    }

    if not required_columns.issubset(evidence.columns):
        raise ValueError(
            "DQ-07 evidence is missing required columns."
        )

    actual_rows = []

    for field in REFERENCE_FIELDS:
        values = df[field].astype("string")

        mask = values.str.contains(
            REFERENCE_PATTERN,
            na=False,
        )

        for source_id, value in df.loc[
            mask, ["id", field]
        ].itertuples(index=False, name=None):

            text = str(value)

            match = re.search(
                r"ID\s*#?\s*:\s*(\d+)",
                text,
                flags=re.IGNORECASE,
            )

            if match is None:
                raise ValueError(
                    "Reference classification and ID extraction "
                    "do not agree."
                )

            actual_rows.append({
                "source_id": normalized_id(source_id),
                "field": field,
                "original_value": text,
                "reference_id": match.group(1),
            })

    actual = pd.DataFrame(actual_rows)

    expected = evidence.copy()

    for column in [
        "source_id",
        "field",
        "original_value",
        "reference_id",
    ]:
        actual[column] = actual[column].astype("string").fillna("")
        expected[column] = expected[column].astype("string").fillna("")

    comparison_columns = [
        "source_id",
        "field",
        "original_value",
        "reference_id",
    ]

    actual_tuples = set(
        actual[comparison_columns].itertuples(
            index=False,
            name=None,
        )
    )

    expected_tuples = set(
        expected[comparison_columns].itertuples(
            index=False,
            name=None,
        )
    )

    add_check(
        "DQ-07",
        "Total cross-record reference occurrences",
        len(actual),
        4890,
    )

    for field in REFERENCE_FIELDS:
        count = int(actual["field"].eq(field).sum())

        expected_count = (
            2445 if field == "weight (kilograms)" else 2445
        )

        add_check(
            "DQ-07",
            f"Reference occurrences: {field}",
            count,
            expected_count,
        )

    add_check(
        "DQ-07",
        "Unique source records with references",
        int(actual["source_id"].nunique()),
        2445,
    )

    add_check(
        "DQ-07",
        "Unique referenced target IDs",
        int(actual["reference_id"].nunique()),
        1299,
    )

    add_check(
        "DQ-07",
        "Source reference details match published evidence",
        actual_tuples == expected_tuples
        and len(actual) == len(expected),
        True,
    )


# ------------------------------------------------------------
# 11. DQ-08: MISSING INSURANCE
# ------------------------------------------------------------

def check_dq08(df):
    insurance = df["line item insurance (usd)"]

    add_check(
        "DQ-08",
        "Missing line-item insurance",
        missing_count(insurance),
        287,
    )


# ------------------------------------------------------------
# 12. MAIN EXECUTION
# ------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_source()

    check_dq01(df)
    check_dq02(df)
    check_dq03(df)
    check_dq04(df)
    check_dq05(df)
    check_dq06(df)
    check_dq07(df)
    check_dq08(df)

    results = pd.DataFrame(checks)

    matches = int(results["status"].eq("MATCH").sum())
    reviews = int(results["status"].eq("REVIEW").sum())

    print("\nSOURCE EVIDENCE VERIFICATION")
    print("=" * 72)

    print(f"Source rows: {len(df):,}")
    print(f"Source columns: {len(df.columns):,}")
    print(f"Checks performed: {len(results)}")
    print(f"Matching results: {matches}")
    print(f"Results requiring review: {reviews}")

    print("\nDetailed results:")
    print(results.to_string(index=False))

    results.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nVerification results saved to:\n{OUTPUT_FILE}")

    print(
        "\nIMPORTANT: Matching results confirm consistency "
        "with previous investigation evidence."
    )
    print(
        "They do not prove business meaning, data correctness, "
        "or the validity of an assumed business rule."
    )
    print(
        "\nDQ-02 checks only two date-text patterns. "
        "This is not a complete date-field validation."
    )

    if reviews:
        print("\nFAIL: One or more checks require investigation.")
        return 1

    print("\nPASS: All configured source-evidence checks matched.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"\nERROR: Verification could not be completed: {error}")
        sys.exit(1)
