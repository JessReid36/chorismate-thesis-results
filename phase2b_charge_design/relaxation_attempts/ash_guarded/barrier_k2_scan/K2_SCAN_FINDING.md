# K2 relaxed-scan barrier (1D O3-C4) — dissociative-ridge artifact + mechanistic hypothesis

## Result
1D relaxed scan of the breaking bond O3-C4 (1.45 -> 3.00 A, 0.10 step), MM molecular-surrogate K2
field (QM -2, guanidinium/formate + LJ), ActiveRegion=QM. Reactant ref E0 = -837.37630 Eh.
Profile crests at O3-C4 = 2.55 A, +36.5 kcal/mol (vs +17.47 bare-substrate Phase-1 baseline).

## Why this is NOT the barrier: the scan found a DISSOCIATIVE ridge, not the concerted TS
At the scan peak, C1-C6 (the FORMING bond) = 6.084 A - larger than reactant (5.0) or product (1.57).
The concerted Claisen TS has C1-C6 ~2.5 A (Phase-1: O3-C4 2.11 / C1-C6 2.53). So the 1D scan did NOT
find the pericyclic saddle; it climbed a path where the two reacting carbons FLEW APART.

## Mechanistic hypothesis (why the forming bond blows out under the field)
A 1D scan constrains only O3-C4 and lets everything else relax under the FIXED external field. Nothing
in that constraint drives C1-C6 to form. Breaking O3-C4 redistributes charge on the substrate; K2's
field (salt-bridged +1 guanidinium + the -1 sites) is most stabilised when the developing fragment
charges SPLAY APART to align with the external charges - i.e. the field actively favours a DISSOCIATIVE
response over puckering into the cyclic TS. The scan, having no incentive to close C1-C6, follows that
direction and rides a dissociative ridge.
IMPLICATION (to test, not assume): the external field may be RESHAPING the reaction coordinate - pushing
it toward a more dissociative / asynchronous (possibly stepwise-ionic) mechanism - not merely raising or
lowering a barrier on the enzyme's concerted path. This is consistent with OEEF literature (Shaik et al.):
strong oriented fields can switch concerted reactions to stepwise. If real, the "barrier" comparison to
the enzyme must account for a possibly DIFFERENT mechanism, not just a different barrier height.

## Consequence for method choice (do NOT seed TSOpt from the enzyme TS)
Seeding a TS optimisation from the Phase-1 (enzyme) TS would PRESUPPOSE the design produces an
enzyme-like concerted TS - which the C1-C6=6 blowout suggests it may not. That would assume the answer.
Unbiased routes that do not presuppose the TS geometry:
  - NEB-TS between the design's OWN relaxed reactant and product (running) - finds whatever TS the field
    actually produces (concerted / asynchronous / dissociative).
  - 2D scan (O3-C4 AND C1-C6) - maps the true surface, reveals concerted vs dissociative saddle.
Any TSOpt polish should be seeded from the NEB climbing image (the field's own TS), never the enzyme TS.

## Status
1D scan retained as a method-comparison reference ONLY (cheap but wrong for this concerted reaction:
found a dissociative ridge). +36.5 is NOT the K2 barrier. Barrier verdict deferred to NEB-TS (+ optional
2D scan). Files: k2_scan_profile.txt, k2_scan_traj.xyz, k2_scan.py, k2_scan_stdout.log.
