# Design decision: reactant conformer choice for the charge search

**Status:** open modeling choice, leaning to the two-step approach below. Not a physical
necessity — a deliberate scoping decision with a stated rationale.

## The question
Should the deterministic charge-placement search start from / constrain to the
**lowest-energy (non-reactive, extended pseudo-diequatorial)** conformer, or the
**reactive (folded pseudo-diaxial chair, near-attack C1-C6 ~3 A)** conformer?

The trade-off is **tractability vs ambition**.

## Argument for reactive-start (constrained geometry)
1. It is the conformer that actually reacts (extended conformers cannot reach the TS
   without first folding).
2. The barrier measured against it is the clean *chemical* barrier, not conflated with
   conformer-folding energy.
3. Matches how the enzyme works, and how our own bare-substrate geometry was obtained
   (inherited from the enzyme reaction path; ~3.12 A near-attack baked in).
4. **Decisive practical point:** it makes the cheap Sigma(q*dV) / CAMM-DTSS electrostatic
   surrogate *valid*. Fixing the geometry removes the confound that made the Phase 1
   surrogate FAIL on free geometry (Pearson r = -0.839 — field designs distorted the
   substrate, so an electrostatics-only score on a moving substrate could not rank them).
5. Clean controlled experiment: one variable (the charges).
6. It is the two-layer architecture made literal — a neutral cradle supplies the held
   geometry, charges are designed independently for it.

## Argument for lowest-start (unconstrained geometry)
1. It is the physically prevalent species (substrate is mostly non-reactive in solution
   and before binding).
2. A genuinely good charge design might need to do conformer-selection *itself* (pull the
   substrate into the reactive chair). Constraining to the reactive conformer FORECLOSES
   discovering such self-organizing designs — which is exactly what a coupled method
   (e.g. GOCAT) could find and our constrained method cannot.
3. It tests the stronger *unconditional* claim ("these charges catalyse the free
   substrate") rather than the conditional one ("given the geometry is held").
4. It sits better with Claeyssens/Mulholland 2011 (Org. Biomol. Chem., DOI
   10.1039/c0ob00691b), which concludes there is NO unique reactive conformation and that
   catalysis is TS stabilisation per se, not NAC / reactive-conformer selection. Anchoring
   on "the reactive conformer is special" leans against the TS-stabilisation camp.
5. It avoids baking in the confinement free-energy-cost artifact: flat-bottom walls impose
   the near-attack geometry "for free", omitting the real cost of achieving it (the same
   cost a PMF would capture).
6. It is closer to a real deployed catalyst, which meets the substrate non-reactive and
   must do everything.

## Recommended resolution: two-step approach
- **Step 1 (screen, constrained):** rank charge arrangements affordably using the cheap
  surrogate on the CONSTRAINED reactive geometry (valid because geometry is fixed),
  e.g. via MILP over a grid.
- **Step 2 (validate, unconstrained):** take the top hits and test them UNCONSTRAINED
  starting from the non-reactive minimum, to see whether any of them ALSO hold the
  geometry / drive the substrate reactive on their own — i.e. discover a self-organising
  design by validation rather than exhaustive search.

This buys the tractability of reactive-start for the *search* while still checking the
ambitious unconstrained question for the *winners*, so self-organising designs are not
fully foreclosed — we just do not pay to search for them exhaustively.

**Defensible thesis framing:** "constrained screening for tractability + unconstrained
validation of top hits for realism," with the fully-unconstrained self-organising charge
design stated honestly as the harder open problem beyond our screen.

## Concrete next experiment
Re-run the Phase 1 Sigma(q*dV) surrogate test, but evaluate the potential on the
**constrained reactive geometry** rather than the free relaxed geometry. If the ranking
correlation goes positive (vs the -0.839 obtained on free geometry), that confirms
constraining rescues the surrogate's ranking power and validates Step 1 of the two-step
approach — putting the tractable MILP charge search back on the table, scoped to the
constrained (two-layer) regime.
