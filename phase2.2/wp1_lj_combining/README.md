# phase2.2/wp1_lj_combining - how ORCA 6.0.1 combines Lennard-Jones parameters (WP1)

Job: code phase2.2/wp1_lj.pbs, PBS 417143 on comp050, 6 Oct 2026. Analysis: code
phase2.2/wp1_lj_analyse.py, run on hpc1. Two atoms, zero charges, no bonds, MM only, scanned
2.00-6.00 A in 0.05 A steps, with ORCA's default LJ force switching and with it off. LJ parameters
copied exactly from 05_qmmm/13_bridge/complex_solvated.ORCAFF.prms.

## Result (WP1_REPORT.txt)

- The length column of ORCAFF.prms is the atom type's full R_min (2 R* in Amber terms).
- Unlike pairs: R_ij = (R_i + R_j)/2 and eps_ij = sqrt(eps_i eps_j), the Lorentz-Berthelot form
  Amber uses. With one fitted energy scale this rule reproduces all 324 switched-off energies to
  within 4e-8 |E|; the three alternatives miss by 0.75 |E| or more.
- Pair minima this gives: Na - carboxylate O 3.0302 A; generic Amber N - carboxylate O 3.4852 A;
  Na - ether O 3.0527 A; O - O 3.3224 A.
- Default force switching (10-12 A) only adds a constant per pair below 10 A (1.8e-7 to 6.2e-7 Eh,
  constant to 1e-12 Eh), so forces and distances are unchanged.
- The fitted scale is 1.0000021787: ORCA's MM energies imply 627.508107 kcal/mol per Eh, against the
  CODATA-based 627.5094740631 used in this project's scripts. The source of ORCA's value is not
  documented. It changes MM energies by 2.2 parts per million and no distance or force.

## Criteria

WP1_CRITERIA.txt was written by the job before any single point ran. Criterion 1 asked for an
absolute 1e-8 Eh match. After the first sample point, and before the full analysis ran, it was
amended to a fitted-scale shape test, because a 2.2e-6 relative difference in ORCA's energy-unit
constant alone would exceed 1e-8 Eh at short range even for the right rule. The amendment and its
reason are in the analysis script's docstring; the report prints the original absolute test too.

## Files

WP1_CRITERIA.txt, WP1_REPORT.txt, wp1_energies.tsv (all 648 energies), pairs.txt, distances.txt,
wp1.pbs.out (job log), wp1_outputs.tar.xz (all 648 inputs and outputs and the two-atom force-field
files; sha256 30140ccc26fbe1c44917ea23537b5f811fa6fbb73385dbcef1f613efa5d96fad).
