# W.n The optimised reactant ensemble

> Draft subsection for the Phase 1 chapter, to sit after the frame-selection
> section and before the reaction-path results. Section number to be assigned.
> All values trace to `05_qmmm/19_ensemble_harvest/reactant_summary.tsv` and
> `05_qmmm/12_frame_selection/selection_manifest.tsv`.

---

## W.n The optimised reactant ensemble

I optimised the reactant state of all fourteen selected frames under the same
QM/MM protocol before computing any reaction path, so that each barrier would be
formed between endpoints obtained by an identical procedure. The optimised
geometries are reported here in their own right, because the relationship
between the sampled and the optimised structures bears on how the barrier
ensemble should be interpreted.

Every optimisation converged. Convergence took 240 to 396 steps, corresponding
to walltimes of 6 h 17 min to 10 h 6 min on eight cores. Table W.n.1 gives the
reacting-bond distances of each optimised reactant alongside the values measured
in the molecular-dynamics frame from which it started.

**Table W.n.1** Reacting-bond distances in the selected frames and after QM/MM
optimisation. Selection values from `selection_manifest.tsv`; optimised values
from `reactant_summary.tsv`, measured on the extracted 24-atom QM region.

| Frame | Form C1–C6 at selection (Å) | Break O3–C4 optimised (Å) | Form C1–C6 optimised (Å) | Steps |
|---|---|---|---|---|
| 2450 | 3.407 | 1.472 | 3.295 | 363 |
| 4085 | 3.149 | 1.465 | 3.329 | 262 |
| 5680 | 3.032 | 1.461 | 3.281 | 261 |
| 7310 | 3.288 | 1.469 | 3.181 | 275 |
| 8170 | 3.434 | 1.472 | 3.243 | 268 |
| 9025 | 3.496 | 1.477 | 3.353 | 291 |
| 9900 | 2.945 | 1.473 | 3.143 | 280 |
| 10775 | 3.566 | 1.470 | 3.472 | 305 |
| 11630 | 3.152 | 1.487 | 3.177 | 261 |
| 12485 | 3.461 | 1.484 | 3.155 | 240 |
| 14155 | 3.284 | 1.477 | 3.285 | 295 |
| 15825 | 3.385 | 1.466 | 3.347 | 396 |
| 17505 | 3.387 | 1.473 | 3.260 | 265 |
| 19185 | 2.990 | 1.480 | 3.107 | 270 |

### The two reacting bonds behave differently

The breaking ether bond is effectively invariant across the ensemble. Its
optimised length spans 1.461 to 1.487 Å, a range of 0.026 Å with a standard
deviation of 0.007 Å. That is the scale of the optimisation convergence
criterion rather than of any structural variation, so the fourteen frames agree
on this coordinate to within the resolution of the method.

The forming carbon–carbon distance behaves differently. It spans 3.107 to
3.472 Å, a range of 0.365 Å and a standard deviation of 0.100 Å, fourteen times
the spread of the breaking bond.

The asymmetry is a property of the bound state rather than of the optimisation.
A bound substrate has a covalent ether bond whose length is set by its own
electronic structure and is largely insensitive to the surroundings, and a
forming bond that does not yet exist, whose length is set by how the active site
holds two parts of the molecule relative to one another. The ensemble therefore
measures conformational variation in the active site, expressed almost entirely
through the coordinate that has not yet become a bond.

### Optimisation compresses the sampled variation without removing it

The frames were selected across a wider range than they occupy after
optimisation. At selection the forming distance spanned 2.945 to 3.566 Å, a
range of 0.621 Å with a standard deviation of 0.199 Å; after optimisation the
range is 0.365 Å and the standard deviation 0.100 Å. Optimisation therefore
halved the spread of this coordinate.

The compression is not an erasure. The optimised forming distance correlates
with the value measured in the starting frame, with a Pearson coefficient of
+0.589 (exact permutation test, p = 0.026, n = 14). A frame sampled with its
reacting carbons further apart relaxes to a structure in which they remain
further apart. The active site narrows the distribution of near-attack
geometries it will accept, and does not impose a single one.

This matters for the barrier ensemble that follows. Had the optimisation
converged every frame to a common geometry, the barriers would differ only
through the surrounding protein and solvent configuration, and a single frame
would be nearly as informative as fourteen. Because a measurable part of the
sampled variation survives into the optimised reactants, the barrier
distribution reported below carries genuine conformational sampling, and its
width should be read as such.

No relationship was found between the Arg90–O13 contact distance measured at
selection and the optimised forming distance (r = +0.067, p = 0.821), nor
between that contact and the optimised breaking bond (r = +0.345, p = 0.226).
The near-attack geometry and the electrostatic contact vary independently in
this ensemble, at least at this sample size.

### W.n.1 Pipeline of Operations

`[FIGURE W.n.1 — flowchart of the reactant ensemble. Inputs: the frame manifest
and the extracted restart files. Steps: per-frame QM/MM reactant optimisation →
convergence check → harvest of geometry and energies → ensemble summary. A
branch from each converged reactant feeds the restrained scan that follows. No
data file required; this is a schematic.]`

- `19_ensemble/frame_XXXXX/reactant_opt.inp` — ORCA QM/MM input for one frame,
  declaring the 24-atom QM region as `QMAtoms {6207:6230}` and a movable region
  of 1959 atoms, with the force field supplied by
  `complex_solvated.ORCAFF.prms`. Runs an L-BFGS minimisation.
- `19_ensemble/frame_XXXXX/reactant_opt.pbs` — batch driver for one frame.
  Reports `REACTANT_OPT_PASS` on convergence.
- `step19a_ensemble_prepare.sh` — builds a frame directory from the selection
  manifest and the extracted restart file. Outputs `reactant_opt.inp`,
  `reactant_opt.pbs`, `neb.inp` and `neb.pbs`.
- `step19d_harvest.py` — extracts the committable record from each converged
  optimisation. Parses `QMAtoms` from the input, applies it to
  `reactant_opt.pdb`, and outputs `reactant_qm.xyz` per frame plus
  `reactant_summary.tsv` carrying the QM/MM, QM and MM energies, step count,
  walltime and reacting-bond distances.
- `19_ensemble_harvest/reactant_summary.tsv` — the ensemble table from which
  Table W.n.1 is drawn.

---

## Notes on this draft

1. **A correction to an earlier reading.** At an intermediate stage, with five
   frames optimised, the correlation between selection-time and optimised
   forming distance was +0.073 with p = 0.894, and I recorded that the
   optimisation appeared to erase the sampled geometry. At fourteen frames the
   correlation is +0.589 with p = 0.026. The earlier reading was an artefact of
   the small sample and should not appear anywhere in the thesis.
   `PHASE1_ENSEMBLE_NOTES.md` currently carries it and needs correcting.

2. **Frame 820 is excluded from this table.** The fourteen frames here are those
   optimised as part of the ensemble. Frame 820 was optimised earlier, as the
   original Phase 1 calculation, under the same protocol but outside
   `19_ensemble/`. Its optimised distances are 1.464 and 3.251 Å, which fall
   within the ranges above. Whether to fold it into this table or keep it
   separate is a presentation decision; folding it in would give n = 15 and the
   statistics above would need recomputing.

3. **Energies are deliberately absent from Table W.n.1.** The optimised QM/MM
   total energies span roughly 900 kcal mol⁻¹ across the ensemble, because each
   frame carries a different solvent configuration in the classical term.
   Absolute energies are therefore not comparable between frames and only
   differences within a frame are meaningful. They are recorded in
   `reactant_summary.tsv` but would mislead if tabulated here.

4. **Statistical method.** Correlations are Pearson coefficients with p-values
   from a permutation test over 200,000 random orderings. At n = 14 the test is
   adequately powered for a correlation of this size but not for a small one, so
   the two null results reported for Arg90 should be read as an absence of
   evidence rather than as evidence of absence.
