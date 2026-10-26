# The charge budget: a physical calibration, and a negative result

Written 26 October 2026, after the six diagnostics and Errata 3 and 4, in answer to two
questions: are the charges in each design split evenly or simply saturated, and why do the
designs past n = 5 come out STRAINED.

**An assessment, not a pre-registration. It changes nothing and fixes nothing.** Every
number in sections 1 to 5 and 7 is re-derived by `phase2.2/y03_field_calibration.py` from
committed files, and that script is read-only with respect to both repos. Nothing here is a
barrier and nothing here is quoted as a result. Corrections to the committed record are in
`STAGE6_ERRATUM5_20261026.txt`, not here. The session's working notes are in the `y03`
section of the work log.

**This document reaches a negative result.** An earlier draft recommended a budget of
Σ|q| ≤ 3.0 e. That recommendation is withdrawn in section 6, for a reason that came from
Erratum 4.

---

## The conclusions, stated first

1. **The charges are neither even nor saturated. They are proportional to −a**, the analytic
   interior optimum of the pre-registered L2 budget. Over S6-20's twenty sites the ratio
   q/(−a) is constant to 10 per cent and decision 3's closed form predicts Σaq to 0.22 per
   cent.
2. **At the best sites the charge is not a decision variable.** Eighteen of the twenty
   top-ranked single sites admit `[1.00, 1.00]` — one value. A per-site cap therefore cannot
   be set independently of the grid (Erratum 5, E5.2).
3. **Under a pure L2 budget "more charges is better" is an algebraic identity**, since the
   best score is −√(B·Σa²) over the chosen sites.
4. **Every committed design applies a field larger than the one measured in this enzyme.**
   Along the breaking C–O the designs give 0.82 to 1.21 V/Å; wild-type BsCM gives 0.20 to
   0.53. The top site, modelled on Arg90, applies about eight times Arg90's own share.
5. **The useful field saturates and the total does not.** From S6-5 to S6-20 the charge
   nearly doubles while the field at the reacting bonds stops improving.
6. **No global scalar on the charge vector orders the def2-SVP verdicts** once Erratum 4
   E4.5's Stage 4c runs are included. Σ|q|, max|q| and n all fail; Σq² separates only inside
   the width of the shared budget. This is the negative result.
7. **What distinguishes them is arrangement, not amount.** The one candidate still standing
   is the peak local field at the substrate, and it is offered as a hypothesis with a
   bracket, not a threshold.
8. **A CLEAN verdict is necessary and not sufficient.** Erratum 4 E4.6 establishes that the
   Pauli wall was pre-registered as the fix, tested, and failed criterion B1 on the
   energetics while recovering the gap.

---

## 1. What was re-derived

`y03_field_calibration.py` reproduces, from `relax/ARRANGEMENTS.txt`,
`frame_42436/reactant_qm.xyz` and the Stage 4c directories alone: the recorded
`sum q^2 (true)` for every design to the fifth decimal; the admitted-charge census of the
ranking block; the proportionality test and decision 3's closed form; the field tables of
sections 4 and 7; and the carboxylate separation. It verifies the geometries against the
sha256 values recorded in `ARRANGEMENTS.txt`, checks that the Stage 4c sphere coordinates
agree between the L1 and L0 levels, and refuses on either mismatch.

Separately, by hand, `DIAGNOSTIC6_RESULT.txt`'s verdict on `qp0800_R` was checked against
the raw ORCA output: HOMO (orbital 58, occupied) −1.7131 eV, LUMO (orbital 59, empty)
−1.2414 eV, gap 0.4717 eV against the 0.472 printed; 36 SCF cycles against the def2-SVPD
control's 14, i.e. 2.57× against 2.6×; largest Loewdin −0.7996 on O7 against the control's
0.339, i.e. +0.461 against +0.461. All three.

`cs6_audit.py` and `cs6_decomp.py` were re-run and reproduce `DIAGNOSTIC6_RESULT.txt` and
`DIAGNOSTIC5_RESULT.txt` byte for byte.

---

## 2. The charges are proportional to −a

| design | n | Σ\|q\| | max\|q\| | Σq² | recorded | distinct \|q\| | gap |
|---|---|---|---|---|---|---|---|
| S6-P | 1 | 1.0000 | 1.0000 | 1.00000 | — | 1 | — |
| S6-2 | 2 | 2.0000 | 1.0000 | 2.00000 | 2.00000 | 1 | 0.00000 |
| S6-3 | 3 | 2.4125 | 1.0000 | 2.00391 | 2.00391 | 3 | 0.00000 |
| S6-5 | 5 | 3.0000 | 1.0000 | 2.01000 | 2.01000 | 3 | 0.00000 |
| S6-10 | 10 | 4.3800 | 0.5500 | 2.02340 | 2.02340 | 5 | 0.00000 |
| S6-20 | 20 | 5.7600 | 0.5500 | 2.04760 | 2.04760 | 7 | **0.55864** |

Only S6-2 is uniform, and only because both its sites sit at a bound. From n = 3 upward
there is a spread of three to seven distinct magnitudes.

Decision 3 predicts q_i = −a_i·√(B/Σa²) and Σaq = −√(B·Σa²) under Σq² ≤ B with a linear
objective and no bound active:

| design | mean q/(−a) | spread | predicted Σaq | actual |
|---|---|---|---|---|
| S6-P | 0.1497 | 0.0% | −6.6778 | −6.6778 |
| S6-2 | 0.1718 | 12.9% | −11.9314 | −11.8340 |
| S6-3 | 0.1477 | 1.2% | −13.5151 | −13.5142 |
| S6-5 | 0.1156 | 17.6% | −16.2371 | −15.9522 |
| S6-10 | 0.1118 | 6.8% | −18.0649 | −18.0335 |
| S6-20 | 0.1062 | 10.3% | **−19.5611** | **−19.5175** |

S6-20 agrees to 0.22 per cent. The worst agreements, S6-2 and S6-5, are exactly those with a
site pinned at a bound, which the derivation says to expect.

**So the first question is answered: the charges are a genuine distribution.** Each site
gets charge in proportion to how much its own differential potential helps — the magnitude
pattern of the Sokalski unit-charge map.

The same closed form also says the best achievable electrostatic score is −√(B·Σa²) over the
chosen sites, so any site with a ≠ 0 improves it. **"More charges is better" is an algebraic
consequence of the constraint form, not a chemical finding** — which is what `s14`'s
docstring and decision 3 both warned of, now measured.

---

## 3. At the best sites the charge is not a decision variable

The ranking block lists the twenty best single sites: **18 admit `[1.00, 1.00]`**, one
`[0.75, 1.00]`, one `[0.25, 1.00]`. That is why S6-P, S6-2, S6-3 and S6-5 all carry a
+1.00 e charge, and it is the ranking-block form of the fact Erratum 4 E4.3 cites from
`OPTIMISER_CODE_README.md` — 1064 sites admit only |q| = 1.

S6-10 and S6-20 use none of the top twenty: Finding 5 records that all twenty lie within
3.25 Å of one another, so the spacing rule admits at most one, and at larger n the optimiser
leaves the pocket for neighbours that admit a range.

A per-site cap below 1.00 e would make those eighteen infeasible rather than restrained, and
`STAGE5_GRID_DEV` records the floors as monotone in q, so the cap and the layer move
together. **A per-site cap is a Stage 5 quantity** (Erratum 5, E5.2). Whether one is needed
at all is Erratum 4 E4.3's question and is not answered here.

---

## 4. The field the designs apply, against measurement

E = 14.39965·q/r² V/Å, in vacuo, no screening, from the committed sphere centres, at every
substrate atom and projected onto each reacting bond at its midpoint. The script identifies
the bonds from the geometry and recovers the breaking O–C at 1.495 Å and the forming C–C at
3.225 Å, matching Finding 7.

| design | Σ\|q\| | mean \|E\| | max \|E\| | E∥(C–O) | E∥(C–C) | ddE |
|---|---|---|---|---|---|---|
| S6-P | 1.00 | 0.614 | 1.644 | 0.694 | 0.195 | −7.68 |
| S6-2 | 2.00 | 0.815 | 1.748 | 0.821 | 0.447 | −12.38 |
| S6-3 | 2.41 | 0.971 | 1.835 | 1.020 | 0.688 | −14.73 |
| S6-5 | 3.00 | 1.244 | 2.199 | **1.214** | 0.721 | −18.16 |
| S6-10 | 4.38 | 1.459 | 2.315 | 1.174 | **1.001** | −21.82 |
| S6-20 | 5.76 | 1.633 | 2.523 | 1.152 | 1.013 | −24.83 |

Siddiqui & Dubey (*PCCP* 2022, 24, 1974, doi:10.1039/d1cp03978d) report the field projected
along the breaking ether C–O of wild-type BsCM as **−0.20 V/Å without solvent and −0.53 with**,
R90A at −0.133 and R90G at −0.095, so Arg90's own share is roughly 0.1 to 0.2 V/Å.

**(a) The designs apply two to six times the whole enzyme's field** along the bond that
breaks.

**(b) The top site applies about eight times the field of the residue it is modelled on.**
A single +1.00 e at 2.96 Å in vacuo gives 1.64 V/Å against Arg90's ~0.2. Independent check:
a guanidinium +1 e at 4–5 Å gives 0.58–0.90 V/Å in vacuum, or 0.14–0.22 at ε_r = 4, which
brackets the measured value — the enzyme number and Coulomb's law agree, and the difference
is distance plus screening, both of which this model removes.

**(c) The useful field saturates while the total does not.** From S6-5 to S6-20 the charge
nearly doubles, E∥(C–O) falls from 1.214 to 1.152, E∥(C–C) rises one per cent, and the mean
over all 24 atoms climbs from 1.244 to 1.633 — while ddE improves by 6.7 kcal/mol.

For scale: the strongest field measured in any enzyme active site is 1.44 V/Å, on the bound
steroid's C=O in ketosteroid isomerase (Fried, Bagchi & Boxer, *Science* 2014, 346, 1510),
worth 7.3 kcal/mol and about 70 per cent of that enzyme's catalysis. Shaik's B3LYP critical
fields for field-induced heterolysis begin at 1.54 V/Å for Me₃C–Cl (*Chem. Soc. Rev.* 2018,
47, 5125, ESI).

**This section does not use Diagnostic 6 and is unaffected by everything in sections 6
and 7.**

---

## 5. Why n > 5 comes out STRAINED

The gap falls monotonically with Σ|q| and not with Σq²: 3.40, 3.19, 2.29, 2.13, 1.76, 0.85,
0.61 eV for n = 0, 1, 2, 3, 5, 10, 20, while Σq² is flat from n = 2 (2.000 → 2.048).

**The mechanism, from the raw file.** With a single +0.80 e at 2.96 Å the HOMO is −1.7131 eV
and the LUMO −1.2414. The bare reactant at that basis has HOMO +1.231 and a 3.573 eV gap, so
its LUMO is about +4.80. With the charge present the HOMO falls 2.94 eV and **the LUMO falls
6.05 eV** — twice as hard — and the gap closes.

That is the second-order Stark response: the low-lying virtuals have most amplitude where
the Coulomb well is deepest. It happens at def2-SVP too, with no diffuse functions, so it is
not purely a basis artefact; def2-SVPD collapses at a single charge while def2-SVP needs
more, which is the model artefact on top — a point charge with no Pauli wall for electrons.

**So the second question is answered: it is the field, not n; the narrowing is real physics
amplified by a model with no electron wall; and STRAINED reports that single-reference
closed-shell B3LYP has stopped being reliable, not that the chemistry has saturated.**

Two things qualify it. Diagnostic 6's two STRAINED criteria have no published anchor —
there is no HOMO–LUMO gap threshold in the literature for abandoning single-reference DFT,
and SCF cycle count is nowhere endorsed as a near-degeneracy diagnostic. SCF stability
analysis (RKS→UKS) and FOD at T_el = 9000 K for B3LYP are the literature-backed
replacements, both single points on geometries already committed, and neither has been run.
And Erratum 4 E4.6 establishes that **a CLEAN verdict is necessary and not sufficient**: the
Pauli wall recovers 3.09 eV of gap at identical coordinates and takes the SCF from 26 cycles
to 14, yet B1 failed on b by 32.6 per cent against a 10 per cent criterion. Gating Stage 7
on wavefunction health alone would gate it on the wrong quantity.

---

## 6. The negative result: no scalar on the charges orders the verdicts

An earlier draft of this assessment recommended **Σ|q| ≤ 3.0 e**, on three legs: the field
saturation of section 4(c), the calibration against the enzyme, and the observation that
Σ|q| ordered the def2-SVP verdicts — CLEAN to 3.000, STRAINED from 4.380.

**The third leg is gone, and it takes the number with it.**

Erratum 4 E4.5 establishes that `cs6_audit.py` opens only tarballs, so 415 completed runs in
loose `.xz` files were never classified, and that four Stage 4c runs at three point charges
are STRAINED at def2-SVP. `STAGE4C_CRITERIA.txt` defines them: E5 is "three sites by |a|,
charges opposing a, ×1", E7 is E5 reversed. The charges are confirmed without a new
measurement — the sphere positions in `L1_E5_R/combined.xyz` agree to all eight decimals
with the `Ne>` centres Erratum 4 E4.6 quotes from `L0_E5_R`, at +1, −1, +1.

| design | n | Σ\|q\| | max\|q\| | Σq² | verdict |
|---|---|---|---|---|---|
| S6-P | 1 | 1.000 | 1.00 | 1.000 | CLEAN |
| S6-2 | 2 | 2.000 | 1.00 | 2.000 | CLEAN |
| S6-3 | 3 | 2.413 | 1.00 | 2.004 | CLEAN |
| **S6-5** | 5 | **3.000** | **1.00** | 2.010 | **CLEAN** |
| **E5** | 3 | **3.000** | **1.00** | 3.000 | **STRAINED** |
| **E7** | 3 | **3.000** | **1.00** | 3.000 | **STRAINED** |
| S6-10 | 10 | 4.380 | 0.55 | 2.023 | STRAINED |
| S6-20 | 20 | 5.760 | 0.55 | 2.048 | STRAINED |

- **Σ|q| does not separate.** CLEAN reaches 3.000; STRAINED starts at 3.000.
- **max|q| runs backwards.** Every CLEAN design carries a +1.00 e charge; the two STRAINED
  Stage 6 designs top out at 0.55.
- **n does not separate.** E5 is STRAINED at three charges, S6-5 is CLEAN at five.
- **Σq² separates only inside a window of 0.013 e²**, 2.010 to 2.023. All six Stage 6
  designs were built to saturate B = 2.0 e² and cluster there by construction; six tenths of
  one per cent in Σq² cannot flip a wavefunction verdict. That is the budget showing
  through, not the physics.

**S6-5 and E5 carry the same total charge and the same largest single charge, on the same
basis, and get opposite verdicts.** They differ in how the charge is arranged, not how much
there is.

So a budget expressed as a bound on Σ|q|, max|q|, n or Σq² cannot be justified from this
evidence. **The Σ|q| ≤ 3.0 e recommendation is withdrawn.** Any such bound written into
Stage 7 must either come from somewhere other than the D6 verdicts, or be stated on its face
as unsupported by them.

The ordering that the earlier draft found was an artefact of looking only at six designs
that all saturate one budget, against a table now known to omit a fifth of the record in the
direction that matters.

---

## 7. What is left: a hypothesis, with its bracket

E5 stacks three full charges at the three strongest sites — two of them 3.429 Å apart,
closest approach to the substrate **2.581 Å**, inside the 2.85–2.96 Å that every Stage 6
design respects — while S6-5 spreads the same total over five sites. That points at a local
quantity rather than a norm.

| design | Σ\|q\| | max\|q\| | mean \|E\| | **max \|E\|** | verdict |
|---|---|---|---|---|---|
| S6-P | 1.000 | 1.00 | 0.614 | 1.644 | CLEAN |
| S6-2 | 2.000 | 1.00 | 0.815 | 1.748 | CLEAN |
| S6-3 | 2.413 | 1.00 | 0.971 | 1.835 | CLEAN |
| S6-5 | 3.000 | 1.00 | 1.244 | **2.199** | CLEAN |
| S6-10 | 4.380 | 0.55 | 1.459 | **2.315** | STRAINED |
| S6-20 | 5.760 | 0.55 | 1.633 | 2.523 | STRAINED |
| E5 / E7 | 3.000 | 1.00 | 1.649 | **2.920** | STRAINED |

Peak field at a substrate atom: CLEAN to 2.199 V/Å, STRAINED from 2.315, with E5 at 2.920 —
the highest of the eight. E5 and E7 differ only in sign, so their field magnitudes are
identical at every atom, consistent with both carrying the same verdict.

It was a real test: E5 could have landed anywhere, and it is the only candidate that
survived it. Two things make it worth testing properly. It has a measured enzyme comparator,
unlike any norm on q. And it is linear in q, so a cap would enter the MILP as 24 rows per
frame with no change to the solver.

**It is not adopted and must not be quoted as a predictor.** Seven points; two frames, so
frame is confounded with arrangement in the one comparison that carries the weight; one
basis; a bracket between 2.199 and 2.315 rather than a threshold; and a field computed in
vacuo at fixed geometry from bare point charges. Two electrostatic predictors have already
been proposed, tested and failed in this project — Erratum 3 E3.5, and Σq·V_R against the D6
table — so the prior on a third is low. It must be tested against the whole corpus after
`cs6_audit.py`'s walker and charge detection are fixed together.

---

## 8. Three passes over the judgment

**Does anything rest on a report rather than a result?** The field tables, the
proportionality test, the admitted-charge census, the bond identification, the Stage 4c
charges and the carboxylate separation are all re-derived by the attached script from
primary files. The D6 verdict on `qp0800_R` was checked against the raw output by hand. The
GOCAT constraints were read out of the thesis text directly. A quotation attributed to
Dittner §8.3 during this work did not survive a grep of the source and was discarded.

**Where could this be wrong?**

- The peak-field result rests on one cross-block comparison with frame confounded.
- Field at two bond midpoints is not the whole of the differential stabilisation of a
  pericyclic reaction, in which charge redistributes over the whole substrate. ddE keeps
  improving while the bond fields flatten, and that divergence may be legitimate.
- The field is computed at the reactant geometry; ddE is a TS-minus-R differential.
- D6's verdicts, which every ordering claim here is tested against, rest on two criteria
  with no published anchor and chosen post hoc.
- The Stage 4c block is the only one that breaks the Stage 6 designs' shared budget, so it
  carries the whole weight of section 6's negative result. If those four verdicts were
  wrong, section 6 would change. They come from Erratum 4's measurement, not from this work.

**Is the direction honest?** Section 6 removes a recommendation rather than making one, and
section 4 tightens rather than loosens. Nothing here is chosen to reach a lower barrier. The
one place this document could still be over-reaching is section 7, and it is labelled a
hypothesis throughout.

---

## 9. What is not established

- Whether any quantity orders the verdicts. Open, and needs the fixed audit.
- Whether the domain transfers to a second design. Untested; `HANDOVER` open item 5.
- Whether the STRAINED designs are genuinely near-degenerate. Needs stability analysis and
  FOD.
- Whether λ_quad = 0.25 survives a like-for-like prediction (Erratum 5, E5.5), and which of
  the two live total-field bounds stands.
- Whether S6-20 is optimal at all: it is the only design with a non-zero certified gap,
  0.55864, and the only one solved with strategy `lp` rather than `full`.
- What the designs would do in a dielectric. Burschowsky et al. (*FEBS Open Bio* 2017, 7,
  789, doi:10.1002/2211-5463.12224) compute Arg90's ΔΔG‡ at 36.6 kJ/mol at ε = 1, about 18
  at converged ε ≥ 10, against an experimental 27.2. **In this exact enzyme, vacuum
  overshoots by 35 per cent.** It belongs on Stage 7's face as a stated limitation.
- Whether a design that reaches a useful reduction inside any defensible budget exists.

---

## 10. Order of work this leaves

1. **Fix and re-run `cs6_audit.py`** — walker, charge detection, control filter, category
   overlap — as one dated change, with Erratum 4 E4.6's binding constraint: charge detection
   must be fixed in the same change as the walker, or the `Ne>` centres read as charge-free
   controls and the audit becomes more permissive rather than more complete. Section 6's
   negative result cannot be turned into a positive one against an incomplete corpus.
2. **SCF stability analysis and FOD** on the committed geometries. Erratum 4 E4.6 makes this
   more urgent, not less.
3. **Then the budget**, on a complete table and a tested predictor — or an explicit
   statement on Stage 7's face that the validity domain cannot currently be written as a
   constraint on the design.

Section 4 is the one part of this document that could be committed to a write-up today,
because it never uses Diagnostic 6.

---

## 11. Literature, and the tier each claim sits in

**Read in full and quotable after the reader checks the PDF:** Dittner's and Behrens's theses
(constraints, charge counts, the §8.3 future-work passage, the ±0.751 e colour-scale
correction confirming `OPTIMISER_DECISIONS` §1); Fried, Bagchi & Boxer *Science* 2014;
Fried & Boxer *Annu. Rev. Biochem.* 2017; Siddiqui & Dubey *PCCP* 2022; Burschowsky et al.
*FEBS Open Bio* 2017; Wilkins et al. *JCTC* 2024; Marefat Khah et al. *JCTC* 2020; Kałka,
Novotný & Stare *JCIM* 2025; the Shaik *Chem. Soc. Rev.* 2018 ESI.

**Not in `chorismate-refs/` and needed before any of this reaches the write-up:**

| paper | why | DOI |
|---|---|---|
| Siddiqui & Dubey, *PCCP* 2022, 24, 1974 | the only published field for this enzyme | 10.1039/d1cp03978d |
| Fried, Bagchi & Boxer, *Science* 2014, 346, 1510 | the measured enzyme field comparator | 10.1126/science.1259802 |
| Burschowsky et al., *FEBS Open Bio* 2017, 7, 789 | ε = 1 inflates Arg90 by 35% | 10.1002/2211-5463.12224 |
| Wilkins et al., *JCTC* 2024, 20, 451 | experimental BsCM parameters; functional spread | 10.1021/acs.jctc.3c01105 |
| Kienhöfer, Kast & Hilvert, *JACS* 2003, 125, 3206 | Arg90Cit, >10⁴-fold kcat drop | 10.1021/ja0341992 |
| Bauernschmitt & Ahlrichs, *JCP* 1996, 104, 9047 | SCF stability analysis | 10.1063/1.471637 |
| Grimme & Hansen, *Angew. Chem.* 2015, 54, 12308 | FOD | 10.1002/anie.201501887 |
| Shaik et al., *Chem. Soc. Rev.* 2018, 47, 5125 | critical fields for heterolysis | 10.1039/C8CS00354H |
| Dittner & Hartke, *JCTC* 2018, 14, 3547 | GOCAT constraints — **JCTC, not JCP** | 10.1021/acs.jctc.8b00151 |
| Dittner & Hartke, *JCP* 2020, 152, 114106 | the 2020 GOCAT paper | 10.1063/1.5142839 |
| Verlet, Horke & Chatterley, *PCCP* 2014, 16, 15043 | the dicarboxylate EB fit in the script | 10.1039/c4cp01667j |

**Secondary or unverified, not to be quoted until checked:** the dicarboxylate fit
coefficients, read from a figure caption via a summary; the attribution of
`r = 0.575, R² = 0.330` to Dittner's Fig. 7.17 — the number is in the thesis text and
Fig. 7.17 is the N_Ch = 81 sphere plot with 4070 individuals, but the extraction order does
not pin the label conclusively.

**Bibliographic correction:** the 2018 GOCAT paper is *J. Chem. Theory Comput.* 14,
3547–3564, not *J. Chem. Phys.*; the Kiel thesis authors are **Mark** Dittner (2019) and
**Dominik** Behrens (2024).

**One negative literature result worth recording**, because it is a stronger position than
inventing a number: there is no published HOMO–LUMO gap threshold for abandoning
single-reference DFT. The established diagnostics are amplitude- and occupation-based, and
Stein & Reiher's automated active-space work deliberately uses orbital entanglement entropy
rather than orbital-energy gaps.

---

## 12. Corrections to this session's own reasoning

A quotation was offered to this work as verbatim Dittner §8.3:

> "Note that such simpler solutions are already part of the search space used in this
> Thesis. However, these are not specifically favored by additional objective function
> ingredients."

**It does not exist.** The phrase "specifically favored" occurs nowhere in the extracted
thesis text, including after collapsing whitespace and ligatures. It was discarded and
nothing rests on it. Recorded because it is the same failure `HANDOVER_20261026.md` §10
already names once, and because the surrounding passage, which is real, says the opposite of
what a careless reading would take: Dittner proposes charge regularisation as future work
for parsimony and interpretability, not for surrogate validity.

Four further corrections, all of them to statements made during this work and later
overturned by evidence, are recorded in full at the end of `STAGE6_ERRATUM5_20261026.txt`:
the withdrawn Σ|q| ≤ 3.0 e recommendation; a Σq²-inertness calculation that assumed charges
may fall to zero on sites that cannot carry zero charge; describing B = 2.0 e² as simply
uncalibrated when `STAGE6_CRITERIA.txt` fixes it for two arrangements while naming it a
code-test value; and writing that the Pauli wall is untested when B1 tested it and it failed.
