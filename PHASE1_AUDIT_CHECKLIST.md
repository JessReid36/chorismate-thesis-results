# PHASE1_AUDIT_CHECKLIST.md

Audit of the Phase-1 QM/MM barrier against the two reference papers, with a
decision and a fix for each flag. The aim is not to copy the published protocol
but to be able to say, for every difference, either "this matches the
literature" or "this differs, deliberately, and here is why it is better".

**Reference papers**

- **Claeyssens et al. 2011** (Org. Biomol. Chem. 9, 1578) — QM/MM reaction-path
  science reference. 16 enzyme pathways, 24 in water. B3LYP/6-31G(d)/CHARMM27,
  QM region = chorismate only (24 atoms), electrostatic embedding, no link
  atoms. Average enzyme barrier **11.3**, water **17.4** kcal/mol.
- **Agbaglo & DeYonker 2024** (nihms1987271) — MD protocol source. 20 ns MD,
  **250 snapshots**, QM-cluster models, ΔG‡ = **10.34 ± 2.62** kcal/mol.

**This work, frame 820:** +16.00 kcal/mol. B3LYP-D3BJ/def2-SVP/CPCM(4),
QM = 24 atoms, 102-atom movable region, ff14SB/GAFF/TIP3P.

---

## Should the running jobs be stopped?

**No.** The five reactant→scan→product→NEB chains in progress are valid work
under a defensible protocol, and their output is needed no matter which
decisions below are taken:

- They give the spread of the barrier under the current protocol, which is the
  quantity missing from the thesis today.
- Items 1, 2, 5 and 6 below are read-only analyses that run alongside them on
  the login node and cost nothing.
- Item 4 (the sampling-protocol decision) is better made *with* the spread in
  hand than without it. If the spread turns out to be small and centred near
  16.00, the protocol difference is the explanation for the gap with Claeyssens
  and becomes a finding. If the spread is large and straddles 11–16, snapshot
  variance is the explanation and no protocol change is needed.

Let them finish. Nothing below is invalidated by their completion.

---

## A. Flags to fix before the barrier is quoted

### A1. The 3.7 Å near-attack cutoff is unsourced  ☐

`step11c` calls 3.7 Å "the NAC threshold" and `step12a` uses it as a hard
filter, but no source is cited. Hur & Bruice's NAC definition includes angular
criteria as well as a distance. If 3.7 Å is not theirs, the selection filter is
undocumented and an examiner can ask where it came from.

**Fix.** Read the Hur & Bruice definition and either cite it or state the
criterion as this work's own with a geometric justification. If their definition
includes angles, record whether the selected frames satisfy those too — the
trajectory is still on disk, so this is a read-only re-analysis.

**Effort:** an afternoon of reading plus a short script.

### A2. The selection log was never committed  ☐

`step12a_select.sh` prints the per-site competence percentages and the
qualification decision, but that output is not in either repo. There is
currently no committed record of *why* CHA#1 and CHA#3 were excluded.

**Fix.** Re-run `step12a_select.sh` with the same arguments (stride 5, N 12,
3.2, 3.7, 0.5) and commit the log. The script is deterministic and read-only on
the trajectory, so this reproduces the existing manifest exactly and simply
captures the reasoning. **Verify the regenerated manifest is byte-identical to
the committed one** — if it is not, something has changed and that is itself a
finding.

**Effort:** minutes.

### A3. All 12 frames come from one site, contradicting the stated intent  ☐

`step11_trajectory_analysis.md` states the criterion as *"Draws from all three
sites, weighted toward CHA#2"*. The manifest is 12/12 CHA#2. The `site_min=0.5`
filter excluded CHA#1 and CHA#3, whose mean forming distances (4.15 and 3.83 Å)
lie above the 3.7 Å cutoff.

This is not necessarily wrong — competent frames are the ones you want, and
CHA#2 is described as "a textbook Michaelis complex" with Arg90–O13 locked at
2.92 Å for 100% of frames. But the ensemble samples conformational variation
**within a single active site**, not across three, and the note says otherwise.

**Fix.** Decide and document. Two defensible positions:

- *Keep one site.* Argue that a barrier ensemble should sample competent
  conformations, and that CHA#1/#3 are transiently bound rather than
  catalytically poised. Correct the `step11` note so intent matches outcome.
- *Add the other sites.* Argue that site asymmetry at 20 ns is finite-sampling
  symmetry-breaking (as `step11` itself concludes) and that excluding two of
  three sites discards real conformational diversity. This would need frames
  drawn from CHA#1/#3 during their competent excursions.

**Recommendation:** keep one site and correct the note. The excluded sites fail
the near-attack criterion on average, so paths from them would start further
from reaction and are not comparable. But say so explicitly.

### A4. Frame 820 is not a representative frame  ☐

Frame 820 is **idx 1 — the earliest competent frame in time**, chosen by
position in the list rather than by any property. Among the twelve:

- Arg90–O13 = 3.130 Å, **9th of 12** (median 2.889, so 0.24 Å looser than typical)
- forming distance 3.220 Å, **4th of 12** (tighter than typical)

Since the literature attributes TS stabilisation largely to Arg90, a loose
Arg90 contact is the condition under which a high barrier would be expected —
and the barrier is high. This is an observation, not a demonstrated cause.

**Fix, in order of increasing cost:**

1. *Report the ensemble mean as the Phase-1 barrier*, with frame 820 identified
   as the fully characterised member. Cheapest and matches the literature, which
   quotes averages.
2. *Additionally* run the full characterisation — reduced-region TS
   optimisation, frequencies, IRC — on a **median frame** (14155: Arg90 2.920,
   form 3.284, both near the middle). This would let the thesis say the saddle
   is genuine on a representative frame, not only on an atypical one.
3. Full characterisation on every frame. Not warranted.

**Recommendation:** do 1, and do 2 if the ensemble shows frame 820 to be an
outlier. Option 2 is roughly one extra frame's worth of TS work.

### A5. Sample size may be too small  ☐

My earlier advice that five frames would suffice assumed a spread of ~0.7
kcal/mol. That was a guess where a measured value was available: **Agbaglo
report ±2.62 kcal/mol across 250 snapshots of this enzyme.** If the spread here
is comparable, n = 5 gives a standard error near ±1.2 and n = 12 near ±0.76.
Against a 3.3 kcal/mol discrepancy with experiment, ±1.2 cannot resolve
anything.

Claeyssens used **16** enzyme pathways.

**Fix.** Run all twelve. The remaining six are already prepared on disk by
`step19a`. Decide after the first five report: if the sample standard deviation
is under ~1 kcal/mol, twelve is comfortably enough; if it approaches Agbaglo's
2.62, twelve is the minimum and the sem should be quoted prominently.

**Effort:** six more frames × (reactant + scan + product + NEB), in parallel.

### A6. No autocorrelation analysis justifies frame independence  ☐

The twelve frames are spaced ~1,670 ps apart, which is almost certainly enough
for independence, but nothing demonstrates it. A mean over correlated samples
has a smaller *apparent* error than it deserves, so this bears directly on the
error bar being quoted.

**Fix.** Compute the autocorrelation time of the forming C1–C6 distance and of
the Arg90–O13 contact over the production trajectory, and confirm the frame
spacing exceeds it — ideally by several multiples. Read-only on `prod.nc`, using
the existing stdlib NetCDF reader from `step11c` (cpptraj is broken
cluster-wide).

**Bonus:** this also gives an effective sample size, which is the honest
denominator for the standard error.

**Effort:** one script, minutes to run.

---

## B. Deliberate protocol decisions

### B1. Reactant-start sampling versus TS-restrained sampling  ☐

**What Claeyssens did.** Ran SCCDFTB/CHARMM22 QM/MM MD with chorismate
restrained near the TS (r = −0.3 Å), saved 16 structures from 60 ps at 4 ps
intervals after 500 ps equilibration, then generated each pathway by restrained
optimisation outward in both directions.

**What this work does.** Selects competent *reactant* frames from unrestrained
classical MD, optimises the reactant, scans forward to product, then runs
NEB-CI between the optimised endpoints.

**Why this matters.** In their scheme the protein relaxes around a TS-like
substrate throughout sampling, so the enzyme is already partly organised for the
TS and the barrier omits some reorganisation cost. In this work the protein is
equilibrated around a genuine Michaelis complex and the path pays for whatever
reorganisation is needed. That predicts a **higher** barrier here, which is what
is observed (16.00 versus 11.3).

**This is a candidate explanation for the entire discrepancy** and should be
tested rather than assumed.

**Options:**

- *Keep reactant-start, argue it is more physical.* The enzyme rests in the
  Michaelis complex between turnovers; reorganisation is part of the barrier.
  Free, but needs the argument made explicitly and the difference from
  Claeyssens acknowledged.
- *Add a TS-restrained set for comparison.* Would require QM/MM MD with the
  substrate restrained near the TS — a capability this workflow does not
  currently have — then paths from those structures. Substantial new work, but
  would settle the question and would be a genuine contribution: nobody appears
  to have compared the two sampling choices directly for this system.
- *Switch entirely to TS-restrained.* Discards the current ensemble and matches
  the literature protocol. Only worth it if the goal is reproduction rather than
  a defensible independent result.

**Recommendation:** keep reactant-start, state the reasoning, and note the
comparison as a limitation. Revisit only if the ensemble mean remains far from
the literature after A5 and A6 are closed.

### B2. Path method — this work is already better  ☐

Claeyssens used **adiabatic mapping**: restrained optimisation in steps along a
distinguished coordinate. That is path-dependent, can suffer hysteresis, and
does not locate a true saddle point. Their own earlier paper (Ranaghan 2004)
acknowledges "no configurational averaging is taken into account" as a
limitation of the approach.

This work uses NEB-CI followed by eigenvector-following TS optimisation, with
frequency verification (one imaginary mode, −313.30 cm⁻¹) and IRC connecting the
intended basins.

**Action:** none needed — but say so in the methods. This is an improvement over
the reference protocol and currently goes unclaimed.

### B3. Sampling window — this work is also better  ☐

Claeyssens sampled 16 structures from a **60 ps** window at 4 ps intervals.
This work draws 12 frames from **20 ns** at ~1,670 ps intervals — roughly 400×
better decorrelated.

**Action:** state it, and support it with A6 so the claim rests on a measured
autocorrelation time rather than on the spacing alone.

---

## C. Comparison and reference-state items

### C1. The comparison to experimental ΔH‡ is not like-for-like  ☐

+16.00 is a potential-energy barrier. The experimental 12.7 ± 0.4 is an
activation enthalpy including zero-point and thermal contributions. The
frame-820 frequencies already exist (612 displacements on each endpoint), so
this is arithmetic, not new computation.

Note Claeyssens' own position: they argue entropic, zero-point and thermal
contributions are small for this reaction and similar in both environments, so
potential-energy comparison is acceptable. Fine — but state it rather than
leaving the comparison implicit.

**Fix.** Compute ZPE and thermal corrections for frame 820 and report ΔH‡
alongside the potential-energy barrier.

### C2. The +17.47 reference state needs a diagnostic  ☐

The bare barrier uses CPCM at ε = 4 on enzyme-derived geometries. Two questions
are open: how much of the 17.47 is the continuum doing, and is the def2-SVP
result an artefact of having no diffuse functions for a dianion (vacuum HOMO is
+0.078 Eh, i.e. unbound).

**Fix.** Four single points — {vacuum, CPCM} × {def2-SVP, def2-SVPD} at reactant
and TS, reusing the committed geometries. Seconds each. If the vacuum barrier
moves substantially between bases while the CPCM barrier does not, that
demonstrates the continuum is doing necessary work and that a vacuum reference
would be unreliable.

### C3. Decide what "the Phase-1 barrier" is  ☐

The thesis must state, explicitly and once, whether the quoted enzyme barrier is
frame 820's +16.00 or the ensemble mean. Both are defensible; leaving it
ambiguous is not.

**Recommendation:** quote the ensemble mean ± sem as the barrier, with frame 820
named as the fully characterised member and its value given. This matches how
Claeyssens and Agbaglo report, and it is the honest presentation of what was
computed.

---

## D. Suggested order

1. **A2** regenerate and commit the selection log — minutes, no dependencies
2. **A6** autocorrelation analysis — one script, needed for the error bar
3. **A1** verify the NAC criterion against Hur & Bruice
4. **C2** vacuum/def2-SVPD diagnostic — seconds of compute
5. *wait for the five NEB barriers*
6. **A5** decide on running the remaining six frames, based on the spread
7. **A4** decide whether a median frame needs full characterisation
8. **C1** ZPE and thermal correction
9. **A3, B1, B2, B3, C3** — write the decisions into the methods

Items 1–4 can all proceed while the current jobs run.
