d45: the 14 run(s) kept as physical files, then read (cs6_d45_harvest.sh).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 63 files of d45 as they
   stood on hpc1 after the job had ended, together with hpc1's own HPC_MANIFEST.sha256, which is
   64 members in one hpc_all_files_d45.tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after the download,
   and every archive member was checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt for each run that wrote them; the PBS log
   run.pbs.out, and run.pbs.out.part<N> for each earlier submission if the job was submitted
   more than once; PROGRESS.txt, the job script's record of the scratch in use;
   HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256, INVENTORY.tsv (every file with its size and
   category) and OUTPUTS.sha256.
3. NOT in this repo: .peak_mb.
   The split decided on 28 October 2026 for Diagnostic 14: these are fixed-geometry single
   points whose reading uses job.out alone, and the inputs that would regenerate them are
   committed beside them. The job script leaves no wavefunction file at home: each run is made
   in node-local scratch, which is removed when the run ends. Every one of these files is in
   the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. The harvest deletes nothing on hpc1.

job.out is present for 14 of the 14 run(s) and reports normal termination in 14. A run that did
not finish is a result and is kept as it is; the reader reports it.

The inputs were committed and pushed before the job was submitted; the harvest started from
results 11cba65e. Every committed file hpc1 ran was checked against the committed one twice: by
sha256sum -c on hpc1 before the archive was made, and byte for byte between the archive's copies
and this repository's.

The archive is named hpc_all_files_d45.tar.xz.
