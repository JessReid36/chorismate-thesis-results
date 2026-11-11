d37: the 28 runs kept as physical files, then read (cs6_d37_harvest.sh).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 207 files of d37 as they
   stood on hpc1 after the job had ended, together with hpc1's own HPC_MANIFEST.sha256, which is
   208 members in one hpc_all_files_d37.tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after the download,
   and every archive member was checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt for each run that wrote them, the PBS log
   run.pbs.out, HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256, INVENTORY.tsv (every file with its
   size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.bibtex, job.densities, job.densitiesinfo, job.gbw.
   Wavefunction and scratch files are excluded by this repository's own .gitignore, the split
   decided on 28 October 2026 for Diagnostic 14: these are fixed-geometry single points whose
   reading uses job.out alone, and the inputs that would regenerate them are committed beside
   them. Every one of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. The harvest deletes nothing on hpc1.

job.out is present for 28 of the 28 runs and reports normal termination in 24. A run that did not
finish is a result and is kept as it is; the reader reports it.

The inputs were committed and pushed before the job was submitted; the harvest started from
results 19424803. Every input hpc1 ran was checked against the committed one twice: by sha256sum -c on
hpc1 before the archive was made, and byte for byte between the archive's copies and this
repository's.

The archive is named hpc_all_files_d37.tar.xz.
