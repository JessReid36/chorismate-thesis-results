# Write-up skeleton and provenance state — 3 November 2026

Built by a full read of all four repositories at `chorismate-thesis-code@f0cbdb0` (branch
`tier1-realism`), `chorismate-thesis-results@cbd9331`, `consolidated_works@794dcca` and
`chorismate-refs@1401ed3`, plus the frozen sibling `chorismate-thesis-code@acf133b`
(`rebuild-cleanroom`). Four independent subject sweeps, each required to take every number from a
raw output file rather than from prose.

**This document is a map, not a result.** It carries no new measurement. Its job is to say, for
each part of the thesis, what is established and citable, what is superseded, what cannot be
sourced, and what is blocked on a decision. Every number in it names the file it came from.

## 0. How to read the status tags

| tag | meaning |
|---|---|
| `[RAW]` | re-derived from a raw ORCA/MD output in this sweep |
| `[SUMMARY]` | taken from a committed report or RESULT file, not re-derived |
| `[UNSOURCED]` | asserted in prose with no committed file behind it — **do not quote** |
| `[SUPERSEDED]` | correct for its own conditions, replaced for the thesis |
| `[RETRACTED]` | wrong; must never appear as a result |
| `[DECISION]` | blocked on Jessica, not on work |

**Reading rules that govern every number here** (project's own, each learned from an error):
last `FINAL SINGLE POINT ENERGY` in an ORCA output, never an earlier one; the FINAL frame of a
`*_trj.xyz`, never the first; the converged NEB iteration, never a transient; the energy column of
`final_band.txt`, never trajectory comment lines; and NEVER the comment energies in
`knarr_MEP_FULL.xyz`, which are spring-augmented.

**Numerical floor.** `cs_stage6/NUMERICAL_FLOOR_20261101.md`, measured over 937 committed runs:
**2.194e-11 Eh = 1.4e-08 kcal/mol = 96 ULP**. No energy comparison anywhere in this thesis may be
set tighter than that.

---

## 1. Phase 1 — the enzyme system and the reference barriers

**STATE: verified and citable.** Steps 01-19 are consolidated in `consolidated_works` with per-step
manifests, interpretation notes and 15-45 recorded passing checks each. `INDEX.tsv` reads
"verified, drafted" for steps 01-18; step 19 (ensemble) is PROVISIONAL.

### 1.1 Build
System construction, steps 01-12: input acquisition, terminal repair, cleanup, substrate placement,
Arg63 provenance, acceptance freeze, protonation, ligand GAFF, tleap build, MD, trajectory analysis,
frame selection. Canonical home `consolidated_works/01_*` through `12_*`.

### 1.2 Experiments
QM/MM setup and the reaction path, steps 13-18: bridge and smoketest, DFT single points, path
endpoints and restraint scan, NEB-TS, reduced-region OptTS, IRC. Step 19: the 30-frame ensemble.

### 1.3 Results — the reference barriers

| Quantity | Value | Status | Source |
|---|---|---|---|
| Enzyme QM/MM barrier, frame 820, 102-atom consistent region | **+16.00** (exactly +15.9995) | `[RAW]` retained-final | `18e_reactant_reduced/reactant_reduced.out`, `18c_reduced_region/ts_reduced.out` |
| Reaction energy | **-13.15** (exactly -13.1520) | `[RAW]` | + `18f_product_reduced/product_reduced.out` |
| TS character | one imaginary mode, **-313.07 cm-1** | `[RAW]` | `ts_reduced.out` after `OPTIMIZATION RUN DONE` (line 96542) |
| Cross-check triplet | OptTS 16.00 / NEB-CI 15.94 / relaxed scan 16.37 | `[SUMMARY]` | `phase1_system_dev/BARRIER_FINAL.md` |
| Substrate dianion, no external charges, CPCM eps=4 | **+17.47** | `[SUMMARY]`, reproduced within a 1.0 gate | originates `phase2b_charge_design/05_optimise/` @ `ad09dfe`; reproduced `07_rebuild/L0_groundtruth/` @ `acf133b` |

Frame provenance verified: all 45 selected MD frames reproduce the forming-bond C6-C1 distance
recorded in their selection manifests, 15 from `prod.nc` and 30 from `prod_ext.nc`, zero mismatches
(`checks/verify_frame_provenance.py`). Frame 820 lies inside the first trajectory.

### 1.4 Do not quote
- `15.08` `[RETRACTED]` — mixed active region: 102-atom TS minus a ~1959-atom-region reactant. The
  reactant mismatch alone is 0.9168 kcal/mol.
- `15.3` `[RETRACTED]` — never committed to either repo. Its only appearance was the stale
  results-repo duplicate of `notes/model_fidelity_validation_framework.md`, synced 2026-11-03.
- `15.771` `[SUPERSEDED]` by +17.47.
- The starting-Hessian frequency pair `-313.30 / -18.65` — printed by ORCA before cycle 1. The
  second mode does not exist in the converged structure.

### 1.5 Open
- Step 19 ensemble is PROVISIONAL; gradient -0.998 (n=22) against a published -0.95.
- `05_qmmm/24_sp_barriers` holds 30 frame directories with a full plan/amendment apparatus and
  **no committed barrier summary**. Any number from there must be read from individual outputs.

---

## 2. The charge representation — what a "charge" physically is

**STATE: the Stage 1-4e arc is sound and superseded in its central conclusion by Stage 6.**

### 2.1 Build
A charge is a **GOCAT-style quasi-atom**: one ORCA MM site carrying continuous `q` in [-1, +1] with
a single fixed Lennard-Jones sphere, baseline **Amber N, R\* 1.824 A, eps 0.170** (full `R_min`
3.648 A), spheres frozen during validation. Defining document
`phase2.2/CHARGED_SPHERE_DEVELOPMENT_APPROACH.docx`. Per-site energy `ddE = a*q + b*q^2 + dE_LJ`.
Sphere spacing >= **3.25 A** = 3.648 / 2^(1/6).

The option space was closed first, in `step_7b_charge_representation_options.md` (repo root):
QM/MM-with-LJ rejected at the time because ORCA refuses CPCM with QM/MM; Gaussian-smeared charges
**unavailable** (`.pc` is strictly four columns; ORCA's Gaussian machinery exists only inside CPCM);
ghost atoms rejected on theory; stock capped ECPs rejected on a non-physical distance scan;
increased standoff rejected as circular against BsCM's own 2.63-3.43 A residues.

### 2.2 Experiments
Group A: does the software do what the model assumes (WP1 combining rules, 648 MM single points;
Stage 1 element label / fractional charge / frozen-sphere cancellation). Group B: where a sphere
comes to rest (Stage 2 rigid model, Stage 3 QM/MM, WP4/WP5). Group C: is a bare positive charge
electronically safe (Stage 4, 4b, s11). Group D: does the representation change the answer (Stage
4c basis, 4d enzyme yardstick, 4e five levels of theory). Group E: Phase 2b relaxation under a bare
field.

### 2.3 Results
`[RAW]` verified in this sweep: Stage 1 single points -836.340705524817 / -836.144202020935 /
-836.240335906898; Stage 4c bare barrier at fixed geometries **+16.634**; QM-only ddE **-10.938**,
`dE_LJ` **+1.641**, QM/MM total **-9.297**; the sphere row literally
`N 1.000000 -0.170000 3.648000 -0.085000 3.648000`.

Established: the LJ wall is exactly what the rigid model assumes; a bare charge collapses to
0.95-1.02 A where the sphere stops at 2.54-2.71 A; Stage 4e finds the A matrix's **sign robust**
across five levels including MP2 (k 0.880 vs MP2 sets a ~12% method uncertainty).

### 2.4 The overclaim risk — read this before writing section 2
**Stage 4b's B1 is a FAIL** at def2-SVPD and contact: deviation from trend **-1.432** against a 0.5
limit, `b` **32.6%** against a 10% limit (`cs_stage4b/STAGE4B_REPORT.txt`). The decision record
(`CHARGE_MODEL_DECISIONS.md` lines 177-180) states only that the pseudopotential sphere
"reproduces the bare sphere at def2-SVP (representation check PASS: residual 0.284)" and then makes
it "the representation used for every def2-SVPD check of final designs". Both statements are true
and they concern **different checks**. Written as they stand, a reader concludes the pseudopotential
sphere is validated at def2-SVPD. **It is not.** Both verdicts must appear together.

### 2.5 Do not quote / cannot source
- `[UNSOURCED]` "the pseudopotential removes about 95% of the def2-SVPD trap at contact" — no file
  prints it; it is 94.5% derived from Stage 4b exploratory figures. A derived claim, not a result.
- `[UNSOURCED]` "WP4's methylguanidinium arm failed on automatically assigned torsion and improper
  parameters" — "torsion"/"improper" appear in none of the WP4 records. `WP4_REPORT.txt`'s own
  recorded reason is the CZ...O window.
- `s13_lj_test/` used a **sodium** sphere, not Amber N, and its producing script exists only at
  commit `b9e5672`. `s13_lj_test2/` has no criteria file, no report and no first-party analysis.
- `s15b_density/` is **not** a results directory: its producer is
  `s15b_regen_density.sh.REJECTED` ("WRITTEN, RUN, AND WRONG").

### 2.6 Stale pre-registrations with no erratum pointer
`PHASE22_PLAN.txt` section 2.3 is still headed "SMEARED CHARGES, NOT POINT CHARGES <- the main
physical change" and section 4 still makes the smearing width a calibration target. All of it is
dead (ORCA cannot do it); the correction lives in `PHASE22_PLAN_UPDATE_20261009.md` line 37 and
`step_7b`. The plan is pre-registered and deliberately not rewritten, but unlike
`LIBRARY_ERRATUM1_20261020.md`'s practice it carries **no in-file pointer to its correction**. Same
for section 3.1 "One layer, as agreed" (superseded by the two-layer decision of 19-20 October) and
for `s11_probe_scan_result.txt` Finding 1.

`s11` Finding 1 deserves its own line, in the project's own words
(`cs_stage6/STAGE6_ASSESSMENT_20261022.md`): "**The scan that found nothing wrong at 1.5 A was run
in the one condition that cannot show it... Both are in the repository, they disagree, and the
production pipeline inherited the reassuring one.**" Generalised by `STAGE6_ERRATUM7` E7.9: "a
compact basis does not prevent electron spill-out; **it conceals it**. EVERY COMMITTED STAGE 6
DESIGN WAS EVALUATED AT def2-SVP."

---

## 3. The grid and the A matrix

**STATE: four distinct lineages. Confusing them is the principal write-up hazard.**

### 3.1 The four lineages

| | Sites | Surface | Environment | Status |
|---|---|---|---|---|
| **A1** legacy | **331** | 3 shells 2/3/4 A, r_min 1.5 | CPCM(eps=4) | in `SUBMISSION_MANIFEST.tsv` as `final` |
| **A2** Poisson rebuild | **1448** | 3 shells 3/4/5 A, r_min 1.0 | CPCM(eps=4) | committed, **no manifest rows** |
| **A3** extensions | 1224 / 1041 / 3579 | shells to 15 A | CPCM(eps=4) | orphaned, producers absent |
| **B** ensemble grid | **233** | ON the union vdW surface, floor 2.5 A | **in vacuo**, 30 frames | current for the MILP |
| **C** two-layer sphere grid | **2769** dev / **2626** prod | two layers, floors by charge | **in vacuo**, per frame | current for charged spheres |
| **D** cleanroom lattice | **17028** | 0.7 A Cartesian | CPCM(eps=4) | frozen branch only |

All counts `[RAW]`, counted directly from the committed datasets in this sweep.

### 3.2 The environment split — the most consequential inconsistency
`[RAW]` Lineage A densities, `phase2b_charge_design/02_singlepoints/sp_reactant.inp` line 1:
`! B3LYP D3BJ def2-SVP def2/J RIJCOSX CPCM KeepDens` with `%cpcm epsilon 4.0`.
`[RAW]` Lineage B densities, `05_qmmm/20_invacuo/sp_02450_R.inp` line 1:
`! B3LYP D3BJ def2-SVP def2/J RIJCOSX TightSCF` — **no CPCM anywhere in the file**.

And `PHASE22_PLAN.txt` section 2.2 rules that a continuum must not sit beside the charges, "because
a continuum next to the charges supplies the same electrostatic stabilisation the charges are being
optimised to provide."

**Consequence: every Dv number in `GRID_DESIGN_DECISIONS.md` section 7 is a CPCM(eps=4) quantity and
the in-vacuo A matrix is a different physical quantity. They must never be tabulated together.**
Independently flagged from the Stage 6 side as inconsistency 1 of
`RESULTS_charge_representation_domain_DRAFT`.

### 3.3 Build / Experiments / Results
Build: A1 four-step SDF pipeline; A2 Poisson-vs-CVT package with convergence and envelope tests; B
`s12_build_grid.py` placing sites ON the union vdW surface after DTHESIS Eq. 2.16, with
`min_approach` a **floor on the site radius** rather than a filter; C `cs5_grid.py` + `cs5_floors.py`
building two layers whose radii are floors by charge, with deterministic greedy Poisson thinning so
a rerun reproduces the grid byte for byte; D a plain Cartesian lattice with an LJ-equilibrium
standoff.

Alignment underpins everything in lineages B and C: `s16_align_frames.py`, Kabsch on an 8-atom
rigid core, one transform fitted from the reactant and applied unchanged to that frame's TS and P.
Its own docstring records why: centroid spread 10.50 / 13.59 / 25.06 A over 30 frames against a
~6 A molecule.

Results: A2 grid quality `[SUMMARY]` Poisson min NN 1.000, CV 0.054, condition 81,832, zero pairs
under 1.0 A, against CVT's 0.552 / 0.112 / 2,230,234 / 299. A2 Dv `[RAW, re-derived]`
Dv in [-3.491, +3.847] kcal/mol per +1e, 903/1448 = **62.4% stabilising**; most stabilising site
idx 1107 at -3.4915; the stated ceiling "-3.847" comes from a **-1** at the most destabilising site,
not a +1 at the most stabilising one.

### 3.4 There is no Stage 5 production grid
`STAGE5_CRITERIA.txt` section 8 specifies `sites.tsv`, `L.tsv`, `A.tsv`, `AP.tsv`, `A_REPORT.txt`,
`STAGE5_REPORT.txt`. `cs_stage5/` holds only the criteria, two amendments, `floors.tsv` and
`exploratory/`. **Every multi-frame two-layer number in circulation — 2769 sites, the 1541/1228
layer split, the site-effect-map figures — is from the exploratory development set.** Only frame
42436 has production files. None of it may be presented as a Stage 5 result.

### 3.5 Do not quote / needs marking
- `[UNSOURCED]` the **-0.839** surrogate correlation — prose only, twice, in
  `phase2_charge_design/REACTANT_CONFORMER_DECISION.md`, no committed dataset.
- `[RETRACTED]` `dv_grid_dist.tsv` **at the results repo root** — the 252-site `*_realgeom` Dv map,
  retracted class, in the most visible location in the repo with no quarantine marker. Recommend
  moving it under the quarantined directory or adding a marker file beside it.
- `dv_grid_ensemble_mean.tsv` is the **not-for-results** pilot (ten pre-equilibration frames at the
  400 kJ spring). Committed **twice with different md5s**, neither carrying an in-file banner, and
  still named as a design input by `CHARGE_DESIGN_OBJECTIVE_NOTE.md` and `HANDOFF.md`. Those two
  documents are stale.
- `SUBMISSION_MANIFEST.tsv` presents the **331-point A1 grid** as `final` with thesis references
  Sec X.3 / Table X.2 / Fig X.5, while `GRID_DESIGN_DECISIONS.md` presents the 1448-point grid as
  "the grid, as built". `README_GRID_BUILD.md` states plainly that "every statistic in the current
  Section X.4 refers to the old 331-point grid and will need replacing." Three open items in
  `GRID_DESIGN_DECISIONS.md` section 10 cover this; **none is done.**
- The A3 extension grids cannot be regenerated on the authoritative branch: ten named producing
  scripts are absent from `tier1-realism` and the results repo. `GRID_EXT_2to12_README.md` declares
  the only committed dataset superseded **by a grid that was never committed**.

---

## 4. The optimiser

**STATE: four parallel lines, not one evolution. The live one is not where the write-up would look.**

### 4.1 The four lines
- **Line A** `phase2b_charge_design/05_optimise`, `05b_optimise_realism`, `05c_cradle` — the Tier-1
  discrete MILP ("certified screen") and its preorganisation-penalty variants. HiGHS native.
- **Line B** `phase2b_charge_design/06_convex_cutplane/solver/convex_solve.py` — HEAD only. An
  **L1-regularised LP**, not the convex QP the directory name and README promise.
- **Line C** `07_rebuild/L0-L4` on `rebuild-cleanroom` only — the clean-room stack, including the
  only committed convex **QP** (`solve_qp.py`, Clarabel) and the SOCP OEEF solvers.
- **Line D** `phase2.2/cs_opt_milp.py` (47 kB) + `cs_opt_null.py` + `s14_design_milp.py` +
  `OPTIMISER_CODE_README.md` — **the live production optimiser**, written against
  `OPTIMISER_DECISIONS_20261020.md`. Every `phase2b` optimiser is its predecessor.

**Any write-up section covering only the `phase2b` directories describes superseded code.**

Lines B and C are parallel executions of the same decision record
(`07_rebuild/DECISION_next_optimizer.md`), not a continuation of each other. Line D is a clean break
from all three.

### 4.2 Build — Line D, the one to document
Per site and admitted charge range: binary `y_ir`, continuous `q_ir`, at most one range per site.
Per frame `f`: `d_f = sum_i a_if q_i + sum_i L_if z_i`. **Objective: `dbar + (lambda/F) sum_f u_f`**
— mean plus lambda x semi-deviation, with `lambda = t(0.975,F-1)/(0.399 sqrt(F))` **not tuned**
(0.94 at F=30). Rules: `sum_i z_i = n`; `sum_i s_i <= B`; 3.25 A spacing as clique rows; one
no-good cut per earlier design. `s_i` stands in for `q_i^2` via **21 tangent lines** with the
constant **tied to the indicator** — a genuine formulation contribution: without the tie the relaxed
bound collapses and HiGHS returns nothing at n=4; with it the solve finishes at gap 0. 78 self-test
checks in 10 groups. LP-guided search makes n >= 10 reachable.

Line D honours decision O8: "certified" appears nowhere in its solve path, only `certified_gap` as
a reported property.

### 4.3 Results
`[SUMMARY]` Solver facts: CBC and HiGHS agree at 0.7827 on the distributed min-max, CBC 103.4 s vs
HiGHS 0.6 s; at 600 s on the real field CBC's K=7 incumbent (0.80, gap 0.046) is **worse than
HiGHS's certified 0.77** — an open gap can conceal a genuinely suboptimal design.

`[SUMMARY]` The one genuinely interesting placement result: K=1 distributed and K=2 max-lowering both
put a **+1 at the ether-oxygen valley, 3.84 A from O3** — the Arg90 role, found with no enzyme
knowledge. The same rediscovery recurs in Line C.

`[RAW, re-derived]` Relaxed geometries, Line A/05b/05c: every design **opens** the forming bond
rather than closing it — K2 `a_pot` 5.277 A, K2 `a_force` 4.060 A, K6 `a_pot` 4.243 A against a bare
reactant 3.124 A — and K6 `a_force`, K10 `a_pot`, K10 `a_force` and the r2SCAN-3c calibration all
**FRAGMENT**. Adding a 6-bead neutral cage made it **more** open (5.306 A), not less.

**Line D has produced no designs.** `OPTIMISER_CODE_README.md` states it twice in bold: "Nothing
either script produces on the development set is a result."

### 4.4 The novelty claim, as it now stands
Original claim (certified MILP, gap=0, as *the* contribution) **dropped 2 September 2026**
(`OPTIMISER_FORK_AND_WRITEUP_SCOPE.md` section 1) and re-affirmed as dropped on 20 October
(decision O8). The three surviving requirements: **not black-box, deterministic/white-box, novel
against GOCAT's GA / Sokalski's DTSS / Reiher's GdMC.**

**Proxy optimality is not catalytic optimality**, stated independently in three places. The
empirical demonstration is `results_proxy_ceiling.md`: a design the proxy scored at
`sum q*dV = -0.011` (i.e. *stabilising*) has a true NEB barrier of **+37.6** against a bare 17.47.

The defensible form, per `DECISION_next_optimizer.md`, is "certified optimum of a physically-grounded
**convex surrogate of the relaxed-path barrier**". **No such surrogate is validated.**

### 4.5 The gate that was never run
`DECISION_next_optimizer.md` section 2 names the barrier-correlation test as "**the decision-maker,
BEFORE any new optimizer**": take the designs in hand, compute their true relaxed barriers, plot
true barrier against objective. **No committed plot, table or script does this.** Yet both forks it
was meant to gate — the OEEF response optimiser and the steric cradle — were built and run. The
write-up must say which pre-registration was superseded by events.

### 4.6 Do not quote / needs recasting
- `[RETRACTED]` the max-lowering `barrier` column going negative from K=4 (-3.41, -8.07, -12.47,
  -16.68, -20.58, -24.42, -27.53) — present as a results table in three committed files.
- `[RETRACTED]` `results_uniform_field_catalysis.md` on the frozen branch still states "**The
  capacitor CATALYSES: 15.78 < 17.47 bare**" as a real result, **unmarked, sitting beside the file
  that retracts it** (`results_oeef_relaxed_NEGATIVE.md`, commit `eacab5e`, superseding `0db07f0`).
- `[RETRACTED]` `STEP2_PREORG_SWEEP_FINDING.md`'s "HIGHER-K designs retain MORE barrier-lowering at
  low distortion... Emergent, not imposed" — the by-construction artefact of the max-lowering
  objective presented as a chemical finding. Its own caveat three lines later says "NO barrier
  number in this sweep is trustworthy as catalysis."
- `[UNSOURCED]` `05c_cradle/03_certified_cover/` reports certified set-cover results at "gap 0.000
  all" and names four files. **None was ever committed to any branch.** The directory holds only the
  README.
- `[UNSOURCED]` `SURROGATE_SPACING_FIX.md`'s "verified" K4 sites 150/188/209/210 at 4.11 A and its
  "K3 +2.68 | K4 -0.85 | K6 -8.00 | K8 -13.14" — the committed sweep gives sites 13/51/131/209 and
  +0.76 / -5.45 / -8.92, and no K3 row. The same document states a 3.7 A threshold where the code
  enforces 4.7 A, so its own "verified" design would fail the rule that produced it.
- **"Certified" survives in five committed docstrings and READMEs** against O8, including
  `finalise_K.py`'s "with a provable optimality certificate (MILP, gap -> 0)... we find the
  provably-optimal K-charge set by MILP". First text an examiner would find.
- **A grep trap:** energies in the 05b/05c prose are **ASH QM/MM totals**, not ORCA
  `FINAL SINGLE POINT ENERGY`. They differ by ~0.7-0.8 Eh. Applying the project's own reading rule
  to those directories legitimately returns a different number from the prose. Any energy cited from
  there must name which quantity it is.
- Line B's thirteen designs have **zero screens** — no integrity verdict, no relaxed geometry, no
  barrier, and no `06_convex_cutplane` directory in the results repo at all. The m-series summary
  was overwritten.
- Route B's 14.39 / 6.40 / 7.23 are `[exploratory]`, reproducible from **neither branch alone**
  (runner only in non-tip commit `e74b031` on the frozen branch; its input design files only on
  `tier1-realism`), and **Route B's Arg90 charge is hand-placed, not optimised** — it is not an
  optimiser result and must not be presented as validating one.

---

## 5. Stage 6 — the domain of validity of the representation

**STATE: the largest and most recent body of work, and the least written up. D1-D23 unbroken.**

### 5.1 Build and convention
4958 files. A narrative layer of pre-registrations at the top level
(`STAGE6_DIAGNOSTIC<n>_<date>.txt`, committed **before** any run of that diagnostic exists, never
edited — changes go into dated errata/amendments), and a data layer of one subdirectory per
diagnostic holding `job.inp` / `job.out` / `job.property.txt` / `pc.pc` per run plus `PLAN.tsv`,
`INVENTORY.tsv` and three sha256 manifests. 1059 ORCA outputs. Readers are one committed
`cs6_d<n>.py` per diagnostic.

### 5.2 What the diagnostics jointly establish

| | Finding | Consequence for the thesis |
|---|---|---|
| **D5** | the two bases agree to <1.0 kcal/mol only up to lambda 0.50, **Sum\|q\| <= 2.880 e** | the honest domain |
| **D6.3** | the four-class CLEAN/POLARISED/STRAINED/COLLAPSED readability rule | the gate the whole draft rests on |
| **D9** | **no scalar on the charge vector survives** — Sum\|q\|, max\|q\|, n, Sum q^2 and peak local field all falsified | five candidate screens dead |
| **D11** | `r_safe` = **3.50 A**; every committed arrangement sits at **2.85-2.96 A** | "no design measured inside r_safe is interpretable" |
| **D12** | **no geometric descriptor** predicts the artefact | "the charge model must change — not the spacing, and not the surface" |
| **D14-A1 / D15** | the artefact is **not** confined to positive charges; the per-site sum does **not** bound the mixed-sign set | D14's premise destroyed |
| **D20** | SCF instability **onset at Sum\|q\| = 4.32 e**; correction up to **+9.5558 kcal/mol** (896% of the quoted budget) | invalidates every barrier at or above onset |
| **D21/D22** | every reported leg of every readable condition is a **verified SCF minimum** | the reported numbers sit on stable solutions |
| **D23** | `d_shield` is **a property of the ECP parameter set**; propagation factor runs **-9.314 to +2.279** | reverses D15 R1, D16 R1, D16 R3; terminal supersession of the whole `d_shield` line |

### 5.3 Results — the seven readable conditions
`[RAW]` All re-derived in this sweep from `job.out` last `FINAL SINGLE POINT ENERGY`. Control
barrier **+18.3323** (`d16/def2-SVPD/ctl_{R,TS}`). Designs lower the frozen barrier by **4.9965 to
10.6714**, giving barriers of **7.6609 to 13.3357**; every barrier positive.

**Labelling, mandatory.** Each is a **frozen single-point barrier in vacuo at def2-SVPD on one MD
frame**. Not an activation free energy, not a catalytic barrier. Four distinct bare barriers now
exist in the record and none may be quoted without its conditions: **17.47** (def2-SVP, CPCM eps=4,
L0 geometry), **16.00** (enzyme), **18.3323** (def2-SVPD, in vacuo, frozen), **18.4610** (def2-SVP,
in vacuo, frozen).

### 5.4 Correctly demoted
**`d_shield` is a diagnostic of the representation, not a reportable property of a design.** It is a
small residual of two larger terms; at n >= 5 the uncorrected discrepancy carries the *opposite*
sign to the reported quantity; the subtracted term moves 0.5-0.8 kcal/mol with basis and up to
0.9608 with parameter set; three of four arrangement-comparing statements reverse under He. The
draft's demotion is the right call and is sourced to D23.

### 5.5 The draft and its four errata
`writeup/RESULTS_charge_representation_domain_DRAFT_20261102.md` is corrected **in place**, with
each erratum the record of what changed. **E1 is the only substantive error** — a `max|q|` column
populated **from memory** rather than from each arm's `pc.pc`, three values wrong, caught by an
independent review in a separate session. E2, E3 and E4 are consequences of new work (D23 landing,
Claeyssens 2011 read in full, a data file written). The instability is in the subject, not the
drafting discipline.

**First fix:** the draft contradicts itself. Sections 4 and 6 report D23's results; **Sourcing gaps
item 3 still reads "ECP parameter sensitivity. Still unmeasured... 56 single points. Not yet
pre-registered."** D23 ran 2 November with **50** single points and *is* pre-registered. E2 rewrote
sections 4 and 6 and did not reach the gap list.

**One claim to soften:** section 3's "lower a frozen vacuum barrier by 4.9965 to 10.6714 kcal/mol,
which **brackets** that published range". The draft's own four stated mismatches each individually
undercut "brackets". "Is of the same order as" survives scrutiny; "brackets" invites the reader to
treat it as a match.

### 5.6 Structural defects in the Stage 6 record
- **The verification gates do not exist.** Nine committed documents, including the draft and three
  of its errata, cite `cs6_y47.py`, `y48`, `y53`, `y54`, `y55`, `y57`, `y58` as the scripts that
  re-derived every number. **None has ever been committed to any branch in any commit.** Every
  `cs6_d*.py` reader *is* committed. The numbers check out — all seven bare-arm pairs and the
  `d_shield` decomposition were independently re-derived in this sweep — but the project's stated
  defence against from-memory numbers is unreproducible, and E1 shows that defence has already
  failed once. **This is the most important gap in the project.**
- **No relaxation has ever run.** `relax/` holds 166 files and **zero** `job.out`. ORCA refuses the
  TS optimisation (`You cannot use transition state optimization for a Cartesian optimization`),
  twice — 21 October and 3 November, exit code 25. The `OptTS`/`coordsys cartesian` conflict is
  still open from 26 October. **Every Stage 6 barrier is a frozen single point.**
- **The relaxation targets are the wrong designs.** The committed targets are S6-5, S6-10 and S6-20
  at 3.00 / 4.38 / 5.76 e, which D20 places at or above the instability onset and D17 outside the
  readable window. Every condition the draft reports (1.0777-2.19 e) has no relaxation inputs except
  the one Amendment 3 added on 3 November.
- **D6's instrument has six measured defects and was never re-run.** Its control pool included
  geometry optimisations, its categories were not disjoint, its walker missed 415 completed runs,
  and runs carrying charges as `Ne>` centres were filed as **charge-free controls**, where they
  helped set the thresholds every charged run is judged against. D8 and D9 fixed the corpus and the
  detection; `cs6_audit.py` was deliberately not changed and **D6's thresholds were never
  re-derived.** The readability rule the draft gates on still carries thresholds anchored partly to
  a contaminated control pool.
- **The readability window is a disclosed non-blind test.** D6.0: the four thresholds were chosen
  **after** the Stage 6 outputs had been inspected. D9.0 is stronger: "its charge detector, model
  classes and readings were all developed by reading this corpus directly, in the same session that
  wrote the file." Both disclose it; neither repairs it. The chapter must say so where the window is
  claimed.
- **The walled (ECP) arms are VOID under the diagnostics' own inertness rule** at the arrangements
  the project most wants to read (S6-10's `wall0` at -0.7187, 2.4x the 0.30 limit; S6-20's at
  -0.6190), and `STAGE6_ERRATUM7` E7.8 records that the Ne ECP is used **outside its published
  octet assumption**. The right conclusion, from `APPROACH_POSITION_20261028.md`: **the wall is how
  the artefact is measured, not a model that may be adopted.**
- `[UNSOURCED]` **the "1.067 kcal/mol budget"** quoted as an absolute from D17 onward. D11.3 states
  a *relative* rule; 1.067 is its value at D12's sites 1988 and 1991 — **the largest among D12's
  thirteen voided sites.** Every "% of budget" figure in D18, D20, D21 and D22 inherits this.
- `[SUPERSEDED]` the **0.80 e** per-site cap still stands as the verdict of
  `qrefine/DIAGNOSTIC2_AMENDMENT1_RESULT.txt`, with no in-file marker, because results are never
  edited. `ERRATUM3` E3.1 withdrew it. The live figure is D17 R3's **0.5389-0.6500 e**.
- `cs_stage6` and `writeup` were grepped for every retracted value. **No retracted value is being
  presented as a result anywhere.** Every hit was coincidental digits, a section label, or an
  explicitly-labelled mention of a superseded value. **This part of the record is clean.**

---

## 6. Cross-cutting — the consolidated do-not-quote register

The authoritative list is `OPTIMISER_FORK_AND_WRITEUP_SCOPE.md` section 4a, amended 3 November.
Summarised here with what replaces each.

| Never quote | Use instead |
|---|---|
| enzyme 15.08 (mixed region), 15.3 (never committed) | **+16.00** |
| bare 15.771 (frozen proxy on a superseded geometry) | **+17.47** |
| capacitor 15.78 "catalyses" (derailed-scan artefact, `eacab5e`) | the negative result 29.77 / 46.37 |
| OEEF 21.32 scan | same class of artefact |
| all `*_realgeom` Phase-2 results; the "+10.9 exceeds enzyme" headline | nothing — omit |
| all K>2 max-lowering values as results | the max-lowering column is a diagnostic ceiling |
| "more charges do worse" | retracted; it confused per-charge efficiency with total lowering |
| "shell-ladder / K2 NEBs failed to converge" | `SHELL_LADDER_NEB_CORRECTION.md` shows clean single-peaked MEPs |
| `shell_restricted_sweep.py` and its conclusion | retracted (misread the 1.7 A grid floor as an atom-centre distance) |
| the -0.839 surrogate correlation | unsourced; no committed dataset |
| the 1.067 kcal/mol "budget" as an absolute | a relative rule's value at voided sites |
| the 0.80 e per-site cap | D17 R3, 0.5389-0.6500 e |

**A monotone "more charges -> lower barrier" trend in the max-lowering objective is an artefact of
that objective by construction, never a chemical finding.** Charges and geometry must be
**co-relaxed**; no violation was found in the current optimiser scope.

---

## 7. Decisions that block writing — these need Jessica, not more work

1. **`Sum|q| <= 6.0 e` vs `Sum q^2 <= B`.** `[DECISION]` The 6.0 e figure was decided 26 October.
   `claude/START_HERE_STAGE7_20261026.md` section 2 then recorded that it **inverts the measurement**
   (the defensible domain is 2.880 e), that it has **no committed source** — attributed there to
   "Claude's reasoning in conversation, 23 Oct 2026, conflating the six *literature-ranked* residues
   of the site-effect map with a charge budget" — and that it changes a pre-registered **form**,
   requiring a dated amendment plus a code change. **Neither exists**, and `cs_opt_milp.py`
   implements `Sum q^2`. The decision is recorded, contradicted, and unimplemented. Three options:
   pause the budget and state the measured domain; calibrate; or change the form by dated amendment.
2. **`B` has never been calibrated.** `[DECISION]` `B = 2.00 e^2` in every committed Stage 6 design
   is "the code default, NOT the calibrated B" (`relax/ARRANGEMENTS.txt`, `STAGE6_CRITERIA.txt`).
   Decision O3 scheduled the calibration for Stage 6; Stage 6 produces `G_0` and `kappa` instead.
3. **Does `phase2.2`'s CPCM objection retire the 17.47 anchor or recontextualise it?** `[DECISION]`
   Not recoverable from the commits.
4. **Which section of the thesis holds the Stage 6 results?** `[DECISION]` The draft was written as
   "section 6.3" and no outline in either repo defines one.
5. **Is 05b's preorganisation work a superseded dead end or a cited precedent for O2?** `[DECISION]`
   Neither `a_pot` nor `a_force` appears in Line D's formulation, which uses `G_add` instead.

---

## 8. The scientific question both subjects converge on

Stage 6 and the optimiser map reach the same place from opposite ends. D12: "**the charge model must
change** — not the spacing, and not the surface." `APPROACH_POSITION_20261028.md`: "**The optimiser
is trustworthy once the charge model is, and not before.**"

All three considered replacements are blocked, for stated reasons:
- **ECP / pseudopotential** — used outside its published octet assumption (`ERRATUM7` E7.8), fails
  its own inertness control at n >= 5, and fails Stage 4b's B1 basis-robustness test at def2-SVPD.
- **Gaussian smearing** — unsupported in ORCA (`.pc` is four columns) *and* ruled out by Marefat
  Khah's own paper.
- **Continuum (CPCM)** — removed for cause, and D2.3 shows it does not fix the response.

**No fourth route has been proposed anywhere in the record.** Experiment 0 (2 November) removed one
part of the ECP block by validating the convention and the He/Ne sets, but not the substantive
octet-assumption problem.

The one unmeasured quantity that would decide whether the current model can be rescued is named
first by both D12 and D13 and by `APPROACH_POSITION` section 4: **does the overpolarisation artefact
add across charges?** Every representation run to date carries **one** charge. What is established
is the additivity of *ddE* at def2-SVP (3.1% at n=2, 6.1% at n=3) — a different quantity. If the
artefact does not add, a many-charge design at small |q| may be faithful. If it does, a 20-charge
design is where it is worst and **every frozen Stage 6 number is affected.** Nothing in the record
distinguishes these, and it is the only item named as needing new HPC time.

On 27 October the decision was to improve the components until a design works rather than write up
the negative result. That decision stands on this one measurement.
