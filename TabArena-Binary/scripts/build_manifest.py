#!/usr/bin/env python3
"""Write manifest.json: every pinned file with URL, retrieval date, bytes and SHA-256.

    python scripts/build_manifest.py

Standard library only. Run after measure_counts.py and build_published_results.py.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETRIEVED = "2026-09-19"
REPO_COMMIT = "60d0f66771c87bb8a255c3d595476119324aaf41"
API = "https://www.openml.org/api/v1/json"
BUCKET = "https://tabarena.s3.amazonaws.com/cache/artifacts"
DERIVED = {
    "references/TabArena_arXiv_2506.16791v4_pypdf_text.txt": "pypdf text layer of the arXiv PDF, page by page",
    "references/TabArena_arXiv_2506.16791v4_TableF1_parsed.csv": "scripts/parse_pdf_table_f1.py on the arXiv PDF",
    "references/TabArena_arXiv_2506.16791v4_TableF1_html_parsed.csv": "scripts/crosscheck_pdf_vs_html.py on the arXiv HTML",
    "references/TabArena_NeurIPS2025_Paper_TableF1_parsed.csv": "scripts/parse_pdf_table_f1.py on the proceedings PDF",
}
REFERENCE_URLS = {
    "references/TabArena_arXiv_2506.16791v4.pdf": "https://arxiv.org/pdf/2506.16791",
    "references/TabArena_arXiv_2506.16791v4.html": "https://arxiv.org/html/2506.16791v4",
    "references/TabArena_NeurIPS2025_Paper.pdf": "https://proceedings.neurips.cc/paper_files/paper/2025/file/"
                                                 "1697e3fb412da11dc9488249f9e7bbc9-Paper-Datasets_and_Benchmarks_Track.pdf",
    "references/TabArena_NeurIPS2025_Supplemental.pdf": "https://proceedings.neurips.cc/paper_files/paper/2025/file/"
                                                        "1697e3fb412da11dc9488249f9e7bbc9-Supplemental-Datasets_and_Benchmarks_Track.pdf",
}


def entry(rel, url=None, origin="downloaded", **extra):
    p = ROOT / rel
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    e = dict(path=rel, bytes=p.stat().st_size, sha256=h.hexdigest(), origin=origin)
    if url:
        e.update(url=url, retrieved=RETRIEVED)
    e.update(extra)
    return e


def shared_url(rel):
    parts = rel.split("/")
    if rel in REFERENCE_URLS:
        return REFERENCE_URLS[rel]
    if rel == "suite/study_457.json":
        return f"{API}/study/457"
    if parts[:2] == ["suite", "tasks"]:
        return f"{API}/task/{parts[2][5:-5]}"
    if parts[:2] == ["suite", "nonbinary_classification"]:
        did, kind = parts[2][:-5].split("_")
        return f"{API}/data/{'' if kind == 'description' else kind + '/'}{did}"
    if parts[:2] == ["references", "tabarena_repo"]:
        repo_path = parts[2].replace("___", "/_").replace("__", "/")
        return f"https://raw.githubusercontent.com/autogluon/tabarena/{REPO_COMMIT}/{repo_path}"
    if parts[:2] == ["references", "uci_metadata"]:
        return f"https://archive.ics.uci.edu/api/dataset?id={parts[2][4:-5]}"
    if parts[0] == "results_artifact":
        return f"{BUCKET}/{'/'.join(parts[1:])}"
    raise KeyError(rel)


def main():
    plan = [l.rstrip("\n").split("\t") for l in (ROOT / "build/download_plan.tsv").open(encoding="utf-8")]
    counts = {r["dataset"]: r for r in csv.DictReader((ROOT / "measured-counts.csv").open(encoding="utf-8"))}
    measured_keys = ["n_rows", "n_columns_incl_target", "n_features", "n_numeric_columns", "n_nominal_columns",
                     "n_string_columns", "n_date_columns", "n_missing_cells", "n_rows_with_missing",
                     "n_columns_with_missing", "n_data_lines_with_wrong_field_count", "target",
                     "target_declared_values", "class_counts", "target_missing"]
    flag_keys = [k for k in next(iter(counts.values())) if k.startswith(("flag_", "note_", "n_columns_with_pseudo"))]
    datasets = []
    for name, tid, did, arff_url, pq_url, md5 in plan:
        c = counts[name]
        desc = json.loads((ROOT / f"raw/{name}/openml_description_{did}.json").read_text(encoding="utf-8"))["data_set_description"]
        arff = f"raw/{name}/{arff_url.rsplit('/', 1)[1]}"
        files = [entry(arff, arff_url, openml_md5=md5, role="primary data file (ARFF, plain text)"),
                 entry(f"raw/{name}/{pq_url.rsplit('/', 1)[1]}", pq_url, role="OpenML's parquet copy of the same table"),
                 entry(f"raw/{name}/openml_description_{did}.json", f"{API}/data/{did}", role="OpenML dataset description"),
                 entry(f"raw/{name}/openml_features_{did}.json", f"{API}/data/features/{did}", role="OpenML feature list"),
                 entry(f"raw/{name}/openml_qualities_{did}.json", f"{API}/data/qualities/{did}", role="OpenML qualities")]
        datasets.append(dict(
            name=name, openml_data_id=int(did), openml_task_id=int(tid), openml_version=int(desc["version"]),
            openml_version_label=desc.get("version_label"), openml_upload_date=desc.get("upload_date"),
            licence_as_displayed=desc.get("licence"), original_data_url=desc.get("original_data_url"),
            citation_as_displayed=desc.get("citation"), target=c["target"], status="acquired",
            task_record=f"suite/tasks/task_{tid}.json",
            openml_split_file_url_NOT_DOWNLOADED=f"https://openml.org/api_splits/get/{tid}/Task_{tid}_splits.arff",
            tabarena_protocol=dict(outer_folds=int(c["tabarena_folds"]), repeats_used=int(c["tabarena_repeats"]),
                                   splits=int(c["tabarena_splits"]), can_run_tabpfnv2=c["repo_can_run_tabpfnv2"],
                                   can_run_tabicl=c["repo_can_run_tabicl"]),
            primary_data_file=arff, files=files,
            measured={k: c[k] for k in measured_keys},
            measured_equals_openml_qualities=c["measured_equals_openml_qualities"],
            flags={k: c[k] for k in flag_keys if c[k] not in ("", "no", "0")}))

    listed = {f["path"] for d in datasets for f in d["files"]}
    shared = []
    for top in ("suite", "references", "results_artifact"):
        for p in sorted((ROOT / top).rglob("*")):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and rel not in listed:
                shared.append(entry(rel, origin="derived", derived_by=DERIVED[rel]) if rel in DERIVED
                              else entry(rel, shared_url(rel)))

    pub = list(csv.DictReader((ROOT / "published_results.csv").open(encoding="utf-8")))
    manifest = dict(
        schema_version="1.0",
        package_name="TabArena-Binary raw-acquisition package",
        stage="raw acquisition only; no built data files; HELD OUT for a pre-specified confirmatory run",
        created_utc_date=RETRIEVED, retrieval_date=RETRIEVED,
        benchmark=dict(
            title="TabArena: A Living Benchmark for Machine Learning on Tabular Data",
            authors="Nick Erickson, Lennart Purucker, Andrej Tschalzev, David Holzmueller, Prateek Mutalik Desai, "
                    "David Salinas, Frank Hutter",
            venue="NeurIPS 2025, Datasets and Benchmarks Track; arXiv:2506.16791v4 (3 Nov 2025)",
            openml_suite=457, openml_suite_alias="tabarena-v0.1", repo="https://github.com/autogluon/tabarena",
            repo_commit_read=REPO_COMMIT),
        selection_rule="OpenML suite 457 lists 51 tasks; 38 are Supervised Classification; the 30 whose target feature "
                       "declares exactly two nominal values are kept. The same 30 are marked problem_type=binary in the "
                       "repo's curated_tabarena_dataset_metadata.csv and carry the AUC metric in Table F.1.",
        counting_rules=dict(
            row="a non-empty, non-comment line after @DATA with as many fields as declared attributes",
            missing="an unquoted '?' (the ARFF missing token). OpenML's feature records and the parquet nulls agree with "
                    "this on every column.",
            pseudo_missing="literal values such as nan, unknown, Not Available are ordinary values in the files and are "
                           "NOT counted as missing; they are tallied per column in measured-column-counts.csv",
            distinct="exact for nominal and STRING columns; for numeric columns exact up to 1000, else '>1000'"),
        tools=dict(downloader="curl (sequential, at most two retries, no credentials)",
                   python="3.13", build_only_third_party=["pypdf 6.10.2", "pandas", "pyarrow"],
                   verifier="scripts/verify.py, standard library only"),
        published_results=dict(
            file="published_results.csv", rows=len(pub),
            models=sorted({r["model"] for r in pub}), regimes=["default", "tuned", "tuned_ensemble"], metric="roc_auc",
            pdf_dataset_name_aliases={"HR_Analytics_Job_Change_of_Data_Scientists": "HR_Analytics_Job_Change"},
            crosscheck_status_counts=dict(Counter(r["crosscheck"] for r in pub)),
            artifact_suites={"tabarena-2025-06-12": "all methods except Linear and KNN",
                             "tabarena-2025-10-20": "LinearModel and KNeighbors (camera-ready re-run)"}),
        not_acquired=[dict(item="OpenML task split files (Task_<id>_splits.arff)", reason="not needed for counting; public, "
                           "one URL per dataset recorded under openml_split_file_url_NOT_DOWNLOADED"),
                      dict(item="TabArena raw and processed prediction artifacts", reason="about 100 GB and 10 GB per "
                           "method according to the repo README; only the small results tier was taken"),
                      dict(item="original upstream sources (Kaggle, UCI, FICO)", reason="Kaggle downloads are gated behind "
                           "a login; this package holds the OpenML versions that TabArena evaluates")],
        datasets=datasets, shared_files=shared)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    n = sum(len(d["files"]) for d in datasets) + len(shared)
    size = sum(f["bytes"] for d in datasets for f in d["files"]) + sum(f["bytes"] for f in shared)
    print(f"manifest.json: {len(datasets)} datasets, {n} files, {size} bytes pinned")


if __name__ == "__main__":
    main()
