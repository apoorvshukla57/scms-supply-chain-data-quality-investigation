
from pathlib import Path
import hashlib
import sys

import pandas as pd


PROJECT_BASE = Path(r"C:\Project_03")
PUBLICATION_BASE = PROJECT_BASE / "publication"
EVIDENCE_DIR = PUBLICATION_BASE / "evidence"
MANIFEST_PATH = PUBLICATION_BASE / "PUBLICATION_EVIDENCE_MANIFEST.csv"
EVIDENCE_MAP_PATH = PUBLICATION_BASE / "EVIDENCE_TO_FINDING_MAP.md"

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

# Files explicitly mapped in the publication evidence documentation.
FINDING_EVIDENCE = {
    "DQ-01": [
        "missing_dosage_by_product_group.csv",
        "missing_dosage_by_sub_classification.csv",
        "missing_dosage_records_for_review.csv",
    ],
    "DQ-02": [
        "date_field_quality_summary.csv",
        "date_field_quality_exceptions.csv",
    ],
    "DQ-03": [
        "pricing_discrepancy_overall.csv",
        "pricing_discrepancy_by_product_group.csv",
        "pricing_rounding_hypothesis_overall.csv",
        "unit_price_uom_rounding_overall.csv",
        "unit_price_uom_rounding_by_group.csv",
        "unit_price_uom_rounding_noncomparable.csv",
        "unit_price_uom_rounding_record_checks.csv",
        "line_value_relationship_overall.csv",
        "line_value_rounding_by_group.csv",
    ],
    "DQ-04": [
        "zero_unit_price_by_group.csv",
        "zero_unit_price_by_product.csv",
        "zero_unit_price_positive_comparison.csv",
        "zero_unit_price_records.csv",
    ],
    "DQ-05": [
        "potential_duplicate_groups.csv",
        "potential_duplicate_records.csv",
    ],
    "DQ-06": [
        "weight_freight_classification_summary.csv",
        "weight_freight_refined_categories.csv",
        "weight_freight_reference_examples.csv",
    ],
    "DQ-07": [
        "weight_freight_reference_examples.csv",
    ],
    "DQ-08": [
        "missing_insurance_by_product_group.csv",
        "missing_insurance_by_shipment_mode.csv",
        "missing_insurance_by_country.csv",
        "missing_insurance_by_fulfill_via.csv",
        "missing_insurance_records_for_review.csv",
    ],
}

SHARED_GOVERNANCE_FILES = [
    "initial_findings_register.csv",
    "prioritized_findings_register.csv",
    "register_evidence_verification.csv",
    "section04_register_reconciliation.csv",
]

EXPECTED_EVIDENCE_COUNT = 32
REQUIRED_MANIFEST_COLUMNS = {
    "file_name",
    "file_size_bytes",
    "data_rows",
    "sha256",
}

REQUIRED_REGISTER_FIELDS = [
    "finding",
    "evidence",
    "classification",
    "validation_status",
    "next_validation",
]


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest().upper()


def add_issue(issues, message):
    issues.append(message)
    print(f"  FAIL: {message}")


def main():
    issues = []

    print("=" * 72)
    print("PROJECT 03 - PUBLICATION EVIDENCE AUDIT")
    print("=" * 72)

    # 1. Required publication documents
    print("\n1. PUBLICATION DOCUMENTS")

    for path in [MANIFEST_PATH, EVIDENCE_MAP_PATH]:
        if path.is_file():
            print(f"  PRESENT: {path.name}")
        else:
            add_issue(issues, f"Required publication document missing: {path}")

    if not MANIFEST_PATH.is_file() or not EVIDENCE_MAP_PATH.is_file():
        raise SystemExit(1)

    evidence_map = EVIDENCE_MAP_PATH.read_text(encoding="utf-8")

    for finding_id in EXPECTED_PRIORITIES:
        if finding_id not in evidence_map:
            add_issue(
                issues,
                f"{finding_id} not found in evidence-to-finding map"
            )

    # 2. Manifest structure
    print("\n2. MANIFEST VALIDATION")

    manifest = pd.read_csv(MANIFEST_PATH, encoding="utf-8-sig")

    missing_columns = REQUIRED_MANIFEST_COLUMNS - set(manifest.columns)

    if missing_columns:
        add_issue(
            issues,
            f"Manifest missing columns: {sorted(missing_columns)}"
        )
        raise SystemExit(1)

    if manifest["file_name"].isna().any():
        add_issue(issues, "Manifest contains blank filenames")

    filenames = manifest["file_name"].astype("string").str.strip()

    if filenames.eq("").fillna(False).any():
        add_issue(issues, "Manifest contains empty filenames")

    duplicate_names = filenames[filenames.duplicated(keep=False)].dropna().unique()

    if len(duplicate_names):
        add_issue(
            issues,
            f"Duplicate manifest filenames: {duplicate_names.tolist()}"
        )

    if len(manifest) != EXPECTED_EVIDENCE_COUNT:
        add_issue(
            issues,
            f"Expected {EXPECTED_EVIDENCE_COUNT} manifest rows; "
            f"found {len(manifest)}"
        )
    else:
        print(f"  PASS: {len(manifest)} manifest rows")

    # 3. Evidence coverage against the documented mapping
    print("\n3. FINDING-LEVEL EVIDENCE COVERAGE")

    manifest_names = set(filenames.dropna().tolist())

    for finding_id, required_files in FINDING_EVIDENCE.items():
        missing = sorted(set(required_files) - manifest_names)

        if missing:
            add_issue(
                issues,
                f"{finding_id} evidence absent from manifest: {missing}"
            )
        else:
            print(
                f"  PASS: {finding_id} - "
                f"{len(required_files)} mapped evidence files"
            )

    missing_shared = sorted(
        set(SHARED_GOVERNANCE_FILES) - manifest_names
    )

    if missing_shared:
        add_issue(
            issues,
            f"Shared governance files absent from manifest: {missing_shared}"
        )
    else:
        print(
            f"  PASS: {len(SHARED_GOVERNANCE_FILES)} shared "
            "governance files mapped"
        )

    # 4. File integrity, CSV readability and row-count verification
    print("\n4. EVIDENCE FILE INTEGRITY")

    verified = 0

    for record in manifest.to_dict("records"):
        filename = str(record["file_name"]).strip()
        path = EVIDENCE_DIR / filename

        if not path.is_file():
            add_issue(issues, f"Evidence file missing: {filename}")
            continue

        try:
            expected_size = int(record["file_size_bytes"])
            expected_rows = int(record["data_rows"])
            expected_hash = str(record["sha256"]).strip().upper()

            if path.stat().st_size != expected_size:
                add_issue(
                    issues,
                    f"{filename}: size mismatch "
                    f"(expected {expected_size}, "
                    f"actual {path.stat().st_size})"
                )
                continue

            actual_hash = sha256_file(path)

            if actual_hash != expected_hash:
                add_issue(issues, f"{filename}: SHA-256 mismatch")
                continue

            evidence = pd.read_csv(path, encoding="utf-8-sig")

            if len(evidence) != expected_rows:
                add_issue(
                    issues,
                    f"{filename}: row-count mismatch "
                    f"(expected {expected_rows}, actual {len(evidence)})"
                )
                continue

            verified += 1
            print(f"  PASS: {filename} ({len(evidence):,} rows)")

        except Exception as exc:
            add_issue(issues, f"{filename}: verification error: {exc}")

    print(
        f"\n  Verified files: {verified}/{len(manifest)}"
    )

    # 5. Actual evidence folder inventory
    print("\n5. EVIDENCE FOLDER INVENTORY")

    actual_csv_files = {
        path.name for path in EVIDENCE_DIR.glob("*.csv")
    }
    expected_csv_files = manifest_names

    unexpected = sorted(actual_csv_files - expected_csv_files)
    absent = sorted(expected_csv_files - actual_csv_files)

    if absent:
        add_issue(issues, f"Manifest files absent from folder: {absent}")

    if unexpected:
        add_issue(
            issues,
            f"Unlisted CSV files found in evidence folder: {unexpected}"
        )

    if not absent and not unexpected:
        print(
            f"  PASS: evidence folder contains exactly "
            f"{len(expected_csv_files)} manifest CSV files"
        )

    # 6. Register integrity and priority checks
    print("\n6. FINDINGS REGISTER VALIDATION")

    initial_path = EVIDENCE_DIR / "initial_findings_register.csv"
    priority_path = EVIDENCE_DIR / "prioritized_findings_register.csv"

    for path in [initial_path, priority_path]:
        if not path.is_file():
            add_issue(issues, f"Register missing: {path.name}")

    if initial_path.is_file() and priority_path.is_file():
        initial = pd.read_csv(
            initial_path,
            encoding="utf-8-sig",
            dtype={"finding_id": "string"},
        )
        priority = pd.read_csv(
            priority_path,
            encoding="utf-8-sig",
            dtype={"finding_id": "string"},
        )

        expected_ids = set(EXPECTED_PRIORITIES)

        for name, register in [
            ("Initial register", initial),
            ("Prioritized register", priority),
        ]:
            if "finding_id" not in register.columns:
                add_issue(issues, f"{name} lacks finding_id")
                continue

            ids = register["finding_id"].str.strip()

            if ids.isna().any() or ids.eq("").fillna(False).any():
                add_issue(issues, f"{name} contains blank finding IDs")

            if ids.duplicated().any():
                add_issue(issues, f"{name} contains duplicate finding IDs")

            actual_ids = set(ids.dropna())

            if actual_ids != expected_ids:
                add_issue(
                    issues,
                    f"{name} ID mismatch: "
                    f"missing={sorted(expected_ids - actual_ids)}, "
                    f"unexpected={sorted(actual_ids - expected_ids)}"
                )
            else:
                print(f"  PASS: {name} contains DQ-01 through DQ-08")

        if "finding_id" in initial.columns:
            initial_ids = initial["finding_id"].str.strip()

            for field in REQUIRED_REGISTER_FIELDS:
                if field not in initial.columns:
                    add_issue(
                        issues,
                        f"Initial register missing column: {field}"
                    )
                    continue

                values = initial[field].astype("string").str.strip()
                blank = values.isna() | values.eq("").fillna(False)

                if blank.any():
                    add_issue(
                        issues,
                        f"Initial register has {int(blank.sum())} "
                        f"blank values in {field}"
                    )
                else:
                    print(f"  PASS: Initial register {field} populated")

        if (
            "finding_id" in priority.columns
            and "investigation_priority" in priority.columns
        ):
            priority_ids = priority["finding_id"].str.strip()

            if not priority_ids.duplicated().any():
                indexed = priority.assign(
                    finding_id=priority_ids
                ).set_index("finding_id")

                for finding_id, expected in EXPECTED_PRIORITIES.items():
                    if finding_id not in indexed.index:
                        continue

                    actual = str(
                        indexed.at[finding_id, "investigation_priority"]
                    ).strip()

                    if actual != expected:
                        add_issue(
                            issues,
                            f"{finding_id}: expected priority {expected}, "
                            f"found {actual}"
                        )
                    else:
                        print(f"  PASS: {finding_id} priority {expected}")
        else:
            add_issue(
                issues,
                "Prioritized register lacks required priority columns"
            )

    # 7. Explicit publication-scope limitations
    print("\n7. DOCUMENTED PUBLICATION LIMITATIONS")

    print(
        "  INFO: line_value_rounding_exceptions.csv and "
        "line_value_rounding_flagged_review.csv are intentionally excluded."
    )
    print(
        "  INFO: weight_freight_value_classification.csv and "
        "weight_freight_nonnumeric_examples.csv are intentionally excluded."
    )
    print(
        "  INFO: full independent rerun of all investigations was not completed."
    )
    print(
        "  INFO: presence, hashes and populated fields do not independently "
        "prove analytical correctness."
    )

    # 8. Final result
    print("\n" + "=" * 72)
    print("PUBLICATION EVIDENCE AUDIT SUMMARY")
    print("=" * 72)

    if issues:
        print(f"FAIL: {len(issues)} issue(s) require review.")
        raise SystemExit(1)

    print("PASS: All configured publication evidence checks passed.")
    print("No files were modified or generated.")
    print("Read-only publication evidence audit completed.")


if __name__ == "__main__":
    main()

