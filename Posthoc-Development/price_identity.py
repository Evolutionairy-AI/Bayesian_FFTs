"""POST HOC DEVELOPMENT on spent data (Holte's sixteen and the thirty of the 2008 study). Exploratory.
Touches no fresh collection. Written 2026-09-19, after the confirmatory run.

With two categories, whenever two classifiers disagree on a case, exactly one of them is right. Hence, on any
set of cases,
    acc(full Bayes) - acc(tree) = (1 - A) * (2q - 1),
where A is the share of cases on which they agree and q the share of disagreements in which full Bayes is
right. This script counts both sides exactly, in sample and out of sample, with the protocol, the seed and
the folds of the saved runs (it asserts that the saved cross-validated accuracies are reproduced).

    python price_identity.py        ->  price_identity_results.csv
"""
import csv
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402


def count(cols, y, rng):
    n = len(y)
    t = Counter()
    m = v2.fit(cols, y, range(n))
    outs = set()
    for r in range(n):
        _, sp, full, _, _ = v2.verdicts(m, v2.cue_row(m, cols, r))
        outs.add(sp)
        t["in_n"] += 1
        t["in_sp"] += sp == y[r]
        t["in_full"] += full == y[r]
        if sp != full:
            t["in_dis"] += 1
            t["in_dis_full_right"] += full == y[r]
    for _ in range(v2.REPEATS):
        for test in v2.stratified_folds(y, v2.FOLDS, rng):
            held = set(test)
            m = v2.fit(cols, y, [i for i in range(n) if i not in held])
            for r in test:
                _, sp, full, _, _ = v2.verdicts(m, v2.cue_row(m, cols, r))
                t["cv_n"] += 1
                t["cv_sp"] += sp == y[r]
                t["cv_full"] += full == y[r]
                if sp != full:
                    t["cv_dis"] += 1
                    t["cv_dis_full_right"] += full == y[r]
    for k in ("in", "cv"):  # the identity, in whole cases
        assert t[k + "_full"] - t[k + "_sp"] == 2 * t[k + "_dis_full_right"] - t[k + "_dis"], k
    return t, len(outs) > 1


def row(collection, code, t, both, saved):
    assert round(100 * t["cv_sp"] / t["cv_n"], 1) == float(saved["cv_acc_spine"]), (code, "cv tree accuracy not reproduced")
    assert round(100 * t["cv_full"] / t["cv_n"], 1) == float(saved["cv_acc_full"]), (code, "cv full accuracy not reproduced")
    out = {"collection": collection, "code": code, "n": t["in_n"], "tree_offers_both_verdicts": both}
    for k in ("in", "cv"):
        dis = t[k + "_dis"]
        out[k + "_agreement"] = round(100 * (1 - dis / t[k + "_n"]), 1)
        out[k + "_q_full_right_when_disagree"] = round(100 * t[k + "_dis_full_right"] / dis, 1) if dis else ""
        out[k + "_price_points"] = round(100 * (t[k + "_full"] - t[k + "_sp"]) / t[k + "_n"], 1)
    return out


def main():
    results = []
    # Holte's sixteen, in the order and with the random stream of the saved run
    saved = {r["code"]: r for r in csv.DictReader(open(os.path.join(DS, "Holte-16", "analysis", "indicator_results.csv"), newline=""))}
    rng = random.Random(v2.SEED)
    for code in v2.CODES:
        _, cols, cls = v2.prepare(code)
        maj = Counter(cls).most_common(1)[0][0]
        y = [1 if c == maj else 0 for c in cls]
        t, both = count(cols, y, rng)
        results.append(row("Holte-16", code, t, both, saved[code]))
        print(results[-1])
    # the thirty, likewise
    pkg = os.path.join(DS, "MKW08-30")
    saved = {r["code"]: r for r in csv.DictReader(open(os.path.join(pkg, "analysis", "confirmatory_results.csv"), newline=""))}
    v1.DATA = os.path.join(pkg, "data")
    rng = random.Random(v2.SEED)
    for ds in json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]:
        code = ds["code"]
        _, cols, cls = v2.prepare(code)
        counts = Counter(cls)
        c1 = "1" if counts["1"] >= counts["0"] else "0"
        y = [1 if c == c1 else 0 for c in cls]
        t, both = count(cols, y, rng)
        results.append(row("MKW08-30", code, t, both, saved[code]))
        print(results[-1])
    with open(os.path.join(HERE, "price_identity_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print("saved", len(results), "rows; identity held in whole cases everywhere; saved CV accuracies reproduced")


if __name__ == "__main__":
    main()
