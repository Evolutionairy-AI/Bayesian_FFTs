# Bayesian fast-and-frugal trees: code and results

Code and results for the paper *The price or bonus of transparency: Bayesian fast-and-frugal trees*, by Alex Bogdan and Konstantinos V. Katsikopoulos. Citation details will be added on publication.

The repository holds every script that produced a number in the paper and the output files of those runs. It does not hold the raw data: `fetch_data.py` downloads each public file from its source and checks it against the SHA-256 recorded when it was first retrieved.

## Contents

| Folder | What it holds |
|---|---|
| `Holte-16/` | The sixteen datasets of Holte (1993): acquisition and build script, the analysis harness (`analysis/depth_one_harness.py`, `analysis/indicator_cv_harness.py`) that every later analysis imports, and its outputs |
| `MKW08-30/` | The thirty datasets of Martignon, Katsikopoulos and Woike (2008): acquisition, verification and build scripts; the confirmatory run and the robustness run on Woike's files, with their outputs |
| `TabArena-Binary/` | The 29 binary tasks of TabArena (version 0.1, OpenML suite 457): acquisition and build scripts, the published results used for comparison, and the run under Addendum B with its outputs |
| `Posthoc-Development/` | Analyses defined after the planned ones: the price identity, the conflict rate and agreement given a conflict counted on the test folds (the basis of Table 1, Figure 2 and Extended Data Tables 3 and 4), the large-prior case, the screening rule on the development data, the base-rate checks, concordance and cumulative dominance, and the check of the certified-tree definition on every profile |
| `figures/` | The scripts and the plotted values of Figure 2, and the questions each of its trees asks |
| `tables/` | Table 1, Extended Data Tables 2 to 4 and the counts and medians quoted in the text, tabulated from the saved results |
| `theory/` | Exhaustive numerical verification of Result 1 on synthetic attribute sets, and a brute-force check of the necessary and sufficient condition, with their outputs |

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
python Posthoc-Development/heldout_conflict_share.py       # about 5 minutes
python Posthoc-Development/large_prior_case.py
python figures/make_fig2_price_of_transparency.py           # superseded (thirty trees); kept for the record
python figures/fig2_questions_asked.py
python figures/make_fig2_price_of_transparency_43.py
python tables/make_paper_tables.py
python theory/verify_theorem_2_7_5.py
python theory/verify_iff_bruteforce.py
```

The scripts whose names end in `_woike` repeat an analysis on the files that Jan K. Woike supplied; they are included for inspection but cannot be run from this repository (see below). `heldout_conflict_share.py` and `large_prior_case.py` also cover his files: without them they skip `MKW08-30-Woike` (the results file of `heldout_conflict_share.py` then holds 75 rows instead of 105, and `git diff` shows the other 30 as removed).

The scripts added on 24 November 2026 (`heldout_conflict_share.py`, `large_prior_case.py`) read the analysis files from the `data/` folders of this repository; to read them from another folder with the same layout, set the environment variable `BFFT_DATA_ROOT` to that folder.

## Where each result comes from

| In the paper | Source |
|---|---|
| Summary paragraph: certified depth of two or three in 32 of 75 datasets; median agreement 84%; 43 trees with both verdicts, median price 2.0 points, negative for 11 | `tables/paper_numbers_log.txt` (written by `tables/make_paper_tables.py`) |
| Table 1 | `tables/table1_rows.tex`, from `Posthoc-Development/heldout_conflict_share_results.csv` (every row on the test folds) and the certified depths in `Holte-16/analysis/indicator_results.csv`, `MKW08-30/analysis/confirmatory_results.csv` and `TabArena-Binary/analysis/tabarena_results.csv` |
| Section 3: decisiveness (348 of 3,532 attributes outweigh the prior), the medians of $A$, $c$ and $s$, the 43 trees (queries, gains over the base rate, prices), Iris, the TabArena tasks in which the Bayesian classifier falls below the base rate, the one-class trees | `tables/paper_numbers_log.txt` |
| Section 3 and Extended Data Table 1: the datasets in which the prior outweighs all attributes combined (the large-prior case) | `Posthoc-Development/large_prior_case_log.txt` |
| Figure 2 (43 trees) | `figures/make_fig2_price_of_transparency_43.py` and its plotted values, `figures/Fig2_price_data_43_2026-11-13.csv`; the published figure is a redrawing of the draft this script makes |
| Remark (iii) and Methods, "A necessary and sufficient condition", with its two numerical examples | `theory/verify_iff_bruteforce.py`, `theory/verify_iff_bruteforce_log.txt` |
| Methods, verification of the identity on synthetic attribute sets | `theory/verify_theorem_2_7_5.py`, Part A. The other parts concern a companion analysis and are not used; Part D (the former "sharpness" example) is no longer cited |
| Methods, the identity on the objects of the forty-six datasets and of Woike's files | `Holte-16/analysis/summary.json` (20,407 objects) and `MKW08-30/analysis/identity_check.py`, which prints the count (15,120 cases with `data`, 14,939 with Woike's files) |
| Methods, the identity on every profile of the certified attributes; the definition of the certified tree; the questions the trees ask | `Posthoc-Development/certified_definition_check.py`; `figures/Fig2_questions_asked_2026-09-24.csv` (the thirty trees of the first two collections) and the column `questions_asked` of `TabArena-Binary/analysis/tabarena_results.csv` |
| Methods, the identity on the TabArena cases | `TabArena-Binary/analysis/tabarena_summary.json`, `TabArena-Binary/analysis/tabarena_results.csv` |
| Methods, empirical estimation of the price: $A$, $c$, $s$, $q$ and the price on the test folds | `Posthoc-Development/heldout_conflict_share_results.csv` and `_log.txt` |
| Methods, exploratory correlations on the sixteen | `Holte-16/analysis/indicator_summary.json` |
| Methods and Extended Data Table 1, pre-specified tests and counts (left column: the thirty; right column: Woike's files) | `MKW08-30/analysis/confirmatory_summary.json`, `MKW08-30/analysis/robustness_woike_summary.json` |
| Extended Data Table 1, rows computed afterward | `tables/paper_numbers_log.txt` (medians in and out of sample, gains of the benchmarks, the one-class trees, the correlation within the thirteen); `Posthoc-Development/price_identity_run_log.txt` and `price_identity_woike_run_log.txt` (identity exact in whole cases); `baserate_checks_log.txt` and `baserate_checks_woike_log.txt` (published tree below the base rate); `prior_dominance_log.txt` and `prior_dominance_woike_log.txt` (graded condition, rival predictor); `large_prior_case_log.txt` |
| Extended Data Table 2 | `tables/extended_data_table2.csv`, from `MKW08-30/analysis/confirmatory_results.csv` and `robustness_woike_results.csv` |
| Extended Data Table 3 | `tables/extended_data_table3.csv` |
| Methods, the screening rule on the development data | `Posthoc-Development/prior_dominance_log.txt` |
| Methods, the screening rule on TabArena and H3; Extended Data Table 4 | `TabArena-Binary/analysis/tabarena_summary.json`, `TabArena-Binary/analysis/tabarena_results.csv`; `tables/extended_data_table4.csv` |
| Attribute lists (Supplementary Information) | `MKW08-30/data/APPENDIX_A.md`, `MKW08-30/analysis/ADDENDUM_B_APPENDIX_B1.md`; for the sixteen, the build rules in `Holte-16/scripts/holte16.py` |

Superseded, kept for the record:

| File | Superseded by |
|---|---|
| `figures/make_fig2_price_of_transparency.py`, `figures/Fig2_price_data_2026-09-23.csv` (Figure 2 of 25 September 2026: thirty trees, in-sample conflict counts) | `figures/make_fig2_price_of_transparency_43.py`, `figures/Fig2_price_data_43_2026-11-13.csv` |
| The out-of-sample columns of `Posthoc-Development/price_identity_results.csv` and `price_identity_woike_results.csv` as a source of Figure 2 and Extended Data Table 3 | `Posthoc-Development/heldout_conflict_share_results.csv`, which reproduces them and adds $c$ and $s$ on the test folds |
| `Posthoc-Development/concordance_cumulative_dominance.*` | Not cited in the final main text or Methods (the concordance paragraph moved to the Supplementary Information) |

## Pre-specification

A pre-specification fixed the confirmatory analysis of the thirty before any quantity was computed on them (frozen on 19 September 2026); Addendum A fixed the single re-run on Woike's files (21 September 2026), and Addendum B fixed the test on TabArena (24 September 2026). These three documents are not part of this repository; they are available from the corresponding author on request. The drivers read them from `MKW08-30/analysis/` (`PRESPECIFICATION_FROZEN.md`, `ADDENDUM_A_FROZEN.md`, `ADDENDUM_B_FROZEN.md`) and refuse to run without them, so the confirmatory drivers run here only in their self-test modes (`--selftest` and `--smoke`).

Each driver recorded the SHA-256 of the documents it read in the summary it wrote (`prespecification_sha256` in `MKW08-30/analysis/confirmatory_summary.json`; `addendum_a_sha256` in `robustness_woike_summary.json`; `addendum_b_sha256` in `TabArena-Binary/analysis/tabarena_summary.json`), so a copy of any of them can be checked against the run that used it:

```text
python -c "import hashlib; print(hashlib.sha256(open('MKW08-30/analysis/PRESPECIFICATION_FROZEN.md','rb').read()).hexdigest())"
```

The history of this repository begins after the runs, so it does not time-stamp the freezes; the dates are those stated in the documents and in the paper.

## What is not here, and why

- **The frozen pre-specification and addenda.** Available from the corresponding author on request (see Pre-specification).
- **Raw data.** The datasets remain under their sources' terms (UCI Machine Learning Repository, the companion site of Simonoff's *Analyzing Categorical Data*, StatLib, hbiostat.org, OpenML); `fetch_data.py` downloads them, and each collection's `SOURCES.md` records where every file came from.
- **Woike's files.** The robustness analysis used the thirty data files of Jan K. Woike's dissertation, which he supplied privately; they are not redistributed. The outputs of that analysis are included, and `tables/make_paper_tables.py` tabulates Extended Data Table 2 from them; the outputs themselves, and the cell-by-cell comparison of his files with ours, cannot be recomputed from this repository.
- **Papers and dissertations.** PDF copies mentioned in the collection READMEs (under `references/`) are not included. As part of its acquisition step, `Holte-16/scripts/holte16.py` downloads the author-hosted copy of Holte (1993) and checks its SHA-256.
- **Working notes.** The collection READMEs mention internal notes, for example on how the thirty were identified; the identification is described in the paper's Methods.

## Licenses

Code: Apache License 2.0 (`LICENSE`). Results files (the CSV, JSON and text outputs of the analyses): CC BY 4.0 (`LICENSE-results.md`). The datasets are not covered by either license.
