#!/usr/bin/env python3
"""
analyse_charge_tests.py - analyse the single-charge tests of Section X.4.

Reads whatever has completed in 06_charge_tests and reports four things:

  1. the first-order error, explicit minus q*Dv, per site
  2. the second-order (polarisation) term, per site
  3. whether the second-order term falls with standoff as R^-4, which Sokalski
     (1985) gives for the classical induction contribution
  4. whether the polarisation term is systematic across sites, which is the
     question Beker and Sokalski (2016) leave open

WHAT DECIDES THE SCREEN
  Not the size of the second-order term but its variation. A constant offset
  leaves the ranking untouched and the screen valid. Scatter reorders candidates
  and means anything the screen selects must be verified explicitly.

  The spread is therefore judged against the range of Dv across the grid, which
  is what the ranking has to resolve, rather than against the mean of the
  second-order term itself. A term of 0.5 kcal/mol with a spread of 0.5 is
  useless as a correction but harmless if the Dv range is 8; the same spread
  against a Dv range of 1 would be fatal.

  No conclusion is drawn from fewer than three sites.

Usage:  python3 analyse_charge_tests.py [directory]
Needs only the standard library, so it is safe on the login node.
"""
import os, re, sys, math

H = 627.5094740631
D = sys.argv[1] if len(sys.argv) > 1 else "."

def E(p):
    p = os.path.join(D, p)
    if not os.path.exists(p): return None
    t = open(p, errors="replace").read()
    if "TERMINATED NORMALLY" not in t: return None
    m = re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)
    return float(m[-1]) if m else None

def pair(tag, suffix=""):
    """Return (first order, second order) for a site, or None."""
    a = [E(f"sp_{g}_{tag}{suffix}_p.out") for g in ("reactant", "ts")]
    b = [E(f"sp_{g}_{tag}{suffix}_m.out") for g in ("reactant", "ts")]
    if None in a + b: return None
    dp = (a[1] - a[0]) * H - B0
    dm = (b[1] - b[0]) * H - B0
    return (dp - dm) / 2.0, (dp + dm) / 2.0

r0, t0 = E("sp_reactant_q0.out"), E("sp_ts_q0.out")
if r0 is None or t0 is None:
    sys.exit("the q = 0 control has not completed; nothing can be normalised")
B0 = (t0 - r0) * H
print(f"reference barrier, no external charge: {B0:.4f} kcal/mol\n")

rows = [l.split("\t") for l in
        open(os.path.join(D, "sites.tsv")).read().splitlines()[1:] if l.strip()]

print("=" * 96)
print("Per-site results at q = +/- 1 e")
print("=" * 96)
print(f"{'site':<20}{'shell':>6}{'Dv':>9}{'1st order':>11}{'error':>9}"
      f"{'err %':>8}{'2nd order':>11}{'2nd/1st %':>11}")
print("-" * 96)

data = []
for c in rows:
    tag, shell, dv = c[0], float(c[5]), float(c[7])
    got = pair(tag)
    if got is None:
        print(f"{tag:<20}{shell:>6.1f}   incomplete"); continue
    fo, so = got
    err = fo - dv
    pe = 100 * err / dv if abs(dv) > 1e-6 else float("nan")
    ratio = 100 * so / fo if abs(fo) > 1e-6 else float("nan")
    data.append((tag, shell, dv, fo, err, so))
    print(f"{tag:<20}{shell:>6.1f}{dv:>9.3f}{fo:>11.3f}{err:>9.3f}"
          f"{pe:>8.1f}{so:>11.3f}{ratio:>11.1f}")

MIN_SITES = 8
if len(data) < MIN_SITES:
    print(f"\nOnly {len(data)} site(s) complete. No conclusion is drawn below"
          f" {MIN_SITES}, because the first sites to finish are the extremes and"
          f"\nany correlation computed from them is an artefact of that choice.")
    sys.exit(0)

# ---------------------------------------------------------------- statistics
def stats(v):
    n = len(v); m = sum(v) / n
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0.0
    return m, s

errs = [d[4] for d in data]; sos = [d[5] for d in data]
dvs = [d[2] for d in data]
me, se = stats(errs); ms, ss = stats(sos)
dv_range = max(dvs) - min(dvs)

print("\n" + "=" * 96)
print(f"{len(data)} sites")
print("=" * 96)
print(f"first-order error   mean {me:+.4f}  sd {se:.4f}  max |e| {max(abs(x) for x in errs):.4f} kcal/mol")
print(f"second-order term   mean {ms:+.4f}  sd {ss:.4f}  range {min(sos):+.3f} to {max(sos):+.3f}")
print(f"Dv range across these sites: {dv_range:.3f} kcal/mol")
print(f"second-order spread as a fraction of the Dv range: {100*ss/dv_range:.1f}%")
srt = sorted(dvs)
gaps = [srt[i+1]-srt[i] for i in range(len(srt)-1)]
if gaps:
    print(f"median Dv gap between adjacent sites sampled here: {sorted(gaps)[len(gaps)//2]:.3f} kcal/mol")
    print("  The Dv range is set by two extremes and flatters the comparison. What")
    print("  the ranking must resolve is the gap between candidates the optimiser")
    print("  chooses among, which on the full 1448-site grid is far smaller than any")
    print("  gap sampled here. The reordering test below is the operative one.")

print("\nInterpretation")
if se < 0.02:
    print("  The first-order term is reproduced essentially exactly. The linear")
    print("  model is doing what it claims at fixed geometry.")
elif se < 0.10:
    print("  The first-order term is reproduced to within a few hundredths of a")
    print("  kcal/mol. The residual is second order and is reported separately.")
else:
    print("  The first-order term is NOT reproduced within a constant. Something")
    print("  beyond polarisation is contributing and must be identified.")

if 100 * ss / dv_range < 5:
    print(f"\n  The polarisation term varies by {ss:.3f} kcal/mol across sites,")
    print(f"  which is {100*ss/dv_range:.1f}% of the {dv_range:.2f} kcal/mol range the ranking")
    print("  must resolve. It does not reorder candidates, and the screen stands")
    print("  as a ranking. This is the behaviour Beker and Sokalski (2016)")
    print("  describe, of a term significant in magnitude but summing to an")
    print("  approximately systematic value.")
else:
    print(f"\n  The polarisation term varies by {ss:.3f} kcal/mol across sites,")
    print(f"  which is {100*ss/dv_range:.1f}% of the {dv_range:.2f} kcal/mol range the ranking must")
    print("  resolve. It is not systematic, so it can reorder candidates whose Dv")
    print("  values differ by less than that. The screen remains usable for coarse")
    print("  ranking, but anything it selects must be verified explicitly rather")
    print("  than trusted. Politzer and Murray (2002) reach the same conclusion")
    print("  for the extrema of V(r), which they call 'not consistently reliable'")
    print("  for precisely this reason.")

# ------------------------- does polarisation amplify the map or reorder it?
print("\n" + "=" * 96)
print("Does the polarisation term track Dv, or scatter independently of it?")
print("=" * 96)
print("  The two terms depend on different molecular properties, so no correlation")
print("  is expected. The first-order term follows the difference in POTENTIAL")
print("  between the endpoints, V_TS - V_R. The second-order term follows the")
print("  difference in POLARISABILITY, weighted by the square of the field the")
print("  charge exerts: roughly -(alpha_TS - alpha_R)F^2/2. Sokalski (1985) gives")
print("  the basis, noting second-order magnitudes are 'related to polarizabilities")
print("  of interacting molecules'.")
print()
print("  A transition state has partially broken bonds and therefore looser")
print("  electrons, so alpha_TS generally exceeds alpha_R and the second-order term")
print("  is generally negative. A site where the potential difference vanishes need")
print("  not have a vanishing polarisability difference, so a near-zero Dv site can")
print("  still carry a substantial second-order term. That is the diagnostic.")
print()
if len(data) >= MIN_SITES:
    xs = [d[2] for d in data]; ys = [d[5] for d in data]
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxx = sum((a-mx)**2 for a in xs); syy = sum((b-my)**2 for b in ys)
    r = (sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / math.sqrt(sxx*syy)
         if sxx > 0 and syy > 0 else float("nan"))
    print(f"  Pearson r between Dv and the second-order term: {r:+.4f}  (n = {n})")
    neg = sum(1 for v in ys if v < 0)
    print(f"  second-order term negative at {neg}/{n} sites")
    print()
    # the question that decides the screen: does adding it reorder candidates?
    tot = [a + b for a, b in zip(xs, ys)]
    pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    swaps = [(i, j) for i, j in pairs if (xs[i] < xs[j]) != (tot[i] < tot[j])]
    print(f"  site pairs reordered by adding the second-order term:"
          f" {len(swaps)}/{len(pairs)}")
    if swaps:
        gaps = [abs(xs[i]-xs[j]) for i, j in swaps]
        print(f"  those pairs differ in Dv by {min(gaps):.3f} to {max(gaps):.3f}"
              f" kcal/mol")
        print(f"  the largest Dv gap that gets reordered is {max(gaps):.3f} kcal/mol,")
        print("  which is the resolution limit of the screen: candidates separated by")
        print("  less than that cannot be ordered reliably by the linear objective")
        print("  alone and must be verified explicitly.")
    else:
        print("  No pair is reordered at these sites, so the screen orders them")
        print("  correctly despite the neglected term. Note this is a statement")
        print("  about the sites sampled, not a guarantee for candidates closer")
        print("  together in Dv than any pair tested here.")

# --------------------------------------------------- Sokalski's R^-4 prediction
print("\n" + "=" * 96)
print("Does the second-order term fall as R^-4, as Sokalski (1985) gives for")
print("the classical induction contribution?")
print("=" * 96)
by = {}
for tag, shell, dv, fo, err, so in data:
    by.setdefault(shell, []).append(abs(so))
shells = sorted(by)
if len(shells) < 2:
    print("  fewer than two shells complete")
else:
    print(f"{'shell':>7}{'n':>4}{'mean |2nd order|':>19}")
    means = {}
    for s in shells:
        m = sum(by[s]) / len(by[s]); means[s] = m
        print(f"{s:>7.1f}{len(by[s]):>4}{m:>19.4f}")
    print("\n  ratios, observed against the R^-4 expectation:")
    base = shells[0]
    for s in shells[1:]:
        obs = means[base] / means[s] if means[s] > 0 else float("inf")
        exp = (s / base) ** 4
        print(f"    {base:.0f} A / {s:.0f} A :  observed {obs:6.2f}   R^-4 predicts {exp:6.2f}")
    print("\n  The relevant distance is from the charge to the polarisable density,")
    print("  not the standoff from the van der Waals surface, and the two differ by")
    print("  roughly a molecular radius. Treat this as a trend rather than a fit.")
    print("  Agreement would indicate the second-order term is classical")
    print("  polarisation and nothing further; departure would indicate otherwise.")

# ------------------------------------------------------------- charge scaling
print("\n" + "=" * 96)
print("Charge-magnitude scaling: first order should go as q, second as q^2")
print("=" * 96)
print(f"{'site':<20}{'q':>6}{'1st order':>12}{'/q':>10}{'2nd order':>12}{'/q^2':>10}")
print("-" * 70)
for tag in ("most_stabilising", "most_destabilising", "shell3_q1"):
    block = []
    for lab, qv in (("_q025", 0.25), ("_q050", 0.50), ("", 1.00)):
        got = pair(tag, lab)
        if got is None: continue
        fo, so = got
        block.append((qv, fo, so))
        print(f"{tag:<20}{qv:>6.2f}{fo:>12.4f}{fo/qv:>10.4f}{so:>12.4f}{so/qv**2:>10.4f}")
    if len(block) >= 2:
        f = [b[1] / b[0] for b in block]; s = [b[2] / b[0] ** 2 for b in block]
        df = 100 * (max(f) - min(f)) / abs(sum(f) / len(f))
        ds = 100 * (max(s) - min(s)) / abs(sum(s) / len(s))
        print(f"{'':<20}{'spread':>6}{'':>12}{df:>9.1f}%{'':>12}{ds:>9.1f}%")
print("\n  Both normalised columns constant means the expansion is perturbative")
print("  at 1 e, so these results scale to the magnitudes a design would use.")
print("  Note that charge-transfer induction, which Sokalski describes as")
print("  exponential rather than polynomial, cannot arise for a bare point")
print("  charge, which has no orbitals. Clean q^2 behaviour is therefore")
print("  expected here and does not license the same assumption for a molecular")
print("  surrogate treated quantum-mechanically.")

# ------------------------------------------------------------------ controls
print("\n" + "=" * 96)
print("Controls")
print("=" * 96)
print(f"  q = 0            barrier {B0:.4f} kcal/mol")
for tag, note in (("distant_p", "+1 e at 20 A"), ("distant_m", "-1 e at 20 A")):
    a, b = E(f"sp_reactant_{tag}.out"), E(f"sp_ts_{tag}.out")
    if a is None or b is None: continue
    print(f"  {note:<16} DDE = {(b-a)*H-B0:+.4f} kcal/mol")
print("  At 20 A the expectation is q*Dv at that position, which is small but")
print("  finite, not zero: the monopole term cancels exactly between two")
print("  endpoints of equal charge, leaving the difference in the higher moments.")
