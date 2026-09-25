# MKW08-30 raw-acquisition package

This package holds the raw public sources of the thirty datasets used in Martignon, Katsikopoulos & Woike (2008), *Categorization with limited resources: A family of simple heuristics*, Journal of Mathematical Psychology 52, 352-361 (MKW08).

It is the **raw-acquisition stage only**. It contains pinned, hashed, byte-for-byte copies of the source files, a machine-readable manifest, a comparison of every raw file with the counts Woike reports, and a standard-library-only script that re-checks all of it. It contains **no built analysis files**: nothing has been binarized, filtered, selected or recoded. See "What is NOT done" below.

**Added 2026-09-19, after Alex's ruling (our own protocol, Woike's criterion definitions, all attributes):** `scripts/mkw08_build.py` now writes the analysis files `data/<CODE>.csv` by selecting rows and columns only, with every n and class split asserted, and generates `data/APPENDIX_A.md`. `analysis/mkw08_confirmatory.py` is the run driver; it refuses to start until `analysis/PRESPECIFICATION_FROZEN.md` exists. The sections below describe the raw-acquisition stage as it stood on 2026-09-18 and are left unchanged.

Retrieval date for everything in `raw/`: **2026-09-18** (six UCI bundles were copied from `Holte-16`, retrieved 2026-08-25 and re-confirmed identical upstream on 2026-09-18).

## How the thirty were identified

MKW08 names none of its datasets. The list is in the third author's dissertation: Jan K. Woike (2008), *Die paradoxe Rationalität einfacher Heuristiken*, Ruhr-Universität Bochum, **Tabelle 6.9** (printed p. 212) with one descriptive paragraph per dataset on pp. 211-214. Four independent fingerprints tie that table to MKW08 (declared link to the manuscript, the n and cue ranges 50-4052 and 4-69, the mean accuracies to the percentage point, and the two datasets that drop out at 15% training). The argument and all quotations are in `../DATASET_HUNT_MKW08_Lichtenberg_2026-09-18.md`, section 1A. Copies of the dissertation, a text extract of pp. 211-214, and Woike, Hoffrage & Martignon (2017, *Decision* 4(4); Table 1 describes the eleven medical sets in English) are in `references/`.

Composition by Woike's own source tag: 17 UCI, 10 from Simonoff's *Analyzing Categorical Data* (ACD) companion site, 3 other (StatLib twice, UCLA Statistics once).

## Result of the acquisition

**30 of 30 acquired.** No source failed and no dataset was substituted. Two sources are no longer where Woike found them: Pima Indians Diabetes has left UCI (taken from OpenML 37, MD5 confirmed against OpenML's record), and the UCLA cardiac page returns 404 (taken from hbiostat, plus the Internet Archive capture of the original file dated 2007-07-01).

Raw row count against Woike's n (Tabelle 6.9):

| Status | Count | Datasets |
|---|---|---|
| `exact` | 18 | BANK, SOLV, CRED, ZOO, IRIS, STRK, WINE, CYY, GLAS, SPCT, HUNG, ALCO, IONO, CARD, FOOT, AUTH, YEAS, SCOT |
| `explained` | 10 | ECHO, POST, BWAY, HEPA, CLEV, TOUR, EDUC, BCW, PIMA, HOF |
| `unexplained` | 2 | HORS (raw 368, Woike 218, split 128/90), VOTE (raw 435, Woike 402, split 248/154) |

For all 28 `exact` or `explained` sets, Woike's class split n1/n0 is also reproduced exactly. `explained` means a stated, measured reduction yields both his n and his split: in nine cases the deletion of rows with missing values on a natural predictor set (together with the exclusion of the two-row intensive-care class for POST and of primary terminal leavers for EDUC), and for PIMA a digit transposition in the dissertation (786 printed for 768). For the two `unexplained` sets, what was tried is recorded in `manifest.json` and `SOURCES.md`; nothing was forced.

The four Simonoff file mappings that had only been inferred from file names are all **confirmed**: Solvency = `japansolvent.csv`, Strikes = `wildcat.csv`, Tourism = `braziltourism.csv`, Baseball CYY = `cyyoung8092.csv` + `cyyoung9302.csv` pooled. Details in `SOURCES.md`.

### Findings the authors should see before any build

These are measurements on the raw files, reported without taking a decision.

1. **FOOT.** The dissertation says the criterion is whether the *home team* wins. The raw file gives home team wins 391 / does not win 281. Woike's 451/221 is reproduced exactly by whether the *favorite* wins.
2. **CARD.** Woike's n1 = 469 equals the count of raw code 1 in the original UCLA file, and the UCLA codebook defines that code as *no* cardiac event (0 = yes). The 2017 paper labels the same .841 base rate "Heart disease". The hbiostat copy has the event columns recoded to 1 = yes.
3. **ECHO.** Woike's 62 rows and 18/44 split match the shipped column `alive-at-1` on complete cases. On those 62 rows that column contradicts its own definition in `echocardiogram.names`: 42 of the 44 rows coded 0 survived 12 months or more, and 17 of the 18 rows coded 1 are patients followed for less than a year.
4. **GLAS.** "Window glass" in Woike's split is types 1+2 (building windows, 146). Counting vehicle windows (type 3) as well gives 163/51.
5. **POST.** Woike's 86 requires dropping the intensive-care class (2 rows) rather than merging it, plus the rows with a missing COMFORT value.
6. **HUNG.** Tabelle 6.9 uses all 294 rows although 293 contain a `?` somewhere. The 2017 paper prints 262 objects for the same set; complete cases on the first ten attributes give 261.
7. **EDUC.** `irish.ed` carries an ownership statement restricting use to examples for research on statistical methods. Read it before redistributing.

## Package layout

```text
MKW08-30/
  README.md
  SOURCES.md                 per-dataset provenance, comparison notes, decisions a build would need
  manifest.json              30 dataset records + 1 shared archive; every file with URL, date, bytes, SHA-256
  expected-counts.csv        Tabelle 6.9 transcribed, beside the measured raw counts and statuses
  verification-report.json   written by the script
  raw/<CODE>/                original files, byte-for-byte
  raw/<CODE>/extracted/      all members of a UCI ZIP, extracted unchanged (UCI sets only)
  raw/_ACD_bundle/           Simonoff's whole-site data.zip, kept as a cross-check for the per-file CSVs
  references/                Woike (2008) dissertation, text extract of pp. 211-214, Woike et al. (2017)
  scripts/mkw08_verify.py    verifier, standard library only
```

Codes, in Tabelle 6.9 order: BANK, SOLV, ECHO, POST, BWAY, CRED, ZOO, IRIS, HEPA, STRK, WINE, CYY, GLAS, HORS, SPCT, HUNG, CLEV, ALCO, IONO, TOUR, VOTE, EDUC, CARD, FOOT, BCW, PIMA, AUTH, HOF, YEAS, SCOT. The mapping to Woike's labels is in `expected-counts.csv`.

## Conventions

- **Raw files are never edited.** Downloads are stored as received. ZIP members are extracted with Python's `zipfile` (no newline or encoding conversion) and the script confirms each extracted file equals its archive member.
- **Every file is pinned** by byte size and SHA-256 in `manifest.json`, with its URL, retrieval date and origin (`downloaded`, `copied_from_Holte-16`, or `extracted`).
- **Reuse of Holte-16.** The UCI bundles 42, 45, 46, 47, 53 and 105 (seven of the thirty, since 45 serves both heart sets) were copied from `../Holte-16/raw/uci-bundles/`. Their hashes equal those in `Holte-16/manifest.json` and equal a fresh download made on 2026-09-18. `Holte-16` itself was not touched. Holte's built CSVs are not Woike's versions (different rows, cues and, for Horse Colic, a different class column) and were not copied.
- **Self-contained folders.** The Heart Disease bundle is stored under both `HUNG` and `CLEV` with the same hash.
- **Row counting.** A row is a non-empty data record of the primary file(s) named in the manifest: CSV records after the header; non-blank lines of UCI `.data` files; lines after `@data` in the ARFF; for the two StatLib text files, the lines matching the data pattern recorded in the manifest (contiguous blocks: lines 87-586 of `irish.ed`, lines 49-720 of `profb`). `raw_attribute_count` is the number of fields per record, identifiers and class included.
- **Missing tokens** counted by the script: `?` (UCI), blank (ACD), `.` (`halloffame.csv`). Zero codes that stand for missing (`irish.ed` prestige and educational level) are handled explicitly in the relevant check and documented.
- **Status vocabulary** is defined in `manifest.json` under `status_vocabulary`. `reproduced_by_rule` marks criteria that need a binarization; the rule recorded is the one that reproduces Woike's split, stated as a finding, not adopted as a decision.
- **Nothing is transcribed as measured.** All counts in `manifest.json`, `SOURCES.md` and `expected-counts.csv` were written by code from the downloaded files; Woike's figures are transcribed from Tabelle 6.9 and labelled as his.

## Verification

Python 3 (run here with 3.13); no third-party packages; no network access.

```text
python scripts/mkw08_verify.py
```

The script re-hashes all 161 files, confirms `raw/` holds no unlisted file, confirms each extracted file against its archive, re-counts rows, fields and class values, re-runs the reduction and binarization counts behind every comparison, prints one line per dataset, writes `verification-report.json`, and exits nonzero on any mismatch. It does not download anything. To re-acquire a file, use the URL in the manifest with `curl` (Python's `urllib` fails certificate verification on the machine this was built on) and compare the hash.

## What is NOT done

Deliberately left for the authors to rule on:

- No `data/*.csv` analysis files, no harness runs.
- No binarization of predictors. Woike median-split every continuous predictor and set cue direction inside each training sample; none of that is applied here.
- No cue selection. Where Woike used a subset (HEPA 7 of 19, HORS 6 of the 28 fields, HUNG 10 of 13, PIMA 6 of 8, BWAY 5 of 7, TOUR 4 of 8, CARD 8 or 5 of about 30, FOOT 4), the subset is not documented in the dissertation. The notes record which subsets are consistent with his counts and no more.
- No choice of positive class and no binarization of multi-class or numeric criteria. Eight criteria are multi-class or ordinal (POST, ZOO, IRIS, WINE, GLAS, CLEV, YEAS, AUTH; HOF has three codes), four are numeric counts or amounts (STRK, ALCO, TOUR, SCOT), and two are derived from other columns (BWAY run length, FOOT scores). For IRIS the positive species cannot be recovered from the counts.
- No complete-case deletion. Rows with missing values are all still in the raw files. The open question for the authors is whether to replicate Woike's reductions, which are recoverable for ten sets and not for HORS and VOTE, or to apply one documented protocol to the full raw files.
- No contact with Woike. His preprocessed files would settle HORS, VOTE and every cue subset.

Per-dataset lists of the decisions a build would need are in `SOURCES.md` and in `manifest.json` under `decisions_needed`.

## Citation and terms

Cite MKW08 for the benchmark and Woike (2008) for the list. Cite each UCI record by its DOI (in `manifest.json` and `SOURCES.md`), Simonoff (2003) for the ACD files, Garfinkel et al. (1999) for the cardiac data, and the StatLib and OpenML records as given. This is a research acquisition copy and does not supersede upstream terms.
