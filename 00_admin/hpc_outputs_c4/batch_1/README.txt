C4's re-optimisation runs kept as physical files, batch 1 (x81): what was archived and what was committed

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a physical file, not
only reported; for C4 this comes before its analysis (C4_CLOSURE.txt). Runs (jobs ended; RUNS.txt, with how each
job's output ends):
  S0_23268 S0_42436 S0_44388 S0_49592 S0_54795 S2_20000 S2_21634 S2_23268 S2_24883 S2_26495 S2_33320 S2_34991 
  S2_36665 S2_38344 S2_40485 S2_41786 S2_42436 S2_43087 S2_43738 S2_44388 S2_45688 S2_46990 S2_47641 S2_48292 
  S2_49592 S2_50892 S2_52192 S2_53493 S2_54144 S2_54795 S2_55446 S2_56098 S2_57397 S2_58698 S2_59999
Job outputs at staging time: 35 with C4_REOPT_CONVERGED, 0 with C4_REOPT_INCOMPLETE, 0 with a PBS
message (e.g. the walltime). Whether a run is finished in C4's sense (M1) is for the analysis, not this batch.

1. PC archives (PC_ARCHIVES.tsv; one per run, in the archive folder on Jessica's PC): all 735 regular files of
   the batch (1.37 GB uncompressed), every member's sha256 checked against inventory.tsv after the download and
   again where it lies; PCMANIFEST_RUN.sha256 lists each member. Nothing of the batch exists only on hpc1.
   35 of these PC archives were already in place from an earlier run of this commit that stopped before its git
   commit (for batch 1: x80's run, stopped when the PC's disk filled); each was tested whole (xz -t), checked member
   by member against this batch's inventory again, and reused.
2. In this repo: 595 text files in 35 tar.xz archives with manifests (hpc_text_outputs_1.tar.xz in each run
   folder: ORCA input and output, job script and output, energy CSV, start and final geometries, gradients and other
   text); 70 file(s) compressed one by one as .xz (70 final wavefunction/densities files, the rest text over
   50 MB; individual.tsv); 0 file(s) as the jobs compressed them (as_is.tsv).
3. On the PC only (pc_keep.tsv; they stay on hpc1): 70 trajectory and binary file(s) - a run killed by the walltime
   keeps its trajectory for its M1 continuation - and 0 scratch file(s).
4. Links (links.tsv, 35): the force field, with the target's sha256 in inventory.tsv.
x81 deletes nothing on hpc1. Checks (scripts/verify_c4.py, on the PC, before this commit): every PC archive read
member by member; every git archive extracted and matched to its manifest; every .xz decompressed and matched to
its original's sha256; nothing committed overwrites a file.
