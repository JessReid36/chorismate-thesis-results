Diagnostic 14's 148 runs kept as physical files, then read (y21).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 1244 regular files of
   the 148 runs, in one tar.xz. Every member's sha256 was checked against HPC_MANIFEST.sha256,
   which hpc1 wrote over its own files, after the download; the archive was tested whole again
   where it lies. Nothing of this batch exists only on hpc1.
2. In this repo: the 298 text output files (the 148 job.out, the 148 job.property.txt and the
   two PBS logs), HPC_MANIFEST.sha256 (the sha256 of every archived file), INVENTORY.tsv (every
   file with its size and category) and OUTPUTS.sha256.
3. NOT in this repo: the 148 job.gbw (306 MB), 148 job.densities (286 MB), 148 job.bibtex and
   148 job.densitiesinfo. This repository's own .gitignore already excludes all four kinds -
   "ORCA scratch and wavefunction binaries: large, and regenerable from the .inp". The rule of
   18 October says the repo gets the final wavefunctions themselves and C4's re-optimisations
   were committed that way, so this is a deviation from that rule, decided on 28 October 2026 and
   recorded here: these are fixed-geometry single points whose reading uses job.out alone, the
   wavefunction restarts nothing, the inputs that would regenerate it are committed beside it,
   and ~400 MB compressed would be permanent in a history already 1.2 GB. No Stage 6 diagnostic
   has committed a .gbw - DIAGNOSTIC 7, qscale, qrefine, pauli and diffuse all commit job.out
   only. Every one of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. y21 deletes nothing on hpc1.

The inputs were committed before the jobs were submitted. Every one was checked byte for byte
against the file hpc1 actually ran, here and again by the reading's own GATE 0.
