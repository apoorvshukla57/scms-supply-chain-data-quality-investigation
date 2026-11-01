# The Data Nobody Wants to Clean
## A Supply Chain Shipment Data Quality Investigation

### Project Overview

Supply chain decisions depend on data that is complete, consistent, interpretable, and reliable. Yet operational datasets often contain missing attributes, inconsistent pricing relationships, ambiguous workflow values, and references to other records that require investigation before the data can be trusted.

This project investigates data quality across a shipment and pricing dataset associated with the USAID Supply Chain Management System (SCMS).

Rather than treating every unusual value as an error, the investigation distinguishes observable data-quality patterns from unresolved business interpretations. It combines SQL-based analysis, Python investigations, evidence reconciliation, and business-oriented recommendations to establish where the data requires review and what should happen next.

**The objective was not simply to clean the dataset. It was to determine which data-quality issues matter, quantify their extent, preserve supporting evidence, and identify the controls needed before operational use.**

---

## 1. Investigation Scope

| Dataset characteristic | Value |
|---|---:|
| Shipment records | 10,324 |
| Source columns | 33 |
| Unique shipment IDs | 10,324 |
| Investigation findings | 8 |
| Selected evidence files | 32 |
| Python scripts in release | 25 |

The original source dataset was preserved without modification.

The investigation covered eight data-quality areas:

1. Missing dosage information
2. Date-field quality and chronology
3. Pricing arithmetic and recorded precision
4. Zero unit prices
5. Potential duplicate shipment records
6. Weight and freight field usability
7. Cross-record reference integrity
8. Missing insurance information

---

## 2. Executive Findings

Eight findings were documented and prioritized according to their investigation significance and the need for follow-up.

| ID | Finding | Priority | Key observation |
|---|---|---|---|
| DQ-01 | Missing dosage | P2 | 1,736 records (16.82%) have missing dosage values. |
| DQ-02 | Date-field quality | P1 | Two date fields contain workflow labels or unavailable values requiring interpretation. |
| DQ-03 | Pricing arithmetic and precision | P3 | 7,774 records exceeded the initial $0.02 pack-price comparison tolerance. |
| DQ-04 | Zero unit prices | P2 | 103 records contain zero unit prices. |
| DQ-05 | Potential duplicate shipments | P2 | Four candidate pairs involving eight records match across 32 non-ID fields. |
| DQ-06 | Weight and freight usability | P1 | 3,952 weight values and 4,126 freight values are nonnumeric text. |
| DQ-07 | Cross-record reference integrity | P2 | 2,445 records contain references in both weight and freight fields. |
| DQ-08 | Missing insurance | P2 | 287 records have missing insurance values. |

P1 and P2 are investigation priorities, not confirmed measures of financial or operational impact. DQ-06 and DQ-07 overlap and should be assessed jointly rather than added together.

### Selected results

**Missing dosage**

- 1,736 of 10,324 records have missing dosage values.
- 1,728 are in HRDT and eight are in MRDT.
- Applicability has not been independently established, so missing values were not automatically imputed.

**Date-field quality**

- The PQ first-sent field contains 205 unavailable values and 2,476 `Pre-PQ Process` labels.
- The PO-sent field contains 328 unavailable values and 5,404 `N/A - From RDC` labels.
- Three recorded dates precede their corresponding delivered-to-client dates.
- Recognized date formats do not establish that the underlying business events were recorded correctly.

**Pricing arithmetic**

- The initial pack-price comparison identified 7,774 records outside a $0.02 tolerance.
- A separate rounded unit-price-times-UOM test brought 90 records within tolerance, leaving 7,684 outside it.
- Separately, 549 line-value exceptions passed an implied-pack-price rounding test.
- These are distinct tests. The source-system pricing convention remains unconfirmed.

**Zero unit prices**

- 103 records contain zero unit prices.
- The observed concentration in safety-lancet products warrants review.
- The investigation does not assume that zero values are invalid or recommend automatic price correction.

**Potential duplicate shipments**

- Four candidate pairs involving eight records match across all 32 non-ID fields.
- These are candidate matches, not confirmed duplicate shipments.
- No records were deleted or deduplicated.

**Weight and freight usability**

- Weight: 6,372 numeric values and 3,952 nonnumeric values.
- Freight: 6,198 numeric values and 4,126 nonnumeric values.
- The nonnumeric categories include cross-record references and explanatory text.

**Cross-record reference integrity**

- 2,445 records contain references in both fields.
- This represents 4,890 field-level reference occurrences.
- Both fields point to the same target record in all 2,445 cases.
- Tested target identifiers and ASN/DN references reconcile, while some other shipment attributes differ.

**Missing insurance**

- 287 records have missing insurance values.
- 360 records have missing shipment-mode values.
- 106 records have both values missing.
- Missing insurance does not automatically establish that a shipment was uninsured.

---

## 3. Methodology

The investigation followed an evidence-led workflow.

### Step 1 — Source inspection

- Reviewed dataset structure, record counts, field types, and identifiers.
- Checked for exact duplicate rows.
- Preserved the original source dataset.

### Step 2 — SQL investigations

PostgreSQL was used to investigate shipment-level patterns, compare related fields, test date relationships, identify candidate duplicate records, and reconcile cross-record references.

The publication SQL file is available at:

`SQL/SCMS_SQL_Publication_Ready.sql`

### Step 3 — Python investigations

Python and pandas were used for focused investigations, classification, numerical comparisons, record-level evidence generation, and validation.

The publication scripts are organized into:

- `python/investigations/`
- `python/register_workflow/`
- `python/validation/`
- `python/utilities/`

### Step 4 — Findings prioritization

Eight findings were documented in an initial register and a prioritized register.

Each finding includes its investigation context, evidence, classification, severity, recommended action, and validation status.

### Step 5 — Evidence reconciliation

Selected evidence outputs were mapped to their corresponding findings.

The publication package contains 32 unique CSV files and 33 finding/purpose assignments. The reference-example file shared by DQ-06 and DQ-07 is counted once in the unique file total.

### Step 6 — Reporting and visualization

The investigation was documented in a written report and supported by a Power BI dashboard developed during the project.

The report is available in both formats:

- `reports/SCMS_Data_Quality_Investigation_Report.md`
- `reports/SCMS_Data_Quality_Investigation_Report.pdf`

The Power BI dashboard file is not included in this release package.

---

## 4. Recommended Actions

The investigation translates the observed patterns into practical follow-up priorities.

| Area | Recommended action |
|---|---|
| Dosage | Confirm product-specific applicability and define required-field rules. |
| Dates | Establish valid workflow states, date definitions, and chronology checks. |
| Pricing | Confirm the authoritative pricing formula, UOM convention, and rounding policy. |
| Zero prices | Review zero-price records against approved pricing and product rules. |
| Potential duplicates | Validate candidate pairs against shipment documentation before any deduplication. |
| Weight and freight | Define permitted value types and formalize cross-record reference handling. |
| Reference integrity | Establish documented rules for reference resolution and attribute comparison. |
| Insurance | Confirm applicability requirements and investigate missing-value patterns. |

These actions are recommendations for validation and control design, not claims that the underlying business processes have failed.

---

## 5. Repository Structure

```text
github_release/
│
├── README.md
├── EVIDENCE_TO_FINDING_MAP.md
├── PYTHON_EXECUTION_PLAN.md
├── PUBLICATION_EVIDENCE_MANIFEST.csv
├── RELEASE_COPY_VERIFICATION.csv
│
├── evidence/
│   └── 32 selected evidence CSV files
│
├── python/
│   ├── investigations/
│   ├── register_workflow/
│   ├── validation/
│   └── utilities/
│
├── SQL/
│   └── SCMS_SQL_Publication_Ready.sql
│
|-- dashboard/
|   |-- project_03_data_nobody_wants_to_clean.pbix
|   `-- project_03_data_nobody_wants_to_clean.pdf
|
└── reports/
    ├── SCMS_Data_Quality_Investigation_Report.md
    └── SCMS_Data_Quality_Investigation_Report.pdf
```

### Important supporting documents

- **Evidence-to-Finding Map:** Explains which evidence files support each finding and documents publication limitations.
- **Python Execution Plan:** Describes the script inventory, execution considerations, and known workflow limitations.
- **Publication Evidence Manifest:** Records selected evidence filenames, sizes, row counts, and source hash comparisons.
- **Release Copy Verification:** Records SHA-256 comparisons between the publication workspace and this release package.

---

## 6. Evidence Integrity and Reproducibility

The selected evidence package contains 32 CSV files.

The evidence files were compared against their original project outputs using SHA-256 hashes:

- Evidence source comparisons: 32/32 matched.
- Release-copy comparisons: 63/63 matched.
- Release-copy hash mismatches: 0.

These checks establish file-copy integrity. They do not independently reproduce every analytical result.

The project includes SQL and Python investigation scripts, but a complete independent rerun of all investigations and regeneration of every evidence file has not been completed.

Some scripts have execution dependencies, fixed output paths, or overwrite risks. Refer to `PYTHON_EXECUTION_PLAN.md` before executing them. In particular, the register-building and refresh scripts should not be run indiscriminately against an existing project workspace.

The original dataset is not included in this repository. The investigation should therefore be interpreted alongside the documented methodology, evidence files, and report.

---

## 7. Limitations and Interpretation

This investigation identifies patterns requiring review. It does not establish that every unusual value represents a business defect.

The following limitations apply:

- Business applicability of some missing fields remains unconfirmed.
- Workflow labels and operational meanings require source-system clarification.
- Pricing conventions and authoritative formulas have not been independently confirmed.
- Potential duplicate pairs are not confirmed duplicate shipments.
- Cross-record references have been tested, but their business meaning and transfer rules remain unresolved.
- Missing insurance values do not establish that shipments were uninsured.
- No financial-loss, fraud, or operational-failure estimate is claimed.

The findings should be used to guide validation, documentation, and control improvements rather than as automatic correction instructions.

---

## 8. Tools and Technologies

- PostgreSQL
- SQL
- Python
- pandas
- Power BI
- CSV-based evidence management
- SHA-256 file integrity verification

---

## 9. Project Outcome

This project demonstrates an end-to-end approach to investigating complex operational data quality issues.

The work moves beyond identifying missing values or unusual records. It establishes measurable findings, separates confirmed observations from unresolved interpretations, preserves record-level evidence where selected, reconciles findings to a documented register, and translates the results into practical follow-up actions.

**The central principle: data should not be corrected simply because it looks unusual. It should first be understood, tested, documented, and validated against the business process it represents.**