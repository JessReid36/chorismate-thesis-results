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

## D-WP4. Consequences for WP4 (the s13 rerun), fixed now

- **Frame**: 41786 (no reactant-end dip, NEB-CI; untouched by C4 and C5), so WP4 never needs redoing.
- **Contact tested**: the carboxylate contact, because a free single site always goes there (WP5).
  References: Arg-carboxylate N to O 2.74-2.77 A (QM/MM) and 2.87 +- 0.12 A (MD); CZ to O 3.23-3.27 A
  (QM/MM) and 3.52 +- 0.17 A (MD, nearest O).
- **Arms**: bare +1 (control); nitrogen-sized LJ site (model property: rigid-model expectation
  2.584 A to O2 at frame 41786, a departure over 0.3 A to be explained); methylguanidinium (D4),
  accepted if its N to O and CZ to O distances fall within the MD mean +- 2 sd (N to O 2.62-3.11 A,
  CZ to O 3.18-3.86 A).
- **Degrees of freedom**: every arm gets the same freedom (the test2 lesson). The control is run the
  same way as the LJ arms, as a QM/MM site with zero LJ parameters (ORCA accepts zero LJ, as for the
  hydroxyl hydrogen), not as a point-charge file; the substrate may move as a whole in every arm, and
  centroid drift is reported separately.
