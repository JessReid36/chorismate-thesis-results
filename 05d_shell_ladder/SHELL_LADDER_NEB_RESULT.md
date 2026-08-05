# Discrete ±1 External-Charge Ladder + GOCAT-Style Screen + NEB-under-Field: Negative Result

**Two-part negative:** (1) a certified geometry ceiling — no distance preorganises the dianion into the
near-attack window; and (2) where a connected NEB path can be read, the field *raises* the barrier well
above the bare value — the charges are **anti-catalytic**, not path-destroying. "Certified" refers to the
charge *placement*: the MILP (HiGHS, gap 0.000) finds the provably optimal ±1 arrangement on each shell,
and even that optimal arrangement fails to catalyse.

## Question
Can a set of external ±1 point charges (represented by frozen molecular surrogates: guanidinium=+1,
formate=−1) around the bare chorismate dianion electrostatically catalyse chorismate→prephenate, and if
so at what distance? Bare barrier = +17.47 kcal/mol.

## Method (three stages, GOCAT-faithful)
1. **Distance ladder.** Certified MILP (HiGHS, gap 0.000) placed K=10 discrete ±1 charges on vdW shells
   from 2–15 Å (0.1 Å fine sweep through 7–9 Å), minimising the Sokalski ΔV=V_TS−V_R proxy. Each design's
   substrate relaxed under the fixed field (QM/MM, B3LYP-D3BJ/def2-SVP/CPCM ε=4; surrogates frozen).
2. **Controls.** Bare substrate (no bodies, no field) and uncharged bodies (field off) relaxed identically.
3. **GOCAT stationary-point screen + NEB.** Following Dittner/Hartke GOCAT (Algorithm 1, Eq 3.2–3.3):
   relax reactant AND product under each field, keep only designs whose endpoints converge to intact minima
   (reactant: ether O3–C4 intact; product: C1–C6 formed, not shattered), then run NEB-CI under the field
   (ASH/Knarr, 14 images including the two endpoints, ActiveRegion freezing the 64 surrogate atoms to
   anchor the lab frame) between the field-relaxed endpoints. Barrier = highest band image − reactant
   image, on ONE connected path.

## Results

### Controls (baselines, clean)
- Bare substrate relaxes to C1–C6 = 3.538 Å (the dianion sits at the window edge on its own).
- Uncharged bodies: C1–C6 = 3.367 Å ≈ bare → **surrogate bodies are sterically inert**; all field effects
  are attributable to the charges, not the bodies.

### Geometry ladder (2–15 Å, 30 designs) — no preorganisation at any distance
- **Close shells (3–6 Å): fragment** the substrate (ether O3–C4 stretched 4–15 Å).
- **Far shells (7–15 Å): intact but OPEN**, pushed *past* the bare baseline (C1–C6 4–5.4 Å) by net-negative
  charge imbalance prying the dianion apart.
- **Window (C1–C6 ∈ [2.6,3.5]):** only 7.4 Å touched it (3.407) in the first relaxation, but on clean
  re-relaxation it settled OPEN at 3.813 Å — a non-robust fluke, not a sweet spot.
- **No distance yields robust near-attack preorganisation.**

### GOCAT stationary-point screen (26 intact designs) — half fail outright
- **14/26 FAIL** the screen: the field over-stretches/shatters the PRODUCT (O3–C4 5.5–8.0 Å vs reference
  2.9 Å) → no valid product minimum → non-catalytic by GOCAT's Eq 3.2/3.3 criterion, no barrier possible.
- **12–13/26 PASS** (valid reactant + product minima) → eligible for NEB. But every passing reactant is
  intact-yet-OPEN (C1–C6 3.5–5.2 Å) — none preorganised into the window.

### NEB-under-field on PASS designs — a valid path exists; the barrier goes UP (anti-catalytic)
This is the corrected reading (see SHELL_LADDER_NEB_CORRECTION.md for what changed and why). The committed
`final_band.txt` for each design was re-read directly; the barrier is the highest band image relative to
the reactant image (image 0), on the connected band.

**Every band that produced a profile has a clear positive forward peak — none is barrierless.** A product
image lying *below* the reactant image means the reaction is exothermic under the field, NOT that there is
no forward barrier; the barrier is the peak between them.

| design | peak barrier (kcal/mol) | product ΔE | peak MaxF (eV/Å) | band |
|--------|------------------------:|-----------:|-----------------:|------|
| 7p4    | +77.3 | −2.3  | 1.04 | clean single peak |
| 8p1    | +77.7 | +9.8  | 0.70 | clean single peak |
| 13p0   | +77.6 | −18.1 | 0.59 | clean single peak |
| 15p0   | +37.9 | +8.2  | 0.90 | clean single peak |
| 7p3    | +32.3 | −29.2 | 0.86 | bounded, mildly rugged |
| 8p2    | +50.4 | −21.7 | 0.82 | bounded, mildly rugged |
| 8p5    | +84.3 | −32.2 | 0.84 | bounded, mildly rugged |
| 7p8    | +20.8 | −30.6 | 1.86 | bounded, rugged |
| 7p6    | (+36) | +10.0 | 3.26 | under-converged — not quoted |
| 8p6    | (+48) | −4.2  | 5.10 | under-converged — not quoted |
| 8p9    | (+47) | −19.5 | 10.31| under-converged — not quoted |
| 7p1    | (+171)| −74.6 | 4.89 | under-converged — not quoted |
| 12p0   | (+177)| +9.0  | 5.87 | under-converged — not quoted |
| 2p0    | — | — | — | no band (close shell, fragmented) |

- **Four designs (7p4, 8p1, 13p0, 15p0) give clean single-peaked minimum-energy paths** with moderate
  residual forces (peak MaxF 0.6–1.0 eV/Å). Their barriers, **+37.9 to +77.7 kcal/mol**, are 2.2–4.5× the
  +17.47 bare barrier: a valid connected R→TS→P path exists and the field makes the barrier **worse**.
- The bounded mildly-rugged set (7p3, 8p2, 8p5, 7p8) also peaks above bare (+20.8 to +84.3); their exact
  values are not tightly converged and are reported for shape, not as final numbers.
- Five designs (7p6, 8p6, 8p9, 7p1, 12p0) carry large residual forces (peak MaxF 2–10 eV/Å) and are
  genuinely under-converged; their peak values are **not quoted as barriers**. None drops below bare in its
  current loose state, but each must be reconverged before it can be quoted.
- 2p0 (a close shell) produced no band — consistent with the fragmentation seen in the geometry ladder.

**Convergence caveat (honest):** the four clean bands are *moderately*, not tightly, converged (the climbing
image has not fully climbed, so each reported peak is if anything a slight *under*-estimate of the true
saddle). The +38–78 values are therefore approximate; the *sign* — barrier raised well above bare — is
robust and is very unlikely to flip on tighter convergence given how far above +17.47 the peaks sit.

**Not present in these committed bands:** the earlier "peak dE +150 to +700, with ~1e6 outliers" figures do
NOT appear in any committed `final_band.txt` (the maximum committed peak is +177, from the two
under-converged designs 7p1/12p0). Those earlier values came from a superseded run/parse (cf. the Knarr
interior-energy corruption noted in the archived K2 run) and are not part of this result.

## Conclusion
The provably-optimal uniform ±1 external-charge arrangement does **not** catalyse chorismate→prephenate at
any distance 2–15 Å. Concretely: designs either (a) fragment the substrate (close shells), (b) push it open
past baseline (far shells), (c) shatter the product and fail the GOCAT stationary-point screen (14/26), or
(d) admit a connected NEB path on which the barrier is **raised** above the bare value (anti-catalytic).
Where the path is clean (7p4, 8p1, 13p0, 15p0) the barrier is +38 to +78 kcal/mol vs +17.47 bare. The
reaction coordinate is not destroyed by these fields — it is made worse. Combined with the certified
geometry ladder, this closes the discrete/uniform ±1 design space and motivates a graded, net-balanced
fractional design.

## Why (mechanism)
The −2 dianion has two mutually-repelling carboxylates → it intrinsically favours the open geometry. A
uniform ±1 field at a fixed distance cannot both preorganise C1–C6 shut and preserve a low-barrier path:
strong enough to help means close enough to rupture; gentle enough not to rupture means too weak, and the
certified optimiser then resorts to net-negative imbalance that pries the substrate open. The consequence
is not the absence of a path but a path with a *higher* saddle — the field destabilises the TS relative to
the reactant rather than the reverse. Recovering catalysis needs a *shaped, graded, net-balanced* field:
strong exactly where needed, gentle elsewhere, net-neutral to avoid prying the substrate apart. This is the
empirical motivation for the next stage: certified FRACTIONAL (graded, net-balanced) charge design.

## Relation to GOCAT
We implemented GOCAT's external-charge/vdW-surface paradigm, its barrier-lowering objective, and —
critically — its stationary-point screen (Eq 3.2 RMSG, Eq 3.3 stabilisation): compute a barrier ONLY for
designs whose endpoints stay at true minima. Our designs either fail exactly that screen (product shatters)
or pass it and then yield an anti-catalytic on-path barrier — in both cases non-catalytic by GOCAT's own
criteria. Novelty vs GOCAT: certified-optimal charge placement (vs their genetic algorithm), and a stronger
negative regime (a −2 dianion is anti-catalysed / broken at all distances, where their neutral test systems
admitted working designs).

## Key methodological lesson (recorded in TIER2_KNOWN_ISSUES)
Barriers under a fixed external field MUST be computed on a CONNECTED reaction path (NEB) between
field-relaxed endpoints, NOT as a difference of two independently-relaxed endpoint energies — the latter is
dominated by the substrate's displacement through the fixed potential (gave physically-impossible values)
and is invalid. Endpoints must first pass a stationary-point screen (converged + intact). The on-path NEB
barrier is finite and readable for well-converged designs (this result); "no barrier" is a statement about
convergence, not chemistry, and must not be conflated with anti-catalysis.

## Reproducibility note (open)
The committed band outputs (`neb_screen/bands/<tag>/final_band.txt`, `nebP_<tag>.log`, endpoint xyz) are the
verified record. The NEB *runner* itself (the `neb_pass.py` / submit script) is not yet committed to the
code repo; committing it — with the exact image count, maxiter, and free_end setting — is required to make
this result fully reproducible from the repos alone.
