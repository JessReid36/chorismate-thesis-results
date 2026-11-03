# Comparator note, ADDENDUM 1 — there are three families of figure, not one range

**3 November 2026.** `COMPARATOR_CLAEYSSENS_20261103.md` records the enzyme comparator as a
published range of 4.2 to 7.3 kcal/mol. That is a range for **one family of quantity**. The
reference library also carries figures between about 20 and 30 kcal/mol for something the same
papers call the differential transition-state stabilisation or the activation barrier lowering,
and one of them — Szefczyk et al., *J. Am. Chem. Soc.* 2004, **126**, 16148, now committed as
`chorismate-refs/ja049376t.pdf` — was already read by this project. **Nothing in the parent note
is withdrawn. It was incomplete, and this addendum states the families and which one our own
quantity belongs to.**

---

## A1.1 Szefczyk's Table 1, read from the committed PDF

The MP2/6-31G(d) column of Table 1, all thirteen residues, in kcal/mol, negative being
transition-state stabilising:

| residue | ΔMP2 | | residue | ΔMP2 |
|---|---|---|---|---|
| Arg90 | −9.06 | | XSOL116 | −0.38 |
| Arg7 | −5.90 | | Tyr108 | +0.29 |
| Glu78 | −3.57 | | Val73 | +0.68 |
| XSOL124 | −2.48 | | Phe57 | +0.85 |
| Arg116 | −2.45 | | Lys60 | +1.39 |
| Arg63 | −1.40 | | | |
| Cys75 | −0.81 | | **sum** | **−23.26** |
| SOLV7102 | −0.42 | | | |

The sum is re-derived here by adding the thirteen values and agrees with the table's own sum row
to the last digit. The paper states it as −23.3 in the text and describes it as the total
differential TS stabilisation "calculated with respect to the gas phase", from the sum of binary
interaction energies with the active-site residues considered. Its own RHF/6-31G(d) column sums to
−29.60, and the correlation coefficient between the RHF and MP2 per-complex values is 0.98.

**This project had already read that table.** `notes/phase2_dtss_literature_reconciliation.md` in
the code repository carries ten of those thirteen values and the correct total. The three it omits
are SOLV7102 (−0.42), XSOL116 (−0.38) and Val73 (+0.68), which come to −0.12 between them, so the
ten it lists sum to −23.14 rather than the −23.26 printed beneath them. Recorded here rather than
corrected there: that note is in the other repository and carries other material of its own.
**Val73 is worth having back**, because a neutral residue contributing +0.68 to the differential
is a second example of the point that note makes with Lys60.

## A1.2 Three families, and the reference frame is what separates them

| family | what it measures | published values |
|---|---|---|
| 1 | differential TS stabilisation relative to the **bound substrate**, same environment, QM/MM-relaxed geometries | 4.2 (Claeyssens 2005), 7.3 ± 2.0 (Claeyssens 2011); electrostatic parts 4.7 and 9.9 |
| 2 | barrier lowering from **in vacuo on the bound geometries** to the enzyme | 7.9 (2011, by subtracting its 11.3 from its 19.2); in 2005 this coincides exactly with family 1, since 16.2 − 12.0 = 4.2 |
| 3 | barrier lowering with respect to the **gas-phase reaction** | −23.26 (Szefczyk MP2 sum), −19.7 (Ranaghan QM/MM), −27.7 (Hall), −27 to −28 (Crespo), about −20 (Lee), −29.6 (Szefczyk RHF) |

Family 3 is large because its reference includes the substrate's reorganisation from a gas-phase
minimum, and because that reference is itself method-dependent: the gas-phase barrier is 49.0
kcal/mol at RHF/6-31G(d) and 24.8 at B3LYP/6-31G(d), against an enzyme barrier of 11.0 to 16.1.
Szefczyk's own arithmetic shows how far that can carry: the B3LYP//HF barrier plus his ΔMP2 of
−23.3 leaves 1.5 kcal/mol for the enzyme barrier, which he says must be read carefully because the
total covers thirteen residues only and omits the protein's intramolecular contribution; adding
about 6 kcal/mol for that gives 7.5.

**Our quantity is family 2.** The 18.3323 kcal/mol control is a frozen single point on frame 42436
with the charges removed, in vacuo — the same construction as the 19.2. So the designs' 4.9965 to
10.6714 kcal/mol belongs beside 7.9 and 4.2. Setting Table 5 against −27.7 would say the designs
recover about a third of what the enzyme does; that is an error of reference frame and not a
measurement, and it is the error this addendum exists to prevent.

## A1.3 What this changes

- The parent note's §4 range of 4.2 to 7.3 stands, as a family-1 range. Read it with this addendum
  beside it.
- `RESULTS_charge_representation_domain_DRAFT_20261102.md` §3 stands as written: it quotes family 1
  and the family-2 subtraction, and states the mismatches.
- Nothing is withdrawn, no measured quantity changes, and no committed result file is edited.

## A1.4 What is not claimed here

- **Szefczyk's per-residue signs are not a validation of our A matrix.** The project's own note
  marks the Arg63 comparison CORRECTED, because the placeholder geometry gave the wrong sign
  there, and says that re-running on the real transition state is what would make the agreement a
  validation. That run has not happened.
- **No single figure is "what the enzyme achieves".** The three families do not reduce to one
  number, and the quantity has to be named with its reference frame wherever it is quoted.
- The dissent stands: Hur and Bruice's position is cited in the parent note as a position, not as
  a settled matter.

## A1.5 Two things recorded rather than fixed

1. **The novelty artifacts describe a formulation that is not the committed one.**
   `notes/phase2_dtss_literature_reconciliation.md` and
   `phase2b_charge_design/GOCAT_DIFFERENTIATION_TABLE.md` describe a convex or MIQP inverse design
   over charges of −1, 0 and +1 with a separately designed neutral cradle. The committed Stage 5
   and Stage 6 optimiser is a mixed-integer **linear** program with charges continuous inside each
   site's admissible interval, a budget on Σq², and no cradle. The physics statement in those
   documents is unaffected and is correct — the objective is Dv = V_TS − V_R, the Sokalski
   catalytic field, and both documents say so — but the method description is stale, and it is
   stale in the two documents that defend the novelty of the method.
2. **`WRITEUP_INDEX.md` is stale** in the two ways the draft's Inconsistencies 1 and 2 already
   record: the theory level it states for all bare and charge work, and its canonical-barrier
   table, which does not carry the 18.3323 figure every number in the charge-representation
   section is referenced to.
