hpc1 clean-up of 7 October 2026 - what was committed, what was deleted, and why

Basis. Every file in the hpc1 home was listed (00_admin/hpc_inventory/hpc_files_20261007.tsv.gz, results
fbb3c69) and compared with the results repo (paths, .xz/.gz copies, the WP1 archive by member name and size,
and 05_qmmm/19_ensemble/CHECKSUMS_not_committed.sha256) and with the code repo (scripts matched by name and
size). Of 114.6 GB, 1.8 GB was committed, 0.6 GB archived (WP1), 40.2 GB checksum-recorded (19_ensemble),
68.6 GB uncommitted, 3.5 GB outside both repos.

Committed before any deletion (step 1):
  - every uncommitted text output (outputs, logs, inputs, structures, tables, scripts) of 50 MB or less,
    except full-system trajectories over 20 MB, as xz archives named in archives.tsv; each archive has a
    .MANIFEST.sha256 of its members (paths relative to system_development), verified on the PC by
    extracting every member;
  - text outputs over 50 MB individually as .xz (05_qmmm/18_nebts/nebts.out);
  - the sha256 of every file proposed for deletion (DELETE_CHECKSUMS.sha256).
Not in scope (left untouched): 04_amber_md (MD trajectories, kept), 05_qmmm/22_c5_nebci (C5 restarts,
two still running; committed when all eight finish), everything outside system_development.

Deleted (step 2, x39_delete.pbs), only files in delete.tsv whose sha256 still matched the record:
  - scratch: ORCA *.tmp files, approximate Hessians (*.appr.hess), NEB-TS Cartesian Hessians (*.carthess),
    optimisation trajectories (*.dcd), optimiser restart files (*.mdrestart);
  - wavefunctions and densities (*.gbw, *.densities) of finished runs, outside protected folders;
  - all-iteration full-system NEB trajectories (*MEP_ALL_trj.xyz); their QM-region versions are committed.
Never deleted (protected): 05_qmmm/22_c5_nebci, 05_qmmm/20_invacuo (in vacuo wavefunctions and densities used
by Phase 2.2), phase2.2, 04_amber_md, true Hessians (*.hess, e.g. 18b_ts_numfreq/ts_optfreq.hess), final
bands, IRC and optimisation trajectories, and 19_ensemble's structures, final bands and TS geometries (needed
by C4).

Step 2 (7 October 2026): x39_delete.pbs deleted all 3912 listed files (36.76 GB), none skipped or absent
(DELETED.log, x39_delete.pbs.out). Checked on hpc1 afterwards: no deleted file remains; 36142 files remain
outside 22_c5_nebci, exactly the 40054 of the inventory minus the 3912 listed, so nothing else was removed;
ts_optfreq.hess (1193873651 bytes), all 1054 files of 20_invacuo and all 44 final bands of 19_ensemble are
present; system_development is 70 GB (was 104 GB). The two job scripts as run are in scripts/ (the queue
directive removed and mail lines added before submission, after a first submission was refused).
