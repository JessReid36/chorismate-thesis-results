SP smoke test 1 clean-up, batch 1: what was committed, what is to be deleted, and why

Steps (jobs ended; STEPS.txt): f42436_r6/_run f42436_r6/irc f42436_r6/p_irc f42436_r6/p_irc_freq f42436_r6/r0 f42436_r6/r0_freq f42436_r6/r_irc f42436_r6/r_irc_freq f42436_r6/ts f42436_r6/ts_freq f42436_r8/_run f42436_r8/irc f42436_r8/p_irc f42436_r8/p_irc_freq f42436_r8/r_irc f42436_r8/r_irc_freq f42436_r8/ts f42436_r8/ts_freq
Done as on 7 October (00_admin/hpc_cleanup_20261007): staged on hpc1 by scripts/smoke1_cleanup.py (non-destructive),
fetched and checked on the PC by scripts/verify_stage.py (every archive extracted and each member compared with
its manifest; every compressed output decompressed and compared with its original's sha256), committed here
before anything is deleted. inventory.tsv lists every file of both run folders at staging time.

Committed: 2 archive(s) of text files (94 files; hpc_text_outputs_1.tar.xz with .MANIFEST.sha256, in the run
folders), kept on hpc1; 2 text output(s) over 50 MB as .xz (0.50 GB uncompressed; individual.tsv), which replace
the originals on hpc1 at deletion; 1 file(s) already compressed by the jobs, as they are (as_is.tsv);
SP_REPORT.txt, sp_report.py's report of smoke test 1 at staging time.
To be deleted on hpc1 (delete.tsv, DELETE_CHECKSUMS.sha256): 268 file(s), 8.51 GB. As on 7 October: scratch
(*.tmp), approximate Hessians (*.appr.hess), Cartesian Hessians (*.carthess), wavefunctions and densities (*.gbw,
*.gbwN, *.densities), *.dcd, *.mdrestart. Departures from 7 October, all in runs that ended without converging:
(1) 2 full-system trajectory(ies) over 20 MB (7 October kept optimisation trajectories) - deleted only where the
step's activeRegion trajectory, committed, holds at least as many complete frames and its start.xyz is committed;
ORCA moves no atom outside ActiveAtoms, so every frame is start.xyz with that frame's active atoms; (2) 4 TS
search Hessian(s) (ts/*.hess; 7 October kept every .hess except *.appr.hess; the job scripts delete them after a
passing TS step, which these never reached); (3) *.tmp.N scratch files, which 7 October's pattern did not cover.
Kept on hpc1, not committed (keep.tsv, sha256 recorded): 29 file(s) - links, frequency Hessians (as on 7 October),
and 12 other file(s) left in place for the reason given in keep.tsv (e.g. basis-set scratch, binary files of no
known kind).
Deletion (x76_smoke1.sh delete): only files on the committed list whose sha256 still matches, and only if no
listed file belongs to a job still in the queue; the log and the post-deletion check are added to this folder.
