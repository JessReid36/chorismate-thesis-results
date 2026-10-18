# Package amendment: answers to questions 1–7 from the literature (18 October 2026)

Jessica asked for each question to be settled by the literature standard, not by one or two papers, with each answer
checked three times. This document supersedes the recommendations in `PACKAGE_AMENDMENT_BRIEF_20261018.md`.

**How it was done.**
- Four readers read their assigned papers in full (every page, tables from rendered pages). The papers are all of
  chorismate-refs at 28eec7b that bear on these questions, plus the Project's copies of Claeyssens 2011, Szefczyk 2004
  and Agbaglo 2024.
- **Pass 1:** I drafted the answers and checked the load-bearing quotes against the PDFs.
- **Pass 2:** an independent reviewer re-checked every quote, count and conclusion against the PDFs. It found one paper
  that changes question 1 (Li & Hartke 2013), misreadings in questions 4 and 6, and an unstated downward direction in
  question 5.
- **Pass 3:** I verified the reviewer's new sources myself and rewrote the answers below.

**Conventions.** Pages are printed pages. "ms" marks the accepted-manuscript versions (Ryde 2017, Kulik 2016, Grossfield
2018, Agbaglo 2024).

Every answer states which way it moves the reported barrier ("Direction").

---

## 1. Which reactant the barrier is measured from

**Answer.**
- **The primary quantity stays B_sp = E(TS) − E(R_IRC),** as SP_PLAN fixed it before any result.
- **Added now, before any package result:** every frame and the ensemble also report the effective barrier
  B_eff = E(TS) − min(E(R_IRC), E(R0)).
  - Where R0 lies below R_IRC, B_sp is stated to be a lower bound.
  - In the package, R0 is the only second reactant search, so B_eff captures only what R0 finds.
- **Frame 42436's lower reactant** (smoke test 1, exploratory) is reported as found: 2.85 kcal/mol below R_IRC, B_eff
  16.88 against B_sp 14.03.

**Direction:** B_sp is the lower definition. B_eff is the higher one and is reported beside it.

**The literature.**
- **For an enzyme barrier from minimised paths, the chorismate mutase (CM) standard is the reactant on the TS's own
  path.**
  - Claeyssens 2011 plots each path "relative to the lowest point on the reactant (substrate) side" (p.1581). It checks
  that reactant by unrestrained re-optimisation (<1 kcal/mol, p.1580).
  - Claeyssens 2005, Senn 2009 (CM), Ranaghan 2004 and Klähn 2005 do the same.
  - B_sp is like for like with the comparator's enzyme value.
- **Where a distinct lower reactant state is known, the literature puts its cost into the barrier:**
  - **Li & Hartke 2013** (explicit water clusters) reference the barrier to the globally optimised reactant cluster
    ("was used as a reference"). The IRC-connected reactant lies 4.2 kcal/mol above it. Measured from the IRC reactant,
    "the effective barrier ... is lowered by this amount (in the scenario that the cluster re-arranges itself along the
    reaction pathway)". They call barriers from re-optimised solvent "lower bounds".
  - **Claeyssens 2011** (p.1583) adds the cost of the lower substrate conformer in water, 0.9–3.6 kcal/mol: it "should
    be added to the computed reaction barrier".
  - **Kästner 2006** (p.457) found a more stable minimum lacking the TS's hydrogen bond ("the transition state belongs
    to a different manifold"). Their free-energy perturbation starts from the more stable manifold.
- **Why the primary is not switched to B_eff:**
  - It would change a pre-registered definition after a result was seen.
  - It would break like-for-like with Claeyssens' enzyme value.
  - Ryde 2016's "same local minimum" rule (p.130) and the free-energy cure ("The proper way to cure it is to calculate
    free energies") both caution against treating one minimised lower reactant as the reference.

  Reporting both, with B_sp named as a lower bound, follows all of these.

---

## 2. How C4 closes

**Answer.**
1. Collect C4's 35 runs under the 18 October rule.
2. Complete steps 0–2 exactly as pre-registered, including M1 continuations, and report them whatever they show. Step 2
   answers the Phase 1 audit's own question for the write-up.
3. Close C4 with a new amendment, named so it does not clash with the dropped draft "Amendment 2". It does not run steps
   3–6 and says why.
4. The amendment discloses that the decision follows the provisional step-2 results (13 of 13 frames failed A1).

**Why steps 3–6 are not run.**
- **Step 3 (forth and back) is a check some authors use, not the standard route.**
  - Ryde 2016 (p.130) lists it among three ways to detect local minima and calls it "tedious and time consuming". Ryde
    2017 (ms p.3) names it among strategies.
  - Senn 2009 scans each CM snapshot in both directions as a check ("at most 1.0 and 0.5 kJ mol–1", p.1332). Zhang 2000
    maps forward and reverse paths.
  - The "more common approach" is several snapshots (Ryde 2016 p.130). That is the SP package.
- **Repairing the band would carry its flaw forward.** Every band held the first-shell waters fixed (audit A8), and a
  step-3 repair in the same band setup keeps it.
- **The concern step 3 targets, a lower reactant than the band's, is carried on the SP route by B_eff** (question 1).
- **Step 5 is not replaced.** The SP route's region sensitivity rests on one frame: 6 against 8 Å differ by
  1.07 kcal/mol, above C4 step 5's own 1.0 kcal/mol tolerance. That is reported as a limitation. Question 5's check
  tests the frozen boundary on three frames.
- **Step 6** belongs to the Phase 2 redesign.

**Direction:** dropping step 3 removes the band-repair candidate, which step 2's data suggest would be higher. On the SP
route that direction is represented by B_eff.

---

## 3. Attrition

**Answer.**
- The 30 frames are fixed in advance and none is replaced. A frame failing a pre-registered check is reported with the
  step it failed and the values it reached. Only A1.5's machinery stops are re-run, once. Every frame's values are
  tabulated.
- The ensemble needs at least 20 complete frames. Below that it is reported but not used as the Phase 1 barrier
  (SP_PLAN's rule). C4's "more than 3 dropped" rule is retired with C4's step 3.
- A selectivity check compares the failed frames' band barriers (`barrier_klow`) with those of the complete frames.
- The 20-frame floor is a minimum, not a guarantee of precision. The 95% confidence interval (question 4) shows the
  precision actually reached.

**Direction:** none. The check catches non-random failures.

**The literature.**
- No barrier study in the library excludes, replaces or re-runs failed snapshots. In every one, the number reported is
  the number used:
  - Claeyssens 2005: 16;
  - Claeyssens 2011: 16 + 24;
  - Senn 2009: 10;
  - Agbaglo 2024: 250;
  - Li & Chan 2025: 11 per condition.
- Problems were handled across the whole set. Claeyssens 2011 replaced AM1/PM3 starting structures, whose dynamics
  formed an Arg90–Glu78 interaction, and reported the effect (about 0.7 kcal/mol). Outliers were kept and explained
  (Agbaglo, frame 394).
- Grossfield 2018 (ms p.9): do not "cherry-pick" data, and "Use all of the available data unless there is an objective
  and compelling reason not to". A pre-registered check applied to every frame is such a reason.
- **Minimum.**
  - Grossfield & Zuckerman 2009 (p.29): an average from "fewer than ~20 statistically independent configurations ...
    should be considered unreliable".
  - Agbaglo 2024 (CM, 250 frames): 20 "may not be a robust amount".
  - The frames are independent on the project's own rule: at least 650 ps apart, against the 485 ps set as 5τ of the
    slowest observable (DECISION_SAMPLING.md, τ(θ₂) = 97 ps).

---

## 4. Primary statistic

**Answer.**
- **Primary:** the arithmetic mean of the complete frames' B_sp, given with the sd, a 95% confidence interval
  (t-distribution, n − 1 degrees of freedom) and n. It is compared, as the CM papers do, with ΔH‡ = 12.7 ± 0.4 kcal/mol
  and with Claeyssens' 11.3 ± 1.8. The same statistics are given for B_eff.
- **Comparisons** (enzyme against water, against designs): the difference of means, with a 95% confidence interval
  (Welch).
- **Secondary, as estimates of the free-energy barrier, compared with ΔG‡ = 15.4 kcal/mol:**
  - the exponential average;
  - Ryde's cumulant estimate, mean − σ²/2RT, with a normality check;
  - σ in kJ/mol, stated against Ryde's Table 2.

  Both are at 298.15 K.
- Also given: the median, the range and every frame's value.

**Direction:** the mean is the highest of the three estimators. As an estimate of the free-energy barrier it is biased
high (Cooper & Kästner, Ryde). That is stated.

**The literature.**
- **Every CM minimisation paper reports an arithmetic-type potential-energy average and compares it with ΔH‡:**
  - Claeyssens 2005: "12.0 kcal mol−1 (standard deviation, σ = 1.7 kcal mol−1)";
  - Claeyssens 2011: 11.3 ± 1.8, from the averaged profile;
  - Senn 2009: mean ± SEM, "as is usually done in the literature" for ΔH‡;
  - Agbaglo 2024: mean ± σ.

  None averages snapshot barriers exponentially. The enzyme–water comparison is a difference of averages (6.1
  kcal/mol).
- **Outside CM the exponential average is the stated consensus.**
  - Ryde 2017: "the current consensus seems to be to use an exponential average".
  - Cooper & Kästner 2014: with 65 random snapshots, the exponential average (87.5 kJ/mol) is closer to the free energy
    (75.9) than the arithmetic mean (119.9).
- **But at our spread it is badly conditioned.**
  - Ryde 2017: badly conditioned "when σ is large (more than ~7 kJ/mol)". The band barriers have σ 10.7–18.2 kJ/mol.
  - "If σ is above ~10 kJ/mol, the user may prefer to employ the cumulant approximation", with evidence of a Gaussian
    distribution.
  - For ranking, "arithmetic averages give more stable results (but less accurate energies)".
- **The uncertainty is a confidence interval.** Grossfield 2018: the sd "is, in itself, not a measure of the statistical
  uncertainty". Authors "should report (and graph) their best estimates of 95 % confidence intervals".

So the mean is the primary, because the barrier is compared with CM values and between environments. The free-energy
estimators are reported beside it, against the free-energy experiment.

---

## 5. If the surroundings check fails

**Answer.** The check is SP_PLAN's: frames 20000, 44388 and 59999 with S = ci, failing if B_sp changes by more than
2 kcal/mol in at least two of the three. If it fails:
1. The B_sp ensemble is reported but not used as the Phase 1 barrier.
2. A further amendment applies the remedies in this order, each re-checked on the three frames:
   - (a) enlarge the relaxed region towards the CM literature's (16–20 Å);
   - (b) if the dependence persists, extend the QM region (Ryde's rule), with Arg90 first;
   - (c) free energies, the literature's eventual cure, outside this thesis's present scope.
3. SP_PLAN's "both sets are carried forward" is dropped.

**Direction:**
- (a) unknown;
- (b) in every data point in the library a larger QM region lowered the barrier, so (b) would lower it. That is stated
  in advance;
- if the check passes, nothing changes.

**The literature.**
- **Ryde 2016, step 7 (p.148),** the only explicit rule: "optimize the MM system for one state and employ this MM
  structure for all the other states. If ... the results depend on the state for which the MM system is relaxed, the
  QM system needs to be extended until the energies are stable." The S = ci check tests exactly "depends on the state",
  for the atoms frozen beyond 8 Å.
- **CM studies relax far more than 8 Å** (SP_PLAN Limitations):
  - Ranaghan 2004: atoms beyond 16 Å fixed;
  - Claeyssens 2005/2011: a 25 Å sphere with the outer 5 Å fixed;
  - Senn 2009: protein within 17 Å free.

  Because the check varies only atoms beyond 8 Å, matching that practice is the direct remedy. The alternating scheme's
  L-BFGS environment step makes it feasible. (The ordering is my reading; each element is from the literature.)
- **Both worked examples in the library were cured with free energies (QTCP), not by a larger QM region:**
  - Rod & Ryde 2005: 59 against 26 kJ/mol, then 56 kJ/mol by QTCP;
  - Ryde 2016, plastocyanin: 1.5 V reduced to 0.1 V. Enlarging the QM region there swung results between 1.3 and −1.0 V.
- **QM size for CM, both sides:**

  | For a substrate-only QM region | Against |
  |---|---|
  | Claeyssens 2011 (p.1580): "Including active site residues in the QM region does not greatly influence the reaction barrier" | Lee et al. via Ranaghan 2004: 19.7 → 16.6 kcal/mol with Glu78 and Arg90 in QM (RHF/4-31G) |
  | Claeyssens 2005: "insensitive to the size of the QM region" | Li & Chan 2025: rates up 5–27× on adding Arg7 and Glu78 |
  | Szefczyk 2004 (p.16158): "the DTSS analysis validates the QM/MM approach for modeling CM catalysis" | Kulik 2016 (another enzyme): 24 → 16 kcal/mol as the QM region grows |

---

## 6. The designs' barrier definition

**Answer.** Fix now: every barrier compared with the enzyme's is computed by the same chain, with the enzyme's settings
(substrate-only QM, B3LYP-D3BJ/def2-SVP, the same embedding):
- a TS optimised in that system, with one imaginary mode;
- an IRC in both directions whose ends are the reactant and product of the same reaction;
- the reactant and product minimised from the IRC ends;
- B = E(TS) − E(R_IRC);
- B_eff from the lowest reactant found by a stated conformer search, including the pseudo-diequatorial substrate
  conformer, reported beside B as in question 1.

This applies to the bare substrate (the uncatalysed reference) and to every design. Quasi-atoms are held fixed. The
catalytic effect is ΔΔE‡ against the reference in the same medium. A flexible medium (explicit water) is averaged over
configurations with question 4's statistics. NEB-CI may supply the TS start; frozen scores stay screening numbers. The
medium is left to Phase 2.2.

**Direction:** like for like by construction. B_eff stops a design from looking better because its field favours a
non-reactive conformer.

**The literature** (16 design and field papers):
- **Like for like means the reference goes through the same pipeline.**
  - Dittner's thesis sets its thresholds from the pristine path's "fitness ... on PBE0/def2-TZVP".
  - Behrens & Hartke 2021 pass "the reference structure into the fitness function".
  - Claeyssens 2011 uses one QM/MM protocol for enzyme and water.
  - Warshel 2006 asks for "the same formulation".
- **Validation of designs.**
  - The GOCAT papers relax the reactant and product in the fixed charges, then run an NEB. Behrens' thesis: quasi-atoms
    "held fixed throughout the fitness evaluation process, including reactant, product and NEB optimization".
  - Dittner & Hartke 2018 and Dittner's thesis re-optimise final designs to stationary points "with final additional
    frequency checks". Dubey 2020 optimises the TS in the field.
  - Li & Hartke 2013 run TS, frequencies and IRC inside optimised explicit water.

  Our enzyme chain is at the strict end of this practice, so applying it to designs is both like for like and standard.
- **Frozen scores mislead.**
  - Dittner's thesis: relaxing designs produced new reactions.
  - Rankings did not carry over between levels of theory.
  - Hence the IRC check that the reaction is unchanged.
- **The reactant conformer.** Claeyssens 2011 adds the pseudo-diequatorial conformer's cost to the water barrier
  (p.1583), which the conformer search in B_eff covers.
- **The reference medium is disputed.**
  - Szefczyk 2004 calls gas phase "sufficient and convenient for analysis of the nature of interactions". The preceding
    sentence: "For many applications, it is useful to define the TS stabilization with respect to the reaction in
    water."
  - Warshel 2006: water is "the most natural reference state".
  - Phase 2.2 decides the medium. The definition holds either way.

---

## 7. The cycle limit

**Answer.**
- Raise the limit from 8 to 20 cycles, with A1.3's test unchanged. Report every frame's cycle count, including which
  frames needed more than 8.
- The code changes in `spa_prepare.py`, `spa_stage.py` and `spa_report.py` (loop, KMAX, docstrings, rule text). Their
  sha256 records are superseded.
- Added as a limitation: the stopping rule leaves the energy still falling at the last cycle. Extrapolating the last
  cycles (my arithmetic) leaves B_sp about 0.0–0.3 kcal/mol too high.

**Direction:** the limit decides which frames finish, not their values; question 3's check covers that. The limitation
is upward.

**The literature.**
- **No paper sets a cycle cap.** These schemes iterate until their criteria are met (Zhang 2000; Kästner 2006 and 2007;
  Murphy 2000; Senn & Thiel 2009).
- **Zhang's "no more than eight cycles" (p.3489) is an observation.** It is one reactant minimisation (TIM–DHAP), judged
  by gradient criteria, still changing by about 0.1 kcal/mol per cycle at cycle 8.
- **No paper reports cycle counts for an alternating TS search.** The library's TS searches are adiabatic (Senn & Thiel
  p.1206; Kästner 2006 p.455). Prat-Resina 2004, which compares the options, is not held. It cannot change this
  answer, because the convergence test, not the cap, defines the result.
- **A cap is a resource guard, like MaxIter.**
  - Our 8 Å TS core changes shrink by 0.45–0.79 per cycle. A change of 1.5 kcal/mol at cycle 2 shrinking by 0.8
    reaches 0.10 at cycle 15. Twenty cycles cover ratios up to about 0.86. The substrate-shift criterion decays more
    slowly but still fits.
  - Later cycles took up to 3.4 h (R_IRC at 8 Å), so 20 cycles take about 68 h. The worst case, with a 5000-step first
    environment step, is about 161 h, inside the 176 h walltime.
  - The number 20 is mine; the literature supplies its role, not its value.

---

## Papers the library lacks (none needed to settle these answers)

| Paper | Why it would matter |
|---|---|
| Senn & Thiel 2007, Top. Curr. Chem. 268, 173 | The practical guide the 2009 review defers to |
| Prat-Resina et al. 2004, Int. J. Quantum Chem. 98, 367 | Alternating against adiabatic options for an enzyme |
| Crespo et al. 2003, J. Phys. Chem. B 107, 13728 | QM size in CM |
| Lee et al. 2002, J. Phys. Chem. B 106, 12059 | QM size in CM |
| Hall et al. 2000, J. Comput. Chem. 21, 1433 | A CM TS from an asynchronous scheme |
| Lonsdale, Harvey & Mulholland 2010, J. Phys. Chem. B 114, 1156 | Snapshot practice |

DOIs to be confirmed before download, on request.
