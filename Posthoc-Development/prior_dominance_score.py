"""DEVELOPMENT on spent data only (Holte's sixteen and the thirty). Post hoc, exploratory.
A continuous prior-dominance score from the theorem, against how much published benchmarks gain over the base rate.
Touches no fresh collection."""
import csv
import json
import os
import random
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the repository root
sys.path.insert(0, ROOT + "/Holte-16/analysis")
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

rows = []
# ---- the thirty
PKG = ROOT + "/MKW08-30"
res = {r["code"]: r for r in csv.DictReader(open(PKG + "/analysis/confirmatory_results.csv", newline=""))}
holte_data = v1.DATA
v1.DATA = os.path.join(PKG, "data")
for ds in json.load(open(PKG + "/manifest.json", encoding="utf-8"))["datasets"]:
    code = ds["code"]
    header, cols, cls = v2.prepare(code)
    counts = Counter(cls)
    c1 = "1" if counts["1"] >= counts["0"] else "0"
    y = [1 if c == c1 else 0 for c in cls]
    m = v2.fit(cols, y, range(len(y)))
    r = res[code]
    best = max(float(r["woike_LR"]), float(r["woike_CART"]))
    rows.append({"set": "MKW", "code": code, "base": float(r["base_rate"]), "best": best, "l0": m["l0"],
                 "llo_max": m["llo"][0], "lm_max": max(-x for x in m["lms"]), "K": m["K"],
                 "deg": r["spine_nondegenerate"] != "True"})
# ---- Holte's twelve two-category datasets (C4 is a two-category accuracy only there)
v1.DATA = holte_data
hres = {r["code"]: r for r in csv.DictReader(open(ROOT + "/Holte-16/analysis/indicator_results.csv", newline=""))}
for code, r in hres.items():
    if r["classes"] != "2":
        continue
    header, cols, cls = v2.prepare(code)
    maj = Counter(cls).most_common(1)[0][0]
    y = [1 if c == maj else 0 for c in cls]
    m = v2.fit(cols, y, range(len(y)))
    rows.append({"set": "Holte", "code": code, "base": float(r["base_rate"]), "best": float(r["holte_c4"]), "l0": m["l0"],
                 "llo_max": m["llo"][0], "lm_max": max(-x for x in m["lms"]), "K": m["K"],
                 "deg": r["spine_nondegenerate"] != "True"})

for r in rows:
    r["G"] = 100 * (r["best"] - r["base"]) / (100 - r["base"])      # share of headroom gained by the published benchmark
    r["S1"] = abs(r["l0"]) - r["llo_max"]                            # > 0: no attribute outweighs the prior by its weaker reading
    r["S2"] = abs(r["l0"]) - r["lm_max"]                             # > 0: no single attribute can carry the verdict to the rarer category


def partial(xs, ys, zs):
    rxy, rxz, ryz = v1.spearman(xs, ys), v1.spearman(xs, zs), v1.spearman(ys, zs)
    return (rxy - rxz * ryz) / ((1 - rxz ** 2) * (1 - ryz ** 2)) ** 0.5


def perm_p(xs, ys, zs, obs, rng, n=5000):
    ys = list(ys); hits = 0
    for _ in range(n):
        rng.shuffle(ys)
        hits += partial(xs, ys, zs) <= obs + 1e-12
    return (hits + 1) / (n + 1)


rng = random.Random(20260919)
for name, g in (("the thirty", [r for r in rows if r["set"] == "MKW"]), ("Holte's twelve", [r for r in rows if r["set"] == "Holte"]),
                ("pooled 42", rows)):
    G = [r["G"] for r in g]; B = [r["base"] for r in g]
    print(f"\n== {name} (n = {len(g)})")
    print(f"   rho(base rate, G)            = {v1.spearman(B, G):+.2f}")
    for s in ("S1", "S2"):
        S = [r[s] for r in g]
        pr = partial(S, G, B)
        print(f"   rho({s}, G) = {v1.spearman(S, G):+.2f} | rho({s}, base rate) = {v1.spearman(S, B):+.2f} | "
              f"partial rho({s}, G | base rate) = {pr:+.2f} (one-sided perm p = {perm_p(S, G, B, pr, rng):.3f})")
    pb = partial(B, G, [r["S1"] for r in g])
    print(f"   partial rho(base rate, G | S1) = {pb:+.2f}")

print("\nFlag = S1 > 0 (no attribute outweighs the prior). Flagged datasets, by gain share:")
for r in sorted([r for r in rows if r["S1"] > 0], key=lambda r: r["G"]):
    print(f"   {r['set']:5} {r['code']:5} base {r['base']:5.1f}  best {r['best']:5.1f}  G {r['G']:5.0f}%  S1 {r['S1']:+.2f}  S2 {r['S2']:+.2f}  K {r['K']:3d}  majority-only tree: {r['deg']}")
unfl = [r for r in rows if r["S1"] <= 0]
print(f"Unflagged: n = {len(unfl)}; with G < 25%: {[(r['code'], round(r['G'])) for r in unfl if r['G'] < 25]}")

print("\nRival predictor: the strongest attribute alone, without the prior")
for name, g in (("the thirty", [r for r in rows if r["set"] == "MKW"]), ("Holte's twelve", [r for r in rows if r["set"] == "Holte"]), ("pooled 42", rows)):
    G = [r["G"] for r in g]; L = [r["llo_max"] for r in g]; S = [r["S1"] for r in g]; P = [abs(r["l0"]) for r in g]
    print(f"   {name}: rho(strongest weaker reading, G) = {v1.spearman(L, G):+.2f} | rho(S1, G) = {v1.spearman(S, G):+.2f} | "
          f"partial rho(S1, G | strongest reading) = {partial(S, G, L):+.2f} | partial rho(strongest reading, G | prior) = {partial(L, G, P):+.2f}")
