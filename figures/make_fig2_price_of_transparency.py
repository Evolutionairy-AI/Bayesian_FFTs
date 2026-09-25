"""Draft Figure 2 for Section 3: the price of transparency in thirty certified trees.
Reads the saved price-identity results (DATA_SETS/Posthoc-Development/price_identity_results.csv)
and the two indicator files for names, depths and accuracies. Computes nothing new; verifies the
identity and the medians quoted in Section 3 before drawing.
    python make_fig2_price_of_transparency.py
"""
import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "..")  # the repository root
STAMP = "2026-09-23"
SURFACE, INK, MUTED, GRID, CURVE = "#ffffff", "#0b0b0b", "#52514e", "#e4e3df", "#9a9995"


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


price = read(os.path.join(DS, "Posthoc-Development", "price_identity_results.csv"))
holte_ind = {r["code"]: r for r in read(os.path.join(DS, "Holte-16", "analysis", "indicator_results.csv"))}
mkw_ind = {r["code"]: r for r in read(os.path.join(DS, "MKW08-30", "analysis", "confirmatory_results.csv"))}
holte_names = {r["code"]: r["name"] for r in read(os.path.join(DS, "Holte-16", "expected-counts.csv"))}
mkw_names = {r["code"]: r["woike_label"] for r in read(os.path.join(DS, "MKW08-30", "expected-counts.csv"))}

rows = []
for r in price:
    if r["tree_offers_both_verdicts"] != "True":
        continue
    holte = r["collection"] == "Holte-16"
    ind = (holte_ind if holte else mkw_ind)[r["code"]]
    A, q, d = float(r["cv_agreement"]), float(r["cv_q_full_right_when_disagree"]), float(r["cv_price_points"])
    rows.append({
        "collection": r["collection"], "code": r["code"],
        "dataset": (holte_names if holte else mkw_names)[r["code"]], "n": int(r["n"]),
        "questions": int(ind["kmax"]), "A_pct": A, "q_pct": q, "price_points": d,
        "price_negative": d < 0, "cv_acc_tree": float(ind["cv_acc_spine"]), "cv_acc_full": float(ind["cv_acc_full"]),
    })

# ---- verification against the text of Section 3 -------------------------------------------
h = [r for r in rows if r["collection"] == "Holte-16"]
m = [r for r in rows if r["collection"] == "MKW08-30"]
assert (len(h), len(m)) == (13, 17), (len(h), len(m))
worst = 0.0
for r in rows:
    ident = (1 - r["A_pct"] / 100) * (2 * r["q_pct"] / 100 - 1) * 100
    gap = r["cv_acc_full"] - r["cv_acc_tree"]
    worst = max(worst, abs(ident - r["price_points"]), abs(gap - r["price_points"]))
print(f"identity and accuracy gap reproduce the saved price on all 30 rows within {worst:.2f} points (rounding)")
med = statistics.median
print("disagreement medians", round(100 - med(r["A_pct"] for r in h), 1), round(100 - med(r["A_pct"] for r in m), 1))
print("q medians", med(r["q_pct"] for r in h), med(r["q_pct"] for r in m))
print("price medians", med(r["price_points"] for r in h), med(r["price_points"] for r in m))
neg = [r for r in rows if r["price_negative"]]
within = [r for r in rows if 0 <= r["price_points"] <= 1.5]
rest = sorted(r["price_points"] for r in rows if r["price_points"] > 1.5)
print("negative", len(neg), sorted(r["code"] for r in neg))
print("within 1.5", len(within), "remaining", len(rest), "range", rest[0], rest[-1])
assert len(neg) == 7 and len(within) == 6 and len(rest) == 17

# ---- data table for the figure ------------------------------------------------------------
out_csv = os.path.join(HERE, f"Fig2_price_data_{STAMP}.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r["collection"], r["price_points"])):
        w.writerow(r)
print("wrote", out_csv)

# ---- figure ---------------------------------------------------------------------------------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "xtick.labelsize": 7, "ytick.labelsize": 7})
fig, ax = plt.subplots(figsize=(3.5, 3.4), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.grid(True, axis="x", color=GRID, linewidth=0.6, zorder=0)
X0, X1 = 60, 101

# equal-price curves: q = 50 + 50 * delta / (100 - A)
import numpy as np
As = np.linspace(X0, 99.6, 400)
for delta in (-10, -5, 0, 5, 10, 20):
    qs = 50 + 50 * delta / (100 - As)
    keep = (qs >= 0) & (qs <= 100)
    lw, col = (1.1, MUTED) if delta == 0 else (0.8, CURVE)
    ax.plot(As[keep], qs[keep], color=col, linewidth=lw, zorder=1)
    label = "Δ = 0" if delta == 0 else "Δ = " + f"{delta:+d}".replace("-", "−")
    if delta == 20:   # this curve leaves the top at A = 80; the left edge is taken by CH
        ax.text(80.8, 99, label, fontsize=6.5, color=MUTED, va="top", ha="left", zorder=2)
    else:
        ax.text(X0 + 0.6, 50 + 50 * delta / (100 - X0) + (1.2 if delta >= 0 else -1.2), label,
                fontsize=6.5, color=MUTED, va="bottom" if delta >= 0 else "top", ha="left", zorder=2)

for r in rows:
    marker = "o" if r["collection"] == "Holte-16" else "^"
    face = INK if r["price_negative"] else SURFACE
    ax.scatter(r["A_pct"], r["q_pct"], s=70, marker=marker, facecolor=SURFACE, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.scatter(r["A_pct"], r["q_pct"], s=34, marker=marker, facecolor=face, edgecolor=INK, linewidth=1.0, zorder=4)

labels = {"CH": (5, 0, "left"), "LA": (5, 0, "left"), "HO": (-5, 0, "right"), "G2": (-5, 0, "right"),
          "MU": (-5, 0, "right"), "SO": (-5, 2, "right"), "PIMA": (-5, 0, "right"), "VO": (-5, 0, "right")}
for r in rows:
    if r["code"] in labels:
        dx, dy, ha = labels[r["code"]]
        text = "VO, VOTE" if r["code"] == "VO" else r["code"]
        ax.annotate(text, (r["A_pct"], r["q_pct"]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=6.5, color=MUTED, va="center", ha=ha, zorder=5)

ax.set_xlim(X0, X1)
ax.set_ylim(-3, 104)
ax.set_xticks(range(60, 101, 10))
ax.set_yticks(range(0, 101, 25))
ax.set_xlabel("Agreement A with the additive Bayesian classifier (%)")
ax.set_ylabel("Share q of disagreements the additive classifier wins (%)")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
handles = [
    Line2D([], [], marker="o", color=INK, markerfacecolor=SURFACE, linestyle="", markersize=5.5, label="Holte (1993), 13 trees"),
    Line2D([], [], marker="^", color=INK, markerfacecolor=SURFACE, linestyle="", markersize=5.5, label="Martignon et al. (2008), 17 trees"),
    Line2D([], [], marker="o", color=INK, markerfacecolor=INK, linestyle="", markersize=5.5, label="Filled: price Δ < 0, 7 trees"),
]
ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=6.5, handletextpad=0.4, borderaxespad=0.4)
fig.tight_layout(pad=0.4)
for ext in ("png", "pdf"):
    out = os.path.join(HERE, f"Fig2_price_of_transparency_DRAFT_{STAMP}.{ext}")
    fig.savefig(out, dpi=300, facecolor=SURFACE)
    print("wrote", out)
