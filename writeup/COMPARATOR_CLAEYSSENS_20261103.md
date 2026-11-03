# The enzyme comparator, read from the full paper: what 7.3 kcal/mol is, and what it is not

**3 November 2026.** `RESULTS_charge_representation_domain_DRAFT_20261102.md` §3 carried a
placeholder: the differential transition-state stabilisation for BsCM was quoted as 7.3 kcal/mol in
`HANDOVER_20261014.md`, attributed to the **abstract** of Claeyssens et al. (2011), never read.
ERRATUM 7 withdrew three comparator figures for exactly that reason. The full paper has now been
read end to end — Claeyssens, Ranaghan, Lawan, Macrae, Manby, Harvey and Mulholland,
*Org. Biomol. Chem.* **2011**, *9*, 1578–1590, DOI 10.1039/c0ob00691b, committed as
`chorismate-refs/c0ob00691b.pdf`. Every literature figure in this document is checked against the
extracted text of the committed PDF it is attributed to, by `cs6_y54.py` GATE 3, before this
document can be written.

**The figure is correctly transcribed from that paper, it is not the quantity our Table 5
reports, and the same group published 4.2 kcal mol⁻¹ for the same quantity six years earlier.**
The second of those is the reason this document exists; the third is the reason the comparator
cannot be a single number.

---

## 1. What the paper measures, in its own terms

The QM/MM total energy is decomposed as E(QM/MM) = E(QM) + E(MM) + E(QM–MM), and the interaction
energy of the reacting system with its environment is E(INTERACTION) = E(QM/MM) − E(QM). The paper
defines the **stabilisation energy** of a structure as E(INTERACTION) at that structure minus
E(INTERACTION) at the reactant complex of the same pathway. Differential transition-state
stabilisation is that quantity evaluated at the transition state.

| quantity, as the paper reports it | value / kcal mol⁻¹ | provenance |
|---|---|---|
| differential TS stabilisation, BsCM, averaged over 16 pathways | **7.3 ± 2.0** | measured by them, QM/MM decomposition |
| — its electrostatic (QM–MM) component | 9.9 ± 2.4 | measured by them |
| — its MM component (QM/MM van der Waals plus protein relaxation) | −2.6 ± 1.7 | measured by them |
| range over the 16 enzyme pathways | 3.2 to 11.4 | measured by them |
| differential TS stabilisation in water, 24 pathways | 1.0 (extremes +3.9 and −2.0) | measured by them |
| Arg90 electrostatic contribution | 6.0 ± 0.8 | measured by them |
| Arg7 / Glu78 | 3.1 ± 0.5 / 2.1 ± 0.3 | measured by them |
| Cys75 / Tyr108 / Arg116 / Phe57 / Arg63 | 1.3 / 1.1 / 1.0 / 0.8 / −0.6 | measured by them |
| barrier, enzyme | 11.3 ± 1.8 | measured by them, B3LYP/6-31G(d)/CHARMM27 |
| barrier, water | 17.4 ± 1.9 | measured by them |
| barrier in vacuo on the same optimised geometries, enzyme / water paths | 19.2 ± 1.3 / 18.4 ± 2.5 | measured by them |
| intrinsic barrier at zero stabilisation (intercept of the linear fit, gradient −0.95, R 0.96) | 18.3 | derived by them |
| experimental ΔH‡, enzyme / water, 25 °C | 12.7 ± 0.4 / 20.7 ± 0.4 | experimental, their ref. 24 (Kast 1996) |
| experimental catalytic effect ΔΔG‡ | 9.1 | experimental, their ref. 24 |

Conditions: B3LYP/6-31G(d) QM region of 24 atoms (substrate only) with CHARMM27, 7077-atom enzyme
model, PDB 2CHT, reaction coordinate r = difference of the breaking C2–O13 and forming C4–C14
lengths, TS taken at r = −0.5 Å and reactant at r = −1.8 Å for both environments. The paper states
that B3LYP underestimates this barrier by about 3 kcal mol⁻¹ against LCCSD(T), that ZPE lowers it
by about 1.5 and thermal energy by 0.1, and that the figures carry no continuum or sampling
correction beyond the 16 and 24 pathways averaged.

## 2. Why it is not our Table 5 quantity

Our `ddE(bare)` is **a change in a frozen barrier**: the TS-minus-reactant energy difference with
the designed point charges in the Hamiltonian, minus the same difference without them, on fixed
frame 42436 geometries in vacuo at def2-SVPD. Their 7.3 is **a difference of interaction energies**
between two geometries that were each fully optimised in the presence of the environment, and it
excludes the substrate's own energy change by construction. The two differ by every term that
geometry relaxation and the QM region's internal response contribute.

The closest quantity in the paper to ours is the barrier lowering produced by the environment on
the enzyme pathways: 19.2 in vacuo against 11.3 in the enzyme, a lowering of **7.9 kcal mol⁻¹**
(derived here by subtraction of their two reported averages, and not a figure they state). It is
not like for like, because their two numbers come from geometries optimised with the environment
present while ours are frozen.

In this system the two quantities nearly coincide, which helps rather than hurts the comparison. In
the 2005 precursor they coincide **exactly**: that paper's in vacuo barrier of 16.2 minus its
QM/MM barrier of 12.0 is 4.2, which is the differential TS stabilisation it reports. In the 2011
paper the same subtraction gives 7.9 against a reported 7.3, the 0.6 kcal mol⁻¹ residual being the
shift of the reactant reference to r = −1.8 Å and the averaging over paths. So for BsCM, "how much
the environment lowers the barrier" and "how much more the environment stabilises the TS than the
reactant" are the same number to within about half a kcal mol⁻¹. Our `ddE(bare)` is the first of
those, on a frozen geometry, with a purely electrostatic environment.

Three further mismatches, all of which must be stated wherever the comparison is made:

- **Our control is vacuum; their catalytic effect is against water.** Their enzyme-minus-water
  barrier difference of 6.1 kcal mol⁻¹ is not our comparator. Our 18.3323 control is a vacuum
  barrier, so the environment-versus-vacuum lowering is the comparable direction.
- **Our field is purely electrostatic.** Point charges carry no exchange, no van der Waals term and
  no protein relaxation. Their 7.3 is the sum of +9.9 electrostatic and −2.6 MM, so the electrostatic
  component is the part our designs could in principle reproduce, and it is larger than the total.
- **Basis, QM region and geometry source all differ**: 6-31G(d) against def2-SVPD, a 24-atom QM
  region against ours, QM/MM-relaxed geometries against one frozen frame.

Our control barrier of 18.3323 kcal mol⁻¹ sits 0.0323 kcal mol⁻¹ above their intrinsic-barrier
intercept of 18.3. **That is a coincidence and not a validation**: different basis, different QM region,
different geometry, and their 18.3 is the intercept of a fit rather than a computed barrier. It is
worth a sentence in the write-up only if it is labelled as such.

## 3. What this permits the Results section to say

Defensible, with the figures attributed and the spread shown: *QM/MM studies of BsCM by one group
report the enzyme stabilising the transition state relative to the substrate by 4.2 kcal mol⁻¹
(Claeyssens et al. 2005) and by 7.3 ± 2.0 kcal mol⁻¹ (Claeyssens et al. 2011) at the same level of
theory, the difference arising in the in vacuo arm and therefore in the starting geometries; the
electrostatic component is 4.7 and 9.9 ± 2.4 respectively. Independently, the kinetics of the
Arg90-to-citrulline variant place the contribution of that single residue at up to 5.9 kcal mol⁻¹
(Burschowsky et al. 2014). Our designed arrangements lower a frozen vacuum barrier of 18.3323
kcal mol⁻¹ by 4.9965 to 10.6714 kcal mol⁻¹, bracketing that published range — under a different
basis, a frozen geometry and a purely electrostatic field, none of which the enzyme figures assume.*

Not defensible: calling 7.3 "the enzyme's barrier lowering", comparing it to `ddE(bare)` without
the three mismatches above, presenting it as a settled community value on one paper, or quoting it
without the 2005 figure beside it.

## 3b. The figure is not stable inside the one lineage that produces it

`chorismate-refs/b508181e.pdf` is Claeyssens, Ranaghan, Manby, Harvey and Mulholland,
*Chem. Commun.* **2005**, 5068–5070, the direct precursor of the 2011 paper: same system, same
B3LYP/6-31G(d)/CHARMM27 QM/MM level, same 16 adiabatic pathways, same definition of the
stabilisation energy, same group. It reports the enzyme stabilising the TS by **4.2 kcal mol⁻¹**
more than the reactant, with an electrostatic component of 4.7, an intercept of 16.0 and an
in vacuo barrier of 16.2 ± 0.3 against a QM/MM barrier of 12.0 ± 1.7.

| quantity | 2005 ChemComm | 2011 Org Biomol Chem |
|---|---|---|
| differential TS stabilisation | **4.2** | **7.3 ± 2.0** |
| its electrostatic component | 4.7 | 9.9 ± 2.4 |
| QM/MM barrier, enzyme | 12.0 ± 1.7 | 11.3 ± 1.8 |
| in vacuo barrier on the same paths | 16.2 ± 0.3 | 19.2 ± 1.3 |
| intrinsic barrier, intercept of the fit | 16.0 | 18.3 |

The two differ by 3.1 kcal mol⁻¹ on the headline quantity, which is 74 per cent of the smaller
value. The QM/MM barriers agree to 0.7, and the 2011 paper accounts for exactly that 0.7 by the
change of starting structures — SCCDFTB/CHARMM22 molecular dynamics in 2011 against AM1 or
PM3/CHARMM22 in 2005, which alters the hydrogen-bond network around the substrate. **The whole of
the stabilisation difference sits in the in vacuo arm**, 16.2 against 19.2, so it is the strain in
the starting geometries and not the environment that moved. The 2011 paper states the 0.7 barrier
difference and does not reconcile the stabilisation figures.

Their catalytic accounting also differs while both reach the experimental 9.1: 2005 adds its 4.2 to
a reactive-conformation cost of 3.8–5 from other work; 2011 attributes about 69 per cent of 9.1 to
TS stabilisation, 26 per cent to binding the pseudo-diaxial conformer and 5 per cent to
compression. Each is internally consistent. The TS-stabilisation term itself is not stable.

**Consequence for the write-up.** The comparator is a published range of 4.2 to 7.3 kcal mol⁻¹
for one definition of one quantity by one group, with the spread set by a methodological choice in
the preparation of starting structures. Quoting 7.3 alone, with or without attribution,
over-states how well that number is known.

## 4. The independence rule, applied

One paper is not a standard, and independent means a different group, not the same lineage. For the
**number** 7.3 there is one lineage only: Claeyssens 2011, its 2005 ChemComm precursor
(`b508181e.pdf`), Ranaghan et al. 2004 (`B313759G.pdf`) and Szefczyk et al. 2004 (`ja049376t.pdf`)
are all Mulholland-group work. **The figure is single-source and must be attributed, never stated
as consensus.**

For the **claim** that CM catalysis is dominated by electrostatic TS stabilisation, the reference
library does hold independent support:

| source | group | method | what it gives |
|---|---|---|---|
| Claeyssens et al. 2011, `c0ob00691b.pdf` | Mulholland, Bristol | QM/MM, B3LYP, 16+24 paths | 7.3 ± 2.0 total; Arg90 6.0 ± 0.8 |
| Claeyssens et al. 2005, `b508181e.pdf` | the same group, same level | QM/MM, 16 paths, AM1/PM3 starting structures | 4.2 total; electrostatic 4.7 |
| Burschowsky et al. 2014 PNAS, `pnas.1408512111.pdf` | Krengel, Oslo / Hilvert, Kast, ETH | X-ray at 1.6 Å plus kinetics of the Arg90Cit variant | Arg90 contributes **up to 5.9** kcal mol⁻¹ to TS stabilisation and only 0.6 to ground-state binding |
| Senn, Kästner, Breidung and Thiel 2009, `v09-092.pdf` | Thiel, Mülheim | QM/MM free-energy perturbation and umbrella sampling | finite-temperature and entropic contributions small, about 9 kJ mol⁻¹ for BsCM |
| Hur and Bruice 2003 PNAS, `pnas.1534873100.pdf` | Bruice, Santa Barbara | NAC populations from MD | the dissenting position: catalysis from reactive-conformer selection, TS stabilisation minor |

The agreement between Claeyssens' computed Arg90 contribution of 6.0 ± 0.8 and Burschowsky's
experimental ≤ 5.9 from an Arg90-to-citrulline substitution is a genuinely independent
cross-check — different group, different method, same residue, same magnitude — and it is the
strongest single thing to cite beside our own numbers. Hur and Bruice must be cited as the
dissent, not omitted.

## 5. Provenance

Every figure above comes from one of these files, and GATE 3 found each figure in the extracted
text of the file it is attributed to. All six are committed in `chorismate-refs` at
`bd94b1651b9d59e93d21c611c8ca6169c7eb29d4`:

```
pnas.1408512111.pdf     984f3c2b447471db18b469dcee3b1fc3220da9d231eb1774eca43e450063a276  Burschowsky et al. 2014, PNAS 111, 17516
b508181e.pdf            c5ea9901016dc561a4ec1f89141b6962fa865b84a4ca1f5056e880fa9a6ad708  Claeyssens et al. 2005, Chem. Commun., 5068
c0ob00691b.pdf          891109102a82d99c33cd369db854426eafbd7a064ffc9b820997a1218818397e  Claeyssens et al. 2011, Org. Biomol. Chem. 9, 1578
pnas.1534873100.pdf     93d595dffdec5e7fcb3e448b1e2971fe1ca98bc46f1b485616fc979d20f9a4b2  Hur and Bruice 2003, PNAS 100, 12015
B313759G (1).pdf        f2fdbc4b9aa1d77c2ec5a8f8dc27956e1a60e5996c59127087708ad396b88c1e  Ranaghan et al. 2004, Org. Biomol. Chem. 2, 968
v09-092.pdf             714ef48c26a6b7fc7da837e0b61cf24d140ce745535521134a7fc32586ebeabc  Senn, Kaestner, Breidung and Thiel 2009, Can. J. Chem. 87, 1322
```

`ja049376t.pdf` (Szefczyk et al. 2004) is in the Project but not in `chorismate-refs`; no figure in
this document is attributed to it. To pin it:

```
cp <the PDF> ~/Desktop/chorismate-refs/ja049376t.pdf
cd ~/Desktop/chorismate-refs && git add ja049376t.pdf \
  && git commit -m "Add Szefczyk et al. 2004 JACS 126 16148 (chorismate mutase TS stabilisation)" \
  && git push origin master
```

## 6. What this closes and what it does not

Closed: the §3 placeholder, and `Sourcing gaps` item 2 of the draft. The figure has been read from
the full paper rather than an abstract, its definition is recorded, and the comparison in §3 now
carries the range and the caveats.

Not closed: the comparator is still one group's quantity. An independent computed value for the
total differential TS stabilisation in BsCM — a different group, not merely a different paper from
the same lineage — would be worth having, and the reference library does not contain one. What it
does contain is Burschowsky's experimental figure for the dominant residue, which is why that is
cited beside the computed ones rather than instead of them.
