# phase2.2/archive_v1_unaligned - the first, UNALIGNED, 30-frame grid and a-matrix

Kept as a record, not for use. grid_v1.tsv was built on the 30 post-cut frames in their raw
MD coordinates, before s16_align_frames.py existed, so a fixed grid point sat in a different
place relative to each frame's substrate. A_v1.tsv is the a-matrix s15 built on it; s15_dv/
is that run's work directory (one shared points file, no transforms). s16's docstring records
what exposed the problem: almost no site agreed in sign across frames.

Superseded by phase2.2/grid_v2.tsv and A_v2.tsv (built in s16-aligned space; s15_dv2/).
row_order.tsv here was committed in 7542aeb as phase2.2/row_order.tsv and moved on 5 Oct 2026.
