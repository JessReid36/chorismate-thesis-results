# Write-up index — map of committed results, methods, and decisions

Last corrected: 2026-11-03 (enzyme barrier reconciliation; see CORRECTION_RECORD_20261103.md).

Purpose: a single authoritative map for drafting the thesis Methods & Results, so nothing
is missed. Every number in the write-up must trace to a committed file listed here. Where a
discrepancy is noted, RECONCILE before writing — do not silently pick one value.

Two repos (both public):
- Results (this repo): JessReid36/chorismate-thesis-results, branch `main`
- Code: JessReid36/chorismate-thesis-code. Corrected 2026-11-03: these are not three
  independent lines of work. `main` (`ad09dfe`) is a strict ANCESTOR of both others — the common
  trunk, needing no separate citation. `tier1-realism` and `rebuild-cleanroom` are SIBLINGS forked
  at `e860bd7`; rebuild-cleanroom was never merged back.
  - **`tier1-realism` (`f0cbdb0`) = AUTHORITATIVE for the write-up.** A strict superset of `main`.
    Carries `phase2.2` (106 files), the Phase-1 ensemble/NAC thread (46 files), the convex-cutplane
    solver, `refstate_diagnostic.pbs`, and the corrected `step12b_extract.sh` (see below).
  - **`rebuild-cleanroom` (`acf133b`) = FROZEN citable source, by SHA, for `07_rebuild` only:**
    the L0 reproduction of 17.47 and the committed anchor geometries (`07_rebuild/inputs/`),
    the restrained-NEB machinery behind 14.39 / 6.40 / 7.23, the L1/L2/L3 clean-room pipeline and
    design set, `DECISION_next_optimizer.md`, and the `results_*.md` negative results.
  - Across all three branches only TWO files differ at a shared path: `.gitignore` and
    `phase1_system_dev/step12b_extract.sh`. Everything else is additive/disjoint. `notes/` and
    `phase2_charge_design/` are byte-identical on all three.
  - **DO NOT MERGE** `acf133b` into `f0cbdb0`: the two `phase2b_charge_design/07_rebuild/L3_solver/`
    sets are disjoint (9 HEAD-side, 73 cleanroom-side, zero shared filenames) and git would union
    them without conflict, silently destroying which branch produced which design.

## Canonical barrier numbers (with conditions + status)
Theory level throughout the bare/charge work: ORCA 6.0.1, B3LYP-D3BJ/def2-SVP/def2-J/RIJCOSX,
**CPCM eps=4**, charge -2, singlet. (State the continuum setting for EVERY barrier.)

| Barrier (kcal/mol) | System / conditions | Continuum | Status | Source file |
|---|---|---|---|---|
| 17.47 | bare dianion, single-point on committed geoms | CPCM eps=4 | canonical bare | L0 (code repo 07_rebuild/L0_groundtruth) |
| 16.00 | enzyme QM/MM, reduced-region OptTS, frame 820, one snapshot, 102-atom consistent region | QM/MM elec-embed | **retained-final**, freq-verified | phase1_system_dev/BARRIER_FINAL.md (code repo); 05_qmmm/18e_reactant_reduced/reactant_reduced.out + 05_qmmm/18c_reduced_region/ts_reduced.out |
| 29.77 | capacitor (50 charges), UNRESTRAINED relaxed | CPCM eps=4 | negative result | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/cap_f0p020_n5_barrier_energy_table.txt |
| 46.37 | OEEF-020 (6 charges), UNRESTRAINED relaxed | CPCM eps=4 | negative result | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/oeefs_..._barrier_energy_table.txt |
| 14.39 | walls-only control (no field), converged | CPCM eps=4 | Route B control | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/cradleArg90_restrained_control_barrier.txt |
| 6.40 | walls + Arg90 charge, CI-NEB HEI | CPCM eps=4 | Route B main [exploratory] | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md |
| 7.23 | walls + Arg90 charge, tighter clamp2 (k=100) | CPCM eps=4 | robustness check [exploratory] | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md |

**RESOLVED 2026-11-03** (this block previously read "RECONCILE before writing"; see
CORRECTION_RECORD_20261103.md). The enzyme barrier is **+16.00 kcal/mol** [retained-final],
re-derived from raw ORCA outputs:

- TS       -1076.104998186095 Eh  (`05_qmmm/18c_reduced_region/ts_reduced.out`, last FINAL SINGLE POINT ENERGY (QM/MM); equals frame 22/22 of ts_reduced.QMRegion_trj.xyz)
- reactant -1076.130494943784 Eh  (`05_qmmm/18e_reactant_reduced/reactant_reduced.out`)
- barrier = **+15.9995 kcal/mol**; reaction energy = **-13.1520 kcal/mol** (product -1076.151454007164 Eh, 18f)

All three jobs sit in the SAME 102-atom reduced active region on the common frozen bulk.

The superseded **+15.08** subtracted this 102-atom TS from a ~1959-atom-region reactant
(-1076.129034 Eh); that reactant mismatch alone accounts for 0.9168 kcal/mol. **15.3 was never
committed** to either repo.

The second imaginary mode is **not real**: -313.30 and -18.65 cm^-1 are the STARTING Hessian that
ORCA prints before optimisation cycle 1. The converged NumFreq, after `*** OPTIMIZATION RUN DONE ***`
(`ts_reduced.out` line 96542), lists **one** imaginary mode, **-313.07 cm^-1**. The reduced-region TS
is a clean first-order saddle; IRC connects R and P (`05_qmmm/18d_irc`).

Cross-check: reduced-region OptTS 16.00 / NEB-CI 15.94 / relaxed scan 16.37 (spread ~0.4).
See PHASE1_AUDIT_CHECKLIST A7 (resolved 12 Oct 2026) and TIER2_KNOWN_ISSUES B3.
Re-run `checks/verify_barrier_18c_18e_18f.sh` to reproduce every number above.

## Result / decision notes (by theme)

### Enzyme QM/MM (Phase 1 system)
- notes/model_fidelity_validation_framework.md — methods philosophy, theory level, the 16.00
  barrier, cross-check triplet (scan 16.37 / NEB-CI 15.94 / reduced-region 16.00), imaginary
  mode -313, and the OUTSTANDING items (enzyme-minus-solution differential; ensemble;
  higher-level single points). This is the core methods/validation narrative. **Quote the CODE
  repo copy** (`chorismate-thesis-code@f0cbdb0:notes/...`), which was corrected on 2026-07-22
  in commit cb5cb5e [retained-final] and is byte-identical on all three code branches
  (blob 52dc260f). The duplicate under this repo's `notes/` had never been updated and still
  carried the pre-correction 15.3 / 16.6 / 15.2 — it is the source of the stale 15.3 formerly
  cited in this index. Synced 2026-11-03; see CORRECTION_RECORD_20261103.md.
- 05_qmmm/18c_reduced_region/ts_frequencies_summary.txt — the reduced-region TS vib check.
  Corrected 2026-11-03: now reports the CONVERGED NumFreq (one mode, -313.07) and the
  consistent-region barrier +16.00, replacing the starting-Hessian table and the +15.08 footer.
- 04_amber_md/11_analysis/step11_trajectory_analysis.md — MD trajectory analysis.

### Route B (charge + geometric confinement) — the positive result
- route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md — THE central result note: 6.40/7.23 under held
  geometry, decomposition (walls -3, charge -8), negative result (29.77/46.37), the free-energy
  framing (PE barrier as ranking metric, PMF deferred), how-to-read-NEB-outputs. [exploratory]

### Substrate geometry / continuum (today's work)
- substrate_geometry/CONTINUUM_VS_VACUUM.md — CPCM stabilises the fold (3.54) vs vacuum opens
  (4.39); Arg90 charges open the substrate in BOTH environments -> continuum exonerated,
  charge-collapse intrinsic, two-layer thesis reinforced.
- substrate_geometry/CPCM_REFOLD_TEST.md — CPCM preserves but does not DRIVE the fold (from-open
  stays open); reactive geometry is inheritance+preservation, not CPCM-driven.
- substrate_geometry/REACTANT_CONFORMER_ID.md — reactant rigorously classified as reactive CHAIR
  (methylene over ring at 3.12 A), not non-reactive DIAX.

### Charge-search design (Phase 2 core)
- phase2_charge_design/REACTANT_CONFORMER_DECISION.md — the lowest-vs-reactive conformer choice,
  the two-step approach (constrained screen + unconstrained validation), and the concrete next
  experiment (re-run surrogate on constrained geometry).
- phase2_charge_design/03_dvpot_realgeom/stage1_realgeom_summary.txt + 05_select/, 06_polarize/
  — the DTSS/dvpot surrogate pipeline outputs (real-geometry).
- phase2_charge_design/08_validate/ — TS-frame residue agreement, offset map, overlay result.

### Phase 2b (earlier charge-design attempt) + point-charge issues
- phase2b_charge_design/07_stage0/STAGE0_results_table.md + stage1/STAGE1_results_table.md
- phase2b_charge_design/relaxation_attempts/ash_guarded/ — NEB_FINDING(_395444).md,
  K2_SCAN_FINDING.md, SWITCH_EVIDENCE.md, ENDPOINTS_PROVENANCE.md, ENDPOINT_VALIDITY_ASSESSMENT.md
  (the discrete-ladder negative result + point-charge collapse investigation).
- step_7_relaxed_validation_and_point_charge_collapse.md — the .pc / CPCM cavity / point-charge
  singularity investigation (why bare point charges collapse; representation options).
- step_7b_charge_representation_options.md — charge-representation alternatives evaluated.

### Shell ladder
- 05d_shell_ladder/SHELL_LADDER_NEB_RESULT.md + SHELL_LADDER_NEB_CORRECTION.md

### Admin / provenance / known issues
- README.md — repo layout + large-file checksum policy.
- TIER2_KNOWN_ISSUES.md — known issues list.
- 00_admin/ — provenance, checksums, submit summaries.

## PENDING (not yet committed — leave placeholders in the write-up)
- Held-geometry barriers for OEEF and capacitor on the COMMON Arg90 substrate (jobs oeef_held /
  cap_held, running as of 2026-09-01). These test whether the electrostatic surrogate ranks
  correctly ON HELD GEOMETRY (surrogate predicts OEEF < capacitor < Arg90(6.40)). Result pending.
- Constrained-geometry surrogate correlation (the re-test that the free-geometry r=-0.839
  motivated). Pending the held barriers above.
- The MILP charge search itself (Phase 2 core) — not yet built.

## Discipline reminders for the write-up
- Every barrier: quote from the committed file, cite the file, STATE THE CONTINUUM SETTING.
- Numbers come from committed .txt/.md, never from prose memory (three retracted errors earlier
  in the project came from trusting summaries over committed outputs).
- Use the correct code-repo BRANCH per component (rebuild-cleanroom for barrier/charge work).
- Flag every [exploratory] result as such; do not present exploratory numbers as final.

---

## Open provenance items raised 2026-11-03 (not yet resolved)

**P1 — frame extraction differs between branches, and the old version fails silently.**
`phase1_system_dev/step12b_extract.sh` is the QM/MM frame-extraction script; it selects which MD
snapshot every downstream barrier is computed on. On `tier1-realism` it reads TWO trajectories
(`04_amber_md/10c_production/prod.nc` plus `10d_production_extend/prod_ext.nc`) and routes a frame
index between them, with an explicit out-of-range guard. On `main`/`rebuild-cleanroom` it reads only
`prod.nc` and indexes into it via `np.memmap` with **no bounds check** — so a frame index at or
beyond that file's length returns wrong coordinates rather than an error.
**Consequence:** any barrier whose snapshot came from the extension segment is only correctly
attributable on `tier1-realism`. ACTION: cross-check `selection_manifest.tsv` and the Phase-1 frame
indices (frame 820 included) against the first trajectory's frame count, and record for each
reported barrier which trajectory its frame came from. Until that is done, no frame index should be
cited without stating which branch's extractor produced it.

**P2 — 15.78 is RETRACTED; add to the do-not-quote list.**
Commit `0db07f0` on rebuild-cleanroom claimed "capacitor (50 chg) gives 15.78 vs 17.47 bare (-1.69),
uniform point-charge field CATALYSES". Commit `eacab5e` retracts it: a DERAILED-SCAN artefact.
Fixed-geometry OEEF (-10.6) does not survive relaxation; scans are unreliable here, NEB only. The
29.77 and 46.37 negative results in the table above are the post-correction values and are correct.

**P3 — 17.47 attribution needs two qualifications.**
(i) `07_rebuild/L0_groundtruth` is where 17.47 is REPRODUCED, not where it originates. `L0_groundtruth.py`
hardcodes `REF_BARRIER = 17.47` and passes on `abs(barrier - REF_BARRIER) < 1.0`. The originating value
predates `07_rebuild` and sits in `phase2b_charge_design/05_optimise/` on `ad09dfe`. Cite L0 as
"independently reproduced within a 1.0 kcal/mol gate", not as the source.
(ii) The row label "bare dianion" is a risk: the value is CPCM eps=4, not a no-environment state.
The repo's own `phase2b_charge_design/02_singlepoints/refstate_diagnostic.pbs` (tier1-realism only)
says to "report the CPCM barrier as the reference and state the continuum contribution explicitly,
so that +17.47 is not mistaken for a 'no environment' state." Relabel accordingly.

**P4 — three Route B numbers are unreproducible from any single branch.**
`07_rebuild/L4_barrier/barrier_restrained.py` produced 14.39 / 6.40 / 7.23 (commit `e74b031`,
self-tagged `[exploratory]`) and exists only on `rebuild-cleanroom`. Its input files
`design_cradleArg90_charges.txt` / `_coords.xyz` exist only on `tier1-realism` (commit `2454f45`).
Neither branch alone can regenerate those three numbers. ACTION: cherry-pick
`barrier_restrained.py` onto `tier1-realism` under a RENAMED path (e.g. `07_rebuild_cleanroom/`),
never onto the colliding `07_rebuild/` path. Also apply the `[exploratory]` tag to the 14.39
walls-only control row above, which currently lacks it despite sharing that commit.

**P5 — does phase2.2 retire or merely recontextualise 17.47?**
`phase2.2/README.md` objects that "point charges plus CPCM eps = 4 matches neither published GOCAT
setting, and the continuum supplies the stabilisation the charges are being optimised to provide"
— a direct methodological objection to the setting every barrier row above is labelled with. Whether
the 17.47 anchor is retired, recontextualised, or kept as a reference point is a DECISION, not
recoverable from the commits. Needs a ruling before this index records a status for it.
