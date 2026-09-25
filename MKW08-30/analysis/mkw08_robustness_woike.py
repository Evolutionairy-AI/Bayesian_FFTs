#!/usr/bin/env python3
"""Robustness run on Woike's original files. Follows analysis/ADDENDUM_A_FROZEN.md (section 2, item 6 of
analysis/PRESPECIFICATION_FROZEN.md). NOT confirmatory: the results of the primary analysis were known.

    python analysis/mkw08_robustness_woike.py      # refuses to run until the addendum is approved and frozen

A copy of mkw08_confirmatory.py that differs in three things: the data folder (data-woike/, written by
scripts/mkw08_build_woike.py), the names of the output files, and the refusal below. Protocol, indicator,
tests, seeds and permutations are unchanged.
"""
import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
HOLTE = os.path.join(os.path.dirname(PKG), "Holte-16", "analysis")
sys.path.insert(0, HOLTE)
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

FROZEN = os.path.join(HERE, "PRESPECIFICATION_FROZEN.md")
ADDENDUM = os.path.join(HERE, "ADDENDUM_A_FROZEN.md")
PERMS = 20000


def one_sided(xs, ys, sign, rng):
    """Spearman rho and the permutation p-value for the pre-specified direction."""
    obs = v1.spearman(xs, ys)
    ys, hits = list(ys), 0
    for _ in range(PERMS):
        rng.shuffle(ys)
        hits += sign * v1.spearman(xs, ys) >= sign * obs - 1e-12
    return round(obs, 3), round((hits + 1) / (PERMS + 1), 4)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    for path in (FROZEN, ADDENDUM):
        if not os.path.exists(path):
            sys.exit(f"REFUSED: analysis/{os.path.basename(path)} does not exist. "
                     "The addendum must be approved and frozen before this run.")
    out_csv = os.path.join(HERE, "robustness_woike_results.csv")
    if os.path.exists(out_csv):
        sys.exit("REFUSED: robustness_woike_results.csv exists. The run is made once.")

    with open(os.path.join(PKG, "manifest.json"), encoding="utf-8") as f:
        datasets = json.load(f)["datasets"]  # Tabelle 6.9 order
    bench = {}
    with open(os.path.join(HERE, "woike_tables_6_10_to_6_12.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["block"] == "pred90" and r["model"] in ("LR", "CT", "VF"):
                bench[(r["dataset"], r["model"])] = float(r["accuracy"])

    v1.DATA = os.path.join(PKG, "data-woike")
    rng = random.Random(v2.SEED)
    results = []
    for ds in datasets:
        code, label = ds["code"], ds["woike_label"]
        header, cols, cls = v2.prepare(code)
        counts = Counter(cls)
        c1 = "1" if counts["1"] >= counts["0"] else "0"  # the larger side; a tie goes to his category 1
        y = [1 if c == c1 else 0 for c in cls]
        _, r = v2.in_sample(cols, y)
        r.update(v2.cross_validate(cols, y, rng))
        lr, ct, zig = bench[(label, "LR")], bench[(label, "CT")], bench[(label, "VF")]
        r = {"code": code, "n": len(y), "attributes": len(header),
             "base_rate": round(100 * sum(y) / len(y), 1), **r,
             "woike_LR": lr, "woike_CART": ct, "woike_Zig": zig,
             "margin_H1": max(lr, ct) - zig, "margin_CART": ct - zig}
        r["cv_gap_full_minus_spine"] = round(r["cv_acc_full"] - r["cv_acc_spine"], 1)
        results.append(r)
        print(f"{code}: Ak={r['Ak_agree_spine']} kmax={r['kmax']} CV spine={r['cv_acc_spine']} "
              f"full={r['cv_acc_full']} margin={r['margin_H1']}")

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    perm = random.Random(v2.SEED)
    ak = lambda rows: [r["Ak_agree_spine"] for r in rows]  # noqa: E731
    no_hv = [r for r in results if r["code"] not in ("HORS", "VOTE")]
    nondeg = [r for r in results if r["spine_nondegenerate"]]
    tests = {
        "H1_Ak_vs_margin": one_sided(ak(results), [r["margin_H1"] for r in results], -1, perm),
        "H2_Ak_vs_cv_spine_accuracy": one_sided(ak(results), [r["cv_acc_spine"] for r in results], +1, perm),
        "S_a_H1_without_HORS_VOTE": one_sided(ak(no_hv), [r["margin_H1"] for r in no_hv], -1, perm),
        "S_b_H1_CART_minus_Zig": one_sided(ak(results), [r["margin_CART"] for r in results], -1, perm),
        "S_c_H1_nondegenerate_only": one_sided(ak(nondeg), [r["margin_H1"] for r in nondeg], -1, perm),
    }
    W = sum(r["K_kept"] for r in results)
    summary = {
        "status": "robustness check, not confirmatory",
        "prespecification_sha256": sha(FROZEN),
        "addendum_a_sha256": sha(ADDENDUM),
        "protocol": {"repeats": v2.REPEATS, "folds": v2.FOLDS, "seed": v2.SEED, "permutations": PERMS},
        "tests_rho_p_one_sided": tests, "n_nondegenerate": len(nondeg),
        "counts": {
            "datasets": len(results),
            "condition_over_all_attributes": sum(r["slack_all"] > 0 for r in results),
            "certified_prefix_deeper_than_one": sum(r["kmax"] >= 2 for r in results),
            "attributes_kept": W,
            "attributes_outweighing_prior": sum(r["Z_beats_prior"] for r in results),
            "spine_cv_at_least_full": [r["code"] for r in results if r["cv_gap_full_minus_spine"] <= 0],
            "spine_cv_within_1.5_of_full": [r["code"] for r in results
                                            if 0 < r["cv_gap_full_minus_spine"] <= 1.5],
        },
    }
    with open(os.path.join(HERE, "robustness_woike_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
