# Write-up index — map of committed results, methods, and decisions

Purpose: a single authoritative map for drafting the thesis Methods & Results, so nothing
is missed. Every number in the write-up must trace to a committed file listed here. Where a
discrepancy is noted, RECONCILE before writing — do not silently pick one value.

Two repos (both public):
- Results (this repo): JessReid36/chorismate-thesis-results, branch `main`
- Code: JessReid36/chorismate-thesis-code, branches `main`, `rebuild-cleanroom`, `tier1-realism`
  - `rebuild-cleanroom` (latest acf133b) = the current clean-room barrier/geometry work
    (07_rebuild/, Route B, continuum, surrogate). USE THIS for the barrier/charge work.
  - `main` (ad09dfe) = GOCAT primary-source comparison / competitive positioning.
  - `tier1-realism` (e860bd7) = convex-cutplane / fractional-charge exploration.

## Canonical barrier numbers (with conditions + status)
Theory level throughout the bare/charge work: ORCA 6.0.1, B3LYP-D3BJ/def2-SVP/def2-J/RIJCOSX,
**CPCM eps=4**, charge -2, singlet. (State the continuum setting for EVERY barrier.)

| Barrier (kcal/mol) | System / conditions | Continuum | Status | Source file |
|---|---|---|---|---|
| 17.47 | bare dianion, single-point on committed geoms | CPCM eps=4 | canonical bare | L0 (code repo 07_rebuild/L0_groundtruth) |
| 15.3 (see note) | enzyme QM/MM, reduced-region OptTS, one snapshot | QM/MM elec-embed | single-snapshot | notes/model_fidelity_validation_framework.md; 05_qmmm/18c_reduced_region/ts_frequencies_summary.txt |
| 29.77 | capacitor (50 charges), UNRESTRAINED relaxed | CPCM eps=4 | negative result | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/cap_f0p020_n5_barrier_energy_table.txt |
| 46.37 | OEEF-020 (6 charges), UNRESTRAINED relaxed | CPCM eps=4 | negative result | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/oeefs_..._barrier_energy_table.txt |
| 14.39 | walls-only control (no field), converged | CPCM eps=4 | Route B control | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md; route_b/cradleArg90_restrained_control_barrier.txt |
| 6.40 | walls + Arg90 charge, CI-NEB HEI | CPCM eps=4 | Route B main [exploratory] | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md |
| 7.23 | walls + Arg90 charge, tighter clamp2 (k=100) | CPCM eps=4 | robustness check [exploratory] | route_b/ROUTE_B_GEOMETRY_CHARGE_RESULT.md |

**RECONCILE before writing:** the enzyme barrier is quoted as 15.3 in model_fidelity but the
reduced-region ts_frequencies_summary.txt shows +15.08 AND a second small imaginary mode
(-18.65 cm^-1) alongside the main -313 cm^-1. Decide the authoritative value and address the
second imaginary mode (is the reduced-region TS a clean first-order saddle?).

## Result / decision notes (by theme)

### Enzyme QM/MM (Phase 1 system)
- notes/model_fidelity_validation_framework.md — methods philosophy, theory level, the 15.3
  barrier, three-method cross-check (scan 16.6 / NEB-CI 15.2 / reduced-region 15.3), imaginary
  mode -313, and the OUTSTANDING items (enzyme-minus-solution differential; ensemble; higher-level
  single points). This is the core methods/validation narrative.
- 05_qmmm/18c_reduced_region/ts_frequencies_summary.txt — the reduced-region TS vib check.
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
