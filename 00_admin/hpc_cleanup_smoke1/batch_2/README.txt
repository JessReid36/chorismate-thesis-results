SP runs' outputs kept as physical files, batch 2 (x77): what was archived, what was committed, what is to be deleted

Rule (Jessica, 18 October 2026): every output file of a finished step is downloaded and kept as a physical file,
not only reported. Steps (jobs ended; STEPS.txt): f42436_r6_a1/_run f42436_r6_a1/irc f42436_r6_a1/p_irc f42436_r6_a1/p_irc_freq f42436_r6_a1/r0 f42436_r6_a1/r0_freq f42436_r6_a1/r_irc f42436_r6_a1/r_irc_freq f42436_r6_a1/ts f42436_r6_a1/ts_freq f42436_r8/r0 f42436_r8/r0_freq f42436_r8_a1/_run f42436_r8_a1/irc f42436_r8_a1/p_irc f42436_r8_a1/p_irc_freq f42436_r8_a1/r0 f42436_r8_a1/r0_freq f42436_r8_a1/r_irc f42436_r8_a1/r_irc_freq f42436_r8_a1/ts f42436_r8_a1/ts_freq
Also 13 file(s) that x76's batches had left on hpc1 uncommitted (EXTRAS.txt: frequency Hessian, basis-set files).
Smoke test 1's steps are exploratory (SP Amendment 1); smoke test 2's are SP Amendment 1's. Region rule at staging
time (SPA_REPORT.txt, spa_report.py smoke): the 30 frames use 8 A.

1. PC archives (PC_ARCHIVES.tsv; one per run, in the archive folder on Jessica's PC): all 1906 regular files of
   the batch (2.11 GB uncompressed), every member's sha256 checked against inventory.tsv after the download and
   again where it lies; PCMANIFEST_RUN.sha256 lists each member. Nothing of the batch exists only on hpc1.
2. In this repo: 1655 text files in 23 tar.xz archives with manifests (hpc_text_outputs_2_STEP.tar.xz in the run
   folders; ORCA inputs and outputs, geometries, QM-region trajectories, Hessians, gradients, records, job outputs);
   40 file(s) compressed one by one as .xz (40 wavefunction/densities files of the steps' final states, the rest
   text over 50 MB; individual.tsv); 1 file(s) as the jobs compressed them (as_is.tsv). On hpc1, 0 text
   file(s) over 50 MB in step folders will be replaced by that same .xz; every other file committed here stays.
3. On the PC only (pc_keep.tsv, 111 file(s); stay on hpc1): active-region trajectories (also as the jobs
   compressed them), full-system trajectories over 20 MB, MD-format files, binary files of no other kind, jobs'
   .xz over 95 MB. To be deleted from hpc1 after this commit (delete.tsv, 99 file(s), 0.15 GB, all in the
   PC archives): scratch and working files only - ORCA scratch, the optimiser's working Hessians, and the
   wavefunctions and densities of intermediate states.
4. Links (links.tsv, 112): the force field, with the target's sha256 in inventory.tsv.
Already gone before this batch, as the job scripts did after each passing step (SP_PLAN, SP Amendment 1;
FILES_BEFORE_CLEANUP.txt in each step or cycle folder lists them): full-system trajectories, scratch, the IRC
step's copy of the TS frequency Hessian (the original is in ts_freq), and in cycle folders the DCD trajectory,
full-system PDB, densities and start.xyz. x76's batch 1, before the rule, deleted without a PC copy its steps'
scratch, wavefunctions and densities, approximate and TS-search Hessians and two full-system trajectories
(its delete.tsv lists each); those cannot be recovered, only recomputed from the committed geometries and inputs.
Checks (scripts/verify_stage.py, on the PC, before this commit): every file of the steps earlier batches took is
in one of them with the same size and modification time; every PC archive read member by member; every git archive extracted and matched to its manifest;
every .xz decompressed and matched to its original's sha256; every file to be deleted is scratch or a working
file in a step folder.
Deletion (x77_sp.sh delete): only after every PC archive of the batch verifies again against PC_ARCHIVES.tsv and
its manifest, and every file to be deleted is in those manifests; only listed files whose sha256 still matches;
the log and post-deletion check are added here.
