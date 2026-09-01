# Continuum (CPCM eps=4) vs vacuum: effect on the bare dianion geometry

**Method:** the same bare 24-atom chorismate dianion reactant (charge -2, singlet;
enzyme-inherited folded geometry, C1-C6 = 3.538 A) was relaxed under four conditions
(ORCA 6.0.1, B3LYP-D3BJ/def2-SVP/def2-J/RIJCOSX, serial). C1-C6 = forming-bond distance
(atoms 0,12); O3-C4 = breaking ether bond (atoms 7,8).

| Condition | C1-C6 (A) | Outcome |
|---|---|---|
| bare + CPCM eps=4 | 3.537 | folded / near-attack |
| bare + vacuum | 4.386 | opened |
| Arg90 charges + CPCM eps=4 | 4.753 | opened |
| Arg90 charges + vacuum | 4.860 | opened |

## Finding 1: the continuum stabilises the folded (near-attack) geometry
On the bare substrate, CPCM eps=4 holds the folded reactive geometry (3.54) whereas in
vacuum the substrate opens (4.39). Mechanism: in vacuum the two carboxylates of the -2
dianion repel with nothing to screen them, so the substrate opens toward the extended,
less-reactive form; the continuum screens that repulsion and preserves the fold. This is
the unscreened-carboxylate-repulsion effect (cf. Guo et al. PNAS 2001; Hur & Bruice: the
reactive pseudo-diaxial conformer is high-energy partly *because* of carboxylate
repulsion, worse when unscreened). **This justifies the CPCM eps=4 choice for the dianion.**

## Finding 2: the Arg90 charges open the substrate in BOTH environments
Adding the Arg90 design charges opens the substrate under CPCM (4.75) *and* in vacuum
(4.86). Crucially, under CPCM -- which holds the *bare* substrate folded at 3.54 -- the
charges still push it open to 4.75. So the charge-driven opening is **intrinsic to the
charges, not a continuum artifact**; the continuum is exonerated as the cause.

This independently reproduces the Route B finding (the Arg90 charge, unconstrained, drives
the substrate 3.12 -> 3.88 into a non-reactive open well; the k=800 pin failed to hold it)
and shows the effect is **environment-independent**. It directly confirms the honest
two-layer framing: the Arg90 charge REQUIRES geometric confinement (walls/cradle) to
catalyse -- without confinement it opens the substrate regardless of solvation; only the
held near-attack geometry lets the charge lower a proper barrier (~6-7 kcal/mol).

## Caveat on the ">3.6 A" collapse label
The analysis script flags anything > 3.6 A as "collapse", which lumps two *different*
phenomena: (i) bare + vacuum opening (4.39, mild, unscreened carboxylate repulsion) and
(ii) charge-driven opening (4.75-4.86, the Arg90 drive). Only bare + CPCM (3.54) stays
genuinely near-attack.

**Script:** `continuum_control_test.py` (code repo). Note: earlier partial runs of this
test failed via the HPC ORCA/mpirun startup bug (geometry echoed back unchanged = the opt
never ran); the MPI-fixed serial run gave the divergent results above. Lesson: an opt that
"fails in Startup" and returns the input geometry unchanged did not actually run.
