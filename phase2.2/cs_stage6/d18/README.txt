d18: the 6 runs kept as physical files, then read (y35).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 51 files of the 6
   runs, together with hpc1's own HPC_MANIFEST.sha256, which is 52 members in one tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files before the download;
   every file was checked against it after the download, and every archive member was checked
   against it again where the archive lies. Nothing of this batch exists only on hpc1.
2. In this repo: the 13 text output files (job.out, job.property.txt and the PBS log),
   HPC_MANIFEST.sha256, INVENTORY.tsv (every file with its size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.gbw, job.densities, job.bibtex and job.densitiesinfo, excluded by this
   repository's own .gitignore. This is the deviation from the rule of 18 October decided on
   28 October 2026 for Diagnostic 14 and applied here for the same reasons: these are
   fixed-geometry single points whose reading uses job.out alone, the wavefunction restarts
   nothing, and the inputs that would regenerate it are committed beside it. Every one of these
   files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. y35 deletes nothing on hpc1.

The inputs were committed before the jobs were submitted. Every one was checked byte for byte
against the file hpc1 actually ran (GATE 0 above), and again by the reading's own control gate.

The archive is named hpc_all_files_d18.tar.xz. Four earlier PC_ARCHIVES.tsv files in this tree
record their archive as hpc_all_files_$NAME.tar.xz, unexpanded; that is a defect in those
records, not in this one.
