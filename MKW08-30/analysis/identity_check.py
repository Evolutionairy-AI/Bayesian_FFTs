#!/usr/bin/env python3
"""Case-by-case check of the identity on the thirty: on every case, the certified tree must return the verdict
of additive Bayes over the certified attributes. Fitted on all cases, as the in-sample quantities are.

    python analysis/identity_check.py data          # the primary files
    python analysis/identity_check.py data-woike    # Woike's original files (Addendum A)
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(PKG), "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

v1.DATA = os.path.join(PKG, sys.argv[1])
cases = mismatches = 0
with open(os.path.join(PKG, "manifest.json"), encoding="utf-8") as f:
    datasets = json.load(f)["datasets"]
for ds in datasets:
    _, cols, cls = v2.prepare(ds["code"])
    counts = Counter(cls)
    c1 = "1" if counts["1"] >= counts["0"] else "0"
    y = [1 if c == c1 else 0 for c in cls]
    m = v2.fit(cols, y, range(len(y)))
    for r in range(len(y)):
        x = v2.cue_row(m, cols, r)
        _, tree, _, _, _ = v2.verdicts(m, x)
        s = m["l0"] + sum(m["lps"][i] if x[i] else m["lms"][i] for i in range(m["kmax"]))
        cases += 1
        mismatches += tree != (1 if s > 0 else 0)
print(f"{sys.argv[1]}: {cases} cases, {mismatches} mismatches between the certified tree and Bayes over the certified attributes")
