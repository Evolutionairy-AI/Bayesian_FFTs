"""Brute-force check of the necessary and sufficient condition in Methods ("A necessary and sufficient condition") and
Remark (iii) of the main text, and of the two numerical examples of that Methods paragraph.

Written 2026-11-24 from the specification of the check of 13 November 2026, whose script was lost.

Part A. With w_i = l_i^1 + |l_i^0|, the Bayesian classifier assigns x to C1 exactly when sum_k w_k x_k > t, and every
threshold t is attained by some prior. For every integer weight vector with entries 1..12 (three attributes) and
1..10 (four attributes), sorted into decreasing order, and for every threshold that gives a distinct classifier
(t = m + 1/2, m = -1, ..., sum w), the script checks whether the classifier is a fast-and-frugal tree that queries
the attributes in decreasing weight: at every level, at least one answer settles the class of every object that
reaches it. The claim: this holds for every threshold if and only if w_i >= sum_{j>i} w_j for all i.
Also counted: the vectors where the condition holds with equality somewhere (where the strict form would be wrong),
and the same check with the attributes in ANY order (Methods: when the condition fails, no fast-and-frugal tree
reproduces the classifier, whatever its order of attributes).

Part B. The examples of the Methods paragraph: (1) an attribute with l^1 = 0.1, l^0 = -10 followed by one with
l^1 = 1, l^0 = -1 violates Condition (1) and satisfies the weaker inequality; (2) at a base rate of 20% for C1,
attributes that multiply or divide the odds by 5, 3 and 2 violate both conditions, and the tree of Result 1 still
coincides with the Bayesian classifier, assigning C1 exactly when the first two attributes are present.

Standard library only. python theory/verify_iff_bruteforce.py  ->  theory/verify_iff_bruteforce_log.txt
"""
import itertools
import math
import os
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LOG.append(line)


def is_fft(w, t, order):
    """True if x -> [sum w x > t] is a fast-and-frugal tree querying the attributes in `order`."""
    k = len(w)
    fixed = {}                                    # answers on the continuing branch so far
    for level, a in enumerate(order):
        rest = [b for b in order[level + 1:]]
        base = sum(w[b] * v for b, v in fixed.items())
        settles = {}
        for v in (0, 1):
            s = base + w[a] * v
            lo, hi = s, s + sum(w[b] for b in rest)  # the range of the sum over all completions
            settles[v] = (lo > t) or (hi < t)         # every completion has the same class
        if settles[0] and settles[1]:
            return True                           # both answers exit: the tree ends here
        if not settles[0] and not settles[1]:
            return False                          # no exit at this level
        fixed[a] = 0 if settles[1] else 1         # continue on the answer that does not settle
    return True


def condition(w):
    return all(w[i] >= sum(w[i + 1:]) for i in range(len(w) - 1))


def part_a(k, top):
    vectors = agree = holds = equality = fft_all = mismatches = 0
    any_order_mismatches = 0
    for raw in itertools.product(range(1, top + 1), repeat=k):
        w = sorted(raw, reverse=True)
        vectors += 1
        thresholds = [m + 0.5 for m in range(-1, sum(w) + 1)]
        dec = tuple(range(k))
        fft_every_t = all(is_fft(w, t, dec) for t in thresholds)
        cond = condition(w)
        holds += cond
        equality += cond and any(w[i] == sum(w[i + 1:]) for i in range(k - 1))
        fft_all += fft_every_t
        if fft_every_t == cond:
            agree += 1
        else:
            mismatches += 1
            say("  MISMATCH", w, "condition", cond, "FFT for every threshold", fft_every_t)
        any_order = all(any(is_fft(w, t, o) for o in itertools.permutations(range(k))) for t in thresholds)
        if any_order != cond:
            any_order_mismatches += 1
            say("  ANY-ORDER MISMATCH", w, "condition", cond, "FFT in some order for every threshold", any_order)
    say(f"k = {k}, entries 1..{top}: {vectors} weight vectors; condition holds for {holds} "
        f"(with equality somewhere for {equality}); FFT in decreasing order for every threshold: {fft_all}; "
        f"agreement {agree}, mismatches {mismatches}; any-order check mismatches {any_order_mismatches}")
    return mismatches + any_order_mismatches


def result1_tree(prior_odds, r):
    """The tree of Result 1 for symmetric attributes (factor r_i multiplies the odds when present, divides when
    absent), in exact arithmetic on odds; returns a function x -> class and the levels used."""
    n = len(r)

    def classify(x):
        s = prior_odds
        for i in range(n):
            m1 = math.prod(r[i + 1:], start=Fraction(1))
            i1 = s * r[i] / m1 > 1                # (I1): exit to C1 on x_i = 1
            i0 = s / r[i] * m1 < 1                # (I0): exit to C0 on x_i = 0
            if i == n - 1:
                return 1 if (s * r[i] if x[i] else s / r[i]) > 1 else 0
            if i1 and i0:
                return 1 if x[i] else 0
            if i1 and x[i]:
                return 1
            if i0 and not x[i]:
                return 0
            if not i1 and not i0:
                raise AssertionError("no exit")
            s = s * r[i] if x[i] else s / r[i]
        raise AssertionError("unreachable")
    return classify


def part_b():
    # (1) l^1 = 0.1, l^0 = -10, then l^1 = 1, l^0 = -1
    a, b = (0.1, -10.0), (1.0, -1.0)
    cond1 = min(a[0], -a[1]) > max(b[0], -b[1])
    w = [a[0] - a[1], b[0] - b[1]]
    weaker = w[0] >= w[1]
    sums = sorted({w[0] * x0 + w[1] * x1 for x0 in (0, 1) for x1 in (0, 1)})
    cuts = [sums[0] - 1] + [(u + v) / 2 for u, v in zip(sums, sums[1:])] + [sums[-1] + 1]
    every_prior = all(is_fft(w, t, (0, 1)) for t in cuts)
    say(f"example 1: Condition (1) holds: {cond1}; weaker inequality w1 = {w[0]:.1f} >= w2 = {w[1]:.1f}: {weaker}; "
        f"the Bayesian classifier is a fast-and-frugal tree for every prior: {every_prior}")
    ok1 = (not cond1) and weaker and every_prior

    # (2) base rate 20% for C1 (prior odds 1/4), factors 5, 3, 2
    prior, r = Fraction(1, 4), [Fraction(5), Fraction(3), Fraction(2)]
    cond1 = r[0] > r[1] * r[2] and r[1] > r[2]              # l_1 > l_2 + l_3 and l_2 > l_3 (log scale)
    weaker = r[0] ** 2 >= (r[1] * r[2]) ** 2 and r[1] >= r[2]  # w_i = 2 ln r_i
    tree = result1_tree(prior, r)
    objs = list(itertools.product((0, 1), repeat=3))
    bayes = {x: int(prior * math.prod((ri if xi else 1 / ri) for ri, xi in zip(r, x)) > 1) for x in objs}
    same = all(tree(x) == bayes[x] for x in objs)
    first_two = all(bayes[x] == int(x[0] == 1 and x[1] == 1) for x in objs)
    say(f"example 2: base rate {prior / (1 + prior)} for C1, factors 5, 3, 2: Condition (1) holds: {cond1}; "
        f"weaker inequality holds: {weaker}; tree of Result 1 equals the Bayesian classifier on all 8 objects: {same}; "
        f"C1 exactly when the first two attributes are present: {first_two}")
    ok2 = (not cond1) and (not weaker) and same and first_two
    return ok1 and ok2


if __name__ == "__main__":
    start = time.time()
    say("Part A: the Bayesian (linear threshold) classifier is a fast-and-frugal tree for every threshold "
        "if and only if w_i >= sum_{j>i} w_j")
    bad = part_a(3, 12) + part_a(4, 10)
    say("Part B: the examples of the Methods paragraph")
    ok = part_b()
    say(f"Part A mismatches: {bad}; Part B as stated: {ok}")
    assert bad == 0 and ok
    with open(os.path.join(HERE, "verify_iff_bruteforce_log.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")
    print(f"({time.time() - start:.0f} s)")
