# TabArena-Binary raw-acquisition package

This package holds the raw public files of the thirty binary-classification datasets of TabArena-v0.1 (Erickson, Purucker, Tschalzev, Holzmüller, Mutalik Desai, Salinas & Hutter, *TabArena: A Living Benchmark for Machine Learning on Tabular Data*, NeurIPS 2025 Datasets and Benchmarks Track; arXiv:2506.16791; OpenML suite 457), together with the per-dataset results the authors published for them.

It is the **raw-acquisition stage only**. It contains pinned, hashed, byte-for-byte copies of the source files, a machine-readable manifest, counts measured from those files, the published results table checked cell by cell across four renderings, and a standard-library-only script that re-checks all of it. It contains **no built analysis files**.

**This collection is held out for a pre-specified confirmatory run.** Nothing beyond counts was computed on the datasets: no model was trained, no accuracy or AUC was computed, no feature was correlated or cross-tabulated with a target, and nothing under `DATA_SETS/Holte-16/analysis/` was run. The only arithmetic on the published results is stated under "The published results" below. See "What is NOT done".

Retrieval date for everything: **2026-09-19**.

## How the thirty were identified

OpenML suite 457 (`tabarena-v0.1`) lists 51 tasks. Their task records give 38 Supervised Classification and 13 Supervised Regression tasks. Of the 38 classification targets, 30 declare exactly two nominal values; the other eight declare three to eight (anneal, hiva_agnostic, maternal_health_risk, MIC, SDSS17, splice, students_dropout_and_academic_success, website_phishing). Two independent sources give the same thirty: the repo's `curated_tabarena_dataset_metadata.csv` marks exactly these as `problem_type = binary`, and Table F.1 of the paper prints exactly these thirty with the AUC metric. Note that `hiva_agnostic` is a three-class task here (the curators kept "the original labels with three classes"), although older OpenML versions of it are binary.

## Result of the acquisition

**30 of 30 acquired. No failure, no substitution, nothing gated.** For each dataset the package holds the ARFF (primary, plain text), OpenML's parquet copy, and the OpenML description, feature and quality records.

| Check | Result |
|---|---|
| ARFF MD5 against the `md5_checksum` OpenML publishes | 30 of 30 equal |
| Measured rows, columns, missing cells, rows with missing, class sizes against the OpenML qualities | 30 of 30 equal |
| Measured rows and features against the repo's metadata CSV | 30 of 30 equal |
| ARFF (stdlib parser) against parquet (pyarrow): rows, column names and order, nulls per column, distinct values per categorical column, class counts | 30 of 30 equal |
| Every row of the 2026-09-18 scan table (OpenML id, n, columns, class sizes, the quoted best cell, the quoted Linear cell) looked up in these files | 30 of 30 rows confirmed |

Sizes run from 748 rows (blood-transfusion-service-center) to 150,000 (GiveMeSomeCredit), and from 5 to 1,777 columns (Bioresponse). Ten datasets have missing cells; twenty have none. All counts are in `measured-counts.csv` (one row per dataset) and `measured-column-counts.csv` (one row per column, 2,938 rows).

## The published results

`published_results.csv` has 1,530 rows: 30 datasets x 17 models x 3 regimes. Each row carries two renderings of the same published number.

- `published_auc_mean_pdf`, `published_auc_sd_pdf`: the cell as printed in **Table F.1** of arXiv:2506.16791v4 (PDF pages 58-66), empty where the table prints a dash.
- `artifact_auc_mean`, `artifact_auc_sd`: from the authors' **cached results artifact** (public S3 bucket, results tier), which stores one `metric_error = 1 - ROC AUC` per dataset, split and method variant. The only arithmetic done in this package is the collapse to the table's granularity: the mean and the sample standard deviation (ddof = 1) of `1 - metric_error` over the splits. No margin, difference between models, best-of or ranking was computed.

**Metric and protocol (as published).** ROC AUC for binary tasks ("Elo scores are computed using ROC AUC for binary classification, log-loss for multiclass classification, and RMSE for regression", p. 6). Outer evaluation: "for datasets with less than 2 500 samples, we use 10 times repeated 3-fold outer cross-validation; (II) for all other datasets, we use 3 repeats", class-wise stratified (p. 6). So a cell is a mean over 30 test folds for the eight sets under 2,500 rows and over 9 test folds for the other twenty-two; the artifact confirms these split counts. Each test fold is one third of the data. Inside each training fold, configurations are validated by 8-fold inner cross-validation, 200 random configurations per model, one hour per configuration (pp. 3-4, 10).

**Regimes.** `default` (default hyperparameters), `tuned` (best single configuration by inner validation), `tuned_ensemble` (post-hoc weighted ensemble of the configurations of that one model).

**Coverage.**

| Models | Regimes | Datasets |
|---|---|---|
| RF, ExtraTrees, XGBoost, LightGBM, CatBoost, EBM, FastAIMLP, TorchMLP, RealMLP, TabM, MNCA, **Linear, KNN** | all three | all 30 |
| TabDPT | default only ("do not specify hyperparameter optimization") | all 30 |
| TabICL | default only | 29 (not Bioresponse: limit 100,000 training samples and 500 features) |
| TabPFNv2 | all three | 20 (limit 10,000 training samples and 500 features; not run on Amazon_employee_access, APSFailure, bank-marketing, Bioresponse, credit_card_clients_default, customer_satisfaction_in_airline, Diabetes130US, GiveMeSomeCredit, HR_Analytics_Job_Change_of_Data_Scientists, kddcup09_appetency) |
| AutoGluon ("version 1.3, with the best_quality preset and 4 hours for training"; a system, not a model) | one entry, printed in the Tuned + Ens. column | all 30 |

That is 1,319 printed cells and 211 dashes.

**Spot-check outcome.** The check was run on every cell, not on a sample.

| Comparison | Cells | Disagreements |
|---|---|---|
| arXiv v4 PDF against the results artifact (mean and s.d., rounded to three decimals) | 1,319 printed cells | **0** |
| Dashes in the PDF against the artifact | 211 | 0: 180 are absent from the artifact, 31 are present but flagged `imputed` (see finding 3) |
| arXiv v4 PDF against arXiv v4 HTML (whole table, all 51 datasets) | 2,601 (1,530 AUC) | **0** |
| arXiv v4 PDF against the NeurIPS 2025 proceedings PDF (whole table) | 2,601 | **0** |

Thirty of the compared cells, one per dataset, are listed side by side in `build/spot_check_sample.csv`. The zero was reached only after finding 1 below.

### Findings the authors should see before any build

These are measurements and readings, reported without taking a decision.

1. **The Linear and KNN baselines were re-run for the camera-ready, and both versions are public.** The repo defines the published collection as suite `tabarena-2025-06-12` for every method except `LinearModel` and `KNeighbors`, which come from a re-run, suite `tabarena-2025-10-20` (`contexts/tabarena/methods.py`, `updated_methods_camera_ready`). With the first-run files, 129 of the 180 Linear and KNN cells differ from the printed table (all 90 KNN cells, 39 of 90 Linear cells); with the re-run files all 180 agree. Examples for Linear, Tuned + Ens.: Bioresponse printed 0.817, first run 0.793; churn 0.825 against 0.816; polish_companies_bankruptcy 0.896 against 0.891. The first-run values are kept in `published_results_superseded_linear_knn.csv` so that nobody picks them up by accident. Which arXiv version printed them was not checked. Since Linear is the natural "simple" end of any margin, cite v4 or the proceedings, not an earlier version, and do not load the 2025-06-12 Linear artifact.
2. **TabArena is a living benchmark.** The repo's default context now serves newer results (AutoGluon 1.4 to 1.6, re-run EBM, CatBoost and ExtraTrees, more foundation models). This package pins the frozen NeurIPS 2025 table. The live leaderboard will not match it.
3. **The artifact contains imputed rows.** Where TabPFNv2 or TabICL could not run, the artifact still has rows, filled with the default random forest's values and flagged `imputed = True`, `impute_method = RandomForest_c1_BAG_L1`. Averaging the artifact without that filter produces TabPFNv2 numbers for ten datasets that were never run. In `published_results.csv` those cells have an empty published value and the status `not_run_dash_in_pdf_imputed_in_artifact`.
4. **`diabetes` (OpenML 46921) is the Pima set already held as PIMA in `DATA_SETS/MKW08-30`.** The two files are identical as multisets of rows (768 of 768; `scripts/check_pima_overlap.py`). It is not new data for this programme. No other name overlap with Holte-16, MKW08-30 or Simsek-56 was found.
5. **Not all of it is modern.** By the repo's own `year` column, 10 of the 30 datasets date from 2020 or later; the oldest are diabetes (1988), credit-g (1994), coil2000 (2000), jm1 (2004) and churn (2005).
6. **Several OpenML versions are reductions of better-known originals.** polish_companies_bankruptcy is the year-5 file only (5,910 rows; UCI record 365 reports 10,503 instances). NATICUSdroid has 7,491 rows after the curators dropped duplicates (UCI record 722 reports 29,333). Diabetes130US keeps one encounter per patient (71,518 rows; UCI record 296 reports 101,766) with a binary target built from `readmitted`. heloc comes from a Kaggle upload, not from FICO, with the licence field "Public". bank-marketing lost `duration`, `month` and `day_of_week`. The curators' own comments are quoted verbatim per dataset in `SOURCES.md`.
7. **Missing values come in two kinds.** The ARFF token `?` (also where a nominal declares `?` as a value, as in Diabetes130US `race`) is missing in OpenML's records and null in the parquet; these are the counted missing cells. Separately, literal strings such as `nan`, `unknown`, `Not Available` are ordinary categories in the files: 7 columns of HR_Analytics_Job_Change_of_Data_Scientists, 6 of in_vehicle_coupon_recommendation (`car` is `nan` in 12,576 of 12,684 rows), 5 of Diabetes130US, 22 of kddcup09_appetency, 4 of bank-marketing (`unknown`). credit-g is listed only because `none` is one of its legitimate categories. The zero codes that stand for missing in the Pima data are not counted here.
8. **Heavy missingness in two sets.** kddcup09_appetency has 6,727,959 missing cells in 171 columns and no complete row; APSFailure has 1,078,695 in 169 columns and 756 complete rows of 76,000.
9. **Class ratios are natural and often extreme** (minority : majority): APSFailure 1,375 : 74,625; kddcup09_appetency 890 : 49,110; taiwanese_bankruptcy_prediction 220 : 6,599; Amazon_employee_access 1,897 : 30,872; GiveMeSomeCredit 10,026 : 139,974. Only hazelnut-spread-contaminant-detection is balanced (1,200 : 1,200). In Amazon_employee_access the minority class is `No`.
10. **Size flags.** Above 100,000 rows: customer_satisfaction_in_airline (129,880), GiveMeSomeCredit (150,000). Above 200 columns: Bioresponse (1,777; 835 numeric columns take at most two values), kddcup09_appetency (213).
11. **High-cardinality categoricals (more than 50 observed values):** Amazon_employee_access, all nine features (67 to 7,518 values; the whole dataset is categorical); kddcup09_appetency, 14 columns (up to 15,416); Diabetes130US `diag_1`, `diag_2`, `diag_3`, `medical_specialty`; HR_Analytics `city` (123); churn `state` (51); Marketing_Campaign `Dt_Customer` (663 dates stored as STRING).
12. **STRING-typed columns** that a reader must interpret: bank-marketing `poutcome`; coil2000 `avgAge`, `contributionPrivateThirdPartyInsurance`; HR_Analytics `experience`; in_vehicle `coupon`; Marketing_Campaign `Dt_Customer`; seismic-bumps `ghazard`. **Constant columns:** APSFailure `cd_000`; Diabetes130US `examide`, `citoglipton`, `glimepiride-pioglitazone`; kddcup09 `Var118`. In the parquet copies the targets of online_shoppers_intention and jm1 (and `Weekend`) are booleans, in the ARFF they are nominals `{False, True}`.
13. **Identifier columns.** No nominal, string or integer-valued feature column has all values distinct (25 continuous REAL columns do, as ratios will); the curators dropped row identifiers in eight datasets. What remains by name: Amazon `MGR_ID` (4,243 values) and the three decoded `*_id` columns of Diabetes130US.
14. **Leakage candidates, flagged from names and documentation only. Nothing was measured, no feature was related to a target.** Diabetes130US `discharge_disposition_id` (categories include `Expired` and hospice); online_shoppers_intention `PageValues`; customer_satisfaction_in_airline, the 14 service ratings from the same survey as the target; heloc `ExternalRiskEstimate` (an external risk score); seismic-bumps `seismic`, `seismoacoustic`, `ghazard` (other methods' hazard assessments); bank-marketing `campaign`; E-CommereShippingData `Discount_offered` (unverified recollection). Column meanings not quoted from the curators come from general knowledge of the source documentation, which was not re-fetched; check them before relying on them.
15. **Published contamination note.** The paper states (p. 56) that TabDPT was pretrained on seven TabArena datasets; five of them are binary sets held here: kddcup09_appetency, Amazon_employee_access, APSFailure, Diabetes130US, heloc.
16. **Licences as displayed by OpenML:** CC BY 4.0 (14), Public Domain (5), "Public" (5), CC0 (4), MIT (1), CC BY-SA (1). "Public" is not a licence. Eleven sets originate from Kaggle according to the repo metadata.

## Package layout

```text
TabArena-Binary/
  README.md
  SOURCES.md                      generated; per-dataset provenance, curators' comments, decisions a build would need
  manifest.json                   30 dataset records + shared files; every file with URL, date, bytes, SHA-256
  measured-counts.csv             one row per dataset: counts, OpenML and repo figures beside them, flags
  measured-column-counts.csv      one row per column: declared type, missing, distinct values, pseudo-missing literals
  published_results.csv           1,530 cells: Table F.1 as printed, the artifact beside it, cross-check status, source
  published_results_superseded_linear_knn.csv   first-run Linear/KNN values, NOT the published table (finding 1)
  published_results_crosscheck.json
  verification-report.json        written by scripts/verify.py
  raw/<name>/                     <name>.arff, dataset_<id>.pq, openml_{description,features,qualities}_<id>.json
  suite/                          study_457.json, tasks/ (51 task records), nonbinary_classification/ (8 sets, evidence)
  results_artifact/<suite>/methods/<method>/results/   19 parquet files from the public TabArena bucket
  references/                     arXiv v4 PDF + HTML, NeurIPS paper + supplement, parsed Table F.1 (3 renderings),
                                  tabarena_repo/ (7 source files at a pinned commit + LICENSE), uci_metadata/
  build/                          download plan and log, task index, ARFF-vs-parquet report, spot-check sample, PIMA check
  scripts/                        verify.py (stdlib) and the build scripts
```

## Conventions

- **Raw files are never edited.** Downloads are stored as received.
- **Every file is pinned** by byte size and SHA-256 in `manifest.json`, with its URL and retrieval date. Files produced by the scripts from a pinned file are marked `derived`.
- **Names** are the TabArena and OpenML dataset names, unchanged, including the misspelt `E-CommereShippingData`. The paper abbreviates one name (`HR_Analytics_Job_Change`).
- **Row counting.** A row is a non-empty, non-comment line after `@DATA` with as many fields as declared attributes (no line failed that test). Columns include the target. Missing is an unquoted `?`.
- **Distinct values** are exact for nominal and STRING columns; for numeric columns exact up to 1,000, otherwise `>1000`.
- **Nothing is transcribed as measured.** Counts in the CSVs, the manifest and `SOURCES.md` are written by code from the files. Published numbers are labelled published, with the PDF page and the artifact URL in the `source` column.
- **Requests.** `curl` only, one at a time, at most two retries, no credentials, cookies or API keys. No request carried a name, an e-mail address or any other personal identifier; Unpaywall and Crossref were not called.

## Verification

Python 3 (run here with 3.13); no third-party packages; no network access.

```text
python scripts/verify.py
```

The script re-hashes all 264 pinned files (SHA-256, and MD5 for the ARFFs), confirms the pinned folders hold no unlisted file, re-counts every ARFF (rows, columns, declared types, missing and distinct values per column, class counts) against both CSVs and the manifest, confirms that `published_results.csv` has 30 x 17 x 3 rows whose published columns equal the PDF parse, writes `verification-report.json`, and exits nonzero on any mismatch. Last run: **PASS**. The build scripts (`parse_pdf_table_f1.py` needs pypdf; `build_published_results.py` and `crosscheck_arff_vs_parquet.py` need pandas and pyarrow) are documented at the top of each file; `crosscheck_pdf_vs_html.py`, `measure_counts.py`, `build_manifest.py` and `build_sources_md.py` are standard library only.

## What is NOT done

Deliberately left for the authors to rule on:

- No `data/*.csv` analysis files, no harness run, no model, no score, no correlation. The pre-specification has to be approved first.
- No choice of positive class, no binarization of cues, no cue selection, no grouping of categories, no handling of missing or pseudo-missing values, no removal of constant, redundant or suspect columns, no subsampling.
- No decision on scoring. The published metric is ROC AUC on predicted probabilities. A tree that returns a hard verdict has an AUC equal to its balanced accuracy; a tree that returns exit-level frequencies does not. Which of the two the harness reports, and against which published column (Linear, the best single model, AutoGluon, default or tuned), belongs in the pre-specification.
- No decision on splits. Reusing TabArena's folds would need the OpenML split files (`Task_<id>_splits.arff`; public, HTTP 200 without login, URL per dataset in the manifest). They were not downloaded.
- No margins, no ranking of datasets, no best-of over models. The scan of 2026-09-18 computed margins from the HTML; its quoted cells are confirmed here, its arithmetic was not repeated.
- Not acquired: the raw and processed prediction tiers of the TabArena artifact (about 100 GB and 10 GB per method according to the repo README), and the upstream originals on Kaggle (login required: not acquired, gated) and UCI.

Per-dataset lists of the decisions a build would need are in `SOURCES.md`.

## Citation and terms

Cite Erickson et al. (2025) for the benchmark and the published results, and each dataset by the citation OpenML displays for it (in `manifest.json` and `SOURCES.md`). The TabArena repository is Apache-2.0 (`references/tabarena_repo/LICENSE`). Dataset licences are those displayed by OpenML and listed in `measured-counts.csv`; five records say only "Public". This is a research acquisition copy and does not supersede upstream terms.
