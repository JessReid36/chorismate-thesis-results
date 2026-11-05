d28: the 22 runs kept as physical files, then read (y67).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv): all 190 files of the 22 jobs together with hpc1's own
   HPC_MANIFEST.sha256, 189 members in one hpc_all_files_d28.tar.xz. hpc1 wrote the manifest over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after it, and every
   member checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt per job, the PBS log, HPC_MANIFEST.sha256,
   INPUT_CHECKSUMS.sha256, INVENTORY.tsv and OUTPUTS.sha256.
3. NOT in this repo: job.gbw and the other binaries, excluded by .gitignore, per the deviation of
   28 October for fixed-geometry single points. All are in the PC archive with their sha256.
4. y67 deletes nothing on hpc1.

THE RULE THIS DIAGNOSTIC WAS BUILT AROUND. An orbital energy from a run where ORCA engaged its TRAH
converger is NOT quoted: the printed energies are level-shifted and any negative-gap warning
precedes convergence rather than describing the converged state. DIAGNOSTIC 27 lacked this rule and
a claim had to be retracted. The reader records which runs were affected and what it withheld, and
the independent verifier checks that no withheld value reached the document.
