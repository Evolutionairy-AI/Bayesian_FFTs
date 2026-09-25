#!/usr/bin/env python3
"""Independent check of the ARFF counts against OpenML's parquet copy of each dataset.

    python scripts/crosscheck_arff_vs_parquet.py

Build step only (needs pyarrow). The standard-library ARFF counter in verify.py and pyarrow's
parquet reader share no code, so agreement here means the ARFF parser counted correctly and that
the two files OpenML serves for a dataset hold the same table.
Compared per dataset: row count, column count, column names in order; per column: number of
missing cells (ARFF '?' vs parquet null) and, for non-numeric columns, the number of distinct
values; for the target: the class counts. COUNTS ONLY.
Writes build/arff_vs_parquet.json; exits nonzero on any disagreement.
"""
import csv
import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]


def main():
    ds = list(csv.DictReader((ROOT / "measured-counts.csv").open(encoding="utf-8")))
    cols = {}
    for r in csv.DictReader((ROOT / "measured-column-counts.csv").open(encoding="utf-8")):
        cols.setdefault(r["dataset"], []).append(r)
    report, n_bad = {}, 0
    for d in ds:
        name = d["dataset"]
        t = pq.read_table(ROOT / f"raw/{name}/dataset_{d['openml_data_id']}.pq")
        bad = []
        if t.num_rows != int(d["n_rows"]):
            bad.append(f"rows {t.num_rows} vs {d['n_rows']}")
        if t.num_columns != int(d["n_columns_incl_target"]):
            bad.append(f"columns {t.num_columns} vs {d['n_columns_incl_target']}")
        if t.column_names != [c["column"] for c in cols[name]]:
            bad.append("column names or order differ")
        else:
            for c in cols[name]:
                col = t.column(c["column"])
                if col.null_count != int(c["n_missing"]):
                    bad.append(f"{c['column']}: nulls {col.null_count} vs missing {c['n_missing']}")
                if c["declared_type"] in ("nominal", "STRING"):
                    if pa.types.is_dictionary(col.type):
                        col = col.cast(col.type.value_type)
                    n = pc.count_distinct(col, mode="only_valid").as_py()
                    if n != int(c["n_distinct_observed"]):
                        bad.append(f"{c['column']}: distinct {n} vs {c['n_distinct_observed']}")
            tgt = t.column(d["target"])
            if pa.types.is_dictionary(tgt.type):
                tgt = tgt.cast(tgt.type.value_type)
            # parquet stores some {False, True} nominals as bool, which prints as false/true
            fix = (lambda v: v.capitalize()) if pa.types.is_boolean(tgt.type) else (lambda v: v)
            vc = ";".join(f"{k}={v}" for k, v in sorted(
                (fix(x["values"]), x["counts"]) for x in pc.value_counts(tgt.cast(pa.string())).to_pylist()))
            if vc != d["class_counts"]:
                bad.append(f"class counts {vc} vs {d['class_counts']}")
        bools = [f.name for f in t.schema if pa.types.is_boolean(f.type)]
        report[name] = dict(parquet_rows=t.num_rows, parquet_columns=t.num_columns,
                            parquet_boolean_columns=bools, disagreements=bad)
        n_bad += bool(bad)
        print(("AGREE " if not bad else "DIFFER"), name, "" if not bad else bad[:6])
    (ROOT / "build/arff_vs_parquet.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"{len(ds) - n_bad} of {len(ds)} datasets agree")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
