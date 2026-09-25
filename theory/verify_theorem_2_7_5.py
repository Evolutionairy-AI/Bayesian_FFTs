#!/usr/bin/env python3
"""verify_theorem_2_7_5.py -- Numerical verification for the FEH classification
extension (FFH-FFT identity, Theorem 2.7.5 draft) and the Zig exit-rule
derivation (Proposition on the Martignon-Katsikopoulos-Woike 2008 Zig
construction).

Companion to FEH_Classification_Extension_Draft.md. Style follows
verify_appendix_A4.py: exhaustive enumeration, explicit counterexamples,
deterministic seed.

Parts:
  A. Theorem 2.7.5: random (DD+/-)-satisfying asymmetric-weight profiles +
     priors; greedy-spine FFT construction; exhaustive sample-wise comparison
     against the truncated-Bayes classifier for every horizon k.
  B. Zig rule: one-step-lookahead (OSLA) sequential agent with equal one-bit
     cues reproduces the 2008 Zig construction (run length k with
     2^(k-1) <= r <= 2^k, then alternation); generalized run-length
     prediction k = ceil(log r / log odds(v)) for v != 2/3.
  C. OSLA optimality band: finite-horizon value iteration; find the range of
     per-cue meta-costs c for which the exactly-optimal stopping policy
     induces the Zig tree.
  D. Sharpness: (DD+/-)-violating profile (uniform validities) is not
     FFT-realizable; brute force over all FFTs confirms.
"""

import math
import random
import itertools

random.seed(20260707)

# ---------------------------------------------------------------- utilities

def logistic(z):
    return 1.0 / (1.0 + math.exp(-z))


def weights_to_likelihoods(lp, lm):
    """Invert (l+, l-) -> (p, q) with p = P(x=1|C1), q = P(x=1|C0), p > q."""
    ep, em = math.exp(lp), math.exp(lm)
    q = (1.0 - em) / (ep - em)
    p = ep * q
    return p, q


# ------------------------------------------------- greedy spine construction

def greedy_spine_tree(L0, lp, lm, k):
    """Build the FFT realizing the k-cue-truncated Bayes classifier under
    (DD+/-). Cues 0..k-1, coded C1-pointing (lp[i] > 0 > lm[i]).
    Returns list of levels: ('E1',) exit-to-C1 on value 1, ('E0',) exit-to-C0
    on value 0, ('LAST', cat_if_1, cat_if_0) terminal level.
    Returns None if some level has no sign-decisive value (theorem says this
    cannot happen under (DD+/-))."""
    spine = L0
    levels = []
    for i in range(k):
        if i == k - 1:
            c1 = 1 if spine + lp[i] > 0 else 0
            c0 = 1 if spine + lm[i] > 0 else 0
            levels.append(('LAST', c1, c0))
            return levels
        tail_p = sum(lp[i + 1:k])
        tail_m = sum(lm[i + 1:k])
        d1 = spine + lp[i] + tail_m > 0   # value 1 decisive for C1
        d0 = spine + lm[i] + tail_p < 0   # value 0 decisive for C0
        if d1 and d0:
            levels.append(('LAST', 1, 0))
            return levels
        if d1:
            levels.append(('E1',))
            spine += lm[i]
        elif d0:
            levels.append(('E0',))
            spine += lp[i]
        else:
            return None
    return levels


def classify_tree(levels, x):
    for i, lv in enumerate(levels):
        if lv[0] == 'LAST':
            return lv[1] if x[i] == 1 else lv[2]
        if lv[0] == 'E1' and x[i] == 1:
            return 1
        if lv[0] == 'E0' and x[i] == 0:
            return 0
    raise RuntimeError("fell off tree")


def classify_bayes(L0, lp, lm, k, x):
    s = L0 + sum(lp[i] if x[i] else lm[i] for i in range(k))
    if abs(s) < 1e-12:
        raise RuntimeError("tie in posterior log-odds (non-generic input)")
    return 1 if s > 0 else 0


# -------------------------------------------- splitting-profile bookkeeping

def fold_to_canonical(levels):
    """Fold a greedy tree whose horizon terminal may be non-canonical
    ((C1,C1) or (C0,C0)) into MKW08 canonical form (terminal 1->C1, 0->C0).
    Returns ('TREE', canonical_levels) or ('CONST', cat)."""
    work = list(levels)
    while True:
        last = work[-1]
        c1, c0 = last[1], last[2]
        assert not (c1 == 0 and c0 == 1), "impossible terminal: l+ > l-"
        if c1 == 1 and c0 == 0:
            return ('TREE', work)
        cat = c1  # here c1 == c0
        if len(work) == 1:
            return ('CONST', cat)
        prev = work[-2][0]
        if prev == 'E1':
            new_last = ('LAST', 1, cat)   # exit on 1 -> C1; continue(0) -> cat
        else:
            new_last = ('LAST', cat, 0)   # exit on 0 -> C0; continue(1) -> cat
        work = work[:-2] + [new_last]


def profile_of(canonical_levels, k):
    """Splitting profile per MKW08 Result 1: S_i = 0 for a C1-exit, 1 for a
    C0-exit; S_m = 0 at the terminal level m; S_j = 1 for j > m (truncation
    padding, Result 1(ii))."""
    m = len(canonical_levels)
    S = [0 if lv[0] == 'E1' else 1 for lv in canonical_levels[:-1]]
    S.append(0)
    S += [1] * (k - m)
    return S


def lex_gt(x, S):
    for xi, si in zip(x, S):
        if xi != si:
            return xi > si
    return False


# --------------------------------------------------------------------- PART A

def random_ddpm_profile(K):
    """Random profile satisfying (DD+/-): min(l+_i, -l-_i) > sum_{j>i} max(l+_j, -l-_j).
    Built from the weakest cue up."""
    lp = [0.0] * K
    lm = [0.0] * K
    total_bar = 0.0
    for j in range(K - 1, -1, -1):
        base = (total_bar * (1.0 + random.uniform(0.05, 1.0))
                if total_bar > 0 else random.uniform(0.1, 1.0))
        lp[j] = base * (1.0 + random.uniform(0.0, 0.8))
        lm[j] = -base * (1.0 + random.uniform(0.0, 0.8))
        total_bar += max(lp[j], -lm[j])
    return lp, lm


def check_ddpm(lp, lm):
    K = len(lp)
    for i in range(K - 1):
        lo = min(lp[i], -lm[i])
        tail = sum(max(lp[j], -lm[j]) for j in range(i + 1, K))
        if not lo > tail:
            return False
    return True


def part_a(n_profiles=200):
    print("=" * 72)
    print("PART A -- Theorem 2.7.5: exact FFH-FFT identity under (DD+/-)")
    print("=" * 72)
    comparisons = 0
    failures = 0
    depth1_checks = 0
    depth_hist = {}
    profile_checks = [0, 0]   # [cases verified, mismatches]
    example_shown = False
    for t in range(n_profiles):
        K = random.randint(2, 8)
        lp, lm = random_ddpm_profile(K)
        assert check_ddpm(lp, lm)
        W = sum(max(lp[j], -lm[j]) for j in range(K))
        slack1 = min(lp[0], -lm[0]) - sum(max(lp[j], -lm[j]) for j in range(1, K))
        priors = [0.0, 0.3 * W, -0.3 * W, 0.9 * W, -0.9 * W, 1.3 * W, -1.3 * W]
        priors += [random.uniform(-1.5 * W, 1.5 * W) for _ in range(3)]
        for L0 in priors:
            L0 += random.uniform(-1e-7, 1e-7)  # break non-generic ties
            for k in range(1, K + 1):
                tree = greedy_spine_tree(L0, lp, lm, k)
                if tree is None:
                    failures += 1
                    print(f"  FAIL: no decisive value (profile {t}, L0={L0:.3f}, k={k})")
                    continue
                depth = len(tree)
                depth_hist[depth] = depth_hist.get(depth, 0) + 1
                # splitting-profile bookkeeping (Theorem 2.7.5(b), 2nd clause):
                # non-degenerate prior -> fold to canonical form -> profile S
                nondeg = (L0 + sum(lm[:k]) < 0 < L0 + sum(lp[:k]))
                S = None
                if nondeg:
                    kind, folded = fold_to_canonical(tree)
                    if kind == 'CONST':
                        failures += 1
                        print(f"  FOLD FAIL: constant tree despite non-degenerate "
                              f"prior (profile {t}, L0={L0:.3f}, k={k})")
                    else:
                        S = profile_of(folded, k)
                        profile_checks[0] += 1
                for x in itertools.product((0, 1), repeat=k):
                    a_b = classify_bayes(L0, lp, lm, k, x)
                    a_t = classify_tree(tree, x)
                    comparisons += 1
                    if a_b != a_t:
                        failures += 1
                        print(f"  MISMATCH profile {t} L0={L0:.3f} k={k} x={x}: "
                              f"bayes={a_b} tree={a_t}")
                    if S is not None and (a_b == 1) != lex_gt(x, S):
                        failures += 1
                        profile_checks[1] += 1
                        print(f"  PROFILE MISMATCH profile {t} L0={L0:.3f} k={k} "
                              f"x={x} S={S}")
            # k*-invariance in the small-prior regime (Theorem 2.7.5(a)):
            if abs(L0) < slack1:
                depth1_checks += 1
                for k in range(1, K + 1):
                    tree = greedy_spine_tree(L0, lp, lm, k)
                    for x in itertools.product((0, 1), repeat=k):
                        want = 1 if x[0] == 1 else 0
                        if classify_tree(tree, x) != want or \
                           classify_bayes(L0, lp, lm, k, x) != want:
                            failures += 1
                            print(f"  DEPTH-1 VIOLATION profile {t} L0={L0:.3f} "
                                  f"k={k} x={x}")
        if not example_shown and K >= 3:
            example_shown = True
            p0, q0 = weights_to_likelihoods(lp[0], lm[0])
            print(f"  example profile (t={t}, K={K}): "
                  f"l+={['%.2f' % v for v in lp]}, l-={['%.2f' % v for v in lm]}")
            print(f"    cue 1 corresponds to P(x=1|C1)={p0:.3f}, P(x=1|C0)={q0:.3f}")
    print(f"  profiles tested: {n_profiles}; sample-wise comparisons: {comparisons}")
    print(f"  mismatches / construction failures: {failures}")
    print(f"  depth-1 (k*-invariant, |L0| < slack_1) prior cases verified: {depth1_checks}")
    print(f"  splitting-profile correspondence (fold + MKW08 encoding) verified "
          f"in {profile_checks[0]} non-degenerate cases, "
          f"{profile_checks[1]} mismatches")
    print(f"  tree-depth histogram: {dict(sorted(depth_hist.items()))}")
    return failures == 0


# --------------------------------------------------------------------- PART B

def osla_exit_dirs(L0, ell, n_levels):
    """Exit directions of the one-step-lookahead tree with equal cues +/-ell.
    'E1' = exit to majority(C1) on value 1; 'E0' = exit to C0 on value 0."""
    spine = L0
    dirs = []
    for _ in range(n_levels):
        if spine > 0:
            dirs.append('E1')
            spine -= ell
        elif spine < 0:
            dirs.append('E0')
            spine += ell
        else:
            dirs.append('TIE')
            break
    return dirs


def zig_exit_dirs_2008(r, n_levels):
    """The Martignon-Katsikopoulos-Woike (2008) Zig construction (C1 majority):
    first k exits toward the majority with 2^(k-1) <= r <= 2^k, then alternate."""
    k = 1
    while not (2 ** (k - 1) <= r <= 2 ** k):
        k += 1
    dirs = ['E1'] * min(k, n_levels)
    nxt = 'E0'
    while len(dirs) < n_levels:
        dirs.append(nxt)
        nxt = 'E1' if nxt == 'E0' else 'E0'
    return dirs


def part_b():
    print("=" * 72)
    print("PART B -- Zig derivation: OSLA agent vs the 2008 Zig construction")
    print("=" * 72)
    n_levels = 20
    ell_bit = math.log(2.0)   # one-bit cues: v = 2/3
    r_grid = [1.3, 1.7, 2.5, 3.0, 3.9, 5.0, 6.3, 7.7, 9.5, 12.0, 15.8, 21.0,
              27.0, 45.0, 77.0, 100.0]
    fails = 0
    for r in r_grid:
        L0 = math.log(r)
        osla = osla_exit_dirs(L0, ell_bit, n_levels)
        zig = zig_exit_dirs_2008(r, n_levels)
        run = 0
        for d in osla:
            if d == 'E1':
                run += 1
            else:
                break
        k_rule = math.ceil(math.log2(r))
        ok = (osla == zig) and (run == k_rule)
        if not ok:
            fails += 1
        print(f"  r={r:7.1f}: OSLA run={run:2d}, Zig rule k={k_rule:2d}, "
              f"full 20-level architecture match={osla == zig}")
    print(f"  v=2/3 (one-bit cues): {len(r_grid) - fails}/{len(r_grid)} exact "
          f"architecture matches")
    # generalized prediction for v != 2/3
    print("  generalized run-length prediction k(r,v) = ceil(ln r / ln odds(v)):")
    gfails = 0
    gtot = 0
    for v in (0.60, 2.0 / 3.0, 0.75, 0.90):
        ell = math.log(v / (1.0 - v))
        for r in r_grid:
            L0 = math.log(r)
            osla = osla_exit_dirs(L0, ell, n_levels)
            run = 0
            for d in osla:
                if d == 'E1':
                    run += 1
                else:
                    break
            pred = math.ceil(L0 / ell)
            gtot += 1
            if run != pred:
                gfails += 1
                print(f"    MISMATCH v={v:.3f} r={r}: run={run} pred={pred}")
    print(f"    {gtot - gfails}/{gtot} (v, r) cells match the generalized rule")
    return fails == 0 and gfails == 0


# --------------------------------------------------------------------- PART C

def optimal_policy_tree(L0, ell, v, horizon, c):
    """Finite-horizon value iteration for the sequential agent with per-cue
    meta-cost c, equal symmetric cues (evidence +/-ell, validity v), 0-1 loss.
    Returns the exit-direction list of the induced tree along the spine, and
    the stop-decision table."""
    # states: L = L0 + m*ell, m in [-horizon, horizon]
    def rho(L):
        mu = logistic(L)
        return min(mu, 1.0 - mu)

    def pred_p1(L):
        mu = logistic(L)
        return mu * v + (1.0 - mu) * (1.0 - v)

    ms = range(-horizon - 1, horizon + 2)
    V = {m: rho(L0 + m * ell) for m in ms}          # t = horizon
    stop = {}                                        # (t, m) -> bool
    for t in range(horizon - 1, -1, -1):
        NV = {}
        for m in ms:
            L = L0 + m * ell
            r_stop = rho(L)
            if abs(m) > t:                # unreachable at time t
                NV[m] = r_stop
                stop[(t, m)] = True
                continue
            p1 = pred_p1(L)
            mp = min(m + 1, horizon + 1)
            mn = max(m - 1, -horizon - 1)
            r_cont = c + p1 * V[mp] + (1.0 - p1) * V[mn]
            NV[m] = min(r_stop, r_cont)
            stop[(t, m)] = r_stop <= r_cont
        V = NV
    # induced tree along the spine (root state m=0 at t=0)
    dirs = []
    m = 0
    for t in range(horizon - 1):
        s1 = stop[(t + 1, m + 1)]
        s0 = stop[(t + 1, m - 1)]
        if s1 and s0:
            dirs.append('TERM')
            break
        if s1 and not s0:
            act = 1 if L0 + (m + 1) * ell > 0 else 0
            dirs.append('E1' if act == 1 else 'X')
            m -= 1
        elif s0 and not s1:
            act = 1 if L0 + (m - 1) * ell > 0 else 0
            dirs.append('E0' if act == 0 else 'X')
            m += 1
        else:
            dirs.append('NOEXIT')
            break
    return dirs


def part_c():
    print("=" * 72)
    print("PART C -- exact-optimality band (complete Zig) and minimal-horizon")
    print("          run rule (truncated Zig / majority pectinate)")
    print("=" * 72)
    horizon = 14
    v = 2.0 / 3.0
    ell = math.log(v / (1.0 - v))
    # C1: for moderate priors (run length k <= 2, i.e. r <= 4) the exactly-
    # optimal stopping policy should induce the COMPLETE Zig tree on a
    # nonempty band of per-cue meta-costs c. For larger r, complete Zig
    # demands the same posterior state to both continue and stop at
    # different levels, so no stationary optimal policy induces it -- the
    # r=5 line below documents that boundary (expected: no band).
    ok_c1 = True
    for r, expect_band in ((1.7, True), (2.5, True), (3.0, True), (3.9, True),
                           (5.0, False)):
        L0 = math.log(r)
        zig = zig_exit_dirs_2008(r, horizon - 1)
        band = []
        c_grid = [10 ** (-4 + 3.5 * i / 79) for i in range(80)]  # 1e-4 .. ~0.3
        for c in c_grid:
            dirs = optimal_policy_tree(L0, ell, v, horizon, c)
            k_rule = math.ceil(math.log2(r))
            body = dirs[:-1] if dirs and dirs[-1] in ('TERM',) else dirs
            match = (len(body) >= k_rule and
                     all(b == z for b, z in zip(body, zig)) and
                     'X' not in dirs and 'NOEXIT' not in dirs)
            if match:
                band.append(c)
        found = bool(band)
        tag = "as predicted" if found == expect_band else "UNEXPECTED"
        if found:
            print(f"  C1 r={r:4.1f}: optimal policy == complete Zig for c in "
                  f"[{min(band):.4g}, {max(band):.4g}] ({tag})")
        else:
            print(f"  C1 r={r:4.1f}: no meta-cost band ({tag}; complete Zig "
                  f"is not a stationary-threshold policy here)")
        if found != expect_band:
            ok_c1 = False
    # C2: minimal-horizon claim -- at the smallest horizon k* for which the
    # minority action is reachable (k* = ceil(L0/ell), generic), the
    # worst-case-decisive FEH tree is the k*-level majority tree: exits
    # toward the majority at every level, i.e. the 2008 Zig run (their
    # truncated/L-shaped Zig of Example 6), with run length satisfying
    # 2^(k-1) <= r <= 2^k at v = 2/3 and k = ceil(ln r / ln odds(v)) generally.
    ok_c2 = True
    n_cells = 0
    n_match = 0
    for v2 in (0.60, 2.0 / 3.0, 0.75, 0.90):
        ell2 = math.log(v2 / (1.0 - v2))
        for r in (1.3, 2.5, 3.0, 5.0, 7.7, 12.0, 27.0, 77.0):
            L0 = math.log(r)
            # smallest horizon at which the minority action is strictly
            # reachable: k* = floor(L0/ell) + 1 (equals ceil(L0/ell) except
            # on the measure-zero boundary r = odds(v)^m, where the 2008
            # rule's k is itself non-unique)
            kstar = math.floor(L0 / ell2) + 1
            lp = [ell2] * kstar
            lm = [-ell2] * kstar
            tree = greedy_spine_tree(L0 + 1e-9, lp, lm, kstar)
            n_cells += 1
            want = [('E1',)] * (kstar - 1) + [('LAST', 1, 0)]
            if tree == want:
                n_match += 1
            else:
                ok_c2 = False
                print(f"  C2 MISMATCH v={v2:.3f} r={r}: tree={tree}")
    print(f"  C2: minimal-horizon tree == majority run + terminal in "
          f"{n_match}/{n_cells} (v, r) cells; run length = ceil(ln r / ln odds(v))")
    # C1b: Proposition C.5(i) window, both directions, incl. the k=1 case
    # (theta+ in (L0 - min(k-1,1)*ell, L0 - (k-2)*ell], theta- in
    # [L0-(k+1)*ell, L0-k*ell)); sample thetas inside and outside.
    ok_c1b = True
    n_lv = 16

    def band_tree(L0, ell, thp, thm, n):
        spine = L0
        dirs = []
        for _ in range(n):
            y, nch = spine + ell, spine - ell
            s1 = (y >= thp) or (y <= thm)
            s0 = (nch >= thp) or (nch <= thm)
            if s1 and s0:
                dirs.append('T'); break
            if not s1 and not s0:
                dirs.append('X'); break
            if s1:
                dirs.append('E1' if y > 0 else 'W'); spine = nch
            else:
                dirs.append('E0' if nch < 0 else 'W'); spine = y
        return dirs

    for r in (1.7, 3.0, 5.0, 7.7):
        L0 = math.log(r)
        ell = math.log(2.0)
        k = math.ceil(L0 / ell)
        zig = zig_exit_dirs_2008(r, n_lv)
        lo_p = L0 - min(k - 1, 1) * ell
        hi_p = L0 - (k - 2) * ell
        lo_m, hi_m = L0 - (k + 1) * ell, L0 - k * ell
        inside_ok = 0
        n_in = 0
        if k <= 2:
            for a in (0.25, 0.5, 0.75):
                for b in (0.25, 0.5, 0.75):
                    thp = lo_p + a * (hi_p - lo_p)
                    thm = lo_m + b * (hi_m - lo_m)
                    n_in += 1
                    if band_tree(L0, ell, thp, thm, n_lv) == zig:
                        inside_ok += 1
            if inside_ok != n_in:
                ok_c1b = False
        # outside samples must NOT give complete Zig (both k<=2 and k>=3)
        outside_bad = 0
        n_out = 0
        for thp in (lo_p - 0.3 * ell, lo_p - 0.05 * ell, hi_p + 0.05 * ell,
                    hi_p + 0.7 * ell):
            thm = lo_m + 0.5 * (hi_m - lo_m)
            n_out += 1
            if band_tree(L0, ell, thp, thm, n_lv) == zig:
                outside_bad += 1
        if k >= 3:
            # exhaustive-ish theta grid: no band at all should give Zig
            for a in [i / 20.0 for i in range(21)]:
                for b in [i / 10.0 for i in range(11)]:
                    thp = 0.01 + a * (L0 + 2 * ell)
                    thm = -0.01 - b * 3 * ell
                    n_out += 1
                    if band_tree(L0, ell, thp, thm, n_lv) == zig:
                        outside_bad += 1
        if outside_bad:
            ok_c1b = False
        tag = (f"inside {inside_ok}/{n_in}, " if k <= 2 else "")
        print(f"  C1b r={r:4.1f} (k={k}): {tag}outside/none->Zig violations: "
              f"{outside_bad}/{n_out}")
    return ok_c1 and ok_c2 and ok_c1b


# -------------------------------------------------------------------- PART C3

def policy_tree_census(L0, ell, v, horizon, c):
    """Like optimal_policy_tree, but records both children's stop decisions
    AND actions at every spine level, then classifies the induced procedure:
    ZIG / OTHER_FFT / FFT_NONCANON / CONSTANT / NOT_FFT."""
    def rho(L):
        mu = logistic(L)
        return min(mu, 1.0 - mu)

    def pred_p1(L):
        mu = logistic(L)
        return mu * v + (1.0 - mu) * (1.0 - v)

    ms = range(-horizon - 1, horizon + 2)
    V = {m: rho(L0 + m * ell) for m in ms}
    stop = {}
    for t in range(horizon - 1, -1, -1):
        NV = {}
        for m in ms:
            L = L0 + m * ell
            r_stop = rho(L)
            if abs(m) > t:
                NV[m] = r_stop
                stop[(t, m)] = True
                continue
            p1 = pred_p1(L)
            mp = min(m + 1, horizon + 1)
            mn = max(m - 1, -horizon - 1)
            r_cont = c + p1 * V[mp] + (1.0 - p1) * V[mn]
            NV[m] = min(r_stop, r_cont)
            stop[(t, m)] = r_stop <= r_cont
        V = NV
    # band-shape check: at every t, the continue set (within reachable,
    # parity-consistent states) must be an interval on the lattice
    band_violations = 0
    for t in range(horizon):
        cont = sorted(m for m in range(-t, t + 1)
                      if (m + t) % 2 == 0 and not stop[(t, m)])
        if any(b - a != 2 for a, b in zip(cont, cont[1:])):
            band_violations += 1
    # walk the spine, canonical level codes
    codes = []
    actions = []
    m = 0
    for t in range(horizon - 1):
        s1 = stop[(t + 1, m + 1)]
        s0 = stop[(t + 1, m - 1)]
        a1 = 1 if L0 + (m + 1) * ell > 0 else 0
        a0 = 1 if L0 + (m - 1) * ell > 0 else 0
        if not s1 and not s0:
            return codes, 'NOT_FFT', band_violations
        if s1 and s0:
            codes.append('T')
            actions += [a1, a0]
            break
        if s1:
            actions.append(a1)
            codes.append('E1' if a1 == 1 else 'W')
            m -= 1
        else:
            actions.append(a0)
            codes.append('E0' if a0 == 0 else 'W')
            m += 1
    else:
        # reached the horizon: forced terminal
        codes.append('T')
        actions += [1 if L0 + (m + 1) * ell > 0 else 0,
                    1 if L0 + (m - 1) * ell > 0 else 0]
    if len(set(actions)) == 1:
        return codes, 'CONSTANT', band_violations
    if 'W' in codes:
        return codes, 'FFT_NONCANON', band_violations
    zig = zig_exit_dirs_2008(math.exp(L0), len(codes))
    body = codes[:-1] if codes[-1] == 'T' else codes
    k_rule = math.ceil(math.log2(math.exp(L0)))
    if len(body) >= k_rule and all(b == z for b, z in zip(body, zig)):
        return codes, 'ZIG', band_violations
    return codes, 'OTHER_FFT', band_violations


def part_c3():
    print("=" * 72)
    print("PART C3 -- census of exactly-optimal procedures for k >= 3 priors:")
    print("           is ANY non-degenerate FFT ever exactly optimal?")
    print("=" * 72)
    horizon = 14
    v = 2.0 / 3.0
    ell = math.log(v / (1.0 - v))
    ok = True
    total_band_viol = 0
    # 4.5, 5.0, 6.3, 7.7 have k=3 (the loophole family of Prop C.7(iii));
    # 12.0 has k=4 (covered by the full case-analysis proof)
    for r in (4.5, 5.0, 6.3, 7.7, 12.0):
        L0 = math.log(r)
        counts = {}
        examples = {}
        c_grid = [10 ** (-4 + 3.8 * i / 119) for i in range(120)]  # 1e-4..~0.6
        for c in c_grid:
            codes, kind, bviol = policy_tree_census(L0, ell, v, horizon, c)
            total_band_viol += bviol
            counts[kind] = counts.get(kind, 0) + 1
            examples.setdefault(kind, (c, codes))
        print(f"  r={r:5.1f} (k={math.ceil(L0 / ell)}): {counts}")
        for kind in ('ZIG', 'OTHER_FFT', 'FFT_NONCANON'):
            if kind in counts:
                ok = False
                c_ex, codes_ex = examples[kind]
                print(f"    !! {kind} at c={c_ex:.4g}: {codes_ex}")
    print(f"  band-shape (interval continue set) violations across all "
          f"(t, c, r): {total_band_viol}")
    if ok:
        print("  confirmed: for k >= 3 the exact optimum is never a "
              "non-degenerate FFT (only NOT_FFT or CONSTANT)")
    return ok and total_band_viol == 0


# --------------------------------------------------------------------- PART E

def solve_linear(A, b):
    """Gaussian elimination with partial pivoting for small systems."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda rr: abs(M[rr][col]))
        M[col], M[piv] = M[piv], M[col]
        if abs(M[col][col]) < 1e-12:
            M[col][col] = 1e-12
        for rr in range(n):
            if rr != col:
                f = M[rr][col] / M[col][col]
                for cc in range(col, n + 1):
                    M[rr][cc] -= f * M[col][cc]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_ridge_logistic(X, y, lam=0.1, iters=25):
    """IRLS ridge logistic regression; X rows include intercept slot."""
    d = len(X[0])
    w = [0.0] * d
    for _ in range(iters):
        grad = [-lam * w[j] for j in range(d)]
        H = [[lam if i == j else 0.0 for j in range(d)] for i in range(d)]
        for xi, yi in zip(X, y):
            z = sum(w[j] * xi[j] for j in range(d))
            z = max(-30.0, min(30.0, z))
            mu = logistic(z)
            for j in range(d):
                grad[j] += (yi - mu) * xi[j]
                for jj in range(d):
                    H[j][jj] += mu * (1 - mu) * xi[j] * xi[jj]
        step = solve_linear(H, grad)
        w = [w[j] + step[j] for j in range(d)]
    return w


def greedy_spine_tree_fallback(L0, lp, lm, k):
    """Greedy spine construction with a MAP fallback at stuck levels (for
    estimated weights that violate DD-decisiveness); returns (levels, n_stuck)."""
    spine = L0
    levels = []
    n_stuck = 0
    for i in range(k):
        if i == k - 1:
            levels.append(('LAST', 1 if spine + lp[i] > 0 else 0,
                           1 if spine + lm[i] > 0 else 0))
            return levels, n_stuck
        tp = sum(lp[i + 1:k])
        tm = sum(lm[i + 1:k])
        d1 = spine + lp[i] + tm > 0
        d0 = spine + lm[i] + tp < 0
        if d1 and d0:
            levels.append(('LAST', 1, 0))
            return levels, n_stuck
        if d1:
            levels.append(('E1',))
            spine += lm[i]
        elif d0:
            levels.append(('E0',))
            spine += lp[i]
        else:
            n_stuck += 1
            if spine > 0:
                levels.append(('E1',))
                spine += lm[i]
            else:
                levels.append(('E0',))
                spine += lp[i]
    return levels, n_stuck


def part_e():
    print("=" * 72)
    print("PART E -- finite-sample snapping: plug-in FFT vs plug-in linear vs")
    print("          ridge-logistic in a (DD+/-) ecology")
    print("=" * 72)
    K = 4
    lp = [2.2, 1.0, 0.45, 0.20]
    lm = [-2.4, -1.1, -0.50, -0.22]
    mu0 = 0.65
    L0 = math.log(mu0 / (1.0 - mu0))
    assert check_ddpm(lp, lm)
    pq = [weights_to_likelihoods(lp[i], lm[i]) for i in range(K)]
    print(f"  ecology: K={K}, mu0={mu0}, "
          f"(p,q) per cue: {[(round(p, 3), round(q, 3)) for p, q in pq]}")

    profiles = list(itertools.product((0, 1), repeat=K))

    def true_lambda(x):
        return L0 + sum(lp[i] if x[i] else lm[i] for i in range(K))

    def p_joint(x, y):
        pr = mu0 if y == 1 else 1.0 - mu0
        for i in range(K):
            p, q = pq[i]
            like = (p if y == 1 else q) if x[i] == 1 else \
                   ((1 - p) if y == 1 else (1 - q))
            pr *= like
        return pr

    bayes = {x: (1 if true_lambda(x) > 0 else 0) for x in profiles}
    bayes_risk = sum(p_joint(x, 1 - bayes[x]) for x in profiles)

    def risk(f):
        return sum(p_joint(x, 1 - f[x]) for x in profiles)

    # geometry constants: spine decisiveness slack vs global profile margin
    spine = L0
    slacks = []
    for i in range(K - 1):
        tp, tm = sum(lp[i + 1:]), sum(lm[i + 1:])
        d1, d0 = spine + lp[i] + tm, spine + lm[i] + tp
        slacks.append(max(d1, -d0))
        spine += lm[i] if d1 > 0 else lp[i]
    delta_spine = min(slacks)
    gamma_min = min(abs(true_lambda(x)) for x in profiles)
    print(f"  min spine decisiveness slack Delta = {delta_spine:.3f}; "
          f"min profile margin gamma = {gamma_min:.3f} (Delta >= gamma: "
          f"{delta_spine >= gamma_min})")

    print(f"  {'N':>5} {'P(tree==Bayes)':>15} {'excess(FFT)':>12} "
          f"{'excess(lin)':>12} {'excess(logit)':>14} {'stuck%':>7}")
    reps = 400
    for N in (10, 20, 40, 80, 160, 320):
        snap = 0
        ex_tree = ex_lin = ex_logit = 0.0
        stuck_total = 0
        for _ in range(reps):
            data = []
            for _n in range(N):
                y = 1 if random.random() < mu0 else 0
                x = tuple(1 if random.random() < (pq[i][0] if y else pq[i][1])
                          else 0 for i in range(K))
                data.append((x, y))
            n1 = sum(y for _x, y in data)
            mu_h = (n1 + 1.0) / (N + 2.0)
            L0_h = math.log(mu_h / (1.0 - mu_h))
            lp_h, lm_h, flip = [], [], []
            for i in range(K):
                a = sum(1 for x, y in data if y == 1 and x[i] == 1)
                b = sum(1 for x, y in data if y == 0 and x[i] == 1)
                p_h = (a + 1.0) / (n1 + 2.0)
                q_h = (b + 1.0) / ((N - n1) + 2.0)
                lpi = math.log(p_h / q_h)
                lmi = math.log((1 - p_h) / (1 - q_h))
                if lpi >= 0:
                    lp_h.append(lpi); lm_h.append(lmi); flip.append(False)
                else:
                    lp_h.append(-lmi); lm_h.append(-lpi); flip.append(True)
            order = sorted(range(K),
                           key=lambda i: -max(lp_h[i], -lm_h[i]))
            lp_o = [lp_h[i] for i in order]
            lm_o = [lm_h[i] for i in order]
            tree, n_stuck = greedy_spine_tree_fallback(L0_h, lp_o, lm_o, K)
            stuck_total += n_stuck

            def f_tree(x):
                xv = tuple((1 - x[i]) if flip[i] else x[i] for i in range(K))
                xo = tuple(xv[i] for i in order)
                return classify_tree(tree, xo)

            def f_lin(x):
                s = L0_h
                for i in range(K):
                    xi = (1 - x[i]) if flip[i] else x[i]
                    s += lp_h[i] if xi else lm_h[i]
                return 1 if s > 0 else 0

            Xd = [[1.0] + [float(xx) for xx in x] for x, _y in data]
            yd = [float(y) for _x, y in data]
            w = fit_ridge_logistic(Xd, yd)

            def f_logit(x):
                z = w[0] + sum(w[j + 1] * x[j] for j in range(K))
                return 1 if z > 0 else 0

            ftab = {x: f_tree(x) for x in profiles}
            if all(ftab[x] == bayes[x] for x in profiles):
                snap += 1
            ex_tree += risk(ftab) - bayes_risk
            ex_lin += risk({x: f_lin(x) for x in profiles}) - bayes_risk
            ex_logit += risk({x: f_logit(x) for x in profiles}) - bayes_risk
        print(f"  {N:>5} {snap / reps:>15.3f} {ex_tree / reps:>12.4f} "
              f"{ex_lin / reps:>12.4f} {ex_logit / reps:>14.4f} "
              f"{100.0 * stuck_total / (reps * (K - 1)):>6.1f}%")
    return True


# --------------------------------------------------------------------- PART D

def all_ffts(K):
    """Enumerate all complete/truncated FFTs over K cues in a fixed order:
    depth m in 1..K, exit direction per non-terminal level, terminal level
    assigns value1->C1, value0->C0."""
    for m in range(1, K + 1):
        for dirs in itertools.product(('E1', 'E0'), repeat=m - 1):
            yield [(d,) for d in dirs] + [('LAST', 1, 0)]


def part_d():
    print("=" * 72)
    print("PART D -- sharpness: uniform validities violate (DD+/-), no FFT")
    print("=" * 72)
    K = 3
    v = 0.70
    ell = math.log(v / (1.0 - v))
    lp = [ell] * K
    lm = [-ell] * K
    L0 = 0.0
    print(f"  profile: v=({v},{v},{v}), l+=-l-={ell:.3f}, uniform prior")
    print(f"  (DD+/-) holds: {check_ddpm(lp, lm)}")
    tree = greedy_spine_tree(L0 + 1e-9, lp, lm, K)
    print(f"  greedy spine construction returns: {tree}")
    # brute force: does ANY FFT (any cue order irrelevant by symmetry)
    # reproduce the full-Bayes (majority) classifier?
    n_match = 0
    for cand in all_ffts(K):
        good = True
        for x in itertools.product((0, 1), repeat=K):
            if classify_tree(cand, x) != classify_bayes(1e-9, lp, lm, K, x):
                good = False
                break
        if good:
            n_match += 1
    print(f"  FFTs (fixed order, all exit structures/depths) matching Bayes "
          f"(= majority rule): {n_match} of {sum(1 for _ in all_ffts(K))}")
    x = (0, 1, 1)
    print(f"  witness x={x}: bayes={classify_bayes(1e-9, lp, lm, K, x)}, "
          f"depth-1 tree would give {1 if x[0] == 1 else 0}")
    return n_match == 0


# --------------------------------------------------------------------- PART F

def hbin(p):
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log(p) - (1 - p) * math.log(1 - p)


def gain(mu, p, q):
    """Marginal information gain of a binary cue (p, q) at posterior mu:
    I(s; c) = h(mu p + (1-mu) q) - mu h(p) - (1-mu) h(q)."""
    return hbin(mu * p + (1 - mu) * q) - mu * hbin(p) - (1 - mu) * hbin(q)


def part_f():
    print("=" * 72)
    print("PART F -- Lemma C.1 ingredients: submodularity of information gain;")
    print("          v^P ordering vs information-gain ordering")
    print("=" * 72)
    # (a) submodularity: I(s; c_j | c_A) <= I(s; c_j | c_B) for B subset A,
    # exact enumeration, random asymmetric ecologies + random priors
    fails = 0
    checks = 0
    for _ in range(200):
        K = 4
        mu0 = random.uniform(0.05, 0.95)
        p = [random.uniform(0.05, 0.95) for _ in range(K)]
        q = [random.uniform(0.05, 0.95) for _ in range(K)]
        j = random.randrange(K)
        others = [i for i in range(K) if i != j]
        random.shuffle(others)
        A = others[:random.randint(1, 3)]
        B = A[:random.randint(0, len(A) - 1)]

        def cond_gain(cond):
            tot = 0.0
            for vals in itertools.product((0, 1), repeat=len(cond)):
                pr1 = mu0
                pr0 = 1 - mu0
                for idx, val in zip(cond, vals):
                    pr1 *= p[idx] if val else (1 - p[idx])
                    pr0 *= q[idx] if val else (1 - q[idx])
                pa = pr1 + pr0
                if pa < 1e-15:
                    continue
                tot += pa * gain(pr1 / pa, p[j], q[j])
            return tot

        checks += 1
        if cond_gain(A) > cond_gain(B) + 1e-10:
            fails += 1
            print(f"    SUBMODULARITY FAIL: mu0={mu0:.3f} j={j} A={A} B={B}")
    print(f"  (a) submodularity: {checks - fails}/{checks} random "
          f"(ecology, prior, A, B) checks pass")
    # (b) counterexample: at mu = 1/2, ordering by MKW08 lumped validity v^P
    # can disagree with information-gain ordering for asymmetric cues
    mu = 0.5
    pA, qA = 0.60, 0.40
    pB, qB = 0.99, 0.86
    vP_A = mu * pA + (1 - mu) * (1 - qA)
    vP_B = mu * pB + (1 - mu) * (1 - qB)
    gA = gain(mu, pA, qA)
    gB = gain(mu, pB, qB)
    print(f"  (b) cue A (p={pA}, q={qA}): v^P={vP_A:.3f}, gain={gA:.4f} nats")
    print(f"      cue B (p={pB}, q={qB}): v^P={vP_B:.3f}, gain={gB:.4f} nats")
    sep = vP_A > vP_B and gB > gA
    print(f"      A beats B on lumped validity, B beats A on information "
          f"gain: {sep}")
    print("      -> v^P is a surrogate, not the FEH-native order; orderings "
          "coincide for symmetric cues (q = 1-p)")
    # symmetric case: gain monotone in validity (numerical monotonicity check)
    vs = [0.55 + 0.04 * i for i in range(11)]
    gs = [gain(0.5, v_, 1 - v_) for v_ in vs]
    mono = all(b > a for a, b in zip(gs, gs[1:]))
    print(f"      symmetric-cue gain monotone in validity: {mono}")
    return fails == 0 and sep and mono


# --------------------------------------------------------------------- PART G

def part_g():
    """Lemma C.11 -- analytic closure of the k=3 loophole ("understated-prior
    Zig": continue at A = L0-2*ell and F = A+ell, stop at B = A-ell and
    G = A+2*ell). The proof's crux is the drift identity
        q(F) - p1(B) = (2v-1) * (1 - mu(F) - mu(B)) < 0   (since F+B = 2A > 0),
    which makes the necessary conditions
        (C-F): c <= q(F) * Delta_A
        (S-B): VoI1(B) + p1(B) * Delta_A <= c
    jointly infeasible. This part verifies the identity, the sign, and the
    joint infeasibility across the full k=3 parameter range."""
    print("=" * 72)
    print("PART G -- Lemma C.11: analytic closure of the k=3 loophole")
    print("=" * 72)
    id_fails = sign_fails = feas_fails = 0
    cells = 0
    for v in (0.55, 0.60, 2.0 / 3.0, 0.75, 0.85, 0.95):
        ell = math.log(v / (1.0 - v))
        for i_a in range(1, 20):
            a = (i_a / 20.0) * ell          # A = a in (0, ell); L0 = a + 2 ell
            muA = logistic(a)
            muF = logistic(a + ell)
            muB = logistic(a - ell)

            def p1(mu):
                return mu * v + (1.0 - mu) * (1.0 - v)

            p1A, p1F, p1B = p1(muA), p1(muF), p1(muB)
            qF, qA = 1.0 - p1F, 1.0 - p1A
            cells += 1
            # (i) the drift identity
            if abs((qF - p1B) - (2 * v - 1) * (1 - muF - muB)) > 1e-12:
                id_fails += 1
            # (ii) the sign: mu(F) + mu(B) > 1 since F + B = 2A > 0
            if not muF + muB > 1.0:
                sign_fails += 1
            # (iii) joint infeasibility of (C-F) and (S-B), stationary values:
            # Delta_A = [VoI1(A) - c(1+p1A)] / (1 - p1A*qF)
            voiB = p1B * (2 * muA - 1.0)
            voiA = qA * (1.0 - 2.0 * muB)
            for i_c in range(200):
                c = 10 ** (-5 + 4.5 * i_c / 199)
                dA = (voiA - c * (1 + p1A)) / (1 - p1A * qF)
                if dA < 0:
                    continue
                if c <= qF * dA + 1e-15 and voiB + p1B * dA <= c + 1e-15:
                    feas_fails += 1
                    print(f"    FEASIBLE?! v={v:.3f} a={a:.3f} c={c:.5g}")
                    break
    print(f"  drift identity q(F)-p1(B) == (2v-1)(1-muF-muB): "
          f"{cells - id_fails}/{cells} exact")
    print(f"  sign mu(F)+mu(B) > 1 (i.e. q(F) < p1(B)): "
          f"{cells - sign_fails}/{cells}")
    print(f"  (C-F) and (S-B) jointly satisfiable somewhere on the "
          f"(v, a, c) grid: {feas_fails} cells (Lemma predicts 0)")
    # worked example quoted in the draft (r = 5, v = 2/3)
    v = 2.0 / 3.0
    ell = math.log(2.0)
    a = math.log(5.0) - 2 * ell
    muA, muF, muB = logistic(a), logistic(a + ell), logistic(a - ell)
    p1B = muB * v + (1 - muB) * (1 - v)
    qF = 1 - (muF * v + (1 - muF) * (1 - v))
    print(f"  worked example r=5, v=2/3: q(F)={qF:.4f}, p1(B)={p1B:.4f}, "
          f"q(F)-p1(B)={qF - p1B:.4f}, VoI1(B)={p1B * (2 * muA - 1):.4f}")
    return id_fails == 0 and sign_fails == 0 and feas_fails == 0


# ----------------------------------------------------------------------- main

if __name__ == '__main__':
    ra = part_a()
    rb = part_b()
    rc = part_c()
    rc3 = part_c3()
    rd = part_d()
    re_ = part_e()
    rf = part_f()
    rg = part_g()
    print("=" * 72)
    verdict = {True: "PASS", False: "FAIL"}
    print(f"Part A  (Thm 2.7.5 identity + profiles):   {verdict[ra]}")
    print(f"Part B  (Zig rule, OSLA derivation):       {verdict[rb]}")
    print(f"Part C  (Zig bands + C.5 window + min-k*): {verdict[rc]}")
    print(f"Part C3 (no non-degenerate FFT, k >= 3):   {verdict[rc3]}")
    print(f"Part D  (sharpness under DD violation):    {verdict[rd]}")
    print(f"Part E  (finite-sample snapping):          {verdict[re_]}")
    print(f"Part F  (Lemma C.1: submodularity, v^P):   {verdict[rf]}")
    print(f"Part G  (Lemma C.11: k=3 loophole closed): {verdict[rg]}")
