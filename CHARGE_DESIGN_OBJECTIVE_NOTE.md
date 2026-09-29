# The design target and the objective function: what the literature settles

Status: **recommendation, literature-backed.** Companion to
SOLVATION_DECISION_NOTE.md; the two are one supervisor conversation.
Written 2026-09-29. Every claim traces to a paper in `chorismate-refs` that has
been read, or to a committed output file.

---

## 1. The question

Phase 2 places point-charge surrogates and optimises them to catalyse the
chorismate-to-prephenate rearrangement. Two things were undecided:

- **What to target.** The difference-potential map is built from one frame's
  reactant and transition-state geometries. Test B6 asks whether that map is a
  property of the reaction or of the frame.
- **How to score a candidate.** Four aggregation options had been drafted:
  the ensemble mean, the mean penalised by spread, minimax, and Ryde's
  exponential average. No decision had been taken.

---

## 2. What was tried, and what each attempt showed

### 2.1 Assuming one frame would do

The design grid and the difference potential were built from a single reference
frame. `s9_frame_sensitivity.pbs` (test B6) was written to check that choice
rather than assume it, and its header records why: Claeyssens et al. (2005)
report all sixteen of their paths and average them; Senn and Thiel (2009)
report ten snapshots as a mean with its spread; Ryde (2016) describes common
practice as 3-10 snapshots and states plainly that "it is not obvious how the
results should be averaged to give reliable activation barriers". None of them
selects one structure. The design work needs one, so the choice had to be
tested.

### 2.2 Reading the site-by-site spread, and getting it wrong

`dv_grid_ensemble_mean.tsv` gives, per site, the mean difference potential
across ten frames and its standard deviation:

    1448 sites   mean dv -0.025 kcal/mol   mean sd 0.459   max sd 1.174

A mean spread of 0.459 kcal/mol against site values reaching -2.9 looked like
strong evidence that the map is frame-independent. **That reading was wrong**,
and it was wrong because it tested the values rather than the ranking. An
optimiser consumes the ranking.

### 2.3 The ranking test, which says something different

`s9` had crashed on a NameError (`pv` undefined) after completing all twenty
single points and twenty `orca_vpot` evaluations. Repairing the analysis block
and rerunning - seconds, since the expensive work was already on disk - gave
each frame against the ensemble mean map:

| | mean | range |
|---|---|---|
| Spearman | 0.935 | 0.874 - 0.982 |
| top-10 sites kept | 7.0 / 10 | 5 - 9 |
| best site agrees | **3 / 10 frames** | |
| max per-site difference | 1.51 | 1.03 - 2.42 kcal/mol |

Only three of ten frames agree with the ensemble mean on the single
highest-ranked site. Spearman of 0.935 across 1448 sites still permits heavy
reshuffling at the top, and the top is the only part a design uses.

The sites are closely spaced, so a 0.46 kcal/mol shift is enough to reorder
them. **A value test cannot substitute for a ranking test.**

### 2.4 Why this is probably not fatal

Dittner and Hartke (`acs.jctc.8b00151`) report that the broad distributions of
ESP values at their reacting atoms "can be interpreted as a robust solution
domain: as long as the ESP is within those ranges, a significant catalytic
effect is to be expected". They found many different Cartesian placements of
partial charges achieving the same ESP at the reacting atoms.

If the top-ranked sites occupy the same **region** across frames, rank identity
within that region is physically meaningless, and the reshuffling is noise
inside a robust solution domain. **This is the outstanding test** - see section 6.

---

## 3. The design target, from experiment

Burschowsky et al., PNAS 2014 (`pnas.1408512111`, edited by Warshel) performed
the decisive experiment on B. subtilis chorismate mutase. Arg90 was replaced by
**citrulline**: isosteric, but the cationic guanidinium becomes a neutral urea
(NH2+ replaced by O). Their finding:

> the positively charged arginine contributes up to **5.9 kcal/mol to transition
> state stabilization but only 0.6 kcal/mol to the binding energy of the ground
> state**

The citrulline NH2 sits **3.2 A from the ether oxygen** of the transition-state
analogue. Arg90Cit still preorganises the substrate in the reactive
conformation and is nonetheless a poor catalyst. Their title states the
conclusion: electrostatic transition-state stabilisation, not reactant
destabilisation, is the chemical basis of catalysis here.

**Against our own measurement.** The ensemble gives mean `stab_TS` = **-4.8
kcal/mol** over 35 frames with both a barrier and an in vacuo barrier. One
cationic centre at 3.2 A from the ether oxygen therefore accounts for more than
the entire measured stabilisation; the rest of the active site contributes
little net.

This is a large simplification. The design target is not a subtle distributed
field. It is **one positive charge approximately 3 A from the ether oxygen**,
with an approximately 10:1 differential between transition state and reactant.
It is also a benchmark: 5.9 kcal/mol is what one well-placed cation achieves in
a real enzyme.

---

## 4. The objective function, from GOCAT

Dittner and Hartke define their fitness as an aggregate of **five** terms, not
one:

1. the electronic barrier between TS and reactant should be minimal;
2. the TS must be stabilised relative to the reference path with no charges;
3. **no new intermediate minima** - the reaction profile must remain unimodal;
4. a penalty if the reactant, TS or product shifts more than 2 frames along the
   coordinate;
5. **the gradient norms at reactant, TS and product must stay below a
   threshold**, so they retain their character as stationary points.

They are explicit about the fifth. Without it,

> the reaction profile could be transformed into any arbitrary path on the
> GOCAT-modified PES, even into an equi-potential contour line, with no barrier
> at all but also without the defining minimum-energy pathway characteristic

which they name as over-fitting. A bare barrier objective will find a charge
arrangement that flattens the surface rather than one that catalyses a reaction.

**The four options previously drafted address a different axis.** Mean, mean
penalised by spread, minimax and exponential average all concern aggregation
*across frames*. GOCAT's five terms concern validity *within* a frame. Both are
required, and this had not been stated anywhere in the project.

---

## 5. Recommendation

**Per-frame fitness: adopt GOCAT's five terms unchanged.** They are published,
tested on two reaction classes, and term 5 guards against a failure mode a bare
barrier objective cannot see.

**Across-frame aggregation: the mean penalised by spread.** The justification is
no longer aesthetic. Dutta Dubey, Stuyver, Kalita and Shaik (`jacs.9b13029`)
show that solvent organises in response to an applied field and generates a
counter-field opposing it, with screening proportional to solvent polarity, and
that catalysis emerges only once the applied field exceeds that opposing field.
A design that works in some conformers and not others will be screened away in
water precisely where it is weakest. Robustness across conformers is therefore
not a refinement; it is a condition of the design surviving solvation.

**Design against the ensemble mean map**, `dv_grid_ensemble_mean.tsv`, rather
than any single frame, and use its `sd_kcal` column to downweight sites the
ensemble disagrees about. Section 2.3 rules out designing on one frame.

**Target the ether-oxygen region explicitly** and check the map against
Burschowsky: the extremum of the difference potential should lie near the ether
oxygen, roughly 3 A out. If it does, the map reproduces a measured result
independently, which is strong validation of the whole grid construction.

**Precision floor.** The standard error on the 30-frame mean barrier is about
0.78 kcal/mol, so a design effect below roughly 1.6 kcal/mol cannot be separated
from conformational noise. The enzyme achieves -4.8. Burschowsky's single
arginine achieves 5.9. Those set the scale of what is worth claiming.

---

## 6. Outstanding

- **Do the top-ranked sites cluster spatially across frames?** This decides
  whether section 2.3's ranking instability matters or is noise inside a robust
  solution domain. Computable from `row_order.tsv`, `dv_grid_ensemble_mean.tsv`
  and any superposed reactant geometry already in `08_frame_sensitivity`.
- **Each frame against the PRODUCTION map**, not the ensemble mean. The second
  table in `s9` never ran (a second undefined `pv`, now fixed). This matters
  more than the first table: if the reference frame is an outlier, design work
  resting on it inherits that.
- **B6 was run on the original ten `full_NAC` frames** - 400 kJ spring, all
  before the 20,000 ps equilibration cut. The conclusion is demonstrated for the
  pilot. The corrected spring significantly tightened the saddle-position
  distribution (F = 3.21, df 12,16), so the thirty would likely show less Dv
  variation, not more - but that is a prediction, not a result.
