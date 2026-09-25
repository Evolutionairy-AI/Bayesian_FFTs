#!/usr/bin/env python3
"""Build the harness files for the 29 TabArena binary tasks of Addendum B (section 2, items 2 to 4).

Converts each ARFF file of raw/ to the layout the harness reads: data/<dataset>.csv with a header row and the
criterion moved to the last column as `class`. Reuses the package's own verified ARFF reader (scripts/verify.py).
The ARFF token ? becomes the protocol's missing value ?; a quoted '?' stays a value; literal strings such as
nan or unknown stay ordinary values. Also writes data/declared_types.json (numeric or nominal per attribute, from
the ARFF declarations) for the internal benchmarks. Asserts rows, attributes and class counts against
measured-counts.csv. Relates nothing to the target.

    python scripts/tabarena_build.py
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify import MISSING, QUOTED_QM, read_header, split_line  # noqa: E402

EXCLUDED = {"diabetes"}  # the Pima data, already analyzed as PIMA in the thirty (Addendum B, section 2, item 2)
NUMERIC = {"NUMERIC", "REAL", "INTEGER"}


def main():
    counts = {r["dataset"]: r for r in csv.DictReader(open(ROOT / "measured-counts.csv", encoding="utf-8"))}
    out_dir = ROOT / "data"
    out_dir.mkdir(exist_ok=True)
    types = {}
    for name, c in sorted(counts.items(), key=lambda t: int(t[1]["n_rows"])):
        if name in EXCLUDED:
            continue
        path = ROOT / "raw" / name / f"{name}.arff"
        target = c["target"]
        with open(path, encoding="utf-8", newline="") as fh:
            attrs = read_header(fh)
            names = [a[0] for a in attrs]
            ti = names.index(target)
            feats = [i for i in range(len(attrs)) if i != ti]
            rows = []
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("%"):
                    continue
                row = split_line(line)
                assert len(row) == len(attrs), (name, "field count")
                vals = [MISSING if v == MISSING else ("'?'" if v == QUOTED_QM else v) for v in row]
                assert vals[ti] != MISSING, (name, "missing criterion")
                rows.append([vals[i] for i in feats] + [vals[ti]])
        assert len(rows) == int(c["n_rows"]), (name, len(rows))
        assert len(feats) == int(c["n_features"]), name
        measured = dict(kv.split("=") for kv in c["class_counts"].split(";"))
        got = Counter(r[-1] for r in rows)
        assert {k: str(v) for k, v in got.items()} == measured, (name, got, measured)
        header = [names[i] for i in feats]
        assert "class" not in header and len(set(header)) == len(header), name
        with open(out_dir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header + ["class"])
            w.writerows(rows)
        types[name] = [("numeric" if attrs[i][1] in NUMERIC else "nominal") for i in feats]
        print(f"{name}: {len(rows)} rows, {len(feats)} attributes, classes {dict(got)}")
    with open(out_dir / "declared_types.json", "w", encoding="utf-8") as f:
        json.dump(types, f, indent=1)
    print(len(types), "datasets built")


if __name__ == "__main__":
    main()
