"""Depth-one condition harness for the Holte-16 datasets.

Tests, on each of Holte's 16 datasets, the conditions of the identity theorem
(FFT_Classification_Paper_v0.1.md, Theorem 1 / Definition 1 DD+-) and measures
how closely the depth-one fast-and-frugal tree tracks the full additive-Bayes
classifier. Joins the results against Holte's own Table 3 accuracies
(analysis/holte_table3.csv, transcribed from references/holte-1993.pdf p. 4).

Protocol (v1, every choice deliberate and listed):
  1. Category. C1 = the majority class, C0 = all other classes pooled.
     Prior log-odds Lambda_0 = log(n1/n0) >= 0.
  2. Cues. One binary cue per attribute.
     - An attribute is numeric if every non-missing value parses as float and
       it has >= 3 distinct values; numeric attributes are cut at the median
       of non-missing values into pseudo-values 'lo' (<= median) / 'hi'.
       The missing token '?' is kept as its own pseudo-value.
     - Every (pseudo-)value v then joins cue side 1 iff P(C1|v) > P(C1),
       the base rate. This is 1R's own treatment of categorical values
       (class-optimal assignment per value) and guarantees C1-coding
       (p_i > q_i) in sample. Constant attributes are dropped.
  3. Weights. Laplace(+1)-smoothed p_i = P(x_i=1|C1), q_i = P(x_i=1|C0);
     l_plus = log(p/q), l_minus = log((1-p)/(1-q)). Cues whose smoothed
     weights fail l_plus > 0 > l_minus (uninformative after smoothing)
     are dropped and counted.
  4. Order. Cues sorted by descending l_lo = min(l_plus, -l_minus).
  5. Conditions measured (all downward-closed in k, so scanned upward):
     - kmax    = largest k such that the top-k prefix satisfies DD+- internally
                 (for all i<k: l_lo_i > sum_{j=i+1..k} l_hi_j).
     - k_d1    = largest k such that |Lambda_0| < l_lo_(1) - sum_{j=2..k} l_hi_(j)
                 (Theorem 1(a): the best cue alone IS Bayes over the top-k cues).
     - slack_all = l_lo_(1) - sum_{j>=2} l_hi_j - |Lambda_0| over ALL kept cues.
  6. Classifiers compared sample-wise on all n objects (in sample; the
     theorem is a population identity, not a generalization claim):
     - full Bayes:  sign(Lambda_0 + sum over all kept cues)
     - depth-one:   C1 iff top cue = 1
     - truncated Bayes at k = kmax (top kmax cues)
     - greedy spine FFT at k = kmax (Theorem 1(b) construction) --
       agreement with truncated Bayes must be 100% wherever DD+- holds:
       a live verification of the theorem on real data.

Stdlib only except the optional matplotlib figure.
Run:  python analysis/depth_one_harness.py   (from DATA_SETS/Holte-16/)
"""

import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DATA = os.path.join(PKG, "data")
CODES = ["BC", "CH", "GL", "G2", "HD", "HE", "HO", "HY",
         "IR", "LA", "LY", "MU", "SE", "SO", "VO", "V1"]
MISSING = "?"


def load(code):
    with open(os.path.join(DATA, code + ".csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    assert header[-1] == "class"
    return header[:-1], [r[:-1] for r in body], [r[-1] for r in body]


def is_numeric(values):
    seen = set()
    for v in values:
        if v == MISSING:
            continue
        try:
            float(v)
        except ValueError:
            return False
        seen.add(v)
    return len(seen) >= 3


def median(xs):
    s = sorted(xs)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2.0


def binarize(colvals, y):
    """Return list of 0/1 (cue side per object) or None if constant."""
    if is_numeric(colvals):
        med = median([float(v) for v in colvals if v != MISSING])
        pseudo = [MISSING if v == MISSING else ("hi" if float(v) > med else "lo")
                  for v in colvals]
    else:
        pseudo = colvals
    if len(set(pseudo)) < 2:
        return None
    n1 = sum(y)
    base = n1 / len(y)
    by_val = defaultdict(lambda: [0, 0])  # value -> [count, count_C1]
    for v, yy in zip(pseudo, y):
        by_val[v][0] += 1
        by_val[v][1] += yy
    side1 = {v: (c1 / c > base) for v, (c, c1) in by_val.items()}
    cue = [1 if side1[v] else 0 for v in pseudo]
    if len(set(cue)) < 2:
        return None
    return cue


def weights(cue, y):
    n1 = sum(y)
    n0 = len(y) - n1
    c11 = sum(1 for c, yy in zip(cue, y) if c == 1 and yy == 1)
    c01 = sum(1 for c, yy in zip(cue, y) if c == 1 and yy == 0)
    p = (c11 + 1) / (n1 + 2)
    q = (c01 + 1) / (n0 + 2)
    return math.log(p / q), math.log((1 - p) / (1 - q))


def greedy_spine(l0, cues_lp, cues_lm):
    """Theorem 1(b) construction. Returns list of levels:
    ('exit1'|'exit0', level) spine steps, then ('term', cat1, cat0)."""
    k = len(cues_lp)
    tree = []
    lam = l0
    for i in range(k):
        Mp = sum(cues_lp[i + 1:])
        Mm = sum(cues_lm[i + 1:])
        dec1 = lam + cues_lp[i] + Mm > 0
        dec0 = lam + cues_lm[i] + Mp < 0
        if i == k - 1:
            tree.append(("term",
                         1 if lam + cues_lp[i] > 0 else 0,
                         1 if lam + cues_lm[i] > 0 else 0))
            return tree
        if dec1 and dec0:
            tree.append(("term", 1, 0))
            return tree
        if dec1:
            tree.append(("exit1",))
            lam += cues_lm[i]
        elif dec0:
            tree.append(("exit0",))
            lam += cues_lp[i]
        else:
            tree.append(("stuck",))  # only reachable if DD+- fails
            lam += cues_lp[i]  # arbitrary; flagged upstream
    return tree


def spine_classify(tree, xrow):
    for i, level in enumerate(tree):
        if level[0] == "term":
            return level[1] if xrow[i] == 1 else level[2]
        if level[0] == "exit1" and xrow[i] == 1:
            return 1
        if level[0] == "exit0" and xrow[i] == 0:
            return 0
        # 'stuck' or continue branch: fall through
    return 0


def analyze(code):
    header, X, cls = load(code)
    counts = Counter(cls)
    maj, majn = counts.most_common(1)[0]
    y = [1 if c == maj else 0 for c in cls]
    n = len(y)
    n1 = sum(y)
    n0 = n - n1
    l0 = math.log(n1 / n0)

    kept = []
    dropped_const = dropped_uninf = 0
    for j, name in enumerate(header):
        col = [row[j] for row in X]
        cue = binarize(col, y)
        if cue is None:
            dropped_const += 1
            continue
        lp, lm = weights(cue, y)
        if not (lp > 1e-12 and lm < -1e-12):
            dropped_uninf += 1
            continue
        kept.append((min(lp, -lm), lp, lm, name, cue))
    kept.sort(key=lambda t: -t[0])
    K = len(kept)
    llo = [t[0] for t in kept]
    lps = [t[1] for t in kept]
    lms = [t[2] for t in kept]
    lhi = [max(lp, -lm) for lp, lm in zip(lps, lms)]
    cues = [t[4] for t in kept]

    # kmax: largest prefix internally satisfying DD+-
    kmax = 1
    for k in range(2, K + 1):
        ok = all(llo[i] > sum(lhi[i + 1:k]) for i in range(k - 1))
        if ok:
            kmax = k
        else:
            break

    # k_d1: largest k with |L0| < llo[0] - sum_{j=2..k} lhi
    k_d1 = 1 if abs(l0) < llo[0] else 0
    for k in range(2, K + 1):
        if abs(l0) < llo[0] - sum(lhi[1:k]):
            k_d1 = k
        else:
            break
    slack_all = llo[0] - sum(lhi[1:]) - abs(l0)

    # sample-wise classifiers
    def lam_at(row_idx, upto):
        s = l0
        for i in range(upto):
            s += lps[i] if cues[i][row_idx] else lms[i]
        return s

    spine = greedy_spine(l0, lps[:kmax], lms[:kmax])
    agree_1_full = agree_k_full = agree_spine_trunc = 0
    acc1 = accK = accFull = 0
    for r in range(n):
        full = 1 if lam_at(r, K) > 0 else 0
        trunc = 1 if lam_at(r, kmax) > 0 else 0
        d1 = 1 if cues[0][r] == 1 else 0
        sp = spine_classify(spine, [cues[i][r] for i in range(kmax)])
        agree_1_full += d1 == full
        agree_k_full += trunc == full
        agree_spine_trunc += sp == trunc
        acc1 += d1 == y[r]
        accK += trunc == y[r]
        accFull += full == y[r]

    return {
        "code": code, "n": n, "classes": len(counts), "majority": maj,
        "base_rate": round(100 * n1 / n, 1), "lambda0": round(l0, 4),
        "K_attrs": len(header), "K_kept": K,
        "dropped_constant": dropped_const, "dropped_uninformative": dropped_uninf,
        "top_cue": kept[0][3], "l_lo_1": round(llo[0], 3),
        "kmax_DDpm": kmax, "k_depth1": k_d1,
        "slack_all_cues": round(slack_all, 3),
        "agree_depth1_vs_fullBayes": round(100 * agree_1_full / n, 1),
        "agree_truncK_vs_fullBayes": round(100 * agree_k_full / n, 1),
        "agree_spine_vs_truncBayes": round(100 * agree_spine_trunc / n, 1),
        "acc_depth1": round(100 * acc1 / n, 1),
        "acc_trunc_kmax": round(100 * accK / n, 1),
        "acc_full_bayes": round(100 * accFull / n, 1),
    }


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def main():
    holte = {}
    with open(os.path.join(HERE, "holte_table3.csv"), newline="") as f:
        for row in csv.DictReader(f):
            holte[row["code"]] = (float(row["holte_1r"]), float(row["holte_c4"]))

    results = []
    for code in CODES:
        r = analyze(code)
        r1, c4 = holte[code]
        r["holte_1r"] = r1
        r["holte_c4"] = c4
        r["holte_margin"] = round(c4 - r1, 1)
        results.append(r)
        print(f"{code}: n={r['n']} K={r['K_kept']}/{r['K_attrs']} "
              f"kmax={r['kmax_DDpm']} k_d1={r['k_depth1']} "
              f"agree1={r['agree_depth1_vs_fullBayes']}% "
              f"spine=trunc {r['agree_spine_vs_truncBayes']}% "
              f"margin={r['holte_margin']}")

    fields = list(results[0].keys())
    with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)

    ag = [r["agree_depth1_vs_fullBayes"] for r in results]
    mg = [r["holte_margin"] for r in results]
    rho = spearman(ag, mg)
    gap = [r["acc_full_bayes"] - r["acc_depth1"] for r in results]
    rho_gap = spearman(gap, mg)
    # Clean comparison: only the 12 originally 2-class datasets, where
    # Holte's margin and our binarized task measure the same problem.
    bin2 = [r for r in results if r["classes"] == 2]
    rho_bin = spearman([r["agree_depth1_vs_fullBayes"] for r in bin2],
                       [r["holte_margin"] for r in bin2])
    summary = {
        "spearman_agree1_vs_margin": round(rho, 3),
        "spearman_agree1_vs_margin_binary12": round(rho_bin, 3),
        "binary12_codes": [r["code"] for r in bin2],
        "spearman_accgap_vs_margin": round(rho_gap, 3),
        "total_objects": sum(r["n"] for r in results),
        "spine_identity_holds_everywhere": all(
            r["agree_spine_vs_truncBayes"] == 100.0 for r in results),
    }
    with open(os.path.join(HERE, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSpearman(agree_depth1_vs_fullBayes, Holte C4-1R margin) =", round(rho, 3))
    print("  same, 12 originally-binary datasets only              =", round(rho_bin, 3))
    print("Spearman(fullBayes-depth1 accuracy gap, margin)         =", round(rho_gap, 3))
    print("Total objects checked:", summary["total_objects"])
    print("Spine == truncated Bayes on every object of every dataset:",
          summary["spine_identity_holds_everywhere"])

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(ag, mg, s=40, color="#2b6cb0", zorder=3)
        for r in results:
            ax.annotate(r["code"],
                        (r["agree_depth1_vs_fullBayes"], r["holte_margin"]),
                        textcoords="offset points", xytext=(5, 4), fontsize=8)
        ax.set_xlabel("Agreement of depth-one tree with full Bayes verdicts (%)")
        ax.set_ylabel("Holte's Table 3 margin: C4 minus 1R (points)")
        ax.set_title("Depth-one Bayes identity vs. Holte's one-rule margin "
                     f"(Spearman rho = {rho:.2f})")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        for ext in ("png", "svg"):
            fig.savefig(os.path.join(HERE, f"fig_condition_vs_margin.{ext}"),
                        dpi=200)
        print("Figure written.")
    except ImportError:
        print("matplotlib not available; figure skipped.")


if __name__ == "__main__":
    main()
