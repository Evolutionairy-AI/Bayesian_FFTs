"""POST HOC, DESCRIPTIVE. The large-prior case over all kept attributes: the log-odds of the prior outweigh the combined
opposing evidence of every kept attribute, so that the Bayesian classifier returns the more common class on every
profile (Section 3, "the prior outweighs all attributes combined"; Extended Data Table 1, "Datasets that meet the
large-prior case over all attributes"). Fitted on all cases, as the in-sample quantities are.

Written 2026-11-24; the count of 2026-09-21 was made without a saved script (RESULTS_ROBUSTNESS_WOIKE, appendix).

For Lambda_0 > 0 the condition is Lambda_0 + sum_i l_i^0 > 0, for Lambda_0 < 0 it is Lambda_0 + sum_i l_i^1 < 0.
Collections, labels and C1 as in heldout_conflict_share.py: Holte-16, MKW08-30, MKW08-30 on Woike's files (skipped
when MKW08-30/data-woike/ is absent; the files are not redistributed) and TabArena-29.

    python Posthoc-Development/large_prior_case.py   ->  Posthoc-Development/large_prior_case_log.txt
The analysis files are read from the repository's data/ folders, or from the folder named by BFFT_DATA_ROOT.
"""
import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.dirname(HERE)  # the repository root
sys.path.insert(0, os.path.join(DS, "Holte-16", "analysis"))
import depth_one_harness as v1  # noqa: E402
import indicator_cv_harness as v2  # noqa: E402

DATA_ROOT = os.environ.get("BFFT_DATA_ROOT", DS)
LOG = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LOG.append(line)


def large_prior(cols, y):
    m = v2.fit(cols, y, range(len(y)))
    l0, lps, lms = m["l0"], m["lps"], m["lms"]
    opposing = sum(lms) if l0 > 0 else sum(lps)
    flag = l0 + opposing > 0 if l0 > 0 else l0 + opposing < 0
    if flag and m["K"] <= 12:  # confirm on every profile that the Bayesian classifier returns one class
        verdicts = {l0 + sum(p if x else q for x, p, q in zip(xs, lps, lms)) > 0
                    for xs in itertools.product((0, 1), repeat=m["K"])}
        assert len(verdicts) == 1
    return flag, l0, opposing, m["K"]


def report(label, results):
    hits = [(code, round(l0, 2), round(opp, 2), K) for code, (flag, l0, opp, K) in results if flag]
    say(f"{label}: {len(hits)} of {len(results)} datasets meet the large-prior case over all kept attributes"
        + (" (code, prior log-odds, combined opposing evidence, kept attributes): " + str(hits) if hits else ""))
    return len(hits)


def main():
    v1.DATA = os.path.join(DATA_ROOT, "Holte-16", "data")
    res = []
    for code in v2.CODES:
        _, cols, cls = v2.prepare(code)
        maj = Counter(cls).most_common(1)[0][0]
        res.append((code, large_prior(cols, [1 if c == maj else 0 for c in cls])))
    n_holte = report("Holte-16", res)

    pkg = os.path.join(DS, "MKW08-30")
    manifest = json.load(open(os.path.join(pkg, "manifest.json"), encoding="utf-8"))["datasets"]
    n_mkw = None
    for label, folder in (("MKW08-30", "data"), ("MKW08-30-Woike", "data-woike")):
        v1.DATA = os.path.join(DATA_ROOT, "MKW08-30", folder)
        if label == "MKW08-30-Woike" and not os.path.isdir(v1.DATA):
            say("Woike's files not found - MKW08-30-Woike skipped")
            continue
        res = []
        for ds in manifest:
            _, cols, cls = v2.prepare(ds["code"])
            counts = Counter(cls)
            c1 = "1" if counts["1"] >= counts["0"] else "0"
            res.append((ds["code"], large_prior(cols, [1 if c == c1 else 0 for c in cls])))
        n = report(label, res)
        n_mkw = n if label == "MKW08-30" else n_mkw

    v1.DATA = os.path.join(DATA_ROOT, "TabArena-Binary", "data")
    dtypes = json.load(open(os.path.join(v1.DATA, "declared_types.json"), encoding="utf-8"))
    res = []
    for name in list(dtypes):
        _, cols, cls = v2.prepare(name)
        cnt = Counter(cls)
        (c1, n1), (c0, n0) = sorted(cnt.items(), key=lambda t: -t[1])
        if n1 == n0 and "1" in cnt:
            c1 = "1"
        y = [1 if c == c1 else 0 for c in cls]
        if v2.fit(cols, y, range(len(y)))["K"] == 0:
            continue
        res.append((name, large_prior(cols, y)))
    n_tab = report("TabArena-29", res)
    say(f"the first two collections together: {n_holte + n_mkw}; all three: {n_holte + n_mkw + n_tab}")
    with open(os.path.join(HERE, "large_prior_case_log.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
