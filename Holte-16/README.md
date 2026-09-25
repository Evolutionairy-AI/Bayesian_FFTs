# Holte-16 acquisition and reconstruction package

This package reconstructs the 16 classification datasets used in Robert C. Holte's 1993 paper, *Very Simple Classification Rules Perform Well on Most Commonly Used Datasets* (Machine Learning 11, 63-91; DOI `10.1023/A:1022631118932`).

It contains pinned copies of the current authoritative UCI bundles, an author-hosted copy of the paper, a machine-readable manifest, exact transformation rules from Appendix B, standardized CSV outputs, and a standard-library-only Python acquisition/build/validation script.

## Important fidelity result

- **15 of 16 datasets are record-level reproducible** from the raw files currently distributed by UCI and match Holte's Table 2 dimensions, class count, majority-class baseline, and missing-value flag.
- **LY (Lymphography) has unresolved historical version drift.** Holte reports 141 rows and a 56.7% majority-class baseline. The current authoritative UCI `lymphography.data` has 148 rows and a 54.7% baseline (class counts 2/81/61/4). No record-level authoritative snapshot of the 141-row April-1990 version was located. `data/LY.csv` therefore preserves the current 148-row UCI file and is marked `version_drift_unresolved` throughout this package. No arbitrary rows were deleted.

This distinction matters: the package is a complete acquisition and reconstruction specification, but it does not falsely claim that the modern LY file is the exact file used by Holte.

## Quick start

Python 3.10 or newer is sufficient; there are no third-party dependencies.

```text
python scripts/holte16.py all
```

The command:

1. verifies or downloads the pinned UCI bundles and Holte PDF;
2. extracts and hashes the required raw files;
3. rebuilds all 16 standardized CSV files in `data/`;
4. writes `validation-report.json`; and
5. exits nonzero if any dataset other than the documented LY historical drift fails.

To require all historical expectations, including LY=141, use:

```text
python scripts/holte16.py validate --strict-historical
```

That command intentionally fails with the current authoritative LY source.

Available commands:

```text
python scripts/holte16.py acquire
python scripts/holte16.py build
python scripts/holte16.py validate
python scripts/holte16.py all
```

## Package layout

```text
Holte-16/
  README.md
  SOURCES.md
  RECONSTRUCTION_SPEC.md
  HOLTE_APPENDIX_B_EVIDENCE.md
  manifest.json
  expected-counts.csv
  validation-report.json
  data/                         standardized CSV outputs, class last
  raw/uci-bundles/              pinned authoritative UCI ZIP files
  raw/extracted/                required raw files extracted by the script
  raw/metadata/                 UCI API metadata snapshots
  references/holte-1993.pdf     author-hosted paper copy
  scripts/holte16.py            acquire/build/validate entry point
```

## Output conventions

- Each CSV has a header and a final column named `class`.
- Source row order is retained. Where Appendix B combines files, the listed training file precedes the listed test file.
- Original values are retained as strings.
- The literal `?` is retained as the missing-value token. Missing rows are not removed or imputed.
- Moving a class column to the end and adding a header are packaging normalizations, not changes to the observations.
- Feature deletions and class transformations are only those specified by Holte's Appendix B.

## What to cite

For the benchmark definition, cite Holte (1993). For each dataset used in a publication, also cite its UCI DOI from `SOURCES.md` or `manifest.json` and comply with the current UCI record's license and access terms.

## Reproducibility policy

The acquisition script pins SHA-256 hashes for each UCI bundle, required raw file, and the author-hosted paper. If an upstream file changes, acquisition stops rather than silently accepting a different version. Update the manifest only after reviewing and documenting the upstream change.
