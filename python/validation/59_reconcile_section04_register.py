
from pathlib import Path
import sys

import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

PROJECT_DIR = Path(r"C:\Project_03")
PUBLICATION_DIR = PROJECT_DIR / "publication"

EVIDENCE_DIR = PUBLICATION_DIR / "evidence"
OUTPUT_DIR = PUBLICATION_DIR / "execution" / "outputs"

REGISTER_FILE = EVIDENCE_DIR / "prioritized_findings_register.csv"
RECONCILIATION_FILE = (
    OUTPUT_DIR / "section04_register_reconciliation.csv"
)


# ------------------------------------------------------------
# SECTION 04 BASELINE
# ------------------------------------------------------------

EXPECTED_PRIORITIES = {
    "DQ-01": "P2",
    "DQ-02": "P1",
    "DQ-03": "P3",
    "DQ-04": "P2",
    "DQ-05": "P2",
    "DQ-06": "P1",
    "DQ-07": "P2",
    "DQ-08": "P2",
}


# ------------------------------------------------------------
# LOAD AND VALIDATE REGISTER
# ------------------------------------------------------------

def load_register():
    if not REGISTER_FILE.exists():
        raise FileNotFoundError(
            f"Prioritized register not found: {REGISTER_FILE}"
        )

    register = pd.read_csv(
        REGISTER_FILE,
        encoding="utf-8-sig",
    )

    required = {
        "finding_id",
        "investigation_priority",
    }

    missing_columns = required - set(register.columns)

    if missing_columns:
        raise ValueError(
            f"Register is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    register = register.copy()

    register["finding_id"] = (
        register["finding_id"]
        .astype("string")
        .str.strip()
    )

    register["investigation_priority"] = (
        register["investigation_priority"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    if register["finding_id"].isna().any():
        raise ValueError(
            "Blank finding IDs found in the prioritized register."
        )

    if register["finding_id"].eq("").any():
        raise ValueError(
            "Blank finding IDs found in the prioritized register."
        )

    if register["finding_id"].duplicated().any():
        duplicates = sorted(
            register.loc[
                register["finding_id"].duplicated(keep=False),
                "finding_id",
            ].unique().tolist()
        )

        raise ValueError(
            f"Duplicate finding IDs found: {duplicates}"
        )

    if register["investigation_priority"].isna().any():
        raise ValueError(
            "Blank investigation priorities found in the register."
        )

    if register["investigation_priority"].eq("").any():
        raise ValueError(
            "Blank investigation priorities found in the register."
        )

    return register


# ------------------------------------------------------------
# RECONCILIATION
# ------------------------------------------------------------

def build_reconciliation(register):
    actual = (
        register
        .set_index("finding_id")["investigation_priority"]
        .to_dict()
    )

    rows = []

    for finding_id, expected_priority in EXPECTED_PRIORITIES.items():
        actual_priority = actual.get(finding_id)

        if actual_priority is None:
            status = "MISSING FROM REGISTER"
        elif actual_priority != expected_priority:
            status = "PRIORITY MISMATCH"
        else:
            status = "MATCH"

        rows.append({
            "finding_id": finding_id,
            "section04_priority": expected_priority,
            "register_priority": actual_priority,
            "status": status,
        })

    extra_ids = sorted(
        set(actual) - set(EXPECTED_PRIORITIES)
    )

    for finding_id in extra_ids:
        rows.append({
            "finding_id": finding_id,
            "section04_priority": None,
            "register_priority": actual[finding_id],
            "status": "NOT IN SECTION 04",
        })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    print("\nSECTION 04 PRIORITY RECONCILIATION")
    print("=" * 60)

    register = load_register()
    comparison = build_reconciliation(register)

    matches = int(
        comparison["status"].eq("MATCH").sum()
    )

    exceptions = int(
        comparison["status"].ne("MATCH").sum()
    )

    missing_ids = sorted(
        set(EXPECTED_PRIORITIES)
        - set(register["finding_id"])
    )

    extra_ids = sorted(
        set(register["finding_id"])
        - set(EXPECTED_PRIORITIES)
    )

    print(f"Section 04 findings: {len(EXPECTED_PRIORITIES)}")
    print(f"Register findings:   {len(register)}")
    print(f"Matches:             {matches}")
    print(f"Exceptions:          {exceptions}")
    print(f"Missing IDs:         {missing_ids}")
    print(f"Unexpected IDs:      {extra_ids}")

    print("\nDetailed results:")
    print(comparison.to_string(index=False))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(
        RECONCILIATION_FILE,
        index=False,
    )

    print(f"\nReconciliation output saved to:")
    print(RECONCILIATION_FILE)

    if (
        len(register) == len(EXPECTED_PRIORITIES)
        and not missing_ids
        and not extra_ids
        and exceptions == 0
    ):
        print(
            "\nPASS: All eight finding IDs and priorities reconcile."
        )
        print("Original evidence and register files were not modified.")
        return

    print("\nRECONCILIATION FAILED")
    print("Review the exceptions before accepting the result.")
    print("Original evidence and register files were not modified.")

    raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except (
        FileNotFoundError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        ValueError,
        OSError,
    ) as exc:
        print(f"\nERROR: {exc}")
        raise SystemExit(1)
