# Handoff: chorismate mutase ensemble and charge design

State at 23 September 2026. Written to prevent re-investigation of questions
already settled. Conclusions that were reached and later overturned are recorded
explicitly, because several were plausible enough to be re-derived.

---

## 0. How to work on this project

**Read this section before anything else.** Every expensive error in this project
came from breaking one of these rules.

### Say only what the output shows or the literature states

Two sources are admissible: a command whose output is in front of you, and a
paper that has been read. Nothing else.

- If a number is quoted, it came from a file that was opened. Do not reconstruct
  figures from memory, and do not carry a value forward from earlier in a
  conversation without re-reading it if anything has changed.
- If a claim needs a citation and the paper is not in the repository, **say so and
  ask for the DOI.** It will be added. Do not reconstruct a DOI, a page number, a
  quoted sentence, or an author list from memory — one reconstructed DOI in an
  earlier session pointed at the wrong paper.
- If something is inferred rather than measured, label it as inference in the same
  sentence. "The Hessian is scratch" and "the Hessian is named as scratch in
  ORCA's own output" are different claims.
- When asked whether something is the case, the answer is a command, not a view.

### Check the actual output, every time

- **A generator passing `bash -n` says nothing about what it writes.** After
  changing a generator, regenerate one frame and grep the generated file. This
  caught the spring constant living in a copied driver rather than the generator
  that was edited.
- **Never infer a job's state from the presence of an output file.** PBS writes
  its output at job end, and ORCA writes window files on completion, so a running
  job and an unstarted one look identical on disk. Ask `qstat`.
- **An empty grep is not a negative result** until the file has been confirmed to
  exist and the pattern confirmed to be right. Several "nothing found" readings in
  this project were the wrong path or the wrong search term.
- **Absence of a success marker is not absence of progress.** A stage that has
  produced 52,000 lines of output and is running at 780 per cent CPU is working,
  whatever it has not yet printed.
- **Re-read a file after editing it.** Earlier output in a conversation is stale
  the moment anything changes.

### When something looks wrong

Measure before concluding. Three examples from this session where the first
explanation was wrong and a measurement settled it: the transition-state stage
was not stalled but slow; the memory shortfall was not the cause of that
slowness; and the top-site disagreement between frames was near-degeneracy in the
ranking rather than disagreement about location.

### Scope

Do not widen a task without saying so. Deleting files, killing jobs and editing
committed scripts each need the reason stated and, where the action is
irreversible, confirmation.

---

## 1. Where the pipeline is now

Thirty new frames selected from the extended molecular dynamics, all past
reactant optimisation, scan and product optimisation.

| stage | state |
|---|---|
| reactant optimisation | 30 of 30 converged |
| scan | 30 of 30 complete |
| product optimisation | 30 of 30 complete |
| band | 4 converged, 26 outstanding |
| transition-state optimisation | 4 running, 3 to 5 cycles each |

The four converged bands give barriers of **12.97, 15.97, 18.64 and 14.78
kcal/mol**, inside the original ten-frame range of 4.48 to 25.26.

Run the rest with `bash run_ensemble_batched.sh stage4 4`, four at a time, then
`harvest` between batches. `next.sh` advances the earlier stages and is safe to
call repeatedly.

## 2. The ensemble already accepted

Fourteen original frames, ten satisfying the full near-attack criterion.

**It reproduces the published result.** Mean transition-state stabilisation
**-4.32 kcal/mol** against Claeyssens *et al.* (2005) **-4.2**; gradient of
barrier against stabilisation **1.062** against their **0.95**; correlation
r = +0.846. Independent system setup, different force field and basis.

**The spread is ordinary.** Ryde (2017) surveyed 24 QM/MM studies and found the
standard deviation ranges 0.6 to 97 kJ/mol, with 73 per cent exceeding 10. This
work is at 22 kJ/mol. Claeyssens at 7 is the tight end of the field, not the norm.

## 3. Faults found and corrected

### The scan restraint was five times too weak

The restrained scan did not pass through the transition state. In every frame the
achieved distances sat 0.18 to 0.35 A on the reactant side of their targets
approaching the barrier, then flipped to the product side, so the reaction
coordinate jumped by more than an angstrom between adjacent windows whose other
steps are 0.07 to 0.15. The maximum handed to the band as its guess was the last
point before the slip.

**The cause is a unit mismatch.** The ORCA manual specifies the `Restraint`
spring constant in **kJ mol⁻¹ Å⁻²**. The production value of 400 was therefore
about **96 kcal mol⁻¹ Å⁻²**, five times weaker than the **500 kcal mol⁻¹ Å⁻²**
used by Claeyssens *et al.*

Testing 400, 1000, 2500 and 6000 kJ on one frame gave largest deviations of
0.308, 0.104, 0.038 and 0.015 A. **2500 kJ is adopted** — 597 kcal, within twenty
per cent of the published value. Confirmed on five further frames: the step
between windows 12 and 13 is now 0.161 to 0.169 against 1.14 before, and the
transition-state guesses sit 14.4 to 17.5 kcal/mol above the scan start, matching
the reference frame's 16.37.

A stiffer restraint also stores *less* energy here, not more, because the
deviation falls faster than the constant rises, and it converges in a quarter of
the wall time.

**Why two restraints rather than one.** Claeyssens restrain the reaction
coordinate itself. ORCA 6.0's `Manage_Colvar` accepts only `Distance`, `Angle`,
`Dihedral` and `CoordNumber`, with no linear combination — custom collective
variables by mathematical expression arrived in 6.1. Both distances are therefore
restrained separately, which over-determines the geometry and is why a stronger
constant is needed. Do not spend time looking for a difference-of-distances
colvar in 6.0; it does not exist.

### The memory requests were wrong in both directions

Measured against actual use:

| stage | requested | used | now |
|---|---|---|---|
| reactant optimisation | 120 GB | 1.4 GB | 16 GB |
| scan | 120 GB | 1.3 GB | 16 GB |
| product optimisation | 120 GB | ~1.4 GB | 16 GB |
| band | 120 GB | **167 to 216 GB** | 250 GB |

The over-request excluded every job from all seventeen 48-core, 96 GB machines,
which is why five jobs queued while a fraction of 2,344 cores were in use. After
the change every job ran immediately.

The band arithmetic: `%MaxCore` is **memory per process**, and ORCA can exceed it.
With `maxcore 3000`, `nprocs 8` and `NImages 8` the requirement is
8 x 8 x 3000 MB, about 192 GB. Every band before this ran roughly 70 GB over its
request.

### The batch runner could not see the queue at all

Two independent defects in `run_ensemble_batched.sh`, both measured 2026-09-28.
Band job names are `cm19_n<5-digit frame>` - `cm19_n24883` - while the code
asked for `cm19_n${f:1}` = `cm19_n4883`, which strips the leading digit and is
not the job's name. And qstat truncates the Name field to nine characters plus
an asterisk, so even the correct name could not match: `cm19_n24883` prints as
`cm19_n248*`. The "still running" guard in harvest had therefore NEVER been able
to fire, and the same defect was in stage1 line 93. Fixed by `job_running()`,
which compares the printed prefix against the full name, plus a clause refusing
to delete any Hessian written within the hour.

A third defect, found 2026-09-29: `stage4` had no per-frame queue check at all.
A frame that is running but not yet converged passes every other test, so each
stage4 call submitted a duplicate into the same directory. Observed on frame
36665, which acquired two jobs writing the same files; both were killed and the
frame restarted from a cleaned directory. Read this whole file end to end rather
than block by block - three separate faults were found in it, each only because
something else forced a look at that particular block.

### The batch runner tested files instead of the queue

`stage2` decided a scan was outstanding unless `win_20.pdb` existed, which only
appears on completion — so a running scan and an unstarted one looked identical
and duplicates were submitted into live directories. Now it asks `qstat`.

Note that `qstat` truncates job names to ten characters *including* a trailing
asterisk, so the printed field is a **prefix** of the real name. Compare in that
direction.

### Cleanup deleted an input

`rm -f .../scan/win_*.pdb` removed `win_00.pdb`, which `step19c` stages from the
optimised reactant and the scan chains from. Rerunning `step19c` restores it.

## 4. Sampling quality: settled, with a stated limitation

### The molecular dynamics

Production extended by 40 ns to 60 ns total. Averages over the extension 300.02 K
and density 1.0222.

### Correlation times are a property of the observable, not the trajectory

| observable | tau | predicts the barrier? |
|---|---|---|
| backbone RMSD vs fixed reference | invalid | not applicable |
| theta2 near-attack angle | 275 ps full record, 97 ps after 20 ns | see below |
| theta1 | 4.1 ps | r = +0.076, no |
| forming C1-C6 | 7.0 ps | r = -0.202, no |

**The backbone values are discarded.** Measured against two different reference
structures they gave 699 and 2349 ps. Grossfield *et al.* (2018) define the
correlation time only for a stationary series — "Such correlations are often
stationary, meaning that tau is independent of t" — and that series is not. They
also state the deviation against a single reference "should really be considered
as another equilibration test" and "is not even a particularly good test of
equilibration", because its degeneracy means one cannot tell whether the
simulation explores new states equidistant from the reference.

**The committed `step11e_autocorr.py` measures the wrong observables.** It reports
3.2 ps for the forming distance and 2.5 for the Arg90 contact, calling them "the
two quantities that define catalytic competence", and concludes the frames are
independent. Neither predicts the barrier.

### The limitation, which must be stated in the write-up

Theta2's correlation with the barrier is carried by the three near-attack
failures. Across all thirteen frames with an in vacuo barrier r = +0.657,
p = 0.015. Within the ten reported, **r = +0.487, p = 0.154**.

**So no observable has been shown to predict the barrier among the frames
reported**, and the correlation time adopted is the slowest measured rather than
the demonstrably relevant one. With ten frames the test has little power; r =
0.487 is not evidence of absence. Revisit once thirty barriers exist.

### The equilibration cut

**20,000 ps**, by Chodera's (2016) criterion — the discard point maximising the
effective sample size. N_eff rises 109 at t0 = 0 to 205 at 20,000 then falls to
128, so the maximum is interior rather than at the scan edge. The earlier 11,000
ps was read off block means by eye and is superseded.

Chodera's data-sufficiency caveat is satisfied: the trajectory is 218 times the
minimum estimated correlation time.

### The trajectory does revisit states

The all-to-all analysis Grossfield *et al.* recommend in place of
deviation-against-a-reference: **11.3 per cent** of pairs separated by 10 ns or
more are as structurally close as typical pairs within 500 ps. That is the
condition they name as "a necessary condition for good statistics", and it shows
the apparent drift is exploration rather than escape to a new structure.

### The selection

Thirty frames, all after 20,000 ps, minimum spacing **650 ps** against the 485 ps
of five correlation times. Renumbered onto a continuous timeline: extension frame
*i* is production frame 20,000 + *i*.

## 5. Design objective: two tests complete

### B5, additivity — contributions may be summed

At unit charge the non-additive term reaches 1.124 kcal/mol, above the objective's
resolution limit. But it is **bilinear in the two charges to within 8.7 per cent**
across a fourfold range, confirming cross-polarisation, and the sign reverses with
the product of the charges at every separation.

At the magnitudes a design uses — Dittner and Hartke report converged values near
-0.11 and +0.09 e — it is about **0.01 kcal/mol**, fifty times below the
resolution limit. The failure measured at unit charge does not transfer.

### B6, frame sensitivity — design against the ensemble mean

| | Spearman | top-10 kept | max per-site difference |
|---|---|---|---|
| basis, def2-SVP to def2-SVPD | 0.994 | 8/10 | 0.629 |
| frame, across ten | 0.874 to 0.982 | 5/10 to 9/10 | up to 2.4 |

Site-wise standard deviation at the ten most stabilising sites: **0.66 to 0.72
kcal/mol**, above the objective's resolution limit.

`dv_grid_ensemble_mean.tsv` holds the mean and per-site standard deviation.

### What the maps actually show, which is subtler than B6 alone

Every frame's deepest basin lies **within 9 to 30 degrees of the ether oxygen
O3**, the atom gaining negative charge as the C4-O3 bond breaks. Circular
standard deviation in azimuth 32.4 degrees; polar range 23.8 to 39.6 degrees.

But the depths span **-3.43 to -5.56 kcal/mol**, a variation of about half the
magnitude.

**The 3/10 top-site overlap is an artefact of ranking near-degenerate sites.**
Within a frame the top ten span 0.417 kcal/mol with a median step of 0.03 between
neighbours, against an across-frame variation of 0.66 to 0.72. The union of all
ten frames' top tens is **20 sites**, not 200; eleven sites are common to all ten
frames at top-20; and with degeneracy allowed for, the median agreement is
**10/10**.

So the frames agree on a favourable region of about twenty sites spanning 4 to 5
A beside the ether oxygen, and cannot order the sites within it. The design target
is a region, not a point.

## 6. The transition-state optimisation question

`NEB-TS` runs the band, writes the path summary from which the barrier is read,
then performs a saddle optimisation using a 4.8 GB approximate Hessian. Three
earlier frames spent three days each in that stage. I twice concluded it was
stalled; both times I was wrong:

- The first reading looked for a success marker and found none. The stage was
  producing 52,000 lines of output.
- The second attributed the slowness to the memory shortfall. At the corrected
  250 GB it is equally slow, so memory was not the cause. CPU is at 780 per cent,
  so it is computing, not idle.

Current frames are at 3 to 5 cycles. Frame 43738's first cycle gave RMS gradient
0.000057 and MAX 0.00172, at or inside typical tolerances.

**The barrier does not depend on this stage.** It comes from the path summary
written at band convergence.

**And the published work does not converge a saddle at all.** Claeyssens *et al.*
take "the highest point, the approximate TS structure, at r values between -0.5
and -0.7 A" from a restrained scan. The climbing image is more converged than
that. The refined saddle would be an improvement on something already adequate by
the published standard, not a requirement.

**DECISION TAKEN, 2026-09-28: do not run this stage.** All four frames attempted
(24883, 26495, 34991, 43738) were killed at the 176 h walltime after 6 to 9
cycles, with final MAX gradients of 0.00236, 0.00390, 0.00131 and 0.00191
against a 3.0e-4 tolerance - 4 to 13 times over, and rising on 43738. Each had
reached band convergence in 2 to 7 hours, so roughly 96 per cent of each job's
walltime produced nothing. The remaining frames run NEB-CI, which stops at the
climbing image: measured run times 2.6 to 22.7 hours, mean 7.2, and about
450 MB per frame against 22 GB, because no Hessian is built.

Eight images are sufficient to place the saddle. Frame 47641 was rerun with
NImages 16: the highest-energy image sits at fractional path position 0.647
against 0.667 with eight images, and the energies agree to within
0.037 kcal/mol at every matched iteration. The residual offset from Claeyssens'
r = -0.50 is therefore methodological - their transition state is the maximum of
a restrained scan along one coordinate, ours is a climbing image free to find a
saddle displaced in any coordinate - and not a resolution artefact.

## 7. Conclusions overturned — do not re-derive

1. **The barrier spread indicates a defect.** It does not; Ryde's survey puts this
   work mid-range.
2. **ORCA's separate quantum and classical energies can be read as chemistry and
   environment.** Under electrostatic embedding the quantum term already contains
   the coupling (Senn and Thiel). The correct separation is a single point on the
   isolated substrate at the QM/MM geometry, which is what Claeyssens do and what
   produced the -4.32.
3. **The frames are independent because the forming distance decorrelates in 3.2
   ps.** That distance does not predict the barrier.
4. **The transition-state optimisation is stalled.** It is slow. See section 6.
5. **The memory shortfall explains the slow TS stage.** It does not; the corrected
   250 GB is equally slow.

## 8. Outstanding

**Immediate**

- Run the remaining 26 bands, four at a time, harvesting between batches.
- In vacuo single points for the new frames, so stabilisation can be compared
  against Claeyssens' -4.2. Not yet run; their column in `ensemble_barriers.tsv`
  is empty.
- Frame 08170 still has no barrier. Its guess was 7.18 kcal/mol above the scan
  start, the lowest of fourteen, and its band collapsed. Rerun at the corrected
  spring or document the exclusion.

**Design**

- Choose the objective. Four formulations, all but the last linear: single frame;
  ensemble mean; mean penalised by spread, max sum q(mu - lambda sigma); and
  minimax, max t subject to t <= sum q Dv_f for every frame. Ryde records the
  consensus for combining snapshot energies as an **exponential average**, since
  the rate depends on exp(-dG/RT) — that objective is not linear and its
  conditioning at this spread is unmeasured. Worth the supervisor's view; the
  three are different scientific claims.
- Per-site standard deviations assume sites vary independently. They do not.
  The covariance is computable from the ten frames' full vectors, which exist.
- Check whether two charges can even be placed: the favourable region is 4 to 5 A
  across and the separation constraint is 3.5 A.

**Write-up**

- Zero-point and thermal corrections before comparing to an activation enthalpy.
- The reference transition state shows two imaginary modes where one is expected.
- Section X.1.4 claims one level of theory throughout. This is TRUE for every
  structural calculation: optimisations, scans, bands and barriers are
  B3LYP-D3BJ/def2-SVP in both phases. def2-SVPD appears in only four files in
  the whole code repository - s7_additivity, s7b_additivity_scaling,
  s9_frame_sensitivity, and 02_singlepoints/refstate_diagnostic, which runs both
  bases deliberately to compare them. All four are difference-potential single
  points. The split is structural work versus dv work, not Phase 1 versus
  Phase 2. The earlier note here overstated the problem. What has NO written
  justification anywhere is the choice of def2-SVP over Claeyssens' 6-31G(d);
  argue it via stabilisation, where basis error largely cancels.
- The original fourteen frames lie at 2450 to 19185 ps and are therefore all
  before the 20,000 ps equilibration cut adopted in section 4. Their scans also
  ran at the 400 kJ spring, against 2500 for the thirty. The two groups are not
  compared: the ten were a pilot establishing that the pipeline reproduces
  Claeyssens, and the thirty establish it independently. Nothing in the write-up
  should pool or contrast them.
- stab_TS_total, in any ensemble_barriers.tsv written before 2026-09-28, must
  never be quoted. It differenced a QM/MM TOTAL energy for the whole solvated
  system against a 24-atom gas-phase energy, giving about -240 Eh. It is not a
  stabilisation of anything. Nothing downstream ever read it. Replaced by
  stab_TS = barrier - barrier_vac; stab_R, which was not wrong but misnamed, is
  now E_int_R.
- The in vacuo reference is a gas-phase dianion that is electronically UNBOUND,
  HOMO(R) +0.082 Eh at def2-SVP and +0.044 at def2-SVPD. It is retained because
  the unboundedness cancels between reactant and TS: the barrier moves only
  0.66 kcal/mol from vacuum to bulk water. Claeyssens used the same gas-phase
  reference, so the convention is inherited - but state it rather than leave it
  to be found.
- Arithmetic averaging stated as a considered choice, per Ryde's guidance.
- Frame 820, the Phase 2 reference, is at 820 ps and therefore pre-equilibration.

## 9. Working discipline that earned its place

- Verify a generator's change in the **generated file**, not just the generator.
  `bash -n` on a script says nothing about what it writes.
- Never infer a job's state from the presence of an output file. Ask `qstat`.
- When renaming a variable, grep **every** occurrence and account for each.
- Copy the production driver rather than reconstructing an input from a grepped
  fragment. The stage that copied never drifted; the stage that rewrote did.
- Check what a job actually uses before trusting its resource request.
- Absence of a success marker is not evidence of no progress. Count iterations.

## 10. Where things live

**Repositories**
- Code: `~/Desktop/chorismate_thesis_code`, branch `tier1-realism`
- Results: `~/Desktop/chorismate-thesis-results`, branch `main`
- Cluster: `18660916@hpc1.sun.ac.za`, work under `~/system_development`

**On the cluster**
- `05_qmmm/19_ensemble/frame_NNNNN/` — one directory per frame, all stages
- `05_qmmm/19_ensemble_barriers/` — the harvest, which is what the analysis reads
- `05_qmmm/12_frame_selection/selection_manifest.tsv` — 45 frames, the first 15
  from the original run and 30 renumbered from the extension
- `05_qmmm/16_scan/run_scan.sh` — the scan driver, **the single place the spring
  constant is set**; it is copied into each frame
- `04_amber_md/10c_production/prod.nc` and `10d_production_extend/prod_ext.nc` —
  one trajectory in two files, 20,000 and 40,000 frames; scripts route by index
- `phase2b_charge_design/08_frame_sensitivity/` — the per-frame difference
  potentials and the ensemble-mean map

**Driving the pipeline**
```
bash next.sh                              # advance scans and product optimisations
bash run_ensemble_batched.sh status       # what is where
bash run_ensemble_batched.sh stage4 4     # four bands
bash run_ensemble_batched.sh harvest      # read barriers, free space
```

**Papers held** are in the reference repository. If one is needed that is not
there, ask for the DOI.

## References

Chodera (2016) doi:10.1021/acs.jctc.5b00784
Claeyssens *et al.* (2005) doi:10.1039/b508181e
Grossfield *et al.* (2018) doi:10.33011/livecoms.1.1.5067
Hur and Bruice (2003) doi:10.1073/pnas.1534873100
Ryde (2016) doi:10.1016/bs.mie.2016.05.014
Ryde (2017) doi:10.1021/acs.jctc.7b00826
Senn and Thiel (2009) doi:10.1002/anie.200802019

## Errata, 6 October 2026 (provenance audit, s18b_pipeline_check.py)

- The NEB-TS record above calls 24883, 26495, 34991 and 43738 "all four frames attempted".
  The committed outputs show 22 NEB-TS runs: the 14 pilot frames and 20000, 21634, 23268,
  24883, 26495, 33320, 34991 and 43738. None of the 22 neb.out files ends in ORCA TERMINATED
  NORMALLY. Their barriers are read, like every other, from the climbing image of the
  converged NEB stage, but in an NEB-TS run that stage stops at ORCA's NEB-TS thresholds,
  four times looser than NEB-CI's (max force on the climbing image 2.0e-3 against 5.0e-4
  Eh/bohr). On the 22 NEB-CI frames, going from the looser to the full criteria lowered every
  barrier: median 0.38, at most 4.95 kcal/mol, while the climbing image moved by at most
  0.032 A RMSD. The 22 NEB-TS barriers are therefore probably too high by a few tenths of a
  kcal/mol. See PHASE1_AUDIT_CHECKLIST.md item C5.
- Frame 08170 has no barrier. Its band falls monotonically and ORCA marks image 0 as the
  climbing image. ensemble_barriers.tsv recorded 0.000 until the harvester was corrected
  (code 8424715); the field is now blank.
- 05_qmmm/19_ensemble/frame_11630/scan/run_scan.sh is a later copy (code 7f3bc74, SPRING=2500)
  than the version that ran (8c2a372, 8 September). Every scan input of that frame uses
  Spring 400.0; the inputs are the record.
