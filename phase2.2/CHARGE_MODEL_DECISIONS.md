# phase2.2/CHARGE_MODEL_DECISIONS.md - decisions taken without supervisor input, 6 October 2026

Five questions in the charge-model plan were held for the supervisor. They are decided here instead,
each with the evidence it rests on, so later work does not wait. Any of them can be reopened; the
evidence is listed so that reopening one starts from the same facts.

## D1. Design environment: vacuum, with a continuum check on final designs

**Decision.** The Phase 2.2 design and its validation stay in vacuum (no continuum), as already
implemented: A_v2 is built from in vacuo densities, and s11, s13 and s17 run in vacuum. Every final
design gets one CPCM (epsilon = 4) single-point check of its barrier lowering before it is reported.

**Evidence.**
- ORCA 6.0.1 refuses CPCM together with QM/MM ("CPCM or SMD ... requested together with QM/MM method",
  `step_7b_charge_representation_options.md`), so a charge site carrying Lennard-Jones parameters
  can only be validated in vacuum in this code.
- The GOCAT Diels-Alder study built its paths in the gas phase (Dittner & Hartke 2020: initial MEPs
  "in the gas-phase").
- `SOLVATION_DECISION_NOTE.md`: the bare dianion is electronically unbound in vacuum (HOMO +0.082 Eh
  at def2-SVP, +0.044 at def2-SVPD), but the barrier is insensitive to it (def2-SVP against def2-SVPD:
  0.090 kcal/mol in vacuum).

**What stays exposed.** The polarisation term b is the quantity most affected by an unbound
dianion, so WP7 repeats two sites at def2-SVPD. The same note warns that without a continuum the
charges may do "two jobs at once"; the final CPCM check is there to catch that.

## D2. What a design site represents: the charge centre of a cationic group

**Decision.** A +1 site placed by the optimiser stands for the **charge centre of a cationic group**
(for an arginine, close to CZ), not for one of its nitrogen atoms. It is validated with an all-atom
group whose centre sits on the site (D4). The single nitrogen-sized LJ site is kept only as a model
whose stopping distance is reported with its sensitivity (WP5), never validated against Arg90.

**Evidence.**
- In the committed force field the arginine's +1 is spread over the group: CZ +0.8076,
  NH1/NH2 -0.8627 each, NE -0.5295, H +0.3456 to +0.4478 (CD..HH22 sum +0.8755; committed
  `complex_solvated.ORCAFF.prms`, residue 217). A full +1 at a nitrogen position puts charge where the
  force field has -0.86 e; it has no counterpart in the system being imitated.
- GOCAT moved the same way, from abstract point charges to molecules from a library placed around
  the QM region (Behrens & Hartke 2021, "From Abstract Catalyst Design Via Electric Field Optimization
  Back to the Real World"), and Dittner & Hartke 2018 describe ORCA point charges as fractional
  "nuclear core" positions, i.e. abstract entities.
- WP5 (rigid model, `wp5_rigid_scan/`): a free +1 site started at the ether oxygen leaves it for a
  carboxylate in every frame and setting scanned. A single site cannot hold the Arg90-like O3 contact,
  which in the enzyme is held by the protein.

**Structural references for a group centre (Arg90 = residue 217):**
- own QM/MM, single validated path: CZ to O3 3.25 / 3.26 A (R / TS); Arg-carboxylate CZ to nearest
  O 3.23-3.27 A (`05_qmmm/18e`, `18c` reduced-region structures);
- 30 post-cut MD snapshots: CZ to O3 3.54 +- 0.17 A (3.22-3.88); CZ to nearest substrate O
  3.52 +- 0.17 A (3.22-3.84);
- crystal: Chook et al. 1993, Arg90 side chain to the analogue's ether O' 3.1 A (the Arg90 atom is not
  specified).
These fix WP4's acceptance windows (D-WP4 below). The final WP2 measurement on QM/MM geometries
follows C4 and C5.

## D3. Superposition of frames: accept s16's rigid-core fit

**Decision.** The common grid is defined in the frame reached by `s16_align_frames.py`: Kabsch fit of
each frame's reactant onto frame 20000's on the eight-atom core (six ring carbons, O3, C2), the same
transform applied to that frame's TS and product.

**Evidence.** A common grid across an MD ensemble needs a common frame; GOCAT never faced this,
because its frames lie on one path. `s16`'s docstring records the per-atom deviation that motivates
the core (ring and ether 0.05-0.11 A, carboxylate oxygens 0.29-0.47 A). The unaligned alternative was
tried and failed: A_v1 agrees in sign across frames at 4 of 580 sites (0.7%,
`archive_v1_unaligned/`). Everything is reproducible from committed files (s18 section 7).

## D4. Validation site model: an all-atom MM methylguanidinium, built by the substrate's protocol

**Decision.** The group used to validate a +1 site (WP4 arm 3, and later designs) is methylguanidinium
(CH3-NH-C(NH2)2+: arginine's guanidinium group, capped with a methyl at CD), treated as MM with electrostatic
embedding around the QM substrate. Charges: AM1-BCC; LJ: GAFF; i.e. the protocol Phase 1 used for the
substrate (`phase1_system_dev/local_workstation/step08a_am1bcc_charges.sh`, then GAFF typing). AM1-BCC
runs on the PC because `sqm` is broken on hpc1.

**Evidence and reasons.**
- MM keeps the QM region at -2: the field is added without adding electrons, so there is no
  charge transfer into a cation and no polyanion problem (Phase 2b's surrogate runs state the same
  reason, `phase2b_charge_design/relaxation_attempts/ash_guarded/mmsurr_run`).
- Behrens & Hartke 2021 use exactly this arrangement: a QM reactant embedded among MM molecules
  carrying force-field charges and LJ (OPLS-AA there).
- Measured once built (`wp4_site_models/`, wp4b audit): every atom type of the group (c3, h1, nh, hn,
  cz) carries exactly the LJ of the corresponding atom of the enzyme's arginine in the committed force
  field, so the LJ wall matches and only the charges differ.
- The AM1-BCC charges are smaller atom by atom than Amber's (CZ +0.52 against +0.81, terminal N -0.50
  against -0.86), but the potential they produce on the same geometry differs by 2.4% RMS around the
  group and by 1-3% at the hydrogen-bond acceptor positions (`wp4_site_models/WP4_ESP_COMPARE.txt`).
  What a neighbouring atom feels is the potential, so the group presents the enzyme's electrostatics.
- WP8 still uses the enzyme's own arginine (its force-field charges) to ask what a real group presents;
  methylguanidinium is the validation model for a design site.
- The earlier Phase 2b surrogate (hand-set charges C +0.64, N -0.80, H +0.46) is not adopted: the
  source of those values is not recorded. It is kept as a cross-check.
- References to obtain for the library (methods only; no number is taken from them here): Wang et al.
  2004 (GAFF), Jakalian, Jack & Bayly 2002 (AM1-BCC).

## D5. Reference for judging a design

**Decision.** A design's barrier lowering (in vacuum, frozen density first, then relaxed) is judged
against three references, in this order:
1. **zero**: the bare substrate's own in vacuo barrier, the design environment's baseline;
2. **the enzyme, same model chemistry**: the differential TS stabilisation of the same frames in the
   enzyme, stab_TS = QM/MM barrier minus in vacuo barrier at the same geometries (Claeyssens
   et al. 2011: E_INTERACTION = E_QM/MM - E_QM, with E_QM the substrate alone at the QM/MM geometry, so
   the difference of E_INTERACTION between TS and reactant is exactly that barrier difference);
3. **experiment, qualitatively only**: Burschowsky et al. 2014's Arg90 to citrulline differential
   (5.9 against 0.6 kcal/mol), which is a free-energy difference in water for a neutral urea, not an
   in vacuo energy for a removed charge.

**Evidence.** Reference 2 shares the frames, functional and basis with the design and is computed
exactly as the harvester's stab_TS column. Its values wait for C4 and C5, which change the barriers.
Reference 3 is quoted from the paper itself (Burschowsky 2014), with the caveats stated there
(orientation of the urea assigned "based on chemical sense").

## D-WP4. WP4 (the s13 rerun) as run - updated 6 October 2026, before any result was read

- **Frame**: 41786 (no reactant-end dip, NEB-CI; untouched by C4 and C5), so WP4 never needs redoing.
- **Start**: the enzyme's own QM/MM structure at that frame. Arg90 there bridges the ether O3 and the
  carboxylate O2 (N to O3 2.83 A, N to O2 2.71 A, CZ to O3 3.55 A). Arms a and b start at Arg90's CZ,
  which lies 0.11 A from the AM1-BCC group's charge centre (0.19 A with Amber's own charges); arm c sits on
  Arg90's own atoms, CG replaced by a methyl hydrogen.
- **Arms**: (a) bare +1, run as a QM/MM site with zero LJ (control, expected to collapse); (b) +1 with
  Amber's N LJ (model property; rigid-model expectation 2.584 A to O2); (c) methylguanidinium (D4), held
  at CD and HD1 only, as the literature holds a side chain at its backbone atoms.
- **Freedom**, each variant identical across the three arms:
  - *anch* - the four ring carbons farthest from CZ (C5-C8) held, standing in for the pocket; every
    atom of the contact region free. This is the validation test. (A first draft held s16's alignment
    core, which contains O3; that would have fixed the O3 contact by construction.)
  - *free* - all substrate atoms active, optimised in ORCA's redundant internal coordinates. When the
    fixed site is not linked into ORCA's coordinate set the substrate cannot translate (armb_free:
    centroid fixed to 1e-6 A), so these are reported as internal motion only.
  - *freecart* - the same, in Cartesian coordinates (ProjectTR false), so the substrate may translate
    and rotate as a whole in every arm.
- **Acceptance for arm c, anch**: the bridge is kept (one N-H to O3, one to a carboxylate oxygen); nearest
  N to O within 2.62-3.11 A and CZ to nearest O within 3.18-3.86 A (Arg90 MD mean +- 2 sd); each contact's
  change from the enzyme's QM/MM value at this frame reported.
- **Criteria files**: phase2.2/wp4_s13_rerun/WP4_CRITERIA.txt and WP4_CRITERIA_CARTESIAN.txt.
- **Deferred to WP6**: in armb_free the forming C1-C6 distance opened from 3.16 to 4.27 A. Whether a
  site pulls the substrate out of its near-attack geometry, or the dianion relaxes that way in vacuum on
  its own, needs a no-site control; it belongs to WP6, not to the representation test.

## Update 9 October 2026 - after Stage 4b (plan: PHASE22_PLAN_UPDATE_20261009.md)

The end goal was restated: charges optimised on a van der Waals-surface grid, the top ~10 tested for catalysis;
mapping back to residues is out of scope. The decisions above are updated as follows (reasons in the plan, section 4).

- **D2 relaxed.** A site is an abstract charged quasi-atom (GOCAT), not the charge centre of a named group. How close
  a site may sit is set by the sphere's measured contact distance (Stage 5), not by arginine distances.
- **D4 withdrawn.** Designs are validated with the spheres themselves (Behrens' one-embedding scheme, spheres frozen),
  as in the approach document's validation protocol. WP4 arm c, WP8 and the final WP2 measurement are dropped with it.
- **D-WP4.** Arms a and b stand as recorded (bare +1 collapses; the nitrogen-sized sphere stops at 2.54-2.71 A).
  Arm c is not pursued (out of scope).
- **D1.** Unchanged. WP7 (b at two sites, def2-SVPD) is replaced by Stage 4c (`cs_stage4c/`).
- **D5.** Unchanged. If Stage 4c sends magnitudes to def2-TZVPD with pseudopotential spheres, reference 2 is
  recomputed at that level, so a design and the enzyme are always compared at one model chemistry.
- **Stage 4/4b outcome**, as the approach document required ("either way D2 and D4 are updated"): with def2-SVP the
  bare sphere stands; a diffuse basis needs the Ne-type pseudopotential (Stage 4b; exploratory note in
  `cs_stage4b/exploratory/`). Smeared charges, the approach document's first fallback, are not available in ORCA.

## Update after Stage 4c (9 October 2026)

- **D5.** The 9 October note above ("if Stage 4c sends magnitudes to def2-TZVPD ..., reference 2 is recomputed at
  that level") is superseded: reference 2 stays at def2-SVP, like-for-like with the designs' production level, and
  moves to def2-SVPD only if a final design's catalytic verdict differs between the two levels
  (`cs_stage4c/STAGE4C_AMENDMENT1.txt`, decision rule; `PHASE22_PLAN_UPDATE_20261009.md`, Stage 4c section).
- **D1.** Unchanged. Stage 4c adds a reason for its CPCM check: in vacuum, net-negative arrangements put the HOMO at
  +3 to +6.5 eV (`cs_stage4c/exploratory/`).

## Addendum (9 October 2026)

- **D5.** Reference 2 will be computed at both def2-SVP and def2-SVPD, whatever the designs show
  (`cs_stage4c/STAGE4C_AMENDMENT1_ADDENDUM1.txt`). This supersedes the "only if" condition in the Stage 4c update
  above. Not yet run; scheduled after C4.

## Update after Stage 4c Amendment 1 (10 October 2026)

- **Charged sphere at diffuse levels.** The Ne-type pseudopotential sphere, corrected by the same spheres at zero
  charge, reproduces the bare sphere at def2-SVP (representation check PASS: residual 0.284, max 0.739 kcal/mol;
  `cs_stage4c/STAGE4C_AMENDMENT1_REPORT.txt`). It is the representation used for every def2-SVPD check of final
  designs; the bare LJ sphere at def2-SVP stays the production representation.
- **D5.** Addendum 1's condition (the representation check passes) is met, so reference 2 at def2-SVPD can use the
  pseudopotential embedding described in `cs_stage4c/STAGE4C_AMENDMENT1_ADDENDUM1.txt`. Still scheduled after C4.
- **D1.** Unchanged.

## Addendum (10 October 2026)

- **D5.** A design is called catalytic only if it is catalytic at both levels, each against the reference at the same
  level; at one level only, it is "not established" (plan, addendum to the Stage 4c Amendment 1 update, reporting
  commitment 1).

## Update: Stage 4d (10 October 2026)

- **D5.** Stage 4d measures the enzyme of frame 41786 with the design yardstick (frozen geometries, QM plus LJ;
  `cs_stage4d/STAGE4D_CRITERIA.txt`). If its PC1 passes, that value is the screening reference for frozen-geometry
  design numbers. Reference 2 (the relaxed QM/MM barrier difference) is unchanged and alone decides catalysis.
- **D2, D4.** Unchanged: a site is an abstract quasi-atom and designs are not mapped to residues. Stage 4d compares
  spheres with Arg90 and Arg7 only to measure how far a point charge stands in for a real charged group (PC3).

## Update after Stage 4d (10 October 2026)

- **D5.** Stage 4d's PC1 failed, so the enzyme's frozen-geometry value is not a screening reference and no frozen
  design number is compared with an enzyme number. Reference 2 (the relaxed QM/MM barrier difference) is unchanged and
  alone decides catalysis.
- **D1.** Unchanged. Reversing the enzyme's charges around the dianion in vacuum drops its HOMO-LUMO gap to 0.55 eV
  (Stage 4d, NC1): another case of the vacuum limitation that D1's CPCM check of final designs addresses.

## Update after Stage 4e (10 October 2026)

- **Design objective.** The A matrix stays at B3LYP-D3BJ/def2-SVP (Stage 4e: SIGN ROBUST across five levels,
  `cs_stage4e/STAGE4E_REPORT.txt`). Design magnitudes carry a stated method uncertainty (about 12% above MP2/6-31G(d)
  at frame 41786) beside the basis uncertainty of Stage 4c.
- **D1, D2, D5.** Unchanged.

## Update: C4 pre-registered (10 October 2026)

- **D5.** Reference 2 waits for C4 (C5 is done). C4 fixes the definition of the enzyme's barrier: from the lowest image
  at or before the climbing image (`05_qmmm/23_c4_reactant/C4_CRITERIA.txt`), with the in vacuo barrier taken at the
  same reactant geometry, so stab_TS stays the barrier difference at one geometry. The same definition applies to the
  bare substrate's and the designs' relaxed barriers, so reference 2 stays like for like. Fixed before any Phase 2.2
  design's relaxed barrier exists (reporting commitment 5).

## Update: Stage 5 pre-registered (19 October 2026)

- **D2.** How close a site may sit now depends on the sphere's charge (`cs_stage5/STAGE5_CRITERIA.txt`, floors in
  `cs_stage5/floors.tsv`): q <= 0 at the Lennard-Jones contact (H8: Stage 3's 2.331 A); 0 < q < 0.25 at the
  Lennard-Jones contact (H8: the +0.25 level's); q >= +0.25 at the closest approach of Stage 2's resting spheres of
  that level (every minimum, migrated ones included), where nearer. The grid has two layers (anion/neutral and
  cation) and each site admits only the charges whose floors it clears. A site is still an abstract quasi-atom, not a
  named group.
- **D3.** Unchanged in method: s16's rigid-core fit, now applied to the SP package's R_IRC with the same transform on
  TS and P (`cs5_align.py`); the reference is the lowest-numbered complete frame's R_IRC (frame 20000's, as before,
  when that frame is complete).
- **D5.** The barrier definition recorded in "Update: C4 pre-registered" above is superseded for every barrier
  compared with the enzyme's by `05_qmmm/24_sp_barriers/SP_AMENDMENT2.txt` A2.5 (TS, IRC, minimised ends, B = E(TS) -
  E(R_IRC), B_eff beside it; quasi-atoms held fixed), as `05_qmmm/23_c4_reactant/C4_CLOSURE.txt` records.
- **D1.** Unchanged.
## Update: the optimiser stage decided (20 October 2026)

Jessica decided the ten open questions of the optimiser stage on 20 October 2026. The reasoning, the library
citations by page, and the direction of each choice are in `phase2.2/OPTIMISER_DECISIONS_20261020.md`, committed
with this update. Every value below is fixed in the optimiser-stage pre-registration, written before any design is
read; nothing here is chosen by the barriers its designs reach.

**The inputs the optimiser receives** are fixed by Stage 5: the sites of the two-layer grid with the charges each
admits, a = V_TS - V_R per site and frame, L per site and frame, and the 3.25 A minimum spacing. Production uses the
SP package's complete frames; the development set (`cs_stage5/exploratory/dev_sites_a2.tsv`, `dev_L.tsv`,
`dev_A/A_dev.tsv`) is for code testing only and nothing it produces is a result.

- **O1. Polarisation (b) is not in the optimiser's score.** The score is linear: mean over frames of
  sum_i (a_if q_i + L_if z_i), plus the frame penalty of O5. The pool is re-scored with full def2-SVP single points,
  which contain b and every cross term exactly at the frozen geometry. Frozen magnitudes run 10-31 % small until
  re-scored (Stage 4c) and are never quoted as results. Rank correlation was 1.000 on eight widely separated
  arrangements, so near-ties may still reorder; that is what the re-scoring is for.
- **O2. The reactant-gradient (preorganisation) term moves to the re-scoring step. CHANGE, signed off.**
  `PHASE22_PLAN_UPDATE_20261009.md` section 4 item 5 and section 5 require the term in the design objective. Inside
  the MILP it would need each site's unit-charge force on every substrate atom with the electronic response, about
  166 000 SCF-plus-gradient calculations; the nuclear-only version ignores screening, which is large here. It
  therefore enters the re-scored objective instead, as kappa x max(0, G_add,R - G0)^2 summed over frames, where
  G_add,R is the RMS gradient the design adds over the bare substrate at the same geometry. G0 and kappa come from
  Stage 6, which also relaxes a few development-set designs at larger n (for example n = 5, 10, 20), fixed in Stage
  6's own pre-registration. If Stage 6 fixes no threshold, G_add,R is reported for every design without a penalty and
  that is stated as a limitation. The TS gradient is recorded beside it. Direction: the MILP's pool may hold
  stronger-pulling designs than the committed plan would have allowed (towards a lower frozen barrier at that step);
  the re-scoring term then acts against them.
- **O3. The budget is a sum-of-squares budget, sum_i q_i^2 <= B. CHANGE in timing, signed off.** A linear score puts
  every charge at a bound, so without a budget "more charges, lower barrier" is built in. Phase 2b recorded both
  outcomes: a linear objective drove charges to +-1 and the designs fragmented; a convex quadratic penalty gave
  fractional charges (0.06-0.29 e) that did not. HiGHS takes no quadratic rule, so q^2 is replaced by 21 tangent
  lines at q = -1.0, -0.9, ..., +1.0; because they lie below the curve, a design's true sum_i q_i^2 may exceed B by
  at most 0.0025 e^2 per sphere (0.05 e^2 at n = 20), and the true value is reported with every design. **B is sized
  without reference to any barrier:** for each trial B, stress-test designs that spend the whole budget as close to
  the substrate as the grid allows are built, and B is the largest value at which they still pass the plan's two
  electronic screens (the HOMO-LUMO gap and the shift of the substrate's Hirshfeld charges), both measured against
  the bare substrate at the same geometry, basis and level. The number of designs per B, the B values, the frames and
  the pass rate are pre-registered; the estimate given to the supervisor is 20 designs at each of 5 values of B on 5
  frames at R and TS, about 1000 single points and 17 node-hours. **The change in timing:** the plan fixes those
  screens' thresholds in the validation pre-registration, which falls after the optimiser stage; they are brought
  forward into the optimiser-stage pre-registration, written before any design is read. Direction: a smaller B acts
  against a lower barrier, and taking the largest B the screens allow is the most permissive choice consistent with
  them.
- **O4. Total charge is not forced to zero.** It is reported with every design. A potential constant over the
  substrate cancels from a, because the substrate carries -2 at both R and TS, so GOCAT's reason for imposing
  neutrality (an artificial constant-shift freedom in its database) does not apply to this score. Forcing neutrality
  would place compensating anions around a dianion, the electronically risky direction (Stage 4c: net-negative
  arrangements raise the substrate's highest occupied orbital). Direction: compared with neutrality, a free total
  admits more cations near O3, towards a lower barrier; stated with the results.
- **O5. Frames are combined as the mean plus lambda x semi-deviation.** The semi-deviation is
  (1/F) sum_f max(0, dE_f - mean), the average amount by which frames come out worse than the mean; being better on
  some frames is never penalised. Lambda is not tuned: it is tied to the 95 % confidence interval as
  lambda = t(0.975, F-1) / (0.399 sqrt(F)), which makes the score about the least favourable end of the design's
  interval - 0.94 at F = 30, 1.03 at 25, 1.17 at 20 - and is computed from the package's final F. The normal
  assumption sets only the size of lambda. Every complete package frame is weighted equally. The mean is what the
  comparison with the enzyme uses (SP Amendment 2 A2.3) and the most stable statistic for ranking alternatives
  (Ryde 2017). Direction: neutral to conservative, since the penalty only adds.
- **O6. n is solved upward from 3 and stopped by a rule.** Solve n = 3, 4, 5, ... and stop at the first n whose best
  design does not beat the best at n - 1 by more than both (i) the half-width of the paired 95 % interval of the
  per-frame differences - descriptive, not a true test, because both designs were chosen on those same frames, which
  is stated - and (ii) a pre-registered fraction of the score for method and basis uncertainty (the records give
  about 12 % against MP2 from Stage 4e and up to 23 % or 3.2 kcal/mol per arrangement across bases from Stage 4c; the
  fraction, for example 15 %, is fixed in the pre-registration). Every n before the stopping point goes forward. n
  counts spheres whatever their charge; a sphere may carry q = 0 where its site admits it and then acts only through
  L, and the number of neutral spheres is reported. Solve times are measured on the development set, not assumed.
- **O7. Pool, re-scoring and short list.** Per n, the 10 best **distinct** designs, where a new design must place at
  least one sphere more than 1.5 A from every sphere of each earlier design (1.5 A is less than half the 3.25 A
  spacing, so the rule forbids exactly the shifted copies; it ignores charges, so the same sites with different
  charges count as the same design). **The best 20 of the pool are re-scored** on every frame at R and TS with full
  def2-SVP single points, run as energy-plus-gradient for O2: about 1200 calculations, about 20 node-hours at Stage
  4d's energy-only timing, plus a gradient overhead to be measured. Jessica chose 20 rather than the 100 the draft
  proposed, to be widened later if wanted; the pool is kept, so the further 80 can be re-scored without redoing
  anything, and whether 20 sufficed is judged by how much re-scoring reorders those 20 before the short list is
  fixed. **The short list is the top ~10 overall plus the best of each carried-forward n** (about 10 to 28 designs).
  The records' wider reading, the top ~10 per carried-forward n (up to 180 designs), is not taken: that coverage was
  part of what replaced the optimality certificate, so the short list is narrower than the records envisaged, and
  every carried-forward n still contributes its best design.
- **O8. "Optimal" keeps its 2 September meaning.** Each solve reports its gap as a property of that score and those
  rules. "Certified" is not carried into the new code or the write-up as a claim, and "optimal catalyst" is never
  used.
- **O9. No path constraints in the MILP.** Path validity is tested on the relaxed chain of SP Amendment 2 A2.5, where
  Dittner's later work also moved it. The electrostatic part of each design's frozen change in reaction energy,
  sum_i q_i (V_P - V_R), is reported from the product-side potentials Stage 5 keeps; Stage 5 produces no Lennard-Jones
  term at P, so this is not the full reaction-energy change.
- **O10. The null distribution is random designs under the same rules.** Two kinds per n, under the same n, admitted
  charges, spacing and budget: (i) random sites with random charges drawn uniformly inside the budget and moved to
  the nearest admitted value, redrawn only if that pushes sum_i q_i^2 above B, with the acceptance rate reported; and
  (ii) random sites with their best charges, which tests whether choosing the sites matters. 10 000 of each per n at
  first order, and 50 in total re-scored with full single points. Each design is reported with its percentile in both.
  The exact sampling rule shapes the distribution and is pre-registered.
- **Negative spheres** were settled by the two-layer grid (Stage 5 Amendment 2, above): the MILP gives each site one
  yes/no per admitted charge range, and at most one of a site's ranges may be chosen.

**Order of work from here.** The optimiser code is written and tested on the development set (nothing it produces
there is a result); Stage 6 runs as already planned and fixes G0 and kappa; the optimiser-stage pre-registration is
written, fixing lambda from the final F, the stopping fraction, the pool sizes, the sampling rules, the null sample
sizes, the screens' thresholds, the B-calibration procedure and the code's sha256; B is calibrated and recorded; then
production runs on the Stage 5 production inputs once the SP package is FINAL.

**Four corrections to our reading of the library** were found while this draft was written and are recorded in
`phase2.2/LIBRARY_ERRATUM1_20261020.md`. None changes a result or any decision above.
