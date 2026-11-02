d22: the 30 runs kept as physical files, then read (y45).

The walled and wall-at-zero legs of d_shield, with STABPerform, at def2-SVPD. Eighteen walled
arms and twelve wall-at-zero arms, the latter shared where conditions share a position set.

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 663 files, together
   with hpc1's own HPC_MANIFEST.sha256, as 664 members in one tar.xz. hpc1 wrote the manifest
   over its own files before the download; every file was checked against it after the download,
   and every archive member again where the archive lies. Nothing of this batch exists only on
   hpc1.
2. In this repo: the 61 text output files (job.out, job.property.txt and the PBS log),
   HPC_MANIFEST.sha256, INVENTORY.tsv, OUTPUTS.sha256 and DIAGNOSTIC22_RESULT.txt.
3. NOT in this repo: job.gbw, job.densities, job.bibtex, job.densitiesinfo and the stability
   analysis's .tmp scratch, excluded by this repository's .gitignore. Same deviation from the rule
   of 18 October decided on 28 October for Diagnostic 14: these are fixed-geometry single points
   read from job.out alone, the wavefunction restarts nothing, and the inputs that regenerate it
   are committed beside it. Every one is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. y45 deletes nothing on hpc1.

The inputs were committed before submission. GATE 0 above checked all 32 of them byte for byte
against the files hpc1 actually ran.

READ ALONGSIDE STAGE6_DIAGNOSTIC22_ERRATUM1_20261102.txt. Two of the nine conditions, S6-2_D16
and S6-5_D17, carry no readable Dset: their bare arm at R is STRAINED under D6.3. Their arms are
measured here and reported, but their d_shield is not quotable and stability does not change that.
