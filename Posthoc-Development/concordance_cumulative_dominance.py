"""Concordance and cumulative dominance, side by side, on SPENT data only (Holte-16 and the public
reconstruction of the thirty; Woike's files untouched). Exploratory; written 2026-09-25 for
Konstantinos's question on how the two relate. In sample (full-data fit), like c and s in Section 3.

Per case x, with the certified tree's verdict tau(x) = +1 (C1) or -1 (C0) and the unseen attributes U
(those beyond the certified depth d), each unseen reading l_i(x_i) is signed toward the verdict,
s_i = tau * l_i(x_i), and votes v_i = sign(s_i) (never zero: l+ > 0 > l-). Nested conditions:
  DOM   every unseen reading supports the verdict (signs only)            -> agreement for ANY weights
  CD    ranked by |s_i| (ties: opposing first), the supporting readings are never outnumbered
        at any rank (order only)                                          -> agreement for any weights
                                                                             with that ranking
  CONC  sum of s_i >= 0: the unseen evidence does not oppose (amounts)    -> agreement for these weights
  AGREE T(x) = B(x)
DOM => CD => CONC => AGREE is asserted on every case. CD_FIXED is CD in the tree's fixed order (weaker
reading) instead of the case's own ranking; it need not imply CONC, and the failures are counted.
Writes concordance_cumulative_dominance_results.csv and _log.txt next to this file.
"""
import csv, json, os, statistics, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1
import indicator_cv_harness as v2


def prefix_ok(votes):
    tot = 0
    for v in votes:
        tot += v
        if tot < 0:
            return False
    return True


def run(collection, code, cols, y):
    m = v2.fit(cols, y, range(len(y)))
    _, ins = v2.in_sample(cols, y)                       # the harness's own c and s, for the check
    K, d = m["K"], m["kmax"]
    cnt = Counter()
    verdicts = set()
    for r in range(len(y)):
        x = v2.cue_row(m, cols, r)
        _, sp, full, _, unseen = v2.verdicts(m, x)
        verdicts.add(sp)
        tau = 1 if sp == 1 else -1
        s = [tau * (m["lps"][i] if x[i] else m["lms"][i]) for i in range(d, K)]
        dom = all(t > 0 for t in s)
        ranked = sorted(s, key=lambda t: (-abs(t), t > 0))    # by strength; opposing first on ties
        cd = prefix_ok([1 if t > 0 else -1 for t in ranked])
        cd_fixed = prefix_ok([1 if t > 0 else -1 for t in s])
        conc = not ((unseen > 0 and sp == 0) or (unseen < 0 and sp == 1))
        agree = sp == full
        assert (not dom or cd) and (not cd or conc) and (not conc or agree), (code, r)
        assert conc == (sum(s) >= 0) or abs(sum(s)) < 1e-9, (code, r)     # s is already signed by tau
        cnt.update(n=1, dom=dom, cd=cd, cd_fixed=cd_fixed, conc=conc, agree=agree,
                   cd_fixed_not_conc=cd_fixed and not conc, won=agree and not conc)
    n = cnt["n"]
    pct = lambda k: round(100 * cnt[k] / n, 1)
    c = round(100 * (n - cnt["conc"]) / n, 1)
    assert c == ins["ck_conflict_spine"], (code, c, ins["ck_conflict_spine"])
    assert pct("agree") == ins["Ak_agree_spine"], (code, pct("agree"), ins["Ak_agree_spine"])
    return dict(collection=collection, code=code, n=n, K=K, d=d, unseen=K - d,
                both_verdicts=len(verdicts) > 1, dom=pct("dom"), cd=pct("cd"), cd_fixed=pct("cd_fixed"),
                conc=pct("conc"), agree=pct("agree"), c=c, s=ins["wk_win_spine"],
                cd_fixed_not_conc=pct("cd_fixed_not_conc"), won=pct("won"))


rows = []
for code in v2.CODES:
    _, cols, cls = v2.prepare(code)
    maj = Counter(cls).most_common(1)[0][0]
    rows.append(run("Holte-16", code, cols, [1 if c == maj else 0 for c in cls]))
pkg = os.path.join(DS, "MKW08-30")
v1.DATA = os.path.join(pkg, "data")
for ds in json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]:
    _, cols, cls = v2.prepare(ds["code"])
    cnt = Counter(cls); c1 = "1" if cnt["1"] >= cnt["0"] else "0"
    rows.append(run("MKW08-30", ds["code"], cols, [1 if c == c1 else 0 for c in cls]))

with open(os.path.join(HERE, "concordance_cumulative_dominance_results.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

out = []
p = out.append
p("Concordance and cumulative dominance on spent data (in sample). Percent of cases.")
p(f"{'coll':9}{'code':6}{'n':>6}{'U':>4} both {'DOM':>6}{'CD':>6}{'CDfix':>6}{'CONC':>6}{'AGREE':>6}{'won':>6}{'fixNC':>6}")
for r in rows:
    p(f"{r['collection']:9}{r['code']:6}{r['n']:>6}{r['unseen']:>4} {str(r['both_verdicts'])[0]:>4} {r['dom']:>6}{r['cd']:>6}"
      f"{r['cd_fixed']:>6}{r['conc']:>6}{r['agree']:>6}{r['won']:>6}{r['cd_fixed_not_conc']:>6}")
med = lambda xs: round(statistics.median(xs), 1)
for label, sel in [("Holte-16, all 16", lambda r: r["collection"] == "Holte-16"),
                   ("MKW08-30, all 30", lambda r: r["collection"] == "MKW08-30"),
                   ("Holte-16, both verdicts", lambda r: r["collection"] == "Holte-16" and r["both_verdicts"]),
                   ("MKW08-30, both verdicts", lambda r: r["collection"] == "MKW08-30" and r["both_verdicts"]),
                   ("MKW08-30, majority verdict only", lambda r: r["collection"] == "MKW08-30" and not r["both_verdicts"])]:
    rs = [r for r in rows if sel(r)]
    p(f"\n{label} (n = {len(rs)}): medians DOM {med([r['dom'] for r in rs])}, CD {med([r['cd'] for r in rs])}, "
      f"CD_fixed {med([r['cd_fixed'] for r in rs])}, CONC {med([r['conc'] for r in rs])}, AGREE {med([r['agree'] for r in rs])}, "
      f"won conflicts {med([r['won'] for r in rs])}; c {med([r['c'] for r in rs])}, "
      f"s {med([r['s'] for r in rs if r['s'] != ''])}")
    p(f"   median shares of agreement: DOM {med([100 * r['dom'] / r['agree'] for r in rs])}, "
      f"CD beyond DOM {med([100 * (r['cd'] - r['dom']) / r['agree'] for r in rs])}, "
      f"CONC beyond CD {med([100 * (r['conc'] - r['cd']) / r['agree'] for r in rs])}, "
      f"won conflicts {med([100 * r['won'] / r['agree'] for r in rs])}")
p(f"\nCD in the fixed order failed to imply concordance on some cases in {sum(r['cd_fixed_not_conc'] > 0 for r in rows)} "
  f"of {len(rows)} datasets (max {max(r['cd_fixed_not_conc'] for r in rows)}% of cases).")
p("Checks passed: DOM => CD => CONC => AGREE on every case; conflict rate and agreement equal the harness's ck and Ak.")
text = "\n".join(out)
print(text)
open(os.path.join(HERE, "concordance_cumulative_dominance_log.txt"), "w", encoding="utf-8").write(text + "\n")
