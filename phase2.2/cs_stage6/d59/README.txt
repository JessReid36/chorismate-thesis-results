d59: the 286 run(s) kept as physical files, then read (cs6_d59_harvest.sh).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 6329 files of d59 as they
   stood on hpc1 after the jobs had ended, together with hpc1's own HPC_MANIFEST.sha256, which is
   6330 members in one hpc_all_files_d59.tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after the download,
   and every archive member was checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt for each run that wrote them; the 24 PBS
   logs
   run_<job>.pbs.out, and run_<job>.pbs.out.part<N> for each earlier submission if a job
   was submitted more than once; HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256,
   INVENTORY.tsv (every file with its size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.C1.tmp, job.EIJ.tmp, job.H.tmp, job.K.tmp, job.PDAT.tmp, job.S.tmp, job.SHARK.KPRSCR.tmp, job.SHARKINP.tmp, job.SQRTVJ.tmp, job.T.tmp, job.V.tmp, job.VAUXJ.tmp, job.VCDJ.tmp, job.bas0, job.bas1, job.bas2, job.bas3, job.bas4, job.bas5, job.bibtex, job.citations.tmp, job.densities, job.densitiesinfo, job.fxc_cis1.tmp, job.fxc_cis2.tmp, job.fxc_cis3.tmp, job.fxc_cis4.tmp, job.fxc_cis5.tmp, job.fxc_cis6.tmp, job.fxc_cis7.tmp, job.gbw, job.grho_cis1.tmp, job.grho_cis2.tmp, job.grho_cis3.tmp, job.grho_cis4.tmp, job.grho_cis5.tmp, job.grho_cis6.tmp, job.grho_cis7.tmp, job.int.tmp.
   Wavefunction and scratch files are excluded by this repository's own .gitignore, the split
   decided on 28 October 2026 for Diagnostic 14: these are fixed-geometry single points whose
   reading uses the text files kept here, and the inputs that would regenerate them are committed beside
   them. Every one of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. The harvest deletes nothing on hpc1.

job.out is present for 286 of the 286 run(s) and reports normal termination in 226. A run that did
not finish is a result and is kept as it is; the reader reports it.

The inputs were committed and pushed before any job was submitted; the harvest started from
results bb269d21. Every committed file hpc1 ran was checked against the committed one twice: by
sha256sum -c on hpc1 before the archive was made, and byte for byte between the archive's copies
and this repository's.

The archive is named hpc_all_files_d59.tar.xz.
