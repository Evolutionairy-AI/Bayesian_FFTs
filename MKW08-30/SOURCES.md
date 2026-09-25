# Source map and per-dataset provenance

All files were retrieved on **2026-09-18** with `curl` (no credentials, no query parameters other than the public dataset id), except the six UCI bundles that were **copied** from `DATA_SETS/Holte-16/raw/uci-bundles/` (retrieved 2026-08-25 by that package). For those six a fresh download of the same URL on 2026-09-18 was byte-identical, and their SHA-256 values equal the ones pinned in `Holte-16/manifest.json`. Nothing inside `Holte-16/` was moved or modified. Full SHA-256 values, byte sizes and URLs for all 161 files are in `manifest.json`; this file shows the first 12 hex digits only.

## Identification source

- Jan K. Woike (2008), *Die paradoxe Rationalität einfacher Heuristiken*, dissertation, Ruhr-Universität Bochum, URN `urn:nbn:de:hbz:294-21536`. Tabelle 6.9 (printed p. 212) and pp. 211-214. Local copy `references/Woike_2008_Dissertation_Bochum.pdf`, SHA-256 `2946bbf61025acd4fdcbf0b87823b9b8774b9770c76b93d7a7f908349d647c73`.
- Text extract of pp. 211-214: `references/Woike_2008_Tabelle_6.9_pp211-214_extract.txt`, SHA-256 `375d0c6ee7bf3505beea37e493e71e2ffcbd19fe0d75635b680168d15e520774`.
- Woike, Hoffrage & Martignon (2017), Decision 4(4), Table 1 (the 11 medical sets): `references/Woike_Hoffrage_Martignon_2017_Decision.pdf`, SHA-256 `5ebb654bcec104e3b9447dc3670a99944a478f2d94653e26c5883c0ac12df4e4`.
- How the thirty were tied to Martignon, Katsikopoulos & Woike (2008): `../DATASET_HUNT_MKW08_Lichtenberg_2026-09-18.md`, section 1A.

## Source families

| Family | Sets | Base URL | Notes |
|---|---|---|---|
| ACD | 10: BANK, SOLV, BWAY, CRED, STRK, CYY, TOUR, AUTH, HOF, SCOT | https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/<name>.csv | Per-file CSVs, each byte-identical to the member of the same name in the whole-site archive `raw/_ACD_bundle/data.zip` (84 CSV + 84 XLS members), which is kept as a cross-check. |
| UCI | 16: ECHO, POST, ZOO, IRIS, HEPA, WINE, GLAS, HORS, SPCT, HUNG, CLEV, ALCO, IONO, VOTE, BCW, YEAS | https://archive.ics.uci.edu/static/public/<id>/<slug>.zip | One pinned ZIP per record, extracted in full to `raw/<CODE>/extracted/`. The Heart Disease bundle (UCI 45) serves both HUNG and CLEV and is stored under both codes (identical hash). An API metadata snapshot `uci-<id>-metadata.json` sits beside each bundle. |
| StatLib | 2: EDUC, FOOT | https://lib.stat.cmu.edu/datasets/<name> | Plain-text files with the data block embedded after a description; kept whole. |
| UCLA Statistics (dead) via hbiostat and the Internet Archive | 1: CARD | https://hbiostat.org/data/repo/stressEcho.csv and an Internet Archive capture of the original | The UCLA page Woike cites returns HTTP 404. Two copies are held: hbiostat's recoded CSV and the 2007-07-01 Internet Archive capture of the original `cardiac.dat` with its codebook. |
| OpenML | 1: PIMA | https://openml.org/data/v1/download/37/diabetes.arff | Pima Indians Diabetes is no longer hosted by UCI. The ARFF's MD5 equals the checksum in the OpenML description. |

## The four Simonoff file mappings that the hunt report left INFERRED

All four are now **confirmed** against Woike's n, cue count, predictor-type profile and class split.

| Woike label | File(s) | Evidence (all counts measured) |
|---|---|---|
| Solvency | `japansolvent.csv` | 52 rows = Woike n; 8 continuous predictors = Woike cues and type profile; Solvent 1/0 = 27/25 = Woike n1/n0. |
| Strikes | `wildcat.csv` | 163 rows = Woike n; 4 distinct predictors with a 2 binary + 2 continuous profile; strikes>0 / =0 = 86/77 = Woike n1/n0. |
| Baseball CYY | `cyyoung8092.csv + cyyoung9302.csv (pooled)` | 97 + 92 = 189 rows = Woike n; 9 predictors with a 2/1/6 type profile; Cy Young 1/0 = 43/146 = Woike n1/n0. |
| Tourism | `braziltourism.csv` | 412 raw rows reduce to exactly 365 = Woike n under complete cases on four predictors matching his description, with trips>0 / =0 = 85/280 = Woike n1/n0. |

Uniqueness check over all 84 CSV members of `data.zip`: the only other members whose row count equals one of the relevant numbers are `birthday.csv` (365 rows: births per calendar day, 4 columns) and `homerun.csv` (163 rows: per-game home-run logs for McGwire, Sosa and Bonds, 28 columns). Neither fits Woike's description (travel decisions; wildcat strikes with two binary and two continuous predictors), and neither yields his class splits. `AIDS.csv` (50 rows), `chlamydia.csv`, `impeach.csv`, `neavote.csv` (100 rows each) and `negotiation.csv` (92 rows) coincide in row count with Bankruptcy, Credit Score and one Cy Young file, whose mappings were never in doubt. No candidate file had to be ruled out for failing; no mapping failed.

## Per-dataset provenance

### 1. BANK : Bankruptcy

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 50, cues = 5, split = 25 / 25, predictor types bin/cat/cont = 0/0/5, source tag ACD.
- **Criterion:** Bankrupt (1) or not (0); natively binary.
- **Raw data:** `raw/BANK/bankruptcy.csv` (50 rows). Raw rows **50**, fields per record **7**. 7 columns: Company (identifier), five financial ratios, Bankrupt. Five predictors, as in Tabelle 6.9.
- **Raw class counts** (column `Bankrupt`): 0: 25, 1: 25.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 50 data rows, no blank cells; Bankrupt 25/25.
- **Decisions a build would need (not taken here):** Drop the identifier column Company.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/BANK/bankruptcy.csv`: 2290 bytes, SHA-256 `f41e95d9fe05…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/bankruptcy.csv>

### 2. SOLV : Solvency

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 52, cues = 8, split = 27 / 25, predictor types bin/cat/cont = 0/0/8, source tag ACD.
- **Criterion:** Solvent (1) or not (0); natively binary.
- **Raw data:** `raw/SOLV/japansolvent.csv` (52 rows). Raw rows **52**, fields per record **10**. 10 columns: Firm (identifier), Solvent, eight financial ratios. Eight predictors, as in Tabelle 6.9.
- **Raw class counts** (column `Solvent`): 0: 25, 1: 27.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. File mapping CONFIRMED (was inferred from the file name): 52 rows, eight continuous ratios, Solvent 27/25.
- **Decisions a build would need (not taken here):** Drop the identifier column Firm.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/SOLV/japansolvent.csv`: 3788 bytes, SHA-256 `2a2990e13ebf…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/japansolvent.csv>

### 3. ECHO : Echocardiogram

- **Source:** UCI: Echocardiogram (UCI id 38, DOI `10.24432/C5QW24`). Landing page <https://archive.ics.uci.edu/dataset/38/echocardiogram>.
- **Tabelle 6.9:** n = 62, cues = 7, split = 18 / 44, predictor types bin/cat/cont = 1/0/6, source tag UCI.
- **Criterion:** Survival for at least 12 months after the heart attack. The raw file ships a derived column alive-at-1 (attribute 13) that is '?' for 57 of the 131 well-formed rows.
- **Raw data:** `raw/ECHO/extracted/echocardiogram.data` (132 rows). Raw rows **132**, fields per record **13**. 13 fields per record (line 50 has a stray leading comma, hence 14). echocardiogram.names says attributes 10-12 (mult, name, group) are to be ignored and 1, 2 and 13 (survival, still-alive, alive-at-1) carry the outcome; that leaves seven clinical attributes (3-9), of which pericardial-effusion is binary: the 1 + 6 profile of Tabelle 6.9.
- **Comparison with Tabelle 6.9:** n **explained**, split **exact_after_reduction**. 132 raw lines. Rows with alive-at-1 known AND attributes 3-9 complete: 62, with alive-at-1 = 1 for 18 and 0 for 44, which is Woike's n and split exactly. CAUTION, measured on these 62 rows: the shipped alive-at-1 column does not follow its own definition in echocardiogram.names (1 = alive at one year). Of the 44 rows coded 0, 42 have survival >= 12 months (38 died later, 4 still alive) and 2 died within 12 months; of the 18 rows coded 1, 17 are still alive but were followed for fewer than 12 months (the names file says such patients cannot be used) and 1 has survival missing. Woike's 18/44 matches the column as shipped, not a re-derivation from survival and still-alive (which gives 42 survived, 2 died, 18 undeterminable).
- **Counts re-checked by the script:** `rows_with_13_fields` = 131, `alive_at_1_unknown` = 57, `complete_attrs3to9_and_alive_at_1` = 62, `alive_at_1=1` = 18, `alive_at_1=0` = 44.
- **Decisions a build would need (not taken here):** Row policy: 62 complete cases versus all rows with a determinable criterion. Criterion: alive-at-1 as shipped (matches Woike, but contradicts the names-file definition on these rows) or a re-derivation from survival and still-alive. Line 50 is malformed (leading comma, nearly all '?'). Cue set: the seven attributes 3-9, per the names file.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/ECHO/uci-38.zip`: 4562 bytes, SHA-256 `11debc93f397…`, downloaded, <https://archive.ics.uci.edu/static/public/38/echocardiogram.zip>
  - `raw/ECHO/uci-38-metadata.json`: 5008 bytes, SHA-256 `a5def622ee4a…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=38>
  - plus 3 archive members extracted byte-for-byte to `raw/ECHO/extracted/`.

### 4. POST : Post-Operative

- **Source:** UCI: Post-Operative Patient (UCI id 82, DOI `10.24432/C5DG6Q`). Landing page <https://archive.ics.uci.edu/dataset/82/post+operative+patient>.
- **Tabelle 6.9:** n = 86, cues = 8, split = 24 / 62, predictor types bin/cat/cont = 0/7/1, source tag UCI.
- **Criterion:** Discharge decision ADM-DECS with three values: A (general ward), S (home), I (intensive care).
- **Raw data:** `raw/POST/extracted/post-operative.data` (90 rows). Raw rows **90**, fields per record **9**. 9 fields: eight attributes (seven categorical, COMFORT numeric) and the decision ADM-DECS.
- **Raw class counts** (last field): A: 64, I: 2, S: 24.
- **Comparison with Tabelle 6.9:** n **explained**, split **reproduced_by_rule**. 90 raw rows (A 64, S 24, I 2; line 4 carries the token 'A ' with a trailing space, counted here as A). Three rows have '?' in COMFORT (two A, one I); 87 are complete. Removing the one remaining class-I row gives 86 = S 24 / A 62, Woike's n and split. Merging I into either class cannot give 24/62 on the complete rows (it would be 87).
- **Counts re-checked by the script:** `complete_rows` = 87, `complete_rows_excluding_class_I` = 86, `S` = 24, `A` = 62.
- **Decisions a build would need (not taken here):** Class I (2 rows): drop or merge. Three rows with '?' in COMFORT. Positive class: Tabelle 6.9 has n1 = 24 (S); Woike et al. (2017) Table 1 reports base rate .721 (A, 'keep patient in hospital').
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/POST/uci-82.zip`: 2171 bytes, SHA-256 `eed2652e7d4b…`, downloaded, <https://archive.ics.uci.edu/static/public/82/post+operative+patient.zip>
  - `raw/POST/uci-82-metadata.json`: 4054 bytes, SHA-256 `e490f208d565…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=82>
  - plus 3 archive members extracted byte-for-byte to `raw/POST/extracted/`.

### 5. BWAY : Broadway

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 89, cues = 5, split = 27 / 62, predictor types bin/cat/cont = 0/3/2, source tag ACD.
- **Criterion:** Whether the show ran six months or more; from the five-category column Show run.
- **Raw data:** `raw/BWAY/broadway.csv` (95 rows). Raw rows **95**, fields per record **10**. 10 columns: Show (identifier), Type, Revival, NYT rating, DN rating, Tony awards, Tony nominations, Week 1 attendance, Show run (five ordered categories), Show run code. Seven candidate predictors; Woike used five (3 categorical, 2 continuous); which five is not stated.
- **Raw class counts** (column `Show run`): 1-2 years: 11, 2-3 years: 1, 6-12 months: 11, Less than 6 months: 68, More than 3 years: 4.
- **Comparison with Tabelle 6.9:** n **explained**, split **reproduced_by_rule**. 95 raw rows; 9 blank cells (NYT rating 2, DN rating 3, Week 1 attendance 4) spread over 6 rows; 89 complete rows, of which 'Less than 6 months' 62 and longer 27: Woike's n and split.
- **Counts re-checked by the script:** `complete_rows` = 89, `run_less_than_6_months` = 62, `run_6_months_or_more` = 27.
- **Decisions a build would need (not taken here):** Row policy: 6 rows with blank ratings/attendance. Which five of the seven candidate predictors. Binarization of Show run at six months.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/BWAY/broadway.csv`: 6384 bytes, SHA-256 `4f3b371d3352…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/broadway.csv>

### 6. CRED : Credit Score

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 100, cues = 6, split = 73 / 27, predictor types bin/cat/cont = 2/1/3, source tag ACD.
- **Criterion:** Application accepted (1) or not (0); natively binary.
- **Raw data:** `raw/CRED/creditscore.csv` (100 rows). Raw rows **100**, fields per record **7**. 7 columns: six applicant attributes and Application.accepted. Six predictors, as in Tabelle 6.9.
- **Raw class counts** (column `Application.accepted`): 0: 27, 1: 73.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 100 rows, no blank cells; accepted 73 / rejected 27.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/CRED/creditscore.csv`: 2245 bytes, SHA-256 `39d6051846f0…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/creditscore.csv>

### 7. ZOO : Zoo

- **Source:** UCI: Zoo (UCI id 111, DOI `10.24432/C5R59V`). Landing page <https://archive.ics.uci.edu/dataset/111/zoo>.
- **Tabelle 6.9:** n = 101, cues = 16, split = 41 / 60, predictor types bin/cat/cont = 15/1/0, source tag UCI.
- **Criterion:** Mammal versus not; from the seven-valued attribute type.
- **Raw data:** `raw/ZOO/extracted/zoo.data` (101 rows). Raw rows **101**, fields per record **18**. 18 fields: animal name (identifier), 15 boolean attributes, legs (numeric, six values), type (1-7). Sixteen predictors.
- **Raw class counts** (last field): 1: 41, 2: 20, 3: 5, 4: 13, 5: 4, 6: 8, 7: 10.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 101 rows; type 1 (mammal) = 41, all other types = 60.
- **Counts re-checked by the script:** `type_1_mammal` = 41, `rest` = 60.
- **Decisions a build would need (not taken here):** Binarization: type 1 versus the rest. Drop the identifier column; legs is multi-valued.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/ZOO/uci-111.zip`: 2496 bytes, SHA-256 `d49013253628…`, downloaded, <https://archive.ics.uci.edu/static/public/111/zoo.zip>
  - `raw/ZOO/uci-111-metadata.json`: 3993 bytes, SHA-256 `0f933fb3de00…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=111>
  - plus 3 archive members extracted byte-for-byte to `raw/ZOO/extracted/`.

### 8. IRIS : Iris

- **Source:** UCI: Iris (UCI id 53, DOI `10.24432/C56C76`). Landing page <https://archive.ics.uci.edu/dataset/53/iris>.
- **Tabelle 6.9:** n = 150, cues = 4, split = 50 / 100, predictor types bin/cat/cont = 0/0/4, source tag UCI.
- **Criterion:** One of the three species versus the other two; Woike does not say which species.
- **Raw data:** `raw/IRIS/extracted/iris.data` (150 rows). Raw rows **150**, fields per record **5**. 5 fields: four measurements and the species.
- **Raw class counts** (last field): Iris-setosa: 50, Iris-versicolor: 50, Iris-virginica: 50.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 150 rows, 50 per species, so any one-versus-rest coding gives 50/100. The bundle also holds bezdekIris.data, which differs from iris.data on lines 35 and 38 (measured).
- **Counts re-checked by the script:** `smallest_species` = 50, `largest_species` = 50, `rows_minus_one_species` = 100.
- **Decisions a build would need (not taken here):** Which species is the positive class (not recoverable from the counts). iris.data versus bezdekIris.data.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/IRIS/uci-53.zip`: 3738 bytes, SHA-256 `d11fe30213d3…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-53.zip`, <https://archive.ics.uci.edu/static/public/53/iris.zip>
  - `raw/IRIS/uci-53-metadata.json`: 2861 bytes, SHA-256 `0387b83840ad…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-53.json`, <https://archive.ics.uci.edu/api/dataset?id=53>
  - plus 4 archive members extracted byte-for-byte to `raw/IRIS/extracted/`.

### 9. HEPA : Hepatitis

- **Source:** UCI: Hepatitis (UCI id 46, DOI `10.24432/C5Q59J`). Landing page <https://archive.ics.uci.edu/dataset/46/hepatitis>.
- **Tabelle 6.9:** n = 153, cues = 7, split = 121 / 32, predictor types bin/cat/cont = 6/0/1, source tag UCI.
- **Criterion:** Class: 1 = die, 2 = live; natively binary.
- **Raw data:** `raw/HEPA/extracted/hepatitis.data` (155 rows). Raw rows **155**, fields per record **20**. 20 fields: class first, then 19 attributes (AGE and five laboratory values continuous, 13 binary). Woike used 7 (6 binary, 1 continuous); which seven is not stated.
- **Raw class counts** (first field): 1: 32, 2: 123.
- **Comparison with Tabelle 6.9:** n **explained**, split **exact_after_reduction**. 155 raw rows (die 32, live 123); only 80 rows are complete on all 19 attributes. Eight attributes have at most one '?' (AGE, SEX, STEROID, ANTIVIRALS, FATIGUE, MALAISE, ANOREXIA, HISTOLOGY); complete cases on those eight are 153 rows (lines 4 and 57 drop out, both 'live'), giving live 121 / die 32 = Woike's n and split. Exhaustive check: with AGE as the continuous cue, 6 of the 1,716 six-subsets of the 13 binary attributes give 153 rows and 32/121, all drawn from those seven low-missingness binary attributes. The mechanism is identified; the exact seven cues are not.
- **Counts re-checked by the script:** `complete_rows_all_19_attrs` = 80, `complete_on_8_low_missing_attrs` = 153, `class_2_live` = 121, `class_1_die` = 32.
- **Decisions a build would need (not taken here):** Row policy: 2 rows versus 75 rows with any '?'. Cue subset: 7 of 19 (six candidate subsets are consistent with n = 153).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/HEPA/uci-46.zip`: 6235 bytes, SHA-256 `8573c2898714…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-46.zip`, <https://archive.ics.uci.edu/static/public/46/hepatitis.zip>
  - `raw/HEPA/uci-46-metadata.json`: 5183 bytes, SHA-256 `9cf2ba8fd949…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-46.json`, <https://archive.ics.uci.edu/api/dataset?id=46>
  - plus 9 archive members extracted byte-for-byte to `raw/HEPA/extracted/`.

### 10. STRK : Strikes

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 163, cues = 4, split = 86 / 77, predictor types bin/cat/cont = 2/0/2, source tag ACD.
- **Criterion:** Number of wildcat strikes: a COUNT (0-22), dichotomized by Woike.
- **Raw data:** `raw/STRK/wildcat.csv` (163 rows). Raw rows **163**, fields per record **6**. 6 columns: Grievances, Rotate, Union, Workforce, Log workforce, Wildcat strikes. 'Log workforce' equals ln(Workforce) to 5e-6 (measured), so there are four distinct predictors, two binary (Rotate, Union) and two continuous: Woike's profile.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. File mapping CONFIRMED: 163 rows; strikes > 0 in 86 rows and = 0 in 77 rows, Woike's split exactly.
- **Counts re-checked by the script:** `Wildcat strikes>0` = 86, `Wildcat strikes=0` = 77.
- **Decisions a build would need (not taken here):** Threshold for the numeric criterion (any strike versus none reproduces Woike). Workforce versus Log workforce (the same cue after a median split).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/STRK/wildcat.csv`: 3651 bytes, SHA-256 `212e20f9fcf3…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/wildcat.csv>

### 11. WINE : Wine

- **Source:** UCI: Wine (UCI id 109, DOI `10.24432/C5PC7J`). Landing page <https://archive.ics.uci.edu/dataset/109/wine>.
- **Tabelle 6.9:** n = 178, cues = 13, split = 71 / 107, predictor types bin/cat/cont = 0/0/13, source tag UCI.
- **Criterion:** One of three cultivars versus the other two.
- **Raw data:** `raw/WINE/extracted/wine.data` (178 rows). Raw rows **178**, fields per record **14**. 14 fields: cultivar class first, then 13 chemical measurements.
- **Raw class counts** (first field): 1: 59, 2: 71, 3: 48.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 178 rows; classes 59 / 71 / 48. Only class 2 has 71 members, so Woike's 71/107 is class 2 versus the rest.
- **Counts re-checked by the script:** `class_2` = 71, `rest` = 107.
- **Decisions a build would need (not taken here):** Positive class: class 2 reproduces Tabelle 6.9.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/WINE/uci-109.zip`: 6038 bytes, SHA-256 `2bae62c44812…`, downloaded, <https://archive.ics.uci.edu/static/public/109/wine.zip>
  - `raw/WINE/uci-109-metadata.json`: 4496 bytes, SHA-256 `ac0e877a4f06…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=109>
  - plus 3 archive members extracted byte-for-byte to `raw/WINE/extracted/`.

### 12. CYY : Baseball CYY

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 189, cues = 9, split = 43 / 146, predictor types bin/cat/cont = 2/1/6, source tag ACD.
- **Criterion:** Cy Young award won (1) or not (0); natively binary.
- **Raw data:** `raw/CYY/cyyoung8092.csv` (97 rows); `raw/CYY/cyyoung9302.csv` (92 rows). Raw rows **189**, fields per record **11**. 11 columns in both files (identical headers): Year, Pitcher (identifier), League, Type, six performance statistics, Cy Young. Excluding Pitcher leaves nine predictors: 2 binary (League, Type), 1 categorical (Year), 6 continuous, which is Woike's profile.
- **Raw class counts** (column `Cy Young`): 0: 146, 1: 43.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. File mapping CONFIRMED: 97 rows (1980-92) + 92 rows (1993-2002) = 189; Cy Young 43 / 146 pooled. Neither file alone matches.
- **Decisions a build would need (not taken here):** Pooling of the two files (Simonoff uses the second as a validation sample). Whether Year is a cue.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/CYY/cyyoung8092.csv`: 5233 bytes, SHA-256 `46c8a1278b71…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/cyyoung8092.csv>
  - `raw/CYY/cyyoung9302.csv`: 5123 bytes, SHA-256 `4bf100def3dc…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/cyyoung9302.csv>

### 13. GLAS : Forensic Glass

- **Source:** UCI: Glass Identification (UCI id 42, DOI `10.24432/C5WW2P`). Landing page <https://archive.ics.uci.edu/dataset/42/glass+identification>.
- **Tabelle 6.9:** n = 214, cues = 9, split = 146 / 68, predictor types bin/cat/cont = 0/0/9, source tag UCI.
- **Criterion:** Window glass versus other glass; from the six-valued attribute type (1, 2, 3, 5, 6, 7 occur).
- **Raw data:** `raw/GLAS/extracted/glass.data` (214 rows). Raw rows **214**, fields per record **11**. 11 fields: Id, refractive index, eight oxide contents, type. Nine predictors as in Tabelle 6.9 (Woike's text says eight).
- **Raw class counts** (last field): 1: 70, 2: 76, 3: 17, 5: 13, 6: 9, 7: 29.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 214 rows; types 70/76/17/13/9/29. Woike's 146/68 equals types 1+2 (building windows) versus the rest. Counting vehicle windows (type 3) as window glass gives 163/51, which is NOT Woike's split.
- **Counts re-checked by the script:** `types_1+2_building_windows` = 146, `rest_after_1+2` = 68, `types_1+2+3_all_windows` = 163, `rest_after_1+2+3` = 51.
- **Decisions a build would need (not taken here):** Definition of 'window glass': types 1+2 (reproduces Woike) or types 1+2+3. Drop the Id column.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/GLAS/uci-42.zip`: 6380 bytes, SHA-256 `499c07a17115…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-42.zip`, <https://archive.ics.uci.edu/static/public/42/glass+identification.zip>
  - `raw/GLAS/uci-42-metadata.json`: 4085 bytes, SHA-256 `67bcb4030422…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-42.json`, <https://archive.ics.uci.edu/api/dataset?id=42>
  - plus 4 archive members extracted byte-for-byte to `raw/GLAS/extracted/`.

### 14. HORS : Horse Colic

- **Source:** UCI: Horse Colic (UCI id 47, DOI `10.24432/C58W23`). Landing page <https://archive.ics.uci.edu/dataset/47/horse+colic>.
- **Tabelle 6.9:** n = 218, cues = 6, split = 128 / 90, predictor types bin/cat/cont = 1/1/4, source tag UCI.
- **Criterion:** Not described in the dissertation. Woike et al. (2017) Table 1: 'Treated with surgery (yes/no)', base rate .587 = 128/218, which points to attribute 1 (surgery: 1 = yes, 2 = no). Holte's class for the same file is attribute 24 (surgical lesion).
- **Raw data:** `raw/HORS/extracted/horse-colic.data` (300 rows); `raw/HORS/extracted/horse-colic.test` (68 rows). Raw rows **368**, fields per record **28**. 28 whitespace-separated fields. Woike used 6 cues (1 binary, 1 categorical, 4 continuous); which six is not stated, and the dissertation has no descriptive paragraph for this set.
- **Raw class counts** (first field): 1: 214, 2: 152, ?: 2.
- **Comparison with Tabelle 6.9:** n **unexplained**, split **not_reproduced**. 300 + 68 = 368 raw rows; attribute 1: 214 yes, 152 no, 2 '?'. Woike's 218 (128/90) was NOT reproduced. Checked, for the criteria surgery (attr 1), outcome lived/not (attr 23) and surgical lesion (attr 24), on data+test, data only and test only: (a) complete cases on 4 of the 7 continuous attributes plus any two other attributes: no combination gives 218 with 128/90; (b) complete cases on ANY six of the 23 usable attributes (100,947 subsets per criterion and scope): 218 rows with a 128/90 split occur for 4 subsets with surgery on data+test (all built on attributes {6, 9, 10, 12, 20}), 5 with surgical lesion on data+test, 4 with surgery and 1 with surgical lesion on data only, none with outcome. Not one of these 14 subsets contains four continuous attributes, so none has Woike's 1/1/4 profile, and with this many subsets chance hits are expected. They are recorded as candidates, not as an explanation.
- **Decisions a build would need (not taken here):** Everything: criterion column, row policy, cue subset, pooling of .data and .test. Needs Woike's file or his recollection.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/HORS/uci-47.zip`: 14785 bytes, SHA-256 `e4a2d4e77573…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-47.zip`, <https://archive.ics.uci.edu/static/public/47/horse+colic.zip>
  - `raw/HORS/uci-47-metadata.json`: 13665 bytes, SHA-256 `a10b4167e652…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-47.json`, <https://archive.ics.uci.edu/api/dataset?id=47>
  - plus 5 archive members extracted byte-for-byte to `raw/HORS/extracted/`.

### 15. SPCT : SPECT

- **Source:** UCI: SPECT Heart (UCI id 95, DOI `10.24432/C5P304`). Landing page <https://archive.ics.uci.edu/dataset/95/spect+heart>.
- **Tabelle 6.9:** n = 267, cues = 22, split = 212 / 55, predictor types bin/cat/cont = 22/0/0, source tag UCI.
- **Criterion:** Overall diagnosis (1 abnormal, 0 normal); natively binary.
- **Raw data:** `raw/SPCT/extracted/SPECT.train` (80 rows); `raw/SPCT/extracted/SPECT.test` (187 rows). Raw rows **267**, fields per record **23**. 23 fields: diagnosis first, then 22 binary features.
- **Raw class counts** (first field): 0: 55, 1: 212.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 80 (train) + 187 (test) = 267 rows; diagnosis 1 = 212, 0 = 55 pooled.
- **Decisions a build would need (not taken here):** Pooling of the donor's train and test files (train alone is 40/40).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/SPCT/uci-95.zip`: 3669 bytes, SHA-256 `0df4ab4903ce…`, downloaded, <https://archive.ics.uci.edu/static/public/95/spect+heart.zip>
  - `raw/SPCT/uci-95-metadata.json`: 6458 bytes, SHA-256 `6f7d6a5c8ae0…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=95>
  - plus 4 archive members extracted byte-for-byte to `raw/SPCT/extracted/`.

### 16. HUNG : Heart (Hungaria)

- **Source:** UCI: Heart Disease (UCI id 45, DOI `10.24432/C52P4X`). Landing page <https://archive.ics.uci.edu/dataset/45/heart+disease>.
- **Tabelle 6.9:** n = 294, cues = 10, split = 106 / 188, predictor types bin/cat/cont = 1/4/5, source tag UCI.
- **Criterion:** Heart disease present (num = 1) or absent (0); binary in processed.hungarian.data. reprocessed.hungarian.data carries num 0-4 (188/37/26/28/15) for the same 294 patients.
- **Raw data:** `raw/HUNG/extracted/processed.hungarian.data` (294 rows). Raw rows **294**, fields per record **14**. 14 fields: 13 attributes and num. slope, ca and thal are '?' in 190, 291 and 266 of the 294 rows (measured), which is presumably why Woike has 10 cues; the dissertation does not name them.
- **Raw class counts** (last field): 0: 188, 1: 106.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 294 rows, num 1 = 106, 0 = 188: Woike's n and split with NO row deletion, although 293 rows contain a '?' somewhere. Side observation, not Tabelle 6.9: Woike et al. (2017) Table 1 prints 262 objects and base rate .374 for this set; complete cases on the first ten attributes are 261 (98 positive, .375), so the 2017 figure is near but not reproduced.
- **Counts re-checked by the script:** `missing_slope` = 190, `missing_ca` = 291, `missing_thal` = 266, `complete_on_first_10_attrs` = 261.
- **Decisions a build would need (not taken here):** Which Hungarian file (processed, reprocessed, or the 76-attribute hungarian.data). Cue subset: 10 of 13. Missing-value policy for chol (23 '?'), fbs (8) and four single cells.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/HUNG/uci-45.zip`: 128894 bytes, SHA-256 `b17cd273da9c…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-45.zip`, <https://archive.ics.uci.edu/static/public/45/heart+disease.zip>
  - `raw/HUNG/uci-45-metadata.json`: 9622 bytes, SHA-256 `88cbc5a8918c…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-45.json`, <https://archive.ics.uci.edu/api/dataset?id=45>
  - plus 22 archive members extracted byte-for-byte to `raw/HUNG/extracted/`.

### 17. CLEV : Heart (Cleveland)

- **Source:** UCI: Heart Disease (UCI id 45, DOI `10.24432/C52P4X`). Landing page <https://archive.ics.uci.edu/dataset/45/heart+disease>.
- **Tabelle 6.9:** n = 297, cues = 13, split = 137 / 160, predictor types bin/cat/cont = 3/5/5, source tag UCI.
- **Criterion:** Heart disease present (num > 0) versus absent (num = 0); ordinal 0-4 binarized.
- **Raw data:** `raw/CLEV/extracted/processed.cleveland.data` (303 rows). Raw rows **303**, fields per record **14**. 14 fields: 13 attributes and num (0-4). The bundle also holds cleve.mod (Holte's file) and the 76-attribute cleveland.data.
- **Raw class counts** (last field): 0: 164, 1: 55, 2: 36, 3: 35, 4: 13.
- **Comparison with Tabelle 6.9:** n **explained**, split **reproduced_by_rule**. 303 raw rows (num = 0: 164, > 0: 139); 6 rows contain '?' (ca in 4, thal in 2); the 297 complete rows split 137 (num > 0) / 160 (num = 0): Woike's n and split.
- **Counts re-checked by the script:** `complete_rows` = 297, `num=0` = 160, `num>0` = 137.
- **Decisions a build would need (not taken here):** Row policy: 6 rows with '?'. Binarization num > 0. Which Cleveland file.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/CLEV/uci-45.zip`: 128894 bytes, SHA-256 `b17cd273da9c…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-45.zip`, <https://archive.ics.uci.edu/static/public/45/heart+disease.zip>
  - `raw/CLEV/uci-45-metadata.json`: 9622 bytes, SHA-256 `88cbc5a8918c…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-45.json`, <https://archive.ics.uci.edu/api/dataset?id=45>
  - plus 22 archive members extracted byte-for-byte to `raw/CLEV/extracted/`.

### 18. ALCO : Alcohol

- **Source:** UCI: Liver Disorders (UCI id 60, DOI `10.24432/C54G67`). Landing page <https://archive.ics.uci.edu/dataset/60/liver+disorders>.
- **Tabelle 6.9:** n = 345, cues = 5, split = 88 / 257, predictor types bin/cat/cont = 0/0/5, source tag UCI.
- **Criterion:** Alcohol consumption: a NUMERIC variable (drinks), dichotomized by Woike at 'more than 2.5 pints per day'.
- **Raw data:** `raw/ALCO/extracted/bupa.data` (345 rows). Raw rows **345**, fields per record **7**. 7 fields: five blood tests, drinks (half-pint equivalents per day), selector. Five predictors. NB selector is the donor's train/test flag (145/200), not a class; it is recorded below only because it is the last field.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 345 rows. drinks > 5 half-pints (= 2.5 pints) in 88 rows, <= 5 in 257: Woike's split exactly. (drinks >= 5 gives 105.) noteDuplicates.txt in the bundle lists four duplicated rows; Woike kept them (n = 345).
- **Counts re-checked by the script:** `drinks>5_half_pints` = 88, `drinks<=5_half_pints` = 257.
- **Decisions a build would need (not taken here):** Threshold on drinks (strictly more than 5 half-pints reproduces Woike). Do not use selector as a cue or class.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/ALCO/uci-60.zip`: 5985 bytes, SHA-256 `839c8b8c3cd0…`, downloaded, <https://archive.ics.uci.edu/static/public/60/liver+disorders.zip>
  - `raw/ALCO/uci-60-metadata.json`: 3653 bytes, SHA-256 `035bd0a019a0…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=60>
  - plus 10 archive members extracted byte-for-byte to `raw/ALCO/extracted/`.

### 19. IONO : Ionosphere

- **Source:** UCI: Ionosphere (UCI id 52, DOI `10.24432/C5W01B`). Landing page <https://archive.ics.uci.edu/dataset/52/ionosphere>.
- **Tabelle 6.9:** n = 351, cues = 33, split = 225 / 126, predictor types bin/cat/cont = 0/0/33, source tag UCI.
- **Criterion:** Radar return good (g) or bad (b); natively binary.
- **Raw data:** `raw/IONO/extracted/ionosphere.data` (351 rows). Raw rows **351**, fields per record **35**. 35 fields: 34 attributes and the class. Attribute 2 is 0 in all 351 rows (measured), which leaves 33 informative predictors, Woike's count.
- **Raw class counts** (last field): b: 126, g: 225.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 351 rows; g 225 / b 126.
- **Counts re-checked by the script:** `distinct_values_in_attribute_2` = 1.
- **Decisions a build would need (not taken here):** Attribute 2 is constant. Attribute 1 is binary (0/1) although Woike lists all 33 as continuous.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/IONO/uci-52.zip`: 29983 bytes, SHA-256 `4d218ece6275…`, downloaded, <https://archive.ics.uci.edu/static/public/52/ionosphere.zip>
  - `raw/IONO/uci-52-metadata.json`: 6604 bytes, SHA-256 `b9659d2e4129…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=52>
  - plus 3 archive members extracted byte-for-byte to `raw/IONO/extracted/`.

### 20. TOUR : Tourism

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 365, cues = 4, split = 85 / 280, predictor types bin/cat/cont = 1/0/3, source tag ACD.
- **Criterion:** Whether any trip was taken: Trips is a COUNT (0-7), dichotomized.
- **Raw data:** `raw/TOUR/braziltourism.csv` (412 rows). Raw rows **412**, fields per record **9**. 9 columns: Age, Sex, Income, Travel cost, Access road, Active, Passive, Logged income, Trips. 'Logged income' equals ln(Income) (measured). Woike used 4 cues (1 binary, 3 continuous); Age, Sex, Income and Travel cost fit his description ('demographic data and financial information') and his type profile, but he does not name them.
- **Comparison with Tabelle 6.9:** n **explained**, split **reproduced_by_rule**. File mapping CONFIRMED: 412 raw rows (Trips 0: 318, > 0: 94); blank cells in Income/Logged income (44), Travel cost (3), Active (2), Age, Sex, Passive (1 each). Complete cases on Age, Sex, Income, Travel cost: 365 rows with trips > 0 in 85 and = 0 in 280 = Woike's n and split exactly. (Complete on all nine columns: 363; on Sex, Income, Travel cost, Access road: 366.) Line 307 has the out-of-range value Sex = 4 and is inside the 365.
- **Counts re-checked by the script:** `complete_rows_all_columns` = 363, `complete_on_Age_Sex_Income_TravelCost` = 365, `trips>0` = 85, `trips=0` = 280.
- **Decisions a build would need (not taken here):** Row policy: 47 rows with blank predictors. Cue subset: 4 of 8 candidates. Threshold Trips > 0. The Sex = 4 record.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/TOUR/braziltourism.csv`: 15191 bytes, SHA-256 `8cc78497da8b…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/braziltourism.csv>

### 21. VOTE : Voting

- **Source:** UCI: Congressional Voting Records (UCI id 105, DOI `10.24432/C5C01P`). Landing page <https://archive.ics.uci.edu/dataset/105/congressional+voting+records>.
- **Tabelle 6.9:** n = 402, cues = 16, split = 248 / 154, predictor types bin/cat/cont = 0/16/0, source tag UCI.
- **Criterion:** Party: democrat or republican; natively binary.
- **Raw data:** `raw/VOTE/extracted/house-votes-84.data` (435 rows). Raw rows **435**, fields per record **17**. 17 fields: party first, then 16 votes (y / n / ?). Sixteen predictors; Woike types all 16 as categorical, which suggests '?' was kept as a third value.
- **Raw class counts** (first field): democrat: 267, republican: 168.
- **Comparison with Tabelle 6.9:** n **unexplained**, split **not_reproduced**. 435 raw rows (democrat 267, republican 168). Woike's 402 (248/154), i.e. 33 rows fewer (19 democrats, 14 republicans), was NOT reproduced. Checked: complete cases = 232; keeping rows with at most k '?' gives 399 (k = 2) and 415 (k = 3), never 402, also when up to two attributes are left out of the count (n = 402 occurs but never with 248/154); removing duplicate rows gives 342; the first or last 402 rows give 249/153 and 245/157. Complete cases on small attribute subsets do hit 402 with 248/154 (e.g. attributes {11, 14}, {3, 5, 8}, {6, 8, 14}), but Woike used all 16 votes and several subsets hit by chance, so none is an explanation.
- **Counts re-checked by the script:** `complete_rows` = 232, `rows_with_at_most_2_?` = 399, `rows_with_at_most_3_?` = 415, `distinct_rows` = 342.
- **Decisions a build would need (not taken here):** Row policy: Woike's 402 is unexplained; the full 435 is the defensible default. '?' as a third category versus missing.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/VOTE/uci-105.zip`: 4318 bytes, SHA-256 `ffec9d9328f2…`, copied from `DATA_SETS/Holte-16/raw/uci-bundles/uci-105.zip`, <https://archive.ics.uci.edu/static/public/105/congressional+voting+records.zip>
  - `raw/VOTE/uci-105-metadata.json`: 4603 bytes, SHA-256 `719386ae3e95…`, copied from `DATA_SETS/Holte-16/raw/metadata/uci-105.json`, <https://archive.ics.uci.edu/api/dataset?id=105>
  - plus 3 archive members extracted byte-for-byte to `raw/VOTE/extracted/`.

### 22. EDUC : Education

- **Source:** StatLib: irish.ed (Irish Educational Transitions Data). Landing page <https://lib.stat.cmu.edu/datasets/>.
- **Tabelle 6.9:** n = 435, cues = 4, split = 211 / 224, predictor types bin/cat/cont = 2/0/2, source tag O.
- **Criterion:** Leaving Certificate taken (2) or not (1); natively binary.
- **Raw data:** `raw/EDUC/irish.ed` (500 rows). Raw rows **500**, fields per record **6**. 6 integer fields per data line (lines 87-586 of the text file): sex, DVRT, educational level, Leaving Certificate, father's occupational prestige, type of school. Woike names his four cues: school type, test score, sex, father's prestige.
- **Raw class counts** (field 4): 1: 278, 2: 222.
- **Comparison with Tabelle 6.9:** n **explained**, split **exact_after_reduction**. 500 raw rows (not taken 278, taken 222). The file's own header says the simplified 441-case form removes primary terminal leavers and cases with missing data. Measured: dropping educational level 1 (37 primary terminal leavers = school type 9), educational level 0 (6 rows; an undocumented code, evidently missing) and prestige 0 (26 rows; documented as missing) leaves 435 rows, taken 211 / not taken 224 = Woike's n and split exactly. (Without the six level-0 rows it is 441 = 211/230.)
- **Counts re-checked by the script:** `edlevel=0` = 6, `edlevel=1` = 37, `prestige=0` = 26, `rows_edlevel>=2_and_prestige>0` = 435, `cert_taken` = 211, `cert_not_taken` = 224.
- **Decisions a build would need (not taken here):** Row policy: primary terminal leavers and zero-coded missing values. Educational level must not be a cue (it determines the criterion).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/EDUC/irish.ed`: 12729 bytes, SHA-256 `138d15329c34…`, downloaded, <https://lib.stat.cmu.edu/datasets/irish.ed>

### 23. CARD : Cardiac

- **Source:** UCLA Statistics (dead) via hbiostat and the Internet Archive: UCLA Stress Echocardiography Data (Garfinkel et al. 1999). Landing page <https://hbiostat.org/data/repo/stressEcho.html>.
- **Original location:** http://www.stat.ucla.edu/projects/datasets/cardiac.dat (HTTP 404 on 2026-09-18).
- **Tabelle 6.9:** n = 558, cues = 8, split = 469 / 89, predictor types bin/cat/cont = 1/0/7, source tag O.
- **Criterion:** Any cardiac event within a year (MI, PTCA, CABG or death). In the ORIGINAL UCLA coding 0 = yes; hbiostat recoded to 1 = yes.
- **Raw data:** `raw/CARD/stressEcho.csv` (558 rows); alternate `raw/CARD/wayback-20070701/cardiac.dat` (558 rows). Raw rows **558**, fields per record **32**. hbiostat file: 32 columns (row index + 31 variables; several renamed and recoded, posECG/equivecg merged into ecg). Original UCLA file: 42 columns. Woike used 8 cues (1 binary, 7 continuous) per Tabelle 6.9 but 5 in his results tables; none is named.
- **Raw class counts** (column `any.event`): 0: 469, 1: 89.
- **Alternate file class counts** (column `any event`): 0: 89, 1: 469.
- **Comparison with Tabelle 6.9:** n **exact**, split **exact**. 558 rows in both files. hbiostat any.event: 1 (event) 89, 0 (no event) 469. Original UCLA 'any event': 0 (= yes, event) 89, 1 (no event) 469. NB Tabelle 6.9's n1 = 469 equals the count of raw code 1, which the UCLA codebook defines as NO event; Woike et al. (2017) label the same .841 base rate 'Heart disease'. Whether this is a labelling slip or a coding choice is for the authors.
- **Decisions a build would need (not taken here):** Which file: the archived original (what Woike downloaded in 2007) or the recoded hbiostat copy. Polarity of the criterion (see comparison). Cue subset: 8 (or 5) of about 30. newMI, newPTCA, newCABG and death are components of the criterion and cannot be cues.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/CARD/stressEcho.csv`: 66650 bytes, SHA-256 `fa5027902d21…`, downloaded, <https://hbiostat.org/data/repo/stressEcho.csv>
  - `raw/CARD/stressEcho.html`: 7791 bytes, SHA-256 `1b4638d31aa3…`, downloaded, <https://hbiostat.org/data/repo/stressEcho.html>
  - `raw/CARD/wayback-20070701/cardiac.dat`: 71084 bytes, SHA-256 `793097d8ca0d…`, downloaded, <https://web.archive.org/web/20070701100302id_/http://www.stat.ucla.edu/projects/datasets/cardiac.dat>
  - `raw/CARD/wayback-20070701/cardiac-explanation.html`: 6907 bytes, SHA-256 `2421605cedc3…`, downloaded, <https://web.archive.org/web/20070701100345id_/http://www.stat.ucla.edu/projects/datasets/cardiac-explanation.html>

### 24. FOOT : Football

- **Source:** StatLib: profb (Pro Football Scores, Hal Stern). Landing page <https://lib.stat.cmu.edu/datasets/>.
- **Tabelle 6.9:** n = 672, cues = 4, split = 451 / 221, predictor types bin/cat/cont = 1/0/3, source tag O.
- **Criterion:** Woike's TEXT: whether the home team wins. Derived from the two points columns; not a column of the file.
- **Raw data:** `raw/FOOT/profb` (672 rows). Raw rows **672**, fields per record **8**. 8 fields per game (h/a, favorite points, underdog points, point spread, favorite, underdog, year, week) plus 0-2 optional indicator tokens (night/Monday/overtime). Woike used 4 cues (1 binary, 3 continuous); not named. The two points columns define the criterion and cannot be cues.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 672 games. Home team wins 391, does not win 281 (one tie): this is NOT Woike's split. Favorite wins 451, does not win 221: this IS Woike's 451/221 exactly. So the counts in Tabelle 6.9 correspond to 'favorite wins', not to 'home team wins' as the dissertation text says.
- **Counts re-checked by the script:** `favorite_wins` = 451, `favorite_does_not_win` = 221, `home_team_wins` = 391, `home_team_does_not_win` = 281, `ties` = 1.
- **Decisions a build would need (not taken here):** Criterion: 'favorite wins' (matches Woike's numbers) or 'home team wins' (matches his words). The single tie. Cue subset: 4 (spread, h/a, year, week are the only non-outcome numeric fields).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/FOOT/profb`: 27733 bytes, SHA-256 `95cd69fcdd09…`, downloaded, <https://lib.stat.cmu.edu/datasets/profb>

### 25. BCW : Breast Cancer

- **Source:** UCI: Breast Cancer Wisconsin (Original) (UCI id 15, DOI `10.24432/C5HP4Z`). Landing page <https://archive.ics.uci.edu/dataset/15/breast+cancer+wisconsin+original>.
- **Tabelle 6.9:** n = 683, cues = 9, split = 444 / 239, predictor types bin/cat/cont = 0/9/0, source tag UCI.
- **Criterion:** Benign (2) or malignant (4); natively binary.
- **Raw data:** `raw/BCW/extracted/breast-cancer-wisconsin.data` (699 rows). Raw rows **699**, fields per record **11**. 11 fields: sample id, nine cytological attributes (1-10), class. Nine predictors. The bundle also holds the unrelated WDBC and WPBC files. NOT Holte's BC (that is UCI 14, Ljubljana).
- **Raw class counts** (last field): 2: 458, 4: 241.
- **Comparison with Tabelle 6.9:** n **explained**, split **exact_after_reduction**. 699 raw rows (benign 458, malignant 241); 16 rows have '?' in attribute 7 (bare nuclei); the 683 complete rows split 444 / 239 = Woike's n and split.
- **Counts re-checked by the script:** `complete_rows` = 683, `class_2_benign` = 444, `class_4_malignant` = 239.
- **Decisions a build would need (not taken here):** Row policy: 16 rows with '?'. Drop the id column (54 rows repeat an earlier id, measured).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/BCW/uci-15.zip`: 86541 bytes, SHA-256 `3f91e49bceb3…`, downloaded, <https://archive.ics.uci.edu/static/public/15/breast+cancer+wisconsin+original.zip>
  - `raw/BCW/uci-15-metadata.json`: 5607 bytes, SHA-256 `ee82afd3ad87…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=15>
  - plus 8 archive members extracted byte-for-byte to `raw/BCW/extracted/`.

### 26. PIMA : Diabetes

- **Source:** OpenML: OpenML 37 'diabetes' (Pima Indians Diabetes; no longer hosted by UCI). Landing page <https://www.openml.org/d/37>.
- **Tabelle 6.9:** n = 786, cues = 6, split = 268 / 500, predictor types bin/cat/cont = 0/0/6, source tag UCI. (786 as printed; the printed split sums to 768.)
- **Criterion:** tested_positive / tested_negative; natively binary.
- **Raw data:** `raw/PIMA/diabetes.arff` (768 rows). Raw rows **768**, fields per record **9**. 9 ARFF attributes: eight numeric predictors and class. Woike used 6; which two were dropped is not stated. Zero counts (measured): skin 227, insu 374, pres 35, mass 11, plas 5.
- **Raw class counts** (last field): tested_negative: 500, tested_positive: 268.
- **Comparison with Tabelle 6.9:** n **explained**, split **exact**. 768 rows, positive 268 / negative 500 = Woike's split exactly. Tabelle 6.9 and the text print n = 786, but 268 + 500 = 768 and Woike et al. (2017) Table 1 prints 768, so 786 is a digit transposition in the dissertation, not a different file.
- **Decisions a build would need (not taken here):** Cue subset: 6 of 8. Zeros standing for missing values in several columns.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/PIMA/diabetes.arff`: 37419 bytes, SHA-256 `4eddd5b2b646…`, downloaded, <https://openml.org/data/v1/download/37/diabetes.arff>
  - `raw/PIMA/openml-37-description.json`: 4761 bytes, SHA-256 `9c5737c190ab…`, downloaded, <https://www.openml.org/api/v1/json/data/37>

### 27. AUTH : Authorship

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 841, cues = 69, split = 173 / 668, predictor types bin/cat/cont = 0/0/69, source tag ACD.
- **Criterion:** Author is Shakespeare versus not; from the four-valued column Author.
- **Raw data:** `raw/AUTH/authorship.csv` (841 rows). Raw rows **841**, fields per record **71**. 71 columns: 69 function-word counts, BookID, Author. Sixty-nine predictors.
- **Raw class counts** (column `Author`): Austen: 317, London: 296, Milton: 55, Shakespeare: 173.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 841 rows; Austen 317, London 296, Shakespeare 173, Milton 55; Shakespeare versus rest = 173/668.
- **Counts re-checked by the script:** `Shakespeare` = 173, `rest` = 668.
- **Decisions a build would need (not taken here):** Binarization Shakespeare versus rest. BookID must not be a cue (it identifies the author's books).
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/AUTH/authorship.csv`: 143447 bytes, SHA-256 `070119a49866…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/authorship.csv>

### 28. HOF : Baseball HoF

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 1320, cues = 15, split = 124 / 1196, predictor types bin/cat/cont = 0/0/15, source tag ACD.
- **Criterion:** Inducted into the Hall of Fame or not; the column has three codes (0, 1, 2).
- **Raw data:** `raw/HOF/halloffame.csv` (1340 rows). Raw rows **1340**, fields per record **18**. 18 columns: Player (identifier), 15 numeric career statistics, Position, Hall of Fame. The 15 numeric columns are Woike's 15 cues.
- **Raw class counts** (column `Hall of Fame`): 0: 1215, 1: 57, 2: 68.
- **Comparison with Tabelle 6.9:** n **explained**, split **reproduced_by_rule**. 1340 raw rows (code 0: 1215, 1: 57, 2: 68); Strikeouts is '.' (missing) in 20 rows; the 1320 complete rows split 0: 1196 versus 1 or 2: 124 = Woike's n and split.
- **Counts re-checked by the script:** `complete_rows` = 1320, `HoF=0` = 1196, `HoF=1or2` = 124.
- **Decisions a build would need (not taken here):** Row policy: 20 rows with Strikeouts missing ('.'). Merge Hall of Fame codes 1 and 2. Position (categorical) was not among Woike's cues.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/HOF/halloffame.csv`: 124317 bytes, SHA-256 `b0dc892fecd2…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/halloffame.csv>

### 29. YEAS : Yeast

- **Source:** UCI: Yeast (UCI id 110, DOI `10.24432/C5KG68`). Landing page <https://archive.ics.uci.edu/dataset/110/yeast>.
- **Tabelle 6.9:** n = 1484, cues = 8, split = 463 / 1021, predictor types bin/cat/cont = 0/0/8, source tag UCI.
- **Criterion:** Localization site 'cytosolic or cytoskeletal' (CYT) versus any other of the ten sites.
- **Raw data:** `raw/YEAS/extracted/yeast.data` (1484 rows). Raw rows **1484**, fields per record **10**. 10 whitespace-separated fields: sequence name (identifier), eight scores, localization site.
- **Raw class counts** (last field): CYT: 463, ERL: 5, EXC: 35, ME1: 44, ME2: 51, ME3: 163, MIT: 244, NUC: 429, POX: 20, VAC: 30.
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 1484 rows; CYT 463, all other sites 1021.
- **Counts re-checked by the script:** `CYT` = 463, `rest` = 1021.
- **Decisions a build would need (not taken here):** Binarization CYT versus rest. Drop the sequence-name column.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/YEAS/uci-110.zip`: 18938 bytes, SHA-256 `8fe9a4490edf…`, downloaded, <https://archive.ics.uci.edu/static/public/110/yeast.zip>
  - `raw/YEAS/uci-110-metadata.json`: 3535 bytes, SHA-256 `971a1a3647c6…`, downloaded, <https://archive.ics.uci.edu/api/dataset?id=110>
  - plus 2 archive members extracted byte-for-byte to `raw/YEAS/extracted/`.

### 30. SCOT : Supreme Court

- **Source:** ACD: Companion data to J. S. Simonoff, Analyzing Categorical Data (Springer, 2003). Landing page <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>.
- **Tabelle 6.9:** n = 4052, cues = 7, split = 170 / 3882, predictor types bin/cat/cont = 5/1/1, source tag ACD.
- **Criterion:** Whether Congress took any action in response to the decision: Actions taken is a COUNT (0-11), dichotomized.
- **Raw data:** `raw/SCOT/supreme.csv` (4052 rows). Raw rows **4052**, fields per record **8**. 8 columns: Actions taken, five binary decision attributes, Year of decision, Log exposure. Seven predictors (5/1/1 profile).
- **Comparison with Tabelle 6.9:** n **exact**, split **reproduced_by_rule**. 4052 rows; Actions taken > 0 in 170 rows, = 0 in 3882.
- **Counts re-checked by the script:** `Actions taken>0` = 170, `Actions taken=0` = 3882.
- **Decisions a build would need (not taken here):** Threshold Actions taken > 0.
- **Files obtained directly** (extracted archive members are listed in `manifest.json`):
  - `raw/SCOT/supreme.csv`: 178416 bytes, SHA-256 `61c847ceb3e4…`, downloaded, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/Comma_separated/supreme.csv>

## Shared archive

- `_ACD_bundle`: Whole-site archive of the Analyzing Categorical Data companion files (84 datasets, .csv and .xls). Kept as a cross-check: each of the eleven per-file CSVs under raw/<CODE>/ is byte-identical to the member of the same name.
  - `raw/_ACD_bundle/data.zip`: 1222422 bytes, SHA-256 `293fa5627c67…`, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/data.zip>
  - `raw/_ACD_bundle/Data_index.html`: 1346 bytes, SHA-256 `6790b4afc8f2…`, <https://pages.stern.nyu.edu/~jsimonof/AnalCatData/Data/>

## Requests that did not succeed

- `http://www.stat.ucla.edu/projects/datasets/cardiac.dat` (the location Woike cites): HTTP 404 on 2026-09-18. Replaced by the two copies described under CARD.
- `https://archive.org/wayback/available` (availability API, two queries): HTTP 429. Not retried; the capture was fetched directly from `web.archive.org` instead.
- Every other request returned HTTP 200. No dataset was substituted.

## Licensing and access

This is a research acquisition copy. UCI records display CC BY 4.0 and should be cited individually by DOI. `irish.ed` carries an ownership statement (Greaney and Kelleghan retain copyright; use as an example for research on statistical methods is permitted; StatLib may distribute it freely). Simonoff's files accompany his book; the hbiostat and OpenML copies carry their own terms. Check the current upstream terms before redistributing any raw file.
