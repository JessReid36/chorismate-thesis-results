# Library erratum 2 (21 October 2026)

Four things found while the Stage 6 decisions were being drafted, when every paper bearing on frozen-versus-relaxed
estimates was read in full. **No result changes.** One is a correction to a Project record; one is a distinction our
records do not draw and should; two are aids for citing the library correctly. Pre-registered files are not rewritten:
this file is the correction of record.

## 1. Rod & Ryde's "59 vs 26 kJ/mol" is not a frozen-versus-relaxed bias — CORRECTED

**What our records say.** `claude/LIBRARY_INDEX_20261014.md` (Project), the row for `ct0501102.pdf`, gives the use of
Rod & Ryde 2005 (*J. Chem. Theory Comput.* **1**, 1240-1251) as:

> QTCP; frozen-environment bias (59 vs 26 kJ/mol)

**What the paper prints.** Section 3.4, p. 1248, on COMT methyl transfer:

> "Figure 9 shows energy barriers computed in this way using the same fixed MM environments (including solvent
> molecules) for all points on the reaction pathway. Two different configurations for the MM environments are tested.
> One configuration is taken from a simulation of the reactant complex (dashed curve), and the other is taken from a
> simulation of the product complex (dotted curve). The former one gives barrier heights of 59 and 47 kJ/mol for the
> forward and reverse reaction, respectively, and the later one gives barrier heights of 26 and 96 kJ/mol."

("the later one" is the paper's own slip for "the latter one".)

**So both numbers are frozen.** They are two defensible choices of *which configuration you freeze*, not a frozen
value against a relaxed one. The sampled reference from the same paper is 56 kJ/mol forward (QTCP-U). Against that:

| treatment | forward barrier | against the sampled 56 |
|---|---|---|
| MM frozen at a reactant-complex configuration | 59 kJ/mol | +5 % |
| MM frozen at a product-complex configuration | 26 kJ/mol | −54 % |
| sampled (QTCP-U) | 56 kJ/mol | — |

The honest one-line use of this paper is therefore: *the choice of which snapshot is frozen moves the COMT forward
barrier from 26 to 59 kJ/mol, a factor of 2.3, while the sampled answer is 56* - i.e. one frozen choice is nearly
right and the other is half the barrier, and nothing in the frozen calculation tells you which you have. Quoted as
the index has it, "frozen-environment bias (59 vs 26)" would be read as a frozen-to-relaxed discrepancy, which the
paper does not report.

One internal inconsistency in the same paper, for anyone re-deriving these: the QTCP-U reverse barrier is given as
78 kJ/mol on p. 1247 and 79 kJ/mol on p. 1249.

## 2. "10 kcal mol-1 A-1" is two different quantities in the two theses — DISTINCTION ADDED

Our records quote each author correctly but never say that the same printed number means different things.

- **Dittner** penalises the gradient **norm**. Thesis printed p. 86: "a penalty as fitness ingredient if
  ||grad E_{R,TS,P}|| > 10 kcal mol-1 A-1 (usually)". Weight, thesis ESI printed p. 303: "p approximately 4200".
- **Behrens** penalises the **root-mean-squared** gradient, and prints the only closed form either thesis gives,
  Eq. 3.2, printed p. 21:

      Phi_RMSG|m = alpha (RMSG - beta)^2   for RMSG - beta > 0,  else 0

  "The alpha is usually chosen at around 250 ... The value for beta is usually chosen to be around 10 kcal/(mol.A),
  which is somewhat arbitrarily chosen to be considered 'close' to a minimum."

A norm and an RMS of the same gradient differ by the square root of the number of components. For the 24-atom
substrate of this project that is sqrt(72) = 8.49, so Dittner's threshold of 10 on the norm corresponds to about 1.2
on the RMS scale, while Behrens' threshold of 10 is 10 on the RMS scale: the same printed figure, about eight and a
half times apart in strictness. **Any threshold this project writes must name the quantity**, and neither published
value is carried over (see `cs_stage6/STAGE6_CRITERIA.txt`).

Related, and also not in our records: both authors penalise the **total** gradient, with nothing subtracted.
Dittner's Algorithm 3.1 (printed p. 87) computes the norm and compares it straight to the threshold; his converged
best design sits at "a mean of the norms of 11.3 kcal mol-1 A-1 for {E, TS, P}" (ESI printed p. 303), just above the
threshold rather than near zero; and of a COSMO transition state he writes that "in the gas phase it has a gradient
of 78.5 kcal mol-1 A-1, well beyond the allowed tolerance" (printed p. 140), which a design-minus-bare difference
would make identically zero. Behrens, printed p. 67: "all structures therefore have a large gradient norm. The
fitness function merely ensures that it is not too large." The **added**-gradient form this project uses is therefore
its own, adopted because our frames are enzyme geometries evaluated in vacuo where the bare substrate already
carries a gradient. That is already decision O2's reasoning; this erratum records that the form has no literature
precedent, which is also why neither published threshold value travels with it.

## 3. The two theses' page offsets, verified against the page footers

Both were checked directly rather than inferred, because a reading of them circulated with wrong values.

| file | paper | printed page |
|---|---|---|
| `gocat_1.pdf` | Behrens, PhD thesis, Kiel 2024 | **PDF page minus 10** (PDF 31 -> 21, 41 -> 31, 44 -> 34, 48 -> 38, 55 -> 45, 77 -> 67) |
| `gocat_2.pdf` | Dittner, PhD thesis, Kiel 2019 | **PDF page minus 24** (PDF 111 -> 87, 157 -> 133, 327 -> 303, 385 -> 361) |

Dittner's appendix carries its own ESI numbering as well: PDF 327 is printed 303 and also "S5"; PDF 385 is printed
361 and also "S63".

## 4. The 2018 paper's version-of-record pages are recoverable from Dittner's thesis

The library holds Dittner & Hartke 2018 only as the ACS **Just Accepted Manuscript** (`acs.jctc.8b00151.pdf`),
paginated "Page N of 60", so our records cite it by manuscript page. Chapter 6 of Dittner's thesis **reprints the
published article with the journal's own pagination**, which gives any passage its real page.

Worked example, the one this project cites most: the gradient-threshold sentence ("Such a quadratic penalty was also
used for all three gradients, item 5., for all ||grad E_{E,TS,P}|| > 10 kcal mol-1 A-1") is at manuscript p. 13, and
sits in the thesis at printed p. 133 = PDF p. 157, on the sheet carrying **J. Chem. Theory Comput. 2018, 14, 3551**.

For the reprint, journal page = thesis printed page + 3418 (checked at two sheets: printed 131 -> 3549, printed 133
-> 3551). The mapping from *manuscript* pages to journal pages is not linear - the manuscript is single-column and
the journal two-column - so a passage's published page is found by locating it in the reprint, not by arithmetic on
the manuscript page.

The same caution applies to three other library PDFs that are not versions of record: `acs.jctc.0c00139.pdf`
(Beker & Sokalski 2020, Just Accepted, "Page N of 47"), `acs.jctc.6b01131 (2).pdf` (Beker et al. 2017, ASAP, pages
lettered A-K) and `jacs.9b13029.pdf` (Dubey et al. 2020, Just Accepted, "Page N of 37"), plus `nihms-1716744.pdf`
(Hennefarth & Alexandrova 2022, NIH author manuscript) and `s11244-021-01486-1.pdf` (Behrens & Hartke 2021, Online
First, no printed page numbers at all - cite by section). `cphc.201402382.pdf` (Cooper & Kastner 2014) is an Early
View PDF whose footer says "These are not the final page numbers!"; its published form is *ChemPhysChem* **15**,
3264-3269. In that paper, Table 1's row labels for the minimum and the exponential average are swapped relative to
the body text; the text values are the ones to use (cis/trans: exponential average 87.5, minimum 77.1 kJ/mol).

## Checked and not changed

- Behrens' sigma = 3.55 A is a quasi-atom to quasi-atom value (his Eq. 5.6), as `LIBRARY_ERRATUM1_20261020.md`
  item 2 already records.
- Our records' citation of Behrens printed p. 67 for "the penalty is minimised by keeping charges away from the
  substrate" is correct, and citing his Eq. 3.2 by number for the threshold is correct (that equation is on printed
  p. 21).
- Sokalski 1985's four comparisons quoted in `OPTIMISER_DECISIONS_20261020.md` section 1 item 4 and decision 1 -
  H2O(A) -12.69 against -11.00, OH-(A) -50.37 against -49.67, H2O(C') +21.24 against +20.01, H2O(B) -0.59 against
  -2.20 kcal/mol - are all correct, from Table 2 on printed p. 406 (column d, his eqn. 19).
