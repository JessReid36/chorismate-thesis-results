# Library erratum 1 (20 October 2026)

Three claims about the GOCAT papers, checked against the PDFs in the library while the optimiser decisions were being drafted. **No result changes.** Two claims are corrected; one was checked and is left as it stands. The pre-registered `phase2.2/PHASE22_PLAN.txt` is not rewritten: this file is the correction of record, and the places that carry the wrong number point here.

## 1. "±0.751 e" is a colour scale, not a charge — CORRECTED

**What our records say.**

- `phase2.2/PHASE22_PLAN.txt` (the paragraph "A CONSEQUENCE VISIBLE IN EVERY RESULT, STATED RATHER THAN HIDDEN"): "[D2018] Fig. 11 finds charges at +/-0.751, NOT saturated, because their objective is a full NEB barrier whose validity terms penalise strong fields."
- `phase2.2/PHASE22_PLAN_UPDATE_20261009.md` (the Tier 2 paragraph): "the design shown in their Fig. 11 has charges within +-0.751 e."
- Code `phase2.2/s14_design_milp.py`, docstring: the same sentence as the plan.

**What the paper prints.** Dittner & Hartke 2018 (10.1021/acs.jctc.8b00151), Fig. 11 caption, manuscript p. 35 (PDF p. 36):

> Single N_Ch = 10 GOCAT individual (PM7, neutral, COSMO): r0 (of c16) case with values given for the partial charges. Both partial charges and the atoms of the core frames (E, TS, P shown) are colored red/blue in the ranges [−0.751, +0.751] e for charges and [−84.142, +84.142] kcal mol⁻¹ e⁻¹ for ESP values.

So ±0.751 e is the range the colouring spans, not a charge the design carries.

**What that figure's charges are.** The ten labelled partial charges of Fig. 11 are, in e:

    +0.193  +0.106  +0.100  +0.090  +0.075
    −0.056  −0.080  −0.136  −0.137  −0.155

The largest magnitude is **0.193 e**.

**The same pattern in Fig. 8** (manuscript p. 30, PDF p. 31), whose caption gives the colour range as [−0.537, +0.537] e:

    +0.243  +0.230  +0.152  +0.086  +0.067  +0.059
    −0.055  −0.212  −0.277  −0.294

The largest magnitude is **0.294 e**. In both figures the colour range is wider than the charges it colours, which is why the caption numbers cannot be read as charges.

**Charge bounds.** The paper prints none in its main text. Dittner's thesis gives the usual bounds as [−1, +1] e (pp. 10 and 19).

**What does not change.** The point these records make — that their charges do not saturate at the bound, because their objective's validity terms penalise strong fields — stands. At 0.193 e it is stronger than at 0.751 e.

## 2. `HANDOFF.md` §5 B5's "−0.11 and +0.09 e" are one-charge values — CORRECTED

**What the record says.** "At the magnitudes a design uses — Dittner and Hartke report converged values near -0.11 and +0.09 e — it is about **0.01 kcal/mol**, fifty times below the resolution limit."

**Where those two numbers come from.** Section 3.1 of Dittner & Hartke 2018, "Simplest case: N_Ch = 1" (manuscript pp. 23–24; the section ends where §3.2, "More charges: N_Ch = 10", begins). They are the converged charges of **single-charge** GOCATs: about −0.11 e between the methyl C and the attacking N, and about +0.09 e near the Cl.

**What their multi-charge designs carry.** Up to 0.294 e (Fig. 8) and 0.193 e (Fig. 11), as in item 1.

**What that does to B5's estimate.** Scaling B5's own measurement (1.124 kcal/mol at unit charges, bilinear to within 8.7 % across a fourfold range) gives roughly:

| Charges | Non-additive term |
|---|---|
| −0.11 and +0.09 e (one-charge values) | about 0.01 kcal/mol |
| 0.3 e | about 0.1 kcal/mol |
| ±1 e | about 1.1 kcal/mol |

So B5's "fifty times below the resolution limit" holds only for charges of about 0.1 e, not for the magnitudes a ten-charge design may carry.

**What does not change.** Nothing in the plan rests on the estimate: the optimiser re-scores its pool with full def2-SVP single points, which contain the cross terms exactly (optimiser decisions draft, decision 1). B5's conclusion that the failure measured at unit charge does not transfer to design magnitudes is weakened, not reversed.

## 3. Behrens' σ = 3.55 Å — CHECKED, NOT CHANGED

The draft of 20 October proposed calling the Project library index's "fixed sp3-C LJ, σ = 3.55 Å" imprecise. On re-reading the thesis it is not, and no record is corrected here.

- The number is printed once, in footnote 1 to Eq. 5.6 (Behrens' thesis p. 60): "In this case, since all were equally taken to be sp3 carbon atoms, σ_i = σ_j = 3.55 Å." It is stated per quasi-atom, for quasi-atoms that are all sp³ carbons.
- Eq. 5.6 itself is the interaction **between two quasi-atoms**, and it is a quadratic repulsion, not a Lennard-Jones term.
- The quasi-atoms' term with the QM atoms is described only as "an additional LJ-12-6-potential, with parameters mimicking an sp3-hybridized carbon atom" (p. 60). No numbers are printed for it.

Therefore:

- quoting σ = 3.55 Å as the sphere's sp³-carbon σ is fair, since the footnote gives it per quasi-atom;
- `cs_stage2/STAGE2_PROTOCOL.txt`'s "Behrens' stated sigma 3.55 A (eps 0.066)" attributes only σ to Behrens and takes ε from the OPLS-AA sp³ carbon named in the same line, which is accurate;
- `cs_stage5/STAGE5_CRITERIA.txt`'s use of 3.55 Å as the analogue of the sphere–sphere spacing is what Eq. 5.6 supports.

Worth stating once, since it is easy to assume otherwise: **no published number exists for the sphere–substrate Lennard-Jones pair.** Stage 2 built that row itself from the OPLS-AA sp³ carbon.

## 4. The catalytic-field papers impose no charge budget — CHECKED, nothing to correct

Sokalski 1985 (p. 405), Szefczyk et al. 2004 (Fig. 6, p. 16155) and Beker & Sokalski 2020 give the catalytic field as a map of the effect of a **unit** charge at each point. None of them optimises charge sizes, and none imposes a budget or a normalisation. No record of ours says otherwise; it is recorded here because optimiser decision 3 (the Σq² budget) rests on there being no published budget to adopt.

## How this was checked

- The figure captions and section headings were read from the PDF text.
- The partial charges in Figs. 8 and 11 are not in the PDF's text layer. Both pages were rendered at 200 dpi and the labels read from the images.
- Section 3.1's extent was fixed by locating the headings of §3.1 and §3.2 in the text.

## Where the correction is applied

| File | What was done |
|---|---|
| `phase2.2/PHASE22_PLAN.txt` | Not rewritten (pre-registration). Corrected by this erratum. |
| `phase2.2/PHASE22_PLAN_UPDATE_20261009.md` | A dated pointer to this erratum appended. Its own sentence is left as written. |
| `HANDOFF.md` §5 B5 | A pointer to this erratum added beside the paragraph. The paragraph is left as written. |
| Code `phase2.2/s14_design_milp.py` | Docstring corrected: the number, and a pointer to this erratum. No change in behaviour. |
