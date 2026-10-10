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

## Update after Stage 4c Amendment 1 (10 October 2026)

Results: `cs_stage4c/STAGE4C_AMENDMENT1_REPORT.txt` (36 zero-charge runs; thresholds unchanged). Evaluation, not
pre-registered: `cs_stage4c/exploratory/STAGE4C_AMENDMENT1_EXPLORATORY.txt`.

- **Verdicts.** Check 0 PASS. Corrected S4c verdict (L1 against L3): k 0.849, residual 1.831, rho 0.976, signs
  agree -> RANKING ONLY. Representation check (L1 against L0, corrected): k 0.990, residual 0.284, rho 1.000,
  max |diff| 0.739 kcal/mol -> PASS (uncorrected it was residual 0.996, max 1.72).
- **Decision rule applied** (`STAGE4C_AMENDMENT1.txt`; rule 4 replaced by Addendum 1):
  - rule 1: design and relaxed validation stay at def2-SVP with bare LJ spheres - unchanged;
  - rule 2 is active: every final design also gets a def2-SVPD single point with Ne-type pseudopotential spheres,
    corrected by the same spheres at zero charge, and both numbers are reported. The corrected sphere is validated
    against the bare sphere at def2-SVP only; at def2-SVPD the bare sphere cannot be run, so the check is the best
    available rather than directly validated, and is reported with that caveat;
  - rule 3 (electronic screens at every level used) - unchanged;
  - Addendum 1's condition is met: the enzyme reference at def2-SVPD can use the pseudopotential embedding. It stays
    after C4, with its own def2-SVP validation, and is reported beside the def2-SVP reference;
  - rule 5: RANKING ONLY is not FAIL, so the protocol is unchanged and the basis uncertainty is stated. For a
    design's barrier change, def2-SVP against corrected def2-SVPD: k 0.94, residual 1.1 kcal/mol, per arrangement up
    to 3.2 kcal/mol or 23%, where the electronic state does not change. The pre-registered L1-L3 comparison gives
    residual 1.8 and up to 8.0 kcal/mol, driven by E5's change of electronic state at def2-TZVPD; rule 3's screens
    are there to catch that case.
- **Correction.** In the "Update after Stage 4c" section, first bullet, "and make catalytic arrangements slightly
  less catalytic" is withdrawn. Corrected, diffuse functions change the barrier change by about 5% on average, but
  unevenly (under 1% to about 19% per arrangement), and one catalytic arrangement (E1) becomes slightly more
  catalytic. The average in that bullet and in Amendment 1's reason (iv), "about 6%", is confirmed at about 5%.
- **For the design-validation pre-registration** (to be fixed there, recorded now): designs whose def2-SVP barrier
  changes are closer than the stated basis uncertainty can swap at def2-SVPD (E3 and E2: 2.37 kcal/mol apart at
  def2-SVP, 0.59 at def2-SVPD), and an optimiser's top ~10 will be closer together than Stage 4c's eight. How such
  ties are reported is decided with the validation thresholds. Exploratory hypothesis to check on the final
  designs: arrangements with spheres at the C10 carboxylate are the most basis-sensitive.
- **Tier 2.** First order against full L1 (k 1.093, residual 3.13, rho 1.000) is as in Stage 4c; re-scoring the
  candidate pool with full def2-SVP single points stays in the optimiser stage.
- **Next** (section 5): C4.

## Addendum to the Stage 4c Amendment 1 update (10 October 2026): reporting commitments

These belong to the section above. They came out of an audit, before Stage 4d or any design, for anything in the
protocol that could let a too-favourable barrier through. A revised commit script carried them inside that section,
but the earlier version was the one run, so they are appended here unchanged.

- **Reporting commitments, made now, before any design exists.** Nothing in the design or validation may be set up
  so that it favours a lower barrier. Specifically:
  1. a design is called catalytic only if it meets the catalytic criterion at both def2-SVP and corrected def2-SVPD,
     each against D5's reference 2 at the same level (Addendum 1 computes it at both); a design that meets it at one
     level only is reported as "not established". Reason: def2-SVP overstates the lowering by about 5% on average
     and by up to 23% for one arrangement here, and the def2-SVPD check is not directly validated, so neither level
     alone may decide. This also restores the intent of Stage 4c's pre-registered RANKING ONLY consequence
     ("magnitudes are judged at L3"), which Amendment 1 replaced after the results were known; def2-SVPD stands in
     for L3, which agrees with it wherever both are well-behaved (all but E5: within 0.59 kcal/mol before the
     correction, 0.46 after);
  2. barrier changes quoted as results are total QM/MM values (QM plus the spheres' LJ). The QM-only ddE values of
     Stages 4-4c are basis-comparison quantities, not barrier changes, and are not quoted as results (at L1 the LJ
     term moves them by -4.4 to +4.3 kcal/mol);
  3. frozen-geometry values are screening numbers only; the catalytic verdict uses the relaxed NEB-CI barrier
     (WP6: section 4, item 5);
  4. a design flagged by the electronic screens (rule 3) is reported as unresolved, never as catalytic;
  5. the catalytic criterion itself is fixed in the design-validation pre-registration, before any design's barrier
     is computed.

## Update: Stage 4d, positive and negative controls (10 October 2026)

Pre-registered in `cs_stage4d/STAGE4D_CRITERIA.txt` (criteria committed before the inputs were generated; inputs
before any run).

- **Why.** The design numbers are much larger than the enzyme's. At frame 41786 one +1 sphere lowers the barrier by
  9.3 kcal/mol (with LJ) and three spheres by 32.3, while the whole enzyme stabilises the TS by 0.8 at this frame
  and by 5.0 +- 4.2 over 43 frames (Claeyssens et al. 2005: 4.2 for the same quantity). No control yet applied the
  design calculation to the real enzyme, so nothing shows whether these sizes are realistic.
- **What.** The design calculation (frozen reactant and TS of frame 41786, QM energy plus LJ) applied to known
  environments: the whole enzyme (PC1, judged against the Phase 1 ensemble's range); single charged residues alone
  and knocked out (PC2, judged on sign against Szefczyk et al. 2004); +1 spheres standing in for Arg90 and Arg7, at
  their own place and at the nearest grid site (PC3, judged on sign; the size ratios are recorded and quoted beside
  every design magnitude from then on); zero charges and reversed charges (negative controls). Reproduction checks
  against Phase 1's own single points come first and must pass.
- **Where in section 5's order.** Now, alongside C4: frame 41786 is untouched by C4 and C5. Before Stage 5, because a
  PC3 failure would send the sphere representation back for re-examination.
- **Random arrangements (the null distribution), registered now for the optimiser stage.** Before any optimiser
  design is read, the same calculation is applied to arrangements drawn at random under the optimiser's own grid,
  charge bounds, spacing and budget (Stage 5's rules, so not run now): first order for many, full def2-SVP single
  points with LJ for a subset. Every design is reported with its position in that distribution. The numbers drawn
  are fixed in the optimiser-stage pre-registration.
- **Link to reporting commitment 5.** The catalytic criterion, fixed in the design-validation pre-registration, is
  expressed against the enzyme measured with the same calculation: Stage 4d's whole-enzyme value for frozen-geometry
  screening (if PC1 passes), D5's reference 2 for the relaxed NEB-CI barrier, which alone gives the verdict.
- **Not a return to residue fidelity.** Residues appear here only as known test charges for the yardstick; designs
  are still not mapped to residues (section 4, item 3).

## Update after Stage 4d (10 October 2026)

Results: `cs_stage4d/STAGE4D_REPORT.txt`. Evaluation, not pre-registered:
`cs_stage4d/exploratory/STAGE4D_EXPLORATORY.txt`.

- **Verdicts.** Machinery checks PASS: the design calculation reproduces Phase 1's QM/MM reactant energy to 1.5e-8 Eh
  and its in vacuo energies to 1e-12 Eh. PC1 FAIL: the whole enzyme, frozen at the reactant's environment, gives
  +5.26 kcal/mol (QM part -2.00, LJ +7.26), outside [-13.3, +3.3]. PC2 FAIL: Arg90 and Lys60' agree in sign with
  Szefczyk et al. 2004, Arg7 and Arg116 do not. PC3 PASS: r90 0.71, r7 0.49, g 1.14, SUB_R90 - ENZ +2.40. NC1
  unresolved (HOMO-LUMO gap below 1.0 eV).
- **Consequences now in force** (`cs_stage4d/STAGE4D_CRITERIA.txt`):
  - PC1: frozen-geometry totals rank designs only and are never compared with an enzyme number. The failure is
    steric: a protein frozen at the reactant crowds the TS (+7.26, of which Glu78 +5.76), the effect reporting
    commitment 3 already guards against;
  - PC2: the design objective is re-examined before the optimiser stage. For Arg7 and Arg63' the disagreement is not
    specific to frame 41786: in this model's first-order field a cation beside either carboxylate raises the barrier
    in nearly every A_v2 frame, the opposite of the enzyme's arrangement and of Szefczyk et al.'s field at Arg7. The
    re-examination is Stage 4e, below;
  - PC3: the ratios are quoted beside every design magnitude. A sphere understates a real arginine at its own place
    (0.49-0.71 of it; about 0.8 at the grid's contact distance).
- **What Stage 4d establishes about realism.** With each state in its own environment the calculation gives the
  enzyme's electrostatic TS stabilisation at the published size (-4.87 kcal/mol at frame 41786; Claeyssens et al.
  2005, 4.7 on average). One sphere's effect is of the size of one real arginine (Arg90 alone -5.6 kcal/mol with LJ;
  Burschowsky et al. 2014, "up to 5.9", a free energy in water, so only qualitatively). Frozen totals are not barrier
  changes. The sign of the field beside the carboxylates is in question.
- **Stage 4e (proposed; pre-registered separately before it runs): does the field's sign beside the carboxylates
  depend on the electronic-structure method?** At frame 41786's fixed reactant and TS, the residue-alone runs (Arg90
  as the control, Arg7, Arg63', Glu78) and +1 probes at the grid sites nearest Arg7 and Arg63' are repeated at
  HF/6-31G(d) (Szefczyk et al.'s level), B3LYP/6-31G(d) (Claeyssens et al.'s), MP2 and a range-separated hybrid,
  beside the existing B3LYP-D3BJ/def2-SVP. If the sign follows the method, the level that builds the A matrix is
  chosen again before Stage 5; if it holds across methods, the disagreement with the literature is structural and the
  design proceeds at the current level with the disagreement stated.
- **Order from here (section 5):** C4 and Stage 4e side by side, then Stage 5, Stage 6, the optimiser stage (with the
  random-arrangement null) and validation. The end goal (section 1) is unchanged.

## Update: Stage 4e pre-registered (10 October 2026)

`cs_stage4e/STAGE4E_CRITERIA.txt` (criteria committed before the inputs were generated; inputs before any run).
Stage 4d's PC2 re-examination: does the sign of the barrier change beside the carboxylates follow the
electronic-structure method? Frame 41786's fixed reactant and TS; the six residues alone and +-1 probes at the grid
sites nearest Arg90's, Arg7's and Arg63''s places; at B3LYP-D3BJ/def2-SVP (production), B3LYP/6-31G(d), HF/6-31G(d),
MP2/6-31G(d) (the reference, Szefczyk et al. 2004's top level) and wB97X-D3/def2-SVP. SIGN ROBUST keeps the A matrix
at the production level; METHOD-DEPENDENT moves it to the DFT level that keeps MP2's signs (or to MP2 densities) and
marks the earlier values beside the carboxylates as level-dependent. Runs alongside C4; Stage 5 waits for its verdict.
