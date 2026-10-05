# 05_qmmm/20_invacuo - in vacuo single points

B3LYP-D3BJ/def2-SVP, def2/J, RIJCOSX, TightSCF single points of the 24-atom chorismate
dianion (charge -2, singlet) at each frame's QM/MM-optimised R, TS and P geometries.
No MM charges, no continuum. Produced by s8_invacuo*.pbs; their logs are here.

Frames: 44.
- 30 post-cut frames, 20000-59999: the Phase 2.2 set used by grid_v2.tsv and A_v2.tsv.
- 14 pilot frames, 02450-19185, from before the 20 ns cut. Kept as a record; not used
  for reported results.
- Missing: 08170 TS (pilot frame), no geometry and no single point.

Run dates (by .gbw time): 15 Sep 41 sets, 23 Sep 12, 28 Sep 12, 29 Sep 42,
30 Sep 24 (the eight late frames, s8_invacuo_gap.pbs). 131 sets in total.

Coordinates are the ORIGINAL QM/MM frame of reference, not aligned. Phase 2.2 builds
its grid in s16-aligned space and maps each site back into these coordinates with the
inverse of that frame's s16 transform before calling orca_vpot.

Not in git: .gbw and .densities (excluded by .gitignore). Their sha256 sums are in
CHECKSUMS_binaries.sha256; the files stay on hpc1 in
/home/18660916/system_development/05_qmmm/20_invacuo/. Verify there with
    sha256sum -c CHECKSUMS_binaries.sha256
CHECKSUMS_text.sha256 holds the sums of the committed text files as they left hpc1.

Deliberately excluded: sp_24883_R.xyz, sp_24883_R.eldens.cube and sp_24883_R.K.tmp,
written 30 Sep 2026 19:57-20:11 during the rejected density-file work (s15b). The
sp_24883_R .out/.gbw/.densities date from 23 Sep and are the original single point:
FINAL SINGLE POINT ENERGY -836.142478341 Eh, matching E_vac_R in ensemble_barriers.tsv.
