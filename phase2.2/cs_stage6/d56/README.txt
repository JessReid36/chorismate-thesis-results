d56: the 224 run(s) kept as physical files, then read (cs6_d56_harvest.sh).

Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a
physical file, not only reported.

1. PC archive (PC_ARCHIVES.tsv), in the archive folder on Jessica's PC: all 5480 files of d56 as they
   stood on hpc1 after the jobs had ended, together with hpc1's own HPC_MANIFEST.sha256, which is
   5481 members in one hpc_all_files_d56.tar.xz. hpc1 wrote HPC_MANIFEST.sha256 over its own files
   before the download; the archive was checked against hpc1's copy by sha256 after the download,
   and every archive member was checked against the manifest again where the archive lies.
2. In this repo: job.out and job.property.txt for each run that wrote them; the ten PBS logs
   run_<job>.pbs.out, and run_<job>.pbs.out.part<N> for each earlier submission if a job
   was submitted more than once; HPC_MANIFEST.sha256, INPUT_CHECKSUMS.sha256,
   INVENTORY.tsv (every file with its size and category) and OUTPUTS.sha256.
3. NOT in this repo: job.C0.tmp, job.C1.tmp, job.E.tmp, job.EIJ.tmp, job.FAO0.tmp, job.FAO1.tmp, job.FMO0.tmp, job.FMO1.tmp, job.H.tmp, job.K.tmp, job.K0.tmp, job.K1.tmp, job.P0.tmp, job.P1.tmp, job.PDAT.tmp, job.POLD0.tmp, job.POLD1.tmp, job.S.tmp, job.SC0.gridx1.tmp, job.SC0.gridx2.tmp, job.SC0.gridx3.tmp, job.SC0.gridx_cis.tmp, job.SHARK.KPRSCR.tmp, job.SHARKINP.tmp, job.SINV.grid_cis_factor.tmp, job.SINV.gridx1_factor.tmp, job.SINV.gridx2_factor.tmp, job.SINV.gridx3_factor.tmp, job.SM12.tmp, job.SP12.tmp, job.SQRTVEXT.tmp, job.SQRTVJ.tmp, job.T.tmp, job.V.tmp, job.VAUXJ.tmp, job.VCDJ.tmp, job.VEXT.tmp, job.VM1EXT.tmp, job.VXC0.tmp, job.VXC1.tmp, job.bas0, job.bas1, job.bas2, job.bas3, job.bas4, job.bas5, job.bibtex, job.citations.tmp, job.cpscfdata.tmp.0, job.densities, job.densitiesinfo, job.diisao.tmp.0, job.diise.tmp.0, job.diist.tmp.0, job.en.tmp, job.fxc_cis0.tmp, job.fxc_cis1.tmp, job.fxc_cis2.tmp, job.fxc_cis3.tmp, job.fxc_cis4.tmp, job.fxc_cis5.tmp, job.fxc_cis6.tmp, job.fxc_cis7.tmp, job.gbw, job.gpot0.tmp, job.gpot1.tmp, job.gpot2.tmp, job.gpot3.tmp, job.gpot4.tmp, job.gpot5.tmp, job.gpot6.tmp, job.gpot7.tmp, job.grho0.tmp, job.grho1.tmp, job.grho2.tmp, job.grho3.tmp, job.grho4.tmp, job.grho5.tmp, job.grho6.tmp, job.grho7.tmp, job.grho_cis0.tmp, job.grho_cis1.tmp, job.grho_cis2.tmp, job.grho_cis3.tmp, job.grho_cis4.tmp, job.grho_cis5.tmp, job.grho_cis6.tmp, job.grho_cis7.tmp, job.grid.tmp, job.grid_cis.tmp, job.gridx1.tmp, job.gridx2.tmp, job.gridx3.tmp, job.gridx_cis.tmp, job.hostnames, job.int.tmp, job.opot0.tmp, job.opot1.tmp, job.opot2.tmp, job.opot3.tmp, job.opot4.tmp, job.opot5.tmp, job.opot6.tmp, job.opot7.tmp, job.orho0.tmp, job.orho1.tmp, job.orho2.tmp, job.orho3.tmp, job.orho4.tmp, job.orho5.tmp, job.orho6.tmp, job.orho7.tmp, job.propint.tmp.0, job.shark_grid.tmp, job.soscfv.tmp.0, job.stabsigma.0, job.stabtrial.0, job.stabvec, job.stabvec.dvd1.tmp, job.stabvec.dvd2.tmp, job.stabvec.dvd3.tmp, job.stabvec.dvd4.tmp.
   Wavefunction and scratch files are excluded by this repository's own .gitignore, the split
   decided on 28 October 2026 for Diagnostic 14: these are fixed-geometry single points whose
   reading uses job.out alone, and the inputs that would regenerate them are committed beside
   them. Every one of these files is in the PC archive with its sha256 in HPC_MANIFEST.sha256.
4. The harvest deletes nothing on hpc1.

job.out is present for 224 of the 224 run(s) and reports normal termination in 222. A run that did
not finish is a result and is kept as it is; the reader reports it.

The inputs were committed and pushed before any job was submitted; the harvest started from
results 9d6fe0ca. Every committed file hpc1 ran was checked against the committed one twice: by
sha256sum -c on hpc1 before the archive was made, and byte for byte between the archive's copies
and this repository's.

The archive is named hpc_all_files_d56.tar.xz.
