# The Stage 6 per-site charge vectors as a file

**3 November 2026.** Written by `phase2.2/cs6_charges.py` (code repo) from each bare arm's
committed `pc.pc`. Two files, both in `phase2.2/cs_stage6/`:

| file | one row per | columns |
|---|---|---|
| `CHARGE_VECTORS_20261103.tsv` | point charge, 77 rows | condition, diagnostic, stem, tree, point, site, layer, on_atom, x, y, z, q, clearance_A, q_min_neg, q_min_pos |
| `CHARGE_VECTORS_SUMMARY_20261103.tsv` | condition, 9 rows | condition, diagnostic, stem, tree, n, sum_abs_q, max_abs_q, min_q, max_q, n_positive, n_negative, readable_D6_3, source, source_sha256 |

## Why this file exists

`RESULTS_charge_representation_domain_DRAFT_ERRATUM1_20261102.md` corrected a max|q| column that had
been populated from memory rather than from each bare arm's `pc.pc`, and two correlations computed
from it. The vectors themselves were never wrong; they were only ever reachable by reading ORCA
inputs or `relax/ARRANGEMENTS.txt` prose, so a figure derived from them had to be remembered.
**Every max|q| or Σ|q| figure from here on is read from these files or from `pc.pc`, and from
nothing else.**

## Where the numbers come from, and what was checked before they were written

- **The charges and coordinates are the bytes the ORCA inputs carry.** `pc.pc` is read as ORCA
  reads it — a count, then `q x y z` per line — and the charge column is copied as a string, not
  re-formatted. The reactant and transition-state `pc.pc` of all nine conditions are **byte
  identical**, which is checked before anything is written: the designed charges do not move with
  the geometry, so one vector per condition is a fact and not a convention.
- **Site identity comes from `sites_f42436.tsv` by exact coordinate match**, to within 1e-06 Å, and
  every point is required to match exactly one site. That table's sha256 is checked against the one
  `relax/ARRANGEMENTS.txt` records as its own input, so the site numbering here is the numbering the
  arrangements were built with.
- **Every derived figure is checked against the corrected record.** The nine max|q| values re-derive
  to the nine figures the committed Results draft states in its verification log, string for string,
  and each condition's Σ|q| re-derives to the value in its own label — 1.3000, 1.0777, 1.6166 and
  2.1900 e. The summary file is also recomputed from the detail file and must agree with both.
- **The generator is deterministic**: it is run twice and the two outputs must be byte identical.

## What the files are for

The figure of the accessible design region: Σ|q| against max|q| for all nine conditions, readable
points filled and the two STRAINED exclusions open, with D17's per-site band of 0.5389 to 0.6500 e
shaded. Both exclusions are in the file with `readable_D6_3 = no`, so the figure can be drawn from
one file without reconstructing which conditions were withheld.

The `clearance_A`, `q_min_neg` and `q_min_pos` columns come along because they are what the site
table carries beside each position, and because they say what the placement rule allowed at that
site rather than what was chosen.

## What they are not

- **Not a new measurement.** Nothing here was computed; the vectors are the committed inputs and the
  site attributes are the committed site table. No barrier, Dset, stability margin or readability
  verdict is touched.
- **Not a licence for the two post-hoc correlations.** The bare and walled stability margins against
  max|q| — −0.775 and +0.338 — are still post hoc on nine points at one basis and one frame, and
  having the vectors in a file makes them no more quotable. The pre-registered test is a max|q|
  ladder at fixed Σ|q|, and it has not been run.
- **Not the full arrangement record.** `relax/ARRANGEMENTS.txt` remains the account of how each
  arrangement was placed, with the ranking, the budget and the admissible charge interval per site.
  This file is the result of that placement, not its justification.
- **Not every charge in Stage 6.** The nine whole-design conditions only. The single-site additivity
  arms, the q-scale ladder and the standoff series carry their own `pc.pc` files and are not
  collected here; `n10_bare_A` appears because it is one of the nine, as DIAGNOSTIC 15's arm A.
