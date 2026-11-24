"""POST HOC, DESCRIPTIVE, on spent data only. Written 2026-11-06 for item 3 of Konstantinos's questions (version B,
Alex's choice): count the conflict rate c and the share s of Result 2 on the TEST FOLDS, the same cases on which
the disagreement 1 - A and the share q are counted, so that within every dataset

    price = acc(B) - acc(T) = (1 - A)(2q - 1) = c (1 - s)(2q - 1)      exactly, in whole cases.

Definitions (as in indicator_cv_harness.in_sample, now applied to held-out cases):
    conflict  the evidence of the attributes the certified tree T does not use, taken alone (without the prior),
              opposes T's verdict;                                   c = conflicts / cases
    win       under a conflict, the full additive classifier B still returns T's verdict;   s = wins / conflicts
T and B can disagree only under a conflict (T is the Bayesian classifier on its own attributes), so
1 - A = c (1 - s). The script asserts this case by case.

Collections, each with the protocol, seed, order and random stream of its saved run:
    Holte-16 and MKW08-30 (our reconstruction)   as in price_identity.py
    MKW08-30, Woike's files                      as in price_identity_woike.py (Addendum A)
    TabArena-29                                  as in tabarena_confirmatory.py (Addendum B); only the folds are
                                                 drawn from the shared stream there, so the tree side is reproduced
                                                 without refitting logistic regression or CART.
Checks: saved cross-validated accuracies of T and B, saved out-of-sample A and q, and saved in-sample c and s are
all reproduced before anything is written.

    python heldout_conflict_share.py   ->  heldout_conflict_share_results.csv  (+ console log)

Repository copy: the analysis files are read from the data/ folders of the repository (built by fetch_data.py), or
from another folder with the same layout named by the environment variable BFFT_DATA_ROOT. Woike's files
(MKW08-30/data-woike/) are not redistributed; without them, the rows of MKW08-30-Woike are skipped and the other 75
are computed as before.
"""
import csv
import json
import os
import random
import statistics as st
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

DATA_ROOT = os.environ.get("BFFT_DATA_ROOT", DS)  # where the data/ folders are; the repository root by default

def conflict(sp, unseen):
    return (unseen > 0 and sp == 0) or (unseen < 0 and sp == 1)


def count(cols, y, rng, repeats):
    n = len(y)
    t = Counter()
    m = v2.fit(cols, y, range(n))
    outs = set()
    for r in range(n):
        _, sp, full, _, unseen = v2.verdicts(m, v2.cue_row(m, cols, r))
        outs.add(sp)
        t["in_n"] += 1
        if conflict(sp, unseen):
            t["in_conf"] += 1
            t["in_win"] += sp == full
        elif sp != full:
            t["violations"] += 1
        t["in_dis"] += sp != full
    for _ in range(repeats):
        for test in v2.stratified_folds(y, v2.FOLDS, rng):
            held = set(test)
            m = v2.fit(cols, y, [i for i in range(n) if i not in held])
            for r in test:
                _, sp, full, _, unseen = v2.verdicts(m, v2.cue_row(m, cols, r))
                t["cv_n"] += 1
                t["cv_sp"] += sp == y[r]
                t["cv_full"] += full == y[r]
                if conflict(sp, unseen):
                    t["cv_conf"] += 1
                    t["cv_win"] += sp == full
                elif sp != full:
                    t["violations"] += 1
                if sp != full:
                    t["cv_dis"] += 1
                    t["cv_dis_full_right"] += full == y[r]
    assert t["violations"] == 0, "a disagreement without a conflict"
    for k in ("in", "cv"):
        assert t[k + "_dis"] == t[k + "_conf"] - t[k + "_win"], k   # 1 - A = c (1 - s), in whole cases
    assert t["cv_full"] - t["cv_sp"] == 2 * t["cv_dis_full_right"] - t["cv_dis"]   # price identity
    return t, len(outs) > 1


def pct(a, b):
    return 100 * a / b if b else None


def row(collection, code, t, both):
    N = t["cv_n"]
    c, s = pct(t["cv_conf"], N), pct(t["cv_win"], t["cv_conf"])
    A, q = 100 - pct(t["cv_dis"], N), pct(t["cv_dis_full_right"], t["cv_dis"])
    price = pct(t["cv_full"] - t["cv_sp"], N)
    if t["cv_dis"]:   # Result 2, in floating point, as a final check on the counts
        assert abs(price - c / 100 * (1 - s / 100) * (2 * q / 100 - 1) * 100) < 1e-9
    return {"collection": collection, "code": code, "n": t["in_n"], "both_verdicts": both,
            "in_c": pct(t["in_conf"], t["in_n"]), "in_s": pct(t["in_win"], t["in_conf"]),
            "in_A": 100 - pct(t["in_dis"], t["in_n"]),
            "cv_cases": N, "cv_c": c, "cv_s": s, "cv_A": A, "cv_q": q, "cv_price": price,
            "cv_acc_tree": pct(t["cv_sp"], N), "cv_acc_full": pct(t["cv_full"], N)}


def same(a, b, nd, what):
    assert round(a, nd) == round(float(b), nd), what


def close4(a, b, what):
    """TabArena values were saved rounded to four decimals; compare within that rounding."""
    assert abs(a - float(b)) <= 0.5e-4 + 1e-9, (what, a, b)


def check_saved_1dp(r, saved, ident):
    """Holte and the thirty: saved values carry one decimal."""
    same(r["cv_acc_tree"], saved["cv_acc_spine"], 1, (ident, "cv tree accuracy"))
    same(r["cv_acc_full"], saved["cv_acc_full"], 1, (ident, "cv full accuracy"))
    same(r["in_c"], saved["ck_conflict_spine"], 1, (ident, "in-sample c"))
    if saved["wk_win_spine"] != "":
        same(r["in_s"], saved["wk_win_spine"], 1, (ident, "in-sample s"))
    same(r["in_A"], saved["Ak_agree_spine"], 1, (ident, "in-sample A"))


def check_price_identity_csv(r, saved, ident):
    same(r["cv_A"], saved["cv_agreement"], 1, (ident, "cv A"))
    if saved["cv_q_full_right_when_disagree"] != "":
        same(r["cv_q"], saved["cv_q_full_right_when_disagree"], 1, (ident, "cv q"))
    same(r["cv_price"], saved["cv_price_points"], 1, (ident, "cv price"))


def main():
    out = []
    pi = {(r["collection"], r["code"]): r for r in csv.DictReader(open(os.path.join(HERE, "price_identity_results.csv"), newline=""))}
    piw = {(r["collection"], r["code"]): r for r in csv.DictReader(open(os.path.join(HERE, "price_identity_woike_results.csv"), newline=""))}

    # Holte's sixteen
    v1.DATA = os.path.join(DATA_ROOT, "Holte-16", "data")
    holte_data = v1.DATA
    saved = {r["code"]: r for r in csv.DictReader(open(os.path.join(DS, "Holte-16", "analysis", "indicator_results.csv"), newline=""))}
    rng = random.Random(v2.SEED)
    for code in v2.CODES:
        _, cols, cls = v2.prepare(code)
        maj = Counter(cls).most_common(1)[0][0]
        y = [1 if c == maj else 0 for c in cls]
        t, both = count(cols, y, rng, v2.REPEATS)
        r = row("Holte-16", code, t, both)
        check_saved_1dp(r, saved[code], code)
        check_price_identity_csv(r, pi[("Holte-16", code)], code)
        out.append(r)
        print(code, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    assert v1.DATA == holte_data

    # the thirty: our reconstruction, then Woike's files
    pkg = os.path.join(DS, "MKW08-30")
    manifest = json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]
    for label, folder, res, pid in (("MKW08-30", "data", "confirmatory_results.csv", pi),
                                    ("MKW08-30-Woike", "data-woike", "robustness_woike_results.csv", piw)):
        saved = {r["code"]: r for r in csv.DictReader(open(os.path.join(pkg, "analysis", res), newline=""))}
        v1.DATA = os.path.join(DATA_ROOT, "MKW08-30", folder)
        if label == "MKW08-30-Woike" and not os.path.isdir(v1.DATA):
            print("Woike's files not found at", v1.DATA, "- the rows of MKW08-30-Woike are skipped", flush=True)
            continue
        rng = random.Random(v2.SEED)
        for ds in manifest:
            code = ds["code"]
            _, cols, cls = v2.prepare(code)
            counts = Counter(cls)
            c1 = "1" if counts["1"] >= counts["0"] else "0"
            y = [1 if c == c1 else 0 for c in cls]
            t, both = count(cols, y, rng, v2.REPEATS)
            r = row(label, code, t, both)
            check_saved_1dp(r, saved[code], (label, code))
            check_price_identity_csv(r, pid[("MKW08-30", code)], (label, code))
            out.append(r)
            print(label, code, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k.startswith(("cv_c", "cv_s", "cv_A", "cv_q", "cv_p", "in_"))}, flush=True)

    # TabArena-29
    tpkg = os.path.join(DS, "TabArena-Binary")
    v1.DATA = os.path.join(DATA_ROOT, "TabArena-Binary", "data")
    dtypes = json.load(open(os.path.join(v1.DATA, "declared_types.json"), encoding="utf-8"))
    counts_csv = {r["dataset"]: r for r in csv.DictReader(open(os.path.join(tpkg, "measured-counts.csv"), encoding="utf-8"))}
    saved = {r["dataset"]: r for r in csv.DictReader(open(os.path.join(tpkg, "analysis", "tabarena_results.csv"), encoding="utf-8"))}
    rng = random.Random(v2.SEED)
    for name in list(dtypes):
        _, cols, cls = v2.prepare(name)
        cnt = Counter(cls)
        (c1, n1), (c0, n0) = sorted(cnt.items(), key=lambda t: -t[1])
        if n1 == n0 and "1" in cnt:
            c1 = "1"
        y = [1 if c == c1 else 0 for c in cls]
        if v2.fit(cols, y, range(len(y)))["K"] == 0:
            print(name, "excluded (no kept attribute), as in the saved run", flush=True)
            continue
        repeats = 10 if int(counts_csv[name]["n_rows"]) <= 10000 else 1
        t, both = count(cols, y, rng, repeats)
        r = row("TabArena-29", name, t, both)
        s = saved[name]
        close4(r["cv_acc_tree"], s["cv_acc_tree"], (name, "cv tree accuracy"))
        close4(r["cv_acc_full"], s["cv_acc_full"], (name, "cv full accuracy"))
        close4(r["cv_A"], s["A"], (name, "cv A"))
        if s["q"] != "":
            close4(r["cv_q"], s["q"], (name, "cv q"))
        same(r["in_c"], s["c_conflict_spine"], 1, (name, "in-sample c"))
        if s["w_win_spine"] != "":
            same(r["in_s"], s["w_win_spine"], 1, (name, "in-sample s"))
        same(r["in_A"], s["Ak"], 1, (name, "in-sample A"))
        assert str(both) == s["both_verdicts"], (name, "both verdicts")
        out.append(r)
        print(name, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k.startswith(("cv_c", "cv_s", "cv_A", "cv_q", "cv_p", "in_"))}, flush=True)

    with open(os.path.join(HERE, "heldout_conflict_share_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        for r in out:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    # medians, over all datasets and over the trees that offer both verdicts
    med = lambda v: round(st.median(v), 1)
    print("\nMEDIANS (percent; price in points)")
    for coll in ("Holte-16", "MKW08-30", "MKW08-30-Woike", "TabArena-29"):
        R = [r for r in out if r["collection"] == coll]
        if not R:  # Woike's files absent
            continue
        B = [r for r in R if r["both_verdicts"]]
        for tag, S in (("all", R), ("both", B)):
            print(coll, tag, len(S),
                  "in_c", med([r["in_c"] for r in S]), "in_s", med([r["in_s"] for r in S if r["in_s"] is not None]),
                  "in_A", med([r["in_A"] for r in S]), "| cv_c", med([r["cv_c"] for r in S]),
                  "cv_s", med([r["cv_s"] for r in S if r["cv_s"] is not None]), "(n_s", sum(r["cv_s"] is not None for r in S), ")",
                  "cv_A", med([r["cv_A"] for r in S]), "cv_1-A", med([100 - r["cv_A"] for r in S]),
                  "cv_q", med([r["cv_q"] for r in S if r["cv_q"] is not None]), "cv_price", med([r["cv_price"] for r in S]))
    print("saved", len(out), "rows; every held-out disagreement was a conflict; 1-A = c(1-s) and the price identity held "
          "in whole cases; saved accuracies, A, q and in-sample c, s reproduced")


if __name__ == "__main__":
    main()
