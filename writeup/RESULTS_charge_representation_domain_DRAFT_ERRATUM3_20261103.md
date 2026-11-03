# Results draft, ERRATUM 3 — the enzyme comparator, read and placed

**3 November 2026.** `RESULTS_charge_representation_domain_DRAFT_20261102.md` is corrected in place,
as its ERRATUM 1 established and ERRATUM 2 continued. This erratum records both changes with their
before and after; git holds every earlier version. **No barrier, ddE, Dset, stability margin or
readability verdict changes, and no committed result file is edited.** Two changes, both in text
that quoted no measured quantity of this project.

---

## E3.1 §3's placeholder is replaced by the comparison it was holding open

**Before** (the placeholder, as committed):

> `[PLACEHOLDER — needs sourcing: the enzyme comparator. The differential transition-state
> stabilisation for BsCM is quoted as 7.3 kcal/mol in HANDOVER_20261014.md, attributed to the
> abstract of Claeyssens et al. (2011), which is in the Project as 2011_paper.pdf. I have not read
> that abstract directly and the figure must be verified against the PDF before it is placed beside
> Table 5. ERRATUM 7 records three comparator figures withdrawn for exactly this reason.]`

**After**: a paragraph headed *How this compares with the enzyme*, giving both published values for
the quantity, the independent experimental anchor, the bracketing statement against Table 5, and a
pointer to the four caveats. The full reading is `writeup/COMPARATOR_CLAEYSSENS_20261103.md`.

**Why.** The full paper has been read — Claeyssens, Ranaghan, Lawan, Macrae, Manby, Harvey and
Mulholland, *Org. Biomol. Chem.* 2011, 9, 1578–1590, DOI 10.1039/c0ob00691b, now committed as
`chorismate-refs/c0ob00691b.pdf`. Three things follow that the placeholder could not have known:

1. **7.3 kcal/mol is correctly transcribed, and it is not a barrier change.** It is a differential
   transition-state stabilisation: the difference in QM-to-environment interaction energy between
   the transition state and the reactant complex, at geometries each optimised with the environment
   present. Our `ddE(bare)` is a change in a frozen barrier.
2. **The same group published 4.2 kcal/mol for the same quantity in 2005**, at the same QM/MM
   level, on the same system, with the same definition (`chorismate-refs/b508181e.pdf`). The two
   differ by 3.1 kcal/mol, which is 74 per cent of the smaller value. The QM/MM barriers agree to
   0.7; the whole of the discrepancy sits in the in vacuo arm, 16.2 against 19.2, so it comes from
   the semiempirical method used to prepare starting structures and not from the environment. The
   2011 paper states the 0.7 barrier difference and does not reconcile the stabilisation figures.
   **A single number was therefore never available to place here.**
3. **In this system the two quantities nearly coincide**, which is what makes the comparison usable
   at all: 2005's in vacuo 16.2 minus its QM/MM 12.0 is 4.2, exactly its stated stabilisation;
   2011's 19.2 minus 11.3 is 7.9 against its stated 7.3, the 0.6 residual being the shift of the
   reactant reference to r = −1.8 Å.

The replacement paragraph therefore quotes a range with both sources named, adds Burschowsky et
al.'s experimental ≤ 5.9 kcal/mol for Arg90 alone as the one independent anchor the library holds,
and states the four mismatches rather than burying them.

## E3.2 `Sourcing gaps` item 2 is closed

**Before:**

> 2. **The enzyme comparator.** The 7.3 kcal/mol differential transition-state stabilisation must be
>    read from `2011_paper.pdf` before it is used. Placeholdered in §3.

**After**: the item records that the paper was read in full, that the figure is a stabilisation
energy and not a barrier change, that the 2005 precursor gives 4.2, and where the full reading
lives. The gap is closed, not deferred.

## E3.3 What this erratum does not claim

- **The comparator is still single-lineage.** Claeyssens 2011, Claeyssens 2005, Ranaghan 2004 and
  Szefczyk 2004 are all Mulholland-group work. The figure is attributed wherever it appears and is
  never stated as a community value. Burschowsky et al. 2014 is an independent group but gives a
  per-residue experimental figure, not a total.
- **No measured quantity of this project is touched.** Table 5's barrier lowerings of 4.9965 to
  10.6714 kcal/mol, the 18.3323 control, the frozen barriers of 7.6609 to 13.3357 and every Dset
  stand exactly as committed. `cs6_y54.py` re-derives all of them from the committed `job.out`
  files before writing, so that is gated rather than asserted.
- **The dissent is not resolved by citing it.** Hur and Bruice's position — that catalysis comes
  from reactive-conformer selection rather than TS stabilisation — is cited in the comparator note
  as the dissent it is (`chorismate-refs/pnas.1534873100.pdf`). This project takes no side; it
  needs a comparator, not a verdict on enzyme catalysis.
- **ERRATUM 7's three withdrawn comparator figures stay withdrawn.** Nothing here reinstates them.
