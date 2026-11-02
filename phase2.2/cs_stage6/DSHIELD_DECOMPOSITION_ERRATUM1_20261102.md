# DSHIELD_DECOMPOSITION_20261102.md -- ERRATUM 1

**2 November 2026.** Corrects `phase2.2/cs_stage6/DSHIELD_DECOMPOSITION_20261102.md`
(committed in `be16d0c`, sha256 `2cbeb5567be6580c...`).
The note itself is not edited. Three corrections, each recomputed from the committed
raw files by `cs6_y47.py` at the time this document was written; repository at `6e1ed18`.

Raised by an independent review of `ECP_BRIEF_20261102.md` carried out in a separate
session, which found E1.1 and E1.3 and prompted E1.2.

---

## E1.1  Three entries of the max|q| column are wrong [measured]

The column was populated from memory rather than from the committed point-charge files.
Read from each bare arm's own `pc.pc`:

| condition | n | max\|q\| / e | sum\|q\| / e |
|---|---|---|---|
| S6-2_D16     |  2 | 0.6500 | 1.3000 |
| S6-2_D17     |  2 | 0.5389 | 1.0777 |
| S6-3_D16     |  3 | 0.5389 | 1.3000 |
| S6-5_D16     |  5 | 0.4333 | 1.3000 |
| S6-5_D17     |  5 | 0.5389 | 1.6166 |
| S6-10_D16    | 10 | 0.1632 | 1.3000 |
| S6-10_D15    | 10 | 0.2750 | 2.1900 |
| S6-20_D16F1  | 20 | 0.1241 | 1.3000 |
| S6-20_D16F2  | 20 | 0.2091 | 2.1900 |

| condition | published | correct | cause |
|---|---|---|---|
| S6-2_D17 | 0.6500 | **0.5389** | S6-2's DIAGNOSTIC 16 value carried onto its DIAGNOSTIC 17 arm. D17 READING 3 states the difference in words: S6-2's bare arm "was STRAINED at 0.6500 e in DIAGNOSTIC 16. Here it carries 0.538860 e". |
| S6-10_D15 | 0.5000 | **0.2750** | the arm's scaling factor lambda = 0.5 used as if it were a charge; max\|q\| is 0.55 x 0.5. |
| S6-20_D16F2 | 0.2090 | **0.2091** | last digit only: 0.55 x 0.380208 = 0.209115, rounded down instead of up. |

The first two are substantive -- 21 and 82 per cent high. The third is a
single rounding digit and moves nothing.

No other entry of the column is affected, and **no other number in the note changes.**
That is measured, not asserted: every numeric cell of the note's own table was re-derived
from the raw `job.out` energies, and 32 of 35
reproduce to four decimals. The 3 that do not are exactly the max\|q\|
entries above. ddE(bare), the raw discrepancy, the chargeless term and Dset all stand as
printed for all seven conditions.

**What it moves.** The DIAGNOSTIC 22 stability correlations against max\|q\| were computed
from the wrong column:

| | published | correct |
|---|---|---|
| bare arm E(0) at R vs max\|q\| | -0.697 | **-0.775** |
| walled arm E(0) at R vs max\|q\| | +0.024 | **+0.338** |

The bare arm's dependence strengthens. The walled arm's does not stay near zero, so the
claim that the walled margin "shows no dependence on per-site charge" is withdrawn; see
`RESULTS_charge_representation_domain_DRAFT_ERRATUM1_20261102.md`. Nine points, one basis,
one frame, post hoc: +0.338 is weak and is not a finding. `D21_RESULT_20261101.md`
carried the correct -0.775 on 1 November with that caveat attached; the regression
entered with this table, not with the method.

---

## E1.2  The chargeless term is strongly basis-dependent, which the note does not record [measured]

The note says the wall-at-zero term is "a property of which positions, not of the count".
That is correct and incomplete. On identical positions and identical geometry (frame 42436),
changing only the basis moves it by more than its own magnitude:

| arms | ddE(wall0) def2-SVP | ddE(wall0) def2-SVPD | change | ratio |
|---|---|---|---|---|
| S6-20  |  -0.1116 |  -0.6190 |  -0.5074 | 5.55x |
| n2     |  -0.0937 |  -0.0652 |  +0.0286 | 0.70x |
| n3     |  -0.0933 |  -0.0117 |  +0.0816 | 0.13x |
| n4     |  -0.0765 |  +0.1003 |  +0.1768 | sign flips |
| n6neg  |  -0.0432 |  -0.8218 |  -0.7785 | 19.01x |
| n10    |  -0.1199 |  -0.7187 |  -0.5988 | 5.99x |

Single sites at def2-SVP span -0.0666 to +0.0168 over 10 arms.
The term is 5 to 19 times larger with diffuse functions present and changes sign at two
arrangements. It is a property of the positions **and** of how far the substrate's density
extends toward them. Anything that depends on its magnitude -- the D11.3-type inertness
gate above all -- is basis-specific.

---

## E1.3  The experiment the note proposes is withdrawn [design error]

The note's closing section proposes testing parameter sensitivity with "Wall-at-zero arms
only, six position sets x two states". That design cannot answer the question it is set.

Write the quantity as the project computes it:

    d_shield = ddE(bare) - ddE(wall, raw) + ddE(wall0)

The pseudopotential parameters enter **both** `ddE(wall, raw)` and `ddE(wall0)`, and those
two enter `d_shield` with opposite signs. If a parameter change moves them by the same
amount, `d_shield` does not move at all. Running the zero-charge arm alone measures that
change in `ddE(wall0)` and then assumes it reaches `d_shield` one for one -- which is the
hypothesis under test. The propagation factor is undetermined and lies between 0 and 1.

The record already shows both regimes. At def2-SVP the two terms very nearly cancel:

| arms | raw discrepancy | ddE(wall0) | d_shield |
|---|---|---|---|
| n2     |  +0.1053 |  -0.0937 |  +0.0115 |
| n3     |  +0.1059 |  -0.0933 |  +0.0126 |
| n4     |  +0.0893 |  -0.0765 |  +0.0128 |
| n6neg  |  +0.0416 |  -0.0432 |  -0.0017 |
| n10    |  +0.1352 |  -0.1199 |  +0.0152 |

so |d_shield| <= 0.0152 kcal/mol over the collectives and <= 0.0060 over the
10 single sites -- the projector acts additively there, and D14 Amendment 1 and
D15's def2-SVP reading say the same ("NO EFFECT TO LOCATE / TO BOUND"). At def2-SVPD they do
not cancel, and that non-cancellation is the thesis's d_shield.

**Replacement.** Any such experiment must run the charged walled arm as well as the
zero-charge arm, at both parameter sets, and report the per-condition factor
f = delta(d_shield) / delta(ddE(wall0)) with its sign. Nothing here is pre-registered; the
design belongs in a dated pre-registration before any run exists.
