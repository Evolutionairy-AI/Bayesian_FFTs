# Source map and per-dataset provenance

All files were retrieved on **2026-09-19** with `curl`: sequentially, without credentials, cookies or personal identifiers, and with no query parameter other than a public dataset id (the UCI metadata API takes `?id=<n>`). Full SHA-256 values, byte sizes and URLs for every file are in `manifest.json`; this file shows the first 12 hex digits only. **This file is generated** by `scripts/build_sources_md.py`; all counts in it are written by code from the files in the package.

## Source families

| Family | Files | Base URL | Notes |
|---|---|---|---|
| OpenML JSON API | suite, 51 task records, description + features + qualities for the 38 classification datasets | `https://www.openml.org/api/v1/json/{study,task,data,data/features,data/qualities}/<id>` | Public, no key. The 8 non-binary classification sets are kept under `suite/nonbinary_classification/` as evidence for the selection. |
| OpenML data files | 30 ARFF + 30 parquet | `https://openml.org/data/v1/download/<file_id>/<name>.arff`, `https://data.openml.org/datasets/0004/<id>/dataset_<id>.pq` | The URLs are the `url` and `parquet_url` fields of each description. Every ARFF's MD5 equals the `md5_checksum` OpenML publishes for it. |
| TabArena results artifact | 19 parquet files | `https://tabarena.s3.amazonaws.com/cache/artifacts/<suite>/methods/<method>/results/<file>` | Public bucket, anonymous GET. The key layout was read from the repo source (`models/_method_metadata.py`). Results tier only. |
| TabArena repo | 7 source files + LICENSE | `https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/<path>` | Pinned to the commit that was `main` at retrieval. File names encode the repo path with `__` for `/`. |
| Paper | arXiv v4 PDF and HTML, NeurIPS 2025 proceedings paper and supplement | arxiv.org, proceedings.neurips.cc | The arXiv PDF URL carries no version; the file received is v4 (stamp on page 1: 3 Nov 2025). |
| UCI metadata API | 3 JSON records | `https://archive.ics.uci.edu/api/dataset?id=<n>` | Only to document the size of the UCI parents of three sets the curators reduced (365, 722, 296). |

## The 30 datasets

### 1. Amazon_employee_access

- **OpenML:** dataset 46905 (version 3, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:53:54); task 363613; target `ResourceApproved`. <https://www.openml.org/d/46905>
- **Licence as displayed by OpenML:** Public Domain. **Original source as displayed:** https://www.kaggle.com/c/amazon-employee-access-challenge
- **Citation as displayed:** Ben Hamner, kenmonta, and Will Cukierski. Amazon.com - Employee Access Challenge. https://kaggle.com/competitions/amazon-employee-access-challenge, 2013. Kaggle.
- **Repo metadata:** source Kaggle, dataset year 2010.
- **Measured from the ARFF:** 32,769 rows; 10 columns including the target (0 numeric, 10 nominal, 0 string); 0 missing cells; classes No=1897, Yes=30872. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/Amazon_employee_access/Amazon_employee_access.arff`: 2,215,094 bytes, SHA-256 `6b6494c6d49b...`, <https://openml.org/data/v1/download/22125216/Amazon_employee_access.arff>
  - `raw/Amazon_employee_access/dataset_46905.pq`: 438,403 bytes, SHA-256 `d1be0e14e9f4...`, <https://data.openml.org/datasets/0004/46905/dataset_46905.pq>
  - `raw/Amazon_employee_access/openml_description_46905.json`: 2,356 bytes, SHA-256 `3f50a630b579...`, <https://www.openml.org/api/v1/json/data/46905>
  - `raw/Amazon_employee_access/openml_features_46905.json`: 129,491 bytes, SHA-256 `6238986ab8c0...`, <https://www.openml.org/api/v1/json/data/features/46905>
  - `raw/Amazon_employee_access/openml_qualities_46905.json`: 1,026 bytes, SHA-256 `6a05d415ba18...`, <https://www.openml.org/api/v1/json/data/qualities/46905>
- **Curators' comments (verbatim from the OpenML description):**
  - "We only use the training data from Kaggle."
  - "Anomaly: the data might contain sub-groups related to managers and resources."
  - "Anomaly: likely, similar to the test data, each sample represents a unique employee."
- **Relation to the better-known original:** ROWS: Kaggle training file only.
- **Decisions a build would need:**
  - Positive class: the target `ResourceApproved` has the labels No=1897 / Yes=30872; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - High-cardinality categoricals (> 50 observed values): RESOURCE=7518, MGR_ID=4243, ROLE_ROLLUP_1=128, ROLE_ROLLUP_2=177, ROLE_DEPTNAME=449, ROLE_TITLE=343, ROLE_FAMILY_DESC=2358, ROLE_FAMILY=67, ROLE_CODE=343. A binary cue needs a grouping rule, or the column is dropped.
  - Identifier-like names: MGR_ID.
  - Redundancy (by name, NOT measured): ROLE_TITLE and ROLE_CODE both declare 343 values.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363613 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 2. APSFailure

- **OpenML:** dataset 46908 (version 2, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:54:32); task 363616; target `AirPressureSystemFailure`. <https://www.openml.org/d/46908>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5V60Q
- **Citation as displayed:** IDA2016Challenge [Dataset]. (2016). UCI Machine Learning Repository. https://doi.org/10.24432/C5V60Q.
- **Repo metadata:** source UCI, dataset year 2016.
- **Measured from the ARFF:** 76,000 rows; 171 columns including the target (170 numeric, 1 nominal, 0 string); 1,078,695 missing cells; classes neg=74625, pos=1375. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/APSFailure/APSFailure.arff`: 78,323,905 bytes, SHA-256 `14fd7b78bb6d...`, <https://openml.org/data/v1/download/22125219/APSFailure.arff>
  - `raw/APSFailure/dataset_46908.pq`: 35,142,382 bytes, SHA-256 `b43f3448ca33...`, <https://data.openml.org/datasets/0004/46908/dataset_46908.pq>
  - `raw/APSFailure/openml_description_46908.json`: 2,383 bytes, SHA-256 `d18d6442b145...`, <https://www.openml.org/api/v1/json/data/46908>
  - `raw/APSFailure/openml_features_46908.json`: 26,564 bytes, SHA-256 `9eca576ecb3b...`, <https://www.openml.org/api/v1/json/data/features/46908>
  - `raw/APSFailure/openml_qualities_46908.json`: 1,095 bytes, SHA-256 `e00f612ef409...`, <https://www.openml.org/api/v1/json/data/qualities/46908>
- **Curators' comments (verbatim from the OpenML description):**
  - "We combined the original training and testing data into a single dataset."
  - "We renamed the target feature to "AirPressureSystemFailure"."
  - "We converted "na" strings to real NaN/missing values, making the data numeric."
  - "Anomaly: we cannot determine the data types of the features."
  - "Anomaly: some features are bins of histograms (see original data description)."
  - "Anomaly: the original task used a cost matrix for evaluation."
- **Relation to the better-known original:** ROWS: original training and test files combined; 'na' strings turned into missing values.
- **Decisions a build would need:**
  - Positive class: the target `AirPressureSystemFailure` has the labels neg=74625 / pos=1375; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 1,078,695 cells in 169 columns and 75,244 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Constant columns (one observed value): cd_000.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363616 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 3. bank-marketing

- **OpenML:** dataset 46910 (version 10, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:54:48); task 363618; target `SubscribeTermDeposit`. <https://www.openml.org/d/46910>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5K306
- **Citation as displayed:** Moro, Sergio, Paulo Cortez, and Paulo Rita. 'A data-driven approach to predict the success of bank telemarketing.' Decision Support Systems 62 (2014): 22-31. https://doi.org/10.1016/j.dss.2014.03.001
- **Repo metadata:** source UCI, dataset year 2012.
- **Measured from the ARFF:** 45,211 rows; 14 columns including the target (5 numeric, 8 nominal, 1 string); 0 missing cells; classes no=39922, yes=5289. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/bank-marketing/bank-marketing.arff`: 3,233,844 bytes, SHA-256 `fe21d939814f...`, <https://openml.org/data/v1/download/22125221/bank-marketing.arff>
  - `raw/bank-marketing/dataset_46910.pq`: 320,466 bytes, SHA-256 `6ff0f63c357e...`, <https://data.openml.org/datasets/0004/46910/dataset_46910.pq>
  - `raw/bank-marketing/openml_description_46910.json`: 2,420 bytes, SHA-256 `c458b4215621...`, <https://www.openml.org/api/v1/json/data/46910>
  - `raw/bank-marketing/openml_features_46910.json`: 2,606 bytes, SHA-256 `37b1adce2d95...`, <https://www.openml.org/api/v1/json/data/features/46910>
  - `raw/bank-marketing/openml_qualities_46910.json`: 1,068 bytes, SHA-256 `850114c9dcf8...`, <https://www.openml.org/api/v1/json/data/qualities/46910>
- **Curators' comments (verbatim from the OpenML description):**
  - "We removed the "duration" feature following its original description to obtain a "realistic predictive model"."
  - "We further remove the "month" and "day_of_week" features, as they also relate to the last contact -- which is not available in a real-world scenario."
- **Relation to the better-known original:** COLUMNS: duration, month and day_of_week removed by the curators.
- **Decisions a build would need:**
  - Positive class: the target `SubscribeTermDeposit` has the labels no=39922 / yes=5289; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Pseudo-missing literals: 4 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - STRING-typed columns: poutcome. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Leakage candidates (read off names and documentation, NOT measured): campaign (number of contacts in the current campaign, known only once the campaign is over); the curators already removed duration, month and day_of_week for this reason.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363618 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 4. Bank_Customer_Churn

- **OpenML:** dataset 46911 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:55:01); task 363619; target `churn`. <https://www.openml.org/d/46911>
- **Licence as displayed by OpenML:** Public. **Original source as displayed:** https://www.kaggle.com/datasets/gauravtopre/bank-customer-churn-dataset
- **Citation as displayed:** Topre, Gaurav. 'Bank Customer Churn Dataset.' Kaggle, 2022, https://www.kaggle.com/datasets/gauravtopre/bank-customer-churn-dataset.
- **Repo metadata:** source Kaggle, dataset year 2020.
- **Measured from the ARFF:** 10,000 rows; 11 columns including the target (6 numeric, 5 nominal, 0 string); 0 missing cells; classes No=7963, Yes=2037. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/Bank_Customer_Churn/Bank_Customer_Churn.arff`: 482,669 bytes, SHA-256 `88fcfc1f7709...`, <https://openml.org/data/v1/download/22125222/Bank_Customer_Churn.arff>
  - `raw/Bank_Customer_Churn/dataset_46911.pq`: 174,754 bytes, SHA-256 `6f3d4f9bd184...`, <https://data.openml.org/datasets/0004/46911/dataset_46911.pq>
  - `raw/Bank_Customer_Churn/openml_description_46911.json`: 2,183 bytes, SHA-256 `32e2ce0ca0a7...`, <https://www.openml.org/api/v1/json/data/46911>
  - `raw/Bank_Customer_Churn/openml_features_46911.json`: 1,887 bytes, SHA-256 `74a8293481a8...`, <https://www.openml.org/api/v1/json/data/features/46911>
  - `raw/Bank_Customer_Churn/openml_qualities_46911.json`: 1,039 bytes, SHA-256 `719bbbc8e0f6...`, <https://www.openml.org/api/v1/json/data/qualities/46911>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the values of the target variable to be more meaningful."
  - "We dropped the ID column."
- **Relation to the better-known original:** COLUMNS: ID column dropped.
- **Decisions a build would need:**
  - Positive class: the target `churn` has the labels No=7963 / Yes=2037; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363619 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 5. Bioresponse

- **OpenML:** dataset 46912 (version 4, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:55:15); task 363620; target `MoleculeElicitsResponse`. <https://www.openml.org/d/46912>
- **Licence as displayed by OpenML:** Public Domain. **Original source as displayed:** https://www.kaggle.com/c/bioresponse
- **Citation as displayed:** Ben Hamner, dcthompson, and Jorg. Predicting a Biological Response. https://kaggle.com/competitions/bioresponse, 2012. Kaggle.
- **Repo metadata:** source Kaggle, dataset year 2012.
- **Measured from the ARFF:** 3,751 rows; 1777 columns including the target (1776 numeric, 1 nominal, 0 string); 0 missing cells; classes No=1717, Yes=2034. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: False.
- **Files:**
  - `raw/Bioresponse/Bioresponse.arff`: 23,970,797 bytes, SHA-256 `cae8d700c08b...`, <https://openml.org/data/v1/download/22125223/Bioresponse.arff>
  - `raw/Bioresponse/dataset_46912.pq`: 3,795,277 bytes, SHA-256 `44ec2028029f...`, <https://data.openml.org/datasets/0004/46912/dataset_46912.pq>
  - `raw/Bioresponse/openml_description_46912.json`: 2,256 bytes, SHA-256 `35f60fa87cd8...`, <https://www.openml.org/api/v1/json/data/46912>
  - `raw/Bioresponse/openml_features_46912.json`: 269,741 bytes, SHA-256 `1d6dc7b4bb0d...`, <https://www.openml.org/api/v1/json/data/features/46912>
  - `raw/Bioresponse/openml_qualities_46912.json`: 1,073 bytes, SHA-256 `7adfdfe09d67...`, <https://www.openml.org/api/v1/json/data/qualities/46912>
- **Curators' comments (verbatim from the OpenML description):**
  - "We only use the training data from Kaggle."
  - "Anomaly: all feature represent molecular descriptors but we do not have more semantic information."
  - "Anomaly: a large amount of the features (D953-D1776) are sparsely binary encoded variables."
- **Relation to the better-known original:** ROWS: Kaggle training file only.
- **Decisions a build would need:**
  - Positive class: the target `MoleculeElicitsResponse` has the labels No=1717 / Yes=2034; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - 1776 features: cue search cost and any pre-selection rule need to be fixed in advance.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363620 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 6. blood-transfusion-service-center

- **OpenML:** dataset 46913 (version 2, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T19:55:21); task 363621; target `DonatedBloodInMarch2007`. <https://www.openml.org/d/46913>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5GS39
- **Citation as displayed:** Yeh, I-Cheng, King-Jang Yang, and Tao-Ming Ting. 'Knowledge discovery on RFM model using Bernoulli sequence.' Expert Systems with applications 36.3 (2009): 5866-5871. https://doi.org/10.1016/j.eswa.2008.07.018
- **Repo metadata:** source UCI, dataset year 2008.
- **Measured from the ARFF:** 748 rows; 5 columns including the target (4 numeric, 1 nominal, 0 string); 0 missing cells; classes No=570, Yes=178. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/blood-transfusion-service-center/blood-transfusion-service-center.arff`: 12,921 bytes, SHA-256 `80945cb11b50...`, <https://openml.org/data/v1/download/22125224/blood-transfusion-service-center.arff>
  - `raw/blood-transfusion-service-center/dataset_46913.pq`: 7,858 bytes, SHA-256 `8e9fecb0a04a...`, <https://data.openml.org/datasets/0004/46913/dataset_46913.pq>
  - `raw/blood-transfusion-service-center/openml_description_46913.json`: 2,354 bytes, SHA-256 `4b922b3596aa...`, <https://www.openml.org/api/v1/json/data/46913>
  - `raw/blood-transfusion-service-center/openml_features_46913.json`: 888 bytes, SHA-256 `68b1424a0a46...`, <https://www.openml.org/api/v1/json/data/features/46913>
  - `raw/blood-transfusion-service-center/openml_qualities_46913.json`: 1,022 bytes, SHA-256 `8d86b2530a94...`, <https://www.openml.org/api/v1/json/data/qualities/46913>
- **Curators' comments (verbatim from the OpenML description):**
  - "We made feature names more descriptive."
  - "Anomaly: the data has a lot of duplicates (29%) and several duplicates with different target values."
- **Relation to the better-known original:** CODING: features renamed only (curators note 29% duplicate rows).
- **Decisions a build would need:**
  - Positive class: the target `DonatedBloodInMarch2007` has the labels No=570 / Yes=178; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363621 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 7. churn

- **OpenML:** dataset 46915 (version 4, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:15:23); task 363623; target `CustomerChurned`. <https://www.openml.org/d/46915>
- **Licence as displayed by OpenML:** MIT License. **Original source as displayed:** See Description
- **Citation as displayed:** Marcoulides, George A. 'Discovering Knowledge in Data: an Introduction to Data Mining.' (2005): 1465-1465. https://www.tandfonline.com/doi/abs/10.1198/jasa.2005.s61
- **Repo metadata:** source OpenML, dataset year 2005.
- **Measured from the ARFF:** 5,000 rows; 20 columns including the target (15 numeric, 5 nominal, 0 string); 0 missing cells; classes No=4293, Yes=707. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/churn/churn.arff`: 475,249 bytes, SHA-256 `87bc2dd76e08...`, <https://openml.org/data/v1/download/22125226/churn.arff>
  - `raw/churn/dataset_46915.pq`: 149,708 bytes, SHA-256 `22960d2796ac...`, <https://data.openml.org/datasets/0004/46915/dataset_46915.pq>
  - `raw/churn/openml_description_46915.json`: 2,294 bytes, SHA-256 `8edb52ca0401...`, <https://www.openml.org/api/v1/json/data/46915>
  - `raw/churn/openml_features_46915.json`: 3,653 bytes, SHA-256 `2c881df0eaf6...`, <https://www.openml.org/api/v1/json/data/features/46915>
  - `raw/churn/openml_qualities_46915.json`: 985 bytes, SHA-256 `b390f6d1137f...`, <https://www.openml.org/api/v1/json/data/qualities/46915>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the target variable to "CustomerChurned"."
  - "We dropped the "phone_number" feature as it seems to be an index in the original data."
- **Relation to the better-known original:** COLUMNS: phone_number dropped. Original source lost; curators point to PMLB and OpenML 40701.
- **Decisions a build would need:**
  - Positive class: the target `CustomerChurned` has the labels No=4293 / Yes=707; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - High-cardinality categoricals (> 50 observed values): state=51. A binary cue needs a grouping rule, or the column is dropped.
  - Redundancy (by name, NOT measured): total_*_charge columns sit beside total_*_minutes columns (by name, a tariff multiple).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363623 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 8. coil2000_insurance_policies

- **OpenML:** dataset 46916 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:15:30); task 363624; target `MobileHomePolicy`. <https://www.openml.org/d/46916>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5630S
- **Citation as displayed:** Van Der Putten, Peter, and Maarten van Someren. CoIL challenge 2000: The insurance company case. Technical Report 200009, Leiden Institute of Advanced Computer Science, Universiteit van Leiden. Available from:< http://www. liacs. nl/putten/library/cc2000, 2000.
- **Repo metadata:** source UCI, dataset year 2000.
- **Measured from the ARFF:** 9,822 rows; 86 columns including the target (80 numeric, 4 nominal, 2 string); 0 missing cells; classes No=9236, Yes=586. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/coil2000_insurance_policies/coil2000_insurance_policies.arff`: 2,357,766 bytes, SHA-256 `a541ed40161a...`, <https://openml.org/data/v1/download/22125227/coil2000_insurance_policies.arff>
  - `raw/coil2000_insurance_policies/dataset_46916.pq`: 304,980 bytes, SHA-256 `0ee5db0a9913...`, <https://data.openml.org/datasets/0004/46916/dataset_46916.pq>
  - `raw/coil2000_insurance_policies/openml_description_46916.json`: 2,543 bytes, SHA-256 `277b0c91aa34...`, <https://www.openml.org/api/v1/json/data/46916>
  - `raw/coil2000_insurance_policies/openml_features_46916.json`: 15,795 bytes, SHA-256 `97664094042c...`, <https://www.openml.org/api/v1/json/data/features/46916>
  - `raw/coil2000_insurance_policies/openml_qualities_46916.json`: 1,064 bytes, SHA-256 `56bf029cd476...`, <https://www.openml.org/api/v1/json/data/qualities/46916>
- **Curators' comments (verbatim from the OpenML description):**
  - "We created semantic meaningful names for the features."
  - "We combined the original training and validation data into one new dataset."
  - "We reversed the ordinal encoding of the original data where possible."
  - "Anomaly: the data has 15% duplicates."
- **Relation to the better-known original:** ROWS+CODING: original training and validation data combined; ordinal codes turned back into labels where possible.
- **Decisions a build would need:**
  - Positive class: the target `MobileHomePolicy` has the labels No=9236 / Yes=586; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - STRING-typed columns: avgAge, contributionPrivateThirdPartyInsurance. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363624 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 9. credit-g

- **OpenML:** dataset 46918 (version 5, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:15:41); task 363626; target `good_or_bad_customer`. <https://www.openml.org/d/46918>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5NC77
- **Citation as displayed:** Hofmann, H. (1994). Statlog (German Credit Data) [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5NC77.
- **Repo metadata:** source UCI, dataset year 1994.
- **Measured from the ARFF:** 1,000 rows; 21 columns including the target (7 numeric, 14 nominal, 0 string); 0 missing cells; classes bad=300, good=700. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/credit-g/credit-g.arff`: 242,375 bytes, SHA-256 `6149f09b7aee...`, <https://openml.org/data/v1/download/22125229/credit-g.arff>
  - `raw/credit-g/dataset_46918.pq`: 29,802 bytes, SHA-256 `bb071acb2647...`, <https://data.openml.org/datasets/0004/46918/dataset_46918.pq>
  - `raw/credit-g/openml_description_46918.json`: 2,095 bytes, SHA-256 `6c9ead02448e...`, <https://www.openml.org/api/v1/json/data/46918>
  - `raw/credit-g/openml_features_46918.json`: 4,730 bytes, SHA-256 `394b9356cba9...`, <https://www.openml.org/api/v1/json/data/features/46918>
  - `raw/credit-g/openml_qualities_46918.json`: 1,022 bytes, SHA-256 `7ba4b2cf736f...`, <https://www.openml.org/api/v1/json/data/qualities/46918>
- **Curators' comments (verbatim from the OpenML description):**
  - "We revered the original ordinal encoding."
  - "Anomaly: the original task used a cost matrix for evaluation."
- **Relation to the better-known original:** CODING: the original ordinal encoding reversed into labels (Statlog German Credit).
- **Decisions a build would need:**
  - Positive class: the target `good_or_bad_customer` has the labels bad=300 / good=700; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Pseudo-missing literals: 3 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363626 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 10. credit_card_clients_default

- **OpenML:** dataset 46919 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:15:48); task 363627; target `DefaultOnPaymentNextMonth`. <https://www.openml.org/d/46919>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C55S3H
- **Citation as displayed:** Yeh, I-Cheng, and Che-hui Lien. 'The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients.' Expert systems with applications 36.2 (2009): 2473-2480. https://doi.org/10.1016/j.eswa.2007.12.020
- **Repo metadata:** source UCI, dataset year 2009.
- **Measured from the ARFF:** 30,000 rows; 24 columns including the target (20 numeric, 4 nominal, 0 string); 0 missing cells; classes No=23364, Yes=6636. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/credit_card_clients_default/credit_card_clients_default.arff`: 2,736,789 bytes, SHA-256 `9cabdf980c80...`, <https://openml.org/data/v1/download/22125230/credit_card_clients_default.arff>
  - `raw/credit_card_clients_default/dataset_46919.pq`: 1,587,743 bytes, SHA-256 `b49c5ab1e36d...`, <https://data.openml.org/datasets/0004/46919/dataset_46919.pq>
  - `raw/credit_card_clients_default/openml_description_46919.json`: 2,459 bytes, SHA-256 `cd16e2487073...`, <https://www.openml.org/api/v1/json/data/46919>
  - `raw/credit_card_clients_default/openml_features_46919.json`: 3,848 bytes, SHA-256 `08cc1d911601...`, <https://www.openml.org/api/v1/json/data/features/46919>
  - `raw/credit_card_clients_default/openml_qualities_46919.json`: 1,041 bytes, SHA-256 `b78601496ad2...`, <https://www.openml.org/api/v1/json/data/qualities/46919>
- **Curators' comments (verbatim from the OpenML description):**
  - "We rename the target variable and restore the original class names."
  - "We drop the "ID" column."
  - "Anomaly: the data has temporal features but the task is time-invariant."
- **Relation to the better-known original:** COLUMNS: ID column dropped; class names restored.
- **Decisions a build would need:**
  - Positive class: the target `DefaultOnPaymentNextMonth` has the labels No=23364 / Yes=6636; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363627 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 11. customer_satisfaction_in_airline

- **OpenML:** dataset 46920 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:16:00); task 363628; target `satisfaction`. <https://www.openml.org/d/46920>
- **Licence as displayed by OpenML:** CC0: Public Domain. **Original source as displayed:** https://www.kaggle.com/datasets/yakhyojon/customer-satisfaction-in-airline
- **Citation as displayed:** Kaggle User Yakhyojon. 'Customer Satisfaction in Airline.' Kaggle, 2023, https://www.kaggle.com/datasets/yakhyojon/customer-satisfaction-in-airline.
- **Repo metadata:** source Kaggle, dataset year 2023.
- **Measured from the ARFF:** 129,880 rows; 22 columns including the target (5 numeric, 17 nominal, 0 string); 393 missing cells; classes dissatisfied=58793, satisfied=71087. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/customer_satisfaction_in_airline/customer_satisfaction_in_airline.arff`: 12,501,030 bytes, SHA-256 `89caa5fa6151...`, <https://openml.org/data/v1/download/22125231/customer_satisfaction_in_airline.arff>
  - `raw/customer_satisfaction_in_airline/dataset_46920.pq`: 1,387,320 bytes, SHA-256 `fe1e17384dba...`, <https://data.openml.org/datasets/0004/46920/dataset_46920.pq>
  - `raw/customer_satisfaction_in_airline/openml_description_46920.json`: 2,251 bytes, SHA-256 `9b66b61e47ea...`, <https://www.openml.org/api/v1/json/data/46920>
  - `raw/customer_satisfaction_in_airline/openml_features_46920.json`: 4,297 bytes, SHA-256 `89b74c4b25e2...`, <https://www.openml.org/api/v1/json/data/features/46920>
  - `raw/customer_satisfaction_in_airline/openml_qualities_46920.json`: 1,107 bytes, SHA-256 `5de5317fd684...`, <https://www.openml.org/api/v1/json/data/qualities/46920>
- **Curators' comments (verbatim from the OpenML description):**
  - "We removed whitespaces and special characters from the feature names."
- **Decisions a build would need:**
  - Positive class: the target `satisfaction` has the labels dissatisfied=58793 / satisfied=71087; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 393 cells in 1 columns and 393 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - More than 100,000 rows: decide whether the harness runs on all rows or on a documented subsample.
  - Leakage candidates (read off names and documentation, NOT measured): the 14 service-rating columns Seatcomfort ... Onlineboarding (answers from the same passenger survey that yields the target satisfaction).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363628 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 12. diabetes

- **OpenML:** dataset 46921 (version 7, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:16:05); task 363629; target `TestedPositiveForDiabetes`. <https://www.openml.org/d/46921>
- **Licence as displayed by OpenML:** CC0: Public Domain. **Original source as displayed:** See Description
- **Citation as displayed:** Smith, Jack W., et al. 'Using the ADAP learning algorithm to forecast the onset of diabetes mellitus.' Proceedings of the annual symposium on computer application in medical care. 1988. https://pmc.ncbi.nlm.nih.gov/articles/PMC2245318/
- **Repo metadata:** source OpenML, dataset year 1988.
- **Measured from the ARFF:** 768 rows; 9 columns including the target (8 numeric, 1 nominal, 0 string); 0 missing cells; classes No=500, Yes=268. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/diabetes/diabetes.arff`: 25,945 bytes, SHA-256 `a6e55bf62d63...`, <https://openml.org/data/v1/download/22125232/diabetes.arff>
  - `raw/diabetes/dataset_46921.pq`: 17,939 bytes, SHA-256 `4bd1b10df159...`, <https://data.openml.org/datasets/0004/46921/dataset_46921.pq>
  - `raw/diabetes/openml_description_46921.json`: 2,488 bytes, SHA-256 `fb44f16d3c6f...`, <https://www.openml.org/api/v1/json/data/46921>
  - `raw/diabetes/openml_features_46921.json`: 1,470 bytes, SHA-256 `eed90e840ed9...`, <https://www.openml.org/api/v1/json/data/features/46921>
  - `raw/diabetes/openml_qualities_46921.json`: 1,049 bytes, SHA-256 `d11f39f278be...`, <https://www.openml.org/api/v1/json/data/qualities/46921>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the class variable "Outcome" to "TestedPositiveForDiabetes" and replaced 1 with yes, and 0 with no."
- **Relation to the better-known original:** SAME DATA AS AN EARLIER COLLECTION: this is the Pima Indians Diabetes set (OpenML 37 with the target renamed), already held as PIMA in DATA_SETS/MKW08-30.
- **Decisions a build would need:**
  - Positive class: the target `TestedPositiveForDiabetes` has the labels No=500 / Yes=268; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363629 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 13. Diabetes130US

- **OpenML:** dataset 46922 (version 4, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:16:21); task 363630; target `EarlyReadmission`. <https://www.openml.org/d/46922>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5230J
- **Citation as displayed:** Strack, Beata, et al. 'Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records.' BioMed research international 2014.1 (2014): 781670. https://doi.org/10.1155/2014/781670
- **Repo metadata:** source UCI, dataset year 2014.
- **Measured from the ARFF:** 71,518 rows; 48 columns including the target (8 numeric, 40 nominal, 0 string); 137,663 missing cells; classes No=65225, Yes=6293. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/Diabetes130US/Diabetes130US.arff`: 15,535,457 bytes, SHA-256 `74d17c07b833...`, <https://openml.org/data/v1/download/22125233/Diabetes130US.arff>
  - `raw/Diabetes130US/dataset_46922.pq`: 999,825 bytes, SHA-256 `ef4db493d524...`, <https://data.openml.org/datasets/0004/46922/dataset_46922.pq>
  - `raw/Diabetes130US/openml_description_46922.json`: 3,129 bytes, SHA-256 `69a1e1f8068e...`, <https://www.openml.org/api/v1/json/data/46922>
  - `raw/Diabetes130US/openml_features_46922.json`: 25,891 bytes, SHA-256 `2de5031fffff...`, <https://www.openml.org/api/v1/json/data/features/46922>
  - `raw/Diabetes130US/openml_qualities_46922.json`: 1,105 bytes, SHA-256 `7ccff28142bf...`, <https://www.openml.org/api/v1/json/data/qualities/46922>
- **Curators' comments (verbatim from the OpenML description):**
  - "We drop duplicated patients based on the "patient_nbr" feature to avoid target leakage."
  - "We reversed the original ordinal encoding for three ID-based features."
  - "We created the target from the "readmitted" column following the original task description."
  - "We dropped "encounter_id" and "patient_nbr", which are both unique identifiers for each row."
  - "We keep original "?", NULL-codes, and NaN values because they exist in different ways across the columns."
  - "Anomaly: There is a distribution shift based on the original order. The reason for this might be that the encounters are ordered in some way such that later parts of the data contain different sub-groups than earlier parts. This is also indicate by the fact that the "payer_code" feature is responsible for the shift. This distribution shift vanishes after randomly shuffling the data (as done by default for this and all other datasets used in TabArena)."
- **Relation to the better-known original:** ROWS+TARGET: one encounter per patient kept; encounter_id and patient_nbr dropped; binary target built from 'readmitted'. UCI record 296 reports 101,766 instances (UCI API).
- **Decisions a build would need:**
  - Positive class: the target `EarlyReadmission` has the labels No=65225 / Yes=6293; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 137,663 cells in 7 columns and 70,601 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Pseudo-missing literals: 5 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - High-cardinality categoricals (> 50 observed values): medical_specialty=70, diag_1=696, diag_2=725, diag_3=758. A binary cue needs a grouping rule, or the column is dropped.
  - Constant columns (one observed value): examide, citoglipton, glimepiride-pioglitazone.
  - Identifier-like names: admission_type_id, discharge_disposition_id, admission_source_id.
  - Leakage candidates (read off names and documentation, NOT measured): discharge_disposition_id (its categories include 'Expired' and hospice discharges, after which an early readmission cannot occur).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363630 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 14. E-CommereShippingData

- **OpenML:** dataset 46924 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:16:35); task 363632; target `ArrivedLate`. <https://www.openml.org/d/46924>
- **Licence as displayed by OpenML:** Public Domain. **Original source as displayed:** https://www.kaggle.com/datasets/prachi13/customer-analytics
- **Citation as displayed:** Prachi Gopalani. 'E-Commerce Shipping Data.' Kaggle, 2021, https://www.kaggle.com/datasets/prachi13/customer-analytics.
- **Repo metadata:** source Kaggle, dataset year 2021.
- **Measured from the ARFF:** 10,999 rows; 11 columns including the target (6 numeric, 5 nominal, 0 string); 0 missing cells; classes No=4436, Yes=6563. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/E-CommereShippingData/E-CommereShippingData.arff`: 393,860 bytes, SHA-256 `2cfe74fbc7ff...`, <https://openml.org/data/v1/download/22125235/E-CommereShippingData.arff>
  - `raw/E-CommereShippingData/dataset_46924.pq`: 88,617 bytes, SHA-256 `a66d12fb5452...`, <https://data.openml.org/datasets/0004/46924/dataset_46924.pq>
  - `raw/E-CommereShippingData/openml_description_46924.json`: 2,473 bytes, SHA-256 `e8dfbc1c1b22...`, <https://www.openml.org/api/v1/json/data/46924>
  - `raw/E-CommereShippingData/openml_features_46924.json`: 1,963 bytes, SHA-256 `370eb7249862...`, <https://www.openml.org/api/v1/json/data/features/46924>
  - `raw/E-CommereShippingData/openml_qualities_46924.json`: 1,066 bytes, SHA-256 `43780fc5ed69...`, <https://www.openml.org/api/v1/json/data/qualities/46924>
- **Curators' comments (verbatim from the OpenML description):**
  - "We dropped the ID column."
  - "We renamed the target feature and its values to be more meaningful."
  - "Anomaly: the target and task seems somewhat disconnected from the features. Moreover, some source information on the data is missing and there might be some translation issues."
  - "Anomaly: there might be some data issues related to "Warehouse_block" and the value "F" consisting of two block "E" and "F"."
- **Relation to the better-known original:** COLUMNS: ID column dropped.
- **Decisions a build would need:**
  - Positive class: the target `ArrivedLate` has the labels No=4436 / Yes=6563; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Leakage candidates (read off names and documentation, NOT measured): Discount_offered (UNVERIFIED recollection of public discussion of this Kaggle set; the curators note that 'the target and task seems somewhat disconnected from the features').
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363632 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 15. Fitness_Club

- **OpenML:** dataset 46927 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:16:53); task 363671; target `attended`. <https://www.openml.org/d/46927>
- **Licence as displayed by OpenML:** Public Domain. **Original source as displayed:** https://www.kaggle.com/datasets/ddosad/datacamps-data-science-associate-certification
- **Citation as displayed:** Kaggle User Ddosad. 'Fitness Club Dataset for ML Classification.' Kaggle, 2023, https://www.kaggle.com/datasets/ddosad/datacamps-data-science-associate-certification.
- **Repo metadata:** source Kaggle, dataset year 2023.
- **Measured from the ARFF:** 1,500 rows; 7 columns including the target (3 numeric, 4 nominal, 0 string); 20 missing cells; classes No=1046, Yes=454. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/Fitness_Club/Fitness_Club.arff`: 43,343 bytes, SHA-256 `890a327d1e00...`, <https://openml.org/data/v1/download/22125238/Fitness_Club.arff>
  - `raw/Fitness_Club/dataset_46927.pq`: 17,741 bytes, SHA-256 `24ad1662eeaa...`, <https://data.openml.org/datasets/0004/46927/dataset_46927.pq>
  - `raw/Fitness_Club/openml_description_46927.json`: 2,504 bytes, SHA-256 `9d1e7c98ee4a...`, <https://www.openml.org/api/v1/json/data/46927>
  - `raw/Fitness_Club/openml_features_46927.json`: 1,291 bytes, SHA-256 `d3f492075303...`, <https://www.openml.org/api/v1/json/data/features/46927>
  - `raw/Fitness_Club/openml_qualities_46927.json`: 1,096 bytes, SHA-256 `c83aae39d143...`, <https://www.openml.org/api/v1/json/data/qualities/46927>
- **Curators' comments (verbatim from the OpenML description):**
  - "We dropped the ID column."
  - "We renamed the values of the target variable to be more meaningful."
  - "We treat "-0" values as "0" values for the target, following the description."
  - "We removed trailing words (like "days") from "days_before"."
  - "We aligned the naming of "day_of_week" to be consistent per day."
- **Relation to the better-known original:** COLUMNS+CODING: ID column dropped; days_before and day_of_week cleaned; target '-0' read as '0'.
- **Decisions a build would need:**
  - Positive class: the target `attended` has the labels No=1046 / Yes=454; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 20 cells in 1 columns and 20 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363671 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 16. GiveMeSomeCredit

- **OpenML:** dataset 46929 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:17:08); task 363673; target `FinancialDistressNextTwoYears`. <https://www.openml.org/d/46929>
- **Licence as displayed by OpenML:** Public. **Original source as displayed:** https://www.kaggle.com/competitions/GiveMeSomeCredit
- **Citation as displayed:** Credit Fusion and Will Cukierski. Give Me Some Credit. https://kaggle.com/competitions/GiveMeSomeCredit, 2011. Kaggle.
- **Repo metadata:** source Kaggle, dataset year 2011.
- **Measured from the ARFF:** 150,000 rows; 11 columns including the target (10 numeric, 1 nominal, 0 string); 33,655 missing cells; classes No=139974, Yes=10026. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/GiveMeSomeCredit/GiveMeSomeCredit.arff`: 7,226,796 bytes, SHA-256 `92c897782a04...`, <https://openml.org/data/v1/download/22125240/GiveMeSomeCredit.arff>
  - `raw/GiveMeSomeCredit/dataset_46929.pq`: 3,343,752 bytes, SHA-256 `bd4eeb5341b1...`, <https://data.openml.org/datasets/0004/46929/dataset_46929.pq>
  - `raw/GiveMeSomeCredit/openml_description_46929.json`: 2,102 bytes, SHA-256 `7b03d2cc5e67...`, <https://www.openml.org/api/v1/json/data/46929>
  - `raw/GiveMeSomeCredit/openml_features_46929.json`: 1,924 bytes, SHA-256 `cc76590257a4...`, <https://www.openml.org/api/v1/json/data/features/46929>
  - `raw/GiveMeSomeCredit/openml_qualities_46929.json`: 1,093 bytes, SHA-256 `d3b796feeba3...`, <https://www.openml.org/api/v1/json/data/qualities/46929>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the target feature and its value to be more descriptive."
- **Decisions a build would need:**
  - Positive class: the target `FinancialDistressNextTwoYears` has the labels No=139974 / Yes=10026; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 33,655 cells in 2 columns and 29,731 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - More than 100,000 rows: decide whether the harness runs on all rows or on a documented subsample.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363673 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 17. hazelnut-spread-contaminant-detection

- **OpenML:** dataset 46930 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:17:13); task 363674; target `Contaminated`. <https://www.openml.org/d/46930>
- **Licence as displayed by OpenML:** CC BY-SA. **Original source as displayed:** https://www.openml.org/search?type=data&status=active&id=45538
- **Citation as displayed:** Ricci, Marco, et al. 'Machine-learning-based microwave sensing: A case study for the food industry.' IEEE Journal on Emerging and Selected Topics in Circuits and Systems 11.3 (2021): 503-514. https://doi.org/10.1109/JETCAS.2021.3097699; Urbinati, Luca, et al. 'A machine-learning based microwave sensing approach to food contaminant detection.' 2020 IEEE International Symposium on Circuits and Systems (ISCAS). IEEE, 2020. https://doi.org/10.1109/ISCAS45731.2020.9181293
- **Repo metadata:** source OpenML, dataset year 2020.
- **Measured from the ARFF:** 2,400 rows; 31 columns including the target (30 numeric, 1 nominal, 0 string); 0 missing cells; classes 0=1200, 1=1200. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/hazelnut-spread-contaminant-detection/hazelnut-spread-contaminant-detection.arff`: 686,161 bytes, SHA-256 `79b224319a1c...`, <https://openml.org/data/v1/download/22125241/hazelnut-spread-contaminant-detection.arff>
  - `raw/hazelnut-spread-contaminant-detection/dataset_46930.pq`: 401,854 bytes, SHA-256 `e77e8942836e...`, <https://data.openml.org/datasets/0004/46930/dataset_46930.pq>
  - `raw/hazelnut-spread-contaminant-detection/openml_description_46930.json`: 3,098 bytes, SHA-256 `2f01d456beb7...`, <https://www.openml.org/api/v1/json/data/46930>
  - `raw/hazelnut-spread-contaminant-detection/openml_features_46930.json`: 4,674 bytes, SHA-256 `edd5d447dadb...`, <https://www.openml.org/api/v1/json/data/features/46930>
  - `raw/hazelnut-spread-contaminant-detection/openml_qualities_46930.json`: 1,037 bytes, SHA-256 `20f76b9fcf77...`, <https://www.openml.org/api/v1/json/data/qualities/46930>
- **Curators' comments (verbatim from the OpenML description):**
  - "We select a features from a single frequency (10 GHz) as the authors also only considered this frequency for the final experiments."
  - "Anomaly: we use the publicly available dataset state, which is without preprocessing. Moreover, we were not able to inverse the original ordinal encoding of the label."
- **Relation to the better-known original:** COLUMNS: features of a single frequency (10 GHz) selected from OpenML 45538.
- **Decisions a build would need:**
  - Positive class: the target `Contaminated` has the labels 0=1200 / 1=1200; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363674 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 18. heloc

- **OpenML:** dataset 46932 (version 3, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:17:32); task 363676; target `RiskPerformance`. <https://www.openml.org/d/46932>
- **Licence as displayed by OpenML:** Public. **Original source as displayed:** https://www.kaggle.com/datasets/averkiyoliabev/home-equity-line-of-creditheloc
- **Citation as displayed:** Kaggle User Averkiyoliabev. 'Home Equity Line of Credit (HELOC).' Kaggle, 2021, https://www.kaggle.com/datasets/averkiyoliabev/home-equity-line-of-creditheloc.
- **Repo metadata:** source Kaggle, dataset year 2021.
- **Measured from the ARFF:** 10,459 rows; 24 columns including the target (23 numeric, 1 nominal, 0 string); 0 missing cells; classes Bad=5459, Good=5000. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/heloc/heloc.arff`: 669,721 bytes, SHA-256 `6041d6e0c6a9...`, <https://openml.org/data/v1/download/22125243/heloc.arff>
  - `raw/heloc/dataset_46932.pq`: 209,550 bytes, SHA-256 `65cec2870c8b...`, <https://data.openml.org/datasets/0004/46932/dataset_46932.pq>
  - `raw/heloc/openml_description_46932.json`: 2,254 bytes, SHA-256 `f9bbcc8ba6c6...`, <https://www.openml.org/api/v1/json/data/46932>
  - `raw/heloc/openml_features_46932.json`: 4,074 bytes, SHA-256 `7e6fee7a240f...`, <https://www.openml.org/api/v1/json/data/features/46932>
  - `raw/heloc/openml_qualities_46932.json`: 1,067 bytes, SHA-256 `833fb6844f9d...`, <https://www.openml.org/api/v1/json/data/qualities/46932>
- **Curators' comments (verbatim from the OpenML description):**
  - "Anomaly: the dataset has time-related features. However, the task and features are preprocessed to be time-invariant."
- **Relation to the better-known original:** SOURCE: taken from a Kaggle upload (averkiyoliabev), not from FICO; OpenML licence field 'Public'.
- **Decisions a build would need:**
  - Positive class: the target `RiskPerformance` has the labels Bad=5459 / Good=5000; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Leakage candidates (read off names and documentation, NOT measured): ExternalRiskEstimate (an external consolidated risk score, itself a model output).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363676 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 19. HR_Analytics_Job_Change_of_Data_Scientists

- **OpenML:** dataset 46935 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:18:03); task 363679; target `LookingForJobChange`. <https://www.openml.org/d/46935>
- **Licence as displayed by OpenML:** CC0: Public Domain. **Original source as displayed:** https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists
- **Citation as displayed:** Kaggle User Arashnic. 'HR Analytics: Job Change of Data Scientists.' Kaggle, 2021, https://www.kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists.
- **Repo metadata:** source Kaggle, dataset year 2021.
- **Measured from the ARFF:** 19,158 rows; 13 columns including the target (2 numeric, 10 nominal, 1 string); 65 missing cells; classes No=14381, Yes=4777. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/HR_Analytics_Job_Change_of_Data_Scientists/HR_Analytics_Job_Change_of_Data_Scientists.arff`: 1,952,388 bytes, SHA-256 `3103d37cf2da...`, <https://openml.org/data/v1/download/22125246/HR_Analytics_Job_Change_of_Data_Scientists.arff>
  - `raw/HR_Analytics_Job_Change_of_Data_Scientists/dataset_46935.pq`: 131,894 bytes, SHA-256 `78a3794c0589...`, <https://data.openml.org/datasets/0004/46935/dataset_46935.pq>
  - `raw/HR_Analytics_Job_Change_of_Data_Scientists/openml_description_46935.json`: 2,359 bytes, SHA-256 `c4216b7619f3...`, <https://www.openml.org/api/v1/json/data/46935>
  - `raw/HR_Analytics_Job_Change_of_Data_Scientists/openml_features_46935.json`: 4,044 bytes, SHA-256 `d941bc85f60d...`, <https://www.openml.org/api/v1/json/data/features/46935>
  - `raw/HR_Analytics_Job_Change_of_Data_Scientists/openml_qualities_46935.json`: 1,102 bytes, SHA-256 `134ebbb98f51...`, <https://www.openml.org/api/v1/json/data/qualities/46935>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the target feature and its values to be more descriptive."
  - "We drop the ID column."
- **Relation to the better-known original:** COLUMNS: ID column dropped.
- **Decisions a build would need:**
  - Positive class: the target `LookingForJobChange` has the labels No=14381 / Yes=4777; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 65 cells in 1 columns and 65 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Pseudo-missing literals: 7 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - High-cardinality categoricals (> 50 observed values): city=123. A binary cue needs a grouping rule, or the column is dropped.
  - STRING-typed columns: experience. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Redundancy (by name, NOT measured): city_development_index sits beside city (by name, a property of the city).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363679 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 20. in_vehicle_coupon_recommendation

- **OpenML:** dataset 46937 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:18:19); task 363681; target `AcceptCoupon`. <https://www.openml.org/d/46937>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5GS4P
- **Citation as displayed:** Wang, Tong, et al. 'A bayesian framework for learning rule sets for interpretable classification.' Journal of Machine Learning Research 18.70 (2017): 1-37. https://www.jmlr.org/papers/v18/16-003.html
- **Repo metadata:** source UCI, dataset year 2017.
- **Measured from the ARFF:** 12,684 rows; 25 columns including the target (2 numeric, 22 nominal, 1 string); 0 missing cells; classes No=5474, Yes=7210. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/in_vehicle_coupon_recommendation/in_vehicle_coupon_recommendation.arff`: 2,272,860 bytes, SHA-256 `a1f67b534b8e...`, <https://openml.org/data/v1/download/22125248/in_vehicle_coupon_recommendation.arff>
  - `raw/in_vehicle_coupon_recommendation/dataset_46937.pq`: 110,071 bytes, SHA-256 `283ffe518c4d...`, <https://data.openml.org/datasets/0004/46937/dataset_46937.pq>
  - `raw/in_vehicle_coupon_recommendation/openml_description_46937.json`: 2,586 bytes, SHA-256 `d32ccd8234bf...`, <https://www.openml.org/api/v1/json/data/46937>
  - `raw/in_vehicle_coupon_recommendation/openml_features_46937.json`: 5,886 bytes, SHA-256 `3f872f4d3537...`, <https://www.openml.org/api/v1/json/data/features/46937>
  - `raw/in_vehicle_coupon_recommendation/openml_qualities_46937.json`: 1,025 bytes, SHA-256 `5870e624bc91...`, <https://www.openml.org/api/v1/json/data/qualities/46937>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the target feature and its value to be more descriptive."
  - "We removed text data from the "time" feature to make it numeric."
  - "We drop constant columns."
  - "We fixed a typo in the feature names."
  - "Anomaly: the data has many binned numeric features that are treated as categorical features with text describing the bins."
  - "Anomaly: the numeric features in the dataset are low-cardinality (<25)"
- **Relation to the better-known original:** COLUMNS: constant columns dropped; 'time' made numeric; a feature-name typo fixed.
- **Decisions a build would need:**
  - Positive class: the target `AcceptCoupon` has the labels No=5474 / Yes=7210; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Pseudo-missing literals: 6 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - STRING-typed columns: coupon. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363681 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 21. Is-this-a-good-customer

- **OpenML:** dataset 46938 (version 2, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:18:25); task 363682; target `bad_client_target`. <https://www.openml.org/d/46938>
- **Licence as displayed by OpenML:** CC0: Public Domain. **Original source as displayed:** https://www.kaggle.com/datasets/podsyp/is-this-a-good-customer
- **Citation as displayed:** Kaggle User Podsyp. 'Is This a Good Customer?' Kaggle, 2020, https://www.kaggle.com/datasets/podsyp/is-this-a-good-customer.
- **Repo metadata:** source Kaggle, dataset year 2020.
- **Measured from the ARFF:** 1,723 rows; 14 columns including the target (5 numeric, 9 nominal, 0 string); 0 missing cells; classes No=1527, Yes=196. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/Is-this-a-good-customer/Is-this-a-good-customer.arff`: 150,528 bytes, SHA-256 `07410aa7b4cd...`, <https://openml.org/data/v1/download/22125249/Is-this-a-good-customer.arff>
  - `raw/Is-this-a-good-customer/dataset_46938.pq`: 24,119 bytes, SHA-256 `3aaa17c39e53...`, <https://data.openml.org/datasets/0004/46938/dataset_46938.pq>
  - `raw/Is-this-a-good-customer/openml_description_46938.json`: 2,165 bytes, SHA-256 `0c4a2007a49d...`, <https://www.openml.org/api/v1/json/data/46938>
  - `raw/Is-this-a-good-customer/openml_features_46938.json`: 2,969 bytes, SHA-256 `0ae0ff51bb4b...`, <https://www.openml.org/api/v1/json/data/features/46938>
  - `raw/Is-this-a-good-customer/openml_qualities_46938.json`: 1,063 bytes, SHA-256 `7ecaaf77fb21...`, <https://www.openml.org/api/v1/json/data/qualities/46938>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the values of the target variable to be more descriptive."
- **Decisions a build would need:**
  - Positive class: the target `bad_client_target` has the labels No=1527 / Yes=196; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363682 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 22. kddcup09_appetency

- **OpenML:** dataset 46939 (version 2, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:18:41); task 363683; target `appetency`. <https://www.openml.org/d/46939>
- **Licence as displayed by OpenML:** Public. **Original source as displayed:** https://kdd.org/kdd-cup/view/kdd-cup-2009/Intro
- **Citation as displayed:** Guyon, Isabelle, et al. 'Analysis of the kdd cup 2009: Fast scoring on a large orange customer database.' KDD-Cup 2009 Competition. PMLR, 2009. https://proceedings.mlr.press/v7/guyon09.html
- **Repo metadata:** source Other, dataset year 2008.
- **Measured from the ARFF:** 50,000 rows; 213 columns including the target (174 numeric, 39 nominal, 0 string); 6,727,959 missing cells; classes -1=49110, 1=890. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: False; TabICL can run: True.
- **Files:**
  - `raw/kddcup09_appetency/kddcup09_appetency.arff`: 37,428,824 bytes, SHA-256 `91230b3ebf0a...`, <https://openml.org/data/v1/download/22125250/kddcup09_appetency.arff>
  - `raw/kddcup09_appetency/dataset_46939.pq`: 6,812,625 bytes, SHA-256 `a09221ace7ce...`, <https://data.openml.org/datasets/0004/46939/dataset_46939.pq>
  - `raw/kddcup09_appetency/openml_description_46939.json`: 2,617 bytes, SHA-256 `e7b794cc4b46...`, <https://www.openml.org/api/v1/json/data/46939>
  - `raw/kddcup09_appetency/openml_features_46939.json`: 706,924 bytes, SHA-256 `ff789614e36d...`, <https://www.openml.org/api/v1/json/data/features/46939>
  - `raw/kddcup09_appetency/openml_qualities_46939.json`: 1,057 bytes, SHA-256 `84eb92756fb5...`, <https://www.openml.org/api/v1/json/data/qualities/46939>
- **Curators' comments (verbatim from the OpenML description):**
  - "We use the small (230 features) training data from the original data."
  - "We use appetency as label."
  - "We dropped empty columns: "Var8", "Var15", "Var20", "Var31", "Var32", "Var39", "Var42", "Var48", "Var52", "Var55", "Var79", "Var141", "Var167", "Var169", "Var175", "Var185", "Var209", "Var230"."
  - "Anomaly: this dataset has many missing values."
  - "Anomaly: the feature names and categorical values have no semantic meaning."
- **Relation to the better-known original:** ROWS+COLUMNS: the small (230-feature) training data; 18 empty columns dropped; label = appetency.
- **Decisions a build would need:**
  - Positive class: the target `appetency` has the labels -1=49110 / 1=890; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 6,727,959 cells in 171 columns and 50,000 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Pseudo-missing literals: 22 feature columns carry values such as `nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). Keep them as categories or recode them as missing.
  - High-cardinality categoricals (> 50 observed values): Var192=362, Var193=51, Var197=226, Var198=4291, Var199=5074, Var200=15416, Var202=5714, Var204=100, Var212=81, Var214=15416, Var216=2016, Var217=13991, Var220=4291, Var222=4291. A binary cue needs a grouping rule, or the column is dropped.
  - Constant columns (one observed value): Var118.
  - 212 features: cue search cost and any pre-selection rule need to be fixed in advance.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363683 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 23. Marketing_Campaign

- **OpenML:** dataset 46940 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:18:46); task 363684; target `Response`. <https://www.openml.org/d/46940>
- **Licence as displayed by OpenML:** Public. **Original source as displayed:** https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign
- **Citation as displayed:** Saldanha, Rodolfo. 'Marketing Campaign.' Kaggle, 2020, https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign.
- **Repo metadata:** source Kaggle, dataset year 2020.
- **Measured from the ARFF:** 2,240 rows; 26 columns including the target (16 numeric, 9 nominal, 1 string); 24 missing cells; classes No=1906, Yes=334. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/Marketing_Campaign/Marketing_Campaign.arff`: 204,688 bytes, SHA-256 `9efadbe4dace...`, <https://openml.org/data/v1/download/22125251/Marketing_Campaign.arff>
  - `raw/Marketing_Campaign/dataset_46940.pq`: 75,082 bytes, SHA-256 `e468d6379be2...`, <https://data.openml.org/datasets/0004/46940/dataset_46940.pq>
  - `raw/Marketing_Campaign/openml_description_46940.json`: 2,160 bytes, SHA-256 `c3b7f129c3a4...`, <https://www.openml.org/api/v1/json/data/46940>
  - `raw/Marketing_Campaign/openml_features_46940.json`: 4,465 bytes, SHA-256 `f24e20fcef28...`, <https://www.openml.org/api/v1/json/data/features/46940>
  - `raw/Marketing_Campaign/openml_qualities_46940.json`: 1,098 bytes, SHA-256 `bd982a6c413b...`, <https://www.openml.org/api/v1/json/data/qualities/46940>
- **Curators' comments (verbatim from the OpenML description):**
  - "We drop the ID column."
  - "We rename the values of the target variable to be more descriptive."
  - "We drop constant columns."
- **Relation to the better-known original:** COLUMNS: ID column and constant columns dropped.
- **Decisions a build would need:**
  - Positive class: the target `Response` has the labels No=1906 / Yes=334; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 24 cells in 1 columns and 24 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - High-cardinality categoricals (> 50 observed values): Dt_Customer=663. A binary cue needs a grouping rule, or the column is dropped.
  - STRING-typed columns: Dt_Customer. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Leakage candidates (read off names and documentation, NOT measured): AcceptedCmp1..AcceptedCmp5 (responses to earlier campaigns; legitimate if earlier in time, which the file does not state); Dt_Customer is a date stored as STRING.
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363684 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 24. NATICUSdroid

- **OpenML:** dataset 46969 (version 3, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T22:28:30); task 363689; target `Malware`. <https://www.openml.org/d/46969>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5FS64
- **Citation as displayed:** Mathur, Akshay, et al. 'NATICUSdroid: A malware detection framework for Android using native and custom permissions.' Journal of Information Security and Applications 58 (2021): 102696. https://doi.org/10.1016/j.jisa.2020.102696
- **Repo metadata:** source UCI, dataset year 2021.
- **Measured from the ARFF:** 7,491 rows; 87 columns including the target (0 numeric, 87 nominal, 0 string); 0 missing cells; classes No=4867, Yes=2624. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/NATICUSdroid/NATICUSdroid.arff`: 1,319,985 bytes, SHA-256 `b2fd768e8179...`, <https://openml.org/data/v1/download/22125386/NATICUSdroid.arff>
  - `raw/NATICUSdroid/dataset_46969.pq`: 150,973 bytes, SHA-256 `8f328b5d8912...`, <https://data.openml.org/datasets/0004/46969/dataset_46969.pq>
  - `raw/NATICUSdroid/openml_description_46969.json`: 2,468 bytes, SHA-256 `7c8f782c13d8...`, <https://www.openml.org/api/v1/json/data/46969>
  - `raw/NATICUSdroid/openml_features_46969.json`: 18,332 bytes, SHA-256 `ae19cbbbe7d4...`, <https://www.openml.org/api/v1/json/data/features/46969>
  - `raw/NATICUSdroid/openml_qualities_46969.json`: 1,027 bytes, SHA-256 `0641dcef9d42...`, <https://www.openml.org/api/v1/json/data/qualities/46969>
- **Curators' comments (verbatim from the OpenML description):**
  - "Originally, the data has 75% duplicates and a perfect class balance. The authors never mention duplicates in their paper. Given this large amount of duplicates, we dropped all row-duplicates, keeping only the first entry."
  - "Anomaly: all features are binary categorical features."
- **Relation to the better-known original:** ROWS: curators dropped all duplicate rows ('Originally, the data has 75% duplicates and a perfect class balance'). UCI record 722 reports 29,333 instances (UCI API).
- **Decisions a build would need:**
  - Positive class: the target `Malware` has the labels No=4867 / Yes=2624; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363689 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 25. online_shoppers_intention

- **OpenML:** dataset 46947 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:19:31); task 363691; target `Revenue`. <https://www.openml.org/d/46947>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5F88Q
- **Citation as displayed:** Sakar, C. Okan, et al. 'Real-time prediction of online shoppers purchasing intention using multilayer perceptron and LSTM recurrent neural networks.' Neural Computing and Applications 31.10 (2019): 6893-6908.  https://doi.org/10.1007/s00521-018-3523-0
- **Repo metadata:** source UCI, dataset year 2017.
- **Measured from the ARFF:** 12,330 rows; 18 columns including the target (10 numeric, 8 nominal, 0 string); 0 missing cells; classes False=10422, True=1908. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/online_shoppers_intention/online_shoppers_intention.arff`: 1,158,800 bytes, SHA-256 `db34ad0b4506...`, <https://openml.org/data/v1/download/22125258/online_shoppers_intention.arff>
  - `raw/online_shoppers_intention/dataset_46947.pq`: 328,478 bytes, SHA-256 `0c2e251ee858...`, <https://data.openml.org/datasets/0004/46947/dataset_46947.pq>
  - `raw/online_shoppers_intention/openml_description_46947.json`: 2,374 bytes, SHA-256 `54b4acbe395b...`, <https://www.openml.org/api/v1/json/data/46947>
  - `raw/online_shoppers_intention/openml_features_46947.json`: 3,359 bytes, SHA-256 `bf48e72379f9...`, <https://www.openml.org/api/v1/json/data/features/46947>
  - `raw/online_shoppers_intention/openml_qualities_46947.json`: 1,066 bytes, SHA-256 `32cd15906ff4...`, <https://www.openml.org/api/v1/json/data/qualities/46947>
- **Curators' comments (verbatim from the OpenML description):**
  - "Anomaly: the data contains time-based features that were preprocessed to create a time-invariant predictive task."
- **Decisions a build would need:**
  - Positive class: the target `Revenue` has the labels False=10422 / True=1908; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Leakage candidates (read off names and documentation, NOT measured): PageValues (a Google Analytics value derived from e-commerce transactions; the target Revenue is whether the session ended in a transaction).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363691 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 26. polish_companies_bankruptcy

- **OpenML:** dataset 46950 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:19:51); task 363694; target `company_bankrupt`. <https://www.openml.org/d/46950>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5F600
- **Citation as displayed:** Zieba, Maciej, Sebastian K. Tomczak, and Jakub M. Tomczak. 'Ensemble boosted trees with synthetic features generation in application to bankruptcy prediction.' Expert systems with applications 58 (2016): 93-101. https://doi.org/10.1016/j.eswa.2016.04.001
- **Repo metadata:** source UCI, dataset year 2010.
- **Measured from the ARFF:** 5,910 rows; 65 columns including the target (64 numeric, 1 nominal, 0 string); 4,666 missing cells; classes No=5500, Yes=410. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/polish_companies_bankruptcy/polish_companies_bankruptcy.arff`: 2,923,681 bytes, SHA-256 `113352098b5c...`, <https://openml.org/data/v1/download/22125261/polish_companies_bankruptcy.arff>
  - `raw/polish_companies_bankruptcy/dataset_46950.pq`: 3,126,979 bytes, SHA-256 `afe5fcf497e0...`, <https://data.openml.org/datasets/0004/46950/dataset_46950.pq>
  - `raw/polish_companies_bankruptcy/openml_description_46950.json`: 2,527 bytes, SHA-256 `69c8399ab8d9...`, <https://www.openml.org/api/v1/json/data/46950>
  - `raw/polish_companies_bankruptcy/openml_features_46950.json`: 11,548 bytes, SHA-256 `e1f19cc6fdff...`, <https://www.openml.org/api/v1/json/data/features/46950>
  - `raw/polish_companies_bankruptcy/openml_qualities_46950.json`: 1,100 bytes, SHA-256 `a82c80b3acd2...`, <https://www.openml.org/api/v1/json/data/qualities/46950>
- **Curators' comments (verbatim from the OpenML description):**
  - "We only use data from year 5, because it is the newest data and the target is bankruptcy status after only 1 year."
  - "We created semantically meaningful feature names."
  - "Anomaly: the data contains a lot of features created by feature engineering."
- **Relation to the better-known original:** ROWS: curators use the year-5 file only. UCI record 365 reports 10,503 instances (UCI API).
- **Decisions a build would need:**
  - Positive class: the target `company_bankrupt` has the labels No=5500 / Yes=410; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 4,666 cells in 49 columns and 2,879 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363694 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 27. qsar-biodeg

- **OpenML:** dataset 46952 (version 2, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:20:04); task 363696; target `Biodegradable`. <https://www.openml.org/d/46952>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5H60M
- **Citation as displayed:** Mansouri, Kamel, et al. 'Quantitative structureactivity relationship models for ready biodegradability of chemicals.' Journal of chemical information and modeling 53.4 (2013): 867-878. https://doi.org/10.1021/ci4000213
- **Repo metadata:** source UCI, dataset year 2013.
- **Measured from the ARFF:** 1,054 rows; 42 columns including the target (36 numeric, 6 nominal, 0 string); 0 missing cells; classes No=699, Yes=355. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 30 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/qsar-biodeg/qsar-biodeg.arff`: 161,514 bytes, SHA-256 `558eb643ae68...`, <https://openml.org/data/v1/download/22125263/qsar-biodeg.arff>
  - `raw/qsar-biodeg/dataset_46952.pq`: 105,768 bytes, SHA-256 `864c269749de...`, <https://data.openml.org/datasets/0004/46952/dataset_46952.pq>
  - `raw/qsar-biodeg/openml_description_46952.json`: 2,327 bytes, SHA-256 `c7863cb6de0d...`, <https://www.openml.org/api/v1/json/data/46952>
  - `raw/qsar-biodeg/openml_features_46952.json`: 7,302 bytes, SHA-256 `5a2580c848a2...`, <https://www.openml.org/api/v1/json/data/features/46952>
  - `raw/qsar-biodeg/openml_qualities_46952.json`: 1,062 bytes, SHA-256 `79ae5f2dcdcd...`, <https://www.openml.org/api/v1/json/data/qualities/46952>
- **Curators' comments (verbatim from the OpenML description):**
  - "We added semantic meaningful feature names."
  - "Anomaly: several features are numeric-ordinal in nature but it is unclear if they are categorical features."
- **Relation to the better-known original:** CODING: features renamed only.
- **Decisions a build would need:**
  - Positive class: the target `Biodegradable` has the labels No=699 / Yes=355; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 30 outer splits (10 of the 10 repeats x 3 folds that OpenML task 363696 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 28. seismic-bumps

- **OpenML:** dataset 46956 (version 4, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:20:44); task 363700; target `HighEnergySeismicBump`. <https://www.openml.org/d/46956>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5W902
- **Citation as displayed:** Sikora, Marek, and ukasz Wrobel. 'Application of rule induction algorithms for analysis of data collected by seismic hazard monitoring systems in coal mines.' Archives of Mining Sciences 55.1 (2010): 91-114. http://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-article-BPZ5-0008-0008
- **Repo metadata:** source UCI, dataset year 2013.
- **Measured from the ARFF:** 2,584 rows; 16 columns including the target (11 numeric, 4 nominal, 1 string); 0 missing cells; classes No=2414, Yes=170. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/seismic-bumps/seismic-bumps.arff`: 173,522 bytes, SHA-256 `457abff74c71...`, <https://openml.org/data/v1/download/22125267/seismic-bumps.arff>
  - `raw/seismic-bumps/dataset_46956.pq`: 53,840 bytes, SHA-256 `907dfa3a1301...`, <https://data.openml.org/datasets/0004/46956/dataset_46956.pq>
  - `raw/seismic-bumps/openml_description_46956.json`: 2,487 bytes, SHA-256 `2a7845eb3012...`, <https://www.openml.org/api/v1/json/data/46956>
  - `raw/seismic-bumps/openml_features_46956.json`: 2,595 bytes, SHA-256 `1141eb38f2a4...`, <https://www.openml.org/api/v1/json/data/features/46956>
  - `raw/seismic-bumps/openml_qualities_46956.json`: 1,026 bytes, SHA-256 `97d54f4e40e6...`, <https://www.openml.org/api/v1/json/data/qualities/46956>
- **Curators' comments (verbatim from the OpenML description):**
  - "We renamed the target feature and reversed the values' ordinal encoding."
  - "We drop the constant columns "nbumps6", "nbumps7", and "nbumps89"."
- **Relation to the better-known original:** COLUMNS: constant columns nbumps6, nbumps7, nbumps89 dropped; target renamed and relabelled.
- **Decisions a build would need:**
  - Positive class: the target `HighEnergySeismicBump` has the labels No=2414 / Yes=170; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - STRING-typed columns: ghazard. Declared as free text in the ARFF, so a reader must decide whether they are categories, numbers or dates.
  - Leakage candidates (read off names and documentation, NOT measured): seismic, seismoacoustic, ghazard (hazard assessments produced by other methods for the same shift).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363700 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 29. taiwanese_bankruptcy_prediction

- **OpenML:** dataset 46962 (version 1, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-04-30T20:21:31); task 363706; target `Bankrupt`. <https://www.openml.org/d/46962>
- **Licence as displayed by OpenML:** CC BY 4.0. **Original source as displayed:** https://doi.org/10.24432/C5004D
- **Citation as displayed:** Liang, Deron, et al. 'Financial ratios and corporate governance indicators in bankruptcy prediction: A comprehensive study.' European journal of operational research 252.2 (2016): 561-572. https://doi.org/10.1016/j.ejor.2016.01.012
- **Repo metadata:** source UCI, dataset year 2009.
- **Measured from the ARFF:** 6,819 rows; 95 columns including the target (94 numeric, 1 nominal, 0 string); 0 missing cells; classes No=6599, Yes=220. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/taiwanese_bankruptcy_prediction/taiwanese_bankruptcy_prediction.arff`: 11,348,172 bytes, SHA-256 `e8c347eaef96...`, <https://openml.org/data/v1/download/22125273/taiwanese_bankruptcy_prediction.arff>
  - `raw/taiwanese_bankruptcy_prediction/dataset_46962.pq`: 4,681,502 bytes, SHA-256 `0c3955339460...`, <https://data.openml.org/datasets/0004/46962/dataset_46962.pq>
  - `raw/taiwanese_bankruptcy_prediction/openml_description_46962.json`: 2,646 bytes, SHA-256 `7d36a4ec6bd1...`, <https://www.openml.org/api/v1/json/data/46962>
  - `raw/taiwanese_bankruptcy_prediction/openml_features_46962.json`: 16,329 bytes, SHA-256 `21ed65bdc4eb...`, <https://www.openml.org/api/v1/json/data/features/46962>
  - `raw/taiwanese_bankruptcy_prediction/openml_qualities_46962.json`: 1,065 bytes, SHA-256 `ba3dd8e06eab...`, <https://www.openml.org/api/v1/json/data/qualities/46962>
- **Curators' comments (verbatim from the OpenML description):**
  - "We rename the features to be shorter and have no special characters."
  - "We drop the constant column "Net_Income_Flag"."
  - "Anomaly: the paper introducing the dataset has more features, but these do not seem to be in the dataset."
  - "Anomaly: the data is temporal but all features are time-invariant. This might still have a latent, non-verifiable temporal component, which we ignore for our predictive IID task."
- **Relation to the better-known original:** COLUMNS: constant column Net_Income_Flag dropped; features renamed.
- **Decisions a build would need:**
  - Positive class: the target `Bankrupt` has the labels No=6599 / Yes=220; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363706 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

### 30. jm1

- **OpenML:** dataset 46979 (version 3, label `tabular-ml-iid-study-0.0.1`, uploaded 2025-05-06T10:46:18); task 363712; target `defects`. <https://www.openml.org/d/46979>
- **Licence as displayed by OpenML:** Public Domain. **Original source as displayed:** https://www.openml.org/d/1053
- **Citation as displayed:** How Good is Your Blind Spot Sampling Policy?; 2003; Tim Menzies and Justin S. Di Stefano; 2004 IEEE Conference on High Assurance Software Engineering (http://menzies.us/pdf/03blind.pdf).
- **Repo metadata:** source OpenML, dataset year 2004.
- **Measured from the ARFF:** 10,885 rows; 22 columns including the target (21 numeric, 1 nominal, 0 string); 25 missing cells; classes False=8779, True=2106. Equal to the OpenML qualities: yes. Equal to the parquet copy: yes.
- **TabArena protocol (repo metadata):** 9 splits; TabPFNv2 can run: True; TabICL can run: True.
- **Files:**
  - `raw/jm1/jm1.arff`: 1,157,472 bytes, SHA-256 `fdbcb4b9c4b0...`, <https://openml.org/data/v1/download/22125396/jm1.arff>
  - `raw/jm1/dataset_46979.pq`: 406,647 bytes, SHA-256 `fe4cf507abfc...`, <https://data.openml.org/datasets/0004/46979/dataset_46979.pq>
  - `raw/jm1/openml_description_46979.json`: 2,367 bytes, SHA-256 `58669069b652...`, <https://www.openml.org/api/v1/json/data/46979>
  - `raw/jm1/openml_features_46979.json`: 3,381 bytes, SHA-256 `d72110486411...`, <https://www.openml.org/api/v1/json/data/features/46979>
  - `raw/jm1/openml_qualities_46979.json`: 1,101 bytes, SHA-256 `7473e0e66165...`, <https://www.openml.org/api/v1/json/data/qualities/46979>
- **Curators' comments (verbatim from the OpenML description):**
  - "We selected this dataset as representative of a set of predictive modeling tasks of software engineering (other examples of such tasks are available on OpenML under the names mozilla4, pc1, pc2, pc3, mc1, kc1, kc2). This dataset was selected as it has the largest sample size."
- **Relation to the better-known original:** SOURCE: copy of OpenML 1053, chosen by the curators as the largest of a family of software-defect sets.
- **Decisions a build would need:**
  - Positive class: the target `defects` has the labels False=8779 / True=2106; which one is "positive" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do).
  - Missing values: 25 cells in 5 columns and 5 rows. Deleting incomplete rows, imputing, or treating "missing" as a cue value are different experiments.
  - Splits: TabArena scores this set on 9 outer splits (3 of the 10 repeats x 3 folds that OpenML task 363712 defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.

## Shared files

| Path | Bytes | SHA-256 | Origin |
|---|---|---|---|
| `suite/study_457.json` | 1,588 | `0421355639e8...` | https://www.openml.org/api/v1/json/study/457 |
| `references/TabArena_arXiv_2506.16791v4.html` | 2,042,389 | `f8f6fc06988c...` | https://arxiv.org/html/2506.16791v4 |
| `references/TabArena_arXiv_2506.16791v4.pdf` | 1,964,941 | `8853fd1a1eb0...` | https://arxiv.org/pdf/2506.16791 |
| `references/TabArena_arXiv_2506.16791v4_pypdf_text.txt` | 235,741 | `f5eda5abe768...` | derived: pypdf text layer of the arXiv PDF, page by page |
| `references/TabArena_arXiv_2506.16791v4_TableF1_html_parsed.csv` | 133,229 | `335c2be94a64...` | derived: scripts/crosscheck_pdf_vs_html.py on the arXiv HTML |
| `references/TabArena_arXiv_2506.16791v4_TableF1_parsed.csv` | 141,041 | `ddd1b3852ad2...` | derived: scripts/parse_pdf_table_f1.py on the arXiv PDF |
| `references/TabArena_NeurIPS2025_Paper.pdf` | 1,680,337 | `2884b32e2e27...` | https://proceedings.neurips.cc/paper_files/paper/2025/file/1697e3fb412da11dc9488249f9e7bbc9-Paper-Datasets_and_Benchmarks_Track.pdf |
| `references/TabArena_NeurIPS2025_Paper_TableF1_parsed.csv` | 141,041 | `ddd1b3852ad2...` | derived: scripts/parse_pdf_table_f1.py on the proceedings PDF |
| `references/TabArena_NeurIPS2025_Supplemental.pdf` | 751,449 | `ee493dce15ac...` | https://proceedings.neurips.cc/paper_files/paper/2025/file/1697e3fb412da11dc9488249f9e7bbc9-Supplemental-Datasets_and_Benchmarks_Track.pdf |
| `references/tabarena_repo/examples__reproducibility__run_generate_main_leaderboard_neurips2025.py` | 1,401 | `3ef907d6c51a...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/examples/reproducibility/run_generate_main_leaderboard_neurips2025.py |
| `references/tabarena_repo/LICENSE` | 11,357 | `c71d239df917...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/LICENSE |
| `references/tabarena_repo/packages__tabarena__src__tabarena__benchmark__task__metadata__data__curated_tabarena_dataset_metadata.csv` | 13,854 | `b45fa1f33e7f...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/benchmark/task/metadata/data/curated_tabarena_dataset_metadata.csv |
| `references/tabarena_repo/packages__tabarena__src__tabarena__contexts__tabarena___tabarena_method_metadata_2025_06_12.py` | 6,232 | `20204842b7c2...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/contexts/tabarena/_tabarena_method_metadata_2025_06_12.py |
| `references/tabarena_repo/packages__tabarena__src__tabarena__contexts__tabarena__methods.py` | 12,220 | `b7e3e43dd5ef...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/contexts/tabarena/methods.py |
| `references/tabarena_repo/packages__tabarena__src__tabarena__models___method_metadata.py` | 69,047 | `7cf18b668d7c...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/models/_method_metadata.py |
| `references/tabarena_repo/packages__tabarena__src__tabarena__models__knn__info.py` | 895 | `0fc4c9b1d493...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/models/knn/info.py |
| `references/tabarena_repo/packages__tabarena__src__tabarena__models__lr__info.py` | 947 | `5edb332c71a3...` | https://raw.githubusercontent.com/autogluon/tabarena/60d0f66771c87bb8a255c3d595476119324aaf41/packages/tabarena/src/tabarena/models/lr/info.py |
| `references/uci_metadata/uci_296.json` | 19,603 | `6e6e0934d175...` | https://archive.ics.uci.edu/api/dataset?id=296 |
| `references/uci_metadata/uci_365.json` | 14,973 | `6a2ee78e34e8...` | https://archive.ics.uci.edu/api/dataset?id=365 |
| `references/uci_metadata/uci_722.json` | 15,614 | `067080961f00...` | https://archive.ics.uci.edu/api/dataset?id=722 |
| `results_artifact/tabarena-2025-06-12/methods/AutoGluon_v130/results/model_results.parquet` | 19,744 | `d0be4cb80920...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/AutoGluon_v130/results/model_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/CatBoost/results/hpo_results.parquet` | 62,977 | `62959452d201...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/CatBoost/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/ExplainableBM/results/hpo_results.parquet` | 62,412 | `a6110f54d5eb...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/ExplainableBM/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/ExtraTrees/results/hpo_results.parquet` | 60,642 | `b3314dc966c6...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/ExtraTrees/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/KNeighbors/results/hpo_results.parquet` | 57,929 | `3ce73d3bf567...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/KNeighbors/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/LightGBM/results/hpo_results.parquet` | 63,273 | `ff1dcadc450a...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/LightGBM/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/LinearModel/results/hpo_results.parquet` | 54,662 | `f62d21c90075...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/LinearModel/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/ModernNCA_GPU/results/hpo_results.parquet` | 63,859 | `a7cad50898c9...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/ModernNCA_GPU/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/NeuralNetFastAI/results/hpo_results.parquet` | 63,644 | `03d2c23c5e06...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/NeuralNetFastAI/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/NeuralNetTorch/results/hpo_results.parquet` | 63,717 | `a75fe4f418ab...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/NeuralNetTorch/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/RandomForest/results/hpo_results.parquet` | 58,869 | `ba21e8769f8b...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/RandomForest/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/RealMLP/results/hpo_results.parquet` | 64,053 | `0760a1b35458...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/RealMLP/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/TabDPT_GPU/results/hpo_results.parquet` | 25,633 | `b4e9e2db230c...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/TabDPT_GPU/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/TabICL_GPU/results/hpo_results.parquet` | 25,534 | `7f79aca61a3a...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/TabICL_GPU/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/TabM_GPU/results/hpo_results.parquet` | 63,542 | `91692229ad1c...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/TabM_GPU/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/TabPFNv2_GPU/results/hpo_results.parquet` | 57,859 | `146e54cd6d16...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/TabPFNv2_GPU/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-06-12/methods/XGBoost/results/hpo_results.parquet` | 62,853 | `fb37a4ac13ee...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-06-12/methods/XGBoost/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-10-20/methods/KNeighbors/results/hpo_results.parquet` | 78,123 | `cc76c4b1b2fb...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-10-20/methods/KNeighbors/results/hpo_results.parquet |
| `results_artifact/tabarena-2025-10-20/methods/LinearModel/results/hpo_results.parquet` | 77,799 | `1a647b07b416...` | https://tabarena.s3.amazonaws.com/cache/artifacts/tabarena-2025-10-20/methods/LinearModel/results/hpo_results.parquet |

Not listed row by row: 51 task records under `suite/tasks/` and 24 JSON records under `suite/nonbinary_classification/` (all in `manifest.json`).
