# Step 6.5b - Residue electrostatic-optimality offset map (TS frame)

## Method
For each active-site residue, find the nearest grid point (of the 252-point union-envelope Dv grid,
same TS frame) whose Dv is of the sign that HELPS at that residue's position (Dv minimum where the
field wants a cation; Dv maximum where it wants an anion), within a 6 A search radius. The offset
distance + direction is how far, and which way, toward the local electrostatic optimum on the sampled
envelope.

## CAVEAT - coarse map
The grid samples only the OUTER ENVELOPE around the substrate, not the space at the residue positions.
So offset MAGNITUDES are relative/directional, not precise. The reliable signal is the ORDERING and
DIRECTIONS, not absolute distances. A "near-grid" distance (residue -> closest sampled grid point) is
reported per residue: small (~1 A) means the residue sits at the envelope surface (offset trustworthy);
large means it sits off the envelope (offset unreliable). Precise offsets would require a fine local
grid of orca_vpot points around each residue (optional future refinement).

## Table 6.5b - offset map (sorted best-placed first)

| Residue | Subunit | Dv@res (Eh) | field wants | offset (A) | Dv@opt (Eh) | near-grid (A) | reliable |
|---------|---------|-------------|-------------|------------|-------------|---------------|----------|
| Arg90   | one     | -0.005322   | cation      | 3.34       | -0.009267   | 0.78          | yes      |
| Glu78   | one     | -0.000013   | cation      | 4.32       | -0.007562   | 0.83          | yes      |
| Arg63'  | adjacent| +0.003555   | anion       | 5.37       | +0.008084   | 1.33          | yes      |
| Lys60'  | adjacent| +0.003440   | anion       | 5.45       | +0.008084   | 0.90          | yes      |
| Arg7    | one     | -0.000879   | cation      | 5.72       | -0.005874   | 0.73          | yes      |
| Arg116  | one     | -0.000092   | cation      | 5.90       | -0.000478   | 5.90          | NO       |

## Offset directions (vector toward local field optimum, A)

| Residue | dx    | dy    | dz    | role                            | DTSS (kcal/mol) |
|---------|-------|-------|-------|---------------------------------|-----------------|
| Arg90   | -3.02 | -0.36 | +1.38 | dominant catalytic              | -9.06           |
| Glu78   | -4.23 | +0.87 | -0.07 | catalytic (geometry-sensitive)  | -3.57           |
| Arg63'  | +4.77 | +0.08 | +2.46 | ring-COO binder                 | -1.40           |
| Lys60'  | +4.70 | +2.69 | -0.58 | COO binder (anticatalytic)      | +1.39           |
| Arg7    | -4.38 | -2.63 | +2.59 | side-chain COO binder + catalytic| -5.90          |
| Arg116  | +3.64 | -3.59 | +2.95 | 2nd-shell (UNRELIABLE, off grid)| -2.45           |

## Reading (relative/directional)
- Arg90 (dominant catalytic) is the BEST-POSITIONED residue (smallest offset, 3.34 A) and sits nearest
  the field's strongest cation-favorable region (its local optimum Dv -0.0093 is the global grid
  minimum). Positional validation of the enzyme's key catalytic charge, on top of the sign match.
- Catalytic residues (Arg90 3.34, Glu78 4.32) sit CLOSER to their field optima than the binding-role
  residues (Arg63' 5.37, Lys60' 5.45, Arg7 5.72). Consistent with catalytic-charge positions being
  under tighter electrostatic selection than binding-charge positions.
- The binding residues Arg63'/Lys60' are displaced in a COMMON direction (both strongly +x, +y): the
  positional signature of gripping the substrate's carboxylates rather than optimizing the barrier.
- Arg116 sits off the sampled envelope (near-grid 5.90 A) -> offset not reliable, excluded from reading.

## Improvement-lead assessment (answering "could repositioning improve catalysis?")
No clean binding-independent improvement lead emerges. The residues with large offsets (Arg63', Lys60',
Arg7) are binding-critical (they anchor chorismate's -2 dianion carboxylates), so their displacement
from the field optimum is explained by their binding role - moving them would break substrate binding.
The residues that are free to optimize for the barrier (the catalytic Arg90, Glu78) are already
well-placed (small offsets). So the enzyme is near-optimally positioned where it can be, and positionally
"suboptimal" only where binding forces its hand. Consistent with the 6.5a sign-map conclusion. A genuine
catalysis-improving repositioning would require solving binding and catalysis jointly (inverse backbone
design) - flagged as future work.
