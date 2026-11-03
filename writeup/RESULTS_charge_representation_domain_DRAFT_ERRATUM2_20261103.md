# RESULTS_charge_representation_domain_DRAFT_20261102.md — ERRATUM 2

**3 November 2026.** Corrects the draft after DIAGNOSTIC 23. ERRATUM 1 is not edited.
**The draft is corrected in place**, as ERRATUM 1 explains, because it is the text the thesis
section is written from; `git log -p` holds every earlier version. This erratum is the record of
what changed and why.

Six changes, all consequences of one measurement.

## E2.1  Section 6's third limit: the parameter dependence is now measured

Withdrawn:

> "A systematic error in its parameters enters both the charged walled arm and the zero-charge
> arm, and those two carry opposite signs in d_shield, so the fraction that reaches d_shield lies
> between nothing and all of it and has never been measured."

It has now been measured, and the bound is wrong. Across the two alternative published parameter
sets every reported `d_shield` moves by 0.0646 to 0.2805 kcal/mol, and the charged arm's response
does not track the zero-charge arm's: the ratio runs from **−1.28 to +10.31**, so the fraction is
neither bounded by one nor fixed in sign. See
`phase2.2/cs_stage6/STAGE6_DIAGNOSTIC23_ERRATUM1_20261103.txt`.

## E2.2  Section 6's fourth limit: a caution becomes a result

The limit said those three verdicts "should be reported as properties of this parameter set and
this basis" **until the experiment had run**. It has run and they reverse: D16 READING 1 FALLS
WITH n → NOT MONOTONIC, D16 READING 3 COOPERATIVITY FALLS → FLAT, D15 READING 1 NOT BOUNDED →
BOUNDED, with D16 READING 2 surviving at a margin of 0.0126 rather than 0.0721. The bullet now
states that, and adds that both of D16 READING 3's excesses go negative under He, so no claim of
cooperativity may rest on it.

## E2.3  Section 4's decision block is answered

`[DECISION REQUIRED — whether d_shield is reported as a primary observable or as a diagnostic]` is
replaced by the answer DIAGNOSTIC 23 provides: **a diagnostic of the representation, not a
reportable property of a design.** The draft now says the uncorrected discrepancy and the
chargeless term are reported separately, that the parameter set is named wherever a corrected
residual is quoted, and that no arrangement-comparing claim is built on that residual.

## E2.4  Section 4 gains the parameter dependence beside the basis dependence

The paragraph on the chargeless term's basis dependence now has its companion: the term moves by
−0.9608 to +0.4687 kcal/mol between published parameter sets, every reported `d_shield` moves by
37 to 42 per cent under He, and the charged arm does not track it.

## E2.5  Table 6's caption names the parameter set

Table 6 reports the Ne set. Its caption now says so, and records that every value in it moves by
37 to 42 per cent under He.

## E2.6  The ERRATUM 1 banner's parenthetical

The correction banner described ERRATUM 1's replacement claim as "the factor is undetermined
between 0 and 1". That replacement was itself measured false, so the parenthetical now points
here instead of asserting a bound.

---

## What is not affected

Every bare-arm quantity. Tables 1, 2, 3 and 5, the barrier lowerings of 4.9965 to 10.6714
kcal/mol, the frozen barriers of 7.6609 to 13.3357 against the 18.3323 control, the readability
window and its two exclusions, the per-site ceiling, and the stability verdicts. No bare arm was
run in DIAGNOSTIC 23. The correlations of ERRATUM 1 are unaffected. What moved is the shielding
metric built on top of the bare arms, and the statements drawn from comparing it across
arrangements.
