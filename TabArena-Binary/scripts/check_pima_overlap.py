#!/usr/bin/env python3
"""Is TabArena's `diabetes` (OpenML 46921) the same table as PIMA in DATA_SETS/MKW08-30?

    python scripts/check_pima_overlap.py

Standard library only; reads ../MKW08-30/raw/PIMA/diabetes.arff without touching it.
Compares the two files as multisets of rows (8 numeric features as floats + class mapped to 0/1).
A row-identity count, nothing else. Writes build/pima_overlap_check.json.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import ROOT, read_header, split_line  # noqa: E402

POS = {"Yes": 1, "No": 0, "tested_positive": 1, "tested_negative": 0}


def rows(path):
    with open(path, encoding="utf-8", newline="") as fh:
        read_header(fh)
        out = Counter()
        for raw in fh:
            line = raw.strip()
            if line and not line.startswith("%"):
                v = split_line(line)
                out[tuple(float(x) for x in v[:-1]) + (POS[v[-1]],)] += 1
    return out


a = rows(ROOT / "raw/diabetes/diabetes.arff")
b = rows(ROOT.parent / "MKW08-30/raw/PIMA/diabetes.arff")
res = dict(tabarena_rows=sum(a.values()), mkw08_pima_rows=sum(b.values()),
           rows_in_both_as_multiset=sum((a & b).values()), identical_as_multisets=a == b)
(ROOT / "build/pima_overlap_check.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
print(res)
