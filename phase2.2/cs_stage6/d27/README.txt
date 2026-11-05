d27: the 24 runs kept as physical files, then read (y65).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 214 files of the 24
   runs, together with hpc1's own HPC_MANIFEST.sha256, which is 213 members in one hpc_all_files_d27.tar.xz. hpc1
   wrote HPC_MANIFEST.sha256 over its own files before the download; the archive was checked
   against hpc1's copy by sha256 after the download, and every archive member was checked against
   the manifest again where the archive lies. Nothing of this batch exists only on hpc1.
2. In this repo: job.out and job.property.txt for each of the 24 runs, the PBS log,
   HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256, INVENTORY.tsv (every file with its size and
   category) and OUTPUTS.sha256.
3. NOT in this repo: job.gbw, job.densities, job.densitiesinfo, job.bibtex and the .tmp scratch,
   excluded by this repository's own .gitignore. This is the deviation from the rule of 18 October
   decided on 28 October 2026 for Diagnostic 14 and applied here for the same reasons: these are
   fixed-geometry single points whose reading uses job.out alone, the wavefunction restarts
   nothing, and the inputs that would regenerate it are committed beside it. Every one of these
   files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. y65 deletes nothing on hpc1.

The inputs were committed and pushed before the job was submitted (y64). Every one was checked
byte for byte against the file hpc1 actually ran, by the reading's own GATE 0, and the whole chain
was checked again by GATE 3, which reproduces d16's committed ddE of -6.134121 kcal/mol from a
freshly generated input whose pc.pc is byte-identical to d16's.

The archive is named hpc_all_files_d27.tar.xz.
