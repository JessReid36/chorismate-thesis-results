# A note on how this record gets audited

**2 November 2026.** Not a result. A procedural note, written because five errors found in
this project's documents on 2 November share one cause, and the cause is a habit rather than
an arithmetic slip.

## What happened

Five corrections were issued today (`DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md`,
`RESULTS_charge_representation_domain_DRAFT_ERRATUM1_20261102.md`,
`STAGE6_RECORD_CORRECTIONS_20261102.md`). Three of them -- and three further errors made
*while checking someone else's work* -- came from the same move: a regex or a sorted glob was
run over a file, and its output was reported as a verification.

| what was asserted | how it was "checked" | what was true |
|---|---|---|
| max\|q\| = 0.6500 for S6-2_D17 | recalled from the D16 table | 0.5389, stated in words in D17 READING 3 and in the committed `pc.pc` |
| max\|q\| = 0.5000 for S6-10_D15 | the arm's lambda read as a charge | 0.2750 = 0.55 x 0.5 |
| D12: "FAIL 12, VOID 13, pass 2" | a regex requiring a four-digit site id | 20 / 13 / 3, printed by the file on the line below the table |
| D16 READING 3 margin 0.0069 | two four-decimal prints subtracted | 0.0070 from the energies |
| "the ECP block first appears in `B2_inline_svp_q0`" | the first hit of an alphabetically sorted glob, reported as "MATCH" against a claim derived the same way | `483c142`, in block form, from git history |
| "558 walled outputs" | a scan reading `job.out` only | 659; 101 outputs are committed as `job.out.xz` |

## The two rules this adds

**1. Say what the file says about itself.** DIAGNOSTIC 12 prints its own verdict counts one
line below the table a regex was run over. D17 states S6-2's charge in a full sentence. Before
reporting a quantity derived from a file, read what that file asserts about the same quantity,
and if they disagree, the file wins or the disagreement is the finding.

**2. A check by the claim's own method is not a check.** Twice today a claim was confirmed as
"MATCH" using the procedure that produced the claim's error -- an alphabetical glob in one
case, a rounded print in the other. That is worse than being wrong, because it launders
another method's error as independent agreement. Before writing that a claim is confirmed,
name the method used to confirm it and check that it is not the method under test.

These sit alongside, and do not replace, the existing rules in `WORKING_RULES.md`: guard rail
1 (compute, do not estimate -- the margin above was an arithmetic shortcut, not a lookup),
guard rail 3 (a failed search is not absence -- the compressed outputs and the ten def2-SVP
single sites were both missed by searches that were too narrow) and guard rail 6 (label every
number -- a figure read off a rounded print is not "measured").

## Scope

This note makes no claim about any result. Nothing in the project's verdicts changes because
of it. It is here so that the next audit of this record starts from a better procedure than
the last one did.
