"""Check a written definition of the certified tree against the harness, on spent data only
(Holte-16 and the public reconstruction of the thirty; Woike's files untouched). Writes nothing
into DATA_SETS. Full-data fits, as for the in-sample quantities and the figure's 'questions'."""
import itertools, json, math, os, sys
from collections import Counter
DS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the repository root
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1
import indicator_cv_harness as v2

def definition_depth(kept):
    """Written definition: order by weaker reading, largest first (ties: column order);
    d = largest k such that the first k attributes satisfy (1) among themselves."""
    order = sorted(kept, key=lambda t: -min(t[1], -t[2]))       # stable sort = column order on ties
    lo = [min(lp, -lm) for _, lp, lm, *_ in order]
    hi = [max(lp, -lm) for _, lp, lm, *_ in order]
    if not order:
        return 0, order
    d = max(k for k in range(1, len(order) + 1)
            if all(lo[i] > sum(hi[i + 1:k]) for i in range(k - 1)))
    return d, order

rows = []
def run(collection, code, cols, y):
    m = v2.fit(cols, y, range(len(y)))
    d, order = definition_depth(m["kept"])
    assert d == m["kmax"], (code, d, m["kmax"])
    assert [t[3] for t in order] == [t[3] for t in m["kept"]], (code, "order differs")
    spine = m["spine"]
    levels = len(spine) if spine else 0
    # T = B_d on every one of the 2^d profiles, not only on observed cases
    bad = 0
    for x in itertools.product((0, 1), repeat=d):
        s = m["l0"] + sum(m["lps"][i] if x[i] else m["lms"][i] for i in range(d))
        bad += v1.spine_classify(spine, list(x)) != (1 if s > 0 else 0)
    outs = {v1.spine_classify(spine, list(x)) for x in itertools.product((0, 1), repeat=d)} if d else {1 if m["l0"] > 0 else 0}
    stuck = any(l[0] == "stuck" for l in spine) if spine else False
    rows.append(dict(collection=collection, code=code, n=len(y), K=m["K"], d=d, levels_used=levels,
                     l0=round(m["l0"], 3), both_verdicts=len(outs) > 1, profile_mismatches=bad, stuck=stuck,
                     structure=" ".join(l[0] if l[0] != "term" else f"term({l[1]},{l[2]})" for l in spine) if spine else "const"))

for code in v2.CODES:
    _, cols, cls = v2.prepare(code)
    maj = Counter(cls).most_common(1)[0][0]
    run("Holte-16", code, cols, [1 if c == maj else 0 for c in cls])
pkg = os.path.join(DS, "MKW08-30")
v1.DATA = os.path.join(pkg, "data")
for ds in json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]:
    _, cols, cls = v2.prepare(ds["code"])
    cnt = Counter(cls); c1 = "1" if cnt["1"] >= cnt["0"] else "0"
    run("MKW08-30", ds["code"], cols, [1 if c == c1 else 0 for c in cls])

print(f"{'coll':9}{'code':6}{'n':>6}{'K':>4}{'d':>3}{'lev':>4}{'l0':>7}  both  structure")
for r in rows:
    print(f"{r['collection']:9}{r['code']:6}{r['n']:>6}{r['K']:>4}{r['d']:>3}{r['levels_used']:>4}{r['l0']:>7}  {str(r['both_verdicts']):5} {r['structure']}")
print("datasets", len(rows), "| definition depth == harness kmax: all | profile mismatches:", sum(r["profile_mismatches"] for r in rows),
      "| stuck levels:", sum(r["stuck"] for r in rows), "| K=0:", sum(r["K"] == 0 for r in rows))
print("trees stopping before depth d (levels_used < d):", [r["code"] for r in rows if r["levels_used"] < r["d"]])
print("both verdicts:", Counter((r["collection"], r["both_verdicts"]) for r in rows))
print("depth distribution:", Counter((r["collection"], r["d"]) for r in rows))
