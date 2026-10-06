# 05_qmmm/19_ensemble - per-frame QM/MM pipeline, all 44 ensemble frames

Mirror of hpc1:/home/18660916/system_development/05_qmmm/19_ensemble, reduced to what git can hold.
Per frame: reactant optimisation -> 20-window restrained scan (scan/) -> product optimisation -> NEB.
19_ensemble_barriers/ holds the harvested summary (geometries, path summaries, in vacuo inputs).

Committed as text: every input (reactant_opt, product_opt, neb, neb.inp.nebts, neb.inp.neb_ci_superseded,
all 880 scan_NN.inp), job scripts and logs, *-restraints.csv / *-colvars.csv / *-minimize-ener.csv, scan
energy tables, NEB logs and interpolation files, QM-region geometries and paths, and the text of the
superseded NEB-CI runs (neb_ci_superseded/, the 14 pilot frames).
Committed compressed: neb.out, reactant_opt.out, product_opt.out (and neb_ci_superseded/neb.out) as .xz;
CHECKSUMS_xz_originals.sha256 holds the sums of the uncompressed originals.
Not committed: trajectories, Hessians, wavefunctions, full-system PDBs, scan outputs and the 44 per-frame
copies of complex_solvated.ORCAFF.prms. Their sha256 sums are in CHECKSUMS_not_committed.sha256; the files
stay on hpc1. The input PDB of each frame (frame_NNNNN_CHA2.pdb) is rebuilt by ambpdb from
12_frame_selection/frames/frame_NNNNN_CHA2.rst7 and 03_amber/tleap_build/complex_solvated.prmtop.

Restraints, read from the scan inputs on 5 Oct 2026: harmonic restraints on C4-O3 (0-based atoms
6215-6214) and C6-C1 (6219-6207); spring 400 kJ/mol/A^2 for the 14 pilot frames, 2500 for the 30
post-cut frames. Job logs missing on hpc1: product_opt.pbs.out (09025 17505 34991 55446 57397 58698
59999), neb.pbs.out (41786 46990). Frame 08170 has no converged climbing image.

Notes added 6 Oct 2026 (s18b_pipeline_check.py):
- frame_11630/scan/run_scan.sh postdates that frame's scan. It is the 7f3bc74 version
  (SPRING=2500); the scan ran on 8 Sep 2026 with the 8c2a372 version, and every scan_NN.inp
  of the frame uses Spring 400.0. The inputs are the record.
- The 22 neb.out files of the NEB-TS runs do not end in ORCA TERMINATED NORMALLY: the jobs
  were stopped in the TS-optimisation stage. Their barriers come from the NEB stage that
  precedes it, converged only to ORCA's looser NEB-TS thresholds (PHASE1_AUDIT_CHECKLIST.md
  item C5).
