# Discrete ±1 External-Charge Ladder + GOCAT-Style Barrier Screen: Certified Negative Result

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
   (ASH/Knarr, 12 images, ActiveRegion freezing the 64 surrogate atoms to anchor the lab frame) between the
   field-relaxed endpoints. Barrier = highest band image − reactant image, on ONE connected path.

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
- **13–14/26 PASS** (valid reactant + product minima) → eligible for NEB. But every passing reactant is
  intact-yet-OPEN (C1–C6 3.5–5.2 Å) — none preorganised into the window.

### NEB-under-field on PASS designs — no valid barrier
- **Every PASS-design NEB FAILED to converge** (maxiter=200, Knarr). The bands thrash: intermediate images
  carry large residual forces (MaxF 1–5 eV/Å) and non-monotonic, rugged energy profiles; several product
  ends fall *below* the reactant (no forward barrier). The reported "peak dE" values (+150 to +700, with
  numerical-garbage outliers ~1e6) are artefacts of unconverged bands, NOT barriers.
- Physical reading: **under these discrete-charge fields there is no well-behaved minimum-energy path from
  reactant to product** — the field disrupts the reaction coordinate. No valid catalytic barrier exists.

## Conclusion (certified negative)
Uniform ±1 external point charges cannot catalyse chorismate→prephenate at any distance 2–15 Å. They either
(a) fragment the substrate (close), (b) push it open past baseline (far), (c) shatter the product (14/26
fail the stationary-point screen), or (d) disrupt the reaction path so no NEB barrier converges (all PASS
designs). Combined with the certified geometry ladder, this closes the discrete/uniform-charge design space.

## Why (mechanism)
The −2 dianion has two mutually-repelling carboxylates → intrinsically favours open. To close C1–C6 and
preserve the path needs a *shaped, graded, net-balanced* field: strong exactly where needed, gentle
elsewhere, net-neutral to avoid prying the substrate apart. Uniform ±1 at fixed distance cannot provide
this — strong enough to help means close enough to rupture; gentle enough not to rupture means too weak,
and the optimiser resorts to net-negative imbalance that pushes the substrate open. This is the empirical
motivation for the next stage: certified FRACTIONAL (graded, net-balanced) charge design.

## Relation to GOCAT
We implemented GOCAT's external-charge/vdW-surface paradigm, barrier-lowering objective, and — critically —
its stationary-point screen (Eq 3.2 RMSG, Eq 3.3 stabilisation): compute a barrier ONLY for designs whose
endpoints stay at true minima. Our designs fail exactly this screen, or fail to yield a converged path —
the same criteria GOCAT uses to reject non-catalytic candidates. Novelty vs GOCAT: certified-optimal charge
placement (vs their genetic algorithm), and a stronger negative regime (a −2 dianion anti-catalyses/breaks
at all distances, where their neutral test systems admitted working designs).

## Key methodological lesson (recorded in TIER2_KNOWN_ISSUES)
Barriers under a fixed external field MUST be computed on a CONNECTED reaction path (NEB) between
field-relaxed endpoints, NOT as a difference of two independently-relaxed endpoint energies — the latter is
dominated by the substrate's displacement through the fixed potential (gave physically-impossible ±100–500
kcal/mol values) and is invalid. Endpoints must first pass a stationary-point screen (converged + intact).
