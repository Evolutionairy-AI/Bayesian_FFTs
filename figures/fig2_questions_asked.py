"""Questions each Figure 2 tree actually asks, beside its certified depth (2026-09-24).
The certified depth d (harness kmax, the 'questions' column of Fig2_price_data_2026-09-23.csv) counts the leading
attributes that satisfy condition (1); the tree ends earlier when both answers at a level settle the verdict, so
it asks l <= d questions on its longest path. Refits on all cases with the harness, as for the in-sample quantities;
spent data only (Holte-16 and the public reconstruction of the thirty; Woike's files untouched).
    python fig2_questions_asked.py   ->  Fig2_questions_asked_2026-09-24.csv
"""
import csv
import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "..")  # the repository root
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

fig = list(csv.DictReader(open(os.path.join(HERE, "Fig2_price_data_2026-09-23.csv"), encoding="utf-8")))
want = {r["code"]: r for r in fig}


def tree_facts(cols, y):
    m = v2.fit(cols, y, range(len(y)))
    d, spine = m["kmax"], m["spine"]
    profiles = list(itertools.product((0, 1), repeat=d))
    for x in profiles:  # Result 1 on every profile of the certified attributes
        s = m["l0"] + sum(m["lps"][i] if x[i] else m["lms"][i] for i in range(d))
        assert v1.spine_classify(spine, list(x)) == (1 if s > 0 else 0)
    both = len({v1.spine_classify(spine, list(x)) for x in profiles}) > 1
    return d, len(spine), both


out = []
for code in v2.CODES:
    if code in want:
        _, cols, cls = v2.prepare(code)
        maj = Counter(cls).most_common(1)[0][0]
        out.append(("Holte-16", code, *tree_facts(cols, [1 if c == maj else 0 for c in cls])))
pkg = os.path.join(DS, "MKW08-30")
v1.DATA = os.path.join(pkg, "data")
for ds in json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]:
    if ds["code"] in want:
        _, cols, cls = v2.prepare(ds["code"])
        cnt = Counter(cls)
        c1 = "1" if cnt["1"] >= cnt["0"] else "0"
        out.append(("MKW08-30", ds["code"], *tree_facts(cols, [1 if c == c1 else 0 for c in cls])))

assert len(out) == 30
for coll, code, d, asked, both in out:
    assert both and d == int(want[code]["questions"]) and 1 <= asked <= d, code
with open(os.path.join(HERE, "Fig2_questions_asked_2026-09-24.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["collection", "code", "certified_depth", "questions_asked"])
    w.writerows((c, k, d, a) for c, k, d, a, _ in out)
print("questions asked:", Counter(a for *_, a, _ in out), "| stop before depth:", [k for _, k, d, a, _ in out if a < d])
