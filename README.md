# Bayesian fast-and-frugal trees: code and results

Code, pre-specification and results for the paper *When transparency has no price: Bayesian fast-and-frugal trees*, by Alex Bogdan and Konstantinos V. Katsikopoulos. Citation details will be added on publication.

The repository holds every script that produced a number in the paper and the output files of those runs. It does not hold the raw data: `fetch_data.py` downloads each public file from its source and checks it against the SHA-256 recorded when it was first retrieved.

## Contents

| Folder | What it holds |
|---|---|
| `Holte-16/` | The sixteen datasets of Holte (1993): acquisition and build script, the analysis harness (`analysis/depth_one_harness.py`, `analysis/indicator_cv_harness.py`) that every later analysis imports, and its outputs |
| `MKW08-30/` | The thirty datasets of Martignon, Katsikopoulos and Woike (2008): acquisition, verification and build scripts; the confirmatory run and the robustness run on Woike's files, with their outputs |
| `TabArena-Binary/` | The 29 binary tasks of TabArena (version 0.1, OpenML suite 457): acquisition and build scripts, the published results used for comparison, and the run under Addendum B with its outputs |
| `Posthoc-Development/` | Analyses defined after the planned ones: the price identity, the screening rule on the development data, the base-rate checks, concordance and cumulative dominance, and the check of the certified-tree definition on every profile |
| `figures/` | The script and the plotted values of Figure 2 |
| `theory/` | Exhaustive numerical verification of Result 1 on synthetic attribute sets, with its output |

The README of each collection describes its acquisition as it stood on the retrieval date.

## Reproducing the analyses

Python 3.13.5 was used. The harness and every post hoc script need the standard library only; the TabArena benchmarks need the packages in `requirements.txt` (the driver asserts scikit-learn 1.7.2), and the figure needs matplotlib.

```text
pip install -r requirements.txt
python fetch_data.py
```

`fetch_data.py` downloads the raw files (about 210 MB, most of it TabArena), stops if any file differs from its recorded SHA-256, builds the analysis files `data/<name>.csv` of each collection, and confirms that every one of them equals, byte for byte, the file that the paper's analyses read (`data_checksums.json`).

Then run, in this order (each script writes its outputs next to itself, so `git diff` shows any difference from the committed results):

```text
python Holte-16/analysis/depth_one_harness.py
python Holte-16/analysis/indicator_cv_harness.py
python MKW08-30/analysis/mkw08_confirmatory.py --selftest
python MKW08-30/analysis/mkw08_confirmatory.py            # needs the frozen pre-specification (see below)
python MKW08-30/analysis/identity_check.py data
python TabArena-Binary/analysis/tabarena_confirmatory.py --smoke
python TabArena-Binary/analysis/tabarena_confirmatory.py  # needs the frozen documents; about 45 minutes
python Posthoc-Development/price_identity.py
python Posthoc-Development/prior_dominance_score.py
python Posthoc-Development/baserate_checks_spent_data.py
python Posthoc-Development/concordance_cumulative_dominance.py
python Posthoc-Development/certified_definition_check.py
python figures/make_fig2_price_of_transparency.py
python figures/fig2_questions_asked.py
python theory/verify_theorem_2_7_5.py
```

The scripts whose names end in `_woike` repeat an analysis on the files that Jan K. Woike supplied; they are included for inspection but cannot be run from this repository (see below).

## Where each result comes from

| In the paper | Source |
|---|---|
| Verification of Result 1 on synthetic attribute sets (Methods) | `theory/verify_theorem_2_7_5.py`, Part A; the sharpness example, Part D. Parts B, C and E to G concern a companion analysis and are not used |
| The identity on the objects of the forty-six datasets | `Holte-16/analysis/summary.json` (20,407 objects) and `MKW08-30/analysis/identity_check.py` (15,120) |
| The identity on every profile of the certified attributes; the definition of the certified tree | `Posthoc-Development/certified_definition_check.py` |
| The identity on the TabArena cases | `TabArena-Binary/analysis/tabarena_summary.json` |
| Exploratory correlations on the sixteen | `Holte-16/analysis/indicator_summary.json` |
| Confirmatory tests on the thirty (Extended Data Table 1, left column) | `MKW08-30/analysis/confirmatory_summary.json` |
| Robustness run on Woike's files (Extended Data Table 1, right column) | `MKW08-30/analysis/robustness_woike_summary.json` |
| Agreement, conflicts and the price; Figure 2; Extended Data Table 3 | `Posthoc-Development/price_identity_results.csv`, `figures/Fig2_price_data_2026-09-23.csv`, `figures/Fig2_questions_asked_2026-09-24.csv` |
| Concordance and cumulative dominance | `Posthoc-Development/concordance_cumulative_dominance_log.txt` |
| The screening rule on the development data | `Posthoc-Development/prior_dominance_log.txt` |
| The screening rule on TabArena, H3, and Extended Data Table 4 | `TabArena-Binary/analysis/tabarena_summary.json`, `TabArena-Binary/analysis/tabarena_results.csv` |
| Attribute lists (Supplementary Information) | `MKW08-30/data/APPENDIX_A.md`, `MKW08-30/analysis/ADDENDUM_B_APPENDIX_B1.md`; for the sixteen, the build rules in `Holte-16/scripts/holte16.py` |

## Pre-specification

A pre-specification fixed the confirmatory analysis of the thirty before any quantity was computed on them (frozen on 19 September 2026); Addendum A fixed the single re-run on Woike's files (21 September 2026), and Addendum B fixed the test on TabArena (24 September 2026). These three documents are not part of this repository for now. The drivers read them from `MKW08-30/analysis/` (`PRESPECIFICATION_FROZEN.md`, `ADDENDUM_A_FROZEN.md`, `ADDENDUM_B_FROZEN.md`) and refuse to run without them, so the confirmatory drivers run here only in their self-test modes (`--selftest` and `--smoke`).

Each driver recorded the SHA-256 of the documents it read in the summary it wrote (`prespecification_sha256` in `MKW08-30/analysis/confirmatory_summary.json`; `addendum_a_sha256` in `robustness_woike_summary.json`; `addendum_b_sha256` in `TabArena-Binary/analysis/tabarena_summary.json`), so a copy of any of them can be checked against the run that used it:

```text
python -c "import hashlib; print(hashlib.sha256(open('MKW08-30/analysis/PRESPECIFICATION_FROZEN.md','rb').read()).hexdigest())"
```

The history of this repository begins after the runs, so it does not time-stamp the freezes; the dates are those stated in the documents and in the paper.

## What is not here, and why

- **The frozen pre-specification and addenda.** Not included for now (see Pre-specification).
- **Raw data.** The datasets remain under their sources' terms (UCI Machine Learning Repository, the companion site of Simonoff's *Analyzing Categorical Data*, StatLib, hbiostat.org, OpenML); `fetch_data.py` downloads them, and each collection's `SOURCES.md` records where every file came from.
- **Woike's files.** The robustness analysis used the thirty data files of Jan K. Woike's dissertation, which he supplied privately; they are not redistributed. The outputs of that analysis are included; they, and the comparison of his files with ours in Extended Data Table 2, cannot be recomputed from this repository.
- **Papers and dissertations.** PDF copies mentioned in the collection READMEs (under `references/`) are not included. As part of its acquisition step, `Holte-16/scripts/holte16.py` downloads the author-hosted copy of Holte (1993) and checks its SHA-256.
- **Working notes.** The collection READMEs mention internal notes, for example on how the thirty were identified; the identification is described in the paper's Methods.

## Licenses

Code: Apache License 2.0 (`LICENSE`). Results files (the CSV, JSON and text outputs of the analyses): CC BY 4.0 (`LICENSE-results.md`). The datasets are not covered by either license.
