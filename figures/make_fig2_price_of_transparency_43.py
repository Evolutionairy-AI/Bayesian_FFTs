"""Draft Figure 2 with all 43 certified trees that offer both verdicts (three collections).
Reads DATA_SETS/Posthoc-Development/heldout_conflict_share_results.csv (run of 2026-11-06, test folds).
Computes nothing new; verifies the identity and the counts quoted in Section 3 before drawing.
    python make_fig2_price_of_transparency_43.py
"""
import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Posthoc-Development", "heldout_conflict_share_results.csv")  # the repository root
STAMP = "2026-11-13"
SURFACE, INK, MUTED, GRID, CURVE = "#ffffff", "#0b0b0b", "#52514e", "#e4e3df", "#9a9995"
ORDER = ["Holte-16", "MKW08-30", "TabArena-29"]
MARK = {"Holte-16": "o", "MKW08-30": "^", "TabArena-29": "s"}

with open(SRC, newline="", encoding="utf-8") as f:
    src = list(csv.DictReader(f))

rows = []
for r in src:
    if r["collection"] not in ORDER or r["both_verdicts"] != "True":
        continue
    rows.append({
        "collection": r["collection"], "code": r["code"], "n": int(r["n"]),
        "A_pct": float(r["cv_A"]), "q_pct": float(r["cv_q"]), "price_points": float(r["cv_price"]),
        "cv_acc_tree": float(r["cv_acc_tree"]), "cv_acc_full": float(r["cv_acc_full"]),
    })

# ---- verification against Section 3 and Table 1 -------------------------------------------------
by = {c: [r for r in rows if r["collection"] == c] for c in ORDER}
assert [len(by[c]) for c in ORDER] == [13, 17, 13], [len(by[c]) for c in ORDER]
worst = 0.0
for r in rows:
    ident = (100 - r["A_pct"]) * (2 * r["q_pct"] - 100) / 100
    gap = r["cv_acc_full"] - r["cv_acc_tree"]
    worst = max(worst, abs(ident - r["price_points"]), abs(gap - r["price_points"]))
print(f"identity and accuracy gap reproduce the saved price on all 43 rows within {worst:.4f} points")
assert worst < 0.01
med = statistics.median
print("price medians", [round(med(r["price_points"] for r in by[c]), 1) for c in ORDER],
      "all 43:", round(med(r["price_points"] for r in rows), 1))
bins = []
for c in ORDER:
    p = [round(r["price_points"], 1) for r in by[c]]
    bins.append((sum(v < 0 for v in p), sum(0 <= v <= 1.5 for v in p), sum(v > 1.5 for v in p)))
print("negative; 0 to 1.5; above 1.5:", bins)
assert bins == [(5, 2, 6), (2, 4, 11), (4, 2, 7)], bins
rest = sorted(round(r["price_points"], 1) for r in rows if round(r["price_points"], 1) > 1.5)
print("trailing", len(rest), "from", rest[0], "to", rest[-1])
assert (len(rest), rest[0], rest[-1]) == (24, 1.7, 19.6)
for r in rows:
    r["price_negative"] = round(r["price_points"], 1) < 0

# ---- data table for the figure ------------------------------------------------------------------
out_csv = os.path.join(HERE, f"Fig2_price_data_43_{STAMP}.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    fields = ["collection", "code", "n", "A_pct", "q_pct", "price_points", "price_negative", "cv_acc_tree", "cv_acc_full"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in sorted(rows, key=lambda r: (ORDER.index(r["collection"]), r["price_points"])):
        out = dict(r)
        for k in ("A_pct", "q_pct", "price_points", "cv_acc_tree", "cv_acc_full"):
            out[k] = f"{r[k]:.1f}"
        w.writerow(out)
print("wrote", out_csv)

# ---- figure ---------------------------------------------------------------------------------------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "xtick.labelsize": 7, "ytick.labelsize": 7})
fig, ax = plt.subplots(figsize=(3.5, 3.4), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.grid(True, axis="x", color=GRID, linewidth=0.6, zorder=0)
X0, X1 = 60, 101

As = np.linspace(X0, 99.6, 400)
for delta in (-10, -5, 0, 5, 10, 20):
    qs = 50 + 50 * delta / (100 - As)
    keep = (qs >= 0) & (qs <= 100)
    lw, col = (1.1, MUTED) if delta == 0 else (0.8, CURVE)
    ax.plot(As[keep], qs[keep], color=col, linewidth=lw, zorder=1)
    label = "Δ = 0" if delta == 0 else "Δ = " + f"{delta:+d}".replace("-", "−")
    if delta == 20:
        ax.text(80.8, 99, label, fontsize=6.5, color=MUTED, va="top", ha="left", zorder=2)
    else:
        ax.text(X0 + 0.6, 50 + 50 * delta / (100 - X0) + (1.2 if delta >= 0 else -1.2), label,
                fontsize=6.5, color=MUTED, va="bottom" if delta >= 0 else "top", ha="left", zorder=2)

for r in rows:
    m = MARK[r["collection"]]
    face = INK if r["price_negative"] else SURFACE
    size = 28 if m == "s" else 34
    ax.scatter(r["A_pct"], r["q_pct"], s=size * 2, marker=m, facecolor=SURFACE, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.scatter(r["A_pct"], r["q_pct"], s=size, marker=m, facecolor=face, edgecolor=INK, linewidth=1.0, zorder=4)

# labels: the eight of the earlier figure, and four TabArena trees (two negative prices, two extremes)
labels = {"CH": (5, 0, "left", "CH"), "LA": (5, 0, "left", "LA"), "HO": (-5, 0, "right", "HO"),
          "G2": (-5, 0, "right", "G2"), "MU": (-5, 0, "right", "MU"), "SO": (-5, 2, "right", "SO"),
          "PIMA": (-5, 0, "right", "PIMA"), "VO": (-5, 0, "right", "VO, VOTE"),
          "Bioresponse": (5, 0, "left", "BIOR"), "online_shoppers_intention": (-5, -5, "right", "SHOP"),
          "NATICUSdroid": (-5, 3, "right", "NATI"), "customer_satisfaction_in_airline": (0, 8, "center", "AIRL")}
for r in rows:
    if r["code"] in labels:
        dx, dy, ha, text = labels[r["code"]]
        ax.annotate(text, (r["A_pct"], r["q_pct"]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=6.5, color=MUTED, va="center", ha=ha, zorder=5)

ax.set_xlim(X0, X1)
ax.set_ylim(-3, 104)
ax.set_xticks(range(60, 101, 10))
ax.set_yticks(range(0, 101, 25))
ax.set_xlabel("Agreement A with the Bayesian classifier (%)")
ax.set_ylabel("Bayesian classifier correct, given a disagreement, q (%)")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
n_neg = sum(r["price_negative"] for r in rows)
handles = [
    Line2D([], [], marker="o", color=INK, markerfacecolor=SURFACE, linestyle="", markersize=5.5, label="Holte, 13 trees"),
    Line2D([], [], marker="^", color=INK, markerfacecolor=SURFACE, linestyle="", markersize=5.5, label="Martignon et al., 17 trees"),
    Line2D([], [], marker="s", color=INK, markerfacecolor=SURFACE, linestyle="", markersize=5.0, label="TabArena, 13 trees"),
    Line2D([], [], marker="o", color=INK, markerfacecolor=INK, linestyle="", markersize=5.5, label=f"Filled: price Δ < 0, {n_neg} trees"),
]
ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=6.5, handletextpad=0.4, borderaxespad=0.4)
fig.tight_layout(pad=0.4)
for ext in ("png", "pdf"):
    out = os.path.join(HERE, f"Fig2_price_of_transparency_43_DRAFT_{STAMP}.{ext}")
    fig.savefig(out, dpi=300, facecolor=SURFACE)
    print("wrote", out)
