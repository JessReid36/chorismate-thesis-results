# RESULTS_charge_representation_domain_DRAFT_20261102.md -- ERRATUM 1

**2 November 2026.** Corrects `writeup/RESULTS_charge_representation_domain_DRAFT_20261102.md`
(committed in `6e1ed18`, sha256 `17986ce0fa4806f9...`).
The draft is not edited. **Read this before building the section from that draft.**

Cause: the two max\|q\| errors recorded in
`phase2.2/cs_stage6/DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md` E1.1.

---

## E1.1  Table 4's two correlations are wrong [measured]

Recomputed from the committed `pc.pc` charges and the DIAGNOSTIC 21 / 22 stability margins:

| | bare arm | walled arm |
|---|---|---|
| range over the nine conditions | 0.00137315 - 0.05663975 | 0.04787002 - 0.05667827 |
| span, maximum over minimum | 41.2 | 1.18 |
| correlation with max\|q\|, **as published** | -0.697 | +0.024 |
| correlation with max\|q\|, **correct** | **-0.775** | **+0.338** |

The span figures, the ranges and the Sigma\|q\| correlations are unaffected.

## E1.2  The sentence built on the walled correlation is withdrawn

Withdrawn, in Section 2 immediately below Table 4:

> "The walled representation's margin lies within 15.4 per cent of the chargeless control
> for every condition and shows no dependence on per-site charge."

The first clause stands. The second does not: +0.338 is weak but it is not zero.
Replacement text:

> The walled representation's margin lies within 15.4 per cent of the chargeless control
> for every condition, and its residual dependence on per-site charge (+0.338 over nine
> points) is far weaker than the bare arm's (-0.775) and of the opposite sign. Both
> correlations are post hoc on nine points at one basis and one frame; neither is quotable
> as a finding, and the pre-registered test is a max\|q\| ladder at fixed Sigma\|q\|.

## E1.3  Section 6's fourth limit overstates the parameter dependence

Withdrawn, in Section 6:

> "a systematic error in its parameters propagates into d_shield at n >= 5 close to one for one."

The pseudopotential parameters enter the charged walled arm and the zero-charge arm, and those
two enter d_shield with opposite signs, so an error that moves both equally does not reach
d_shield at all. The factor is undetermined and lies between 0 and 1; at def2-SVP the two terms
cancel to within 0.0152 kcal/mol in every collective arm.
Replacement:

> a systematic error in its parameters enters both the charged walled arm and the zero-charge
> arm, which carry opposite signs in d_shield, so the fraction that reaches d_shield is between
> nothing and all of it and has never been measured. At def2-SVP the two terms cancel almost
> exactly; at def2-SVPD they do not, and that non-cancellation is the reported d_shield.

The sensitivity remains unmeasured, which the limit already says. See
`phase2.2/cs_stage6/DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md` E1.3 for the experiment this
rules out and the one it requires.

## E1.4  The figure specification

`[FIGURE 6.N -- bare against walled stability margin]` instructs the caption to "give both
correlations". It must give -0.775 and +0.338, and state that both are post hoc.

---

## What is not affected

Tables 1, 2, 3 and 5, the barrier figures (4.9965 to 10.6714 kcal/mol lowering, 7.6609 to
13.3357 kcal/mol barriers against the 18.3323 control), the 94.8 / 94.2 per cent retention,
the two NOT READABLE exclusions and their 0.567 / 0.880 eV gaps, and the Section 4 treatment
of d_shield all reproduce from the committed files and stand as written. The enzyme
comparator placeholder and the open section-number question are unchanged.
