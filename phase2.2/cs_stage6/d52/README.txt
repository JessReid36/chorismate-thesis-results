d52: the 104 run(s) kept as physical files, then read (cs6_d52_harvest.sh).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 2091 files of d52 as they
   stood on hpc1 after the jobs had ended, together with hpc1's own HPC_MANIFEST.sha256, which is
   2092 members in one hpc_all_files_d52.tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after the download,
   and every archive member was checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt for each run that wrote them; the PBS log
   run_K1.pbs.out, and run_K1.pbs.out.part<N> for each earlier submission if the job
   was submitted more than once; HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256,
   INVENTORY.tsv (every file with its size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.B.24.tmp, job.C0.tmp, job.C1.tmp, job.E.tmp, job.EIJ.tmp, job.FAO0.tmp, job.FAO1.tmp, job.FMO0.tmp, job.FMO1.tmp, job.H.tmp, job.K.tmp, job.K0.tmp, job.K1.tmp, job.P0.tmp, job.P1.tmp, job.PDAT.tmp, job.POLD0.tmp, job.POLD1.tmp, job.S.tmp, job.SC0.gridx1.tmp, job.SC0.gridx2.tmp, job.SC0.gridx3.tmp, job.SHARK.KPRSCR.tmp, job.SHARKINP.tmp, job.SINV.gridx1_factor.tmp, job.SINV.gridx2_factor.tmp, job.SINV.gridx3_factor.tmp, job.SM12.tmp, job.SP12.tmp, job.SQRTVC.tmp, job.SQRTVJ.tmp, job.T.tmp, job.V.tmp, job.VAUXC.tmp, job.VAUXJ.tmp, job.VCDC.tmp, job.VCDJ.tmp, job.VM12C.tmp, job.VXC0.tmp, job.VXC1.tmp, job.bas0, job.bas1, job.bas2, job.bas3, job.bas4, job.bas5, job.bibtex, job.citations.tmp, job.cpscfdata.tmp.0, job.densities, job.densitiesinfo, job.diisao.tmp.0, job.diise.tmp.0, job.diist.tmp.0, job.en.tmp, job.gbw, job.gpot0.tmp, job.grho0.tmp, job.grid.tmp, job.gridx1.tmp, job.gridx2.tmp, job.gridx3.tmp, job.hostnames, job.int.tmp, job.opot0.tmp, job.orho0.tmp, job.propint.tmp.0, job.shark_grid.tmp, job.soscfv.tmp.0.
   Wavefunction and scratch files are excluded by this repository's own .gitignore, the split
   decided on 28 October 2026 for Diagnostic 14: these are fixed-geometry single points whose
   reading uses job.out alone, and the inputs that would regenerate them are committed beside
   them. Every one of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. The harvest deletes nothing on hpc1.

job.out is present for 104 of the 104 run(s) and reports normal termination in 80. A run that did
not finish is a result and is kept as it is; the reader reports it.

The inputs were committed and pushed before any job was submitted; the harvest started from
results e08d1dab. Every committed file hpc1 ran was checked against the committed one twice: by
sha256sum -c on hpc1 before the archive was made, and byte for byte between the archive's copies
and this repository's.

The archive is named hpc_all_files_d52.tar.xz.
