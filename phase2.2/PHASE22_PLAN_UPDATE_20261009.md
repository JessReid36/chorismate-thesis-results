# Phase 2.2 plan update - 9 October 2026

Supersedes the stage order after Stage 4 in `CHARGED_SPHERE_DEVELOPMENT_APPROACH.docx` (v2) and the work-package
list in `CHARGE_MODEL_DECISIONS.md`; everything those documents fixed and this one does not change still stands.
Reviewed three times before commit: for redundancy, for coherence with the end goal and the repos, and for method.

## 1. End goal and scope

Find arrangements of partial charges on a grid on the substrate's van der Waals surface (one shell to start; more
shells possibly later) that lower the chorismate-to-prephenate barrier; take about the top 10 and test whether any
lowers it enough to count as catalytic. Mapping charges back to residues or protein backbones is out of scope.
The product is a catalytic electrostatic environment, not a protein.

## 2. Where the charge representation enters

- **Design loop (cheap).** Per site, ddE = a*q + b*q^2 + dE_LJ (approach document): a from the A matrix (in vacuo
  B3LYP-D3BJ/def2-SVP densities, TS minus reactant potential, `A_v2.tsv`); b the differential polarisation, left
  out of the current surrogate ("Tier 2", `PHASE22_PLAN.txt`: built only if it reorders the top designs); dE_LJ the
  sphere's Lennard-Jones energy at the TS minus at the reactant (Stage 5).
- **Validation of the top designs.** QM/MM at B3LYP-D3BJ/def2-SVP, spheres frozen; frozen-geometry ddE first, then
  the substrate relaxed in Cartesian coordinates and the barrier from NEB-CI to the tight thresholds (approach
  document, validation protocol). Judged against D5's references, the second of which is the enzyme at the same
  model chemistry.

## 3. Where things stand (Stages 0-4b)

The sphere is a GOCAT-style quasi-atom: one MM site with q in [-1, +1] and Amber N's LJ (Stages 0-3: ORCA
implementation verified; contact distance 2.59-2.78 A to a carboxylate oxygen at q = +1; QM/MM agrees with the rigid
model within 0.07 A; no hydroxyl-hydrogen artefact). Stage 4 and 4b (results 1382b07, exploratory 19f93a3):
- with diffuse functions (def2-SVPD) a bare positive sphere traps electron density (Laio et al. 2002; Laino et al.
  2005) at every tested distance up to 3.5 A for q >= +0.75; moving the sphere out is not a practical remedy;
- with def2-SVP the response is symmetric at every distance (compact bases confine the wavefunction: Nabo et al.
  2016), and a Ne-type pseudopotential (Marefat Khah et al. 2020) changes def2-SVP's a and b by 0.49% and 1.6%;
- the pseudopotential removes about 95% of the def2-SVPD trap at contact;
- def2-SVP's polarisation is about a quarter below def2-SVPD's (negative-side ratio 1.37-1.39, independent of
  distance), in line with def2-SVP's polarisability deficit (Rappoport & Furche 2010; Woon & Dunning 1994).
ORCA has no smeared external charges (manual checked), so the approach document's first fallback is unavailable.
Open: does def2-SVP's polarisation deficit change how much a design lowers the barrier, or which designs rank top?

## 4. Decisions taken in this update, with the path judged more likely to succeed

1. **Proposed Stage 4c arm C1 (a real Na+ as reference) is dropped.** It would matter only if validation moved to
   diffuse bases and needed the pseudopotential sphere to behave like a real ion; the end goal needs abstract
   charges, not real ions. More likely to succeed: test the design objective itself (Stage 4c below).
2. **Proposed arm C2 (convergence of b) and WP7 (b at two sites, def2-SVPD) are replaced by Stage 4c**, which
   measures the basis effect on the quantity that decides catalysis (the change in barrier) and on ranking, for the
   kinds of arrangement the design will produce.
3. **D4 (validate each +1 site with an all-atom methylguanidinium) is withdrawn; designs are validated with the
   spheres themselves.** D4 served residue fidelity, now out of scope, and WP4's methylguanidinium arm failed on
   automatically assigned torsion and improper parameters. Sphere-only validation is Behrens' one-embedding scheme
   (spheres frozen), already the approach document's protocol, and tests exactly the object designed. With it go
   WP8 (the enzyme's own arginine as a model) and the final WP2 measurement (arginine distances).
4. **D2 is relaxed**: a site is an abstract charged quasi-atom (GOCAT), not the charge centre of a named group.
   What D2 fixed that still matters - how close a site may sit - is set by the sphere's measured contact distance
   (Stage 5).
5. **WP6 (frozen versus relaxed) moves to the centre.** Prior evidence in the repo: a certified two-charge Phase 2b
   design (bare point charges), relaxed, opened the forming C1-C6 bond from 3.12 to 5.00 A, and its 1D scan barrier
   rose from 17.5 to 36.5 kcal/mol, an upper bound (`phase2b_charge_design/relaxation_attempts/ash_guarded/SWITCH_EVIDENCE.md`); WP4's free single sphere opened it
   from 3.16 to 4.27 A. Dittner & Hartke 2020 report that a fixed reaction path "allowed for only small catalytic
   effects". So a design optimised on frozen frames can lose its effect, or reverse it, on relaxation. **Judgement:**
   the plan that adds a reactant-gradient (preorganisation) term to the design objective - Dittner & Hartke 2018
   already used gradient criteria among their fitness terms - and validates relaxed is more likely to deliver
   catalytic designs than frozen-frame optimisation alone. The optimiser stage (section 5) must include it.

## 5. Remaining work, in dependency order

| Step | What | Depends on | Output used by |
|---|---|---|---|
| Stage 4c | Basis sensitivity of the design objective (below) | nothing (frame 41786 is untouched by C4/C5) | validation level; Tier 2 |
| C4 | Phase 1 audit, re-optimisations | C5 (done) | Stage 5 grid rebuild, D5 reference 2 |
| Stage 5 | Rebuild grid and A on the C4/C5 geometries; grid floor = contact distance by atom type (Stage 2); sphere spacing >= 3.25 A; dE_LJ per site | C4 | design inputs |
| Stage 6 | 2-3 spheres together, relaxed: no collapse, bonds intact, first-order additivity at fixed geometry; WP6: same arrangements frozen against relaxed, with a no-sphere relaxed control | Stage 5 | size of the relaxation problem; preorganisation term |
| Optimiser stage | Choose a transparent optimiser for: a (and b if Stage 4c shows it reorders), dE_LJ, charge bounds, spacing, a field or total-charge budget, and a reactant-gradient term; n = 3-20 charges scanned | Stages 4c, 5, 6 | designs |
| Designs and validation | Top ~10: frozen ddE, relaxed NEB-CI (def2-SVP, spheres frozen, Cartesian), Behrens/Dittner screens, the Stage 4c check level, CPCM check (D1); judged against D5 | all above | thesis result |

## 6. Stage 4c - does the basis change the barrier change? (pre-registered separately in `cs_stage4c/`)

Frame 41786's reactant and TS, fixed (the aligned geometries, identical to Stage 1's). Eight arrangements on
`grid_v2` sites, chosen by a stated rule from frame 41786's A-matrix column (not by an optimiser): the most
catalytic site at +1 and +0.5; the most anti-catalytic site at -1; the site nearest a carboxylate oxygen at +1;
three and five sites taken greedily by |a| at least 3.25 A apart with charges opposing a (1.0 and 0.5); the
three-site set with signs reversed; three of the most negative-a sites at +1 each. First-order predictions span
about -23 to +23 kcal/mol, so the set covers catalytic and anti-catalytic cases.
Levels: L1 production (QM/MM, def2-SVP, bare spheres); L0 def2-SVP with Ne-type pseudopotential spheres;
L2 def2-SVPD with them; L3 def2-TZVPD with them (Rappoport & Furche recommend def2-TZVPD for accurate routine work;
diffuse bases need the pseudopotential, Stage 4b). Compared: the QM part of ddE (LJ is identical across levels and
reported separately). Decision: if L1 keeps L3's ranking and sign, with a common scale factor near 1 and small
scatter, design and relaxed validation stay at def2-SVP and the top designs get an L3 single-point check; if the
ranking and signs hold but the magnitudes do not (scale factor or scatter), def2-SVP ranks and L3 judges
magnitudes; if the ranking does not hold, validation moves to the diffuse level (L2 if it passes against L3). L0 separates the pseudopotential's part of any L1-L3 difference from
the basis's. The same runs give first-order against full ddE for the Tier 2 question.
D5 compares a design with the enzyme at one model chemistry. If Stage 4c sends magnitudes to L3, reference 2 is
recomputed at L3 for the frames used (single points at the QM/MM geometries, with He/Ne-type pseudopotentials on
the MM atoms nearest the QM region, as Marefat Khah et al. do); that work is planned only if that branch occurs.
One frame is tested; the L3 check on every final design guards against a frame-specific verdict.

## 7. Inventory of earlier items

| Item | Status |
|---|---|
| C1 (Na+ reference), C2 (b convergence), WP7 (b at def2-SVPD) | replaced by Stage 4c |
| D4, WP4 arm c, WP8, final WP2 measurement | out of scope (residue fidelity) |
| WP3 (the bare charge's well) | superseded by the sphere |
| WP6 (frozen against relaxed) | kept: Stage 6 and validation |
| D1, D3, D5; validation protocol and restraints (approach document) | unchanged |

## Update after Stage 4c (9 October 2026)

Stage 4c's verdict is RANKING ONLY (`cs_stage4c/STAGE4C_REPORT.txt`); the evaluation is in
`cs_stage4c/exploratory/STAGE4C_EXPLORATORY.txt`, and the correction and decision rule in
`cs_stage4c/STAGE4C_AMENDMENT1.txt`. What changes in this plan:

- **Section 3, last bullet, corrected.** The "about a quarter" polarisation deficit of def2-SVP was measured on the
  total energy at one geometry (Stage 4b). In the barrier change most of it cancels: like-for-like, diffuse functions
  change the barrier change by about 6%, and make catalytic arrangements slightly less catalytic.
- **Section 6's consequences are replaced** by the decision rule in `STAGE4C_AMENDMENT1.txt`: design and relaxed
  validation at def2-SVP with bare LJ spheres; a corrected def2-SVPD single point with Ne-type pseudopotential spheres
  on every final design if the representation check passes; D5's reference 2 stays at def2-SVP unless a final design's
  verdict depends on the level. def2-TZVPD is not used further.
- **Validation protocol, added:** electronic screens at every level used (HOMO-LUMO gap; shift of substrate charges
  against the bare substrate, Hirshfeld), because the most strongly polarising arrangement (E5) changed electronic
  state with def2-TZVPD. Thresholds are fixed when validation is pre-registered.
- **Optimiser stage, added:** at def2-SVP, polarisation adds 10-31% beyond the first-order prediction for the tested
  arrangements, so the candidate pool is re-scored with full def2-SVP single points before the top designs are taken
  (the inexpensive form of the Tier 2 question in `PHASE22_PLAN.txt`). This project's own reading, not yet a decision:
  the strongest arrangements are the nearest to electronic breakdown, which adds to the case for the reactant-gradient
  term (section 4, item 5) and for a field or charge budget. Dittner & Hartke 2018 penalise gradient norms above
  10 kcal/mol/A at their E, TS and P frames so that these stay near-stationary, and the design shown in their Fig. 11
  has charges within +-0.751 e.

## Addendum (9 October 2026): enzyme reference at def2-SVPD - committed, to be done later

- D5's reference 2 will be computed at def2-SVPD as well as def2-SVP, whatever the designs show
  (`cs_stage4c/STAGE4C_AMENDMENT1_ADDENDUM1.txt`, which replaces Amendment 1's rule 4 and sets out the method). Not run now.
- Place in section 5's order: after C4, alongside Stages 5-6, and before design validation. It needs Amendment 1's
  representation check to pass and its own def2-SVP validation.
- From here on, every stage that compares a design with the enzyme reports both levels.
