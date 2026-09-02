# Optimiser fork + write-up scope decision (2026-09)

Records a deliberate change in the optimiser framing, why, how the charge-search proceeds
from here, and which previously-committed material must be OMITTED (erroneous) vs KEPT AND
RECAST (right work, superseded framing) in the thesis Methods/Results.

---

## 1. THE FORK: drop the certificate; keep deterministic + white-box + novel

**Previous framing** (`code/phase2b_charge_design/PHASE2B_MASTER_STATUS.md` section E;
`NAMING_CROSSWALK.md` two-tier table): the headline novelty was a **certified** optimiser
with a provable optimality guarantee (gap = 0) -- "certified MILP" as *the* contribution,
with Tier 1 = certified screen.

**Decision (this fork):** the optimiser **does not need an optimality certificate.** The
requirements are now:
- **NOT black-box** -- rules out GA / GOCAT-style stochastic search AND opaque ML;
- **deterministic / white-box** -- the method and its scoring are inspectable and reproducible;
- **a novel way of solving this class of problem** given what already exists (GOCAT's GA,
  Sokalski's DTSS visualisation, Reiher's GdMC) -- novelty lives in the **approach**, not in
  the certificate.

**Why the certificate is not load-bearing:** the design workflow validates the top ~10
candidates per charge count with real NEB regardless. The optimiser only has to produce good
*candidates* for empirical verification; provable optimality of the *proxy* was never what
made a design catalytic (see `TIER2_KNOWN_ISSUES` D2: certified = proxy-optimal, NOT
catalysis-optimal). Dropping the certificate removes an over-claim, not a result.

**What survives unchanged:** the deeper thesis through-line in Master Status E is intact and
arguably *cleaner* -- a **deterministic, principled, white-box optimiser** for external-charge
catalyst design, contrasted with GOCAT's stochastic black-box GA. The empirical
TS-stabilisation-vs-over-polarisation trade-off still becomes the objective. We simply no
longer claim "provably optimal"; we claim "deterministic, inspectable, and novel, with
candidates verified by QM."

---

## 2. WHAT THE COMMITTED WORK ACTUALLY ESTABLISHED (the real state, not the old framing)

Reading the committed record (`PHASE2B_MASTER_STATUS.md` A/B), the settled physics is:
1. Discrete +-1 charges alone cannot recover near-attack geometry (too few -> open ~4 A;
   too many -> over-polarise / rupture).
2. A neutral steric cradle alone fails (walls leak; substrate opens along un-intercepted routes).
3. **Linear objective -> charges rail to +-1 (LP vertex) -> harsh field -> fragmentation.**
   The linearity itself drives the physical failure.
4. **Convex QP with a quadratic penalty -> gentle fractional charges** (max|q| 0.06-0.29,
   distributed) that do NOT fragment. Gentleness without a certificate requirement.
5. Distance, harshness and catalysis are coupled -- cannot be fixed by distance alone.

**Crucial caveat the committed notes already flag:** the destructive NEB results for the
raw +-1 designs were run on **field-relaxed (open) endpoints** and are explicitly labelled
"NOT a barrier number" (`phase2b .../barrier_k2_neb/NEB_FINDING.md`) -- dissociative-character
corroboration only, never clean barriers. So "charges make it worse" was never a clean
quantitative negative; it reflects harsh +-1 fields AND incoherent endpoints.

**Method-development side-note (2026-09):** a held-geometry barrier attempt that bolted the
OEEF/capacitor charge sets onto the Arg90-held substrate reproduced exactly this known failure
mode (barrierless / dissociative, because those charges were positioned for their own relaxed
geometry, not the held one). Recorded so it is not repeated: do NOT mix a design's charges
with a different design's substrate geometry -- charges and geometry must be co-relaxed.

---

## 3. HOW THE CHARGE SEARCH PROCEEDS FROM HERE

The live thread is the optimiser that produces **gentle, non-destructive** designs and then
verifies them by QM -- no certificate needed, novelty in the formulation.

**Step 1 (next experiment):** a deterministic convex/regularised program that produces gentle
fractional charges -- e.g. proximity-weighted quadratic penalty (Sum w_i q_i^2, w heavier near
the breaking C-O bond) or an RESP-style hyperbolic restraint. Solve deterministically
(HiGHS / OSQP / Clarabel). This is white-box and inspectable; the novelty is casting
external-charge catalyst design as a *regularised deterministic program that encodes the
TS-stabilisation-vs-over-polarisation trade-off*, rather than a black-box GA over +-1 charges.

**Step 2:** RELAX the resulting gentle design on the substrate (co-relaxed, coherent inputs)
-- does C1-C6 reach the near-attack window [2.6, 3.5] WITHOUT rupture? This is the make-or-break
test of whether gentle fractional fields avoid the fragmentation that killed the +-1 designs.

**Step 3:** for designs that survive relaxation, take the top ~10 per charge count and compute
real NEB-CI barriers (the empirical verification that replaces the certificate).

**Step 4 (from the reactant-conformer decision):** the screen runs on the constrained reactive
geometry (surrogate valid because geometry fixed); top hits also tested unconstrained from the
non-reactive minimum to check for self-organising designs.

**Fallbacks (unchanged, still valid):** dipolar/active cradle (oriented net-neutral dipoles),
or publish the certified/deterministic **negative** result as itself a contribution -- external
charge/steric design hits a wall for this -2 dianion, established comprehensively.

---

## 4. WRITE-UP SCOPE: OMIT (erroneous) vs KEEP-AND-RECAST (superseded framing)

### 4a. MUST OMIT from Results (genuinely erroneous -- wrong numbers / artefacts)
Per `NAMING_CROSSWALK.md` "Superseded (NOT for final numbers)" + `TIER2_KNOWN_ISSUES` closed bugs:
- **All Phase-2 `*_realgeom` result dirs** (`03_dvpot_realgeom`, `05_select_realgeom`,
  `06_polarize_realgeom`) -- rode the **stale NEB-TS geometry** (2.173/2.547) instead of the
  validated OptTS (2.111/2.526); "every *_realgeom result was silently wrong until audited"
  (`TIER2_KNOWN_ISSUES` B4 CLOSED). Do NOT quote their numbers (the "+10.9 kcal/mol exceeds the
  enzyme" headline, the frozen -10.888/-11.354, polarised -12.201/-14.009, the K-sweep).
- **The mixed-region enzyme barrier 15.08** and the uncommitted **15.3** -- superseded by the
  freq-verified **+16.00** (`TIER2_KNOWN_ISSUES` B3 CLOSED). `notes/model_fidelity_validation_
  framework.md` still carries 15.3 + a stale cross-check triplet in BOTH repos -- FIX before quoting.
- **The +15.771 "frozen" bare barrier** -- superseded by **+17.47** (L0, validated geometry).
- **`shell_restricted_sweep.py`** and its conclusion -- retracted (misread the 1.7 A grid floor
  as an atom-centre distance; it is a vdW-surface distance).
- **All committed K>2 max-lowering barrier values as *results*** -- the frozen-density objective
  is a first-order expansion with no lower bound; K4/K6/K8 imply unphysical negative barriers.
  K=2 is the only charge count where the frozen prediction is physically meaningful
  (`TIER2_KNOWN_ISSUES` D3). The max-lowering column is a diagnostic ceiling, never a result.
- **The "more charges do worse" claim** -- retracted; it confused per-charge efficiency with
  total lowering (`step_7...md`).
- **Any statement that the shell-ladder / K2 NEBs "failed to converge" as a negative result** --
  the corrected reading (`SHELL_LADDER_NEB_CORRECTION.md`) shows clean single-peaked MEPs exist;
  and the K2 NEBs were on incoherent open endpoints, never valid barriers.

### 4b. RECAST (right work, drop only the certificate claim)
- **The certified-MILP framing** (`PHASE2B_MASTER_STATUS.md` E; `NAMING_CROSSWALK` two-tier
  "certified screen = THE novelty"): keep the *deterministic/white-box* optimiser and the
  separation-constraint-binds evidence, but re-cast the headline from "certified/provably
  optimal" to "deterministic, inspectable, novel formulation, QM-verified." The gap=0 machinery
  becomes a *property of the solver used*, not the thesis claim.
- **Solver choice** (HiGHS over CBC): keep as reproducibility/engineering detail, not as
  "certified" novelty.

### 4c. KEEP AS-IS (solid, correctly framed)
- Enzyme QM/MM barrier **+16.00** [retained-final], now fully raw-output-verifiable
  (reactant/TS/product .out all committed).
- Bare barrier **+17.47** (L0).
- Route B: charge + geometric confinement ~6-7 (6.40/7.23) under held near-attack geometry,
  as a **potential-energy ranking metric** with the deferred-PMF free-energy framing.
- Route B negative result: unrestrained fields raise the barrier (29.77 / 46.37).
- Substrate geometry results (continuum stabilises the fold; CPCM preserves-not-drives; reactant
  is the reactive CHAIR).
- The settled mechanistic physics (Master Status B): linearity -> harsh +-1 -> fragmentation;
  convex QP -> gentle fractional; distance/harshness/catalysis coupled.
- The enzyme-rediscovery / residue-agreement result (TS-frame pair: 5/6 sign agreement with
  Szefczyk DTSS; Arg90 dominant; Lys60' binding-at-catalytic-cost).
- Szefczyk 2004 as the direct precedent for the differential-potential object; GOCAT/GdMC as the
  stochastic foils the deterministic approach improves on.

---

## 5. ONE-LINE SUMMARY
Optimiser no longer needs a certificate; it must be deterministic, white-box, and a novel
formulation vs GOCAT, with candidates QM-verified. The `*_realgeom` numbers, the 15.08/15.3
enzyme barriers, the 15.771 bare barrier, the K>2 max-lowering "results", and the "more charges
worse" / "NEBs failed" claims are ERRONEOUS and omitted. The deterministic-optimiser work,
Route B, the geometry/continuum results, and +16.00/+17.47 are KEPT (certificate claim dropped).
