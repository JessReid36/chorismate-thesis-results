# Stage 6: what to relax, what to measure, and how G0 and kappa get fixed (21 October 2026)

**Status (21 October 2026): Jessica has decided.** She agreed to all of it: Stage 6 runs now on frame 42436 in
parallel with the SP package, the bare point-charge comparator is included, and the tolerance is a fraction of the
design's own frozen effect with the fraction taken from the literature rather than chosen - which, after 21 papers
were read in full, is 15 % tied to decision O6's single constant, with the floor clause of section 5. The agreed
rules are pre-registered in `phase2.2/cs_stage6/STAGE6_CRITERIA.txt`, committed with this file and before any Stage 6
input is generated. This document holds the reasoning and the citations; the criteria file holds what was fixed.

It follows the pattern of `OPTIMISER_DECISIONS_20261020.md`: each question gets a recommendation, the literature
behind it, and the direction it moves the reported barrier.

**What Stage 6 owes the rest of the project.**
- The plan update's row for it: "2-3 spheres together, relaxed: no collapse, bonds intact, first-order additivity at
  fixed geometry; WP6: same arrangements frozen against relaxed, with a no-sphere relaxed control". Its outputs are
  used for "size of the relaxation problem; preorganisation term".
- Decision **O2**: "G0 and kappa come from Stage 6", and Stage 6 "should test whether G_add,R predicts the loss of
  effect". If it cannot fix a threshold, "G_add,R is reported for every design without a penalty, and this is stated
  as a limitation of the short list".
- Decision **O2** also asks that Stage 6 relax "a few development-set designs at larger n (for example n = 5, 10,
  20), chosen and fixed in Stage 6's own pre-registration".

**Its sources.** The library, read in full for this draft: Dittner & Hartke 2018 (the Just Accepted manuscript held
in the library; its printed pages run 1-60 and are *not* the journal's 3547-3564), Dittner & Hartke 2020, Dittner's
thesis 2019 with its ESI, Behrens' thesis 2024. Page numbers below are the printed ones; for the two theses the PDF
page is the printed page plus 24 (Dittner) or plus 10 (Behrens), both verified against the page footers. Plus the project's committed records.

**What of the package has been seen.** Only frame 42436's smoke-test results, already disclosed in
`SP_AMENDMENT2.txt`. This draft proposes to run Stage 6 on that frame, so it reads no new package result. The SP
package itself is still in the queue.

---

## 0. What the literature actually says, and why it changes the design

This matters because two of them differ from what a reader of our records would assume.

### 0.1 Both GOCAT papers penalise the TOTAL gradient, not the gradient the design adds

Dittner's penalty is on the plain gradient norm of the embedded system. His thesis Algorithm 3.1 (printed p. 87)
computes `||grad E_i|| <- calcGradNorm(i)` for `i` in {R, TS, P} and compares it straight to a threshold; nothing is
subtracted. The clearest proof is a number: at his converged best design the gradients sit at "a mean of the norms of
11.3 kcal mol-1 A-1 for {E, TS, P}" (thesis ESI, printed p. 303), i.e. just above the threshold, not near zero. And
of a COSMO-path transition state he writes that "in the gas phase it has a gradient of 78.5 kcal mol-1 A-1, well
beyond the allowed tolerance" (thesis printed p. 140; 2018 manuscript p. 36) - a design-minus-bare difference would
be identically zero there by construction.

Behrens is the same: "the QM/MM system is never locally optimized as a whole and all structures therefore have a
large gradient norm. The fitness function merely ensures that it is not too large" (printed p. 67).

**Why we cannot copy that.** Their frozen frames are stationary points of their own reference path, so a total
gradient measures only what the design did. Ours are enzyme geometries evaluated in vacuo: the bare substrate
already carries a gradient of its own, so a total-gradient threshold would mostly measure the geometry, not the
design. Decision O2 already chose the added gradient for this reason. This draft records that the added form is
**ours**, not the literature's, and that it is the reason their threshold value cannot come with it.

### 0.2 The number "10 kcal mol-1 A-1" means two different things in the two theses

- **Dittner** penalises the gradient **norm**: "a penalty as fitness ingredient if ||grad E_{R,TS,P}|| > 10 kcal
  mol-1 A-1 (usually)" (thesis printed p. 86), weight "p approximately 4200" (ESI printed p. 303).
- **Behrens** penalises the **root-mean-squared** gradient, and prints the only closed form either thesis gives
  (Eq. 3.2, printed p. 21):

      Phi_RMSG|m = alpha * (RMSG - beta)^2   for RMSG - beta > 0,   and 0 otherwise

  "where the alpha is a scaling factor and beta is a minimum threshold ... The alpha is usually chosen at around
  250 ... The value for beta is usually chosen to be around 10 kcal/(mol.A), which is somewhat arbitrarily chosen to
  be considered 'close' to a minimum."

A norm and an RMS over the same gradient differ by the square root of the number of components. For our 24-atom
substrate that is sqrt(72) = 8.49. So Dittner's threshold of 10 on the norm is about 1.2 on the RMS, while Behrens'
threshold of 10 is 10 on the RMS: the same printed number, about eight and a half times apart in how strict it is.
Both of our records quote each author correctly, but neither says this. **Any threshold we write must name the
quantity**, and we should not carry over either number.

### 0.3 The authors call the threshold arbitrary, and Dittner abandoned it

Behrens: "somewhat arbitrarily chosen" (printed p. 21, quoted above). Dittner gives no justification at all for the
value; his ESI argues only that the weight is free, since "the final fitness is of course dimensionless such that any
weight can be used that creates a meaningful balance between gradients and barrier" (printed p. 303).

By 2020 Dittner dropped the criteria entirely. The purpose of that paper was "to lift some of the arbitrary criteria,
such as the rough gradient norms" (p. 114106-4), and once the path relaxes inside each evaluation, "all criteria
referring to gradient norms, shift of frames, etc., are all per constructionem not present anymore after this new MEP
influenced by a GOCAT is found. Only the final reaction barrier determines the final fitness essentially"
(p. 114106-6). The 2018 paper had already said why: "a full reaction-path relaxation within the GOCAT embedding
during GOCAT optimization would be advantageous: This would eliminate the need for additional gradient thresholds and
would allow for bigger GOCAT impacts" (manuscript p. 43).

**Consequence for us.** A gradient term is needed only because our design score is on frozen frames, which is our
situation and not something to apologise for. But no published value can be borrowed: the threshold has to be
measured on our own system, which is exactly what decision O2 asks Stage 6 to do.

### 0.4 One warning that bears on how the term will behave

Behrens, printed p. 67, on what a gradient penalty does on a fixed path: "The penalty employed to do this is
obviously minimized when the charged particles are further away from the center, weakening the interaction and
additional gradient introduced."

So a gradient penalty is a keep-away term in disguise. In our design it sits in **re-scoring** (decision O2), not
inside the MILP, so it cannot push the search outward - but it will systematically rank close-contact designs below
distant ones. That is a real direction and it belongs with the short list, not buried.

---

## 1. The decisions at a glance

| # | Question | Recommendation | Direction | Waits on |
|---|---|---|---|---|
| S1 | What geometries | Frame 42436's committed smoke-test stationary points (ts/final.xyz, r_irc/final.xyz, 8 A), not the development set | None; it reads no new package result | nothing |
| S2 | What quantity | G_add = RMS over the 24 substrate atoms of (gradient with the design minus gradient bare) at the same geometry, named as RMS and not compared with any published norm | None | nothing |
| S3 | What arrangements | 2 and 3 spheres placed by a stated rule from this frame's A column, plus the committed optimiser's own designs at n = 5, 10 and 20 on this frame's grid, plus a no-sphere control and one bare-point-charge comparator | None | the Stage 6 grid (PC) |
| S4 | How they are relaxed | Spheres frozen, substrate active, Cartesian, B3LYP-D3BJ/def2-SVP, as WP4's armb_anch; reactant by Opt, TS by OptTS with a frequency check | None | nothing |
| S5 | How G0 is fixed | The largest G_add,R whose measured loss stays under 15 % of the design's own frozen effect - decision O6's single constant - with a floor clause for effects below 3.2 kcal/mol, and the frame spread reported alongside (section 5) | A larger G0 admits stronger-pulling designs: towards a lower frozen barrier | O6's fraction |
| S6 | How kappa is fixed | So that the penalty at the largest G_add,R observed equals the loss of effect measured there, making the penalty an estimate of the loss rather than a free scale | Neutral by construction | S5 |
| S7 | If G_add,R does not predict the loss | O2's fallback: no penalty, G_add,R reported for every design, limitation stated | Removes a term that acts against a lower barrier | the result |
| S8 | What counts as failure | WP4's two criteria: a sphere-to-atom contact under 1.2 A is collapse; a bond moving more than 0.15 A is broken integrity | None | nothing |

---

## 2. S1. What Stage 6 runs on

**Recommendation: frame 42436, radius 8 A, from the committed smoke test.**

`SP_AMENDMENT2.txt` records that "smoke test 2 is that frame's package run", and `STAGE5_CRITERIA.txt` confirms that
"Of the SP package, only frame 42436's results were seen". Its run folder holds `ts/final.xyz` (converged in 7
cycles) and `r_irc/final.xyz` (6 cycles) - the same two files `STAGE5_CRITERIA.txt` section 8 names as Stage 5
production's per-frame inputs. So the geometries are at the production protocol, are already committed, and are
already disclosed.

**Why not the development set.** Its "reactant" is NEB band image 0 and its "TS" is the climbing image. Neither is a
stationary point. C4 re-optimised those band reactants and found dE_reopt of -1.84 to -11.56 kcal/mol, which is why
C4 rejected image 0 as a reactant definition in the first place. Relaxing a design from such a start would be
dominated by the substrate falling towards its own minimum, and a TS "relaxation" from a climbing image with no TS
search would simply slide downhill. A threshold measured there would not mean the same thing in production.

**Why one frame can still fix a threshold.** G0 relates two quantities measured on the same geometry - how hard the
design pulls, and how much effect it loses when the substrate is let go. That relation is a property of the design
and the substrate, not of which frame was chosen, to the extent that the frames are the same conformational band
(they are: the package's 30 frames are the C4 band frames, and 42436 is one of them).

**The limitation, stated plainly.** It is one frame. Decision O2 already flags that applying a 2-3 sphere threshold
at n up to 20 is an extrapolation; this adds a second, from one frame to the ensemble. Recommendation: the
pre-registration commits in advance to **confirming** G0 on two or three production frames once Stage 5 production
exists, by re-measuring the same pairs and reporting whether G0 would have changed - **without re-tuning it**. If it
would have changed by more than its own spread, that is reported as a limitation of the short list rather than used
to move the threshold after designs have been seen.

**The grid.** Stage 6 needs sphere positions on this frame. Recommendation: build them with the committed
`cs5_grid.py` rule and the fixed `floors.tsv`, on frame 42436's own R and TS, on the PC, with no HPC and no new
single points. It is labelled a Stage 6 input, not Stage 5 production, and its sha256 goes in the record. Stage 4c
and 4d set the precedent for taking grid sites into one frame's coordinates.

## 3. S2. The quantity, written out

For a design D at geometry X (the reactant R, and separately the TS):

    g_i(D)  = the gradient on substrate atom i with the design's spheres present, at geometry X
    g_i(0)  = the gradient on substrate atom i with no spheres, at the same geometry X
    G_add   = sqrt( (1 / 3N) * sum_i | g_i(D) - g_i(0) |^2 ),  N = 24 substrate atoms

So G_add is an **RMS**, in kcal mol-1 A-1, of the gradient the design adds. It is zero for the no-sphere control by
construction, which is why the control does not set G0 (section 5 says what does).

Reported with every design: G_add,R and G_add,TS. Decision O2 penalises the reactant one only; the TS one is recorded
because Dittner and Behrens both check all three stationary points and because it costs nothing once the gradient is
computed.

**Not compared with 10.** Neither 10-on-the-norm (Dittner) nor 10-on-the-RMS (Behrens) is a bound on this quantity,
for the reasons in section 0. Where the write-up wants a scale, the honest anchors are: a genuinely relaxed GOCAT
design reaches gradients "around 1 kcal mol-1 A-1" (Dittner thesis ESI, printed p. 361), and his frozen-path designs
sat at about 11.3 on the norm (printed p. 303).

## 4. S3 and S4. The arrangements and how they are relaxed

**Arrangements** (all placed by rule, never by reading a barrier):
1. **Two spheres and three spheres**, from this frame's A column by a stated rule - the most barrier-lowering
   admitted site, then the next that respects the 3.25 A spacing, and so on, with charges at the budget's own
   optimum for those fixed sites. This mirrors Stage 4c's "chosen by a stated rule from frame 41786's A-matrix
   column (not by an optimiser)".
2. **The optimiser's own designs at n = 5, 10 and 20** on this frame's Stage 6 grid, from the committed
   `cs_opt_milp.py` (code tier1-realism 148683d), which is what decision O2 asks for. These are code outputs on a
   test grid, not results.
3. **A no-sphere control**, relaxed from the same start. This is what WP4 lacked and what makes every number above
   interpretable.
4. **One bare point-charge comparator** at the strongest site, to put a number on what the spheres are buying.
   WP4 already showed the contrast at one sphere (below); this repeats it inside Stage 6's own protocol.

**How they are relaxed.** Exactly WP4's `armb_anch` protocol, which is committed and has run:
`! B3LYP D3BJ def2-SVP def2/J RIJCOSX TightSCF QMMM Opt`, `QMAtoms {0:23}`, `ActiveAtoms` the substrate only, the
spheres held fixed in the force field, Cartesian coordinates. The reactant side uses `Opt` from `r_irc/final.xyz`;
the TS side uses `OptTS` from `ts/final.xyz` followed by frequencies, and a TS that does not come back with exactly
one imaginary mode is reported as such rather than used.

**Why this protocol and not another.** It is Behrens' one-embedding scheme with the embedding frozen, which the plan
update already adopted for validation ("sphere-only validation is Behrens' one-embedding scheme (spheres frozen)"),
and it is what WP4 ran, so Stage 6 adds the control and the second and third spheres rather than a new method.

**What WP4 already tells us**, from its committed report, and the single best argument for the charged-sphere
decision:

| at one site | forming C1-C6 | closest sphere-to-oxygen | bond integrity |
|---|---|---|---|
| bare +1 point charge (arma_anch) | 3.16 -> 4.67 A | collapsed, O2 at 0.95 A | largest bond change +0.083 A |
| N-sized LJ sphere (armb_anch) | 3.16 -> 3.71 A | O2 at 2.71 A | PASS (within 0.15 A) |

WP4 cannot say how much of the sphere's 0.55 A is the sphere and how much is the substrate relaxing on its own,
because it had no control. Stage 6's control answers exactly that.

**Cost.** `armb_anch` converged in 46 cycles and 5 h 58 m on 8 cores with 24 GB. The spheres sit in the force field,
not the QM region, so two or three cost essentially the same as one. The whole of Stage 6 as proposed is about a
dozen such jobs: of order 60-120 core-hours, in small jobs that do not compete with the SP package's 16-core,
64-250 GB jobs.

## 5. S5 and S6. How G0 and kappa get fixed

Decision O2 fixes the form. It is Behrens' Eq. 3.2, one-sided and quadratic:

    the re-scoring objective gains   kappa * max(0, G_add,R - G0)^2 ,  summed over frames

(Notation warning: our `kappa` is Behrens' `alpha`. In his thesis `kappa` is the weight of a different term, the
energy-stabilisation penalty of his Eq. 3.3. Our records should keep saying kappa, but the pre-registration should
note the clash so nobody reads "around 10^4" across from his thesis.)

What Stage 6 measures is a set of pairs, one per arrangement:

    G_add,R          how hard the design pulls on the reactant, as defined in section 3
    Loss             the effect it loses when the substrate is let go

with **Loss = ddE(frozen) - ddE(relaxed)**, both computed on this frame, the relaxed one with the substrate
re-optimised and the spheres frozen, and the control's own relaxation subtracted so that Loss is the design's share.

**Then, in this order:**

1. **Test whether G_add,R predicts Loss at all.** Pre-registered test: Spearman rank correlation across the
   arrangements, reported with its confidence interval. This is the test decision O2 asks for ("It should test
   whether G_add,R predicts the loss of effect").
2. **If it predicts** (the interval excludes zero, in the expected direction): **G0 is the largest G_add,R whose
   measured Loss stays under a tolerance**, and **kappa is set so that kappa * (G_max - G0)^2 equals the Loss
   measured at the largest G_add,R observed**. That makes the penalty an estimate of the effect a design is expected
   to lose, in the same units as the score, rather than a free scale factor. It is also why kappa does not need a
   separate decision once the tolerance is set.
3. **If it does not predict**: decision O2's fallback, unchanged - no penalty, G_add,R reported for every design,
   and the short list carries the limitation.

**The tolerance that defines G0: settled from the literature (21 papers read in full, 21 October).**

**First, the honest headline: no published source states a tolerance of this form.** Across the QM/MM method papers
and the whole design literature in the library, nobody writes "at least X per cent of a predicted effect must survive
a fuller treatment". The nearest things to acceptance criteria are a protocol and two noise-floor arguments (below).
So this number has to be proposed, and the right thing is to name the analogy it rests on rather than imply a
standard exists.

**What the literature does measure.** Four independent groups, every number checked against the PDF text:

*(i) A frozen or single-structure barrier against a sampled one - "what does freezing cost".*

| system | frozen | relaxed / sampled | error |
|---|---|---|---|
| PHBH barrier (Kastner 2006, Table 1, p. 458) | 112.3 kJ/mol, static optimisation | 101.5, umbrella sampling | +10.6 % |
| TIM barrier (Zhang 2000 p. 3491 vs Hu 2007 p. 399) | 21.9 kcal/mol, MEP on minimised MM | 19.8, MFEP with sampling | about 10 % |
| Cyclophilin A cis/trans (Cooper & Kastner, Table 1) | 87.5 kJ/mol, exponential average of 65 frozen-environment optimisations | 75.9 +- 1.0, umbrella sampling | +15.3 % |

*(ii) A frozen-geometry first-order electrostatic model against the full calculation - the closest analogue to the
MILP's own score, which is exactly this kind of model.* Sokalski 1985's Table 2 (printed p. 406) compares
Delta = sum q (V_TS - V_R), our score's form, with ab initio for the same arrangements: the model retains 86.7 %,
98.6 %, 94.2 %, 94.8 % and 92.1 % of the ab initio effect at the sites where the effect is of appreciable size - an
error of 1 to 13 %. Dittner's thesis Table 7.1 (printed p. 203) does the same for a dipole estimate: 93 % retained
for a uniform field, 68 % and 50 % for the inhomogeneous sphere and vdW fields, then 33 % and 1.7 % for his strongest
relaxed-path designs. Our own Stage 4c measured 10-31 % with the ranking preserved.

*(iii) The warnings.* Freezing the environment in the wrong state moves a barrier by a factor of 2.3 (Rod & Ryde's
COMT: 26 and 59 kJ/mol from two defensible frozen snapshots, against 56 sampled) and a redox potential by a factor of
12.5 (Ryde, Table 1). Freezing one coordinate that matters - an active-site Mg2+ - moves a barrier by about its own
size (Klahn). Averaging badly costs more than freezing: the arithmetic mean of those same 65 cyclophilin snapshots is
+58 % off where their exponential average is +15 %.

*(iv) The acceptance logic that does exist.* Kastner 2006 accepts an approximation whose error is "not negligible but
would seem to be tolerable in practice", being of the order of their 1.0 kJ/mol sampling error. Cooper & Kastner
accept theirs "in the light of the accuracy of typical DFT calculations". Ryde 2016 section 4 item 7 gives a protocol
and no number at all: run it with the environment fixed and relaxed, and if the answer still depends on which,
enlarge the QM region until it does not.

**Recommendation, which changes the draft's earlier one.** The quarter this draft first proposed had nothing behind
it. Instead:

1. **The fraction is 15 %, and it is the same number decision O6 already requires.** O6 fixes a fraction for the
   method-and-basis uncertainty and says "The fraction to use (for example 15 %) is fixed in the pre-registration".
   Using that one number in both places means the project carries a single such constant, fixed once. The 10-15 %
   band is where all three frozen-versus-sampled barrier comparisons sit, and where Sokalski's linear-model error
   sits for effects of appreciable size, so the analogy supports the value rather than the value being chosen to
   suit.
2. **A floor clause, which Sokalski's data forces.** At his one weakly-interacting site the true effect is
   -0.59 kcal/mol and the linear model gives -2.20: the absolute error, 1.6 kcal/mol, is unremarkable, but the ratio
   is meaningless. So: if a design's frozen effect is smaller in magnitude than the absolute method floor the records
   already give (3.2 kcal/mol per arrangement across bases, Stage 4c), its survival is **not assessable**. It is
   reported as such, and it does not enter the fit for G0. Without this clause a fractional tolerance would fail or
   pass small-effect designs on noise.
3. **The frame spread is reported alongside**, so a reader who prefers the noise-floor rule of Kastner and Cooper &
   Kastner can apply it to the same numbers.

**One finding that changes what Stage 6 must report.** Dittner's carry-over of PM7 designs to PBE0 succeeded for
83-100 % of designs when the question was only "is the barrier still lower?", but for 2.8-80 % when the stationary
points were also required to still be stationary (thesis Tables 6.2 and 6.3, printed pp. 164-165); the entire gap is
the residual gradient. So survival is reported under **both** criteria separately - effect still favourable, and
geometry still a stationary point - and the pre-registration states that G0 is fitted on the stricter of the two.

**And the floor for the whole approach, worth having in the write-up.** None of 1000 random designs was catalytic at
PBE0 in Dittner's test, at either 3 or 10 charges. Whatever a frozen score loses, it is not nothing, and that is the
honest defence of a cheap first pass rather than a claim that freezing is harmless.

## 6. S8. What counts as failure, and what else is measured

**Failure criteria, both taken from WP4 so they are not invented here:**
- **Collapse**: a sphere-to-substrate-atom distance under 1.2 A. WP4's bare charge hit 0.95 A and was reported as
  collapsed; its LJ sphere stopped at 2.71 A.
- **Integrity**: a substrate bond moving by more than 0.15 A from its start.

A collapsed or broken arrangement is reported and excluded from the G0 fit, with the exclusion stated. If the spheres
collapse at all, that is itself a finding about the sphere model and goes in the record.

**Also measured and reported for every arrangement** (all of these come free from the same relaxation):
- the forming C1-C6 distance before and after, against the control's;
- the substrate's centroid displacement, rotation and internal RMSD, as WP4 reported them;
- ddE frozen and ddE relaxed, and Loss;
- G_add,R and G_add,TS;
- the TS's imaginary mode count after relaxation;
- **first-order additivity at fixed geometry** (the plan update's third criterion): the sum of the one-sphere
  effects against the measured effect of the 2 and 3 sphere arrangements, at the frozen geometry. This needs single
  points only, not relaxation, and it is the cheap check that the linear score the MILP optimises is adding up.

## 7. Direction, and what Stage 6 cannot settle

**Direction of the stage as a whole.** The term it calibrates acts **against** a lower frozen barrier: it penalises
designs that pull hard. Within the stage, a larger G0 or a smaller kappa is the more permissive choice, towards a
lower barrier; the recommendation in section 5 is the stricter of the options offered. Nothing in Stage 6 is chosen
by the barrier any design reaches: the arrangements are placed by rule, the geometries are fixed in advance, and the
tolerance is fixed before any relaxation runs.

**What it cannot settle, to be written into the record rather than discovered later:**
1. **One frame.** Section 2's confirmation rule is the mitigation, not a fix.
2. **2-3 spheres, used at up to 20.** Decision O2 already flags this; including n = 5, 10 and 20 narrows it but
   those designs come from a test grid on one frame.
3. **The keep-away bias.** Behrens' p. 67 result means the term ranks distant designs above close ones for reasons
   that are partly an artefact of scoring a frozen path. Because the term is applied at re-scoring and not inside
   the MILP, the pool still contains the close designs; the bias affects the ranking, and that is stated with the
   short list.
4. **Relaxation is not validation.** Stage 6 relaxes the substrate with the spheres frozen at a fixed geometry. The
   catalytic verdict still comes from the relaxed NEB-CI chain of A2.5, as the plan update requires.
5. **The spheres are frozen.** Dittner's own view is that the honest fix is relaxing the path inside the search
   (2020), which we are not doing and cannot afford. Stage 6 measures the size of the error that choice leaves,
   which is the most that can be said for it.

## 8. What is still open

1. **Settled by Jessica, 21 October:** the tolerance is a fraction of the design's own frozen effect (option (c)),
   with the fraction and its justification taken from the literature rather than chosen - section 5 above now does
   that, and recommends 15 % tied to decision O6's single constant, plus the floor clause and the two-criteria
   reporting. **This needs her confirmation of the 15 % and of the floor clause**, since both are new numbers in the
   record even though neither is new to the project.
2. **Settled by Jessica, 21 October:** Stage 6 runs now, on frame 42436, in parallel with the SP package.
3. **Settled by Jessica, 21 October:** the bare point-charge comparator is included.

Next: `STAGE6_CRITERIA.txt` in the house style with the sha256 of every input and of the code, and a bundle that
builds the Stage 6 grid on the PC and generates the job inputs for checking before anything is submitted.
