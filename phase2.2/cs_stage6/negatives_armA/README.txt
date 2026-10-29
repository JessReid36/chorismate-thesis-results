negatives_armA: the 26 runs kept as physical files, then read (y24).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 224 regular files of
   the 26 runs, in one tar.xz. Every member's sha256 was checked against HPC_MANIFEST.sha256,
   which hpc1 wrote over its own files, after the download; the archive was tested whole again
   where it lies. Nothing of this batch exists only on hpc1.
2. In this repo: the 53 text output files (job.out, job.property.txt and the two PBS logs),
   HPC_MANIFEST.sha256 (the sha256 of every archived file), INVENTORY.tsv (every file with its
   size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.gbw, job.densities, job.bibtex and job.densitiesinfo. This repository's
   own .gitignore excludes all four kinds - "ORCA scratch and wavefunction binaries: large, and
   regenerable from the .inp". The rule of 18 October says the repo gets the final wavefunctions
   themselves and C4's re-optimisations were committed that way, so this is a deviation from that
   rule, decided on 28 October 2026 for Diagnostic 14 and applied here for the same reasons:
   these are fixed-geometry single points whose reading uses job.out alone, the wavefunction
   restarts nothing, and the inputs that would regenerate it are committed beside it. Every one
   of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. y24 deletes nothing on hpc1.

The inputs were committed before the jobs were submitted. Every one was checked byte for byte
against the file hpc1 actually ran, here and again by the reading's own GATE 0.
