# Holte-16 reconstruction specification

## General rules

1. Acquire only the bundle URLs pinned in `manifest.json` and verify their SHA-256 hashes.
2. Extract the listed raw files and verify their file hashes.
3. Preserve source row order and source values.
4. Interpret a literal `?` as the source missing-value marker; retain it as a value. Do not drop or impute missing data.
5. Apply only the transformations below.
6. Normalize packaging by adding a header and moving the target to the final `class` column. This does not alter observations.
7. Validate rows, predictor columns, class cardinality, majority-class percentage rounded to one decimal, and the presence/absence of missing values against Holte's Table 2.

## Dataset recipes

### BC - Breast Cancer

- Source: UCI 14, `breast-cancer.data`.
- Parse: comma-delimited, 10 fields; source class is field 1.
- Transform: none from Appendix B; move class after the nine predictors.
- Expected: 286 rows, 9 predictors, 2 classes, 70.3% baseline, missing values present.

### CH - Chess King-Rook vs. King-Pawn

- Source: UCI 22, `kr-vs-kp.data`.
- Parse: comma-delimited, 37 fields; class is final.
- Transform: none.
- Expected: 3,196 rows, 36 predictors, 2 classes, 52.2% baseline, no missing values.

### GL - Glass Identification

- Source: UCI 42, `glass.data`.
- Parse: comma-delimited, 11 fields; first field is an observation ID; final field is class.
- Transform: delete the first field. Retain source class labels 1, 2, 3, 5, 6, and 7; label 4 has no rows.
- Expected: 214 rows, 9 predictors, 6 observed classes, 35.5% baseline, no missing values.

### G2 - Derived two-class Glass

- Parent: GL after its ID deletion.
- Transform: retain rows whose original class is 1, 2, or 3; map class 3 to class 1; discard original classes 5, 6, and 7. Class 4 is absent.
- Resulting class counts: class 1 = 87 (70 original class 1 + 17 original class 3); class 2 = 76.
- Expected: 163 rows, 9 predictors, 2 classes, 53.4% baseline, no missing values.

### HD - Cleveland Heart Disease

- Source: UCI 45, `cleve.mod` (the exact historical filename survives in the current bundle).
- Parse: discard `%` comment lines; split remaining lines on whitespace into 15 fields.
- Source structure: 13 mixed-type predictors, a binary `buff`/`sick` class, and a final original diagnosis code (`H`, `S1`, `S2`, etc.).
- Transform: delete only the final diagnosis-code field; retain the penultimate binary class.
- Expected: 303 rows, 13 predictors, 2 classes, 54.5% baseline, missing values present.

### HE - Hepatitis

- Source: UCI 46, `hepatitis.data`.
- Parse: comma-delimited, 20 fields; source class is first.
- Transform: none from Appendix B; move class after the 19 predictors.
- Expected: 155 rows, 19 predictors, 2 classes, 79.4% baseline, missing values present.

### HO - Horse Colic

- Source: UCI 47, `horse-colic.data` followed by `horse-colic.test`.
- Parse: whitespace-delimited, 28 fields named V1-V28.
- Transform: concatenate the 300 training rows then the 68 test rows; use V24 as class; delete V3 and V25-V28; retain predictors V1, V2, and V4-V23.
- Expected: 368 rows, 22 predictors, 2 classes, 63.0% baseline, missing values present.

### HY - Hypothyroid

- Source: UCI 102, `hypothyroid.data`.
- Parse: comma-delimited, 26 fields; class is first.
- Transform: none from Appendix B; move class after the 25 predictors.
- Expected: 3,163 rows, 25 predictors, 2 classes, 95.2% baseline, missing values present.

### IR - Iris

- Source: UCI 53, `iris.data` (not `bezdekIris.data`).
- Parse: comma-delimited, five fields; class is final. Ignore empty trailing lines.
- Transform: none.
- Expected: 150 rows, 4 predictors, 3 classes, 33.3% baseline, no missing values.

### LA - Labor Relations

- Source: UCI 56, usable C4.5 split `C4.5/labor-neg.data` followed by `C4.5/labor-neg.test`.
- Parse: comma-delimited, 17 fields; class is final.
- Transform: concatenate the 40 data rows then the 17 test rows. No further transformation is specified by Holte.
- Why these files: the root `labor-negotiations.data` and `.test` are email-format source material; the C4.5 files are usable data and reproduce Holte's 57 rows, 16 predictors, two classes, 64.9% baseline, and missing-value flag.
- Expected: 57 rows, 16 predictors, 2 classes, 64.9% baseline, missing values present.

### LY - Lymphography

- Source: UCI 63, `lymphography.data`.
- Parse: comma-delimited, 19 fields; class is first; move it after the 18 predictors.
- Holte transformation: none.
- Historical expectation: 141 rows, 18 predictors, 4 classes, 56.7% baseline, no missing values.
- Current authoritative observation: 148 rows; class counts 2, 81, 61, and 4; 54.7% baseline; 18 predictors; no missing values.
- Fidelity rule: build the current 148-row file as `data/LY.csv`, flag `version_drift_unresolved`, and never select seven rows without a recovered authoritative snapshot or documented record identities.

### MU - Mushroom

- Source: UCI 73, `agaricus-lepiota.data`.
- Parse: comma-delimited, 23 fields; class is first.
- Transform: none from Appendix B; move class after the 22 predictors.
- The `?` values in `stalk-root` are retained as missing values.
- Expected: 8,124 rows, 22 predictors, 2 classes, 51.8% baseline, missing values present.

### SE - Sick Euthyroid

- Source: UCI 102, `sick-euthyroid.data`.
- Parse: comma-delimited, 26 fields; class is first.
- Transform: none from Appendix B; move class after the 25 predictors.
- Expected: 3,163 rows, 25 predictors, 2 classes, 90.7% baseline, missing values present.

### SO - Soybean Small

- Source: UCI 91, `soybean-small.data`.
- Parse: comma-delimited, 36 fields; class is final.
- Transform: none.
- Expected: 47 rows, 35 predictors, 4 classes, 36.2% baseline, no missing values.

### VO - Congressional Voting Records

- Source: UCI 105, `house-votes-84.data`.
- Parse: comma-delimited, 17 fields; class is first.
- Transform: none from Appendix B; move class after the 16 predictors.
- Expected: 435 rows, 16 predictors, 2 classes, 61.4% baseline, missing values present.

### V1 - Derived Voting Records without the best cue

- Parent: VO in source feature order.
- Transform: delete predictor 4, `physician-fee-freeze`; retain the other 15 predictors and the original class.
- Expected: 435 rows, 15 predictors, 2 classes, 61.4% baseline, missing values present.

## Validation behavior

`scripts/holte16.py validate` checks every built CSV and emits `validation-report.json`. A normal validation run passes when all 15 reproducible datasets match Holte and LY matches the pinned current UCI file while carrying its drift flag. `--strict-historical` additionally requires LY to match Holte's 141-row summary and therefore fails until an authoritative historical source is recovered.
