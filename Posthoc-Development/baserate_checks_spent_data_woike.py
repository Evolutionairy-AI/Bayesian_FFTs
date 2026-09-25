# Addendum A, item 7: a copy of baserate_checks_spent_data.py that differs only in the data folder and in the names of the files read and written.
"""Checks of the base-rate observation on data already spent. Post hoc, descriptive.
Reads saved results and the transcribed published tables only; runs no harness; touches no fresh collection."""
import csv
import os
import json
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the repository root
PKG = ROOT + "/MKW08-30"
mkw = list(csv.DictReader(open(PKG + "/analysis/robustness_woike_results.csv", newline="")))
hol = list(csv.DictReader(open(ROOT + "/Holte-16/analysis/indicator_results.csv", newline="")))
label = {d["code"]: d["woike_label"] for d in json.load(open(PKG + "/manifest.json", encoding="utf-8"))["datasets"]}
bench = {}
for r in csv.DictReader(open(PKG + "/analysis/woike_tables_6_10_to_6_12.csv", newline="", encoding="utf-8")):
    if r["accuracy"] != "":  # blank = dataset dropped at that training size in the printed table
        bench[(r["dataset"], r["block"], r["model"])] = float(r["accuracy"])
f = lambda r, k: float(r[k])
deg = [r for r in mkw if r["spine_nondegenerate"] != "True"]
nd = [r for r in mkw if r["spine_nondegenerate"] == "True"]

print("A. Woike's published accuracies: how many datasets fall BELOW the base rate, by group (13 majority-only / 17 both verdicts)")
models = ["VF", "MV", "ZV", "MS", "ZS", "MA", "SF", "VM", "LR", "CT"]
for block in ("pred15", "pred50", "pred90"):
    line = []
    for m in models:
        cnt = []
        for g in (deg, nd):
            vals = [(bench.get((label[r["code"]], block, m)), f(r, "base_rate")) for r in g]
            vals = [(a, b) for a, b in vals if a is not None]
            cnt.append(f"{sum(a < b for a, b in vals)}/{len(vals)}")
        line.append(f"{m} {cnt[0]} vs {cnt[1]}")
    print(f"   {block}: " + " | ".join(line))

print("\nB. Gain of the better of LR and CART over the base rate, as a share of the headroom (median), by group")
for block in ("pred15", "pred50", "pred90"):
    out = []
    for g in (deg, nd):
        sh = []
        for r in g:
            lr, ct = bench.get((label[r["code"]], block, "LR")), bench.get((label[r["code"]], block, "CT"))
            if lr is None or ct is None:
                continue
            sh.append(100 * (max(lr, ct) - f(r, "base_rate")) / (100 - f(r, "base_rate")))
        out.append(f"{st.median(sh):.0f}% (n={len(sh)})")
    print(f"   {block}: majority-only {out[0]} | both verdicts {out[1]}")

print("\nC. Holte's sixteen: the same look, with his own C4 and 1R accuracies")
for r in hol:
    r["_deg"] = r["spine_nondegenerate"] != "True"
for name, g in (("majority-only", [r for r in hol if r["_deg"]]), ("both verdicts", [r for r in hol if not r["_deg"]])):
    sh = [100 * (f(r, "holte_c4") - f(r, "base_rate")) / (100 - f(r, "base_rate")) for r in g]
    print(f"   {name}: n = {len(g)} {[r['code'] for r in g]}")
    print(f"      base rates {sorted(round(f(r,'base_rate'),1) for r in g)}")
    print(f"      C4 gain over base rate, points: {[round(f(r,'holte_c4')-f(r,'base_rate'),1) for r in g]}; share of headroom median {st.median(sh):.0f}%")
    print(f"      1R below base rate: {sum(f(r,'holte_1r') < f(r,'base_rate') for r in g)}/{len(g)}")

print("\nD. Is the audit simply 'no single attribute outweighs the prior'?  Z_beats_prior by group (thirty)")
print("   majority-only:", sorted(int(float(r["Z_beats_prior"])) for r in deg))
print("   both verdicts:", sorted(int(float(r["Z_beats_prior"])) for r in nd))
print("   Holte majority-only:", [(r["code"], r["Z_beats_prior"]) for r in hol if r["_deg"]],
      "| both verdicts:", sorted(int(float(r["Z_beats_prior"])) for r in hol if not r["_deg"]))
