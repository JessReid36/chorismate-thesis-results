# Sampling quality: what must be settled, and in what order

The decision to run further QM/MM frames rests on how many statistically
independent configurations the trajectory holds. That number is not yet known:
the two measurements taken so far disagree by a factor of 3.4, and neither is
valid, because both were computed from a non-stationary observable that the
literature does not recommend for the purpose.

Nothing here affects the barriers already computed or the tests of the design
objective. What it affects is how many further frames are worth running, which is
the decision that has not been taken.

---

## A. Extend the observables across both trajectory files

- [ ] **A1** Apply `patch_step11c_dual.sh`, producing
      `step11c_rxn_coord_full.sh`. It works on a copy, so the committed original
      is untouched.
- [ ] **A2** Confirm the copy reads both files and writes to a new path:
      `grep -n "prod_ext.nc\|_full.dat" step11c_rxn_coord_full.sh`
- [ ] **A3** Run it under the batch system. It reads coordinates only, with no
      superposition, so it is far cheaper than the deviation trace.
- [ ] **A4** Confirm 60000 rows in `rxn_coord_per_frame_full.dat`.

## B. Establish whether any observable is stationary

- [ ] **B1** Run `sampling_quality.py`. Its first table reports, for each
      observable, the drift between the first and last tenth of the record
      against the mean within-block scatter.
- [ ] **B2** Record which observables pass. An observable whose drift exceeds
      twice its fluctuation is not stationary, and Grossfield *et al.* (2018)
      define the correlation time only for a stationary series: "Such
      correlations are often stationary, meaning that τ is independent of t."
- [ ] **B3** If none passes, stop. Report that no effective sample size can be
      quoted from this trajectory, and do not select frames on the basis of one.

## C. Choose the equilibration point by a stated criterion

- [ ] **C1** From the same run, read the scan over discard points. Chodera (2016)
      selects the value that maximises the effective sample size of what remains,
      rather than one read off block means by eye, which is how the present
      11000 ps was chosen.
- [ ] **C2** Compare that value against 11000 ps. If they differ materially, the
      existing selection of thirty frames should be redone from the new cut.
- [ ] **C3** Check the warning about metastability. Grossfield *et al.* note the
      method "can simply result in restricting the production region to the last
      sampled metastable basin" when the run is too short to sample transitions.
      The script flags this when the chosen discard exceeds two fifths of the
      record.

## D. Test whether the trajectory revisits states

- [ ] **D1** Run `11d_all_to_all.pbs` at a 100 ps stride: 600 structures, 179700
      pairwise fits.
- [ ] **D2** Read the revisiting fraction. The guide states that off-diagonal
      regions of low deviation between structures sampled far apart in time
      "indicate that the system is revisiting previously sampled states, a
      necessary condition for good statistics".
- [ ] **D3** If nothing revisits, record that the effective sample size is an
      upper bound and that the trajectory samples one basin. That would mean
      running many frames from it adds little, whatever the correlation time.

## E. Apply the literature's own consistency test

- [ ] **E1** Recompute the barrier statistics with the frames split at whatever
      discard point C1 selects.
- [ ] **E2** Grossfield *et al.*: "if values of observables estimated from the
      production phase depend sensitively on the choice of t_equil, it is likely
      that further sampling is required." With the present four and six frames
      the test is inconclusive: means of 16.69 and 11.62 kcal/mol differ by 5.08,
      which is not significant (Welch t = 1.48 on 5.1 degrees of freedom).
- [ ] **E3** Record the outcome as inconclusive if it remains so, rather than
      reading the direction of a non-significant difference.

## F. Decide the number of frames, with the reasoning recorded

- [ ] **F1** State the effective sample size, the observable it came from, and
      the method, since the guide is explicit that "no single method described
      here has emerged as a clear best practice".
- [ ] **F2** Decide how many frames to run. Frames beyond the effective sample
      size are not useless, since correlated samples still reduce variance, but
      the gain is sublinear and should not be presented as though it were not.
- [ ] **F3** Record the decision and its basis before submitting anything.

## G. Independent of the above

- [ ] **G1** The spring test decides the restraint stiffness for whatever frames
      are run. It does not depend on the sampling question.
- [ ] **G2** Frame 08170 still needs a better guess or a documented exclusion.
- [ ] **G3** The reference transition state's two imaginary modes remain an open
      audit item.

---

## What is already established, and is not in question

- The molecular dynamics is correctly configured and its averages are sound:
  300.02 K and a density of 1.0222 over the extension.
- The drift observed is the behaviour Grossfield *et al.* describe as ordinary.
  Their worked example shows the same signature over roughly 200 ns; this system
  has 60.
- The fourteen barriers, the stabilisation analysis reproducing Claeyssens *et
  al.*, and tests B1 through B6 of the design objective are unaffected.

## References

Chodera, J.D. (2016) 'A simple method for automated equilibration detection in
molecular simulations', *Journal of Chemical Theory and Computation*, 12(4),
pp. 1799–1805. doi:10.1021/acs.jctc.5b00784.

Grossfield, A., Patrone, P.N., Roe, D.R., Schultz, A.J., Siderius, D.W. and
Zuckerman, D.M. (2018) 'Best practices for quantification of uncertainty and
sampling quality in molecular simulations', *Living Journal of Computational
Molecular Science*, 1(1), 5067. doi:10.33011/livecoms.1.1.5067.
