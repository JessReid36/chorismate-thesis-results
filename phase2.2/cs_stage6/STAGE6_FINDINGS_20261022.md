# Stage 6 findings: the first evaluation of optimiser designs by quantum chemistry

Written 22 October 2026, from the 22 frozen single points committed as
`phase2.2/cs_stage6/frozen/sp_outputs.tar.xz` and measured in `frozen/FROZEN_REPORT.txt`, plus the control's
converged reactant relaxation. Pre-registered by `cs_stage6/STAGE6_CRITERIA.txt` with `STAGE6_AMENDMENT1.txt`,
`STAGE6_ERRATUM1.txt`, `STAGE6_ERRATUM2.txt` and `relax/ADDITIVITY_RUNS.txt`.

**Nothing in this file is a barrier and none of it is quoted as a result.** Every number is an effect at a fixed
geometry, which is the quantity the MILP's score estimates. The catalytic verdict remains A2.5's relaxed chain.

## What this is, and what it is not

This is the first time designs from `cs_opt_milp.py` have been judged by anything other than the linear score that
produced them. The development-set runs (`cs_stage5/exploratory/`) were code tests, labelled exploratory and never
quoted. Stage 6 ran the committed optimiser on one frame's real grid, real L and real A column, and measured what
its designs actually do with B3LYP-D3BJ/def2-SVP.

It is **not** a validation of the design approach, and what follows is **not** only fine-tuning. Finding 8 below is a
gap in what the score optimises, not a parameter that needs adjusting.

## What passed before anything was interpreted

- All 22 runs terminated normally, SCF converged, 118 electrons in the QM region, coordinates echoed as generated.
- The MM point-charge count ORCA reports equals each arrangement's sphere count; the control reports no QM/MM
  section at all.
- Every input unchanged since generation (141 entries in `relax/INPUT_CHECKSUMS.sha256`).
- **The control's two energies equal the in vacuo energies the A-matrix job computed for this frame at these
  geometries, to 2.9e-10 and 1.4e-10 Eh.** The A column's single points and the control are the same method, basis
  and geometry reached by two independent routes. This is the check the rest rests on, and it also settles that the
  control being a plain QM job rather than QM/MM with an empty MM region costs nothing.
- The bare substrate's frozen barrier is 18.4610 kcal/mol, matching `A_REPORT.txt`.

## Finding 1. The linear score is conservative, and systematically so

| design | n | ddE(frozen) | score | measured - predicted |
|---|---|---|---|---|
| S6-P | 1 | -7.676 | -6.678 | -1.00 (15 %) |
| S6-2 | 2 | -12.384 | -11.218 | -1.17 (10 %) |
| S6-3 | 3 | -14.727 | -12.857 | -1.87 (15 %) |
| S6-5 | 5 | -18.161 | -15.620 | -2.54 (16 %) |
| S6-10 | 10 | -21.816 | -18.055 | -3.76 (21 %) |
| S6-20 | 20 | -24.826 | -19.654 | -5.17 (26 %) |

Every design does better than its own prediction. The gap is polarisation, which decision O1 deliberately left out
of the linear score, and it grows with n. For scale, decision O6 allows 15 % for method-and-basis uncertainty, so
this bias is comparable to or larger than that allowance from n = 3 upwards.

Per sphere it concentrates where the field is strongest: site 1690 (+1, a = -6.68) deviates by -1.00 on its own,
while sites 678 and 540 deviate by +0.22 to -0.10.

## Finding 2. First-order additivity holds

S6-2: measured -12.384, sum of its one-sphere effects -12.000, error **-0.38 kcal/mol (3.1 %)**.
S6-3: measured -14.727, sum -13.825, error **-0.90 kcal/mol (6.1 %)**.

So the *structure* of the score - a sum of independent per-site terms - is sound, and the underprediction of
Finding 1 is not spheres interfering with one another. Non-additivity grows slowly with n.

## Finding 3. The L matrix is exact

Across all nine sphere arrangements the measured Lennard-Jones contribution (ORCA's own `(MM)` energy difference)
differs from the score's `sum L` by at most **0.0000 kcal/mol**. `cs5_grid.py` computes L classically from the same
Amber N parameters ORCA uses, so this checks the grid's arithmetic and the force field it was handed, not any
physics - but it was never checked before.

## Finding 4. At a fixed geometry the Lennard-Jones wall buys nothing

Same site, same +1 charge:

| | measured | predicted | deviation |
|---|---|---|---|
| S6-P, bare point charge | -7.6757 | -6.6778 | -0.9979 |
| ADD-s1690, LJ sphere | -7.1128 | -6.1149 | -0.9979 |
| difference | **-0.5629** | **-0.5629** | - |

The difference is exactly L, to zero, and the electronic deviation is identical to four decimals - necessary, since
the Lennard-Jones term never enters the QM Hamiltonian, but measuring it confirms the whole QM/MM setup. **The wall
costs 0.56 kcal/mol of barrier lowering at a fixed geometry and its entire value is in the relaxation**, where
WP4's bare charge collapsed onto O2 at 0.95 A and its sphere stopped at 2.54 A.

## Finding 5. The added gradient is large, and worst for the largest designs

Added gradient on the substrate at the reactant, kcal/mol/A:

| design | n | RMS over 72 | worst atom | which | median atom | atoms above 20 |
|---|---|---|---|---|---|---|
| S6-P | 1 | 4.99 | 26.8 | O3 | 4.46 | 1 of 24 |
| S6-2 | 2 | 7.09 | 30.3 | C10 | 4.71 | 3 |
| S6-3 | 3 | 7.77 | 33.9 | C10 | 5.39 | 4 |
| S6-5 | 5 | 10.19 | 38.7 | C10 | 8.14 | 7 |
| S6-10 | 10 | 12.17 | 52.6 | C10 | 8.59 | 7 |
| S6-20 | 20 | 13.27 | 55.9 | C10 | 11.95 | 7 |

Converting the only published figures to the same RMS convention (Dittner's frozen-path norm of about 11.3 is 1.33
as an RMS over 72 components), these designs put **3.7 to 10 times** more added gradient on the substrate than the
designs he reported as frozen-path.

Note this contradicts the natural expectation that many small charges "surrounding" the substrate would balance
their pulls: the optimiser is not building a shell. It places charge where V_TS - V_R is most negative, and all
twenty best single sites lie within 3.25 A of one another - one pocket. With more spheres it finds more such
pockets, each adding its own pull, and the budget constrains sum q^2 but says nothing about net force.

## Finding 6. At n = 10 and n = 20 the frozen barrier is negative

The frozen barrier with the design present: +10.79 (n=1), +6.08 (2), +3.73 (3), +0.30 (5), **-3.36 (10)**,
**-6.37 (20)** kcal/mol. At n >= 10 the transition-state geometry sits *below* the reactant geometry. That is not a
lowered barrier; it means frame 42436's stationary points are no longer stationary points of the perturbed system.
Criterion (ii) exists for this. B = 2.0 e^2 is the code-test value and not the calibrated budget, so part of this is
an uncalibrated budget rather than a property of the method.

## Finding 7. The control's own descent dwarfs the barrier

The control's reactant, relaxed in vacuo from its QM/MM geometry (Cartesian, 95 cycles, converged):

| | |
|---|---|
| energy drop | **-33.816 kcal/mol** |
| centroid displacement | 0.188 A |
| rigid rotation | 8.33 deg |
| internal RMSD | **1.405 A** |
| largest atom displacement | 2.777 A (O1) |
| C1-C6 (forming) | 3.225 -> **4.385 A** (+1.160) |
| O3-C4 (breaking) | 1.495 -> 1.434 A (-0.062) |

The frozen barrier is 18.46 kcal/mol, so **the control's descent is nearly twice the barrier it is the reference
for**. Set against WP4's one-sphere runs - `armb_free` moved 1.416 A internal RMSD and opened C1-C6 by 1.111 A *with*
a sphere - essentially all the motion WP4 attributed to its sphere is motion the bare substrate makes anyway.
Different frames, so not a subtraction, but the magnitudes are the point. This is what the criteria said the control
was for, "what WP4 lacked and what makes every number above interpretable", and it earned that on the first try.

The cause is structural: frame 42436's R and TS are stationary points of the full solvated enzyme under QM/MM, and
Stage 6 relaxes the 24-atom substrate in vacuo. The substrate is not being perturbed by a design so much as
returning to its own gas-phase surface from 33.8 kcal/mol up. C4 rejected NEB image 0 as a reactant because "a
relaxation from such a start is dominated by the substrate falling towards its own minimum"; IRC endpoints of the
QM/MM system are not stationary points of the bare substrate, so the same objection lands anyway.

**Consequence for Loss**: the control's change is already subtracted inside ddE(relaxed), so the subtraction is not
the problem. The problem is that each bracket is a difference of numbers that each moved by about 30 kcal/mol, and
with 1.4 A of internal RMSD over 95 cycles a design may steer the substrate into a different local minimum than the
control reaches, in which case ddE(relaxed) compares different species and Loss is not a quantity. Each design's
relaxed geometry must therefore be compared against **the control's relaxed geometry**, not only against the frozen
start.

## Finding 8. The dianion is not electronically bound in vacuo, and the designs make it worse

HOMO of the 24-atom dianion at the reactant geometry, with each design's charges present:

| design | n | HOMO (eV) | bound? |
|---|---|---|---|
| S6-C, bare | 0 | +2.278 | no |
| **S6-P / ADD-s1690** (+1 at site 1690) | 1 | **-0.243** | **yes** |
| ADD-s540 (-0.65) | 1 | +4.269 | no |
| ADD-s678 (-0.76) | 1 | +4.472 | no |
| ADD-s678 (-1.00) | 1 | +5.205 | no |
| S6-2 | 2 | +2.809 | no |
| S6-3 | 3 | +4.229 | no |
| S6-5 | 5 | +2.904 | no |
| S6-10 | 10 | +6.404 | no |
| S6-20 | 20 | +4.550 | no |

A positive HOMO means the highest electrons are not bound; the calculation only looks well-behaved because
def2-SVP has no diffuse functions to let an electron leave. **Only the single positive sphere at Arg90's own
position binds the dianion.** Every design the optimiser produced makes it less bound, the worst being the negative
spheres it places at positive-a sites. `STAGE6_CRITERIA.txt` already notes that net-negative arrangements push the
orbital up (Stage 4c); this is that effect measured on the real designs, and it is large.

**Why the optimiser does this is structural, not a bug.** The score is built on `a = V_TS - V_R`, a *difference* of
potentials, and a difference is blind to absolute electrostatic stabilisation. The score cannot see that positive
charge near a dianion is what holds the species together; it sees only which sign lowers the barrier at each point,
and at site 678 (a = +5.16) that is negative charge. The feature that is physically essential, and that the enzyme
supplies through Arg90, Arg7 and Arg63', is the one the score under-weights by construction.

**This is a caveat on every number above.** A species whose HOMO is +4 to +6 eV at this basis is basis-set-bound;
its energy is a well-defined variational minimum within the basis, and differences at the same geometry and basis
remain meaningful as such, but the physical reading is weakened and an applied field acts on loosely-held density
exactly where basis-set artefacts bite hardest. Part of what Finding 1 attributes to polarisation may be the basis
set holding unbound density differently in different fields. The diffuse-basis diagnostic recorded in
`STAGE6_DIAGNOSTIC1_20261022.txt` tests this.

## Finding 9. The absolute electrostatics is already computed, and predicts Finding 8

`cs5_amatrix.py` runs `orca_vpot` at every grid site for R, TS and P, then takes differences and discards the
absolutes. The absolute potentials are therefore already in the committed outputs. Reading them back
(`phase2.2/cs_stage6/absolute_potentials/V_f42436.tsv`, extracted here), `(V_TS - V_R) * H` reproduces the committed
A column to 5e-7 kcal/mol per e, which confirms the reading.

Define a design's absolute electrostatic stabilisation of the reactant as `sum_i q_i V_R(r_i)`. Across the seven
arrangements:

| design | n | sum q*V_R (kcal/mol) | HOMO (eV) | net q |
|---|---|---|---|---|
| S6-P | 1 | -120.09 | -0.243 | +1.00 |
| S6-5 | 5 | -21.65 | +2.904 | +0.10 |
| S6-2 | 2 | -3.78 | +2.809 | 0.00 |
| S6-C | 0 | 0.00 | +2.278 | 0.00 |
| S6-20 | 20 | +44.46 | +4.550 | -0.24 |
| S6-3 | 3 | +49.22 | +4.229 | -0.41 |
| S6-10 | 10 | +121.22 | +6.404 | -0.98 |

**Correlation of the HOMO with `sum q*V_R`: r = +0.982** (net charge alone: r = -0.976).

The term is **linear in q**, so it drops into the MILP with no change to the solver's structure: either an extra
objective term, or a hard constraint `sum_i h_i q_i <= bound` with `h_i = V_R(r_i) * H`, requiring no new HPC work
at all. It is preferable to a net-charge constraint because it is position-weighted: a +1 in Arg90's pocket is worth
far more than a +1 further out, and the constraint should know that.

Seven points is seven points. The correlation is offered as a reason to build the term and measure it properly, not
as a calibration.

## What is not established

- One frame. Everything here is frame 42436.
- B = 2.0 e^2 is a code-test value. Findings 5 and 6 would differ under the calibrated budget.
- No relaxed quantity is measured yet: Loss, the two survival criteria, G0 and kappa all wait on the relaxations,
  and Finding 7 raises a real question about whether Loss as defined is interpretable at all. Decision O2's
  pre-registered fallback, that no threshold could be fixed, is a live outcome.
- The relaxation protocol itself is unresolved: ORCA refuses `OptTS` with `coordsys cartesian`, so Erratum 1's
  protocol cannot be run on the TS side as written. See `STAGE6_ERRATUM3` when it is written.
- Finding 9's correlation is seven designs on one frame, with a first-order proxy for an orbital energy.

## What follows

1. The diffuse-basis diagnostic, which decides how much of Findings 1 to 6 survives a basis that lets loosely-held
   density go.
2. A decision on the relaxation protocol and on whether Loss is worth 750 core-hours (Findings 6 and 7).
3. If the diagnostic holds, an absolute-electrostatics term in the optimiser (Finding 9) - a change to what is
   optimised, not a tuning of it, and therefore a new pre-registration rather than an amendment.
