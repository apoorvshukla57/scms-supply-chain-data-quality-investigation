# Project 03 — Python Execution Plan

## 1. Purpose

Document the selected Python scripts, their roles, known input/output behaviour, execution risks, and publication-readiness status for the SCMS Data Quality Investigation.

This plan distinguishes:

- Core analytical investigations.
- Findings register construction and updates.
- Validation and quality assurance.
- Supporting utilities.

It separates verified facts from outstanding execution and reproducibility work. Inclusion in the publication workspace does not mean a script is approved for unrestricted execution.

## 2. Current Status

**Publication preparation — script organization, copy-integrity verification, substantial path isolation, selected execution testing, findings-register reconciliation, evidence mapping, and publication evidence validation completed. Full workflow reproducibility remains unestablished.**

The publication workspace contains 25 selected canonical Python scripts.

All 25 publication copies were SHA-256 verified against their corresponding original files, with zero mismatches. This confirms copy integrity at the time of verification, not independent reproducibility or unrestricted execution readiness.

Publication preparation has progressed beyond script organization:

- The 12 core investigation scripts that generate output files have undergone publication output-path isolation. Script 52 is read-only and retains its hardcoded absolute source-data path.
- Selected investigation scripts have been reviewed and successfully executed.
- Register workflow scripts have been reviewed, with state-changing behaviour and execution risks documented.
- All five selected validation scripts have undergone review and their configured checks have been executed successfully.
- All four supporting utility scripts have been reviewed and successfully executed.
- The publication evidence package contains 32 selected unique CSV files.
- The final configured evidence audit passed all checks for the 32 manifest-listed files.
- Evidence-to-finding mapping coverage has been reconciled: 33 mapping assignments correspond to 32 unique files because one file is shared by DQ-06 and DQ-07.
- The Evidence-to-Finding Map and publication evidence inventory have been reconciled.
- The investigation report has been replaced with the revised version, including the reconciled evidence index.
- The Power BI dashboard has already undergone review and has been accepted. No additional dashboard review is included in the remaining work.

Execution testing remains selective. Successful execution of individual scripts does not establish that all 25 scripts can be run as a complete, reproducible workflow.

Script 51 remains a historical register-recalibration workflow and still references the original project output directory. It is not approved for the publication execution workflow.

The original source dataset, original investigation scripts, and finalized findings registers remain preserved. State-changing register scripts must not be executed casually against the authoritative publication files.

Remaining reproducibility work includes documenting the execution environment and dependencies, completing the script-by-script input/output and overwrite-risk specification, defining a controlled execution sequence, and comparing regenerated outputs with the frozen evidence package where applicable.

**Current readiness distinction**

- Script copy integrity: verified for 25/25 scripts.
- Evidence integrity: verified for 32/32 evidence files.
- Evidence-to-finding mapping: reconciled; 33 assignments across 32 unique files.
- Findings-register reconciliation: completed for the eight findings and finalized priorities.
- Selected execution testing: completed successfully for reviewed scripts.
- Report evidence-index reconciliation: completed.
- Dashboard review: completed and accepted.
- Full workflow reproducibility: not yet established.
- Independent analytical rerun of all investigations: not completed.

## 3. Execution and Preservation Rules

- Preserve the original source dataset.
- Preserve original investigation scripts and outputs.
- Perform publication improvements only on publication copies.
- Do not rerun state-changing register scripts during routine publication preparation.
- Do not assume filename order proves execution dependency.
- Record inputs, outputs, dependencies, and modification behaviour.
- Preserve the finalized DQ-01 to DQ-08 priority baseline.
- Do not silently change analytical definitions, tolerances, or findings.
- Distinguish historical investigation scripts from the approved publication workflow.
- Do not claim reproducibility until dependencies and execution requirements have been verified.
- Do not execute scripts that write to original project output locations as part of the publication workflow.
- Treat validation output as evidence of the specific checks performed, not proof of comprehensive analytical correctness.
- Do not replace frozen publication evidence without a controlled comparison and explicit approval.

## 4. Final Priority Baseline

| Finding | Priority |
|---|---|
| DQ-01 | P2 |
| DQ-02 | P1 |
| DQ-03 | P3 |
| DQ-04 | P2 |
| DQ-05 | P2 |
| DQ-06 | P1 |
| DQ-07 | P2 |
| DQ-08 | P2 |

Priority distribution: 2 P1, 5 P2, 1 P3.

DQ-06 and DQ-07 overlap and must not be double-counted.

This is the finalized publication baseline. Any proposed change requires evidence, review, and explicit approval.

## 5. Publication Script Classification

### 5.1 Core Investigations — 13 Scripts

Location: `python/investigations/`

| Script | Investigation |
|---|---|
| 26 | Pricing discrepancy patterns |
| 29 | Unit-price rounding hypothesis |
| 30 | Line-value relationship |
| 32 | Line-value rounding |
| 35 | Date-field quality |
| 37 | Zero unit prices |
| 40 | Potential duplicate shipments |
| 42 | Weight and freight value classification |
| 43 | Refined weight and freight categories |
| 46 | Missing dosage |
| 48 | Missing insurance |
| 52 | Insurance and shipment-mode overlap |
| 61 | Unit-price/UOM rounding validation |

These scripts support the eight finalized findings. Some investigate separate analytical tests within the same finding.

The reviewed scripts read the original shipment dataset directly. No confirmed dependency chain between these 13 scripts has been established.

Script 43 is conceptually a refinement of the weight/freight classification work, but its reviewed source reads the original dataset directly rather than consuming Script 42's output.

### 5.2 Register Workflow — 3 Scripts

Location: `python/register_workflow/`

| Script | Purpose | Modification behaviour |
|---|---|---|
| 23 | Build initial findings register | Creates or overwrites the initial register CSV |
| 51 | Recalibrate investigation priorities | Updates the prioritized register using backups, a temporary file, and read-back checks |
| 54 | Refresh DQ-06/DQ-07 reference findings | Updates both register files |

These scripts are retained for workflow documentation and historical reproducibility.

They are state-changing and must not be executed casually against the finalized publication registers.

Script 51 has more extensive safeguards than the other reviewed register writers, but those safeguards do not make unrestricted execution appropriate.

### 5.3 Validation — 5 Scripts

Location: `python/validation/`

| Script | Purpose | Current behaviour and validation status |
|---|---|---|
| 24 | Verify selected register evidence | Hardened and successfully executed. Performs 18 configured checks covering DQ-01 through DQ-08, including DQ-05 and DQ-07. Writes `register_evidence_verification.csv`. |
| 50 | Findings register QA | Hardened and successfully executed. Checks finding IDs, required fields, duplicates, approved differences, unexpected differences, and priority assignments. Read-only. |
| 53 | Final register reconciliation | Hardened and successfully executed. Checks register structure, finding IDs, missing or duplicate records, blank fields, unexpected IDs, and priority consistency. Read-only; validation failures produce a nonzero exit status. |
| 56 | Final evidence audit | Successfully executed after the evidence package was updated. Checks the manifest, evidence mappings for all eight findings, file hashes, file sizes, CSV readability, row counts, evidence-folder inventory, and findings-register structure and priorities. Read-only. |
| 59 | Section 04 register reconciliation | Hardened and successfully executed. Compares the Section 04 reconciliation evidence with the prioritized register and expected priorities. Writes `section04_register_reconciliation.csv`. The completed run reported 8 matches and 0 exceptions. |

**Validation coverage and limitations**

- **Script 24:** The 18 checks provide selected evidence-to-register consistency checks, not comprehensive independent verification of every analytical result. Its DQ-02 checks cover the two identified workflow text patterns; they do not constitute complete validation of all date fields or date semantics.
- **Script 50:** Confirms the structure, completeness, approved differences, and priority consistency of the findings registers. It does not independently rerun the underlying investigations.
- **Script 53:** Provides a stricter register-reconciliation check and a nonzero failure status. Its successful execution confirms the configured reconciliation checks, not the analytical correctness of every finding.
- **Script 56:** The final audit maps evidence to all eight findings: DQ-01 (3 files), DQ-02 (2), DQ-03 (9), DQ-04 (4), DQ-05 (2), DQ-06 (3), DQ-07 (1), and DQ-08 (5), alongside four shared governance mappings. These represent 33 mapping assignments across 32 unique CSV files because `weight_freight_reference_examples.csv` is shared by DQ-06 and DQ-07. All 32 manifest-listed evidence files passed the configured integrity and readability checks. These checks establish package integrity and mapping coverage, not independent analytical correctness.
- **Script 59:** The completed reconciliation produced 8 matches and 0 exceptions. This confirms consistency between the configured Section 04 reconciliation evidence and the prioritized register; it does not independently validate the underlying investigation.

**Overall validation status**

All five validation scripts have undergone review, and their selected configured checks have been executed successfully. The validation layer provides register reconciliation, selected evidence consistency checks, and publication-package integrity checks.

It must not be presented as a complete independent rerun of all eight investigations. Full analytical reproducibility remains a separate outstanding task.

### 5.4 Utilities — 4 Scripts

Location: `python/utilities/`

| Script | Purpose | Current behaviour and validation status |
|---|---|---|
| 33 | Inspect findings register | Successfully executed. Reads and displays the initial and prioritized findings registers from the publication execution workspace. Read-only. |
| 57 | Evidence inventory | Successfully executed. Inventories the 32 selected publication evidence files. Read-only. |
| 58 | Inspect evidence verification | Successfully executed. Reads and displays the evidence verification results and both findings registers from the publication evidence directory. Read-only. |
| `inspect_dashboard_sources.py` | Inspect dashboard source evidence | Successfully executed. Reads and displays the eight selected dashboard source files from the publication evidence directory. Read-only. |

These are supporting inspection and reporting utilities, not core analytical investigations.

**Execution and path review**

- All four scripts were reviewed and successfully executed from the publication workspace.
- Their paths were adjusted to reference the publication evidence or execution directories as appropriate.
- Their successful runs confirmed that the expected files were accessible and readable.
- No source datasets, findings registers, or evidence files were modified by these utility executions.
- The scripts still assume the project root is `C:\Project_03`; they have not been made fully portable to arbitrary directory structures.

These utilities support inspection and reporting. Their successful execution does not independently validate the analytical correctness of the findings or dashboard measures.

## 6. Execution Dependencies and Workflow

**Status: Partially reviewed — core input/output behaviour documented; complete script-by-script execution order and full workflow reproducibility remain unapproved.**

The reviewed core investigation scripts generally read the original shipment CSV directly. No demonstrated linear dependency chain has been established in which one core investigation script must generate an input for another.

The publication workflow therefore consists primarily of independent investigations, followed by controlled evidence consolidation, register management, and validation.

The logical workflow is:

1. Confirm the source dataset, project structure, Python environment, and expected schema.
2. Run approved core investigations in the controlled publication environment.
3. Generate, inspect, and preserve the resulting analytical evidence.
4. Construct or load the authoritative findings registers when required.
5. Apply or verify the finalized priority classification through a controlled process.
6. Perform register and evidence validation.
7. Reconcile the findings registers against the publication evidence package.
8. Reconcile the report's evidence index against the Evidence-to-Finding Map and publication manifest.
9. Prepare final documentation and publication outputs.

The Power BI dashboard has already been reviewed and accepted. Its review is not an outstanding workflow task.

This is a logical workflow, not an approved script-by-script execution order. The core investigations have been reviewed for path behaviour, but a complete controlled rerun and output reconciliation of every investigation has not been completed.

### 6.1 Known Input/Output Behaviour

| Script or group | Known input | Known output or behaviour |
|---|---|---|
| 26 | Original shipment CSV | Five pricing discrepancy evidence CSVs in publication execution outputs |
| 29 | Original shipment CSV | Three unit-price rounding hypothesis CSVs |
| 30 | Original shipment CSV | Five line-value relationship CSVs |
| 32 | Original shipment CSV | Three line-value rounding CSVs |
| 35 | Original shipment CSV | Two date-field quality CSVs |
| 37 | Original shipment CSV | Four zero-unit-price CSVs |
| 40 | Original shipment CSV | Two potential-duplicate CSVs |
| 42 | Original shipment CSV | Three weight/freight classification CSVs |
| 43 | Original shipment CSV | Two refined weight/freight category and reference-example CSVs |
| 46 | Original shipment CSV | Six missing-dosage evidence CSVs |
| 48 | Original shipment CSV | Four missing-insurance evidence CSVs |
| 52 | Original shipment CSV | Read-only insurance/mode overlap analysis; no output files |
| 61 | Original shipment CSV | Four unit-price/UOM rounding validation CSVs |
| 23 | Finding definitions embedded in script | Writes `initial_findings_register.csv`; overwrites an existing file without creating a backup |
| 51 | Initial and prioritized registers in the original `C:\Project_03\outputs\` directory | Historical priority-recalibration workflow; creates backups and temporary output when changes are required |
| 54 | Initial and prioritized registers in publication execution outputs | Updates DQ-06 and DQ-07 register details in both files; creates fixed-name backups and overwrites the registers |
| 24 | Original shipment CSV and publication register/evidence checks | Writes `register_evidence_verification.csv` |
| 50 | Findings registers | Read-only register QA; prints validation results |
| 53 | Findings registers | Read-only register reconciliation; produces a nonzero exit status for configured validation failures |
| 56 | Publication evidence manifest, evidence files, and findings registers | Read-only final evidence audit; prints audit results |
| 59 | Section 04 reconciliation evidence and prioritized register | Writes `section04_register_reconciliation.csv` |
| 33 | Publication findings registers | Read-only register inspection |
| 57 | Publication evidence directory | Read-only inventory of evidence files |
| 58 | Publication evidence verification and findings registers | Read-only evidence and register inspection |
| `inspect_dashboard_sources.py` | Eight selected dashboard source evidence files | Read-only dashboard-source inspection |

The core investigation scripts have individual outputs rather than a demonstrated shared output dependency. For example, Script 43 reads the original dataset directly; it does not consume Script 42's generated classification file.

The principal publication locations are:

- Original input: `C:\Project_03\dataset\Suppy_Chain_Shipment_Data.csv`
- Publication execution outputs: `C:\Project_03\publication\execution\outputs\`
- Publication evidence: `C:\Project_03\publication\evidence\`
- Publication Python scripts: `C:\Project_03\publication\python\`

The publication execution output directory currently contains staged registers and selected generated outputs. It must not be treated as an empty directory or disposable temporary workspace.

### 6.2 Path and Execution Risk

The 12 core investigation scripts that generate output files have undergone publication output-path isolation. Their analytical input remains the original source CSV, while their generated outputs are directed to the publication execution workspace.

Important exceptions and qualifications remain:

- Script 52 is read-only but retains a hardcoded absolute path to the original source CSV.
- Script 51 still references the original `C:\Project_03\outputs\` directory. Its priority recalibration has already been applied; it is treated as a historical workflow, not an approved publication execution script.
- Scripts 23 and 54 are path-isolated but modify the findings registers. Their overwrite and backup behaviour must be considered before execution.
- Script 23 overwrites the initial findings register without creating a backup.
- Script 54 creates fixed-name backups and updates both register files. Existing backups may prevent another execution.
- Scripts that write to publication execution outputs may overwrite previously generated files with matching names.

All scripts continue to assume the project root `C:\Project_03`; they are not fully portable to arbitrary directory structures.

**Execution safeguards**

Before rerunning any script:

1. Confirm its exact input and output paths.
2. Identify all existing files with matching output names.
3. Determine whether the script overwrites, appends, or creates backups.
4. Preserve the current authoritative registers and evidence files.
5. Execute only within the approved publication workflow.
6. Compare regenerated outputs against the existing evidence before replacing any frozen publication artifact.

**Do not run the entire script inventory as a batch.** Execution must be controlled and based on the individual script's input, output, and overwrite behaviour.

The current publication package has passed its configured evidence-integrity audit, but this does not establish that every investigation can be independently rerun with identical results.

## 7. Register-Changing Scripts

The following selected scripts modify register files:

- Script 23 — initial register construction.
- Script 51 — priority recalibration.
- Script 54 — DQ-06/DQ-07 register refresh.

These scripts are state-changing.

Script 51 remains in the selected script inventory for historical workflow documentation, but it is excluded from the approved publication execution workflow because it references the original project output directory and its priority recalibration has already been applied.

Do not rerun these scripts merely to demonstrate execution.

Any future execution must:

- Use controlled copies of the relevant inputs.
- Preserve the finalized publication baseline.
- Write only to designated publication output locations.
- Validate the resulting register before acceptance.
- Retain backups and execution records where appropriate.

## 8. Evidence Outputs

The publication evidence package is located at:

`publication/evidence/`

It contains **32 selected unique CSV files**, organized to support the eight finalized findings and shared publication governance checks.

The evidence package covers:

- Missing dosage.
- Date-field quality.
- Pricing discrepancies and rounding tests.
- Zero unit prices.
- Potential duplicate shipments.
- Weight and freight classifications.
- Cross-record references.
- Missing insurance.
- Findings registers and validation results.

The detailed evidence-to-finding mapping is documented separately in:

`EVIDENCE_TO_FINDING_MAP.md`

The publication evidence manifest is:

`PUBLICATION_EVIDENCE_MANIFEST.csv`

### 8.1 Evidence-to-Finding Coverage

| Finding | Evidence files mapped |
|---|---:|
| DQ-01 — Missing dosage | 3 |
| DQ-02 — Date-field quality | 2 |
| DQ-03 — Pricing discrepancies | 9 |
| DQ-04 — Zero unit prices | 4 |
| DQ-05 — Potential duplicate shipments | 2 |
| DQ-06 — Weight and freight values | 3 |
| DQ-07 — Cross-record references | 1 |
| DQ-08 — Missing insurance | 5 |
| Shared governance evidence | 4 |
| **Total listed mapping assignments** | **33** |

The mapping contains 29 finding-specific assignments and 4 shared governance assignments, giving 33 assignments in total.

The package contains 32 unique CSV files because `weight_freight_reference_examples.csv` is intentionally shared by DQ-06 and DQ-07. It is therefore counted once in the unique-file total, although it appears in two finding mappings.

The mapping-assignment count is reconciled. The 33 assignments must not be confused with the 32 unique files in the package.

### 8.2 Evidence Integrity Verification

All 32 selected unique evidence files were checked against the publication manifest.

The final audit verified:

- SHA-256 hashes.
- Recorded file sizes.
- CSV readability.
- Recorded data-row counts.
- Evidence-folder inventory against the manifest.
- Findings-register IDs, required fields, and priority assignments.

All 32 evidence files passed the configured checks, with no hash, size, readability, or row-count exceptions.

The final audit was performed using Script 56. Its configured checks completed successfully.

The register evidence verification output was also updated to contain 18 checks covering selected evidence metrics across DQ-01 through DQ-08. The updated output was promoted into the publication evidence package, and the manifest was updated accordingly.

### 8.3 Interpretation and Limitations

The integrity checks establish that the selected publication evidence files match their recorded manifest entries and satisfy the configured structural checks.

The evidence mapping establishes that all eight findings have selected supporting files in the package. The mapping contains 33 assignments across 32 unique CSV files because `weight_freight_reference_examples.csv` is shared by DQ-06 and DQ-07.

The report's Appendix has been reconciled against the Evidence-to-Finding Map. It documents the selected evidence files, shared assignments, intentionally excluded outputs, and publication verification limitations.

These results do not establish that every evidence file can be regenerated by the 25 selected scripts, nor do they independently revalidate every analytical result.

A complete independent rerun of all investigations and reconciliation of every regenerated output against the frozen evidence package remains outstanding.

## 9. Reproducibility Limitations and Required Improvements

Publication preparation has addressed several important reproducibility, path-isolation, validation, and evidence-integrity issues. However, full workflow reproducibility and independent analytical rerunning have not yet been established.

The status of the improvements is documented below.

### 9.1 Completed Improvements

The following improvements have been completed and selectively tested:

- Publication copies of the selected 25 Python scripts were SHA-256 verified against their corresponding original files.
- The 12 core investigation scripts that generate output files have undergone publication output-path isolation. Script 52 remains read-only and retains its hardcoded absolute source-data path.
- Script 43 was updated to handle non-finite numeric values during weight/freight classification and successfully executed.
- Script 61 was finalized for publication output paths, executed, and reconciled against its saved outputs. The original project script remains unchanged.
- Script 24 was hardened and successfully executed with 18 configured evidence-verification checks.
- Script 50 was hardened and successfully executed for findings-register QA.
- Script 53 was hardened to return a nonzero exit status for configured validation failures and successfully executed.
- Script 59 was hardened and successfully executed for Section 04 register reconciliation.
- Script 56 completed the final configured audit of all 32 publication evidence files.
- The four utility scripts were reviewed and successfully executed using publication paths.
- The findings registers, evidence mappings, and publication evidence manifest were reconciled against the finalized project baseline.
- The report's Appendix was updated using the authoritative Evidence-to-Finding Map.
- The dashboard has already been reviewed and accepted; no further dashboard review is outstanding.

These improvements establish selected copy-integrity, execution, reconciliation, documentation, and evidence-package checks. They do not establish complete workflow reproducibility.

### 9.2 Environment — Outstanding

The following environment documentation remains incomplete:

- Document the Python version used for the publication execution environment.
- Identify and document required package versions, including pandas.
- Confirm compatibility with the date-parsing behaviour used by the investigation scripts.
- Provide a controlled environment setup process, preferably through a documented dependency file.
- Record the commands and environment assumptions required to reproduce selected script executions.

The complete environment specification has not yet been finalized.

### 9.3 Paths, Inputs, and Outputs — Partially Completed

- The 12 core investigation scripts that generate output files have publication-specific output paths.
- Script 52 remains read-only but uses a hardcoded absolute path to the original source CSV.
- Script 51 retains its original output-directory reference and is treated as a historical, already-applied priority-recalibration workflow rather than an approved publication execution script.
- Scripts 23 and 54 have publication-specific output paths but modify the findings registers; their overwrite and backup behaviour must remain documented.
- A detailed inventory of the known inputs and output filenames has been established, but the complete script-by-script specification and overwrite-risk review still require final reconciliation.
- The scripts continue to assume the project root `C:\Project_03` and are not fully portable to arbitrary directory structures.

### 9.4 Analytical Robustness — Partially Completed

- Non-finite numeric handling was added to Script 43 and tested.
- Script 52 checks missing insurance and shipment-mode values, including whitespace-only values.
- Script 61's rounding validation was executed and reconciled against its saved outputs.
- Existing analytical definitions, tolerances, and assumptions have been preserved during publication preparation.
- Original source values and selected evidence files have been retained for auditability.

Further work remains to confirm the execution behaviour and output consistency of the remaining investigation scripts.

No analytical conclusion should be changed solely to make the publication scripts easier to execute.

### 9.5 Validation Behaviour — Selected Improvements Completed

- Scripts 24, 50, 53, and 59 have undergone validation hardening and successful execution testing.
- Script 56's final audit covers all eight findings and all 32 manifest-listed evidence files.
- Validation outputs distinguish selected metric checks, register consistency, evidence mapping, and file-integrity checks.

The remaining limitation is scope: these checks do not independently rerun every analytical investigation or prove every business interpretation.

### 9.6 Publication Verification — Partially Completed

The following work remains before claiming full reproducibility:

- Complete the final script-to-input/output and overwrite-risk mapping.
- Review Script 52's hardcoded source path and document its read-only behaviour.
- Define the approved status of historical and state-changing register scripts.
- Complete controlled execution QA for the remaining selected investigation scripts.
- Compare regenerated outputs with the frozen publication evidence package where applicable.
- Record expected differences, execution results, and any unresolved exceptions.
- Verify that publication executions do not modify the original source dataset or original project artifacts.
- Complete the Python environment and dependency specification.

The report's evidence index and evidence-to-finding mapping have been reconciled. The dashboard has already been reviewed and accepted. Neither task should be treated as an outstanding dashboard-review or report-Appendix task.

A complete independent rerun of all investigations has not been performed.

### 9.7 Publication Safeguards

The following safeguards apply throughout the remaining work:

- Preserve the original source dataset and original investigation scripts.
- Do not execute historical or state-changing register scripts without a specific reason and a verified backup.
- Do not overwrite frozen evidence or authoritative registers without controlled comparison and approval.
- Preserve established analytical definitions, tolerances, and assumptions unless a separately documented validation justifies a change.
- Retain source values, execution outputs, and supporting evidence for auditability.
- Clearly distinguish successful file-integrity checks from independent analytical validation.

Publication improvements must not silently alter established analytical conclusions.

## 10. Publication Verification Status

| Component | Status |
|---|---|
| Original script inventory | Complete |
| Script classification | Complete provisionally |
| Publication folder structure | Complete |
| Core investigation copies | 13/13 SHA-256 verified |
| Register workflow copies | 3/3 SHA-256 verified |
| Validation copies | 5/5 SHA-256 verified |
| Utility copies | 4/4 SHA-256 verified |
| Total canonical script copies | 25/25 SHA-256 verified |
| Evidence package | 32/32 passed configured manifest integrity checks |
| Core investigation input pattern | Reviewed; core investigations read the original CSV directly |
| Logical investigation workflow | Identified; complete script-by-script execution order not approved |
| Script-to-script dependency mapping | Partially reviewed; no linear dependency chain demonstrated among core investigations |
| Input/output specification | Partially documented; known inputs and output filenames identified, final reconciliation pending |
| Path isolation | Substantially completed; Script 52 retains a hardcoded read-only source path, Script 51 remains historical, and register scripts require execution safeguards |
| Environment and package documentation | Pending |
| Validation script hardening | Selected scripts completed and successfully tested |
| Utility script review and execution | 4/4 reviewed and successfully executed |
| Controlled execution QA | Partially completed; selected investigation, validation, and utility scripts successfully executed |
| Regenerated-output comparison | Partially completed; selected outputs reconciled, with further investigation-level comparison pending |
| Findings register reconciliation | Completed; 8 findings reconciled, with priorities confirmed |
| Evidence-to-finding mapping | Completed; 33 mapping assignments across 32 unique files, with one shared DQ-06/DQ-07 file |
| Final evidence integrity audit | Passed all configured checks for 32 manifest-listed files |
| Report evidence-index reconciliation | Completed |
| Power BI dashboard review | Completed and accepted |
| Independent analytical rerun of all investigations | Not completed |
| Full publication reproducibility | Not yet established |

### Overall Status

The publication package has completed:

- Script-copy integrity verification.
- Selected execution testing.
- Findings-register reconciliation.
- Evidence-to-finding mapping reconciliation.
- The configured 32-file evidence integrity audit.
- Report evidence-index reconciliation.
- Dashboard review and acceptance.

The project is not yet classified as fully reproducible.

Remaining work is concentrated on the Python execution environment, dependency documentation, completion of the script input/output and overwrite-risk specification, controlled execution of the remaining investigations, and comparison of regenerated outputs against the frozen publication evidence package.

The original source dataset, original investigation scripts, and original project outputs remain preserved. The finalized findings and publication evidence should not be altered without a documented analytical reason and controlled validation.