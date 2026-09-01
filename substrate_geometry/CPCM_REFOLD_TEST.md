# Does CPCM eps=4 DRIVE toward the reactive fold, or only PRESERVE it?

**Question:** the continuum-vs-vacuum test showed CPCM *holds* the folded reactive geometry
when the optimisation *starts* folded. But does CPCM genuinely stabilise the reactive fold
as a preferred minimum (i.e. would it fold an *open* structure), or does it merely preserve
whatever basin the optimisation starts in?

**Method:** took the vacuum-opened structure (C1-C6 = 4.386 A) and optimised it under
CPCM eps=4 (same level of theory).

**Result:** it stayed open -- C1-C6 = 4.386 -> **4.353** (did NOT re-fold to ~3.5).

## Conclusion
CPCM eps=4 does **not** drive the substrate into the folded reactive geometry; it only
**preserves** the fold if the optimisation starts there. There are (at least) two stable
minima under CPCM eps=4:
- the folded reactive chair (~3.5 A), where the enzyme-inherited geometry sits and stays;
- an opened conformer (~4.35 A), where the vacuum-opened structure sits and stays.

So the reactive reactant geometry used throughout this work is held reactive by **where it
came from** (the enzyme reaction path placed it in the folded basin) **plus** CPCM
preserving it -- **not** by CPCM stabilising the reactive fold as the preferred geometry.

## Implications
1. The inherited reactive geometry is more contingent than the single C1-C6 number
   suggests: CPCM alone is not a sufficient guarantor of the reactive geometry (a from-open
   optimisation gives a non-reactive open conformer that is *also* stable under CPCM).
2. This **strengthens the two-layer case**: explicit geometric confinement (cradle/walls)
   does real, necessary work that the continuum cannot substitute for. CPCM will not
   manufacture the reactive geometry -- it only preserves whatever basin you are in.
3. For the constrained-vs-unconstrained conformer choice (see
   `phase2_charge_design/REACTANT_CONFORMER_DECISION.md`): a fully *unconstrained*
   self-organising charge design would have to do all the folding work itself, since CPCM
   will not help fold the substrate.

**Script:** `cpcm_refold_test.py` (code repo).
