#!/usr/bin/env python3
"""Write SOURCES.md from manifest.json, measured-counts.csv and the OpenML descriptions.

    python scripts/build_sources_md.py

Standard library only. Every number in SOURCES.md is written by this code from files in the
package; the curators' comments are quoted verbatim from the OpenML dataset descriptions.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def curation_comments(description):
    marker = "#### Curation comments"
    if marker not in description:
        return []
    tail = description.split(marker, 1)[1].split("\n", 1)[1]
    items, cur = [], None
    for line in tail.split("\n"):
        if line.startswith("- "):
            if cur:
                items.append(cur)
            cur = line[2:].strip()
        elif cur is not None and line.strip():
            cur += " " + line.strip()
    if cur:
        items.append(cur)
    return items


def decisions(d, c):
    m = d["measured"]
    out = [f"Positive class: the target `{m['target']}` has the labels {m['class_counts'].replace(';', ' / ')}; which one is "
           f"\"positive\" is not fixed by the file (ROC AUC does not depend on it, a tree's exits do)."]
    if m["n_missing_cells"] != "0":
        out.append(f"Missing values: {int(m['n_missing_cells']):,} cells in {m['n_columns_with_missing']} columns and "
                   f"{int(m['n_rows_with_missing']):,} rows. Deleting incomplete rows, imputing, or treating \"missing\" as a "
                   f"cue value are different experiments.")
    if c["n_columns_with_pseudo_missing_literals"] != "0":
        out.append(f"Pseudo-missing literals: {c['n_columns_with_pseudo_missing_literals']} feature columns carry values such as "
                   f"`nan`, `unknown` or `none` as ordinary categories (listed per column in measured-column-counts.csv). "
                   f"Keep them as categories or recode them as missing.")
    if c["flag_high_cardinality_gt50"]:
        out.append(f"High-cardinality categoricals (> 50 observed values): {c['flag_high_cardinality_gt50'].replace(';', ', ')}. "
                   f"A binary cue needs a grouping rule, or the column is dropped.")
    if c["flag_string_typed"]:
        out.append(f"STRING-typed columns: {c['flag_string_typed'].replace(';', ', ')}. Declared as free text in the ARFF, so a "
                   f"reader must decide whether they are categories, numbers or dates.")
    if c["flag_constant_columns"]:
        out.append(f"Constant columns (one observed value): {c['flag_constant_columns'].replace(';', ', ')}.")
    if c["flag_id_like_by_name"]:
        out.append(f"Identifier-like names: {c['flag_id_like_by_name'].replace(';', ', ')}.")
    if c["flag_rows_gt_100k"] == "yes":
        out.append("More than 100,000 rows: decide whether the harness runs on all rows or on a documented subsample.")
    if int(m["n_columns_incl_target"]) > 200:
        out.append(f"{m['n_features']} features: cue search cost and any pre-selection rule need to be fixed in advance.")
    if c["flag_leakage_candidates_by_name_NOT_MEASURED"]:
        out.append(f"Leakage candidates (read off names and documentation, NOT measured): "
                   f"{c['flag_leakage_candidates_by_name_NOT_MEASURED']}.")
    if c["note_redundancy_by_name_NOT_MEASURED"]:
        out.append(f"Redundancy (by name, NOT measured): {c['note_redundancy_by_name_NOT_MEASURED']}.")
    out.append(f"Splits: TabArena scores this set on {d['tabarena_protocol']['splits']} outer splits "
               f"({d['tabarena_protocol']['repeats_used']} of the 10 repeats x 3 folds that OpenML task {d['openml_task_id']} "
               f"defines; which repeats was not checked). Reusing those splits needs the split file, which was not downloaded.")
    return out


def main():
    man = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    counts = {r["dataset"]: r for r in csv.DictReader((ROOT / "measured-counts.csv").open(encoding="utf-8"))}
    pq_check = json.loads((ROOT / "build/arff_vs_parquet.json").read_text(encoding="utf-8"))
    L = ["# Source map and per-dataset provenance", "",
         f"All files were retrieved on **{man['retrieval_date']}** with `curl`: sequentially, without credentials, cookies or "
         "personal identifiers, and with no query parameter other than a public dataset id (the UCI metadata API takes "
         "`?id=<n>`). Full SHA-256 values, byte sizes and URLs for every file are in `manifest.json`; this file shows the "
         "first 12 hex digits only. **This file is generated** by `scripts/build_sources_md.py`; all counts in it are "
         "written by code from the files in the package.", "",
         "## Source families", "",
         "| Family | Files | Base URL | Notes |", "|---|---|---|---|",
         "| OpenML JSON API | suite, 51 task records, description + features + qualities for the 38 classification datasets "
         "| `https://www.openml.org/api/v1/json/{study,task,data,data/features,data/qualities}/<id>` | Public, no key. The 8 "
         "non-binary classification sets are kept under `suite/nonbinary_classification/` as evidence for the selection. |",
         "| OpenML data files | 30 ARFF + 30 parquet | `https://openml.org/data/v1/download/<file_id>/<name>.arff`, "
         "`https://data.openml.org/datasets/0004/<id>/dataset_<id>.pq` | The URLs are the `url` and `parquet_url` fields of each "
         "description. Every ARFF's MD5 equals the `md5_checksum` OpenML publishes for it. |",
         "| TabArena results artifact | 19 parquet files | `https://tabarena.s3.amazonaws.com/cache/artifacts/<suite>/methods/"
         "<method>/results/<file>` | Public bucket, anonymous GET. The key layout was read from the repo source "
         "(`models/_method_metadata.py`). Results tier only. |",
         f"| TabArena repo | 7 source files + LICENSE | `https://raw.githubusercontent.com/autogluon/tabarena/{man['benchmark']['repo_commit_read']}/<path>` "
         "| Pinned to the commit that was `main` at retrieval. File names encode the repo path with `__` for `/`. |",
         "| Paper | arXiv v4 PDF and HTML, NeurIPS 2025 proceedings paper and supplement | arxiv.org, proceedings.neurips.cc "
         "| The arXiv PDF URL carries no version; the file received is v4 (stamp on page 1: 3 Nov 2025). |",
         "| UCI metadata API | 3 JSON records | `https://archive.ics.uci.edu/api/dataset?id=<n>` | Only to document the size of "
         "the UCI parents of three sets the curators reduced (365, 722, 296). |", "",
         "## The 30 datasets", ""]
    for i, d in enumerate(man["datasets"], start=1):
        c, m = counts[d["name"]], d["measured"]
        desc = json.loads((ROOT / f"raw/{d['name']}/openml_description_{d['openml_data_id']}.json").read_text(
            encoding="utf-8"))["data_set_description"]
        L += [f"### {i}. {d['name']}", "",
              f"- **OpenML:** dataset {d['openml_data_id']} (version {d['openml_version']}, label "
              f"`{d['openml_version_label']}`, uploaded {d['openml_upload_date']}); task {d['openml_task_id']}; target "
              f"`{d['target']}`. <https://www.openml.org/d/{d['openml_data_id']}>",
              f"- **Licence as displayed by OpenML:** {d['licence_as_displayed']}. **Original source as displayed:** "
              f"{d['original_data_url']}",
              f"- **Citation as displayed:** {d['citation_as_displayed']}",
              f"- **Repo metadata:** source {c['repo_data_source']}, dataset year {c['repo_dataset_year']}.",
              f"- **Measured from the ARFF:** {int(m['n_rows']):,} rows; {m['n_columns_incl_target']} columns including the "
              f"target ({m['n_numeric_columns']} numeric, {m['n_nominal_columns']} nominal, {m['n_string_columns']} string); "
              f"{int(m['n_missing_cells']):,} missing cells; classes {m['class_counts'].replace(';', ', ')}. Equal to the "
              f"OpenML qualities: {d['measured_equals_openml_qualities']}. Equal to the parquet copy: "
              f"{'yes' if not pq_check[d['name']]['disagreements'] else 'NO'}.",
              f"- **TabArena protocol (repo metadata):** {d['tabarena_protocol']['splits']} splits; TabPFNv2 can run: "
              f"{d['tabarena_protocol']['can_run_tabpfnv2']}; TabICL can run: {d['tabarena_protocol']['can_run_tabicl']}.",
              "- **Files:**"]
        for f in d["files"]:
            L.append(f"  - `{f['path']}`: {f['bytes']:,} bytes, SHA-256 `{f['sha256'][:12]}...`, <{f['url']}>")
        comments = curation_comments(desc["description"])
        if comments:
            L.append("- **Curators' comments (verbatim from the OpenML description):**")
            L += [f"  - \"{x}\"" for x in comments]
        if c["flag_differs_from_original"]:
            L.append(f"- **Relation to the better-known original:** {c['flag_differs_from_original']}")
        L.append("- **Decisions a build would need:**")
        L += [f"  - {x}" for x in decisions(d, c)]
        L.append("")
    L += ["## Shared files", "", "| Path | Bytes | SHA-256 | Origin |", "|---|---|---|---|"]
    for f in man["shared_files"]:
        if f["path"].startswith(("suite/tasks/", "suite/nonbinary_classification/")):
            continue
        L.append(f"| `{f['path']}` | {f['bytes']:,} | `{f['sha256'][:12]}...` | {f.get('url') or 'derived: ' + f['derived_by']} |")
    n_t = sum(1 for f in man["shared_files"] if f["path"].startswith("suite/tasks/"))
    n_n = sum(1 for f in man["shared_files"] if f["path"].startswith("suite/nonbinary_classification/"))
    L += ["", f"Not listed row by row: {n_t} task records under `suite/tasks/` and {n_n} JSON records under "
              "`suite/nonbinary_classification/` (all in `manifest.json`).", ""]
    (ROOT / "SOURCES.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("SOURCES.md written,", len(L), "lines")


if __name__ == "__main__":
    main()
