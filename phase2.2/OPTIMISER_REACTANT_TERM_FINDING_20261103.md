# The optimiser cannot see whether its barrier reduction is transition-state stabilisation

3 November 2026. Hand-written. Nothing computed. Read from committed code and a committed reference.

**This is a vulnerability, not a demonstrated defect.** No design in any pool has been shown to be
reactant-destabilising. The finding is that the formulation cannot distinguish the two cases, that
the method's source document documents the optimiser exploiting exactly that blindness, and that the
check costs no new quantum chemistry. Section 5 proposes it as a pre-registered diagnostic.


## 1. What the objective is

`chorismate-thesis-code/phase2.2/cs_opt_milp.py`, header, "WHAT IT OPTIMISES (O1, O5)":

    d_f = sum_i a_if q_i + sum_i L_if z_i

and "d negative means the transition state is stabilised more than the reactant, so the score is
MINIMISED."

`cs5x_dev_amatrix.py` line 8 defines the coefficient:

    a = (V_TS - V_R) x 627.5094740631, kcal/mol per e

So `a_if` is a **difference of two potentials**, and the reactant and transition state enter the
objective only through that difference. The optimiser is handed `a` and never sees `V_R` or `V_TS`
separately.


## 2. What the constraints are

The header's "THE RULES" block lists the complete rule set:

    sum_i z_i = n                                     exactly n spheres (O6)
    sum_i s_i <= B                                    the budget (O3), s_i standing in for q_i^2
    sum_{i in K} z_i <= 1   for each clique K         the 3.25 A spacing
    one cut per earlier design                        distinct designs (O7)

Four families: cardinality, budget, spacing, distinctness. **None of them references the reactant
term.** There is no constraint of the form "the reactant must not be destabilised".


## 3. Why that matters: the consequence is structural, not incidental

Minimising `sum_i a_if q_i` with `a_if = V_TS,f(r_i) - V_R,f(r_i)` selects sites with the most
negative `a`. A site reaches a large negative `a` in two different physical ways:

- `V_TS` strongly negative and `V_R` near zero: a positive charge there stabilises the transition
  state. This is differential transition-state stabilisation.
- `V_R` strongly positive and `V_TS` near zero: a positive charge there **destabilises the
  reactant**. The barrier falls by raising its foot.

`a` is identical in the two cases. The objective is indifferent between them, and because only the
difference is ever formed, the information needed to tell them apart is discarded before the solver
runs. This is not a missing constraint on a visible quantity; the quantity is not represented.


## 4. The method's source document documents this failure mode and restrains against it

`chorismate-refs/gocat_2.pdf`, Dittner's dissertation, on the Diels-Alder optimisations:

> "Either the R frame is enforced to be stabilized, ΔE_R <= 0 kcal mol^-1, by using an additional
> penalty that deteriorates worse candidate solutions during the search, or without such a penalty."

and:

> "Of course, always ΔE_TS < ΔE_R must hold (with negative stabilization energies) in order to
> generate the barrier decrease. **Without enforcing ΔE_R <= 0, there is a giant search space with
> candidate solutions exploiting the R destabilization with less (or no) TSS at all.**"

The example he gives (Figs. A.13, A.14) is a design whose barrier reduction comes from "the very
positively embedded H-atom from the R frame that serves as handle to destabilize this structure",
which he describes as "probably a case of overfitting" and on which he comments: "Whether this is
seen as a meaningful mechanism is quite another topic."

So the author of the method this project's optimiser descends from (a) found the unrestrained
objective degenerating into reactant destabilisation, (b) added an explicit penalty to stop it, and
(c) ran the two modes as "two qualitatively different GOCAT optimizations".

Note the asymmetry he draws: for the Menshutkin reaction he used no penalty because "no embedding
was intended or anticipated to ever destabilize the educt structures", whereas for Diels-Alder it
"conversely is true and even exploited by the GA". Which case the chorismate Claisen rearrangement
falls into is not established anywhere in this project's record.


## 5. Why this matters particularly for chorismate mutase

`chorismate-refs/ja049376t.pdf`, Szefczyk, Mulholland, Ranaghan & Sokalski, JACS 2004, 126,
16148-16159, abstract: TS stabilisation "by approximately -23 kcal/mol [MP2/6-31G(d)] **relative to
the bound substrate**", and this "contrasts with suggestions that catalysis by this enzyme arises
purely from conformational selection effects."

The literature position for this specific enzyme is that catalysis is genuine differential
transition-state stabilisation. A design that reaches its barrier reduction by destabilising the
reactant would therefore be off-mechanism for the target being mimicked, however good its `d`.


## 6. The check costs no new quantum chemistry

`cs5x_dev_amatrix.py` line 165 builds each column of `A` as

    (vpot(vpot_<f>_TS.out) - vpot(vpot_<f>_R.out)) * H

from two separate files. Those files are committed:

    phase2.2/cs_stage5/exploratory/dev_A/job/vpot_*_R.out    100 files
    phase2.2/cs_stage5/exploratory/dev_A/job/vpot_*_TS.out   100 files

`V_R` at every site on every frame is therefore already in the repository. For any design already in
a pool, the reactant-side first-order term

    dE_R,f(design) = sum_i V_R,f(r_i) q_i x 627.5094740631

is a dot product over committed numbers. No SCF, no orca_vpot call, no HPC.


## 7. Proposed as DIAGNOSTIC 25, to be pre-registered before it is run

Not run here, and deliberately not run here: this project's convention is that a diagnostic is
committed before any of its runs exist, and DIAGNOSTIC 24 already breaks that convention once.

The design would be:

1. For every design in the committed pools, compute `dE_R` and `dE_TS` from the committed vpot files
   and report the decomposition of `d` alongside it, per frame and averaged.
2. Report what fraction of the pool has `dE_R > 0`, and for those, what fraction of `d` the reactant
   term accounts for.
3. State in advance what each outcome means. If `dE_R <= 0` throughout, the blindness never bit and
   the only cost is a sentence in the write-up saying the check was made. If a material fraction has
   `dE_R > 0`, those designs are reactant-destabilising and their barrier numbers do not mean what
   the write-up says they mean.
4. The remedy, if needed, is one additional linear row - `sum_i V_R,f(r_i) q_i <= 0`, or its mean
   over frames - which is linear in `q` and therefore costs the MILP nothing structurally, plus a
   re-solve. It is Dittner's ΔE_R <= 0 penalty written as a constraint.

What it cannot test: it is a first-order term only, built from frozen densities, exactly as `a` is.
It says nothing about polarisation, which O1 excludes from the objective and which the pool's
re-scoring with full single points carries. A design with `dE_R <= 0` at first order could still
destabilise the reactant once polarised. The diagnostic bounds the problem; it does not close it.


## 8. Standing of this document

Nothing above is a result. Sections 1, 2, 6 are readings of committed code and committed file
listings and are checkable by inspection. Sections 4 and 5 are quotations from two papers in
`chorismate-refs`. Section 3 is an argument, not a measurement. Section 7 is a proposal.

This document does not establish that any design is wrong. It establishes that the question has not
been asked, that the method's own source document says it needs asking, and that asking it is free.
