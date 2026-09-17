# What the sampling tests establish, and how to proceed

A critical review before committing roughly 1300 hours of compute. Three
conclusions reached earlier today were overturned by later checks; those are
recorded so they are not re-derived.

---

## 1. Correlation times measured, and what each is worth

| observable | τ_int | predicts the barrier? |
|---|---|---|
| θ₂ near-attack angle | **275 ps** (97 ps after 20 ns) | see below |
| θ₁ | 4.1 ps | r = +0.076, no |
| forming C1–C6 | 7.0 ps | r = −0.202, no |
| backbone deviation | not measurable | not applicable |

The backbone figure is excluded because the series is not stationary, and
Grossfield *et al.* (2018) define the correlation time only for a stationary
series, "meaning that τ is independent of t". Two values, 699 and 2349 ps, were
obtained from it depending on the reference structure; neither is a correlation
time.

**The observables differ by two orders of magnitude.** An independence claim
therefore has to name which observable it rests on. The committed
`step11e_autocorr.py` reports 3.2 ps for the forming distance and concludes the
frames are independent; that conclusion is about a distance, not about the
barrier.

## 2. θ₂ does not predict the barrier within the reported set

Across all thirteen frames with an in vacuo barrier, θ₂ deviation correlates at
r = +0.657, p = 0.015. Restricted to the ten satisfying the full near-attack
criterion, which are the frames actually reported:

    all 13 frames          r = +0.657, p = 0.015, r2 = 0.43
    the 10 full NACs only  r = +0.487, p = 0.154, r2 = 0.24

The correlation is substantially carried by the three near-attack failures, which
have large θ₂ deviation by construction and high barriers. Within the reported
set it is not significant.

**So no observable has been shown to predict the barrier among the frames used.**
That is a limitation to state, not a fault to fix: with ten frames the test has
little power, and r = 0.487 is not evidence of absence.

## 3. What follows for the correlation time

Since the driver of the barrier variation is unidentified, the defensible choice
is the slowest correlation time among the candidate observables, which is θ₂'s.
That is conservative rather than demonstrably correct, and should be described
that way.

Chodera's (2016) equilibration scan on θ₂ gives a genuine interior maximum:

        t0 / ps   τ / ps   N_eff
              0    275.2     109
          10000    183.8     136
          20000     97.4     205   <- maximum
          24000    122.4     147
          28000    125.4     128

Two things follow. The maximum is interior, not at the edge of the scan, so it is
not an artefact of the range. And τ itself falls from 275 to 97 ps as the discard
point advances, which means θ₂ is not stationary over the full record either: the
first 20 ns carries slow structure that the extension does not.

Chodera's data-sufficiency caveat is satisfied: "the data itself should be
suspect if the trajectory is not at least an order of magnitude longer than the
minimum estimated autocorrelation time." Here 60000 ps against 275 ps is 218-fold,
and the post-discard region is 40000 ps against 97 ps, 412-fold.

## 4. The resulting selection rule

Discard to **20000 ps**, the value Chodera's criterion selects, rather than the
11000 ps read off backbone block means by eye.

Within the remaining 40000 ps, τ(θ₂) = 97 ps, so the statistical inefficiency
g = 1 + 2τ = 195 ps and one uncorrelated sample arrives every 195 ps. At the more
conservative 5τ the spacing is 485 ps.

Thirty frames drawn from 40000 ps sit at roughly 1330 ps apart, which is 2.7 times
the conservative requirement and 6.8 times g. **Thirty frames is supportable**,
provided they come from after 20000 ps.

The existing thirty-frame selection does not satisfy this: it was drawn from
11000 ps onward, and its closest pairs are about 210 ps apart. It should be
redone.

## 5. What is unaffected by any of this

**The barrier ensemble reproduces the published result.** Transition-state
stabilisation −4.32 kcal/mol against Claeyssens *et al.*'s −4.2, gradient 1.062
against 0.95, correlation r = +0.846, on an independent system setup with a
different force field and basis. This is a comparison of measured quantities.

**Test B5.** The non-additive term is bilinear in the two charges to within 8.7%
across a fourfold range, so at design magnitudes it is about 0.01 kcal/mol,
fifty times below the objective's resolution limit. Contributions may be summed.

**Test B6.** The difference-potential map depends on the frame more than on the
basis set, with a site-wise spread of 0.66 to 0.72 kcal/mol at the ten most
stabilising sites. Design against the ensemble mean, not one frame.

**The all-to-all analysis.** 11.3% of pairs separated by 10 ns or more are as
close as typical pairs within 500 ps, the condition Grossfield *et al.* name as
necessary for good statistics.

**The molecular dynamics.** Correctly configured, 300.02 K and 1.0222 density
over the extension.

Whether the frames are formally independent affects the standard error on the
mean barrier. It does not affect the finding that the barrier varies across
conformations, which is what the ensemble exists to establish and what both
Claeyssens *et al.* and Ryde treat as the result.

## 6. How to proceed

1. **Reselect thirty frames from 20000 ps onward**, with a minimum spacing of at
   least 485 ps enforced. Check what `step12b_nac_select.py` currently enforces
   before assuming its maximin rule delivers this.

2. **Wait for the spring test.** It decides whether the scan can produce a usable
   transition-state guess at all. As things stand the restrained path steps over
   the barrier rather than through it in every frame examined.

3. **Run the frames.** The generators are corrected and verified against the
   reference.

4. **Report the sampling honestly**: the correlation time used, which observable
   it came from, that no observable was shown to predict the barrier within the
   reported set, and that the value chosen is the slowest measured rather than
   the demonstrably relevant one.

5. **Revisit the θ₂ question once thirty barriers exist.** With thirty frames the
   correlation within the full-NAC set can be tested with real power, and if
   something else drives the variation it may become visible.

## 7. Conclusions overturned today, for the record

- That the barrier spread indicated a defect. Ryde's survey of 24 QM/MM studies
  puts σ between 0.6 and 97 kJ/mol with 73% above 10; this work is at 22.
- That ORCA's separate quantum and classical energies could be read as chemistry
  and environment. Under electrostatic embedding the quantum term already
  contains the coupling.
- That the frames were independent because the forming distance decorrelates in
  3.2 ps. That distance does not predict the barrier.

---

## References

Chodera, J.D. (2016) doi:10.1021/acs.jctc.5b00784.
Claeyssens, F. *et al.* (2005) doi:10.1039/b508181e.
Grossfield, A. *et al.* (2018) doi:10.33011/livecoms.1.1.5067.
Hur, S. and Bruice, T.C. (2003) doi:10.1073/pnas.1534873100.
Ryde, U. (2017) doi:10.1021/acs.jctc.7b00826.
