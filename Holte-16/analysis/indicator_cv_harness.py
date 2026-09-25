"""Indicator + cross-validation harness for the Holte-16 datasets (v2).

Extends depth_one_harness.py (v1, left untouched so the 2026-09-17 numbers stay
reproducible) with what the 2026-09-18 call asked for:

  A. The two-level indicator. Depth-one agreement A with full Bayes decomposes
     exactly as  A = (1 - c) + c * w  where, per object,
       conflict  = the verdict of (prior + all remaining cues) contradicts the
                   top cue;                                 c = conflict rate
       win       = the top cue still carries the full-Bayes verdict under
                   conflict;                                w = win rate
     Theorem 1(a) is the worst-case guarantee w = 1 on every conceivable
     profile. w is a graded decisiveness. (The 2026-09-18 run showed agreement
     comes mostly from low c, not high w.) The same decomposition is computed
     for the certified spine against the cues it never sees (ck, wk): the
     general form used in the paper's Section 2.
  B. Counts for the abstract's "X of Y datasets" and "Z of W attributes",
     under each candidate reading, so the phrasing can be chosen from numbers.
  C. Cross-validated accuracy: repeated stratified 10-fold. Everything that is
     learned (median cuts, value-to-side assignment, weights, cue order, kmax,
     the spine) is refit inside each training fold. Task definition (majority
     vs rest) and attribute type (numeric or not) are fixed on the full data.
     A categorical value unseen in training falls on cue side 0.
  D. One-vs-rest pass on the four multiclass datasets (in sample).

fit() + apply on the full data must reproduce v1's results.csv exactly; the
script asserts this before doing anything else.

Stdlib only.  Run:  python analysis/indicator_cv_harness.py  (from DATA_SETS/Holte-16/)
"""

import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict

from depth_one_harness import (CODES, HERE, MISSING, greedy_spine, is_numeric,
                               load, median, spearman, spine_classify)

REPEATS, FOLDS, SEED = 10, 10, 20260918


def prepare(code):
    """Column-wise data; numeric columns parsed once (None = missing)."""
    header, X, cls = load(code)
    cols = []
    for j in range(len(header)):
        col = [row[j] for row in X]
        if is_numeric(col):
            cols.append(("num", [None if v == MISSING else float(v) for v in col]))
        else:
            cols.append(("cat", col))
    return header, cols, cls


def pseudo_value(kind, v, med):
    if kind == "cat":
        return v
    return MISSING if v is None else ("hi" if v > med else "lo")


def fit(cols, y, idx):
    """Learn cues, weights and order on the rows in idx (v1 protocol)."""
    n = len(idx)
    n1 = sum(y[r] for r in idx)
    n0 = n - n1
    base = n1 / n
    kept = []
    for j, (kind, col) in enumerate(cols):
        med = None
        if kind == "num":
            present = [col[r] for r in idx if col[r] is not None]
            if not present:
                continue
            med = median(present)
        by_val = defaultdict(lambda: [0, 0])
        for r in idx:
            t = by_val[pseudo_value(kind, col[r], med)]
            t[0] += 1
            t[1] += y[r]
        if len(by_val) < 2:
            continue
        side1 = {v: (c1 / c > base) for v, (c, c1) in by_val.items()}
        if len(set(side1.values())) < 2:
            continue
        c11 = sum(c1 for v, (c, c1) in by_val.items() if side1[v])
        c01 = sum(c - c1 for v, (c, c1) in by_val.items() if side1[v])
        p = (c11 + 1) / (n1 + 2)
        q = (c01 + 1) / (n0 + 2)
        lp, lm = math.log(p / q), math.log((1 - p) / (1 - q))
        if not (lp > 1e-12 and lm < -1e-12):
            continue
        kept.append((min(lp, -lm), lp, lm, j, med, side1))
    kept.sort(key=lambda t: -t[0])
    llo = [t[0] for t in kept]
    lps = [t[1] for t in kept]
    lms = [t[2] for t in kept]
    lhi = [max(lp, -lm) for lp, lm in zip(lps, lms)]
    K = len(kept)
    kmax = 1 if K else 0
    for k in range(2, K + 1):
        if all(llo[i] > sum(lhi[i + 1:k]) for i in range(k - 1)):
            kmax = k
        else:
            break
    return {"l0": math.log(n1 / n0), "kept": kept, "llo": llo, "lps": lps,
            "lms": lms, "lhi": lhi, "K": K, "kmax": kmax,
            "spine": greedy_spine(math.log(n1 / n0), lps[:kmax], lms[:kmax]) if K else None}


def cue_row(model, cols, r):
    out = []
    for (_, _, _, j, med, side1) in model["kept"]:
        kind, col = cols[j]
        out.append(1 if side1.get(pseudo_value(kind, col[r], med), False) else 0)
    return out


def verdicts(model, x):
    """(depth-one, certified spine, full Bayes, rest-verdict, unseen sum) for one
    cue row; unseen sum = evidence of the cues beyond the certified prefix."""
    if not model["K"]:
        maj = 1 if model["l0"] > 0 else 0
        return maj, maj, maj, maj, 0.0
    l0, lps, lms = model["l0"], model["lps"], model["lms"]
    rest = l0 + sum(lps[i] if x[i] else lms[i] for i in range(1, model["K"]))
    full = rest + (lps[0] if x[0] else lms[0])
    unseen = sum(lps[i] if x[i] else lms[i] for i in range(model["kmax"], model["K"]))
    return (x[0], spine_classify(model["spine"], x[:model["kmax"]]),
            1 if full > 0 else 0, 1 if rest > 0 else 0, unseen)


def in_sample(cols, y):
    n = len(y)
    m = fit(cols, y, range(n))
    K, l0, llo, lhi = m["K"], m["l0"], m["llo"], m["lhi"]
    k_d1 = 1 if abs(l0) < llo[0] else 0
    for k in range(2, K + 1):
        if abs(l0) < llo[0] - sum(lhi[1:k]):
            k_d1 = k
        else:
            break
    a1 = ak = conflict = win = conflict_k = win_k = acc1 = acck = accf = 0
    spine_out = set()
    for r in range(n):
        d1, sp, full, rest, unseen = verdicts(m, cue_row(m, cols, r))
        a1 += d1 == full
        ak += sp == full
        acc1 += d1 == y[r]
        acck += sp == y[r]
        accf += full == y[r]
        spine_out.add(sp)
        if rest != d1:
            conflict += 1
            win += d1 == full
        # general form used in the paper: the unseen cues contradict the certified tree
        if (unseen > 0 and sp == 0) or (unseen < 0 and sp == 1):
            conflict_k += 1
            win_k += sp == full
    assert a1 == (n - conflict) + win, "decomposition identity violated"
    assert ak == (n - conflict_k) + win_k, "spine decomposition identity violated"
    return m, {
        "K_kept": K, "lambda0": round(l0, 4), "kmax": m["kmax"], "k_d1": k_d1,
        "slack_all": round(llo[0] - sum(lhi[1:]) - abs(l0), 3),
        "A1_agree_depth1": round(100 * a1 / n, 1),
        "Ak_agree_spine": round(100 * ak / n, 1),
        "c_conflict": round(100 * conflict / n, 1),
        "w_win_under_conflict": round(100 * win / conflict, 1) if conflict else "",
        "ck_conflict_spine": round(100 * conflict_k / n, 1),
        "wk_win_spine": round(100 * win_k / conflict_k, 1) if conflict_k else "",
        "spine_nondegenerate": len(spine_out) > 1,
        "Z_beats_prior": sum(1 for v in llo if v > abs(l0)),
        "Z_dominates_successors": sum(
            1 for i in range(K - 1) if llo[i] > sum(lhi[i + 1:])),
        "acc_depth1": round(100 * acc1 / n, 1),
        "acc_spine": round(100 * acck / n, 1),
        "acc_full": round(100 * accf / n, 1),
    }


def stratified_folds(y, k, rng):
    folds = [[] for _ in range(k)]
    for label in (0, 1):
        idx = [i for i, v in enumerate(y) if v == label]
        rng.shuffle(idx)
        for pos, i in enumerate(idx):
            folds[pos % k].append(i)
    return folds


def cross_validate(cols, y, rng):
    n = len(y)
    tot = Counter()
    for _ in range(REPEATS):
        for test in stratified_folds(y, FOLDS, rng):
            held = set(test)
            m = fit(cols, y, [i for i in range(n) if i not in held])
            for r in test:
                d1, sp, full, _, _ = verdicts(m, cue_row(m, cols, r))
                tot["d1"] += d1 == y[r]
                tot["sp"] += sp == y[r]
                tot["full"] += full == y[r]
                tot["agree"] += d1 == full
                tot["n"] += 1
    return {"cv_acc_depth1": round(100 * tot["d1"] / tot["n"], 1),
            "cv_acc_spine": round(100 * tot["sp"] / tot["n"], 1),
            "cv_acc_full": round(100 * tot["full"] / tot["n"], 1),
            "cv_agree_depth1": round(100 * tot["agree"] / tot["n"], 1)}


def main():
    v1 = {}
    with open(os.path.join(HERE, "results.csv"), newline="") as f:
        for row in csv.DictReader(f):
            v1[row["code"]] = row

    rng = random.Random(SEED)
    results, multiclass = [], []
    for code in CODES:
        t0 = time.time()
        header, cols, cls = prepare(code)
        counts = Counter(cls)
        maj = counts.most_common(1)[0][0]
        y = [1 if c == maj else 0 for c in cls]
        _, r = in_sample(cols, y)
        old = v1[code]
        for new_key, old_key in (("K_kept", "K_kept"), ("kmax", "kmax_DDpm"),
                                 ("k_d1", "k_depth1"),
                                 ("A1_agree_depth1", "agree_depth1_vs_fullBayes"),
                                 ("Ak_agree_spine", "agree_truncK_vs_fullBayes"),
                                 ("acc_depth1", "acc_depth1"),
                                 ("acc_full", "acc_full_bayes")):
            assert float(r[new_key]) == float(old[old_key]), (code, new_key)
        r.update(cross_validate(cols, y, rng))
        r = {"code": code, "n": len(y), "classes": len(counts),
             "base_rate": round(100 * sum(y) / len(y), 1), **r,
             "holte_1r": float(old["holte_1r"]), "holte_c4": float(old["holte_c4"]),
             "holte_margin": float(old["holte_margin"])}
        results.append(r)
        print(f"{code}: A1={r['A1_agree_depth1']} c={r['c_conflict']} "
              f"w={r['w_win_under_conflict']} Ak={r['Ak_agree_spine']} | "
              f"CV d1={r['cv_acc_depth1']} spine={r['cv_acc_spine']} "
              f"full={r['cv_acc_full']} base={r['base_rate']} "
              f"({time.time() - t0:.0f}s)")
        if len(counts) > 2:
            for label, cnt in sorted(counts.items(), key=lambda t: -t[1]):
                yy = [1 if c == label else 0 for c in cls]
                _, o = in_sample(cols, yy)
                multiclass.append({"code": code, "positive_class": label,
                                   "n_pos": cnt, "n": len(cls), **o})

    with open(os.path.join(HERE, "indicator_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    with open(os.path.join(HERE, "multiclass_one_vs_rest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(multiclass[0].keys()))
        w.writeheader()
        w.writerows(multiclass)

    for r in results:
        # constant-classifier accuracy; on GL, IR, SO the largest class is < 50%
        const = max(r["base_rate"], 100 - r["base_rate"])
        r["cv_gap_full_minus_d1"] = round(r["cv_acc_full"] - r["cv_acc_depth1"], 1)
        r["cv_gap_full_minus_spine"] = round(r["cv_acc_full"] - r["cv_acc_spine"], 1)
        r["cv_gain_spine_over_const"] = round(r["cv_acc_spine"] - const, 1)
    indicators = ["A1_agree_depth1", "Ak_agree_spine", "w_win_under_conflict",
                  "c_conflict", "slack_all"]
    targets = ["holte_margin", "cv_gap_full_minus_d1", "cv_gap_full_minus_spine",
               "cv_acc_depth1", "cv_acc_spine", "cv_gain_spine_over_const"]
    bin12 = [r for r in results if r["classes"] == 2]
    perm_rng = random.Random(SEED)

    def rho_p(xs, ys, perms=20000):
        obs = spearman(xs, ys)
        ys, hits = list(ys), 0
        for _ in range(perms):
            perm_rng.shuffle(ys)
            hits += abs(spearman(xs, ys)) >= abs(obs) - 1e-12
        return round(obs, 3), round((hits + 1) / (perms + 1), 3)

    corr = {}
    for ind in indicators:
        for tgt in targets:
            for tag, rows in (("all16", results), ("binary12", bin12)):
                rows = [r for r in rows if r[ind] != ""]
                rho, p = rho_p([r[ind] for r in rows], [r[tgt] for r in rows])
                corr[f"{ind}|{tgt}|{tag}"] = {"rho": rho, "perm_p_two_sided": p,
                                              "n": len(rows)}

    W = sum(r["K_kept"] for r in results)
    summary = {
        "protocol": {"repeats": REPEATS, "folds": FOLDS, "seed": SEED},
        "datasets_Y": len(results),
        "X_top_cue_beats_prior(k_d1>=1)": sum(r["k_d1"] >= 1 for r in results),
        "X_top_cue_beats_prior_plus_next(k_d1>=2)": sum(r["k_d1"] >= 2 for r in results),
        "X_condition_over_all_cues(slack_all>0)": sum(r["slack_all"] > 0 for r in results),
        "X_certified_prefix_deeper_than_one(kmax>=2)": sum(r["kmax"] >= 2 for r in results),
        "X_nondegenerate_certified_spine": sum(r["spine_nondegenerate"] for r in results),
        "attributes_W": W,
        "Z_beats_prior": sum(r["Z_beats_prior"] for r in results),
        "Z_in_certified_prefix(sum kmax)": sum(r["kmax"] for r in results),
        "Z_dominates_successors": sum(r["Z_dominates_successors"] for r in results),
        "W_nonlast_positions": W - len(results),
        "spine_cv_at_least_full": [r["code"] for r in results
                                   if r["cv_gap_full_minus_spine"] <= 0],
        "spine_cv_within_1.5_of_full": [r["code"] for r in results
                                        if 0 < r["cv_gap_full_minus_spine"] <= 1.5],
        "spearman": corr,
    }
    with open(os.path.join(HERE, "indicator_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    for key, v in corr.items():
        if v["perm_p_two_sided"] <= 0.10:
            print(f"  {key}: rho={v['rho']:+.3f} p={v['perm_p_two_sided']} n={v['n']}")
    print(json.dumps({k: v for k, v in summary.items() if k != "spearman"}, indent=2))


if __name__ == "__main__":
    main()
