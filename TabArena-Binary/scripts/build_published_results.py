#!/usr/bin/env python3
"""Build published_results.csv for the 30 binary TabArena-v0.1 datasets.

    python scripts/build_published_results.py

Build step only (needs pandas + pyarrow to read the parquet artifacts).
Two renderings of the same published results are put side by side, cell by cell:

  PDF       Table F.1 of arXiv:2506.16791v4, parsed by scripts/parse_pdf_table_f1.py:
            mean±s.d. of ROC AUC over splits, printed to three decimals, "-" where absent.
  ARTIFACT  the authors' cached results (public S3 bucket): one row per (dataset, split, method
            variant) with metric_error = 1 - ROC AUC. The camera-ready collection is used, as
            defined in the repo (contexts/tabarena/methods.py, `methods_2025_10_20_camera_ready`):
            suite tabarena-2025-06-12 for every method except LinearModel and KNeighbors, which
            were re-run and come from suite tabarena-2025-10-20. The superseded 2025-06-12
            Linear/KNN values are written to published_results_superseded_linear_knn.csv.

The ONLY arithmetic done here is collapsing the artifact to the granularity of the table:
the mean and the sample s.d. (ddof=1) over splits of the published per-split AUC = 1 -
metric_error. No margin, difference between models, rank or best-of is computed, and no
dataset under raw/ is opened.

Writes published_results.csv and published_results_crosscheck.json.
"""
import csv
import json
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "results_artifact"
PDF_CSV = ROOT / "references" / "TabArena_arXiv_2506.16791v4_TableF1_parsed.csv"
BUCKET = "https://tabarena.s3.amazonaws.com/cache/artifacts"
RERUN_SUITE = {"LinearModel": "tabarena-2025-10-20", "KNeighbors": "tabarena-2025-10-20"}

# Table F.1 row label -> artifact method folder (ta_name), in the order of the table
MODEL_MAP = [("RF", "RandomForest"), ("ExtraTrees", "ExtraTrees"), ("XGBoost", "XGBoost"),
             ("LightGBM", "LightGBM"), ("CatBoost", "CatBoost"), ("EBM", "ExplainableBM"),
             ("FastAIMLP", "NeuralNetFastAI"), ("TorchMLP", "NeuralNetTorch"), ("RealMLP", "RealMLP"),
             ("TabM", "TabM_GPU"), ("MNCA", "ModernNCA_GPU"), ("TabPFNv2", "TabPFNv2_GPU"),
             ("TabDPT", "TabDPT_GPU"), ("TabICL", "TabICL_GPU"), ("Linear", "LinearModel"),
             ("KNN", "KNeighbors"), ("AutoGluon", "AutoGluon_v130")]
REGIMES = ["default", "tuned", "tuned_ensemble"]
PDF_NAME = {"HR_Analytics_Job_Change_of_Data_Scientists": "HR_Analytics_Job_Change"}


def r3(x):
    return str(Decimal(repr(float(x))).quantize(Decimal("0.001"), rounding=ROUND_HALF_EVEN))


def main():
    plan = [l.rstrip("\n").split("\t") for l in (ROOT / "build/download_plan.tsv").open(encoding="utf-8")]
    datasets = [(p[0], p[1], p[2]) for p in plan]  # name, task id, data id
    pdf = {(r["dataset"], r["model"], r["regime"]): r for r in csv.DictReader(PDF_CSV.open(encoding="utf-8"))
           if r["metric"] == "AUC"}

    def collapse(folder, suite):
        fname = "model_results.parquet" if folder == "AutoGluon_v130" else "hpo_results.parquet"
        rel = f"{suite}/methods/{folder}/results/{fname}"
        df = pd.read_parquet(ART / rel)
        df = df[df["problem_type"] == "binary"]
        assert set(df["metric"]) == {"roc_auc"}, folder
        if folder == "AutoGluon_v130":  # a system: one entry, printed in the Tuned + Ens. column
            df = df.assign(method_subtype="tuned_ensemble")
        res = {}
        for (ds, regime), g in df.groupby(["dataset", "method_subtype"]):
            assert g["fold"].is_unique
            auc = 1.0 - g["metric_error"]
            res[(ds, regime)] = dict(n=len(g), n_imputed=int(g["imputed"].sum()),
                                     impute_method=";".join(sorted(set(g["impute_method"].dropna()))),
                                     mean=auc.mean(), sd=auc.std(ddof=1), file=rel, suite=suite)
        return res

    art = {}
    for label, folder in MODEL_MAP:
        for (ds, regime), v in collapse(folder, RERUN_SUITE.get(folder, "tabarena-2025-06-12")).items():
            art[(ds, label, regime)] = v

    out, stats, disagreements = [], {}, []
    for name, tid, did in datasets:
        for label, folder in MODEL_MAP:
            for regime in REGIMES:
                p = pdf[(PDF_NAME.get(name, name), label, regime)]
                a = art.get((name, label, regime))
                printed = p["mean_as_printed"] != "-"
                if a is None:
                    status = "pdf_value_artifact_absent" if printed else "not_run_dash_in_pdf_absent_in_artifact"
                elif a["n_imputed"] == a["n"]:
                    status = "pdf_value_artifact_imputed" if printed else "not_run_dash_in_pdf_imputed_in_artifact"
                elif not printed:
                    status = "pdf_dash_artifact_value"
                else:
                    ok_mean = r3(a["mean"]) == p["mean_as_printed"]
                    ok_sd = r3(a["sd"]) == p["sd_as_printed"]
                    status = "agree" if ok_mean and ok_sd else ("agree_mean_only" if ok_mean else "DISAGREE")
                stats[status] = stats.get(status, 0) + 1
                row = dict(dataset=name, openml_data_id=did, openml_task_id=tid, model=label, artifact_method=folder,
                           regime=regime, metric="roc_auc", artifact_suite="" if a is None else a["suite"],
                           published_auc_mean_pdf="" if not printed else p["mean_as_printed"],
                           published_auc_sd_pdf="" if not printed else p["sd_as_printed"],
                           pdf_page=p["pdf_page"],
                           artifact_n_splits="" if a is None else a["n"],
                           artifact_n_splits_imputed="" if a is None else a["n_imputed"],
                           artifact_impute_method="" if a is None else a["impute_method"],
                           artifact_auc_mean="" if a is None else f"{a['mean']:.6f}",
                           artifact_auc_sd="" if a is None else f"{a['sd']:.6f}",
                           crosscheck=status,
                           source=f"PDF: Erickson et al., arXiv:2506.16791v4, Table F.1, PDF page {p['pdf_page']}"
                                  + ("" if a is None else f" | ARTIFACT: {BUCKET}/{a['file']}"))
                out.append(row)
                if status not in ("agree", "not_run_dash_in_pdf_absent_in_artifact",
                                  "not_run_dash_in_pdf_imputed_in_artifact"):
                    disagreements.append({k: row[k] for k in ("dataset", "model", "regime", "published_auc_mean_pdf",
                                                              "published_auc_sd_pdf", "artifact_auc_mean",
                                                              "artifact_auc_sd", "artifact_n_splits",
                                                              "artifact_n_splits_imputed", "crosscheck")})
    with (ROOT / "published_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    # superseded first-run values of the two re-run baselines, for the record
    sup = []
    for label, folder in MODEL_MAP:
        if folder not in RERUN_SUITE:
            continue
        old = collapse(folder, "tabarena-2025-06-12")
        for name, tid, did in datasets:
            for regime in REGIMES:
                a = old[(name, regime)]
                pr = pdf[(PDF_NAME.get(name, name), label, regime)]
                same = (a["n_imputed"] == 0 and r3(a["mean"]) == pr["mean_as_printed"]
                        and r3(a["sd"]) == pr["sd_as_printed"])
                sup.append(dict(dataset=name, openml_data_id=did, model=label, artifact_method=folder, regime=regime,
                                published_auc_mean_pdf=pr["mean_as_printed"], published_auc_sd_pdf=pr["sd_as_printed"],
                                superseded_value_equals_published_to_3dp="yes" if same else "no",
                                artifact_suite=a["suite"], artifact_n_splits=a["n"],
                                artifact_n_splits_imputed=a["n_imputed"], artifact_impute_method=a["impute_method"],
                                artifact_auc_mean=f"{a['mean']:.6f}", artifact_auc_sd=f"{a['sd']:.6f}",
                                source=f"ARTIFACT (superseded, NOT the camera-ready table): {BUCKET}/{a['file']}"))
    with (ROOT / "published_results_superseded_linear_knn.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sup[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sup)
    # a readable sample of the full cross-check: one printed cell per dataset, chosen by position only
    others = {}
    for tag, fname in (("html", "TabArena_arXiv_2506.16791v4_TableF1_html_parsed.csv"),
                       ("neurips_pdf", "TabArena_NeurIPS2025_Paper_TableF1_parsed.csv")):
        others[tag] = {(r["dataset"], r["model"], r["regime"]): r["mean_as_printed"] + "±" + r["sd_as_printed"]
                       for r in csv.DictReader((ROOT / "references" / fname).open(encoding="utf-8")) if r["metric"] == "AUC"}
    sample = []
    for i, (name, tid, did) in enumerate(datasets):
        block = [r for r in out if r["dataset"] == name and r["published_auc_mean_pdf"]]
        r = block[(7 * i) % len(block)]
        key = (PDF_NAME.get(name, name), r["model"], r["regime"])
        sample.append(dict(dataset=name, model=r["model"], regime=r["regime"],
                           arxiv_pdf=r["published_auc_mean_pdf"] + "±" + r["published_auc_sd_pdf"],
                           arxiv_html=others["html"][key], neurips_pdf=others["neurips_pdf"][key],
                           artifact_mean_sd=r["artifact_auc_mean"] + "±" + r["artifact_auc_sd"],
                           artifact_n_splits=r["artifact_n_splits"], crosscheck=r["crosscheck"]))
    with (ROOT / "build" / "spot_check_sample.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sample[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sample)
    n_same = sum(r["superseded_value_equals_published_to_3dp"] == "yes" for r in sup)
    report = dict(cells=len(out), status_counts=stats, cells_not_in_plain_agreement=disagreements,
                  superseded_linear_knn=dict(cells=len(sup), equal_to_published_table_to_3dp=n_same,
                                             different_from_published_table=len(sup) - n_same))
    (ROOT / "published_results_crosscheck.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(len(out), "cells;", stats)
    print("superseded Linear/KNN cells:", report["superseded_linear_knn"])
    for d in disagreements:
        print(d)


if __name__ == "__main__":
    main()
