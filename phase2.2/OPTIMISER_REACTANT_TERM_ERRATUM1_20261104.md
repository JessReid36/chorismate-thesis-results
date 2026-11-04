# ERRATUM 1 to OPTIMISER_REACTANT_TERM_FINDING_20261103.md

4 November 2026. `OPTIMISER_REACTANT_TERM_FINDING_20261103.md` **IS NOT EDITED.** Its sections 1 to 5,
7 and 8 stand unchanged, and so does its conclusion that the question has not been asked and that
asking it is free. **Section 6 names the wrong files.** The data it claims is in the repository is in
the repository, in a different file, at a different grid, written by a different script.

Nothing is withdrawn. No measured number is affected, because the finding measured nothing.


## E1.1 WHAT SECTION 6 SAYS

> `cs5x_dev_amatrix.py` line 165 builds each column of `A` as `(vpot(vpot_<f>_TS.out) -
> vpot(vpot_<f>_R.out)) * H` from two separate files. Those files are committed:
> `phase2.2/cs_stage5/exploratory/dev_A/job/vpot_*_R.out` 100 files, `..._TS.out` 100 files.
> `V_R` at every site on every frame is therefore already in the repository.

Three things are wrong with that, and the third is the one that matters.

**(a) The count.** There are **30** of each, not 100:

    git ls-files 'phase2.2/cs_stage5/exploratory/dev_A/job/vpot_*_R.out'   ->  30
    git ls-files 'phase2.2/cs_stage5/exploratory/dev_A/job/vpot_*_TS.out'  ->  30

covering 30 frames, from 20000 to 59999, including 42436.

**(b) The matrix.** `cs5x_dev_amatrix.py` is not the production script. `A_dev.tsv`'s own first line
says so: "EXPLORATORY development A matrix, cs5x_dev_amatrix.py ...: **NOT Stage 5 production**". The
production matrix is `A_f42436.tsv`, assembled by `cs5_amatrix.py`, and that is the matrix
`relax/ARRANGEMENTS.txt` records as the one every Stage 6 design was chosen from.

**(c) The grid, which is fatal to section 6 as written.** The exploratory potentials are evaluated at
a different set of points. `dev_A/job/row_order.txt` states them: rows 0 to 2768 from
`cs_stage5/exploratory/dev_sites.tsv`, rows 2769 to 3001 from `grid_v2.tsv` as a control, 3002 rows
in total. The production sites are the 2626 of `sites_f42436.tsv`. Matching every production site to
its nearest exploratory point, measured 4 November 2026:

    production sites matching an exploratory point within 1e-6 A :   0  of 2626
    nearest-neighbour distance                                   :   median 0.3014 A, max 1.0382 A

**Zero.** A diagnostic built on section 6 as written would have decomposed a different A matrix at
different points from the one the designs were optimised against, and would have looked as though it
had worked.


## E1.2 THE FILE SECTION 6 SHOULD HAVE NAMED

    phase2.2/cs_stage6/absolute_potentials/V_f42436.tsv
    sha256 7b24124a6bac673f57923ad3835535cfc76285af26277b2e64ee462919c49eaf

Its own header states what it is: "absolute electrostatic potential of the bare substrate at every
grid site, kcal/mol per e", "read back from the committed a_matrix outputs by `cs6_potentials.py`;
NO new calculation", at `sites_f42436.tsv` sha256 `d2a750...` — the production sites — with one row
per site and columns `site`, `V_R`, `V_TS`, `V_P`.

**Its reproduction claim is checked here independently rather than taken from its header.** Over all
2626 sites, 4 November 2026:

    (V_TS - V_R)  against  A_f42436.tsv    max |difference| 1.000e-06 kcal/mol per e, median 7.105e-15
    (V_P  - V_R)  against  AP_f42436.tsv   max |difference| 1.000e-06,                 median 7.105e-15

1.0e-06 is one unit in the last printed decimal of the committed files, so the agreement is exact to
the precision at which both are stored. And `A_f42436.tsv`'s sha256 is
`a7faa6c5cacc2f2ee0956f80a1a6645eed1e04cc126830d5f5803d9762eae553`, which is what
`relax/ARRANGEMENTS.txt` records for the A matrix the designs were chosen from, so the matrix has not
changed since.

So section 6's CONCLUSION survives intact: `V_R` at every production site is committed, the reactant
term is a dot product over committed numbers, and the check needs no SCF, no `orca_vpot` call and no
HPC. Only its sourcing was wrong.


## E1.3 TWO THINGS THE CORRECT FILE SHOWS THAT SECTION 6 COULD NOT

Reported here because they bear on how DIAGNOSTIC 25 should be designed, and because they are
properties of a committed column rather than measurements of any design.

**`V_R` does not change sign anywhere on the grid.** Across all 2626 sites it runs from
**-164.3739** to **-71.6115** kcal/mol per e. The substrate is a dianion, so its potential is
negative everywhere outside it. Consequently the sign of `dE_R = sum_i V_R,i q_i` is governed by the
design's NET CHARGE, and site placement only modulates the magnitude, within a factor of about two.

**The quantity being optimised is far smaller than the term it cannot see.** `a = V_TS - V_R` spans
**-6.8436** to **+8.3853** kcal/mol per e, while `|V_R|` is of order 100. The catalytic field is a
small difference between two large and nearly equal potentials, and the reactant-side term that the
objective discards is roughly an order of magnitude larger per unit charge than the term it keeps.

Neither statement says any design is reactant-destabilising. That is DIAGNOSTIC 25's question and it
is not answered here.


## E1.4 STANDING

Sections 1, 2, 4, 5, 7 and 8 of the finding are unaffected. Section 3's argument is unaffected and is
strengthened by E1.3, which was not available to it. Section 7's proposed DIAGNOSTIC 25 stands as the
right next step, with its source corrected to E1.2's file.

The finding's own section 8 says sections 1, 2 and 6 are "readings of committed code and committed
file listings and are checkable by inspection". Section 6 was checkable by inspection and was wrong;
this erratum is the inspection.
