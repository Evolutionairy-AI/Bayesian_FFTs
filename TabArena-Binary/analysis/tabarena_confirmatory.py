#!/usr/bin/env python3
"""Driver for Addendum B (DATA_SETS/MKW08-30/analysis/ADDENDUM_B_FROZEN.md): the screening rule on the TabArena
binary tasks. Refuses to start unless the addendum is frozen; records its SHA-256 and the pre-specification's.

    python analysis/tabarena_confirmatory.py --smoke     # pipeline check on SPENT data only (three of the thirty)
    python analysis/tabarena_confirmatory.py             # the run: self-test on the thirty, then the 29 tasks, once
    python analysis/tabarena_confirmatory.py --resume    # continue after an interruption (logged as a deviation)

Imports the protocol functions unchanged from DATA_SETS/Holte-16/analysis/. New here: the internal benchmarks
(section 4), the H4 statistics with Freedman-Lane permutation (section 3), H3 (section 5.1) and the descriptive
quantities (section 5). Before any TabArena file is read, the self-test must reproduce the development partial
correlations on the thirty (-0.78 and -0.34, section 6).
"""
import csv
import hashlib
import itertools
import json
import math
import os
import pickle
import random
import statistics
import sys
import time
import warnings
from collections import Counter

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DS = os.path.dirname(PKG)
MKW = os.path.join(DS, "MKW08-30")
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

FROZEN = os.path.join(MKW, "analysis", "ADDENDUM_B_FROZEN.md")
PRESPEC = os.path.join(MKW, "analysis", "PRESPECIFICATION_FROZEN.md")
DATA = os.path.join(PKG, "data")
CHECKPOINT = os.path.join(HERE, "tabarena_checkpoint.pkl")
SEED, PERMS, FOLDS = v2.SEED, 20000, v2.FOLDS
ALPHAS = [0.0, 0.0001, 0.0003, 0.001, 0.003, 0.01]
assert sklearn.__version__ == "1.7.2", sklearn.__version__


# ---- statistics ------------------------------------------------------------------------------
def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r, i = [0.0] * len(v), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for t in range(i, j + 1):
            r[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else float("nan")


def partial(x, y, z):
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    return (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def freedman_lane(S, G, Z, rng):
    """Partial Spearman of S and G given Z; one-sided (negative) Freedman-Lane permutation p on the ranks."""
    rS, rG, rZ = ranks(S), ranks(G), ranks(Z)
    obs = partial(rS, rG, rZ)
    mz, mg = sum(rZ) / len(rZ), sum(rG) / len(rG)
    slope = sum((z - mz) * (g - mg) for z, g in zip(rZ, rG)) / sum((z - mz) ** 2 for z in rZ)
    fitted = [mg + slope * (z - mz) for z in rZ]
    resid = [g - f for g, f in zip(rG, fitted)]
    hits = 0
    for _ in range(PERMS):
        rng.shuffle(resid)
        hits += partial(rS, [f + e for f, e in zip(fitted, resid)], rZ) <= obs + 1e-12
    return {"partial_rho": round(obs, 3), "p_one_sided": round((hits + 1) / (PERMS + 1), 5), "n": len(S)}


def one_sided(xs, ys, sign, rng):
    """As in the frozen H1 driver: Spearman rho and the permutation p for the pre-specified direction."""
    obs = v1.spearman(xs, ys)
    ys, hits = list(ys), 0
    for _ in range(PERMS):
        rng.shuffle(ys)
        hits += sign * v1.spearman(xs, ys) >= sign * obs - 1e-12
    return {"rho": round(obs, 3), "p_one_sided": round((hits + 1) / (PERMS + 1), 5), "n": len(xs)}


# ---- self-test on the thirty (spent data) ---------------------------------------------------------
def selftest():
    res = {r["code"]: r for r in csv.DictReader(open(os.path.join(MKW, "analysis", "confirmatory_results.csv"), newline=""))}
    saved = v1.DATA
    v1.DATA = os.path.join(MKW, "data")
    S, G, B, L = [], [], [], []
    for ds in json.load(open(os.path.join(MKW, "manifest.json"), encoding="utf-8"))["datasets"]:
        _, cols, cls = v2.prepare(ds["code"])
        cnt = Counter(cls)
        c1 = "1" if cnt["1"] >= cnt["0"] else "0"
        m = v2.fit(cols, [1 if c == c1 else 0 for c in cls], range(len(cls)))
        r = res[ds["code"]]
        base, best = float(r["base_rate"]), max(float(r["woike_LR"]), float(r["woike_CART"]))
        S.append(abs(m["l0"]) - m["llo"][0]); L.append(m["llo"][0]); B.append(base)
        G.append(100 * (best - base) / (100 - base))
    v1.DATA = saved
    a = freedman_lane(S, G, B, random.Random(SEED))
    b = freedman_lane(S, G, L, random.Random(SEED))
    assert round(a["partial_rho"], 2) == -0.78 and round(b["partial_rho"], 2) == -0.34, (a, b)
    print(f"selftest OK on the thirty: partial(S, G | base) = {a['partial_rho']} (Freedman-Lane p = {a['p_one_sided']}); "
          f"partial(S, G | strongest reading) = {b['partial_rho']} (p = {b['p_one_sided']})", flush=True)
    return {"H4a_on_thirty": a, "H4b_on_thirty": b}


# ---- one dataset ------------------------------------------------------------------------------
def benchmark_frame(header, X, dtypes):
    df = {}
    for j, (name, t) in enumerate(zip(header, dtypes)):
        col = [row[j] for row in X]
        if t == "numeric":
            df[name] = pd.to_numeric(pd.Series([np.nan if v == v1.MISSING else v for v in col]), errors="raise")
        else:
            df[name] = pd.Series(["__missing__" if v == v1.MISSING else v for v in col], dtype=object)
    frame = pd.DataFrame(df)
    num = [h for h, t in zip(header, dtypes) if t == "numeric"]
    cat = [h for h, t in zip(header, dtypes) if t != "numeric"]
    return frame, num, cat


def preprocessor(num, cat):
    parts = []
    if num:
        parts.append(("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)),
                                       ("sc", StandardScaler())]), num))
    if cat:
        parts.append(("cat", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=0.01), cat))
    return ColumnTransformer(parts)


def verdicts_c1(model, Xt):
    j = list(model.classes_).index(1)
    return (model.predict_proba(Xt)[:, j] > 0.5).astype(int)


def run_dataset(name, dtypes, rng, repeats):
    t0 = time.time()
    header, X, cls = v1.load(name)
    _, cols, _ = v2.prepare(name)
    cnt = Counter(cls)
    (c1, n1), (c0, n0) = sorted(cnt.items(), key=lambda t: -t[1])
    if n1 == n0 and "1" in cnt:
        c1 = "1"
    y = [1 if c == c1 else 0 for c in cls]
    n = len(y)
    base = 100 * sum(y) / n
    m = v2.fit(cols, y, range(n))
    row = {"dataset": name, "n": n, "attributes": len(header), "C1": c1, "base_rate": base, "K_kept": m["K"]}
    if m["K"] == 0:
        row["excluded"] = "no kept attribute"
        return row
    _, ins = v2.in_sample(cols, y)
    d, spine = m["kmax"], m["spine"]
    mism_cases = 0
    for r in range(n):
        x = v2.cue_row(m, cols, r)
        s = m["l0"] + sum(m["lps"][i] if x[i] else m["lms"][i] for i in range(d))
        mism_cases += v2.verdicts(m, x)[1] != (1 if s > 0 else 0)
    outs, mism_prof = set(), 0
    for p in itertools.product((0, 1), repeat=d):
        s = m["l0"] + sum(m["lps"][i] if p[i] else m["lms"][i] for i in range(d))
        v = v1.spine_classify(spine, list(p))
        outs.add(v)
        mism_prof += v != (1 if s > 0 else 0)
    row.update({"Ak": ins["Ak_agree_spine"], "certified_depth": d, "questions_asked": len(spine),
                "both_verdicts": len(outs) > 1, "identity_mismatch_cases": mism_cases,
                "identity_mismatch_profiles": mism_prof, "lambda0": m["l0"], "strongest_weaker_reading": m["llo"][0],
                "S": abs(m["l0"]) - m["llo"][0], "S2": abs(m["l0"]) - max(-v for v in m["lms"]),
                "Z_beats_prior": ins["Z_beats_prior"], "c_conflict_spine": ins["ck_conflict_spine"],
                "w_win_spine": ins["wk_win_spine"]})

    frame, num, cat = benchmark_frame(header, X, dtypes)
    yv = np.array(y)
    tot = Counter()
    by_class = Counter()
    nwarn = 0
    for _ in range(repeats):
        for test in v2.stratified_folds(y, FOLDS, rng):
            held = set(test)
            train = [i for i in range(n) if i not in held]
            mf = v2.fit(cols, y, train)
            pre = preprocessor(num, cat).fit(frame.iloc[train])
            Xtr, Xte = pre.transform(frame.iloc[train]), pre.transform(frame.iloc[test])
            with warnings.catch_warnings(record=True) as wlog:
                warnings.simplefilter("always")
                lr = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000).fit(Xtr, yv[train])
                cart = GridSearchCV(DecisionTreeClassifier(criterion="gini", min_samples_leaf=5, random_state=SEED),
                                    {"ccp_alpha": ALPHAS}, scoring="accuracy", n_jobs=-1,
                                    cv=StratifiedKFold(5, shuffle=True, random_state=SEED)).fit(Xtr, yv[train])
                nwarn += len(wlog)
            p_lr, p_cart = verdicts_c1(lr, Xte), verdicts_c1(cart.best_estimator_, Xte)
            for k, r in enumerate(test):
                _, sp, full, _, _ = v2.verdicts(mf, v2.cue_row(mf, cols, r))
                yy = y[r]
                tot["n"] += 1
                by_class[("n", yy)] += 1
                for key, v in (("tree", sp), ("full", full), ("lr", p_lr[k]), ("cart", p_cart[k])):
                    tot[key] += v == yy
                    by_class[(key, yy)] += v == yy
                if sp != full:
                    tot["dis"] += 1
                    tot["dis_full_right"] += full == yy
    N = tot["n"]
    assert tot["full"] - tot["tree"] == 2 * tot["dis_full_right"] - tot["dis"], (name, "price identity")
    acc = {k: 100 * tot[k] / N for k in ("tree", "full", "lr", "cart")}
    bal = {k: 50 * (by_class[(k, 0)] / by_class[("n", 0)] + by_class[(k, 1)] / by_class[("n", 1)])
           for k in ("tree", "full", "lr", "cart")}
    a = max(acc["lr"], acc["cart"])
    row.update({"cv_repeats": repeats, "cv_cases": N,
                **{f"cv_acc_{k}": v for k, v in acc.items()}, **{f"cv_bal_{k}": v for k, v in bal.items()},
                "benchmark_acc": a, "G": 100 * (a - base) / (100 - base),
                "A": 100 * (1 - tot["dis"] / N), "q": 100 * tot["dis_full_right"] / tot["dis"] if tot["dis"] else None,
                "price": acc["full"] - acc["tree"], "sklearn_warnings": nwarn, "seconds": round(time.time() - t0)})
    return row


# ---- the analyses of sections 3 and 5 ---------------------------------------------------------------
def analyses(rows, leak):
    units = [r for r in rows if "excluded" not in r]
    col = lambda rs, k: [r[k] for r in rs]  # noqa: E731
    S, G, B, L = col(units, "S"), col(units, "G"), col(units, "base_rate"), col(units, "strongest_weaker_reading")
    out = {"H4a_S_G_given_base_rate": freedman_lane(S, G, B, random.Random(SEED)),
           "H4b_S_G_given_strongest_reading": freedman_lane(S, G, L, random.Random(SEED))}
    out["H4_supported_against_both_rivals"] = all(out[k]["p_one_sided"] < 0.05 for k in
                                                   ("H4a_S_G_given_base_rate", "H4b_S_G_given_strongest_reading"))
    pub = {}
    for r in csv.DictReader(open(os.path.join(PKG, "published_results.csv"), encoding="utf-8")):
        if r["regime"] == "tuned_ensemble" and r["model"] in ("CatBoost", "Linear"):
            pub[(r["dataset"], r["model"])] = float(r["published_auc_mean_pdf"])
    margin = [pub[(r["dataset"], "CatBoost")] - pub[(r["dataset"], "Linear")] for r in units]
    for r, mg in zip(units, margin):
        r["H3_margin_auc"] = mg
    out["H3_Ak_vs_auc_margin_secondary"] = one_sided(col(units, "Ak"), margin, -1, random.Random(SEED))
    desc = {}
    S2 = col(units, "S2")
    one = [0 if r["both_verdicts"] else 1 for r in units]
    desc["H4a_with_S2"] = freedman_lane(S2, G, B, random.Random(SEED))
    desc["H4b_with_S2"] = freedman_lane(S2, G, L, random.Random(SEED))
    desc["H4a_with_one_verdict_indicator"] = freedman_lane(one, G, B, random.Random(SEED))
    desc["H4b_with_one_verdict_indicator"] = freedman_lane(one, G, L, random.Random(SEED))
    nl = [r for r in units if r["dataset"] not in leak]
    desc["H4a_without_leakage_candidates"] = freedman_lane(col(nl, "S"), col(nl, "G"), col(nl, "base_rate"), random.Random(SEED))
    desc["H4b_without_leakage_candidates"] = freedman_lane(col(nl, "S"), col(nl, "G"), col(nl, "strongest_weaker_reading"), random.Random(SEED))
    flagged = [r for r in units if r["S"] > 0]
    med = lambda v: round(statistics.median(v), 2) if v else None  # noqa: E731
    desc["flagged_S_gt_0"] = len(flagged)
    desc["median_G_flagged_unflagged"] = [med(col(flagged, "G")), med([r["G"] for r in units if r["S"] <= 0])]
    both = [r for r in units if r["both_verdicts"]]
    for tag, rs in (("all", units), ("both_verdicts", both)):
        desc[f"price_{tag}"] = {"n": len(rs), "median_disagreement": med([100 - r["A"] for r in rs]),
                                "median_q": med([r["q"] for r in rs if r["q"] is not None]),
                                "median_price": med(col(rs, "price")),
                                "negative": sum(r["price"] < 0 for r in rs),
                                "within_1.5": sum(0 <= r["price"] <= 1.5 for r in rs),
                                "above_1.5": sum(r["price"] > 1.5 for r in rs)}
    desc["counts"] = {"datasets": len(rows), "units": len(units), "both_verdicts": len(both),
                      "certified_depth": dict(Counter(col(units, "certified_depth"))),
                      "questions_asked_both_verdict_trees": dict(Counter(col(both, "questions_asked"))),
                      "identity_mismatch_cases": sum(col(units, "identity_mismatch_cases")),
                      "identity_mismatch_profiles": sum(col(units, "identity_mismatch_profiles")),
                      "median_tree_gain_over_base_both_verdicts": med([r["cv_acc_tree"] - max(r["base_rate"], 100 - r["base_rate"]) for r in both])}
    return out, desc


def write(rows, path):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


def smoke():
    """Pipeline check on spent data only: three of the thirty, one repeat, output to the console."""
    v1.DATA = os.path.join(MKW, "data")
    rng = random.Random(SEED)
    rows = []
    for code in ("BANK", "HORS", "PIMA"):
        header, X, _ = v1.load(code)
        dtypes = ["numeric" if v1.is_numeric([row[j] for row in X]) else "nominal" for j in range(len(header))]
        rows.append(run_dataset(code, dtypes, rng, 1))
        r = rows[-1]
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    print("smoke OK: every code path ran on spent data; nothing from TabArena was read")


def main():
    if "--smoke" in sys.argv:
        return smoke()
    if not os.path.exists(FROZEN):
        sys.exit("REFUSED: ADDENDUM_B_FROZEN.md does not exist. Addendum B must be approved and frozen first.")
    sha = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (FROZEN, PRESPEC)}
    resume = "--resume" in sys.argv
    if os.path.exists(CHECKPOINT) and not resume:
        sys.exit("REFUSED: a checkpoint exists; this run has started before. Use --resume and log the deviation.")
    st = selftest()  # before any TabArena file is read
    dtypes = json.load(open(os.path.join(DATA, "declared_types.json"), encoding="utf-8"))
    order = list(dtypes)  # Appendix B1 order (by size), as written by the build script
    counts = {r["dataset"]: r for r in csv.DictReader(open(os.path.join(PKG, "measured-counts.csv"), encoding="utf-8"))}
    leak = {k for k, r in counts.items() if r["flag_leakage_candidates_by_name_NOT_MEASURED"]} - {"diabetes"}
    assert len(order) == 29 and len(leak) == 8
    v1.DATA = DATA
    rng, rows, resumed = random.Random(SEED), [], []
    if resume:
        ck = pickle.load(open(CHECKPOINT, "rb"))
        rows, resumed = ck["rows"], ck["resumed"] + [len(ck["rows"])]
        rng.setstate(ck["rng_state"])
        print(f"RESUMED after {len(rows)} datasets (deviation, to be logged in Appendix B2)", flush=True)
    for name in order[len(rows):]:
        n = int(counts[name]["n_rows"])
        r = run_dataset(name, dtypes[name], rng, 10 if n <= 10000 else 1)
        rows.append(r)
        pickle.dump({"rows": rows, "rng_state": rng.getstate(), "resumed": resumed}, open(CHECKPOINT, "wb"))
        write(rows, os.path.join(HERE, "tabarena_results_partial.csv"))
        print(f"[{len(rows)}/29] {name}: n={n} S={r.get('S', float('nan')):+.2f} G={r.get('G', float('nan')):.1f} "
              f"Ak={r.get('Ak')} A={r.get('A', float('nan')):.1f} q={(r['q'] if r.get('q') is not None else float('nan')):.1f} "
              f"price={r.get('price', float('nan')):+.2f} depth={r.get('certified_depth')} asked={r.get('questions_asked')} "
              f"({r.get('seconds')} s)", flush=True)
    tests, desc = analyses(rows, leak)
    write(rows, os.path.join(HERE, "tabarena_results.csv"))
    summary = {"addendum_b_sha256": sha[FROZEN], "prespecification_sha256": sha[PRESPEC], "selftest": st,
               "protocol": {"folds": FOLDS, "seed": SEED, "permutations": PERMS, "repeats": "10 if n <= 10,000 else 1",
                            "sklearn": sklearn.__version__, "ccp_alphas": ALPHAS},
               "resumed_after_datasets": resumed, "tests": tests, "descriptive": desc}
    json.dump(summary, open(os.path.join(HERE, "tabarena_summary.json"), "w"), indent=2)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
