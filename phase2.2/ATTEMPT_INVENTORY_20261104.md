# What has already been attempted: a reference inventory

4 November 2026. Hand-written from a complete mechanical census plus a full reading of the
hand-written record. Nothing here is a new result and no committed number is changed. Its purpose
is narrow: **so that no experiment in this project is run twice, and so that the next experiment is
chosen against what the record already shows.**

Data files committed beside this one:

    ATTEMPT_INVENTORY_20261104.tsv                     1964 rows, the inventory proper
    ATTEMPT_INVENTORY_inputs_loose_20261104.tsv        3864 ORCA inputs, every keyword parsed
    ATTEMPT_INVENTORY_inputs_archived_20261104.tsv     2219 inputs read out of the .xz archives
    ATTEMPT_INVENTORY_outputs_loose_20261104.tsv       1969 loose outputs, status and energies
    ATTEMPT_INVENTORY_outputs_archived_20261104.tsv    3497 outputs read out of the archives
    parse_inp.py  parse_out2.py  parse_archives.py     the three parsers, re-runnable

The TSV is the thing to query. Columns: theme, attempt, parameters, where, outcome, status,
evidence (path:line), source_partition. Grep it before proposing anything.


## 0  HOW THIS WAS BUILT, AND WHAT THAT IS WORTH

TWO LAYERS, and they are not equally reliable.

The MECHANICAL LAYER is exhaustive and exact. Every ORCA input and output in all three work
repositories was parsed by script, including the 2219 inputs and 3497 outputs that exist only
inside 942 compressed archives and are invisible to anyone reading the directory tree:

    ORCA inputs parsed          6083      3864 loose + 2219 archived
    ORCA outputs parsed         4986      1489 loose ORCA logs + 3497 archived
    archives opened              942      134 tarballs (15103 members) + 808 single .xz
    hand-written records        1835      1 784 609 words, 32.8 MB of text

The READING LAYER is seven parallel readings of all 1835 records, partitioned by area, each
returning a structured TSV. Every claim relayed into the sections below was then opened and
verified against the file by hand before it was written here. 16 rows of the 1965 returned had a
field misalignment and were repaired; one row was dropped as stale (see 0.2). The rest are as the
readers wrote them and are NOT individually verified - the TSV is a finding aid, and a row should
be read at its cited path before it is relied on.

### 0.1  A defect in how this was produced, recorded because it matters

The census was begun against a clone of chorismate-thesis-results that was EIGHT COMMITS BEHIND
origin/main, at cbd9331 rather than df1fbd4. The repositories were brought current mid-exercise.
Consequences, both handled:

  - One reader reported ts_frequencies_summary.txt as still carrying the starting-Hessian values
    -313.30 / -18.65 and a +15.08 barrier. That was true of the stale clone only; commit 12f32b4
    corrected the file and retained the superseded values for provenance. That row is dropped.
  - Three documents dated 3 November were absent from the stale tree and were read separately and
    directly: STAGE6_AMENDMENT4_20261103.txt, STAGE6_LOSS_SIGN_FINDING_20261103.txt and
    STAGE6_RELAX_TS_NOTE1_ENTRY2_20261103.txt. They are covered in sections 4 and 8.

Anything committed after df1fbd4 is outside this inventory.

### 0.2  The shape of what was found

    theme                   settled   failed  abandoned  superseded  withdrawn   open   total
    additivity                   55        6          0           5          5      2      73
    basis_set                    66        6          3           6          9     12     102
    charge_representation       190       19          9           8         28     31     285
    frames                       71        3          2           6         11     23     116
    grid                         47        1          7          11          3      2      71
    numerics                     94       11          2           2         18      6     133
    optimiser                    78        7         11          17          9     19     141
    other                       273       10         19          14         65     73     454
    pauli_wall_ecp              144       15          2           5          9     12     187
    relaxation                   59       18          6           8          6     12     109
    solvation                    37        0          1           4          2     11      55
    validation                  161        6          2          18         26     25     238
    ALL                        1275      102         64         104        191    228    1964

191 withdrawn and 104 superseded entries is the most useful number in the table. Roughly one entry
in seven records something that was done and then taken back.


## 1  THE COMPLETE SET OF METHODS AND SETTINGS EVER RUN

From the mechanical census. These are counts of INPUTS, so they measure how much was set up, not
how much was concluded.

### 1.1  Basis sets - six, and only six

    def2-SVP        3404      production throughout
    def2-SVPD        814      the diffuse arm of every basis test
    ma-def2-SVP      500      minimally augmented; D1's and D11's comparator
    6-31G(d)         102      comparator work
    def2-TZVPD        30      cs_stage4c ONLY (see 1.2)
    (none in !)     1233      geometry-only, vpot, FOD and MD inputs

**Plain def2-TZVP has never been run on this system.** Its twelve appearances in the record are all
ORCA's !FOD default (TPSS/def2-TZVP) inside DIAGNOSTIC 19, which states that basis "is neither of
the two production bases". The VALENCE axis of basis improvement is untested; every basis test in
the record moves along the DIFFUSE axis.

### 1.2  def2-TZVPD was run, in cs_stage4c, and the record does not lean on it

30 inputs: bare_tzvpd_R/TS, Z_L3_S1/S3/S4/S5/S6/S8 and L3_E1-E8, each R and TS, all at
`B3LYP D3BJ def2-TZVPD def2/J RIJCOSX TightSCF`. This matters because D5.4 says the record "does
not test def2-TZVPD". That is true of D5; it is not true of the project. Anyone proposing a
diffuse triple-zeta test should read cs_stage4c first.

### 1.3  Functionals and methods - nine

    B3LYP              4748     production
    r2SCAN-3c           144     ARCHIVE ONLY (s10_benchmark, 05b_optimise_realism)
    HF-3c               144     ARCHIVE ONLY
    B97-3c              140     ARCHIVE ONLY
    GFN2-xTB             --     s10_benchmark, as xtb2
    HF                   34
    wB97X-D3             34
    MP2                  34
    (none)              805

The three composite methods and xTB exist only inside archives. See section 6.

### 1.4  Pauli walls and ECPs - five elements

    Ne     663 inputs    the workhorse wall, Marefat Khah ecp-all
    He      24 inputs    DIAGNOSTIC 23's alternative; VALIDATED to 1.381e-06 Eh
    Ar      24 inputs    DIAGNOSTIC 23's alternative; NOT VALIDATED, r0 residual 3.067e-03 Eh
    Na      11 inputs    ARCHIVE ONLY, phase2_charge_design/09_mmtest
    Mg       1 input     ARCHIVE ONLY, same place

### 1.5  Solvation - three dielectrics, then removed

    in vacuo                   the production condition from 27 October
    CPCM epsilon 4.0    734    127 loose + 607 archived; 51 with KeepDens
    CPCM epsilon 78.4     4    ARCHIVE ONLY, 02_singlepoints/refstate_diagnostic

AMENDMENT 2 (27 October) removed CPCM from Stage 6's evaluation condition: "No continuum appears
alongside designed charges again without a further amendment."

### 1.6  Job types, coordinates and paths

    MD (restrained LBFGS windows)    922     the frame ensemble
    EnGrad                           397
    Opt                              324
    NumFreq                          162
    Scan                             144     ARCHIVE ONLY
    NEB-CI                            75
    NEB-TS                            69
    OptTS                             55 + 17 with NumFreq + 8 with Freq
    IRC                               43
    coordsys cartesian               223     19 loose + 204 archived
    ProjectTR false                   19
    NEB NImages 8                    143
    NEB NImages 16                     1     abandoned mid-run, see 7.3

### 1.7  Charge and multiplicity

    -2 / 1    4248    the chorismate dianion, production
     0 / 2     486    ARCHIVE ONLY
     0 / 1     187    ARCHIVE ONLY
    -1 / 2      11    VDE probes
    -1 / 1       9

### 1.8  Run health, over the 1489 loose ORCA logs

    terminated normally               1480
    did NOT terminate normally           9     all nine identified in section 7
    frequency runs with imaginary modes   2     both ts_reduced.out, ONE mode (-313.07) in the
                                               final block, THREE across the whole file

That last line is the project's reading rule, reproduced mechanically: counting imaginary modes
across a whole output gives three; counting after the last OPTIMIZATION RUN DONE gives one.


## 2  DO NOT RE-PROPOSE: THINGS THE RECORD HAS CLOSED

Each line is a thing that has been tried or examined and found not to work. The evidence is in the
TSV at the cited path.

### 2.1  Five scalars on the charge vector, all failed

DIAGNOSTIC9_RESULT.txt:482, verbatim:

      "Peak local field joins sum|q|, max|q|, n and sum q^2. No scalar on the charge vector
       proposed so far survives contact with the corrected corpus."

So: **sum|q|, max|q|, n, sum q^2, peak local field** - all five tested, all five failed. A sixth
scalar needs a reason why it differs in kind from these.

`sum q*V_R` (FINDING 9) is a SIXTH PROPOSAL, NOT A SURVIVOR. It correlates with the HOMO at
r = +0.982, but on seven designs at one frame, and Finding 9 itself says it is "offered as a reason
to build the term and measure it properly, not as a calibration". It has never been tested as a
screen.

### 2.2  Geometry cannot screen the artefact

DIAGNOSTIC12_RESULT.txt:146-153, verbatim, after 282 runs over 36 sites and five descriptors with
rho from +0.056 to +0.786:

      "NO DESCRIPTOR IS ADEQUATE.
       Geometry does not predict the artefact. No screen can be built from the quantities a grid
       has. Every candidate site would need its own QM check, which the grid-and-budget
       formulation cannot absorb. The charge model must change - not the spacing, and not the
       surface. Moving the grid outward does not help, because what fails is the prediction, not
       the distance."

This closes, together: a distance floor, a per-atom floor table (abandoned before any input was
written), and **moving the admitted surface outward**, which is route (a) of DIAGNOSTIC 11
ERRATUM 1 E11.3.

### 2.3  A single charge cap cannot screen it either

DIAGNOSTIC13_RESULT.txt: at |q| = 1.00, **0 of 6 live sites pass**; at 0.50 and at 0.25, 3 of 6.
Fitted exponents 0.61 to 4.49, mean 2.47. Verdict PARTIAL: "The magnitude dependence is real but
site-specific. A single cap cannot be stated from this sample; the screen would have to be
per-site, which the grid cannot carry." And its own limitation: the ARTEFACT's additivity has never
been measured at any n, so "Nothing here supports a claim that weak charges are safe in a
many-charge design."

### 2.4  Smeared Gaussian charges do not help

DIAGNOSTIC 24 (exploratory), 12 cells, 4 PASS / 8 FAIL against D5.3(d). Best reduction 18.8 per
cent at the out-of-domain vector; at 2.8800 e the gap does not fall at all. The authors of the ECP
method say in print that smearing "do[es] not capture the effects of the Pauli exchange repulsion
on the electronic wavefunction" (acs.jctc.9b01162).

### 2.5  A continuum is not a repair for the basis problem

DIAGNOSTIC 10: NOT RECOVERED. S6-20 goes from the committed def2-SVP -24.8261 to **+20.6967** at
CPCM, a 183.4 per cent move with the sign REVERSED, even though the density is bound at CPCM.
Separately, ORCA builds the cavity on the 24 QM atoms alone, so the designed charges sat 1.0-1.7 A
OUTSIDE it.

### 2.6  Relaxation with bare point charges, in the earlier generation

07_stage0: native `%pointcharges` + `%geom Opt` endpoint relaxation, 8 jobs, **0 of 8 converged**
at the 72-cycle cap, 6 of 8 imploded to 0.01-1.06 A atom-to-charge, K4_product diverged at MAX
grad ~4767. Stage 1's fix (`Calc_Hess true` + `Recalc_Hess 5`) also returned 0 of 8 at ~4.5 h per
job. A single fixed-pair pin relocates the implosion (O5 at 0.955 A); a soft global floor at 2.2 A
with k = 100 kcal/mol/A^2 is penetrated to ~1.26 A. Looser tolerances were ruled out.

### 2.7  The preorganisation objective is falsified, not under-tuned

STEP3_RESULT_apot.md:12-14: "FALSIFIED a_pot as the preorganisation coordinate. The certified
optimiser drove Sum q*a_pot -> ~0 (D=0.0006, gap 0.000), yet the substrate STILL relaxed C1-C6 open
to 5.28 A." a_force reaches only 4.060 A with D driven to 4.6e-6 at mu=5000. More charges do not
recover it: K10_apot fragments 20 of 24 atoms; K6_aforce ruptures the ether at O3-C4 6.004 A.

### 2.8  Uniform shells and neutral caging

05d_shell_ladder, 30 designs from 2 to 15 A: close shells fragment, far shells open past the bare
baseline. Clean NEB bands give **+37.9 to +77.7 kcal/mol against a bare +17.47** - "the charges are
anti-catalytic" - and "None drops below bare in its clean set". Uncharged surrogate bodies are
sterically inert (C1-C6 3.367 A vs bare), so the field is doing it, not the bodies. The 6-bead
neutral steric cage left K2aforce MORE open (5.306 vs 4.06).

### 2.9  Other closed items

  - **The endpoint-difference barrier (protocol B2) is invalid under a fixed field**; the +35.51 at
    8 A is not reportable, and the ~32-job all-layer scan is superseded by NEB-under-field.
  - **CBC is not usable for certificates**: on the real field at tmax 600 s its K=7 incumbent
    (0.80) is both uncertified and worse than HiGHS (0.77), which certifies >167x faster.
  - **The point-sized min_dist 2.5 A no-overlap constraint** was superseded twice, 2.5 -> 3.7 ->
    4.7 A surrogate-body-sized; designs at 2.5-2.74 A centres clashed to 0.33 A atom-to-atom.
  - **r2SCAN-3c fails the geometry calibration gate**: mean |delta C1-C6| 1.086 A, max 1.618 A.
  - **The Na+/K+ substitution as specified** (DIAGNOSTIC 3) is withdrawn - its ghost control failed
    at 0.9461 vs a 0.30 limit, and its "Pauli repulsion is a small effect" conclusion went with it.
  - **Whole-region TS search cannot converge**: step 18 ran 87 cycles in 7 days, killed at the
    168 h walltime, gradient never below 1.1e-3 against 3e-4, substrate drifted to the product side
    at C-C 1.76 A. Step 18b's exact-part hybrid Hessian over 1959 atoms was killed for memory
    (221 GB requested against a 125 GB limit). Whole-region OptTS fails at both radii.
  - **DO NOT RETRY the K2 NEB with more iterations** - and Knarr `knarr_MEP_FULL.xyz` comment-line
    energies are corrupt (interior ~-1.3e7 kcal/mol), which is the project's standing reading rule.


## 3  THE REPRESENTATION PROBLEM, WHICH IS ONE PROBLEM

Reading sections 2.2 to 2.8 together, every failure has the same shape. A bare point charge has no
Pauli repulsion, so:

  - held close, it distorts the density      -> r_safe = 3.50 A, d_shield, def2-SVPD spill-out,
                                                SCF instability from lambda 0.75
  - allowed to move, it collapses onto it    -> 0 of 8 relaxations, implosion to 0.01-1.06 A
  - smeared over 1 A, nothing changes        -> D24, because smearing adds no repulsion
  - given an ECP wall, the wall is not inert -> 13 of 36 sites voided in D12, 2 of 8 in D13

THIS IS AN INTERPRETATION, not a quoted verdict, and it is recorded as such. It is offered because
it predicts the pattern across five independent diagnostics and two generations of the project.

### 3.1  The state of the four charge models

    bare point charges at 2.85-2.96 A    INVALIDATED    D11 r_safe = 3.50 A; D13 0 of 6 at |q|=1
    surface moved out to >= 3.50 A       CLOSED         D12, "moving the grid outward does not help"
    ECP Pauli wall at those distances    UNCALIBRATED   never adopted by amendment; inertness
                                                        control fails at close range; Ne used
                                                        outside its published octet assumption
                                                        (ERRATUM7); Ar NOT VALIDATED; Stage 4b B1
                                                        FAILED with b 32.6% apart vs a 10% criterion;
                                                        D20 "WALL DOES NOT CHANGE STABILITY"
    Gaussian smearing                    CLOSED         D24, and ruled out in print

### 3.2  What the record says is required, and what has never been tried

D11 ERRATUM 1 E11.3 sets out two routes and adopts neither. Route (a) is closed by D12 (2.2).
Route (b) - "change the charge model to one that has Pauli repulsion" - "requires its own dated
amendment, and it requires the wall to be calibrated first". **No amendment adopts it.** Amendment 1
is the A matrix, Amendment 2 removes CPCM, Amendment 3 adds one arrangement to the relaxation list,
Amendment 4 is the TS-side coordinates and Hessian.

E11.3 also records what r_safe is NOT: "r_safe = 3.50 A BOUNDS THE VALIDITY OF A MODEL. IT IS NOT A
STATEMENT ABOUT WHERE A CATALYTIC CHARGE MAY SIT." Arg90's guanidinium carbon sits 3.19 A from the
substrate at the reactant and 3.27 A at the TS in this project's own frame 42436 - inside r_safe -
"and it is the catalytic residue Burschowsky's crystallography identifies. A real guanidinium has
electrons and Pauli repulsion; a bare point charge has neither. What fails at 2.96 A is the
representation, not the chemistry."

CHARGE MODELS WITH PUBLISHED PRECEDENT THAT THIS PROJECT HAS NEVER ATTEMPTED - listed as options,
not recommendations, and none of them is free:

    polarizable density embedding              Olsen/Kongsted; replaces points with a density
    sigmoidal distance damping of the charges  Kalka, Novotny & Stare 2025, doi 10.1021/acs.jcim.5c01235
    a real molecular fragment in place of an   Behrens & Hartke, Topics in Catalysis 2021,
      abstract site                              doi 10.1007/s11244-021-01486-1 - the successor to
                                                 the very method this project descends from
    Sokalski's atomic-multipole rotamer route   doi 10.1021/acs.jctc.0c00139, the published path
                                                 from an abstract field to real residues

The last two change what a "site" is rather than how it is screened, which is the only axis
sections 2.1 to 2.4 have not already closed.

### 3.3  The charged-sphere representation is not implemented

writeup/X2_final.md records three items that read as done and are not:

    line 208   "[DECISION REQUIRED - the Lennard-Jones radius sigma for the charged sphere"
    line 285   "[PLACEHOLDER - needs sourcing: no committed input file yet implements the ..."
    line 341   "The Lennard-Jones radius sigma. Undetermined"

So the representation the write-up describes has no committed input file and an undetermined sigma.


## 4  THE RELAXATION, WHICH IS NOW UNBLOCKED

AMENDMENT 4 (3 November) decides the TS side. ORCA 6.0.1 refuses OptTS with `coordsys cartesian` at
input parsing, and refuses Hybrid_Hess on the analytical path; both refusals are quoted verbatim in
the amendment from jobs 423856 and 423860. The replacement, read off converged runs of this project
rather than invented:

      ! B3LYP D3BJ def2-SVP def2/J RIJCOSX TightSCF [QMMM] OptTS NumFreq
      %geom
        MaxIter 1000
        Calc_Hess true
        Hybrid_Hess {the 24 substrate atoms} end
      end

"NumFreq is the whole difference between a refusal and a converged transition state in this
project's own files." The reactant side is untouched and keeps Cartesians. Redundant internals is
also the cheaper route on WP4's own three arms: **185 cycles against 630**, a factor of 3.41.

`relax/S6-C/TS_opt2` and `relax/n10_A/TS_opt2` were submitted on 3 November and are governed by it.

**Do not re-derive the OptTS/cartesian refusal, and do not re-propose Cartesians for the TS side.**

### 4.1  But Stage 6's tolerance cannot fail as written

STAGE6_LOSS_SIGN_FINDING_20261103.txt: STAGE6_CRITERIA.txt line 109's formula is
`Loss = ddE(frozen) - ddE(relaxed)`, while line 109's own clause - the design's change with the
control's subtracted - evaluates to `ddE(relaxed) - ddE(frozen)`, which is IDENTICALLY its negative
for any eight energies. Only one can be what line 139's "Loss must be below 15 % of |ddE(frozen)|"
tests. The finding proposes no correction: it is an amendment and it is Jessica's to make.

A relaxation that runs is not the same thing as a tolerance that can fail.


## 5  WHAT MAY NOT BE QUOTED

A standing list, assembled from the record's own do-not-quote entries. Any of these resurfacing is
a regression.

    +15.08 and 15.3 kcal/mol        a 102-atom TS against a ~1959-atom-region reactant; a
                                    mixed-region category error, reactant mismatch 0.9168 kcal/mol.
                                    The consistent-region barrier is +16.00. ts_frequencies_summary.txt
                                    must not be cited for either the barrier or the mode count.
    -313.30 and -18.65 cm-1         the STARTING Hessian. The converged TS has ONE mode, -313.07.
    ddE(bare) = -24.6898            D18: "not a number the method is entitled to report" - the gap
                                    is closed and single-reference B3LYP is outside its range there.
    +15.771, +15.78                 retracted
    stab_TS_total ~ -240 Eh         retracted
    frame 08170's barrier 0.000000  a collapsed band, no converged climbing image
    q_quad = 0.80 e                 withdrawn; both defining runs COLLAPSED. The largest CLEAN
                                    def2-SVPD single magnitude at site 1690 is +0.65 e.
    the K>2 max-lowering values     retracted
    "more charges do worse"         retracted as a claim
    +-0.751 e                       retracted
    Rod & Ryde's "59 vs 26"         retracted
    7.3 kcal/mol as "the enzyme's   it is a differential TS stabilisation from one lineage; the same
      barrier lowering"             group published 4.2 for the same quantity six years earlier
    any barrier from window 11 of   the 1D scan jumps 1.363 A across Claeyssens' TS at r = -0.5
      the 1D relaxed scan
    the five-frame r = +0.073       overturned small-sample reading
    the linear-statistics           overturned; circular statistics are mandatory for torsions
      "DIVERGENT" torsion verdict

Also: every committed barrier, Dset and d_shield at or above lambda = 0.75 is PROVISIONAL. D20 puts
the SCF instability onset there at BOTH bases, with a correction of +9.5558 kcal/mol at lambda 0.75
- 895.6 per cent of the budget - and states the corrections are LOWER BOUNDS.

### 5.1  The comparator, which is settled

Three families, and they must not be mixed (writeup/COMPARATOR_CLAEYSSENS_20261103.md and
consolidated_works/00_crosscutting/comparator_decision.txt):

    family 1    4.2 (2005) and 7.3 +- 2.0 (2011)    differential TS stabilisation, BsCM, same group
    family 2    7.9                                  this project's own subtraction, 19.2 in vacuo
                                                     against 11.3 in the enzyme
    family 3    -23.26 to -29.6                      DTSS by variation-perturbation decomposition

The gradient sign convention: this project's +0.978 IS the literature's -0.95, and 2011's -0.95 is
a 40-point combined fit that may not be compared to an enzyme-only gradient.


## 6  WORK THAT WAS DONE AND NEVER WRITTEN UP

Each of these has outputs on disk and no recorded conclusion. They are the cheapest results
available to this project, because the compute is already spent.

### 6.1  s10_benchmark - a five-method field-response benchmark with NO record at all

`05_qmmm/s10_benchmark/` contains exactly two files: `hpc_text_outputs.tar.xz` and its manifest.
Inside: 1472 members, 700 energies, **35 frames x 5 methods x {bare, field} x {R, TS}**. It
benchmarks r2SCAN-3c, B97-3c, HF-3c and GFN2-xTB against the B3LYP reference for the FIELD RESPONSE
ddE - the exact design quantity.

Computed here from those committed energies (arithmetic by this document, stated as such, no record
asserts it), mean deviation from the reference ddE over all 35 frames:

    r2SCAN-3c    -0.52 kcal/mol      min -0.76   max -0.26
    B97-3c       -0.46               min -0.70   max -0.14
    HF-3c        +1.01               min +0.52   max +1.56
    GFN2-xTB     -2.15               min -2.84   max -1.75

A method-sensitivity study of the design quantity, on 35 frames, already run.

### 6.2  09_mmtest - Na and Mg ECP walls, a failed experiment

`phase2_charge_design/09_mmtest/`, archive only. A water model with an Na-ECP cap on a 1.5-4.0 A
distance scan. cap-minus-bare, computed here from the committed energies:

    1.5 A  -5062.09 Eh     2.2 A    -37.37      3.0 A    -92.98
    1.8 A   -573.00        2.5 A    -19.85      3.5 A   -274.42
    2.0 A   -146.60                             4.0 A   -471.21

while the bare arm is smooth from -76.308052 to -76.317116 Eh. The cap arm diverges
catastrophically at every separation. Relevant because D23 states the reference library holds only
one published parameterisation of this class: this project tried another and it failed.

### 6.3  refstate_diagnostic - the dielectric series

`phase2b_charge_design/02_singlepoints/refstate_diagnostic/`, archive only. Barriers computed here
from the committed energies:

    def2-SVP    in vacuo 17.9046    CPCM eps 4.0 17.4737    CPCM eps 78.4 17.2439
    def2-SVPD   in vacuo 17.9947    CPCM eps 4.0 17.5347    CPCM eps 78.4 17.3082

The dielectric moves the barrier by about 0.66 kcal/mol from vacuum to water, at both bases.

### 6.4  Three more

  - `06_charge_tests` - 80 ORCA single points, settings and energies present, **no recorded
    verdict** anywhere in the directory.
  - `06_convex_cutplane` - its README says "Scaffold only ... solver/ to be written next", yet
    `solver/` holds 13 `explore_*_charges.txt` designs including genuinely fractional sets down to
    0.0061. No outcome recorded for any of them. The README is stale or the designs came from
    elsewhere; resolve before citing that directory either way.
  - The unified **4713-point 2-15 A re-optimisation is saved and has never been run**
    (04_grid/GRID_EXT_9to15_README.md:29).


## 7  OPERATIONAL TRAPS ALREADY PAID FOR

### 7.1  Do not regenerate ARRANGEMENTS.txt

Re-running `cs_opt_milp.py` reproduces the designs but can DOWNGRADE the record: S6-10 came back
"strategy lp, certified gap 0.21594" against the committed "full, 0.00000"
(relax/ADDITIVITY_RUNS.txt:41).

### 7.2  Do not mix the two grid lineages

The 2-8 A work used the old 1224-point margin-10 grid; 9-15 A used the margin-16 grid. The records
say explicitly: "Do NOT mix dv_grid.tsv (old) and dv_grid_9to15.tsv for a single design."

### 7.3  The nine non-normal terminations, and what each was

    19_ensemble/frame_04085/neb      Segmentation fault, exit 139 - but the NEB had CONVERGED first
    19_ensemble/frame_05680/neb      Killed, exit 137 (OOM) - also CONVERGED first
    nimg_test/frame_47641/neb        the only NImages 16 attempt; abandoned mid-run at LBFGS 26
    s13_lj_test (TEST C)             relaxed optimisation with the site carrying LJ, killed on
                                     walltime at 14454 s against a 14400 s limit
    s13_lj_test2                     LJ parameter investigation; Burschowsky's 3.2 A is the target
    03_dvpot/s5_dvmap_svpd           dv-map sampling comparison; extremes are a property of the
                                     substrate field, not of either sampling
    13_14_qmmm_setup/step13_verify   a check script - ALL CHECKS PASSED
    18_nebts_ts_irc/step18_verify    a check script - ALL CHECKS PASSED, and it is where the
                                     15.08-vs-16.00 explanation lives

The first two matter: a job can converge and still exit non-zero. Check for "THE NEB OPTIMIZATION
HAS CONVERGED" before concluding a frame failed.

### 7.4  Resources and nodes

  - **Memory requests were starving the queue, not the science**: seven of eight job types used
    under 4.11 GiB while requesting 180-250 GB, and after 44.7 h only 3 of 256 jobs were running.
    AMENDMENT 3 fixed it to 64 gb. Already done; do not redo.
  - **A comp036 node fault** (Exit_status -2, no retry, 97-145 s, no CPU used) destroyed six frames'
    whole r0 branch, resubmitted 28 October. **Five rival hypotheses were tested and disproved**:
    memory, walltime, afterok, queue purge, cycle cap. Separately, 7 of 16 D1 submissions died the
    same way and the "%qmmm block" hypothesis was tested and is WRONG.

### 7.5  Numerics

The measured between-batch reproducibility floor is **2.194e-11 Eh (96 ULP)**
(NUMERICAL_FLOOR_20261101.md). No energy gate may be set tighter. And margins must be computed from
the energies, not by subtracting four-decimal prints - the record logs five occurrences of that
error.

### 7.6  Three process traps the record documents and that recurred anyway

  - **A failed string search read as absence.** ERRATUM 7 records a quotation reported absent from a
    PDF because of the fi ligature, after which a committed document accused an earlier session of
    fabricating it. This happened twice more during the production of THIS document.
  - **A disqualified observable reused as a verdict column** (the DFT HOMO sign, PROBE 1).
  - **Margins from printed decimals** rather than from the energies.

Also: `cs_citecheck.py`'s in-text fallback compared a raw DOI against squashed text and could never
match, so every presence verdict was filename-only. Fixed 4 November; presence moved 34 -> 40.


## 8  WHAT IS GENUINELY OPEN

228 rows carry status `open`. The ones that gate the thesis:

  1. **The charge model.** Section 3. Nothing in the record authorises the current one, and the two
     routes out are closed (a) and unadopted (b).
  2. **Loss's sign**, section 4.1. Stage 6's tolerance cannot fail as written. Needs an amendment.
  3. **Whether the two TS_opt2 relaxations converge to a first-order saddle.** Submitted 3 November;
     Amendment 4 A4.8 states it cannot pre-empt the answer, and that if two imaginary modes appear
     at the stationary point it is reported, not resolved.
  4. **Sigma for the charged sphere, and an input file that implements it.** Section 3.3.
  5. **sum|q| <= 6.0 e and "30 to 35 mutually separated sites"** both have NO COMMITTED SOURCE and
     came from "Claude's reasoning in conversation on 23 October". Neither is a measurement.
  6. **The artefact's additivity at n > 1**, never measured at any n, at any basis.
  7. **The def2-SVPD/def2-SVP question** - but see section 1.1: the untested axis is the VALENCE
     one, and cs_stage4c already holds def2-TZVPD data.
  8. Open Phase 1 faults: f34991's r0 hit the 20-cycle cap while still descending; f44388's r0
     failed at cycle 2 undiagnosed; f36665's irc died at step 10; f20000 is stranded with its ts
     failed 11/12; frame 08170 has no converged climbing image.


## 9  WHAT THIS DOCUMENT IS NOT

It is not an assessment of whether the thesis works, and it takes no view on the catalytic verdict,
which remains SP_AMENDMENT2.txt A2.5's chain.

It is not a substitute for the files. The TSV's 1964 rows were produced by seven readings and only
the claims quoted in these sections were verified by hand. **Read a row at its cited path before
relying on it.**

It stops at commit df1fbd4 of chorismate-thesis-results, 7a4cd66 of chorismate-thesis-code, 1401ed3
of chorismate-refs and 794dcca of consolidated_works.

Three numbers in section 6 are arithmetic performed here on committed energies, labelled as such at
each point. They are not results and no record asserts them. If any is to be used, it needs a
pre-registered diagnostic of its own.
