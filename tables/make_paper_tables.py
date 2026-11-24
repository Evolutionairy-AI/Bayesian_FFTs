"""Table 1, Extended Data Tables 2 to 4, and the counts and medians quoted in the summary, Section 3, Methods and
Extended Data Table 1 of the paper, computed from the saved result files only (no data file is read, nothing is
refitted). Written 2026-11-24 to make every number of the final text traceable to a script.

Rounding follows the saved tables (as in the generator of Table 1 of 2026-11-06): the values of the sixteen and the
thirty are rounded to one decimal per dataset before a median or quartile is taken, the TabArena values are used with
the four decimals of their results files. Quartiles are linear interpolations between order statistics,
statistics.quantiles(..., n=4, method="inclusive").

    python tables/make_paper_tables.py
        -> tables/table1_rows.tex                 the data rows of Table 1, as typeset
           tables/extended_data_table2.csv        Extended Data Table 2 (the twelve datasets whose files differ)
           tables/extended_data_table3.csv        Extended Data Table 3 (the 43 certified trees of Figure 2)
           tables/extended_data_table4.csv        Extended Data Table 4 (the 29 TabArena tasks)
           tables/paper_numbers_log.txt           every other count and median, with the file it comes from

Standard library only.
"""
import csv
import json
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # the repository root
LOG = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line)
    LOG.append(line)


def rows(rel):
    with open(os.path.join(ROOT, rel), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def write_csv(name, header, body):
    with open(os.path.join(HERE, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(body)


def f1(x):
    # Python formatting, as used for the paper. Three medians or quartiles are exact ties at the second decimal
    # (Holte s median 30.45, thirty A upper quartile 90.55, Woike s median 56.35); all three print rounded down
    # (30.4, 90.5, 56.3), as in the paper.
    return "n/a" if x is None else f"{x:.1f}"


def tex(x):
    s = f1(x)
    return "$-$" + s[1:] if s.startswith("-") else s


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5


# ---------------------------------------------------------------- inputs
HELD = rows("Posthoc-Development/heldout_conflict_share_results.csv")
HOLTE = {r["code"]: r for r in rows("Holte-16/analysis/indicator_results.csv")}
MKW = {r["code"]: r for r in rows("MKW08-30/analysis/confirmatory_results.csv")}
MKWW = {r["code"]: r for r in rows("MKW08-30/analysis/robustness_woike_results.csv")}
TAB = {r["dataset"]: r for r in rows("TabArena-Binary/analysis/tabarena_results.csv")}
QUEST = {r["code"]: r for r in rows("figures/Fig2_questions_asked_2026-09-24.csv")}
COLLS = ["Holte-16", "MKW08-30", "TabArena-29"]
PER = {"Holte-16": HOLTE, "MKW08-30": MKW, "TabArena-29": TAB}


def held(coll, both=None):
    rs = [r for r in HELD if r["collection"] == coll]
    return [r for r in rs if r["both_verdicts"] == "True"] if both else rs


def val(r, k):
    """One decimal per dataset for the sixteen and the thirty; four decimals for TabArena."""
    if r[k] == "":
        return None
    v = float(r[k])
    return v if r["collection"] == "TabArena-29" else round(v, 1)


def col(coll, both, k):
    return [v for v in (val(r, k) for r in held(coll, both)) if v is not None]


def depth(coll, code):
    r = PER[coll][code]
    return int(r["certified_depth"] if coll == "TabArena-29" else r["kmax"])


def base_larger(coll, code):
    b = float(PER[coll][code]["base_rate"])
    return max(b, 100 - b)


assert [len(held(c)) for c in COLLS] == [16, 30, 29] and [len(held(c, True)) for c in COLLS] == [13, 17, 13]

# ---------------------------------------------------------------- Table 1
def cell(xs):
    q1, _, q3 = st.quantiles(xs, n=4, method="inclusive")
    return f"{tex(st.median(xs))} [{tex(q1)}, {tex(q3)}]"


def bins(coll):
    p = col(coll, True, "cv_price")
    return f"{sum(x < 0 for x in p)}; {sum(0 <= x <= 1.5 for x in p)}; {sum(x > 1.5 for x in p)}"


deep = {c: sum(depth(c, r["code"]) in (2, 3) for r in held(c)) for c in COLLS}
assert max(depth(c, r["code"]) for c in COLLS for r in held(c)) == 3
T1 = [
    ("Datasets", [str(len(held(c))) for c in COLLS]),
    ("Datasets with a certified depth of two or three", [str(deep[c]) for c in COLLS]),
    ("Conflict rate, $c$", [cell(col(c, False, "cv_c")) for c in COLLS]),
    ("Agreement given a conflict, $s$", [cell(col(c, False, "cv_s")) for c in COLLS]),
    ("Agreement, $A$", [cell(col(c, False, "cv_A")) for c in COLLS]),
    ("Trees", [str(len(held(c, True))) for c in COLLS]),
    ("Conflict rate, $c$", [cell(col(c, True, "cv_c")) for c in COLLS]),
    ("Agreement given a conflict, $s$", [cell(col(c, True, "cv_s")) for c in COLLS]),
    ("Agreement, $A$", [cell(col(c, True, "cv_A")) for c in COLLS]),
    ("Bayesian classifier correct, given a disagreement, $q$", [cell(col(c, True, "cv_q")) for c in COLLS]),
    ("Price, $\\Delta$, points", [cell(col(c, True, "cv_price")) for c in COLLS]),
    ("Trees with $\\Delta < 0$; $0 \\le \\Delta \\le 1.5$; $\\Delta > 1.5$", [bins(c) for c in COLLS]),
]
with open(os.path.join(HERE, "table1_rows.tex"), "w", encoding="utf-8", newline="\n") as f:
    for label, cells in T1:
        f.write(label + " & " + " & ".join(cells) + " \\\\\n")

# ---------------------------------------------------------------- Extended Data Table 3 (43 trees)
TAB_CODES = {"Bioresponse": "BIOR", "online_shoppers_intention": "SHOP", "heloc": "HELO", "Fitness_Club": "FITN",
             "E-CommereShippingData": "ECOM", "credit_card_clients_default": "CCCD", "Marketing_Campaign": "MARK",
             "hazelnut-spread-contaminant-detection": "HAZE", "credit-g": "CRDG",
             "in_vehicle_coupon_recommendation": "COUP", "qsar-biodeg": "QSAR",
             "customer_satisfaction_in_airline": "AIRL", "NATICUSdroid": "NATI"}  # labels as printed in the paper


def questions(coll, code):
    if coll == "TabArena-29":
        return int(TAB[code]["questions_asked"])
    q = QUEST[code]
    assert int(q["certified_depth"]) == depth(coll, code)
    return int(q["questions_asked"])


ED3 = []
for c in COLLS:
    for r in sorted(held(c, True), key=lambda r: float(r["cv_price"])):
        code = r["code"]
        ED3.append([c, TAB_CODES.get(code, code), r["n"], depth(c, code), questions(c, code)]
                   + [f1(float(r[k])) for k in ("cv_c", "cv_s", "cv_A", "cv_q", "cv_price", "cv_acc_tree", "cv_acc_full")])
write_csv("extended_data_table3.csv",
          ["collection", "code", "n", "depth", "questions", "c", "s", "A", "q", "price", "tree", "full"], ED3)

# ---------------------------------------------------------------- Extended Data Table 4 (29 TabArena tasks)
HT = {r["code"]: r for r in held("TabArena-29")}
order = sorted((t for t in TAB if TAB[t]["both_verdicts"] == "True"), key=str.lower) + \
        sorted((t for t in TAB if TAB[t]["both_verdicts"] != "True"), key=str.lower)
ED4 = []
for t in order:
    r, h = TAB[t], HT[t]
    both = r["both_verdicts"] == "True"
    num = lambda k: f1(float(r[k])) if r[k] != "" else "n/a"
    ED4.append([t, f"{int(r['n']):,}", f"{int(r['K_kept']):,}", num("base_rate"), "yes" if float(r["S"]) > 0 else "no",
                r["certified_depth"], r["questions_asked"] if both else "--",
                f1(float(h["cv_c"])), f1(float(h["cv_s"])), num("A"), num("q"), num("price"),
                num("cv_acc_tree"), num("cv_acc_full"), num("benchmark_acc"), num("G")])
write_csv("extended_data_table4.csv", ["task", "n", "attributes", "base", "flag", "depth", "questions", "c", "s", "A",
                                       "q", "price", "tree", "full", "benchmark", "G"], ED4)

# ---------------------------------------------------------------- Extended Data Table 2 (twelve datasets)
INSAMPLE = ("n", "attributes", "K_kept", "base_rate", "lambda0", "Ak_agree_spine", "ck_conflict_spine",
            "wk_win_spine", "kmax", "Z_beats_prior", "spine_nondegenerate")
manifest = load("MKW08-30/manifest.json")["datasets"]
ED2, others, cv_gap = [], [], 0.0
for ds in manifest:
    p, w = MKW[ds["code"]], MKWW[ds["code"]]
    if all(p[k] == w[k] for k in INSAMPLE):
        others.append(ds["code"])
        cv_gap = max(cv_gap, abs(float(p["cv_acc_spine"]) - float(w["cv_acc_spine"])),
                     abs(float(p["cv_acc_full"]) - float(w["cv_acc_full"])))
        continue
    pair = lambda k: f"{p[k]} / {w[k]}"
    assert p["margin_H1"] == w["margin_H1"]
    margin = float(p["margin_H1"])
    ED2.append([ds["code"], pair("n"), pair("attributes"), pair("Ak_agree_spine"), pair("ck_conflict_spine"),
                pair("wk_win_spine"), pair("kmax"), pair("cv_acc_spine"), pair("cv_acc_full"), f"{margin:g}"])
write_csv("extended_data_table2.csv", ["code", "cases", "attributes", "agreement", "conflict_rate", "tree_prevails",
                                       "depth", "tree_cv", "additive_cv", "margin"], ED2)

# ---------------------------------------------------------------- counts and medians quoted in the text
both43 = [r for c in COLLS for r in held(c, True)]
all75 = [r for c in COLLS for r in held(c)]
say("== Summary paragraph")
say("certified depth 2 or 3 (Holte kmax, MKW kmax, TabArena certified_depth):", [deep[c] for c in COLLS],
    "total", sum(deep.values()), "of", len(all75), "| deepest certified depth:", 3)
say("median agreement A over all 75 datasets (one-decimal rule):", f1(st.median(val(r, "cv_A") for r in all75)),
    "| unrounded:", round(st.median(float(r["cv_A"]) for r in all75), 4))
p43 = [float(r["cv_price"]) for r in both43]
say("trees that offer both verdicts:", len(both43), "| median price over the 43:", f1(st.median(p43)),
    "| negative:", sum(p < 0 for p in p43))

say("== Section 3")
for c in COLLS:
    K = sum(int(PER[c][r["code"]]["K_kept"]) for r in held(c))
    Z = sum(int(PER[c][r["code"]]["Z_beats_prior"]) for r in held(c))
    full = sum(depth(c, r["code"]) == int(PER[c][r["code"]]["K_kept"]) for r in held(c))
    say(f"{c}: attributes kept {K}, attributes that outweigh the prior singly {Z}, "
        f"datasets where Condition (1) holds over all attributes {full}")
K3 = sum(int(PER[c][r["code"]]["K_kept"]) for c in COLLS for r in held(c))
Z3 = sum(int(PER[c][r["code"]]["Z_beats_prior"]) for c in COLLS for r in held(c))
hs, cs = load("Holte-16/analysis/indicator_summary.json"), load("MKW08-30/analysis/confirmatory_summary.json")
assert (hs["attributes_W"], hs["Z_beats_prior"], cs["counts"]["attributes_kept"], cs["counts"]["attributes_outweighing_prior"]) == \
       (sum(int(HOLTE[k]["K_kept"]) for k in HOLTE), sum(int(HOLTE[k]["Z_beats_prior"]) for k in HOLTE),
        sum(int(MKW[k]["K_kept"]) for k in MKW), sum(int(MKW[k]["Z_beats_prior"]) for k in MKW))
say(f"all three: {Z3} of {K3:,} attributes outweigh the prior log-odds of their dataset")
for tag, k in (("A", "cv_A"), ("c", "cv_c"), ("s", "cv_s")):
    meds = [st.median(col(c, False, k)) for c in COLLS]
    say(f"median {tag}, all datasets:", [f1(m) for m in meds], "-> whole percent", [round(m + 1e-9) for m in meds])
say("trees that offer both verdicts:", [len(held(c, True)) for c in COLLS],
    "| one-class trees:", [len(held(c)) - len(held(c, True)) for c in COLLS])
qs = [questions(c, r["code"]) for c in COLLS for r in held(c, True)]
early = [r["code"] for c in COLLS for r in held(c, True) if questions(c, r["code"]) < depth(c, r["code"])]
say("questions asked by the 43 trees: one", qs.count(1), "two", qs.count(2), "three", qs.count(3),
    "| stop before their certified depth:", len(early), early)
gains = [st.median(float(r["cv_acc_tree"]) - base_larger(c, r["code"]) for r in held(c, True)) for c in COLLS]
say("median gain of the 43 trees over the base rate (share of the larger class), points:", [f1(g) for g in gains])
say("median price by collection:", [f1(st.median(col(c, True, "cv_price"))) for c in COLLS])
p1 = [round(p, 1) for p in p43]
trail = sorted(p for p in p1 if p > 1.5)
say("of the 43: price <= 0 (tree matches or exceeds B):", sum(p <= 0 for p in p1), "| 0 < price <= 1.5:",
    sum(0 < p <= 1.5 for p in p1), "| price > 1.5:", len(trail), "from", trail[0], "to", trail[-1])
iris = [r for r in held("MKW08-30") if r["code"] == "IRIS"][0]
say("Iris (thirty): tree", f1(float(iris["cv_acc_tree"])), "Bayesian classifier", f1(float(iris["cv_acc_full"])),
    "| Woike's CART at 90% training:", MKW["IRIS"]["woike_CART"])
say("TabArena tasks where the Bayesian classifier is below the base rate:",
    sum(float(r["cv_acc_full"]) < float(r["base_rate"]) for r in TAB.values()), "of", len(TAB))
maj = [k for k in MKW if MKW[k]["spine_nondegenerate"] == "False"]
say("the thirty, one-class trees:", len(maj), "| median base rate:", f1(st.median(float(MKW[k]["base_rate"]) for k in maj)))

say("== Methods")
nh = load("Holte-16/analysis/summary.json")["total_objects"]
nm, nw = sum(int(MKW[k]["n"]) for k in MKW), sum(int(MKWW[k]["n"]) for k in MKWW)
say(f"objects: Holte {nh:,} + thirty {nm:,} = {nh + nm:,}; Woike's files {nw:,}; TabArena cases "
    f"{sum(int(r['n']) for r in TAB.values()):,} (identity mismatches: cases "
    f"{sum(int(r['identity_mismatch_cases']) for r in TAB.values())}, profiles "
    f"{sum(int(r['identity_mismatch_profiles']) for r in TAB.values())})")
appx = open(os.path.join(ROOT, "MKW08-30/data/APPENDIX_A.md"), encoding="utf-8").read()
counts = [(int(a), int(b)) for a, b in re.findall(r"Attributes \((\d+); Woike used (\d+)\)", appx)]
say("attribute lists against Woike's counts: equal", sum(a == b for a, b in counts), "| more", sum(a > b for a, b in counts),
    "| fewer", sum(a < b for a, b in counts))
rule = dict(re.findall(r"\*\*\d+\. ([A-Z]+)\*\*.*?Rows: ([^.]*)\.", appx))
unrec, transposed = {"HORS", "VOTE"}, {"PIMA"}   # named in Methods
noreduce = [k for k, v in rule.items() if v == "all" and k not in unrec | transposed]
reduce_ = [k for k, v in rule.items() if v != "all" and k not in unrec]
say("row rules of the thirty: no reduction", len(noreduce), "| a reduction", len(reduce_), reduce_,
    "| transposed count", len(transposed), "| not reconstructed", sorted(unrec))
fam = {}
for ds in manifest:
    fam[ds["source"]["family"]] = fam.get(ds["source"]["family"], 0) + 1
say("sources of the thirty (manifest families):", fam)
wt = rows("MKW08-30/analysis/woike_tables_6_10_to_6_12.csv")
for m in ("LR", "CT"):
    v = {r["block"]: r["accuracy"] for r in wt if r["dataset"] == "Iris" and r["model"] == m}
    say(f"Woike's published Iris accuracy, {m}, by block:", v)
say("TabArena tasks with more than 10,000 cases (one repetition):",
    sum(int(r["n"]) > 10000 and r["cv_repeats"] == "1" for r in TAB.values()),
    "| every other task with ten repetitions:", all(r["cv_repeats"] == "10" for r in TAB.values() if int(r["n"]) <= 10000))
ties = [(k, r["n"], r["base_rate"]) for k, r in TAB.items() if float(r["base_rate"]) == 50.0] + \
       [(k, r["n"], r["base_rate"]) for k, r in MKW.items() if float(r["base_rate"]) == 50.0]
say("ties of the two classes:", ties)
ts = load("TabArena-Binary/analysis/tabarena_summary.json")
say("TabArena: flagged tasks", ts["descriptive"]["flagged_S_gt_0"], "| median G flagged, unflagged",
    ts["descriptive"]["median_G_flagged_unflagged"], "| median gain of the 13 two-verdict trees over the base rate",
    ts["descriptive"]["counts"]["median_tree_gain_over_base_both_verdicts"])
say("TabArena: H4 tests", ts["tests"]["H4a_S_G_given_base_rate"], ts["tests"]["H4b_S_G_given_strongest_reading"],
    "| H3", ts["tests"]["H3_Ak_vs_auc_margin_secondary"])
v = ts["descriptive"]
for side in ("H4b", "H4a"):
    d = [v[f"{side}_with_S2"], v[f"{side}_with_one_verdict_indicator"], v[f"{side}_without_leakage_candidates"]]
    say(f"TabArena descriptive variants of {side}: rho", [x["partial_rho"] for x in d], "p", [x["p_one_sided"] for x in d])
ins = load("Holte-16/analysis/indicator_summary.json")["spearman"]
best = max(ins.items(), key=lambda kv: abs(kv[1]["rho"]))
say("exploratory correlations on the sixteen:", len(ins), "| strongest:", best[0], best[1])

say("== Extended Data Table 1 (quantities derived from per-dataset files)")
W = held("MKW08-30-Woike") if held("MKW08-30-Woike") else None
for label, R, per in (("primary", held("MKW08-30"), MKW), ("Woike's files", W, MKWW)):
    if R is None:
        say(label, ": the rows of MKW08-30-Woike are not in heldout_conflict_share_results.csv")
        continue
    B = [r for r in R if r["both_verdicts"] == "True"]
    say(f"{label}: median in sample A {f1(st.median(float(per[k]['Ak_agree_spine']) for k in per))}, "
        f"c {f1(st.median(float(per[k]['ck_conflict_spine']) for k in per))}, "
        f"s {f1(st.median(float(per[k]['wk_win_spine']) for k in per if per[k]['wk_win_spine'] != ''))} | "
        f"out of sample A {f1(st.median(round(float(r['cv_A']), 1) for r in R))}, "
        f"c {f1(st.median(round(float(r['cv_c']), 1) for r in R))}, "
        f"s {f1(st.median(round(float(r['cv_s']), 1) for r in R if r['cv_s'] != ''))}")
    say(f"{label}: median cross-validated accuracy, tree {f1(st.median(float(per[k]['cv_acc_spine']) for k in per))}, "
        f"Bayesian classifier {f1(st.median(float(per[k]['cv_acc_full']) for k in per))}")
    say(f"{label}: the {len(B)} two-verdict trees: median disagreement {f1(st.median(round(100 - float(r['cv_A']), 1) for r in B))}, "
        f"q {f1(st.median(round(float(r['cv_q']), 1) for r in B))}, price {f1(st.median(round(float(r['cv_price']), 1) for r in B))}; "
        f"negative prices {[(r['code'], f1(float(r['cv_price']))) for r in B if float(r['cv_price']) < 0]}")
    one = [k for k in per if per[k]["spine_nondegenerate"] == "False"]
    two = [k for k in per if per[k]["spine_nondegenerate"] == "True"]
    best_gain = lambda k: max(float(per[k]["woike_LR"]), float(per[k]["woike_CART"])) - float(per[k]["base_rate"])
    say(f"{label}: one-class trees {len(one)}; published tree (Zig, 90%) below the base rate: "
        f"{sum(float(per[k]['woike_Zig']) < float(per[k]['base_rate']) for k in one)} of the one-class datasets, "
        f"{sum(float(per[k]['woike_Zig']) < float(per[k]['base_rate']) for k in two)} of the others")
    say(f"{label}: median gain of the better of LR and CART over the base rate, points: "
        f"{f1(st.median(best_gain(k) for k in one))} (one-class) against {f1(st.median(best_gain(k) for k in two))}")
    below = [k for k in one if float(per[k]["cv_acc_full"]) < float(per[k]["base_rate"])]
    say(f"{label}: Bayesian classifier below the base rate out of sample, among the one-class datasets: {len(below)} {below}")
    say(f"{label}: Spearman rho(Ak, margin) within the one-class datasets: "
        f"{spearman([float(per[k]['Ak_agree_spine']) for k in one], [float(per[k]['margin_H1']) for k in one]):+.2f}")
say("Extended Data Table 2: datasets with a difference", len(ED2), "| other datasets", len(others),
    "with identical in-sample quantities; largest difference in cross-validated accuracy there:", f1(cv_gap))

with open(os.path.join(HERE, "paper_numbers_log.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(LOG) + "\n")
