#!/usr/bin/env python3
"""Count the 30 raw ARFF files and write measured-counts.csv + measured-column-counts.csv.

    python scripts/measure_counts.py

Standard library only. Uses the counting code of scripts/verify.py (one implementation, so the
verifier re-counts with exactly the rules used here; the independent check is
scripts/crosscheck_arff_vs_parquet.py, which reads the parquet copies with pyarrow).

COUNTS ONLY. Each column is counted on its own. No feature is cross-tabulated with, correlated
with, or otherwise related to the target, and nothing is fitted or scored.

Flags are raised WITHOUT deciding anything:
  measured   rows > 100,000; nominal/string columns with > 50 distinct observed values; columns whose
             values are all distinct; STRING-typed columns; constant columns; literal tokens that
             read like "no information" (nan, unknown, ...), which ARFF does not treat as missing
  by name    identifier-like column names (regex)
  judgment   LEAKAGE_CANDIDATES and DIFFERS_FROM_ORIGINAL below: read off the column names and the
             curators' own comments in the OpenML descriptions. They are reading notes, not
             measurements: no association with the target was computed for any of them.
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import ROOT, measure  # noqa: E402

ID_NAME = re.compile(r"(?i)(^|[^a-z])(id|ids|idx|uuid|nbr)($|[^a-z])")

LEAKAGE_CANDIDATES = {
    "Diabetes130US": "discharge_disposition_id (its categories include 'Expired' and hospice discharges, after which an "
                     "early readmission cannot occur)",
    "online_shoppers_intention": "PageValues (a Google Analytics value derived from e-commerce transactions; the target "
                                 "Revenue is whether the session ended in a transaction)",
    "customer_satisfaction_in_airline": "the 14 service-rating columns Seatcomfort ... Onlineboarding (answers from the same "
                                        "passenger survey that yields the target satisfaction)",
    "heloc": "ExternalRiskEstimate (an external consolidated risk score, itself a model output)",
    "seismic-bumps": "seismic, seismoacoustic, ghazard (hazard assessments produced by other methods for the same shift)",
    "bank-marketing": "campaign (number of contacts in the current campaign, known only once the campaign is over); the "
                      "curators already removed duration, month and day_of_week for this reason",
    "E-CommereShippingData": "Discount_offered (UNVERIFIED recollection of public discussion of this Kaggle set; the curators "
                             "note that 'the target and task seems somewhat disconnected from the features')",
    "Marketing_Campaign": "AcceptedCmp1..AcceptedCmp5 (responses to earlier campaigns; legitimate if earlier in time, "
                          "which the file does not state); Dt_Customer is a date stored as STRING",
}
REDUNDANCY_NOTES = {
    "churn": "total_*_charge columns sit beside total_*_minutes columns (by name, a tariff multiple)",
    "HR_Analytics_Job_Change_of_Data_Scientists": "city_development_index sits beside city (by name, a property of the city)",
    "Amazon_employee_access": "ROLE_TITLE and ROLE_CODE both declare 343 values",
}
DIFFERS_FROM_ORIGINAL = {
    "polish_companies_bankruptcy": "ROWS: curators use the year-5 file only. UCI record 365 reports 10,503 instances (UCI API).",
    "NATICUSdroid": "ROWS: curators dropped all duplicate rows ('Originally, the data has 75% duplicates and a perfect class "
                    "balance'). UCI record 722 reports 29,333 instances (UCI API).",
    "Diabetes130US": "ROWS+TARGET: one encounter per patient kept; encounter_id and patient_nbr dropped; binary target "
                     "built from 'readmitted'. UCI record 296 reports 101,766 instances (UCI API).",
    "heloc": "SOURCE: taken from a Kaggle upload (averkiyoliabev), not from FICO; OpenML licence field 'Public'.",
    "bank-marketing": "COLUMNS: duration, month and day_of_week removed by the curators.",
    "APSFailure": "ROWS: original training and test files combined; 'na' strings turned into missing values.",
    "coil2000_insurance_policies": "ROWS+CODING: original training and validation data combined; ordinal codes turned back "
                                   "into labels where possible.",
    "Amazon_employee_access": "ROWS: Kaggle training file only.",
    "Bioresponse": "ROWS: Kaggle training file only.",
    "kddcup09_appetency": "ROWS+COLUMNS: the small (230-feature) training data; 18 empty columns dropped; label = appetency.",
    "hazelnut-spread-contaminant-detection": "COLUMNS: features of a single frequency (10 GHz) selected from OpenML 45538.",
    "in_vehicle_coupon_recommendation": "COLUMNS: constant columns dropped; 'time' made numeric; a feature-name typo fixed.",
    "seismic-bumps": "COLUMNS: constant columns nbumps6, nbumps7, nbumps89 dropped; target renamed and relabelled.",
    "taiwanese_bankruptcy_prediction": "COLUMNS: constant column Net_Income_Flag dropped; features renamed.",
    "Marketing_Campaign": "COLUMNS: ID column and constant columns dropped.",
    "churn": "COLUMNS: phone_number dropped. Original source lost; curators point to PMLB and OpenML 40701.",
    "Bank_Customer_Churn": "COLUMNS: ID column dropped.",
    "credit_card_clients_default": "COLUMNS: ID column dropped; class names restored.",
    "E-CommereShippingData": "COLUMNS: ID column dropped.",
    "Fitness_Club": "COLUMNS+CODING: ID column dropped; days_before and day_of_week cleaned; target '-0' read as '0'.",
    "HR_Analytics_Job_Change_of_Data_Scientists": "COLUMNS: ID column dropped.",
    "credit-g": "CODING: the original ordinal encoding reversed into labels (Statlog German Credit).",
    "diabetes": "SAME DATA AS AN EARLIER COLLECTION: this is the Pima Indians Diabetes set (OpenML 37 with the target "
                "renamed), already held as PIMA in DATA_SETS/MKW08-30.",
    "jm1": "SOURCE: copy of OpenML 1053, chosen by the curators as the largest of a family of software-defect sets.",
    "qsar-biodeg": "CODING: features renamed only.",
    "blood-transfusion-service-center": "CODING: features renamed only (curators note 29% duplicate rows).",
}


def main():
    plan = [l.rstrip("\n").split("\t") for l in (ROOT / "build/download_plan.tsv").open(encoding="utf-8")]
    tasks = {r[0]: r for r in (l.rstrip("\n").split("\t") for l in (ROOT / "build/task_index.tsv").open(encoding="utf-8"))}
    repo = {r["dataset_id"]: r for r in csv.DictReader(
        (ROOT / "references/tabarena_repo/packages__tabarena__src__tabarena__benchmark__task__metadata__data__curated_tabarena_dataset_metadata.csv").open(encoding="utf-8"))}
    ds_out, col_out = [], []
    for name, tid, did, arff_url, pq_url, md5 in plan:
        desc = json.loads((ROOT / f"raw/{name}/openml_description_{did}.json").read_text(encoding="utf-8"))["data_set_description"]
        qual = {q["name"]: q["value"] for q in json.loads(
            (ROOT / f"raw/{name}/openml_qualities_{did}.json").read_text(encoding="utf-8"))["data_qualities"]["quality"]}
        target = tasks[tid][3]
        assert target == desc["default_target_attribute"], name
        summary, per_col = measure(ROOT / f"raw/{name}/{arff_url.rsplit('/', 1)[1]}", target)
        feats = [c for c in per_col if c["is_target"] == "no"]
        n_rows = int(summary["n_rows"])
        q = lambda k: str(int(float(qual[k]))) if qual.get(k) not in (None, "") else ""  # noqa: E731
        counts = sorted(int(x.split("=")[1]) for x in summary["class_counts"].split(";"))
        agree = (q("NumberOfInstances") == summary["n_rows"] and q("NumberOfFeatures") == summary["n_columns_incl_target"]
                 and q("NumberOfMissingValues") == summary["n_missing_cells"]
                 and q("NumberOfInstancesWithMissingValues") == summary["n_rows_with_missing"]
                 and [q("MinorityClassSize"), q("MajorityClassSize")] == [str(c) for c in counts])
        r = repo[did]
        row = dict(dataset=name, openml_data_id=did, openml_task_id=tid, openml_version=desc["version"],
                   openml_version_label=desc.get("version_label", ""), licence_as_displayed=desc.get("licence", ""),
                   **summary,
                   openml_quality_NumberOfInstances=q("NumberOfInstances"),
                   openml_quality_NumberOfFeatures=q("NumberOfFeatures"),
                   openml_quality_NumberOfMissingValues=q("NumberOfMissingValues"),
                   openml_quality_NumberOfInstancesWithMissingValues=q("NumberOfInstancesWithMissingValues"),
                   openml_quality_MinorityClassSize=q("MinorityClassSize"),
                   openml_quality_MajorityClassSize=q("MajorityClassSize"),
                   measured_equals_openml_qualities="yes" if agree else "NO",
                   repo_num_instances=str(int(float(r["num_instances"]))), repo_num_features=str(int(float(r["num_features"]))),
                   repo_problem_type=r["problem_type"], repo_data_source=r["data_source"], repo_dataset_year=r["year"],
                   tabarena_folds=r["num_folds"], tabarena_repeats=r["tabarena_num_repeats"],
                   tabarena_splits=str(int(r["num_folds"]) * int(r["tabarena_num_repeats"])),
                   repo_can_run_tabpfnv2=r["can_run_tabpfnv2"], repo_can_run_tabicl=r["can_run_tabicl"],
                   flag_rows_gt_100k="yes" if n_rows > 100000 else "no",
                   flag_high_cardinality_gt50=";".join(f"{c['column']}={c['n_distinct_observed']}" for c in feats
                                                       if c["declared_type"] in ("nominal", "STRING")
                                                       and int(c["n_distinct_observed"]) > 50),
                   flag_id_like_by_name=";".join(c["column"] for c in feats if ID_NAME.search(c["column"])),
                   flag_all_values_distinct=";".join(c["column"] for c in feats if c["all_values_distinct"] == "yes"
                                                     and (c["declared_type"] in ("nominal", "STRING")
                                                          or c["integer_valued"] == "yes")),
                   flag_string_typed=";".join(c["column"] for c in feats if c["declared_type"] == "STRING"),
                   flag_constant_columns=";".join(c["column"] for c in feats if c["n_distinct_observed"] in ("0", "1")),
                   n_columns_with_pseudo_missing_literals=str(sum(1 for c in feats if c["pseudo_missing_literals"])),
                   flag_leakage_candidates_by_name_NOT_MEASURED=LEAKAGE_CANDIDATES.get(name, ""),
                   note_redundancy_by_name_NOT_MEASURED=REDUNDANCY_NOTES.get(name, ""),
                   flag_differs_from_original=DIFFERS_FROM_ORIGINAL.get(name, ""))
        ds_out.append(row)
        for c in per_col:
            col_out.append(dict(dataset=name, openml_data_id=did, column_index=c["column_index"], column=c["column"],
                                is_target=c["is_target"], declared_type=c["declared_type"],
                                n_declared_nominal_values=c["n_declared_nominal_values"], n_missing=c["n_missing"],
                                n_distinct_observed=c["n_distinct_observed"], all_values_distinct=c["all_values_distinct"],
                                integer_valued=c["integer_valued"], pseudo_missing_literals=c["pseudo_missing_literals"]))
        print(f"{name}: rows {summary['n_rows']}, columns {summary['n_columns_incl_target']}, "
              f"missing {summary['n_missing_cells']}, classes {summary['class_counts']}, = OpenML qualities: {agree}")
    for fname, rows in (("measured-counts.csv", ds_out), ("measured-column-counts.csv", col_out)):
        with (ROOT / fname).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print(f"{len(ds_out)} datasets, {len(col_out)} columns written")


if __name__ == "__main__":
    main()
