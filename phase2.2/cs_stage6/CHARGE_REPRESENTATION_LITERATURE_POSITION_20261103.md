# Where this charge representation stands in the published literature

3 November 2026. Hand-written. Nothing computed here.

Written in response to the question of whether a smeared-Gaussian representation would be the
better-validated choice, and whether the point-charge representation is adequate. DIAGNOSTIC 24
(exploratory) is the measurement; this is the literature side.

**Citation rule.** This project's rule (CITATION_INTEGRITY_20261026.md) is that a claim must come
from the full paper in `chorismate-refs`. Each entry below is marked PRESENT or ABSENT against the
library as it stands on 3 November 2026 (79 PDFs). ABSENT does not mean the claim is wrong; it means
it is not yet verifiable under this project's rule and must not be carried into the thesis until the
paper is in the library.

> **CITATION_INTEGRITY_20261026.md is stale.** It scanned 77 PDFs and lists `10.1021/ja049376t` as
> ABSENT, cited in STAGE4D_CRITERIA.txt, STAGE4E_CRITERIA.txt and SITE_EFFECT_MAP_NOTE.md. That
> paper is now present as `chorismate-refs/ja049376t.pdf`. `cs_citecheck.py` should be re-run; at
> least one DOI will move from absent to present and the 77/69/32/37 counts will change.


## 1. The representation is not unusual. It is the published representation for this method.

**PRESENT** — `acs.jctc.8b00151.pdf`. Dittner & Hartke, *Globally Optimal Catalytic Fields - Inverse
Design of Abstract Embeddings for Maximum Reaction Rate Acceleration*, J. Chem. Theory Comput.,
DOI 10.1021/acs.jctc.8b00151 (2018).

**PRESENT** — `1.5142839.pdf`. Dittner & Hartke, *Globally optimal catalytic fields for a
Diels-Alder reaction*, J. Chem. Phys. **152**, 114106 (2020), DOI 10.1063/1.5142839.

**PRESENT** — `gocat_2.pdf`. Dittner, *Globally Optimal Catalysts: Computational Optimization Of
Abstract Catalytic Embeddings For Arbitrary Chemical Reactions* (dissertation). This is the
method's source document and the most directly relevant text in the library. Charge bounds
q_i in [-1.0, 1.0] e are confirmed in it (Fig. A.14 caption).

**PRESENT** — `ja049376t.pdf`. Szefczyk, Mulholland, Ranaghan & Sokalski, *Differential
Transition-State Stabilization in Enzyme Catalysis: Quantum Chemical Analysis of Interactions in the
Chorismate Mutase Reaction and Prediction of the Optimal Catalytic Field*, J. Am. Chem. Soc. 2004,
**126**, 16148-16159. From its abstract: "Analysis of the differential electrostatic potential of
the TS and substrate allows calculation of the catalytic field, predicting the optimal location of
charged groups to achieve maximal DTSS." That quantity is this project's `a` vector,
a = (V_TS - V_R) x 627.5094740631, computed for *Bacillus subtilis* chorismate mutase - this
project's own enzyme. The linear term of this optimiser is a 2004 JACS quantity for this system.

**PRESENT** — `acs.jctc.0c00139.pdf`. Sokalski and co-workers, *Bottom-Up Nonempirical Approach To
Reducing Search Space in Enzyme Design Guided by Catalytic Fields*, J. Chem. Theory Comput. 2020,
**16**(5), 3420. The route from an abstract catalytic field to real residues, via a rotamer library
of atomic multipoles.

**PRESENT** — `s11244-021-01486-1.pdf`. Behrens & Hartke, Topics in Catalysis 2021,
DOI 10.1007/s11244-021-01486-1. The successor that replaces abstract charges with real fragments.

**PRESENT** — `au3c00536.pdf`. Siddiqui, Stuyver, Shaik & Dubey, *Designed Local Electric Fields -
Promising Tools for Enzyme Engineering*, JACS Au (Perspective).

**ABSENT** — Hennefarth & Alexandrova, *Advances in Optimizing Enzyme Electrostatic
Preorganization*, Curr. Opin. Struct. Biol. 2022, **72**, DOI 10.1016/j.sbi.2021.06.006. The review
of this exact subfield. It annotates Dittner & Hartke at its highest level of interest and records
that their method reproduced optimal fields found independently by Shaik and Coote. Its stated
limitations of the class: the space of environments is "theoretically infinite" and solutions are not
unique; some abstract solutions are "no longer feasible within a protein"; the method "has only
worked with optimizing partial charge distributions"; and fields at discrete points "do not fully
capture a relationship to the reaction barrier". **This paper should be added to the library before
any of the above is quoted in the thesis.**

**Conclusion of section 1.** Two independent groups - Hartke in Kiel, Sokalski in Wroclaw - built
abstract bounded-point-charge catalyst models, the second of them on this project's own enzyme and
with this project's own linear quantity. The representation is a recognised and favourably reviewed
class of model. Its limitations are the class's acknowledged limitations, published as such. It is
not an idiosyncratic choice and does not need defending as one.


## 2. Smearing is not the published remedy for the def2-SVPD problem. A Pauli wall is.

**PRESENT** — `acs.jctc.9b01162.pdf` and its SI `ct9b01162_si_001.pdf`. Marefat Khah, Reinholdt,
Olsen, Kongsted & Hattig, *Avoiding Electron Spill-Out in QM/MM Calculations on Excited States with
Simple Pseudopotentials*, DOI 10.1021/acs.jctc.9b01162. Already the source of the Ne/He/Ar ecp-all
parameters used in every walled arm of the Stage 6 record (ECP_CONVENTION_20261102.md).

Three things in it bear directly on the question.

1. The cause. Standard additive embedding carries electrostatics and polarization but not the Pauli
   repulsion the environment exerts on QM electrons; without it, diffuse basis functions let the
   wavefunction extend into the environment.
2. The size. MAD falls from 0.69 eV to 0.05 eV (TDHF/aug-cc-pVDZ) and from 1.02 eV to 0.14 eV
   (ADC(2)/aug-cc-pVTZ) when minimal one-centre pseudopotentials are placed on the MM sites.
3. Smearing, explicitly ruled out. The authors list Gaussian-smeared charge densities among
   approaches that "can cure" electrostatic singularities and charge penetration, and then write:
   "**However, these methods do not capture the effects of the Pauli exchange repulsion on the
   electronic wavefunction.**"

DIAGNOSTIC 24 is a measurement of that sentence on this system: no Gaussian width tested brings any
failing cell to the D5.3(d) criterion, and at 2.8800 e the gap does not fall at all.

**ABSENT** — Kalka, Novotny & Stare, *Rescaling of Point Charges as a Way to Improve the
Simple-to-Use Electrostatic Embedding Scheme*, J. Chem. Inf. Model. 2025, **65**(16), 8653-8663,
DOI 10.1021/acs.jcim.5c01235. Already cited in STAGE6_ASSESSMENT_20261022.md and already recorded as
absent in CITATION_INTEGRITY_20261026.md. Independently reaches the same conclusion from the enzyme
side: it lists Gaussian smearing among existing approaches and does not implement it, choosing
sigmoidal distance damping instead. It reports RMSEs for uncorrected point charges from about
1.5 kcal/mol (neutral kernel) to about 7.5 kcal/mol for a Q = -3 kernel. This project's kernel is a
dianion. **Should be added to the library.**

**Note that D5 got here first.** D5.3(c), committed 26 October: "If spill-out is supported, the
def2-SVPD high-field points are not usable as physical barriers and a charge model with a Pauli wall
for electrons is needed before any high-field number means anything." D5.4: it "does not test a
charge model with a Pauli wall for electrons, which is the fix if spill-out is supported." The
pre-registration named the correct remedy before the literature was consulted, and the walled arms
of DIAGNOSTIC 23 are that remedy. Nothing in this section is new direction; it is confirmation.


## 3. The method's source document never had this problem, because it never used a diffuse basis.

Keyword census of `gocat_2.pdf` (26,154 lines of extracted text):

    "spill"     0 occurrences
    "diffuse"   0 occurrences

The GOCAT optimisations are run at **PBE0/def2-TZVP** (15 occurrences of def2, all TZVP).
Reference structures are optimised at RIMP2/aug-cc-pVDZ and aug-cc-pVTZ, but the charge
optimisation itself - the part where bare point charges sit next to a QM density - is not run in a
diffuse basis anywhere in the dissertation.

Szefczyk et al. likewise run their production DTSS at **6-31G(d)** (23 occurrences), against three
of 6-31+G(d) and two of 6-311+G(2d,p), and report TS stabilisation of about -23 kcal/mol at
MP2/6-31G(d).

**This is the most useful single fact for the write-up.** The def2-SVPD discrepancy is not a defect
the published method left unsolved. It is a condition this project created by taking the
representation beyond the basis sets its precedents used. Both precedents avoided it by construction.
That makes def2-SVP the defensible production basis, with def2-SVPD-plus-wall as the documented
sensitivity test, and it makes the Stage 4b B1 FAIL at def2-SVPD a correct diagnosis of a named
published artefact rather than a failure of the design model.

The dissertation also anticipates the remedy. Section 1.2, on what abstract entities could
represent: "vdW interactions could be modeled via simple Lennard-Jones (LJ) potentials **or by
rare-gas atoms and pseudo-potentials**". The pseudopotential route to a repulsive wall is named in
the method's own source text as an anticipated extension, and DIAGNOSTIC 23 implements it.


## 4. What the literature does NOT support

No paper found supports predicting an absolute barrier reduction from an optimised abstract charge
distribution. The accuracy standard in this subfield is ranking and search-space reduction, not
chemical accuracy on a barrier:

- Hennefarth & Alexandrova (ABSENT): fields at discrete points "do not fully capture a relationship
  to the reaction barrier"; realising abstract charge distributions in a protein "still poses a
  difficult task, since the protein sequence and fold are interdependent"; Sokalski's rotamer route
  reproduced directed-evolution mutations in KE07 only qualitatively.
- Head-Gordon and co-workers (ABSENT; Vaissier, Sharma, Schaettle, Zhang & Head-Gordon on a designed
  Kemp eliminase, and a related Nature Catalysis 2018 paper DOI 10.1038/s41929-018-0109-2 cited in
  `au3c00536.pdf`): their classical polarizable model "cannot represent charge penetration or charge
  transfer" and they suggest "a quantum description of at least part of the system" would be needed.
  Their realised gain on the Kemp eliminase is 43-fold in k_cat.
- Dittner's own dissertation, on a cluster whose barrier correlated strongly with the field along the
  reaction axis: "the GOCAT effects are thus not simply explainable by TSS induced by a field along
  this plane. Rather subtle inhomogeneities at specific other atoms for small stabilization and
  destabilization effects are present."

Consequence for the thesis framing: the optimiser is a **candidate generator and a screen**, as it is
in Sokalski's bottom-up paper, and the designs it produces are then validated by full QM/MM. It is
not a barrier predictor. Nobody's is. Framing it as a screen is not a retreat; it is the published
workflow.


## 5. Recommendation

Do not change the charge representation. The measurement says smearing does not help, the authors of
the Pauli-wall method say in print that it cannot help, and the two precedents for this
representation never needed it. Switching would cost weeks of pipeline work for no expected gain.

Instead:

1. Declare def2-SVP the production basis, citing `acs.jctc.9b01162.pdf` for why diffuse functions
   are inadmissible without a wall, and keep def2-SVPD and the DIAGNOSTIC 23 walled arms as the
   documented sensitivity test. Documentation, not computation.
2. Report the D5.3(d) domain of validity with the boundary stated correctly - between 1.3000 e and
   2.8800 e, not at or above 2.8800 e (DIAGNOSTIC 24 Reading 3).
3. Frame the LP as a screen validated by full QM/MM on the top designs.
4. Add Hennefarth & Alexandrova and Kalka et al. to `chorismate-refs`, then re-run `cs_citecheck.py`.
5. See OPTIMISER_REACTANT_TERM_FINDING_20261103.md, which is the one place where the literature
   points at something in this project's optimiser that is not yet addressed.


---

# Addendum, same day: the accuracy standard for this enzyme

Added after the sections above, following a wider literature sweep. Kept as an addendum rather than
folded in, so the order in which things were found stays visible.

**ABSENT** — Mulholland, *Chemical accuracy in QM/MM calculations on enzyme-catalysed reactions*,
Chemistry Central Journal **1**, 19 (2007), DOI 10.1186/1752-153X-1-19. Open access. Same Mulholland
as `ja049376t.pdf`. **Should be added to `chorismate-refs`; it is the most directly relevant accuracy
benchmark for this project's own enzyme and it is free to obtain.**

## A.1 What it reports for chorismate mutase

  quantity                                     value (kcal/mol)
  LCCSD(T0) dH‡, average of 16 pathways        13.3, RMS variation 1.1
  experimental dH‡                             12.7
  LCCSD(T0) dG‡                                15.6 +/- 1.1
  experimental dG‡                             15.4
  zero-point correction                        -1.5
  thermal vibrational contribution             +0.1 to +0.2
  entropic contribution                        +2.5  (experiment +2.7)

And the error attribution:

  QM method, LMP2 or B3LYP -> LCCSD(T0)        3 to 5      (the largest single term)
  basis set, tested at MP2                     < 0.5
  local approximations                         < 0.5
  QM region size, much larger region for CM    0.7
  conformational spread across pathways        1.1 RMS
  environment model                            not quantified

Stated plainly in the paper: **B3LYP often gives barriers too low by several kcal/mol**, and
semi-empirical methods can be off by 10 or more.

## A.2 Three consequences for this project

**(1) The basis-set gap this project measures is LARGER than a real basis-set effect on the barrier.**
Mulholland finds the basis set worth less than 0.5 kcal/mol on the chorismate mutase barrier at MP2.
DIAGNOSTIC 24 measures a def2-SVP/def2-SVPD discrepancy of 0.5184 at 1.3000 e and 1.0847 at
2.8800 e, rising to 13.5154 at 5.6433 e. A discrepancy at or above the size of a genuine basis-set
effect is further evidence that what def2-SVPD reports in a field of bare point charges is not basis
convergence. This is an independent line to the spill-out reading of D24.6 and to Reading 5.

**(2) Nobody expects a DFT design pipeline to be chemically accurate, so this one does not need to
be.** The field's best is under 1 kcal/mol and it costs LCCSD(T0) on sixteen sampled pathways. At
B3LYP the expected error is 3 to 5 kcal/mol before anything about the embedding is considered. The
optimiser's job is therefore to RANK, which is what Sokalski's bottom-up paper does with the same
class of quantity. Reporting a design's absolute barrier reduction as a predicted catalytic effect
would be claiming an accuracy the method does not have and that no published method of this class
claims.

**(3) Frame averaging is vindicated, with a number.** The RMS variation across 16 pathways is 1.1
kcal/mol for this enzyme. Single-structure barriers in chorismate mutase genuinely scatter by about
that much. The optimiser's mean-plus-semi-deviation over frames (O5) is therefore not
over-engineering; it is addressing a spread the literature independently measures at a size
comparable to the entire def2-SVP/def2-SVPD discrepancy at 2.8800 e.

## A.3 An estimate, NOT a result, for where the committed +16.00 sits

This is arithmetic on committed numbers plus corrections taken from Mulholland's Table. It is an
ESTIMATE and is recorded as such. It must not be quoted as a result and it is not a substitute for
computing the corrections in this project's own pipeline.

The committed barrier is +15.9995 kcal/mol (05_qmmm/18c vs 18e, verified by
checks/verify_barrier_18c_18e_18f.sh). That is an electronic potential-energy difference on a reduced
QM region: no zero-point energy, no thermal correction, no entropy. Applying Mulholland's corrections
for this enzyme as rough transfers:

  electronic barrier (committed)                  16.00
  + zero-point correction        -1.5     ->       14.5    estimated dH‡
  + thermal                      +0.15   ->       14.6
  + entropic                     +2.5    ->       17.1    estimated dG‡

against experimental dH‡ 12.7 and dG‡ 15.4. That places this project's barrier roughly 1.6 to 1.8
kcal/mol above experiment on both measures.

TWO THINGS TO NOTE. First, that is well inside the 3-to-5 kcal/mol error Mulholland attributes to
B3LYP, so the committed barrier is not anomalous. Second, and worth flagging: B3LYP is reported to
run too LOW for this reaction by 3 to 5, and this barrier estimates HIGH by about 1.7. The sign is
opposite to the canonical B3LYP error. Candidate explanations are the reduced QM region (0.7 for a
region change in Mulholland's own test, so not enough on its own), the D3BJ correction, the dianionic
QM region, and the single frame against his sixteen pathways. **This is not diagnosed and should not
be presented as agreement with experiment until it is.** It is recorded here because the comparison
had not been made anywhere in the project record, and because a reviewer will make it.

## A.4 One live dispute, for balance

The framing of catalysis as electrostatic preorganization is not uncontested in its details. Warshel
and co-workers hold that preorganization is the origin of catalytic power and have argued the concept
is frequently misread (see *Misunderstanding the preorganization concept can lead to confusions about
the origin of enzyme catalysis*, PMID 28905418, and their PNAS papers on dihydrofolate reductase and
ketosteroid isomerase). Boxer and co-workers measure fields directly by vibrational Stark effect and
correlate them with rate. Alexandrova's group continues the design side (*Electrostatics as a Guiding
Principle in Understanding and Designing Enzymes*, J. Chem. Theory Comput., DOI
10.1021/acs.jctc.3c01395). The disagreement is about decomposition and interpretation, not about
whether electrostatics dominates - and for chorismate mutase specifically, `ja049376t.pdf` puts the
DTSS at about -23 kcal/mol and sets it against pure conformational selection. The write-up should
cite the dispute rather than presenting one framing as settled.
