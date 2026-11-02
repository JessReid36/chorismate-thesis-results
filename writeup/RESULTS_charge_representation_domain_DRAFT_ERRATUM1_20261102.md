# RESULTS_charge_representation_domain_DRAFT_20261102.md -- ERRATUM 1

**2 November 2026.** Four statements in
`writeup/RESULTS_charge_representation_domain_DRAFT_20261102.md` were wrong.

**The draft has been corrected in place**, because it is the text the thesis section is written
from and a reader who misses this file would otherwise build on known-false sentences. This
erratum is the record of what changed; `git log -p` on the draft holds the original. No barrier,
ddE, Dset, stability margin or readability verdict changed, and that was gated rather than
asserted: every number the draft asserts was re-derived from the raw committed `job.out` energies
at the time of the correction.

Cause: the max\|q\| column of `claude/D22_RESULT_20261102.md` was populated from memory rather
than from each bare arm's committed `pc.pc`. Raised by an independent review of
`ECP_BRIEF_20261102.md` carried out in a separate session.

---

## E1.1  Table 4's two correlations [measured]

| | as committed | corrected |
|---|---|---|
| bare arm E(0) at R vs max\|q\| | −0.697 | **-0.775** |
| walled arm E(0) at R vs max\|q\| | +0.024 | **+0.338** |

The span figures, the ranges and the Σ\|q\| correlations were unaffected. max\|q\| for the nine
conditions, read from each bare arm's own `pc.pc`:

  S6-2_D16 0.6500   S6-2_D17 0.5389   S6-3_D16 0.5389   S6-5_D16 0.4333   S6-5_D17 0.5389
  S6-10_D16 0.1632   S6-10_D15 0.2750   S6-20_D16F1 0.1241   S6-20_D16F2 0.2091

The three that the source table had wrong were S6-2_D17 (0.6500), S6-10_D15 (0.5000) and
S6-20_D16F2 (0.2090); see `phase2.2/cs_stage6/DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md` E1.1.

## E1.2  The sentence built on the walled correlation

Removed from Section 2:

> "The walled representation's margin lies within 15.4 per cent of the chargeless control for
> every condition and shows no dependence on per-site charge."

The first clause stands. The second does not: +0.338 is weak but it is not zero. The draft now
states the residual dependence with both correlations and records that both are post hoc on nine
points at one basis and one frame.

## E1.3  Section 6's fourth limit overstated the parameter dependence

Removed from Section 6:

> "a systematic error in its parameters propagates into d_shield at n >= 5 close to one for one."

The parameters enter the charged walled arm and the zero-charge arm, which carry opposite signs in
d_shield, so an error that moves both equally does not reach d_shield at all. The factor is
undetermined and lies between 0 and 1. The draft now says so, and says what would measure it.

## E1.4  The two figure captions

Both figure stubs that depend on max\|q\| now instruct that it be taken from each bare arm's
committed `pc.pc` rather than from a summary table, and the Table 4 figure's caption carries the
corrected correlations and the post-hoc qualifier.

---

## What was added at the same time, and was not an error

Four gaps the same review exposed, recorded in the draft rather than left implicit:

- Section 4 now states that the chargeless wall term is strongly basis-dependent (5 to 19 times
  larger at def2-SVPD, sign changes at two of six arrangements), and the d_shield decision block
  notes that the subtracted term moves 0.5 to 0.8 kcal/mol under a change of basis alone.
- Section 6 carries a new limit: D16 READING 1, D16 READING 3 and D15 READING 1 rest on margins of
  0.0068, 0.0070 and 0.0119 kcal/mol against a term of 0.18 to 0.72, so until the parameter
  experiment has been run those three are properties of this parameter set and this basis.
- Sourcing gap 3 records that the literature question is closed and only the 56-single-point
  measurement remains.
- A fourth inconsistency records that the "1.067 kcal/mol budget" is D12's largest voided-site
  tolerance, not a pre-registered absolute.

## Method

The corrected draft was produced by applying twelve named substitutions to the committed text,
each required to match exactly once, so no byte outside a matched span could be lost. Five gates
checked, before and after: the two files byte-identical to what the previous commit left; every
substitution unique; every withdrawn phrase absent and every replacement present; every heading,
table caption, decision block and figure stub still there, with no committed line vanishing
outside a named substitution; both correlations re-derived from the raw charges and margins; and
the control barrier plus all seven conditions' ddE and barrier re-derived from the raw energies and
still matching the draft's text.
