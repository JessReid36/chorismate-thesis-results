# Where the charge-design work stands

**Reading copy of 26 November 2026, version 11, prepared for Jessica’s discussion with her supervisor on 27 November.** It replaces version 10.1 of the same day. It says what has just come in, what comes next, what is settled and what is a proxy. It leaves out the development history, which is in the consolidated write-up. Every number of ours comes from a committed file of the results repository at commit `173668c6` (listed at the end) and is labelled measured, derived, computed or estimate. The eight figures are drawn by scripts from the committed tables and coordinates. The enzyme’s charged groups appear in Figures 2 and 3 only so that positions can be compared; they are in no calculation, and nothing here is a statement about what an enzyme does.

**Status of this document.** It is not part of the committed record. Its quotations and decimal numbers were traced to the committed files by a script on 26 November (last section). It has not been through the validator that the consolidated write-up goes through. Version 8 enters what was committed on 24 and 25 November: D53 and D54 (charges of 0.25 e together), Amendment 11 (the search is run now, on the committed grid), D56 (the search), Amendments 12 and 13 with Amendment 13’s Note 1 (what follows the search), Forms Test 1, D57 (the wall), D58 (the force), Amendment 14, and the pre-registrations of D59, D60 and D61 with D59’s Note 1. Section 6 and Figure 7 are new; the sections that were 6 to 8 are now 7 to 9. Version 8.1 adds what version 8 left out: D56’s lowerings are without the Lennard-Jones shell’s term, and with it each is smaller (Amendment 13’s Note 1). Version 9 enters the results of D59 (the helium wall on the ten survivors with the largest lowering) and D61 (the functions at their positive charges), both committed on 26 November: two new points at the front, a new section 6.5, and section 9. D60 is not collected yet. Version 10 changes no number of ours and no result. It corrects what the text says about the literature: every paper cited is now in Jessica’s library, and each was read on 26 November against the sentences that cite it. Version 9 claimed more for some of them than they say, called a few things standard on fewer than three sources, and wrote of B3LYP’s orbital as if the electron were lost. Sections 3.1, 3.3, 3.4, 3.5 and 3.6, Figure 1’s caption, the references and the last section change. Version 10.1 differs from version 10 only in that Lee and Taylor (1989), the one paper version 10 marked as not yet read, is now in the library and has been read. Version 11 enters D60’s result, committed on 26 November (results `173668c6`): D56’s search with the map at ωB97X-V and with the older B3LYP map, and D56’s designs against random designs (a new point 9 at the front, a new section 6.6 with Figure 8, and section 9). What is not known yet is now section 6.7, and one cross-reference to it is corrected. No other number changes.

## For the discussion

### The position, in ten points

1. **The search has been run on the committed grid, and 18 of its 27 designs survive at both levels.** D56 placed the three best-ranked designs at each of nine numbers of charges, from 3 to 20, every charge 0.25 e, and measured each in two basis sets. There are survivors at 3, 4, 5, 6, 8 and 10 charges. The largest lowering is that of S_n10_k1: -13.02 kcal/mol at the working level and -12.89 in def2-TZVPD, where the barrier without charges is 26.82 and 25.70 (section 6). These are bare charges without the Lennard-Jones shell of the committed charge model; with the shell’s term every lowering is smaller by 0.17 to 0.33 kcal/mol (section 6.2).
2. **What gives way first as charges are added is the hold on the last electron.** The three designs of 12 charges fail on the fifth test alone: the energy to remove the dianion’s last electron falls from +1.25 eV without charges to about zero. Those of 15 charges fail in def2-TZVPD on the four reliability tests (section 6, Figure 7).
3. **A survivor is not a result.** Its numbers are for frozen geometries of one frame, in vacuo, at one functional. No survivor has been through the cross-check or the coupled-cluster reference, and none has been relaxed. Its charges lie 3.13 to 3.21 Å from the nearest atom, inside the 3.50 Å that the designs of 17 November kept to: since Amendment 11 the grid is not cut there, each charge is capped at 0.25 e, and every design is measured instead (section 4).
4. **Charges of 0.25 e together held at two levels** when functions that can hold an electron stood at every positive charge: one to six positive charges, at the reactant and at the transition state (D53). The old eleven-charge design, which also carries five negative charges, took electrons at the reactant at both levels (D54). The old arrangements are set aside (section 8.5).
5. **With functions at their positive charges, five of the ten survivors with the largest lowering hold, five are not settled, and none takes electrons at both levels** (D61). The five that hold are S_n05_k2, the three designs of six charges and S_n08_k2, the largest lowering of the five (-10.76 kcal/mol at the working level). The five not settled are the three of ten charges and two of eight: at the reactant, at the working functional, the 24 atoms give up 0.35 to 0.88 e to the functions (Löwdin charges), while at ωB97X-V the same runs give up 0.03 to 0.05 e. For S_n10_k1 and S_n10_k3 the energy gained, 0.3158 and 0.3749 eV, is above the line of 0.3127 eV the record fixed; for S_n10_k1 by 0.0031 eV (derived). This tells against the designs with the largest lowering: the direction of a higher barrier (section 6.5).
6. **Behind a helium wall on their positive charges all ten keep the word SURVIVOR** (D59), each lowering smaller than bare by 0.15 to 0.26 kcal/mol at the working level (derived; 1.5 to 2.2 per cent). The wall is a model beside the bare charges, and the test of whether it is nearer real ions was not formed (point 8).
7. **Every survivor pushes on the substrate.** It adds 2.4 to 8.8 kcal/mol/Å to the gradient, and one component of the force on one atom reaches 30.7 (D58). A first-order map of that force agrees with the direct calculation, so a rule on it can enter the next search. A first-order map of the hold on the electron does not agree, so no such rule enters (section 6).
8. **The wall’s test against real ions was not formed** (D57). Its two runs of a bare whole charge at the reactant were stopped by their time limit, so by its pre-registration the helium wall is NOT SUPPORTED, and the relaxation pilot has no arm behind the wall. The word comes from two missing runs and not from evidence against the wall (section 6.4).
9. **At first order, a second functional places mostly the same designs, and every design beats chance** (D60). With the map at ωB97X-V/def2-SVPD, which agrees closely with the working map (Pearson 0.9977), D56’s search places 17 of its 27 designs again, and at seven of the nine numbers of charges its best design is D56’s first-ranked. With the older B3LYP map, at def2-SVP, it places different designs at seven of the nine numbers, which give up 0.06 to 0.29 kcal/mol against D56’s best when scored on the working map (derived). Each of D56’s 27 designs scores lower than all 10 000 random designs of each of two kinds. D60’s pre-registration: "Nothing here names, keeps or drops a design" (section 6.6).
10. **No barrier here is quoted as catalytic.** The catalytic verdict is the relaxed chain of the criteria, not a frozen number. A pilot relaxation of three survivors is next (section 6.7).

### What came in on 26 November

- **Collected and committed on 26 November: D59 and D61** (section 6.5). D59’s 60 runs with the functions stopped in ORCA’s start-up, because Claude had placed each ghost centre on its charge (D59 NOTE 1); D61 made them again, each ghost centre 0.01 Å beyond its charge, and all 120 of its runs were measured.
- **Collected and committed on 26 November: D60** (section 6.6), at results `173668c6`. Its first step on the PC took 3 h 38 min as a whole (Jessica’s printout of 26 November), where its pre-registration estimated "about one to one and a half hours". The estimate repeated Claude’s estimate for D56’s search rather than the 1 h 36 min that search took on the PC (her printout of 24 November); the error is Claude’s, no reading depends on it, and D60 NOTE 1, sent for commit on 26 November, records it.

### What is next, in order

1. **The pilot relaxation of three survivors** (Amendment 13, item 5): S_n03_k1, S_n06_k1 and S_n10_k1, by the relaxed chain of the criteria, in vacuo, the charges held where they are (of the three, D61 finds S_n06_k1 holding with functions and S_n10_k1 not settled; S_n03_k1 was not among the ten tested), with the committed sphere model (a Lennard-Jones shell on each charge) because bare charges in a geometry optimisation imploded in the earlier work, the reactants first. Its pre-registration is still to be written. Amendment 13: "A relaxed barrier of the pilot is not quoted as a result and no design is kept or dropped on it."
2. **The second search** (Amendment 13, item 6): D56’s search again with a rule on the first-order added force, at a ladder of limits one step of which is no limit, every charge 0.25 e, and eleven charges added to the numbers of charges because D56 measured none between ten and twelve. Its rule on the hold on the electron is not used, as that map failed its check.
3. **A dated amendment on which designs get the cross-check and the coupled-cluster reference**, once the pilot and the second search have reported (Amendment 13, item 10).
4. **Bring the consolidated write-up up to date** in one revision; it is being prepared.

### Points to settle or discuss

- **The wall.** D57’s test against real ions is not formed because two bare runs reached their time limit, which Claude had set in the job scripts. Whether to measure them again, with a longer limit, in a new diagnostic is open. It could only move the word toward SUPPORTED, which would add the walled arm to the pilot: the direction of a lower barrier, since some designs show larger lowerings behind the wall (section 6.4).
- **What counts as holding.** D61 finds five of the ten holding and five NOT SETTLED, and none taking electrons at both levels. Whether a design that is not settled, or that takes electrons at the working functional only, may still be quoted is left by Amendment 11 "for the amendment that follows that result", which is now D61’s. For S_n10_k1 and S_n10_k3 the second level did not decide because ORCA raised its level shift in those runs (`LevelShift set to 1.000 Eh` in their outputs) and the committed reader then withholds the gap test. A run made otherwise could decide them, in either direction. D61’s pre-registration, as D59’s: "Nothing found here names, keeps or drops a design, and none is rescued; D56's words stand."
- **The pilot’s three designs.** Amendment 13 fixed S_n03_k1, S_n06_k1 and S_n10_k1 before D61; S_n10_k1 is now one of the five not settled. Whether the pilot keeps it is Jessica’s decision.
- **How large a force.** No published limit is used: Amendment 13 records that "the published 10 kcal/mol/A does not carry over". The second search runs a ladder of limits, fixed in its pre-registration from what the map gives for D56’s survivors.
- **How much of a frozen lowering survives relaxation.** That is the pilot’s one question; until it reports, a frozen lowering says nothing about how much of it is left once the substrate can move.
- **Charges of different sizes under a budget.** Jessica decided on 25 November to finish the arm of 0.25 e first (Amendment 13, item 6 (c)).
- **The second method** beside CAM-B3LYP is ωB97X-V, by D52’s rule B. At first order a search at ωB97X-V places mostly the same designs as at the working functional (D60, section 6.6).
- **PWPB95 and revDSD-PBEP86.** ORCA 6.0.1 cannot run the stability check with PWPB95, so its two levels are open; Amendment 9 does not pursue it now and does not drop it. For revDSD-PBEP86 the calculation without charges is itself found unstable (sections 3.3 and 7), and its numbers carry a fixed wording.
- **Barrier only, or binding as well?** The score counts only the barrier. The designs of 17 November put negative charge beside the ring carboxylate, where the enzyme has Arg63′ (table under Figure 3).
- **One frame, gas phase, frozen geometries.** When more frames and an environment come in (sections 2 and 9).

### The findings

Section 9 lists on one page what can be said today and what cannot. The evidence is in sections 3 to 8: the level of theory (3), how the charges are represented and where they sit (4), the optimiser (5), the search on the committed grid and what followed it (6), the six designs of 17 November and their cross-check (7) and when a bare charge takes an electron (8).

## 1. The question

Chorismate mutase speeds up the rearrangement of chorismate to prephenate. The project asks a narrower question: can a few point-like charges placed around the substrate, with no protein, lower the barrier of that rearrangement, and can an optimiser find where to put them?

The substrate is the chorismate dianion: 24 atoms, charge -2, 118 electrons. The number every calculation reports is **ddE**: the barrier with the charges present minus the barrier without them. It is negative when the charges lower the barrier.

## 2. One geometry, and why this one

All current work uses the reactant and the transition state of **one frame, 42436**, held frozen. Jessica decided this on 21 October 2026 (decision S1), and the record gives the reason.

- **Frame 42436's two geometries are optimised stationary points**, the kind of point a barrier is defined between. They come from the QM/MM package: the transition state converged in 7 cycles and the reactant, reached by following the reaction path down from it, in 6.
- **The other frame used earlier, 41786, is not.** The decision document says of that set: "Its "reactant" is NEB band image 0 and its "TS" is the climbing image. Neither is a stationary point." The project's own test of band-image reactants accepted none of 30 frames; re-optimising frame 41786's lowered its energy by 4.58 kcal/mol against a tolerance of 1.0 (measured).
- **The difference is not small.** At the one level run on both frames the barrier is 16.67 kcal/mol at 41786 and 18.46 at 42436 (measured). Across five methods the geometry moves the barrier by 1.5 to 3.6 kcal/mol and changes the order of the methods (D35).

**The limit.** It is one frame of thirty, and whether it is typical is not known. More frames come later, and should be the same package's stationary points, not band images.

## 3. The level of theory

### 3.1 How a level is chosen, in the papers we hold

The papers we hold describe the five steps below. Each step names the papers that say it; what is this project’s own is marked as such.

1. **Get a trustworthy reference for the property.** For a barrier that is a high-level wavefunction calculation (coupled cluster), on the system itself or on the largest model of it that such a calculation can reach (Wappett and Goerigk 2021). Comparing functionals with correlated calculations of this kind is a standard way of choosing one for a given application (Ranaghan and co-workers 2019). For chorismate mutase such a calculation has been made in the enzyme, and it agreed with experiment to within about 1 kcal/mol (Claeyssens and co-workers 2006; Mulholland 2007).
2. **Do not trust one functional.** Density functionals cannot be improved step by step, and for this very reaction in the enzyme the barrier varied by about 13 kcal/mol across functionals in a QM/MM study (Ranaghan and co-workers 2019). DFT barriers are often several kcal/mol too low (Mulholland 2007). For B3LYP on this reaction the Bristol group give the typical error as about 3 kcal/mol (Claeyssens and co-workers 2011).
3. **Start from the classes of functional the large benchmarks favour.** The GMTKN55 study (Goerigk and co-workers 2017) ranks double hybrids first and advises using them wherever they can be afforded; among ordinary hybrids it names ωB97X-V, M05-2X and ωB97X-D3, and PW6B95 as the best conventional one. B3LYP is not among its recommendations. A double hybrid is a functional with an added wavefunction-type term: more accurate and more costly.
4. **Converge the basis set**, with diffuse functions for an anion (Bursch and co-workers 2022). Diffuse functions are the extra, spread-out functions needed to describe loosely held electrons.
5. **Check anything peculiar to the system.** The best-practice guide of Bursch, Mewes, Hansen and Grimme (2022) asks, for example, for a check that the system has no multi-reference character before a single-reference method is trusted, and recommends multi-level work: structures from a cheaper level, energies from a better one. Fixing the choice before using it, and saying how much the answer depends on it, are this project’s own rules (section 3.5).

### 3.2 What we did, step by step

| step | what the record holds |
|---|---|
| 1. reference | DLPNO-CCSD(T), an efficient form of coupled cluster, on our own two geometries: 23.86 kcal/mol at def2-TZVPD (D36) and 22.90 at def2-SVPD (D41), both measured. It is an electronic energy on frozen gas-phase geometries, not the experimental number. Its three approximations have since been measured (D45, section 3.6). |
| 2. several functionals | nine functionals, each at two basis sets (D37 and its Amendment 1) |
| 3. favoured classes | range-separated hybrids, meta-hybrids and two double hybrids are among the nine |
| 4. basis | def2-SVPD and def2-TZVPD, both with diffuse functions. Every functional's barrier is 0.35 to 1.30 kcal/mol lower in the larger basis; the benchmark's is 0.96 higher (derived). |
| 5. system check | whether the dianion holds its last electron: the orbital test (D28, D37) and the detachment energy at eight functionals (D40) and at coupled-cluster level (D39) |
| 5. fixed in advance | Amendment 7 named a working level and five cross-check levels before any design reached them. D44 has run them (section 7). |

### 3.3 What it shows

Figure 1, on the next page, sets the nine functionals against the benchmark barrier and against the question of whether the last electron is bound. Four things can be read from it.

- **B3LYP fails both tests.** Its barrier is 6.56 kcal/mol below the benchmark in def2-TZVPD, and in def2-SVPD its highest occupied orbital lies 1.23 eV above the vacuum level at the reactant, as if the last electron were unbound. Approximate functionals often do this for anions, and it does not by itself mean that the electron is lost (Lee, Furche and Burke 2010; Kim, Sim and Burke 2011): B3LYP’s own detachment energy at the reactant is +0.50 eV, bound.
- **Four functionals are within 3 kcal/mol of the benchmark at def2-TZVPD:** CAM-B3LYP (+1.84), revDSD-PBEP86 (-2.36), PWPB95 (-2.52) and PW6B95 (-2.90). Amendment 7 left PW6B95 out of the cross-check because its orbital is above zero. It drew the 3 kcal/mol line with all nine numbers known, so the line is a convenience and not a test.
- **The general-purpose favourites overshoot here.** ωB97X-V, ωB97X-D3, ωB97M-V and M06-2X are 3.5 to 5.9 kcal/mol too high. This is why step 1, a reference on the system itself, matters.
- **No functional is best on both tests.** CAM-B3LYP is nearest the benchmark barrier at def2-TZVPD, but its orbital (-0.59 eV) lies above the coupled-cluster band. The ωB97 functionals and revDSD-PBEP86 have the reactant's orbital inside the band; the ωB97 barriers are too high.

Two cautions. At the working basis, def2-SVPD, CAM-B3LYP is 3.93 kcal/mol above the benchmark of that basis, because the benchmark and the functionals move in opposite directions with the basis. And PWPB95's orbital is below zero at the reactant (-0.41 eV) but just above it at the transition state (+0.07 eV); the record's orbital test was made at the reactant only.

A third caution, new since 18 November. For revDSD-PBEP86-D4 every barrier, ddE and comparison in this document is, in the record’s fixed wording, "on the restricted solution, which the stability analysis finds unstable in the self-consistent step; the solution it leads to has the higher final energy (D44, F5)". No number at that level is withdrawn. What it means for the comparison with the benchmark is recorded as not decided.

![Figure 1](figs/S1_level_of_theory.png)

**Figure 1.** The nine functionals on the bare dianion, frame 42436, in vacuo. A: the barrier at two basis sets. B: its distance from the coupled-cluster benchmark at the same basis. C: the energy of the highest occupied orbital at the reactant and the transition state; in the hatched region the functional’s highest occupied orbital lies above the vacuum level, as if the last electron were not bound. The short vertical line is minus the functional's own detachment energy, and the grey band in C is minus the coupled-cluster detachment energy by its two routes (section 3.4). The narrow hatched band in A and B is new: the benchmark after D45's three measured corrections, by its two estimates, 23.13 and 23.52 kcal/mol; in B it marks where zero would then lie. Both are estimates and replace nothing (section 3.6). The revDSD-PBEP86-D4 numbers carry the wording of the third caution above. All else measured.

### 3.4 The detachment energy, and which reference to use

The detachment energy is the energy needed to remove one electron: the monoanion's energy minus the dianion's at the same geometry. Positive means the dianion holds its second electron.

The older documents used +0.5123 eV as the yardstick. **That number is a B3LYP calculation, and B3LYP is the functional the project retired, so it should not be the yardstick.** The record holds better ones. All are measured, on the bare dianion at the reactant geometry.

| calculation | detachment energy (eV) |
|---|---|
| B3LYP-D3BJ / def2-SVP, a basis with no diffuse functions | -0.32 |
| B3LYP-D3BJ / ma-def2-SVP, the old yardstick | +0.51 |
| B3LYP-D3BJ / def2-SVPD | +0.50 |
| seven further functionals / def2-SVPD (D40) | +0.77 to +1.32; CAM-B3LYP +1.25 |
| coupled cluster, read directly: IP-EOM / def2-SVPD (D39) | +1.06 |
| coupled cluster, as an energy difference: CCSD(T) / def2-SVPD (D39) | +1.77 |

- **The sign is solid.** Every calculation with diffuse functions in the basis, eleven in all, says the bare dianion is bound. The one without them says the opposite, which is why the basis must carry them.
- **The size is not.** The two coupled-cluster routes differ by about 0.7 eV. D39 reads that difference as a measurement of spin contamination in the monoanion's starting wavefunction (0.958 where a clean doublet gives 0.750), and asserts no preference between the two. So the higher-level reference is a range, about +1.1 to +1.8 eV, two to three and a half times the old number.
- **What changes.** Against the old yardstick CAM-B3LYP's orbital looked nearly exact. Against the coupled-cluster range it is 0.47 eV too shallow at the nearer end (derived).
- **What does not change.** Every test in section 4 uses the sign, not the size.

I found no experimental value for the chorismate dianion in one search, which does not show there is none. Photoelectron experiments on gas-phase benzene dicarboxylate dianions give electron binding energies of roughly 0.2 to 1.0 eV (Wang and co-workers 2000). They are other molecules; that is context, not a test. The analysis follows a published route: Herbert and Ortiz (2000) computed the detachment energies of small dicarboxylate dianions both as an energy difference between the ion with and without the electron and by a direct method, an electron propagator.

One more calculation, the energy-difference route with a spin-pure reference, would narrow the range. It is a suggestion and has not been pre-registered.

### 3.5 Working, cross-check and production levels

**What a production level is.** The one recipe, a functional and a basis set, with which every number the thesis reports is computed. It is written into a dated amendment before the numbers are seen, so that designs can be compared with one another and the recipe cannot be picked for the answer it gives. The project cannot carry six levels to the end; it needs one, or one to search with and one to report with.

**Where we are.**

- **Working level, for searching:** CAM-B3LYP-D3BJ/def2-SVPD, with a stability check on every run. Amendment 7 names it because the design record already stands there: "That, and not a claim that the level is right, is the reason it is named."
- **The larger basis set is now part of the search's own test** (Amendment 9, 20 November): "A design is a SURVIVOR OF THE SEARCH, and nothing more, only if it passes the five legs at the working level AND, at CAM-B3LYP-D3BJ/def2-TZVPD, is RELIABLE on four legs, passes the fifth leg, and has a ddE that is WITHIN the tolerance of its ddE at the working level." A leg is one of the five tests of section 4.
- **Cross-check levels, for confirming:** CAM-B3LYP at def2-TZVPD, and the double hybrids PWPB95 and revDSD-PBEP86 at both basis sets. D44 has run them on the six designs (section 7).
- **Production level: none adopted.** Amendment 8 fixed the rule for choosing it on 18 November. Read on D44's words, no candidate level meets it today: at each one, the larger of the rule's two reference designs is unreliable in the larger basis set, or a test cannot be run (Amendment 9, A9.2). So the coupled-cluster ddE of those two designs is not run, and "The number 46 is not used again." The reference is to be run on two survivors of a search, picked by the same rule: the smallest lowering and the largest. The grid was not rebuilt (Amendment 11), and which search's survivors, D56's or the second search's, is decided by a dated amendment once the pilot relaxation and the second search have reported (Amendment 13, item 10).

**How one is selected after a benchmark.** Five rules. The first, and the last part of the third, are in the papers we hold; the rest are this project’s own working rules and are not claimed from the literature.

1. **Benchmark the quantity you will report**, not a neighbour of it, on a model as close as can be afforded to the one you will run (Bursch and co-workers 2022; Wappett and Goerigk 2021). For us that is ddE with the charges present, and whether the dianion stays bound.
2. **Benchmark at the basis set you will run** (ours).
3. **Set the tolerance first** (ours). Then take the cheapest level inside it that passes the system's own checks, and prefer a class of functional that the large benchmarks support over one that wins a single comparison (Bursch and co-workers 2022).
4. **Keep two levels at most** (ours): one to search, one to report, with a sample of the reported numbers confirmed at the reference level.
5. **Write it down, then stop changing it** (ours). Quote the spread across the levels tried as the uncertainty of the method.

**Our rule, as committed (Amendment 8, with Amendment 9's change of the reference designs).** A level qualifies if both reference designs pass the five tests there, their ddE is within 15 % of the coupled-cluster reference in either direction, and, for a level at the smaller basis set, the five tests also hold with the same functional at the larger one. The report level is the first that qualifies in an order fixed in advance. If none qualifies, none is adopted, and each design is reported at every level with the reference beside it.

### 3.6 Is our benchmark good enough to choose with?

It is the right kind of benchmark, and its three approximations have now been measured (D45, committed 19 November). It is still not a reference for the quantity the thesis reports.

| what the papers we hold ask of a reference | what ours has |
|---|---|
| coupled cluster with triples, on the system itself (Mulholland 2007; Ranaghan and co-workers 2019; Wappett and Goerigk 2021) | yes: DLPNO-CCSD(T) on our own two geometries |
| a check that a single-reference method is valid (Bursch and co-workers 2022) | yes: the T1 diagnostic is 0.016 at the reactant and 0.019 at the transition state, under the 0.02 that Lee and Taylor (1989) suggest as the warning sign (a guide we did not pre-register), and the Hartree-Fock reference holds the last electron |
| tight local-correlation settings, with their error checked (Liakos and co-workers 2015; Wappett and Goerigk 2021) | measured: with the threshold tightened in two steps the barrier is 23.46, 22.90 and 22.48 kcal/mol (def2-SVPD). The steps are -0.56 and -0.42, which the rule fixed in advance reads as CONVERGING; the last step is still 0.42 |
| an accurate treatment of the triples (Guo and co-workers 2018) | measured: the fuller, iterative treatment lowers the barrier by 0.76 kcal/mol (22.90 to 22.14, def2-SVPD) |
| the basis-set limit, by extrapolation (Wappett and Goerigk 2021) | estimated: at a cheaper correlated level (MP2) the barrier is 17.02, 17.48, 17.56 and 17.92 kcal/mol at four basis sets, so +0.45 from def2-TZVPD to def2-QZVPPD (measured), and 18.17 by extrapolation (estimate) |
| the quantity that will be reported (Bursch and co-workers 2022; Wappett and Goerigk 2021) | no: the bare barrier only. No reference for ddE exists; it waits for survivors of a search, chosen by a dated amendment (section 3.5) |
| the chemical environment, and more than one structure of the system (Claeyssens and co-workers 2006; Wappett and Goerigk 2021) | no: one frame, in the gas phase. In one enzyme study the same functionals ranked differently on three models of one active site (Wappett and Goerigk 2021) |

**What the three corrections add up to.** Added to the committed 23.86, they give 23.13 kcal/mol with the measured steps and 23.52 with the extrapolated ones: 0.73 and 0.34 lower (derived). D45's result says of the two: "BOTH ARE ESTIMATES. Each adds corrections that were measured one at a time, two of them at the smaller basis set and one at MP2, and whether they add is not measured. Neither replaces D36's number, and no conclusion rests on either." The committed 23.86 and 22.90 stand.

**What it supports.** Rejecting B3LYP, which is 5.8 to 6.6 kcal/mol low against the committed number and both estimates, and the four functionals that are 3.5 to 6.6 high.

**What it does not support.** A choice among CAM-B3LYP, revDSD-PBEP86 and PWPB95. Against the committed number they are +1.84, -2.36 and -2.52 kcal/mol (revDSD-PBEP86 with the wording of section 3.3); against the two estimates +2.57 and +2.18, -1.64 and -2.03, -1.79 and -2.18. Which is nearest depends on which number is used.

## 4. How the charges are represented

**Bare point charges.** The six designs of section 7 have every charge at least 3.50 Å from every substrate atom at both states. The distance is r~safe~: D11 measured it as the distance inside which a bare charge and the same charge behind a repulsive wall disagree, and concluded "No design measured inside r_safe is interpretable."

Four limits belong with it. The fourth is new.

- D11's erratum: "r_safe = 3.50 A BOUNDS THE VALIDITY OF A MODEL. IT IS NOT A STATEMENT ABOUT WHERE A CATALYTIC CHARGE MAY SIT."
- It was measured at the retired B3LYP level, on one axis, and has not been re-measured at the working level.
- Distance costs effect: the record's own estimate is "about 25 per cent less field per charge" at 3.50 Å than at 2.96 Å.
- **Distance alone does not make a charge safe.** For a charge of +1.00 e, D47's pre-registered reading of what it then measured is: "distance took the charge out of the reach of def2-TZVPD and did nothing else. A safe distance is then a statement about a basis set, and no walk out is made for a size that behaves so." Section 8 gives the measurements.

The grid has not been rebuilt: D43 used the 616 of the grid's 2626 sites that already lie at or beyond 3.50 Å, in a shell that ends at 4.02 Å. Figure 2 gives the true distance of every site and Figure 3 shows where the charges sit, to scale.

**The committed model and the frozen runs.** The committed charge model is the sphere: a point charge that is also an atom of the force field, with the Lennard-Jones term of an Amber nitrogen. The frozen diagnostics since D31 write bare point charges. In a frozen run the two are the same electronic calculation and the shell adds a classical energy, the same at every level of theory (Amendment 13’s Note 1). In a relaxation they are not the same: bare charges in a geometry optimisation collapsed onto the substrate in the earlier work, so the pilot relaxation uses the sphere (section 6.5).

**Since Amendment 11 (24 November).** The grid is still not rebuilt, and the safe surface is not measured first. The search of section 6 used every site of the committed grid that admits a charge of 0.25 e, 1488 of the 2626, inside r~safe~ as well as beyond it, and no charge is larger than 0.25 e. That is the region in which no run of the record with bare charges and no functions at them showed electrons leaving the atoms: Amendment 11 read every output under the diagnostics' folder with a script, and of 40 readable runs of that kind in def2-TZVPD or def2-QZVPPD none showed a sign (derived by that script, with thresholds it states). Every design the search places is measured by the five tests in both basis sets: "A design that fails is dropped; none is rescued." So r~safe~ no longer decides where a charge may stand; the measurement of each design does.

A design's ddE counts only if it passes five tests.

| test | the question in plain words | fails when |
|---|---|---|
| 1. relocation | has the calculation moved electrons onto or off one atom? | the largest atomic charge rises by 0.25 e or more |
| 2. dipole | has the charge distribution been distorted? | the dipole is twice the control's or more |
| 3. gap | has an empty orbital dropped to meet the filled ones? | the gap is below 1.0 eV and below half the control's |
| 4. stability | is the calculation on the lowest solution? | the last stability check says unstable |
| 5. binding | does the dianion still hold its second electron with the charges present? | the detachment energy is zero or negative at either state |

Tests 1 to 4 compare the dianion with the charge-free calculation. Test 5 (Amendment 6) needs a second calculation with the same charges, the monoanion. Since Amendment 9 the five tests are also required at CAM-B3LYP in def2-TZVPD. A further test, with basis functions placed at the positive charges (section 8), is run on the ten survivors with the largest lowering and reported beside them; it is not part of the word SURVIVOR (Amendment 11; D59 and D61).

Four other representations were tried and none is in use for designs: a classical repulsion term on each charge (kept as a small energy term; its purpose is untested), real ions (inconclusive and withdrawn), a charge behind a wall, a core potential that keeps the substrate's electrons off it (it removes the relocation, but is not adopted and not calibrated; it is the fallback, and Amendment 10 allows it as a test arm), and smeared charges (exploratory, not adopted). D57 has since measured the helium and the neon wall on the positive charges of three designs that are not survivors, and the wall against real ions (section 6.4).

![Figure 2](figs/S6_site_distances.png)

**Figure 2.** The sites, and the enzyme’s own charged groups, by their true distance to the nearest substrate atom, hydrogens included. Lower two blocks of the top panel: each tested site at the reactant (filled) and at the transition state (open); the sign is the charge it carries in the designs. All fifteen are at or beyond 3.50 Å at both geometries; the closest is site 1421 at the transition state, 3.504 Å. Upper block: the enzyme’s six charged residues in the same frame, each by its charge centre (the central carbon of an arginine’s charged group, the carboxylate carbon of the glutamate, the nitrogen of the lysine). They are in no calculation. Four of the six lie inside r~safe~: Glu78 at 2.68 and 2.62 Å, Arg63′ at 3.18 and 3.20, Arg90 at 3.19 and 3.27, and Arg7 at 3.47 and 3.49; Arg116 and Lys60′ are off the scale to the right. Blue marks Arg90 and the design sites that agree with it, orange Arg116 and its site, by the rule given under Figure 3. Bottom: all 2626 sites of the grid, each by the smaller of its two distances. 2010 lie inside r~safe~ and were not used by D43; 616 lie at or beyond it, the farthest at 4.02 Å. Site 1107 is 4.04 Å away at the reactant and 3.97 Å at the transition state, so it counts as 3.97. Derived from the committed coordinates; the count of 616 and the 4.023 Å are also D43’s own, and the six residue distances are also the committed map’s own record.

![Figure 3](figs/S5_sites_to_scale.png)

**Figure 3.** Where the charges sit, to scale. All four panels use one scale and the ticks are in Å. The geometries are the two that every calculation uses (frame 42436) and the sites are the committed grid's. Only the size of the symbols is not to scale, since a point charge has no size. Top row: the substrate seen from above. Bottom row: the same, turned a quarter turn and seen from the side. The grey shape is the substrate's van der Waals outline (Bondi's radii), with its atoms and bonds; O marks the oxygens. The black lines are the C–O bond that breaks and the C–C bond that forms, with their lengths. The solid line is r~safe~: every point 3.50 Å from the nearest atom, as that surface looks from this direction. The dotted line is 4.02 Å, beyond which this grid has no site. The six designs use eleven sites between them: a filled circle carries a positive charge and an open one a negative charge, and the numbers are the site numbers of Figure 2 and of the table in section 7. The squares are four more sites, each tested with a single charge in D43. The small dots are the other 601 sites at or beyond r~safe~. The coloured and hatched shapes are the charged groups of five of the enzyme’s six charged residues in the same frame, each drawn to scale as the van der Waals outline of the atoms that carry its charge (nine atoms for an arginine, three for the glutamate); Lys60′, 8.8 Å away, is outside the panels. A group in front of the substrate is drawn over it; a group behind it passes under the grey outline, with its hidden edge dotted. Arg90 is blue and Arg116 orange, and a design site of the same colour agrees with that residue: it carries a charge of the same sign and lies within 3.0 Å of an atom of the group. The hatched groups (Arg7, Glu78, Arg63′) have no such site. The sites do not move between the reactant and the transition state; the substrate does, by 0.26 Å (root mean square over its 24 atoms). **A symbol drawn inside the solid line is above or below the substrate in that view, not closer to it**: compare the two rows, or read its true distance in Figure 2. The calculations contain only the substrate and the point charges: no enzyme, no water and no wall. The enzyme’s groups are drawn so that positions can be compared, and for nothing else. Drawn from committed coordinates; the viewing directions, the outlines and the colouring rule are derived.

**The designs against the enzyme’s own charged groups.** Derived on 18 November and post hoc; nothing is concluded from it. The aim of the design is not to recreate the enzyme, so this is a check on where the charges fall and not a target. The residue positions are those of the same frame, from the committed map of 21 October. A design site *agrees* with a residue when it carries a charge of the residue’s sign and lies within 3.0 Å of an atom of the residue’s charged group at either geometry; with the opposite sign it is *against*. The 3.0 Å is a round number chosen today, so the distances are given and another choice can be applied to them.

| residue (charge) | charge centre to the nearest substrate atom, R and TS (Å) | coefficient at the grid site nearest the centre (kcal/mol per e) | design sites that agree | design sites against |
|---|---|---|---|---|
| Arg90 (+1) | 3.19, 3.27 | −5.70 (site 1680, 0.30 Å from the centre) | 1124 (0.68 Å), 1073 (2.55 Å) | none |
| Arg7 (+1) | 3.47, 3.49 | −1.11 (site 218, 0.03 Å) | none; the nearest positive site is 1005, 3.37 Å | none |
| Glu78 (−1) | 2.68, 2.62 | −0.22 (site 1328, 0.22 Å) | none | none; the nearest design site is 1359 (+), 4.96 Å |
| Arg116 (+1) | 5.63, 5.62 | none: the nearest grid site is 2.27 Å from the centre | 1005 (1.93 Å) | none |
| Arg63′ (+1) | 3.18, 3.20 | +3.05 (site 734, 0.37 Å) | none | 1460 (2.06 Å), 1421 (2.39 Å), 557 (2.88 Å) |
| Lys60′ (+1) | 8.82, 8.99 | none: the nearest grid site is 5.35 Å from the centre | none | none |

A negative coefficient means that a positive charge at that point lowers the barrier at first order (D33a, the working level). So the designs put positive charge where Arg90 sits, which is also the most barrier-lowering of the four positions that have a grid site. They put negative charge next to Arg63′, where the enzyme has a positive group and the map says a positive charge would raise the barrier. Site 1107 (+) is 3.32 Å from Arg90’s group, just outside the rule. Two cautions. The enzyme’s groups also hold the substrate in place, and the design’s score counts only the barrier. And four of the six groups sit inside r~safe~ (Figure 2), where this charge model has not been shown to work, so a design cannot take their positions even where it agrees with them.

## 5. The optimiser

### 5.1 What it does

For every grid site i the optimiser holds one number, a~i~. For a chosen number of charges and one charge size it gives each site the sign that helps, then takes sites in order of how much they help, skipping any site closer than 3.25 Å to one already taken. D43 added two rules: only the outer sites, and at most half the charges negative, so that the charges sum to zero or more.

That is a greedy rule: it takes the best site first and never reconsiders. D43 says so of its own six designs: "Part B is six designs by a greedy rule, not an optimisation."

**D56 used the committed optimiser instead** (`cs_opt_milp.py`). For each number of charges it looks for the arrangement with the best score that obeys the rules: each charge 0.25 e at most, any two charges 3.25 Å apart, the charges summing to zero or more. Its pre-registration: "a design is taken only if the solver proves it optimal". The second and third designs at each number must each have a charge more than 1.5 Å from every charge of the better ones (decision O7). With a linear score and a cap, every charge comes out at +0.25 or -0.25 e unless the rule on the sum holds one back.

### 5.2 From the potential to ddE

- A molecule creates an electrostatic potential V around itself. A small charge q placed at a point has the energy q × V there.
- That holds for the reactant, with potential V(R), and for the transition state, with V(TS).
- The barrier is E(TS) - E(R), so the charge changes it by q × [V(TS) - V(R)].
- **a~i~ is that difference at site i**, in kcal/mol per unit charge. So ddE ≈ a~i~ × q~i~, and for several charges the terms add. The optimiser's score is this sum plus a small classical term, 0.08 to 0.15 kcal/mol for the six designs (derived).

Put simply, a~i~ says how much more the transition state "likes" a positive charge at site i than the reactant does. Where a~i~ is negative a positive charge lowers the barrier; where it is positive a negative charge does.

This is a **first-order, or linear, model**. It treats the substrate's electrons as if the charges did not disturb them. Real charges do, in three ways the model leaves out:

- **Polarisation.** The electrons shift toward a positive charge. The effect grows with the square of the charge and differs between the two states.
- **Relocation.** Too close or too strong, and the calculation moves electrons wholesale. Tests 1 to 4 catch this.
- **Losing an electron.** A negative charge can push the second electron off. Test 5 catches this.

Figure 4 shows how far this model falls short of the measurement at the working level.

![Figure 4](figs/S3_linear_score.png)

**Figure 4.** The first-order prediction against the measurement for D43's eighteen conditions, all at the working level. On the dashed line the two are equal. The six designs (filled) lie below it: the charges lower the barrier by more than predicted, by 3 to 34 %. The crosses are single negative charges, where the dianion is METASTABLE, so their ddE is not a barrier effect. The prediction is the optimiser's objective and not a measurement. Four of the six designs do not pass the cross-check (Figure 5), so this figure says how the score behaves at the working level and nothing about which designs hold.

### 5.3 What is validated and what is a proxy

| ingredient | status | evidence |
|---|---|---|
| a~i~ is the true slope of ddE for a vanishingly small charge at site i | **validated** | finite-difference checks at three sites pass at both levels of theory |
| a~i~ at the working level | **done** | recomputed at CAM-B3LYP-D3BJ/def2-SVPD (D33 stage A); correlation with the old matrix 0.98, so the level matters |
| a~i~ in the larger basis set | **agrees** | at def2-TZVPD the coefficient differs from the working-level one by 0.05 kcal/mol per e (root mean square) and 0.21 at most; of the 1596 sites where it is 1 or more in size, 1595 agree within 15 % and none changes sign (measured, D47) |
| the size: ddE = sum of a~i~ × q~i~ for real charges | **a proxy** | at the working level the measured ddE of the six designs of 17 November is 1.03 to 1.34 times the prediction; for six single charges of +1.00 e it misses by -0.90 to +0.53 kcal/mol (derived, D43). For D56's 18 survivors: "the measured lowering is 1.03 to 1.17 times the first-order score the search ranked by" (Amendment 13) |
| the charges add | **a proxy** | the pair at 1.00 e gives -11.73 kcal/mol; its two charges run one at a time sum to -11.02 (measured, D43; "Reported, not interpreted"). The negative one, run alone, leaves the dianion METASTABLE |
| the order of designs | **supported, weakly** | the six designs come in the same order by prediction and by measurement at the working level (derived), but all six share two sites and four do not pass the cross-check |
| whether a design is reliable | **not in the score** | measured for each design, tests 1 to 4, now in both basis sets |
| whether the dianion stays bound | **not in the score** | measured for each design, test 5. The "sum to zero or more" rule is a hypothesis: not falsified on 12 conditions, and "not falsified is not established". In D56 it is the first thing to give way as charges are added (section 6) |
| the force a design adds, at first order (map F) | **validated** | for each of D56's 18 survivors the map's force on the 24 atoms at the reactant differs from the directly computed one by 0.054 to 0.110 of its size (relative RMS), under the tolerance of 0.25 fixed beforehand (D58) |
| the hold on the last electron, at first order (map E) | **fails its check, not used** | against D56's 54 measured values the map is off by up to 3.259 eV, and by +1.031 eV on average, where the tolerance was 0.15 eV (D58) |
| whether a positive charge will take an electron | **an estimate was tested and is not adopted** | S, formed from the two potential maps at no cost, estimates what it would cost an electron to move from the dianion to a charge. On single charges it was borne out at 4 of 4 (D47). On 44 further runs, single charges and arrangements, it made 28 predictions, of which 27 were borne out and 1 was not, and for 16 runs it made none: "S DOES NOT SEPARATE what the runs did" (D48). It is not put forward for arrangements |
| whether a lowering comes from the transition state or the reactant | **not tested** | D25 pre-registered this test; I found no committed result |
| the same search at another functional | **supported, at first order** | with the map at ωB97X-V/def2-SVPD D56's search places 17 of its 27 designs again; with the committed map at B3LYP-D3BJ/def2-SVP it places 3 of 27, and its best designs give up 0.06 to 0.29 kcal/mol on the working map (derived; D60, Amendment 14) |
| the search against random designs | **supported, at first order** | each of D56's 27 designs scores lower than all 10 000 random designs of each of two kinds at its number of charges (D60) |
| other frames | **not tested** | one frame |

### 5.4 What it can and cannot claim

**It can** propose candidates cheaply and put them in a sensible order. It is a proxy for the search.

**It cannot** say that a candidate is reliable, that the dianion stays bound, that no charge takes an electron, or what the lowering is. Each of those is measured. So the work runs in stages:

1. the optimiser proposes designs;
2. each is **measured** at the working level and, since Amendment 9, at CAM-B3LYP in def2-TZVPD, and must pass the five tests at both (D56 did this for its 27);
3. the survivors are **tested** with functions at their positive charges and behind the wall, and what is found is reported beside them (D59, D61);
4. a pilot of three survivors is **relaxed**, to see how much of a frozen lowering is left;
5. survivors are **confirmed** at the other cross-check levels, and a coupled-cluster reference is run on two of them before any level is adopted for reporting.

### 5.5 How it could be improved

These are proposals, not decisions, except where a date is given.

- **A rule for arrangements.** None exists, and none is sought now: charges that are safe one by one are not always safe together (section 8), S is not that rule, and Amendment 11 measures every design instead. D53 found one to six positive charges of 0.25 e holding together at two levels.
- **Search properly.** Done in D56: the committed optimiser, with each design proved optimal under its rules.
- **Put the force into the choice.** The first-order force map passed its check (D58), so the second search carries a rule on it, at a ladder of limits (Amendment 13, item 6).
- **Put binding into the choice.** The first-order map of the hold on the last electron failed its check (D58), so that rule does not enter; the fifth test stays a measurement of each design.
- **Add the polarisation term**, so the prediction stops falling short.
- **Measure the safe surface and rebuild the grid on it.** Set aside by Amendment 11, which runs the search on the committed grid and measures every design.
- **Repeat the search at a second functional** and compare the arrangements (Amendment 9). Done at first order: D60 (section 6.6).
- **Relax.** The pilot of three survivors is next (section 6.7).
- **More frames.**

## 6. The search on the committed grid, and what followed it

### 6.1 What was searched, and how each design was tested

D56 was pre-registered on 24 November with Amendment 11, before the search had been run on the committed coefficients. Its settings, fixed then:

| setting | D56 |
|---|---|
| sites | the committed grid of frame 42436: 1488 of its 2626 sites admit a charge of 0.25 e |
| coefficients | the working-level map, one frame |
| largest charge at a site | 0.25 e |
| spacing | 3.25 Å between any two charges |
| sum of the charges | zero or more |
| numbers of charges | 3, 4, 5, 6, 8, 10, 12, 15 and 20 |
| designs kept at each | the best three, each proved optimal under the rules |
| what is run for each design | the dianion and the monoanion with its charges, at R and TS, at the working level and in def2-TZVPD: 8 runs, 224 in all with the controls |

Each design is then given its word by the rule of Amendment 9, quoted in section 3.5: SURVIVOR only if it passes the five tests at the working level and, in def2-TZVPD, is reliable, keeps the last electron, and has a ddE within 15 % of its working-level ddE. No basis function stands at a charge and no wall is in any run: those tests come afterwards and are reported beside the word (Amendment 11).

### 6.2 What it found

Measured (D56; the ranges are derived from its committed table, Figure 7).

| charges | sum of the charges (e) | the three designs | ddE, working level (kcal/mol) | ddE, def2-TZVPD (kcal/mol) | energy to remove the last electron at R, working level (eV) |
|---|---|---|---|---|---|
| 3 | +0.25 | SURVIVOR, all three | -4.30 to -4.36 | -4.26 to -4.32 | +1.72 to +1.84 |
| 4 | 0.00 | SURVIVOR, all three | -5.77 to -5.78 | -5.71 to -5.72 | +0.94 to +1.06 |
| 5 | +0.25 | SURVIVOR, all three | -6.93 to -6.96 | -6.86 to -6.88 | +1.46 to +1.53 |
| 6 | 0.00 | SURVIVOR, all three | -8.17 to -8.32 | -8.09 to -8.23 | +0.68 to +0.76 |
| 8 | 0.00 | SURVIVOR, all three | -10.76 to -10.83 | -10.65 to -10.74 | +0.41 to +0.49 |
| 10 | 0.00 | SURVIVOR, all three | -12.35 to -13.02 | -12.20 to -12.89 | +0.20 to +0.24 |
| 12 | 0.00 | FAILS, all three, on the fifth test | -13.94 to -14.64 | -13.80 to -14.50 | -0.01 to +0.05 |
| 15 | +0.25 | FAILS, all three, on the four tests in def2-TZVPD | -16.33 to -16.61 | unreliable | +0.29 to +0.43 |
| 20 | +0.50 | FAILS, one; OPEN, two | -19.50 to -20.13 | one unreliable, two not measured | +0.42 to +0.50 |

For scale, without charges the barrier is 26.82 kcal/mol at the working level and 25.70 in def2-TZVPD, and the energy to remove the last electron is +1.25 eV at the reactant and +0.77 at the transition state (working level).

![Figure 7](figs/S9_search.png)

**Figure 7.** The search on the committed grid (D56) and the force its survivors add (D58). Three designs at each number of charges, the best-ranked on the left of each group; every charge is 0.25 e. A: the change in the barrier at the working level (filled) and in def2-TZVPD (open), drawn where the four tests at that level do not fail; black designs are survivors. B: the energy to remove the dianion’s last electron, at the reactant (circles) and the transition state (triangles), at each level, drawn where the four tests at that level do not fail. Below the dashed line the dianion is METASTABLE and the fifth test fails. C: the gradient each of the 18 survivors adds to the substrate, at the reactant and the transition state, as the root mean square over the 72 components (D58). Measured, from the committed tables d56_designs.tsv, d56_survivors.tsv and d58_forces.tsv.

- **Up to ten charges all 18 designs survive.** In def2-TZVPD their ddE lies within +0.04 to +0.14 kcal/mol of the working level’s (derived), much as the two basis sets agreed for the two designs of 17 November that did not fail (section 7).
- **The largest lowering is S_n10_k1’s**, -13.02 kcal/mol at the working level and -12.89 in def2-TZVPD. The survivors’ charges stand 3.13 to 3.21 Å from the nearest atom, and carry 0.50 to 1.25 e of positive charge in all.
- **The hold on the last electron falls as charges are added**, from +1.72 to +1.84 eV at the reactant with three charges to +0.20 to +0.24 with ten and about zero with twelve (Figure 7, panel B). At five charges, where they sum to +0.25 e, it holds more firmly than at four and six, where they sum to zero. Amendment 13 on how sharp the line is: "these runs do not resolve where between ten and twelve charges the hold is lost, or whether it is lost within that range at all".
- **With fifteen charges the larger basis set shows a failure the smaller one does not.** In def2-TZVPD the dipole at the reactant rises to 3.33 to 3.43 times the control’s and the ddE turns positive, +12.10 to +16.13 kcal/mol. It is the same pattern as the designs of 17 November (section 7).
- **With twenty charges** two runs in def2-TZVPD reached their time limit and are not measured, so those two designs are OPEN; the third fails as the designs of fifteen do.
- **D56 left out the shell’s term, and did not say in which direction.** The committed charge model gives each charge a Lennard-Jones shell. In a frozen run that is the same electronic calculation as a bare charge, and the shell adds only a classical energy, which D56 set to zero. With it, Amendment 13’s Note 1 finds every lowering of D56 smaller by 0.17 to 0.33 kcal/mol. That is 1.0 to 4.4 per cent of the lowering (derived from the note’s own table; the note’s text says 2 to 4 per cent, which does not cover its smallest and largest cases): "So leaving it out was TOWARD A LOWER BARRIER by that much." It changes no word of D56, no best-ranked survivor at any number of charges, and not the ten survivors with the largest lowering. The numbers in this section are D56’s, without the term.
- **The first-order score still falls short.** "Among the 18 survivors the measured lowering is 1.03 to 1.17 times the first-order score the search ranked by" (Amendment 13).
- **Two looks at the running jobs** on 24 November are disclosed in D56 NOTE 1. Every number here is the committed reader’s.

D56’s own words on what a survivor is: "A SURVIVOR is not a result. The cross-check of AMENDMENT 7 and the reference of AMENDMENT 8 have not been run on it."

### 6.3 The force each survivor adds (D58)

A charge beside a frozen molecule also pushes on its atoms. D58 computed, for each of the 18 survivors, the gradient of the energy on the 24 atoms with the charges and without them, at the reactant and the transition state. G_add is the root mean square of the difference over the 72 components, as the criteria define it.

- **Each survivor adds 2.4 to 8.8 kcal/mol/Å**, rising with the number of charges: 2.4 to 3.1 with three, 4.4 to 5.6 with six, 6.4 to 8.8 with ten (Figure 7, panel C). The largest single component on any atom is 8.8 to 30.7 kcal/mol/Å (measured).
- **For scale only, not as a bound**, the criteria record that a relaxed design of the GOCAT method reaches gradients "around 1 kcal mol-1 A-1", on the total gradient and not the added one. The criteria also record that "Neither published threshold is carried over."
- **The map of the force passes its check.** The first-order force, formed from potentials at the sites, agrees with the direct gradient for every survivor: relative RMS 0.054 to 0.110 against a tolerance of 0.25 fixed beforehand. So the second search can carry a rule on the force taken from the map, without a calculation for each design.
- **The map of the hold on the electron fails its check.** Against D56’s 54 measured energies to remove the last electron it is off by up to 3.259 eV, and predicts too much by +1.031 eV on average, against a tolerance of 0.15. It is reported and not used.
- **The Lennard-Jones shell the pilot will put on each charge** adds 0.06 to 0.15 kcal/mol/Å by itself (measured from the committed parameters); its part is small beside the charges’.

### 6.4 Behind the wall (D57)

D57 (Amendment 12) put a wall, a core potential that keeps electrons off a charge, on the positive charges of the best-ranked design that is not a survivor, at each number of charges that has one: S_n12_k1, S_n15_k1 and S_n20_k1, the last also with every charge walled. It ran the helium set and the neon set. The wall stands on the positive charges only by Jessica’s decision, which Amendment 12 says rests "ON THE PRACTICE OF TWO WORKS OF ONE GROUP, NOT ON A TEST". And: "It is reported beside the design's bare reading and it is nothing more."

- **S_n12_k1 still fails behind both walls**, on the fifth test, as it does bare.
- **S_n15_k1 would be a survivor behind both walls**, where bare it fails in def2-TZVPD: ddE -16.23 and -16.10 kcal/mol (working level and def2-TZVPD) behind the helium wall, -15.88 and -15.96 behind the neon wall. That changes nothing of its word.
- **S_n20_k1 stays open** behind both walls, its four tests INCONCLUSIVE.
- **The wall by itself, with no charge on it,** changes the barrier by -0.52 to +0.29 kcal/mol, and raises the largest atomic charge by 0.0103 e at most.
- **The wall against real ions was not formed.** At one site, a whole charge as a bare point, behind each wall and behind a published capping potential, was to be set against Na+ and K+ with their ghost controls. The two runs of the bare charge at the reactant did not finish: ORCA found their wavefunction unstable and was solving again when the run’s time limit stopped it (1800 s at the working level, 5000 s in def2-TZVPD; the committed job logs and outputs). So the reading is not formed at either level, and by the pre-registration’s rule a reading that is not formed counts against the wall: "THE HELIUM WALL, by section 3 of the pre-registration: NOT SUPPORTED (the reading was not formed at SV and TZ)". Every other run of that measurement ended normally.

What follows from it. Amendment 13’s Note 1 gives the pilot "a second arm behind the helium wall only if D57's measurement against real ions supports the wall by the reading its own pre-registration fixes", so the pilot has none. The time limits were Claude’s. Measuring the two runs again, in a new diagnostic with a longer limit, could move the word only toward SUPPORTED; that is the direction of a lower barrier, and it is Jessica’s decision (front, points to settle).

### 6.5 The ten survivors with the largest lowering: functions at their positive charges (D61) and a helium wall (D59)

A11.5 item 5 sends the ten survivors with the largest lowering to two tests, each "Reported beside D56's word and nothing more". D59 ran both on 25 November. Its runs with the functions stopped in ORCA’s start-up (D59 NOTE 1), so D59 settled nothing with functions: "WITH FUNCTIONS: 0 of 10 take electrons, 0 hold, 10 not settled." D61 made those 120 runs again with each ghost centre 0.01 Å beyond its charge and read them by D59’s reading, word for word, with D59’s 46 runs without functions. Every run was measured.

**How a run with functions is read** (D59’s pre-registration, D53’s reading). A run with functions at the positive charges is read against the same design’s control with ghost functions only. It TOOK ELECTRONS when a test fires or "the run LEFT THE ATOMS": the Löwdin charges of the 24 atoms rise by 0.25 e or more over the control’s. The energy gained by it is (F minus GF) minus (N minus GN), the last two being the runs without functions. A run that took electrons is set against L = 0.3127 eV at the working functional and L2 = 0.1151 eV at ωB97X-V, because "a run that takes electrons with a gain in energy not larger than a few times that error is not settled at this level alone." The two levels give one word at each state, and a design HOLDS only if both states hold at both levels. Hartree-Fock is reported beside and changes no word.

Measured (D61, D59; the bare ddE is D56’s, without the shell’s term).

| design | bare ddE, working / TZ (kcal/mol) | at R | at TS | with functions (D61) | behind the helium wall (D59): ddE, working / TZ |
|---|---|---|---|---|---|
| S_n10_k1 | -13.02 / -12.89 | NOT DECIDED: working functional took 0.8321 e, gain -0.3158 eV, above L; ωB97X-V not decided | NOT DECIDED (ωB97X-V not decided) | NOT SETTLED | -12.8243 / -12.6768, SURVIVOR |
| S_n10_k3 | -12.74 / -12.62 | NOT DECIDED: took 0.8772 e, -0.3749 eV, above L; ωB97X-V not decided | NOT DECIDED (ωB97X-V not decided) | NOT SETTLED | -12.5440 / -12.4059, SURVIVOR |
| S_n10_k2 | -12.35 / -12.20 | TAKEN AT THE WORKING FUNCTIONAL ONLY: 0.5184 e, -0.0910 eV, within L | HOLDS AT BOTH LEVELS | NOT SETTLED | -12.0835 / -11.9705, SURVIVOR |
| S_n08_k1 | -10.83 / -10.73 | TAKEN AT THE WORKING FUNCTIONAL ONLY: 0.3521 e, -0.0262 eV, within L | HOLDS AT BOTH LEVELS | NOT SETTLED | -10.6182 / -10.5217, SURVIVOR |
| S_n08_k3 | -10.83 / -10.74 | TAKEN AT THE WORKING FUNCTIONAL ONLY: 0.4376 e, -0.0607 eV, within L | HOLDS AT BOTH LEVELS | NOT SETTLED | -10.6066 / -10.4855, SURVIVOR |
| S_n08_k2 | -10.76 / -10.65 | HOLDS AT BOTH LEVELS | HOLDS AT BOTH LEVELS | HOLDS | -10.5458 / -10.4467, SURVIVOR |
| S_n06_k1 | -8.32 / -8.23 | HOLDS AT BOTH LEVELS | HOLDS AT BOTH LEVELS | HOLDS | -8.1582 / -8.0693, SURVIVOR |
| S_n06_k2 | -8.31 / -8.22 | HOLDS AT BOTH LEVELS | HOLDS AT BOTH LEVELS | HOLDS | -8.1255 / -8.0326, SURVIVOR |
| S_n06_k3 | -8.17 / -8.09 | HOLDS AT BOTH LEVELS | HOLDS AT BOTH LEVELS | HOLDS | -8.0103 / -7.9288, SURVIVOR |
| S_n05_k2 | -6.96 / -6.88 | HOLDS AT BOTH LEVELS | HOLDS AT BOTH LEVELS | HOLDS | -6.8092 / -6.7286, SURVIVOR |

- **The working functional and ωB97X-V disagree at the reactant for the five designs with the largest lowering.** At the working functional their 24 atoms give up 0.35 to 0.88 e to the functions; at ωB97X-V the same runs give up 0.03 to 0.05 e (derived from d61_functions.tsv). Hartree-Fock finds no design taking electrons. At the transition state every design holds at the working functional, and the only words not decided there are ωB97X-V’s for S_n10_k1 and S_n10_k3.
- **Why ωB97X-V did not decide for S_n10_k1 and S_n10_k3.** In those runs ORCA raised its level shift during the SCF (`LevelShift set to 1.000 Eh`), and the committed reader withholds the gap test of such a run, so the run is not decided although its atoms gave up only 0.05 to 0.06 e. Their gains at ωB97X-V are -0.0057 to -0.0059 eV.
- **For S_n10_k1 the gain is above L by 0.0031 eV** (derived), close to the line; for S_n10_k3 by 0.0622 eV.
- **The direction.** Every design that is not settled lies at the top of the ranking; every one that holds lowers the barrier by 10.76 kcal/mol or less at the working level. What D61 found tells against the largest lowerings, the direction of a higher barrier. D52 found that CAM-B3LYP binds an electron shared by charges of 0.25 e too strongly (section 8.4), which is one reason the working functional may take electrons where ωB97X-V does not; it is not tested here.
- **Behind the helium wall all ten are SURVIVOR at both levels**, and each lowering is smaller than bare by 0.15 to 0.26 kcal/mol at the working level and 0.15 to 0.25 in def2-TZVPD (derived). The wall alone, with no charge on it, changes the barrier by +0.0153 to +0.1117 kcal/mol and moves the Löwdin charge of the most charged atom by 0.0045 e at most. Reported beside D56’s bare reading: "No design is named, kept or dropped on it."

### 6.6 The search at a second functional, and against random designs (D60)

D60 (Amendment 14) asked two things of the map D56's search ranks by, at first order, on the same frame and grid and under D56's rules: does the search place the same designs when the map is computed at another functional, and do D56's designs beat random placement? Its control measured the two runs of the working map again, with energies within 1e-11 Eh of D33's, and its runs at ωB97X-V reproduced D37's, so "THE MAP AT wB97X-V IS USED." Its first search, with the working map, gave D56's 27 designs again (gate GV.6).

- **The maps** (measured, over the 1488 sites that admit a charge, kcal/mol per e). Against the working map, the map at ωB97X-V/def2-SVPD has Pearson 0.9977, Spearman 0.9920, mean difference 0.1488 and largest 0.3262; the committed B3LYP-D3BJ/def2-SVP map has Pearson 0.9763, Spearman 0.9358, mean difference 0.4588 and largest 1.1773.
- **At ωB97X-V the designs are PARTLY THE SAME at all nine numbers of charges, and 17 of D56's 27 are found again** (two of three at each number, one of three at 20). At seven numbers the search's best design is D56's first-ranked; at 12 it is S_n12_k2, and at 20 it is a new design, which scores 0.0661 kcal/mol less than S_n20_k1 on the working map (derived).
- **At B3LYP they are DIFFERENT DESIGNS at seven numbers and PARTLY THE SAME at 5 and 6; 3 of 27 are found again.** Scored on the working map, its best design at each of the seven gives up 0.0617 to 0.2851 kcal/mol against D56's best (derived). The two maps differ in the basis set as well as the functional, so this comparison mixes the two; the one at ωB97X-V changes the functional alone.
- **Every one of D56's 27 designs beats 100.00 % of the random designs of both kinds** (10 000 of each at each number of charges, seed 20261125). Kind (i) puts charges of 0.25 e, each with a random sign its site admits, on random sites with the spacing; kind (ii) puts the best charges D56's rules allow on random sites. D56's weakest design at each number lies 0.5733 to 4.7051 kcal/mol below the best random design of kind (ii) (derived), and 4716 to 9979 of the 10 000 of kind (ii) at each number carry a charge smaller than 0.25 e, which none of D56's designs does.
- **What it cannot say.** D60's pre-registration: "A design that a map places is placed by that map, not measured at that functional; a design found again at another map is not confirmed by that, and one not found again is not refuted by that." Its direction: "no reading here moves a reported barrier."

![Figure 8](figs/S10_second_functional.png)

**Figure 8.** D60 at first order (derived from `d60_designs.tsv` and `d60_null.tsv`). A: of D56's three designs at each number of charges, how many the search with each other map places again, with the same sites and the same charges. B: each other map's best design, scored on the working map, minus D56's best there (kcal/mol); zero means the same design or an equal score. C: D56's three designs at each number of charges against 10 000 random designs of each kind; each bar runs from the median random design to the best one.

### 6.7 What is not known yet

- **Whether any survivor’s lowering survives relaxation.** No survivor has been relaxed. In the earlier work bare charges in a geometry optimisation collapsed onto the substrate: "6 of 8 imploded to 0.01-1.06 A atom-to-charge" (recorded in Amendment 13’s Note 1). So the pilot will hold each charge in place with the committed sphere model, "sphere R* 1.824 A eps 0.170 kcal/mol", relax the reactants first, and go on to a transition state only for a design whose reactant held. It answers one question: how much of a frozen lowering is left, and whether the added gradient foretells the loss.
- **Whether the five survivors that are not settled with functions keep their electrons** (section 6.5), and whether the working functional or ωB97X-V is right where they disagree.
- **Whether the designs that the other maps place measure as they score.** D60 placed and scored them at first order; none was run.
- **The cross-check and the coupled-cluster reference** have not been pre-registered: Amendment 13 waits for the pilot and the second search, "so that those costly runs are spent on designs that are still candidates".

## 7. The six designs of 17 November and the cross-check

Six designs passed all five tests at the working level (D43, measured). Each is a set of n point charges of one size, some positive and some negative. The sum of the charges is what is left when the signs are counted: +0.50 and -0.50 sum to 0.00. A site is a numbered point of the grid.

| design | n | each charge (e) and its site | sum of the charges (e) | ddE (kcal/mol) | first-order prediction (kcal/mol) | detachment energy, R / TS (eV) |
|---------|--|--------------------------------------|-------|-------|--------|---------|
| B_n02_q0.50 | 2 | +0.50 at site 1124; -0.50 at site 557 | 0.00 | -5.42 | -5.25 | +0.82 / +0.97 |
| B_n02_q0.75 | 2 | +0.75 at site 1124; -0.75 at site 557 | 0.00 | -8.32 | -7.87 | +0.51 / +0.80 |
| B_n02_q1.00 | 2 | +1.00 at site 1124; -1.00 at site 557 | 0.00 | -11.73 | -10.50 | +0.23 / +0.61 |
| B_n03_q0.75 | 3 | +0.75 at site 1073; +0.75 at site 1124; -0.75 at site 557 | +0.75 | -14.25 | -10.89 | +2.01 / +2.45 |
| B_n05_q0.50 | 5 | +0.50 at site 1073; +0.50 at site 1107; +0.50 at site 1124; -0.50 at site 534; -0.50 at site 557 | +0.50 | -15.31 | -11.44 | +1.25 / +1.71 |
| B_n11_q0.25 | 11 | +0.25 at site 1005; +0.25 at site 1052; +0.25 at site 1073; +0.25 at site 1107; +0.25 at site 1124; +0.25 at site 1359; -0.25 at site 417; -0.25 at site 534; -0.25 at site 557; -0.25 at site 1421; -0.25 at site 1460 | +0.25 | -9.60 | -7.91 | +0.53 / +0.89 |

For scale, the charge-free barrier at this level is 26.82 kcal/mol, and the bare dianion's detachment energy is +1.25 eV at the reactant and +0.77 at the transition state.

**The cross-check (D44, committed 20 November).** The six were run at the five cross-check levels: 196 calculations. A design passes at a level if it passes the four reliability tests there, the dianion is bound at both states, and its ddE lands within 15 % of its working-level value. The result: "Of the 6 designs. Pass the cross-check: 0. Do not pass: 4. Incomplete: 2."

| design | working level | CAM-B3LYP def2-TZVPD | PWPB95 def2-SVPD | PWPB95 def2-TZVPD | revDSD def2-SVPD | revDSD def2-TZVPD | D44's word |
|---|---|---|---|---|---|---|---|
| B_n02_q0.50 | -5.42 | -5.38 | -5.07 (open) | -5.03 (open) | -4.91 | -4.87 | incomplete |
| B_n02_q0.75 | -8.32 | **fails** | -7.80 (open) | -7.67 (open) | -7.59 | -8.38 | does not pass |
| B_n02_q1.00 | -11.73 | **fails** | -11.72 (open) | not measured | -11.00 | **fails** | does not pass |
| B_n03_q0.75 | -14.25 | **fails** | -15.00 (open) | not measured | -13.72 (open) | **fails** | does not pass |
| B_n05_q0.50 | -15.31 | **fails** | -14.30 (open) | not measured | -14.03 | **fails** | does not pass |
| B_n11_q0.25 | -9.60 | -9.51 | -8.87 (open) | -8.77 (open) | -8.64 | -8.52 | incomplete |

ddE in kcal/mol, measured. *Open* means a test could not be run or read there, so nothing is established either way. Where a level fails, the number it prints is not a barrier effect and is left out.

![Figure 5](figs/S7_crosscheck.png)

**Figure 5.** The cross-check of the six designs (D44), with CAM-B3LYP at def2-QZVPPD for two of them (D47). Each design has a row, and within it each level has its own line, in the order of the legend. A: the change in the barrier, drawn only where the level does not fail, with the window of 15 % either side of the working-level value. B: the first reliability test, the largest rise of an atomic charge over the charge-free calculation. Filled symbols pass at that level, open ones are not established, and a cross fails. The four designs that fail do so in def2-TZVPD, with a rise of about one electron; B_n02_q0.75 fails at CAM-B3LYP in def2-TZVPD on the dipole test, with a rise just under the flag. The revDSD-PBEP86-D4 values are on the restricted solution (section 3.3). Measured; the windows and the larger of the two rises are derived.

- **Four designs fail in the larger basis set.** At CAM-B3LYP or revDSD-PBEP86 in def2-TZVPD, or both, the charge on one atom rises by about a whole electron (Figure 5, panel B) and the ddE changes completely: for B_n02_q1.00 it is +13.29 kcal/mol where the working level gave -11.73. B_n02_q0.75 fails at CAM-B3LYP in def2-TZVPD alone, on the dipole test, and passes at revDSD-PBEP86 there.
- **The smaller basis set shows none of it.** No design carries a flag at any functional in def2-SVPD.
- **Two designs fail at no level that could be read.** For the pair of 0.50 e and the eleven charges of 0.25 e the six levels agree within 0.55 and 1.08 kcal/mol, and one basis step further up, at def2-QZVPPD, CAM-B3LYP gives -5.39 and -9.50 (D47). They are incomplete because of PWPB95: ORCA 6.0.1 cannot run the stability check with that functional, so tests 4 and 5 are not established at its two levels.
- **revDSD-PBEP86.** Its numbers are on the restricted solution, with the wording given in section 3.3.
- **What agreement would not have shown.** Amendment 7: "Agreement of three functionals is not that measurement." No coupled-cluster ddE exists.

**What followed.** Amendment 9 (20 November) put the larger basis set into the test of every new design, dropped the coupled-cluster run that was planned on two of these six, and put the rebuild of the grid before the reference (section 3.5). The tests of section 8 then asked why the four failed, and whether the two that did not fail really hold.

**Where the two stand today.** For the eleven charges of 0.25 e, Amendment 10 (23 November): "B_n11_q0.25 IS NOT CARRIED FORWARD AS A DESIGN THAT HOLDS." Its standing is "DOES NOT HOLD AT THE WORKING FUNCTIONAL WITH FUNCTIONS AT ITS CHARGES; NOT SETTLED AT A SECOND LEVEL" (section 8.3). The pair of 0.50 e did not take an electron in the one test made of it, which is weak at that size (section 8.2); Jessica decided on 23 November not to test old arrangements further, since designs would be made again by a search. D54 then read the eleven-charge design as taking electrons at the reactant at both levels (section 8.5), and Amendment 11 set every old arrangement aside: "THE OLD ARRANGEMENTS ARE SET ASIDE."

## 8. When a bare positive charge takes an electron

The four failures of section 7 all show an electron leaving the substrate's atoms in the larger basis set. D47 to D54 (21 to 24 November) asked when a bare positive charge does that, and how far the working functional can be trusted to say so. Figure 6, at the end of this section, shows the four sets of measurements.

**The tool.** A basis set describes electrons with functions centred on the atoms. A point charge has no functions of its own, so a calculation can put an electron at the charge only if some atom's functions happen to reach it. To ask the question properly, functions are placed at the charge itself, on a *ghost atom*: a centre with basis functions and no nucleus and no electrons. A run then *took electrons* if 0.25 e or more left the substrate's atoms, the threshold of test 1.

### 8.1 One charge

All at CAM-B3LYP in def2-TZVPD, with the hydrogen functions of that basis set at the charge (measured; D47, D48).

- **+1.00 e at site 1124 fails in plain def2-TZVPD.** +0.75 e passes all four tests there, and with functions at the charge 0.93 e leaves the atoms at the reactant. The plain pass was a pass because the basis set did not reach.
- **Distance did not help +1.00 e.** Placed 5, 7 and 9 Å from the substrate it is not flagged in plain def2-TZVPD. With functions at it, at 9 Å, a whole electron (1.00 e) leaves the atoms.
- **The size is what matters.** At four sites the charge was raised in steps of 0.05 e (Figure 6, panel A). The last size that did not take electrons was 0.45 to 0.60 e and the first that did was 0.50 to 0.65 e, depending on the site and on the state; the transition state gives way at the same step as the reactant or one step earlier.
- **An estimate agrees roughly.** From the potential maps, the size at which one positive charge and the dianion would hold an electron equally is 0.50 to 0.75 e over the sites at the reactant (median 0.62) and 0.45 to 0.72 e at the transition state (median 0.59) (estimate, D47).

### 8.2 Were the functions good enough?

A test with functions at the charge is only as good as those functions. D49 to D51 measured them on the simplest case, one electron at one charge and nothing else, where the exact answer is known: 13.6057 × q² eV (Figure 6, panel B).

- **The hydrogen functions of def2-TZVPD are too compact for small charges.** At 0.25 e they bind nothing: "These functions do not hold an electron at a charge of that size." At 0.50 e they fall 0.37 eV short. So a run that did not take electrons at 0.50 e or below in D47 and D48 is weaker evidence than it looks.
- **A better set was built.** Set X2 adds two more diffuse shells. With Hartree-Fock it is within 0.006 eV of exact at 0.25 e and closer above (D50, D51).
- **The integration grid matters at a ghost atom.** ORCA's default grid loses 0.036 eV of the binding at 0.25 e (derived from D51's ladder). D51's rule gives the setting to use: "THE GRID FOR A GHOST ATOM: rung i12 (IntAcc 12.000)".
- **The functional has an error of its own.** For one electron at one charge CAM-B3LYP binds too strongly by 0.051 to 0.063 eV between 0.25 and 0.60 e (Figure 6, panel C): "From 0.25 e up, where the grid is converged, the functional lies at most +0.0631 eV from exact (0.40 e)." No set of functions can mend that, and D51 wrote the consequence down before the next run: "a run that takes electrons with a gain in energy not larger than a few times that error is not settled at this level alone."

### 8.3 Charges together

Measured, functions at every positive charge (Figure 6, panel D).

- **Five charges of 0.50 e (B_n05_q0.50) take almost a whole electron**, 0.92 e at the reactant and 0.91 e at the transition state. D48's pre-registered reading of that outcome: "charges that S calls safe alone are not safe together, as S says, and a rule on single charges, by size or by distance, cannot stand in for S of the arrangement." S is the estimate of section 5.3.
- **A neighbour of opposite sign helps, and does not make a charge safe.** Alone, +0.60 e at site 1124 takes 0.52 e at the reactant and 0.63 e at the transition state. With -0.60 e beside it, it takes 0.02 e and 0.33 e. At 0.65 e the pair takes electrons at both states.
- **One charge of +0.25 e, with set X2: nothing moves** (0.002 and 0.003 e). By D50's own rule this run is not counted as a test of capture, because the rule that was to choose its functions chose none; D51 has since measured set X2 adequate from 0.25 e up.
- **Eleven charges of 0.25 e (B_n11_q0.25), with set X2: 0.52 e leaves the atoms at the reactant** and 0.04 e at the transition state. With the compact def2-TZVPD functions the same design had shown nothing (0.015 and 0.020 e). The energy gained at the reactant is 0.0898 eV. With the functions in place its ddE is -7.57 kcal/mol where it was -9.51 without them.

D50's pre-registration had fixed what such an outcome means: "the one design of this size that passes A9.4 does not hold when the basis can hold an electron at its charges, and what fails is charges together."

**How far that goes.** The gain, 0.0898 eV, is 1.4 times CAM-B3LYP's own error for one electron at one charge (0.0631 eV). So by D51's sentence the capture is not settled at this level alone, and Amendment 10 says the design "is not called refuted either". A second level of theory has to be asked, and D52 was run to choose it.

### 8.4 One electron shared by several charges

D52 (committed 23 November) put one electron, with no substrate, among charges of +0.25 e at the positive sites of the eleven-charge design. Functions that can hold an electron (sets X2 and X3 of section 8.2) stood at all six sites in every run. The energy that binds the electron was computed beforehand in a second program, in a basis set large enough to be taken as the limit; it is not a measurement in ORCA.

| system | charges of +0.25 e at sites | distances between them (Å) | computed limit (eV) | CAM-B3LYP minus the limit (eV) | ωB97X-V minus the limit (eV) |
|---|---|---|---|---|---|
| s1 | 1124 | - | 0.8504 | +0.0507 | +0.0158 |
| pc | 1073, 1052 | 3.28 | 2.0967 | +0.0637 | +0.0316 |
| pf | 1124, 1052 | 6.17 | 1.5712 | +0.1042 | +0.0151 |
| t3 | 1124, 1073, 1107 | 3.29 to 3.41 | 3.3705 | +0.0617 | +0.0384 |
| f4 | 1124, 1073, 1107, 1052 | 3.28 to 6.17 | 4.2747 | +0.0663 | +0.0362 |
| x6 | all six | 3.28 to 11.54 | 5.0261 | +0.0656 | +0.0351 |

The two right-hand columns are measured, in the larger set of functions on a fine grid (Figure 6, panel C). The limit shows why charges together matter: one charge of 0.25 e binds an electron by 0.85 eV, four close together by 4.27 eV.

- **The set-up holds.** ORCA and the second program agree at all 12 Hartree-Fock runs. The functions fall short of the limit by 0.003 eV at most, and the grid is converged at IntAcc 12. Rule A gives set X2 with IntAcc 12 on the ghost atoms.
- **CAM-B3LYP holds the shared electron too strongly**, by 0.05 to 0.10 eV, most for the two charges that lie farthest apart. The second program had given 0.1045 eV for that pair beforehand; ORCA gives 0.1042.
- **ωB97X-V is nearer the limit**, within 0.04 eV at every system, and Rule B names it: "RULE B GIVES: wB97X-V."
- **The bar for a capture.** Rule C takes three times CAM-B3LYP's largest error: "RULE C GIVES: L = 0.3127 eV." The capture of section 8.3 gained 0.0898 eV, well under it.
- **Two candidates were not measured.** revDSD-PBEP86 ran at none of its 18 runs: ORCA stops in its dispersion correction when the system has no real atom (read from the outputs afterwards). ωB97M-V did not converge in the larger set, and in the smaller one it holds the electron too weakly by up to 0.29 eV (derived). The result's own caution: "A candidate that ORCA did not run for one electron is not thereby unfit for the dianion, and one that lies near the limit here is not thereby right there."

One electron among bare charges is not the dianion. The result says so itself: it "does not say what a run of the dianion does".

**A reading, not a result.** Taken together the measurements say that capture belongs to the model and is not a numerical accident: a bare positive charge that is strong enough binds an electron, and a calculation shows it as soon as its basis set can reach the charge. Small basis sets hide it. What is not yet known is where the line lies for small charges close together, and whether a better method than CAM-B3LYP draws it in the same place. D53 asked that, with ωB97X-V beside CAM-B3LYP (section 8.5).

![Figure 6](figs/S8_capture.png)

**Figure 6.** When a bare positive charge takes an electron. All runs are CAM-B3LYP in def2-TZVPD with functions placed at the charge. A: one positive charge at four sites, raised in steps (D48, with one point of D47 at 0.75 e); the star is +1.00 e placed 9 Å away (D47). B: what the functions at the charge fall short of the exact binding energy by, for one electron at one charge, at Hartree-Fock. Above the dotted line the shortfall exceeds the binding energy itself, so the functions hold no electron: the def2-TZVPD hydrogen functions at 0.25 e. C: the functional's own error for one electron, in the larger set of functions: CAM-B3LYP at one charge by its size (D51, left), and CAM-B3LYP and ωB97X-V for several charges of 0.25 e (D52, right; the systems of the table in section 8.4), beside the energy the eleven-charge design gained at the reactant (D50). The bar L of rule C, 0.3127 eV, lies above the panel. D: arrangements, with functions at every positive charge; the two kinds of functions are named at the right. The def2-TZVPD functions under-test charges of 0.50 e and below (panel B). Measured; the exact binding energy and the differences from it are derived.

### 8.5 Charges of 0.25 e together, on the dianion (D53, D54)

D53 (committed 24 November) ran the dianion with charges of 0.25 e at sites of the eleven-charge design, at the two levels D52 had chosen, with set X2 and the fine grid at every positive charge: seven arrangements, from one positive charge to all eleven charges, at the reactant and the transition state. All 82 runs are measured, and the second level could be read.

- **One to six positive charges held at both levels**, at both states: "Of the 14 (arrangement, state): HOLDS AT BOTH LEVELS 12". In those runs at most 0.0193 e left the atoms, against the 0.25 e that counts as taking electrons (measured).
- **The eleven-charge design, five of whose charges are negative, was not decided.** At CAM-B3LYP it took 0.5258 e at the reactant onto the functions, as in D50, with a gain of 0.0917 eV; at ωB97X-V a gap could not be read.
- **D54 started ωB97X-V from the solution in which CAM-B3LYP had taken the electrons.** It found a solution in which 0.9755 e had left the atoms, 0.028271 eV below the one reached from its own start: "A CAPTURE SOLUTION, BELOW." Its reading of the design: "at R, TAKES ELECTRONS AT BOTH LEVELS (WITHIN L2 at WXV); at TS, HOLDS AT BOTH LEVELS." Amendment 11 on what the gains mean: "D52 to D54 found the test with functions to turn on 0.03 to 0.09 eV where the second level's own limit L2 is 0.1151 eV, which those levels do not settle."

**What followed.** Amendment 11 (24 November) set the old arrangements aside, ran the search at no more than 0.25 e a charge, and measures every design in place of a rule for arrangements (sections 4 and 6). The test with functions became a test of the survivors, reported beside their word (D59, D61).

## 9. What can be said today, and what cannot

**Can be said, each with its scope** (one frame, gas phase, frozen geometries, bare point charges):

- B3LYP is unsuitable for this dianion. CAM-B3LYP and two double hybrids are within 3 kcal/mol of a coupled-cluster barrier at def2-TZVPD, and each of that benchmark's three approximations moves it by less than 1 kcal/mol.
- The bare dianion holds its second electron in every calculation that has diffuse functions; by how much is known only to within about 0.7 eV.
- A search on the committed grid, every charge 0.25 e, finds designs that pass all five tests at the working level and in def2-TZVPD with 3 to 10 charges: 18 of 27, lowering the frozen barrier by 4.30 to 13.02 kcal/mol at the working level, and the two basis sets agree within +0.04 to +0.14 kcal/mol.
- As charges are added, what gives way first is the hold on the last electron: with twelve charges it is about zero at the reactant. With fifteen the larger basis set shows a failure the smaller one does not.
- Each survivor adds 2.4 to 8.8 kcal/mol/Å to the gradient on the frozen substrate, and a first-order map of that force agrees with direct calculation within 11 % (relative RMS 0.110 at most).
- One to six positive charges of 0.25 e together keep the dianion’s electrons at two levels, with functions that can hold an electron at every positive charge.
- With functions placed at it, one bare positive charge takes electrons from the dianion from 0.50 to 0.65 e up, at the four sites tested, and +1.00 e does so from 9 Å away.
- For one electron shared by charges of 0.25 e, CAM-B3LYP binds too strongly by 0.05 to 0.10 eV and ωB97X-V by 0.02 to 0.04 eV.
- Of the six designs of 17 November none passes the cross-check: four fail in def2-TZVPD and two are incomplete. They are set aside.
- With functions at their positive charges, five of the ten survivors with the largest lowering hold at both levels at the reactant and the transition state: S_n08_k2, S_n06_k1, S_n06_k2, S_n06_k3 and S_n05_k2. None of the ten takes electrons at both levels. At the working functional five take electrons at the reactant, two of them by more than the line the record fixed (D61).
- Behind a helium wall on their positive charges all ten keep the word SURVIVOR, each lowering smaller by 0.15 to 0.26 kcal/mol (D59).
- At first order, with the map at ωB97X-V D56's search places 17 of its 27 designs again; with the older B3LYP map at def2-SVP it places different designs at seven of nine numbers of charges, which give up 0.06 to 0.29 kcal/mol on the working map; and each of D56's designs scores lower than all 10 000 random designs of two kinds (D60).

**Cannot be said yet:**

- That any design lowers the barrier enough to count as catalytic, or at all once the substrate is free to move. No survivor has been relaxed, cross-checked or set against a coupled-cluster reference.
- Whether the five survivors not settled with functions keep their electrons; for them the working functional and ωB97X-V disagree, or ωB97X-V did not decide (D61).
- Whether the designs the other maps place would measure as they score: D60 scored them at first order and ran none.
- Whether the wall is closer to real ions than a bare charge: that test was not formed (D57).
- Where between ten and twelve charges the hold on the last electron is lost.
- That a production level of theory has been chosen, or that a coupled-cluster value of any ddE exists.
- Anything about an enzyme, a solvent or another frame. The charges stand for no residue.

**Next.** The steps are listed at the front, under *What is next, in order*. After them: more frames; then a solvent or protein environment; then real residues in place of point charges.

## References

- Agbaglo, Summers, Cheng and DeYonker, "The influence of model building schemes and molecular dynamics sampling on QM-cluster models: the chorismate mutase case study", *Phys. Chem. Chem. Phys.* 2024, 26, 12467 (in the project files).
- Bondi, "van der Waals Volumes and Radii", *J. Phys. Chem.* 1964, 68, 441.
- Bursch, Mewes, Hansen and Grimme, "Best-practice DFT protocols for basic molecular computational chemistry", *Angew. Chem. Int. Ed.* 2022, 61, e202205735.
- Claeyssens et al., "High-accuracy computation of reaction barriers in enzymes", *Angew. Chem. Int. Ed.* 2006, 45, 6856.
- Claeyssens et al., "Analysis of chorismate mutase catalysis by QM/MM modelling of enzyme-catalysed and uncatalysed reactions", *Org. Biomol. Chem.* 2011, 9, 1578 (in the project files).
- Goerigk et al., "A look at the density functional theory zoo with the advanced GMTKN55 database for general main group thermochemistry, kinetics and noncovalent interactions", *Phys. Chem. Chem. Phys.* 2017, 19, 32184.
- Guo et al., "Communication: An improved linear scaling perturbative triples correction for the domain based local pair-natural orbital based singles and doubles coupled cluster method [DLPNO-CCSD(T)]", *J. Chem. Phys.* 2018, 148, 011101.
- Herbert and Ortiz, "Ab initio investigation of electron detachment in dicarboxylate dianions", *J. Phys. Chem. A* 2000, 104, 11786.
- Kim, Sim and Burke, "Communication: Avoiding unbound anions in density functional calculations", *J. Chem. Phys.* 2011, 134, 171103.
- Lee, Furche and Burke, "Accuracy of electron affinities of atoms in approximate density functional theory", *J. Phys. Chem. Lett.* 2010, 1, 2124.
- Lee and Taylor, "A diagnostic for determining the quality of single-reference electron correlation methods", *Int. J. Quantum Chem.* 1989, 36 (S23), 199.
- Liakos et al., "Exploring the accuracy limits of local pair natural orbital coupled-cluster theory", *J. Chem. Theory Comput.* 2015, 11, 1525.
- Mulholland, "Chemical accuracy in QM/MM calculations on enzyme-catalysed reactions", *Chem. Cent. J.* 2007, 1, 19.
- Ranaghan et al., "Projector-based embedding eliminates density functional dependence for QM/MM calculations of reactions in enzymes and solution", *J. Chem. Inf. Model.* 2019, 59, 2063.
- Wang et al., "Intramolecular Coulomb repulsion and anisotropies of the repulsive Coulomb barrier in multiply charged anions", *J. Chem. Phys.* 2000, 113, 653.
- Wappett and Goerigk, "A guide to benchmarking enzymatically catalysed reactions: the importance of accurate reference energies and the chemical environment", *Theor. Chem. Acc.* 2021, 140, 68.

## Where our numbers come from

All under `phase2.2/` of the results repository at commit `173668c6`, except D60 NOTE 1.

| what | committed file |
|---|---|
| the frame decision | `STAGE6_DECISIONS_20261021.md` |
| the two frames compared | `cs_stage6/STAGE6_DIAGNOSTIC35_20261111.txt` and `STAGE6_DIAGNOSTIC35_RESULT_20261111.txt` |
| barriers, benchmark and orbitals (Figure 1) | `cs_stage6/figures/F1_reference_barrier.tsv`, `F11_two_tests.tsv` |
| detachment energies by functional | `cs_stage6/figures/F12_detachment_energy.tsv`; `STAGE6_PROBE1_ERRATUM1_20261027.txt` |
| coupled-cluster detachment energies | `cs_stage6/STAGE6_DIAGNOSTIC39_RESULT_20261115.txt` |
| working level and cross-check levels | `cs_stage6/STAGE6_AMENDMENT7_20261117.txt` |
| how the report level is chosen; what changed after the cross-check | `cs_stage6/STAGE6_AMENDMENT8_20261118.txt`; `STAGE6_AMENDMENT9_20261120.txt` |
| the benchmark's settings, diagnostics and limits | `cs_stage6/STAGE6_DIAGNOSTIC36_20261111.txt`, `STAGE6_DIAGNOSTIC36_RESULT_20261114.txt`, `STAGE6_DIAGNOSTIC41_RESULT_20261115.txt` |
| the benchmark's three approximations (D45; Figure 1) | `cs_stage6/STAGE6_DIAGNOSTIC45_RESULT_20261119.txt`; `d45_barriers.tsv` |
| r~safe~ and its limits | `cs_stage6/STAGE6_DIAGNOSTIC11_ERRATUM1_20261027.txt`; `WRITEUP_CONSOLIDATED_20261111.md` sections 4.1, 4.6 and 8.1 |
| the five tests | `cs_stage6/STAGE6_DIAGNOSTIC44_20261118.txt` section 2; `STAGE6_AMENDMENT6_20261117.txt` |
| where the charges sit (Figures 2 and 3) | `cs_stage6/sites_f42436.tsv`; `cs_stage6/d33a/sp_42436_R/substrate.xyz` and `sp_42436_TS/substrate.xyz`; `cs_stage6/d43.tsv` |
| the enzyme’s charged groups (Figures 2 and 3, table under Figure 3) | `cs_stage6/charges_map/chorismate_optimal_charges.html` (its embedded coordinates) and `charges_map/BUILD_RECORD.txt`; the coefficient: `cs_stage6/A_f42436_d33a.tsv` |
| the placement rule | `cs_stage6/STAGE6_DIAGNOSTIC43_20261117.txt` |
| D43: sections 5 and 7, Figure 4 | `cs_stage6/figures/T15_d43_conditions.tsv`; `STAGE6_DIAGNOSTIC43_RESULT_20261117.txt` |
| the linear objective's checks | `cs_stage6/WRITEUP_CONSOLIDATED_20261111.md` section 4.10 |
| the cross-check (section 7, Figure 5) | `cs_stage6/STAGE6_DIAGNOSTIC44_RESULT_20261120.txt`; `d44.tsv`; the wording for revDSD-PBEP86-D4: `STAGE6_DIAGNOSTIC44_NOTE2_20261121.txt` |
| one charge; the larger basis set; the estimate S (section 8.1, Figures 5 and 6) | `cs_stage6/STAGE6_DIAGNOSTIC47_20261121.txt`, `STAGE6_DIAGNOSTIC47_RESULT_20261121.txt`; `d47.tsv` |
| single charges in steps; arrangements (sections 8.1 and 8.3, Figure 6) | `cs_stage6/STAGE6_DIAGNOSTIC48_20261121.txt`, `STAGE6_DIAGNOSTIC48_RESULT_20261121.txt`; `d48.tsv` |
| the functions at a charge (section 8.2, Figure 6) | `cs_stage6/STAGE6_DIAGNOSTIC49_RESULT_20261122.txt`, `d49_calibration.tsv`; `STAGE6_DIAGNOSTIC50_RESULT_20261123.txt`, `d50_calibration.tsv`; `STAGE6_DIAGNOSTIC51_20261123.txt`, `STAGE6_DIAGNOSTIC51_RESULT_20261123.txt`, `d51_rule.tsv`, `d51_ladder.tsv` |
| the eleven-charge design with functions that hold an electron (section 8.3) | `cs_stage6/STAGE6_DIAGNOSTIC50_20261122.txt`, `STAGE6_DIAGNOSTIC50_RESULT_20261123.txt`; `d50_dianion.tsv` |
| its standing, the order of events, the wall as a test arm | `cs_stage6/STAGE6_AMENDMENT10_20261123.txt` |
| one electron shared by several charges (D52; section 8.4, Figure 6) | `cs_stage6/STAGE6_DIAGNOSTIC52_20261123.txt`, `STAGE6_DIAGNOSTIC52_RESULT_20261123.txt`; `d52_systems.tsv`, `d52_rules.tsv` |
| charges of 0.25 e together on the dianion (D53, D54; section 8.5) | `cs_stage6/STAGE6_DIAGNOSTIC53_RESULT_20261124.txt`, `STAGE6_DIAGNOSTIC54_RESULT_20261124.txt` |
| the search run now on the committed grid; what the outputs of the record hold (sections 4 and 6) | `cs_stage6/STAGE6_AMENDMENT11_20261124.txt` |
| the search (D56; section 6, Figure 7) | `cs_stage6/STAGE6_DIAGNOSTIC56_20261124.txt`, `STAGE6_DIAGNOSTIC56_RESULT_20261125.txt`, `STAGE6_DIAGNOSTIC56_NOTE1_20261125.txt`; `d56_designs.tsv`, `d56_survivors.tsv` |
| the walled runs and the test against real ions (D57; section 6.4) | `cs_stage6/STAGE6_AMENDMENT12_20261124.txt`, `STAGE6_DIAGNOSTIC57_20261125.txt`, `STAGE6_DIAGNOSTIC57_RESULT_20261125.txt`; `d57_designs.tsv`, `d57_ions.tsv`; the two runs stopped by their limit: `d57/run_I1.pbs.out`, `d57/run_I2.pbs.out` |
| what follows the search: the pilot, the second search, the order of the work (front; sections 5 and 6) | `cs_stage6/STAGE6_AMENDMENT13_20261125.txt`, `STAGE6_AMENDMENT13_NOTE1_20261125.txt` |
| the new forms of input | `cs_stage6/STAGE6_FORMS_TEST1_RESULT_20261125.txt` |
| the force and the two first-order maps (D58; sections 5.3 and 6.3, Figure 7) | `cs_stage6/STAGE6_DIAGNOSTIC58_20261125.txt`, `STAGE6_DIAGNOSTIC58_RESULT_20261125.txt`; `d58_forces.tsv`; G_add and the catalytic verdict: `cs_stage6/STAGE6_CRITERIA.txt` |
| the second functional and the random designs (D60; front, section 6.6, Figure 8) | `cs_stage6/STAGE6_AMENDMENT14_20261125.txt`, `STAGE6_DIAGNOSTIC60_20261125.txt`, `STAGE6_DIAGNOSTIC60_RESULT_20261126.txt`; `d60_designs.tsv`, `d60_null.tsv`; the time estimate: `STAGE6_DIAGNOSTIC60_NOTE1_20261126.txt`, sent for commit on 26 November |
| the functions and the wall on the survivors (D59, D61; front and section 6.5) | `cs_stage6/STAGE6_DIAGNOSTIC59_20261125.txt`, `STAGE6_DIAGNOSTIC59_NOTE1_20261125.txt`, `STAGE6_DIAGNOSTIC59_RESULT_20261126.txt`, `STAGE6_DIAGNOSTIC61_20261125.txt`, `STAGE6_DIAGNOSTIC61_RESULT_20261126.txt`; `d59_wall.tsv`, `d61_functions.tsv`; the level shift: `d61/WXV_F_S_n10_k1_R/job.out` and the other three runs of ωB97X-V with functions of S_n10_k1 and S_n10_k3 |

The times at which D52 ended and was committed are from its committed log and from the commit. The time D56’s search took on the PC (Jessica’s printout of 24 November) and the time D60’s first step took (her printout of 26 November) are in no committed file of `173668c6`.

## How this copy was checked

On 26 November five scripts, kept with this document’s source, compared the text with the results repository at commit `173668c6`, the commit of D60’s result.

- **Quotations.** Each of the 65 passages in quotation marks occurs word for word in a committed file (`check_short.py`). The titles of papers in the references are not quotations from the record and were left out. The line of ORCA’s output in section 6.5 is in the job outputs named in the sources and was found there by hand.
- **Decimal numbers.** All 741 occur, at the precision printed here, in one of the 82 committed files named above or in the printed output of the figure scripts and of `d59_d61_derived.py`, which is where the derived numbers are computed.
- **The numbers added since version 7, one by one.** The check above only asks whether a number occurs somewhere in those files. So `verify_v8.py` recomputes each statement version 8 added from the one committed file it rests on (51 checks, 51 pass), and version 7’s own script (`verify_v7.py`) was run again on this text (58 of 58 pass).
- **D59 and D61, independently.** A fourth script (`indep_check_d59_d61.py`) reads the committed ORCA outputs with its own parsing and none of the committed readers’ functions. It recomputes D61’s 40 gains and 40 changes of the Löwdin charges, its 160 counts of electrons on the grid, which runs took electrons, the marks against L, and the ten designs’ words, and D59’s 60 walled numbers. 0 differences. It does not recompute the tests that make a run "not decided" (the dipole, the gap and the stability analysis); that ORCA raised its level shift in exactly the four runs of ωB97X-V with functions of S_n10_k1 and S_n10_k3 was checked by hand.
- **D60, independently.** A fifth script (`indep_check_d60.py`) reads D60's committed ORCA outputs and tables with its own parsing and none of the committed reader's functions. It recomputes the four energies against D33's and D37's, the potentials against D33's, the map at ωB97X-V from the raw potentials, the 1488 sites, the four comparisons of the maps, the scores of all 81 designs on the three maps and their keeping of D56's rules, the counts of designs found again, and the agreement of the random-design summary: 46 checks, 0 differences. It first differed in four entries of one column, because it took the column as the lowest of D56's three designs where the result gives D56's first-ranked; the script was corrected, not the result.
- **Figures.** Figures 1 to 7, redrawn from this commit, are byte for byte those of version 8.1. Version 10 uses the same files and changes only the wording of Figure 1’s caption. Figure 8 is new in version 11 and drawn from `d60_designs.tsv` and `d60_null.tsv` by `make_fig7.py`, whose printed output holds the derived numbers of section 6.6.
- **Literature (new in version 10).** On 26 November every paper cited was in Jessica’s library, `chorismate-refs` at commit `cd287bb`, or in the project files, and each was read against every sentence that cites it; a sixth script (`verify_lit_v10.py`) also sets each of those sentences against words in the paper’s own text (34 checks, 34 pass). Where version 9 said more than a paper says, version 10 says what the paper says, or marks the rule as this project’s own (sections 3.1 to 3.6). Bondi (1964) is in the library and was not re-read for this version. The papers are paraphrased, not quoted, so the quotation check above still covers the record only.
- **What this check is not.** It is weaker than the validator of the consolidated write-up, which ties every number to the files named on its own paragraph. Whole numbers, counts and times were not traced by a script. All six scripts are Claude’s; no second reader has been through the text.
