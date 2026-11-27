# Charge design for the chorismate rearrangement — work status, November 2026

Nov 26, 2026 · @Jessica

## Summary

An exact optimiser can place small charges around the frozen substrate that lower its barrier and pass every reliability test. What remains open is whether those lowerings survive harder tests and a free geometry.

- **The search finds candidates.** Charges of 0.25 e were placed on a grid around the substrate, at nine numbers of charges from 3 to 20. Of the 27 designs, 18 pass all five reliability tests in two basis sets. They lower the frozen barrier by 4.30 to 13.02 kcal/mol at the working level, where the barrier without charges is 26.82.
- **The substrate's hold on its last electron gives way first.** It falls from +1.25 eV without charges to about zero with twelve charges, which is where designs start to fail.
- **Under a harder test, the smaller designs hold and the largest are not settled.** With basis functions placed at the positive charges, so that an electron could move onto them, five of the ten survivors with the largest lowering keep their electrons at two functionals. The other five, the ones with the largest lowering, are not settled: at the working functional their atoms give up 0.35 to 0.88 e at the reactant, while at a second functional only 0.03 to 0.05 e leaves (for two of them that functional's reading is undecided). Behind a helium wall all ten still pass, each lowering 0.15 to 0.26 kcal/mol smaller.
- **At a second functional the search places mostly the same designs, and every design beats chance.** At ωB97X-V it places 17 of its 27 designs again, its best the same at seven of nine numbers of charges. The older B3LYP map, which also differs in basis set, gives different designs at seven of nine numbers, though they score within 0.29 kcal/mol of the search's best on the working map. Each design scores better than all 10 000 random designs of two kinds. These are first-order scores, not measurements (section 7.4).
- **Nothing here is a catalytic result yet.** Every number is for one enzyme frame, frozen geometries, in vacuo. No survivor has been relaxed, cross-checked at the other levels of theory, or compared with a coupled-cluster reference.
- **The level of theory is a working choice, not a production one.** CAM-B3LYP is 1.84 kcal/mol from the coupled-cluster barrier in the larger basis set. B3LYP, the level of the earlier work, is 6.56 too low, and its highest occupied orbital lies above the vacuum level.
- **Next:** relax three survivors as a pilot; run a second search with a limit on the force the charges exert; then cross-check and set a coupled-cluster reference on the candidates that remain.

## 1. The question, and where the inputs came from

Can a few point charges, placed around the substrate with no protein, lower the barrier of the chorismate-to-prephenate rearrangement, and can an optimiser find where to put them? Chorismate mutase speeds this Claisen rearrangement up about a million-fold (Agbaglo et al. 2024). Much of that is attributed to transition-state stabilisation, largely electrostatic (Claeyssens et al. 2011). The question here isolates the electrostatic part and asks whether it can be designed.

**Where the inputs came from (Phase 1).** Phase 1 simulated the reaction inside the enzyme by QM/MM: quantum mechanics for the substrate, a classical force field for the protein. From a band of 30 reaction-path frames, one frame (42436) was taken through the production protocol. The QM/MM package optimised its transition state, converged in 7 cycles, and followed the path down to its reactant, in 6, with an 8 Å active region. The substrate's two geometries from that frame are the only geometries used here. They are taken out of the enzyme and held frozen.

**The system and the number reported.** The substrate is the chorismate dianion: 24 atoms, charge −2, 118 electrons. Every calculation reports **ddE**, the barrier with the charges present minus the barrier without them. It is negative when the charges lower the barrier.

## 2. The model system: one frame, frozen, in vacuo

All current work uses one frame's reactant and transition state, held frozen and computed without any environment. The frame was chosen because its two geometries are true stationary points.

- **Frame 42436's geometries are optimised stationary points**, the kind of point a barrier is defined between.
- **The frame used earlier, 41786, is not.** Its reactant was the first image of a reaction-path band, not a minimum. Re-optimising it lowered its energy by 4.58 kcal/mol, against a tolerance of 1.0.
- **The choice matters.** At the one level run on both frames the barrier is 16.67 kcal/mol at 41786 and 18.46 at 42436. Across five methods the geometry moves the barrier by 1.5 to 3.6 kcal/mol and changes the order of the methods.

**Limits, and their direction.** It is one frame of thirty, and whether it is typical is not known. The geometries are frozen at the enzyme's, so the substrate cannot respond to the charges or to their push on its atoms; how much of a frozen lowering survives once it can is the pilot relaxation's question (section 10). In vacuo there is no solvent or protein to screen the charges.

## 3. Choosing the level of theory

The working level is CAM-B3LYP-D3BJ, with the def2-SVPD basis for searching and def2-TZVPD as part of every design's test; it is a working choice, and no production level has been adopted. B3LYP, the level of the earlier work, is retired.

**How it was chosen.** We followed the route recommended in the literature: a coupled-cluster reference on the system itself, since comparing functionals with correlated ab initio results is a standard way to choose one for a given application (Ranaghan et al. 2019); several functionals of the classes the large benchmarks favour for barrier heights, namely hybrids, range-separated hybrids and double hybrids (Goerigk et al. 2017; Bursch et al. 2022); basis sets with diffuse functions because the substrate is an anion (Bursch et al. 2022); and a check of anything peculiar to the system. Density functionals cannot be trusted one at a time: for this very reaction, in the enzyme, the barrier varied by 13 kcal/mol across functionals in a QM/MM study (Ranaghan et al. 2019), and Claeyssens et al. (2011) give the typical error of B3LYP for it as about 3 kcal/mol.

- **The reference.** DLPNO-CCSD(T), an efficient coupled-cluster method, on our own two geometries: a barrier of 23.86 kcal/mol in def2-TZVPD and 22.90 in def2-SVPD. Its three approximations were then measured. Corrected for them, it becomes 23.13 or 23.52 by two estimates; the committed values stand.
- **Nine functionals at two basis sets (Figure 1).** Four are within 3 kcal/mol of the reference in def2-TZVPD: CAM-B3LYP (+1.84), the double hybrids revDSD-PBEP86 (−2.36) and PWPB95 (−2.52), and PW6B95 (−2.90). The general-purpose favourites ωB97X-V, ωB97X-D3, ωB97M-V and M06-2X are 3.5 to 5.9 too high, which is why a reference on the system itself matters.
- **B3LYP fails both tests.** Its barrier is 6.56 kcal/mol below the reference, and its highest occupied orbital lies 1.23 eV above the vacuum level in def2-SVPD, as if the last electron were unbound. That is a known artefact of approximate functionals for anions; the electron can still be bound, and B3LYP's own detachment energy here is +0.50 eV (Galbraith and Schaefer 1996; Rienstra-Kiracofe, Tschumper and Schaefer 2002).
- **The dianion holds its second electron, but how firmly is uncertain.** Every one of eleven calculations with diffuse functions finds the detachment energy positive. The two coupled-cluster routes give +1.06 and +1.77 eV, so the reference is a range; at CAM-B3LYP it is +1.25 eV. Every test below uses its sign, not its size.
- **A second functional for the electron tests.** ωB97X-V is used beside CAM-B3LYP wherever electrons might be shared between charges, because it describes one electron shared by charges of 0.25 e more closely (section 4).

**What the benchmark does not support.** A choice among CAM-B3LYP, revDSD-PBEP86 and PWPB95: which is nearest depends on which reference value is used. Nor does it test ddE itself: it is a benchmark of the bare barrier, on one frame, in the gas phase. A coupled-cluster ddE is to be run on two survivors, chosen by a dated rule once the pilot and the second search have reported.

&#91;image: Figure 1: the nine functionals against the coupled-cluster reference\]

**Figure 1.** The nine functionals on the bare dianion, frame 42436, in vacuo. A: the barrier in two basis sets. B: its distance from the coupled-cluster reference in the same basis. C: the energy of the highest occupied orbital at the reactant and the transition state; in the hatched region a functional puts the last electron above the vacuum level, as if it were unbound. The grey band is minus the coupled-cluster detachment energy by its two routes. Measured. The revDSD-PBEP86 numbers are, in the record's words, "on the restricted solution, which the stability analysis finds unstable in the self-consistent step".

## 4. How the charges are represented, and the tests every design must pass

Each charge is a bare point charge of at most 0.25 e, and a design's barrier change counts only if it passes five reliability tests in two basis sets. The size cap rests on the record: a single positive charge takes electrons from about 0.50 e up, and charges of 0.25 e together held when tested.

**The risk.** A positive point charge next to an anion can attract one of its electrons. In a calculation that is easy to miss: a point charge carries no basis functions, so an electron can only move there if the substrate's own functions happen to reach it. To test for it properly, functions are placed at the charge itself, on a *ghost atom*, a centre with basis functions but no nucleus or electrons (Figure 2).

- **One charge takes electrons above about half an electron's charge.** Raised in steps at four sites, the first size that took electrons was 0.50 to 0.65 e. At +1.00 e a whole electron left the substrate even with the charge 9 Å away, so distance alone does not make a charge safe.
- **The functions at the charge must be able to hold an electron.** The standard def2-TZVPD functions bind nothing at 0.25 e. A larger set was built that is within 0.006 eV of the exact answer for one electron at one charge.
- **The functional has an error of its own.** For one electron shared by charges of 0.25 e, CAM-B3LYP binds it too strongly by 0.05 to 0.10 eV and ωB97X-V by 0.02 to 0.04 eV. So ωB97X-V is the second functional, and a capture whose energy gain is below L = 0.3127 eV, three times CAM-B3LYP's largest error, is not settled by CAM-B3LYP alone.
- **Charges of 0.25 e together held.** On the dianion, one to six positive charges of 0.25 e kept their electrons at both functionals and both states, with at most 0.0193 e leaving the atoms. An older eleven-charge design, five of its charges negative, took electrons at the reactant. That older design and its siblings were set aside on 24 November; since then every charge is at most 0.25 e and every design is measured.

**The five tests.** Tests 1 to 4 compare the calculation with the charges against the one without; test 5 needs a second calculation, the monoanion with the same charges. All five must pass at the working level and again in def2-TZVPD.

| test | the question | fails when |
| --- | --- | --- |
| 1. relocation | has an atom gained or lost electrons wholesale? | the largest atomic charge rises by 0.25 e or more |
| 2. dipole | has the charge distribution been distorted? | the dipole is twice the control's or more |
| 3. gap | has an empty orbital dropped to meet the filled ones? | the gap is below 1.0 eV and below half the control's |
| 4. stability | is the calculation on its lowest solution? | the last stability check says unstable |
| 5. binding | does the dianion still hold its second electron? | the detachment energy is zero or negative at either state |

**Table 1.** The five reliability tests.

A design that passes all five at both basis sets, with its two barrier changes agreeing within 15 per cent, is called a **survivor**. A survivor is a candidate, not a result: the record says "A SURVIVOR is not a result." The test with functions at the charges is run on survivors afterwards and reported beside them (section 7).

&#91;image: Figure 2: when a bare positive charge takes an electron\]

**Figure 2.** When a bare positive charge takes an electron. A and D: CAM-B3LYP in def2-TZVPD with functions placed at the charge; B: Hartree-Fock; C: the larger set of functions. A: one positive charge at four sites, raised in steps; the star is +1.00 e placed 9 Å away. B: how far the functions at the charge fall short of the exact binding energy for one electron at one charge; above the dotted line they hold no electron. C: the functional's own error for one electron, at one charge by its size and for several charges of 0.25 e, CAM-B3LYP and ωB97X-V. D: arrangements of charges with functions at every positive charge. Measured; the exact binding energy and the differences from it are derived.

## 5. The optimiser in plain terms

The optimiser ranks arrangements by a cheap first-order estimate of the barrier change and finds the best arrangement under fixed rules, with proof that none is better; every arrangement it proposes is then measured. It proposes candidates; it does not certify them.

**The map.** A molecule creates an electrostatic potential V around itself, and a small charge q at a point has energy q × V there. The barrier is E(TS) − E(R), so to first order a charge changes it by q × \[V(TS) − V(R)\]. That bracket, computed at every grid site i, is the map a(i), in kcal/mol per unit charge. Where a(i) is negative, a positive charge lowers the barrier; where it is positive, a negative charge does. The idea of locating charges from the difference between the transition state's and the reactant's potential is the "catalytic field" of Szefczyk et al. (2004), who found the enzyme's charged residues close to the optimal positions it predicts.

**The grid.** 2626 candidate sites around the substrate (Figure 3); 1488 of them admit a charge of 0.25 e.

**The search.** The score of an arrangement is the sum of a(i) × q(i) over its charges. The optimiser is a mixed-integer linear programme: for each site, a yes-or-no choice of whether it holds a charge and, if so, a charge between −0.25 and +0.25 e. The rules: a fixed number of charges n; no two charges closer than 3.25 Å; the charges sum to zero or more. A standard solver finds the arrangement with the best score and proves that no arrangement obeying the rules scores better. For each n it keeps the best three, each of the second and third having a charge more than 1.5 Å from every charge of the better ones. With a linear score and a cap, every charge comes out at +0.25 or −0.25 e.

**What is validated and what is a proxy.**

- **Validated:** a(i) is the true slope of the barrier change for a vanishingly small charge (finite-difference checks), and it hardly changes with the larger basis set (0.05 kcal/mol per e root mean square).
- **A proxy, and a consistent underestimate:** for the 18 survivors of the search, "the measured lowering is 1.03 to 1.17 times the first-order score the search ranked by" (Figure 4). The estimate leaves out polarisation, the substrate's electrons shifting toward the charges.
- **Not in the score at all:** whether a design passes the reliability tests, whether the dianion keeps its second electron, and whether a charge takes an electron. Each is measured for every design.
- **A first-order map of the force** the charges exert on the atoms agrees with direct calculation (section 7.1) and can enter the next search. **A first-order map of the hold on the last electron does not** (off by up to 3.259 eV), so the fifth test stays a measurement.

**What it can and cannot claim.** It can propose candidates cheaply and in a sensible order. Proven optimality is optimality of the first-order score under the rules, not of the real barrier.

&#91;image: Figure 3: where the charges of two survivors sit, to scale\]

**Figure 3.** Where the charges sit, to scale. The substrate at its reactant geometry seen from above and from the side, with its van der Waals outline; the small grey dots are the grid's 2626 sites. The solid black line is the C–O bond that breaks, the dotted one the C–C bond that forms. Filled circles are the positive and open circles the negative charges of two survivors: one of six charges that holds under every test so far, and the one of ten charges with the largest lowering, which is not settled (section 7). Drawn from the committed coordinates.

&#91;image: Figure 4: first-order score against measured barrier change\]

**Figure 4.** The optimiser's first-order score against the measured barrier change for all 27 designs of the search, at the working level. On the dashed line the two are equal; below it, the charges lower the barrier more than predicted. Survivors are filled; the other designs (failed, or two not fully measured) are open. Measured, with the score taken from the search's own table.

## 6. What the search found

Eighteen of the 27 designs survive, at every number of charges from 3 to 10; beyond ten, the substrate's hold on its last electron gives way first, then reliability in the larger basis set.

The search was pre-registered on 24 November, before it had been run on the real map, and every design was run as the dianion and the monoanion, at both states, in both basis sets: 224 calculations with the controls.

| charges | sum of the charges (e) | outcome for the three designs |
| --- | --- | --- |
| 3 | +0.25 | all survive |
| 4 | 0.00 | all survive |
| 5 | +0.25 | all survive |
| 6 | 0.00 | all survive |
| 8 | 0.00 | all survive |
| 10 | 0.00 | all survive |
| 12 | 0.00 | all fail test 5: the detachment energy reaches zero |
| 15 | +0.25 | all fail tests 1 to 4 in def2-TZVPD |
| 20 | +0.50 | one fails as at 15; two not measured (time limit) |

**Table 2.** The search, by number of charges (measured).

- **The lowering grows with the number of charges** (Figure 5, panel A): from −4.30 to −4.36 kcal/mol with three charges to −12.35 to −13.02 with ten, at the working level. The two basis sets agree within 0.04 to 0.14 kcal/mol for every survivor. For scale, the barrier without charges is 26.82 kcal/mol at the working level and 25.70 in def2-TZVPD.
- **The hold on the last electron falls as charges are added** (panel B): from +1.25 eV without charges to +0.20 to +0.24 with ten and about zero with twelve. At five charges, where they sum to +0.25 e, it holds more firmly than at four and six, where they sum to zero.
- **With fifteen charges the larger basis set shows a failure the smaller one does not:** the dipole rises to more than three times the control's.
- **Where the charges go.** Positive charges by the ether oxygen whose C–O bond breaks, negative charges by the ring carboxylate (Figure 3; derived from the committed designs). The survivors' charges stand 3.13 to 3.21 Å from the nearest atom.
- **One omission, and its direction.** The committed charge model gives each charge a small Lennard-Jones shell, which the search left out. With it, every lowering is smaller by 0.17 to 0.33 kcal/mol, 1.0 to 4.4 per cent: leaving it out favoured a lower barrier by that much. It changes no design's outcome.

&#91;image: Figure 5: the search, the hold on the last electron, and the added force\]

**Figure 5.** The search and the force its survivors exert. Three designs at each number of charges, best-ranked on the left of each group; every charge 0.25 e. A: the barrier change at the working level (filled) and in def2-TZVPD (open), where the four reliability tests do not fail; survivors in black. B: the energy to remove the last electron at the reactant (circles) and the transition state (triangles); below the dashed line test 5 fails. C: the extra gradient each survivor puts on the substrate (section 7.1). Measured.

## 7. Testing the survivors

The survivors were put through three further tests: the force they exert on the substrate, basis functions at their positive charges, and a helium wall on those charges. Smaller designs come through all of them; the five with the largest lowering are not settled. Section 7.4 tests the search itself: whether it places the same designs at another functional, and whether its designs beat random ones.

### 7.1 The force each survivor exerts

A charge beside a frozen molecule also pushes on its atoms, and a large push may foretell a large change once the geometry is free; the pilot relaxation tests that. Each survivor adds 2.4 to 8.8 kcal/mol/Å to the gradient on the 24 atoms (root mean square), rising with the number of charges (Figure 5, panel C). For scale only, the published GOCAT method reports relaxed designs with gradients around 1 kcal/mol/Å, on the total rather than the added gradient; the record notes that "Neither published threshold is carried over." The first-order map of this force agrees with direct calculation within 0.054 to 0.110 of its size, against a tolerance of 0.25 fixed beforehand, so the next search can limit it without extra calculations.

### 7.2 Basis functions at the positive charges

The ten survivors with the largest lowering were rerun with functions at each positive charge, at CAM-B3LYP and ωB97X-V, each with its own control carrying the same functions but no charges. A run took electrons if 0.25 e or more left the substrate's atoms or a reliability test fired; a design holds only if it holds at both functionals and both states. A first attempt placed each ghost atom exactly on its charge, and its runs with charges and functions together stopped at start-up; this is recorded, and the repeat places each 0.01 Å beyond its charge. All 120 runs of the repeat were measured.

| rank | charges | lowering, working level (kcal/mol) | with functions at its positive charges | behind a helium wall |
| --- | --- | --- | --- | --- |
| 1st | 10 | −13.02 | not settled: takes electrons at the reactant at CAM-B3LYP, above L; ωB97X-V undecided | survives |
| 3rd | 10 | −12.74 | not settled: as above | survives |
| 2nd | 10 | −12.35 | not settled: takes electrons at CAM-B3LYP only, within L | survives |
| 1st | 8 | −10.83 | not settled: as above | survives |
| 3rd | 8 | −10.83 | not settled: as above | survives |
| 2nd | 8 | −10.76 | holds | survives |
| 1st | 6 | −8.32 | holds | survives |
| 2nd | 6 | −8.31 | holds | survives |
| 3rd | 6 | −8.17 | holds | survives |
| 2nd | 5 | −6.96 | holds | survives |

**Table 3.** The ten survivors with the largest lowering under the two harder tests (measured). Each design is given by its number of charges and its rank among the three placed at that number.

- **The two functionals disagree for the five largest designs.** At the reactant, at CAM-B3LYP, their atoms give up 0.35 to 0.88 e to the functions; at ωB97X-V the same runs give up 0.03 to 0.05 e (Figure 6, panel B). Hartree-Fock finds no design taking electrons. CAM-B3LYP binds a shared electron too strongly (section 4), which may be why it moves electrons where ωB97X-V does not; that is not tested here.
- **Two gains exceed the line L.** For the first- and third-ranked designs of ten charges the energy gained by moving the electrons is 0.3158 and 0.3749 eV, against L = 0.3127; for the first-ranked the margin is 0.0031 eV. ωB97X-V did not decide these two because its calculation needed a convergence aid, and the reading then withholds one test.
- **Direction.** Every design not settled is among the five largest lowerings; every one that holds lowers the barrier by 10.76 kcal/mol or less. This tells against the largest lowerings: the direction of a higher barrier.

### 7.3 A helium wall, and the wall's own test

A wall is a core potential placed on a charge that keeps the substrate's electrons off it. Behind a helium wall on their positive charges all ten remain survivors (the dipole test is not applied to walled runs, as in the record's earlier wall work), and each lowering is smaller than without the wall by 0.15 to 0.26 kcal/mol (Figure 6, panel A). The wall alone, with no charge, changes the barrier by +0.0153 to +0.1117 kcal/mol.

Whether the wall is closer to real ions than a bare charge was to be tested against Na+ and K+ at one site. That test was not formed: its two bare reference runs were stopped by a time limit that Claude had set, so by the pre-registered rule the wall is "NOT SUPPORTED". The word comes from two missing runs, not from evidence against the wall.

&#91;image: Figure 6: the ten survivors under the harder tests\]

**Figure 6.** The ten survivors with the largest lowering under the harder tests. A: the barrier change at the working level for the bare charges and behind the helium wall. B: the electrons that leave the substrate's atoms at the reactant with functions at the positive charges, at CAM-B3LYP and ωB97X-V; the dashed line is the 0.25 e that counts as taking electrons. Designs that hold are marked apart from those not settled. Measured.

### 7.4 The search at a second functional, and against random designs

This test asks two things of the map the search ranks by, at first order, on the same frame and grid and under the same rules: does the search place the same designs when the map is computed at another functional, and do its designs beat random placement? A control repeated the two runs behind the working map and reproduced their energies to within 1e-11 Eh, and the runs at ωB97X-V reproduced the earlier ones, so the new map was used (Figure 7). The pre-registration put the three searches at 10 to 30 minutes each; on Jessica's PC they took hours, and a dated note records the error. Nothing in the result depends on it.

- **At ωB97X-V the search places mostly the same designs.** Over the 1488 sites that can hold a charge, the map at ωB97X-V/def2-SVPD agrees closely with the working map (Pearson 0.9977, Spearman 0.9920; mean difference 0.15 kcal/mol per e). The search on it places 17 of the 27 designs again, at least one at every number of charges, and at seven of the nine numbers its best design is the search's first-ranked one. At twelve charges its best is the search's second-ranked design; at twenty it is a new design that scores 0.07 kcal/mol less on the working map.
- **Against the older B3LYP map the designs differ, but score nearly as well.** That map (B3LYP-D3BJ/def2-SVP) agrees less closely (Pearson 0.9763, Spearman 0.9358; mean difference 0.46, largest 1.18 kcal/mol per e). The search on it places only 3 of the 27 designs again, all at five and six charges. Scored on the working map, its best design at each of the other seven numbers gives up 0.06 to 0.29 kcal/mol of lowering against the search's best. The two maps differ in basis set as well as functional, so the difference cannot be put on the functional alone.
- **Every design beats every random design.** At its number of charges, each of the 27 designs scores lower than all 10 000 random designs of each of two kinds. Kind (i) places charges of 0.25 e at random sites, with the search's spacing; kind (ii) puts on random sites the best charges the search's rules allow. The search's weakest design at each number lies 0.57 to 4.71 kcal/mol below the best random design of kind (ii), and the margin grows with the number of charges. From 4716 to 9979 of the 10 000 random designs of kind (ii) at each number use a charge smaller than 0.25 e, which none of the search's designs does.
- **What it does not say.** All of it is first order. A design that another map places is placed by that map, not measured at that functional: one found again there is not confirmed by it, and one not found again is not refuted. A random design is scored, not measured. Nothing here keeps or drops a design.
- **Direction.** None: no reading of this test moves a reported barrier.

&#91;image: Figure 7: the search at two other maps, and against random designs\]

**Figure 7.** The search at two other maps, and against random designs, at first order (derived from the committed result). A: of the three designs the search placed at each number of charges, how many the search with each other map places again, with the same sites and the same charges. B: each other map's best design, scored on the working map, minus the search's best there (kcal/mol); zero means the same design or an equal score. C: the search's three designs at each number of charges against 10 000 random designs of each kind; each bar runs from the median random design to the best one.

## 8. Limitations

Every number here is a frozen, gas-phase, single-frame number for bare point charges, and two of the effects below are known or expected to push it toward a lower barrier than a free, real system would show.

| limitation | what it means | which way it pushes the barrier |
| --- | --- | --- |
| frozen geometries | the substrate cannot respond to the charges or their push (2.4 to 8.8 kcal/mol/Å added) | not known until the pilot relaxation; the record expects a loss of lowering |
| one frame of thirty | whether frame 42436 is typical is unknown | either way |
| gas phase | no solvent or protein screens the charges | expected toward a lower barrier, since a medium screens the charges; not measured |
| point charges stand for no atom | no real ion has been placed at these positions; the wall's test against real ions was not formed | not known |
| the shell term left out of the search | each lowering is 0.17 to 0.33 kcal/mol too large | toward a lower barrier |
| CAM-B3LYP over-binds shared electrons | it may move electrons onto charges where ωB97X-V does not | against the largest designs: they may look unsettled when they are not |
| no production level | the benchmark cannot choose among the three nearest levels, and does not test ddE | either way; to be fixed by a dated rule |
| first-order ranking | the score underestimates the lowering by 3 to 17 per cent and ignores reliability | ordering only; every design is measured |

**Table 4.** The main limitations and their direction.

## 9. Conclusions

The method works as a candidate generator; whether any candidate is catalytic is not yet known.

**Established** (one frame, frozen, gas phase, bare point charges):

- B3LYP is unsuitable for this dianion. CAM-B3LYP and two double hybrids lie within 3 kcal/mol of a coupled-cluster barrier in def2-TZVPD.
- The bare dianion holds its second electron in every calculation with diffuse functions.
- An exact search with charges of 0.25 e finds designs that pass all five reliability tests in both basis sets with 3 to 10 charges: 18 of 27, lowering the frozen barrier by 4.30 to 13.02 kcal/mol.
- As charges are added, the hold on the last electron gives way first.
- A single bare positive charge takes electrons from 0.50 to 0.65 e up at the four sites tested, and +1.00 e does so even 9 Å away; one to six positive charges of 0.25 e together do not.

**Supported, but provisional:**

- Five survivors, of five, six and eight charges, hold with functions at their positive charges at two functionals (lowerings of 6.96 to 10.76 kcal/mol). They are the current best candidates for relaxation.
- The helium wall changes the survivors' lowerings by a few per cent and no outcome.
- A force limit can be built into the next search from a first-order map.
- At first order the designs depend only partly on the map: at ωB97X-V the search places 17 of its 27 designs again, and the older B3LYP map, which also differs in basis set, gives different designs at seven of nine numbers of charges that score within 0.29 kcal/mol of the search's best on the working map. Every design beats all 10 000 random designs of two kinds (section 7.4).

**Not known:**

- Whether any lowering survives relaxation, a medium, or other frames.
- Whether the five largest designs keep their electrons: the two functionals disagree.
- Whether the wall is closer to real ions than a bare charge.

**Decisions pending:**

- Whether a design not settled with functions may still be quoted.
- Whether the pilot keeps the first-ranked design of ten charges, now not settled, among its three designs.
- Whether to repeat the wall's test against real ions with a longer time limit.

## 10. Next steps

The next question is how much of a frozen lowering survives when the substrate can move; the order below is fixed in the protocol of 25 November.

1. **A pilot relaxation of three survivors**, by the project's relaxed criteria, in vacuo, with the charges held in place. It uses the committed charge model, a point charge with a small Lennard-Jones shell, because bare charges collapsed onto the substrate in geometry optimisations of the earlier work. Reactants first; a transition state only for a design whose reactant held. In the protocol's words: "A relaxed barrier of the pilot is not quoted as a result and no design is kept or dropped on it." Its pre-registration is not yet written.
2. **A second search** with a limit on the added force, at a ladder of limits one of which is no limit, every charge still 0.25 e, and eleven charges added because none was measured between ten and twelve.
3. **A dated decision on which designs get the cross-check levels and the coupled-cluster reference**, once the pilot and the second search have reported, so that the costly runs go to designs that are still candidates. A production level of theory is then chosen by the rule already committed.
4. **Later:** more frames, then a solvent or protein environment, then real chemical groups in place of point charges.

## Appendix A. The calculations by name, run number and file

All files are under `phase2.2/cs_stage6/` of the results repository at commit `173668c6`, except the frame decision.

| name in this document | run | committed result |
| --- | --- | --- |
| the frame decision | decision S1 | `phase2.2/STAGE6_DECISIONS_20261021.md` |
| the two frames compared | D35 | `STAGE6_DIAGNOSTIC35_RESULT_20261111.txt` |
| the coupled-cluster reference | D36, D41 | `STAGE6_DIAGNOSTIC36_RESULT_20261114.txt`, `STAGE6_DIAGNOSTIC41_RESULT_20261115.txt` |
| the reference's three approximations | D45 | `STAGE6_DIAGNOSTIC45_RESULT_20261119.txt` |
| the nine functionals | D37 | `figures/F1_reference_barrier.tsv` |
| the detachment energies | D39, D40 | `STAGE6_DIAGNOSTIC39_RESULT_20261115.txt`, `figures/F12_detachment_energy.tsv` |
| the working and cross-check levels; the rule for a production level | Amendments 7, 8, 9 | `STAGE6_AMENDMENT7_20261117.txt`, `STAGE6_AMENDMENT8_20261118.txt`, `STAGE6_AMENDMENT9_20261120.txt` |
| the five tests | D44, Amendment 6 | `STAGE6_DIAGNOSTIC44_20261118.txt`, `STAGE6_AMENDMENT6_20261117.txt` |
| one bare charge taking electrons; the functions at a charge | D47 to D51 | `STAGE6_DIAGNOSTIC47_RESULT_20261121.txt` to `STAGE6_DIAGNOSTIC51_RESULT_20261123.txt` |
| one electron shared by several charges; the second functional and L | D52 | `STAGE6_DIAGNOSTIC52_RESULT_20261123.txt`, `d52_rules.tsv` |
| charges of 0.25 e together on the dianion | D53, D54 | `STAGE6_DIAGNOSTIC53_RESULT_20261124.txt`, `STAGE6_DIAGNOSTIC54_RESULT_20261124.txt` |
| the search run on the committed grid at 0.25 e | Amendment 11 | `STAGE6_AMENDMENT11_20261124.txt` |
| the search | D56 | `STAGE6_DIAGNOSTIC56_RESULT_20261125.txt`, `d56_designs.tsv`, `d56_survivors.tsv` |
| a design, by its number of charges and its rank (Table 3, Figures 3 and 6) | D56, which names it S\_nNN\_kK (NN charges, rank K) | `d56_designs.tsv` |
| the wall's test against real ions | D57 | `STAGE6_DIAGNOSTIC57_RESULT_20261125.txt` |
| the force each survivor exerts; the two first-order maps | D58 | `STAGE6_DIAGNOSTIC58_RESULT_20261125.txt`, `d58_forces.tsv` |
| the shell term; the pilot and the second search; the order of work | Amendment 13 and its Note 1 | `STAGE6_AMENDMENT13_20261125.txt`, `STAGE6_AMENDMENT13_NOTE1_20261125.txt` |
| the helium wall on the survivors (and the first attempt with functions) | D59 | `STAGE6_DIAGNOSTIC59_RESULT_20261126.txt`, `d59_wall.tsv`, `STAGE6_DIAGNOSTIC59_NOTE1_20261125.txt` |
| functions at the survivors' positive charges | D61 | `STAGE6_DIAGNOSTIC61_RESULT_20261126.txt`, `d61_functions.tsv` |
| the search at a second functional, against random designs | D60, Amendment 14 | `STAGE6_DIAGNOSTIC60_20261125.txt` (pre-registration), `STAGE6_DIAGNOSTIC60_RESULT_20261126.txt`, `d60_designs.tsv`, `d60_null.tsv` |

## Appendix B. Glossary

| term | meaning |
| --- | --- |
| ddE | the barrier with the charges minus the barrier without them; negative = lower barrier |
| working level | CAM-B3LYP-D3BJ/def2-SVPD, the level the search and its tests use |
| def2-SVPD, def2-TZVPD | a smaller and a larger basis set, both with diffuse functions for loosely held electrons |
| detachment energy | the energy to remove the dianion's second electron; positive = held |
| survivor | a design that passes all five tests in both basis sets, with its two barrier changes agreeing within 15 per cent; a candidate, not a result |
| ghost atom | a centre carrying basis functions but no nucleus or electrons, placed at a charge so an electron could move there |
| L | 0.3127 eV, three times CAM-B3LYP's largest error for an electron shared by charges; a capture gaining less is not settled by CAM-B3LYP alone |
| Löwdin charges | a way of dividing a molecule's electrons among its atoms; used to see whether electrons left the substrate |
| first-order map | a(i) = V(TS) − V(R) at grid site i: the barrier change per unit charge for a very small charge there |
| mixed-integer linear programme | an optimisation with yes-or-no choices and a linear score; the solver proves its answer is the best under the rules |
| helium wall | a core potential placed on a charge that keeps electrons off it |
| added gradient | the extra force the charges exert on the substrate's atoms, root mean square over 72 components, kcal/mol/Å |
| frame 42436 | the snapshot of the enzyme simulation whose reactant and transition state are used throughout |

## Appendix C. How this document was checked

On 26 November the text was compared with the results repository at commit `173668c6`, the commit of the last result in it.

- **Decimal numbers.** All 170 decimal numbers before this appendix occur, at the precision printed, in one of the committed files named in Appendix A or in the printed output of the scripts that compute the derived numbers (a script, `check_short.py`, rounds each committed number to the printed precision and looks for a match). The two in the Literature item below, 7.30 and 20.0, are Ranaghan et al.'s, not ours.
- **Quotations.** All 7 passages in quotation marks occur word for word in a committed file.
- **The results of the three newest tests** (Table 3, Figures 6 and 7) were recomputed from the raw calculation outputs by a separate script with its own parsing: 40 energy gains, 40 changes in the electrons on the atoms, 160 electron counts, and 60 barrier changes behind the wall; for section 7.4, the energies and potentials of its four runs, the map at ωB97X-V rebuilt from its raw potentials, the scores of all 81 designs on the three maps, the counts of designs found again, and the random-design summary (46 checks). The search's numbers (Table 2, section 6, Figure 4) were recomputed the same way from its raw outputs: every barrier change and detachment energy at both levels, the controls, the ranges and the ratio to the score. 0 differences. For section 7.4 the script first differed in four entries of one column, because it had taken the column as the lowest of the search's three designs where the result gives its first-ranked one; the script was corrected, not the result.
- **Literature.** Agbaglo et al. 2024, Claeyssens et al. 2011, Szefczyk et al. 2004, Galbraith and Schaefer 1996 and Rienstra-Kiracofe et al. 2002 were checked against their text in the project library on 26 November. Bursch et al. 2022, Goerigk et al. 2017 and Ranaghan et al. 2019 were added to the library on 26 November and checked against their text the same day. Section 3 attributes each step of the route to the paper that states it; the 13 kcal/mol is Ranaghan et al.'s spread of the enzyme barrier across functionals, from 7.30 (M06) to 20.0 kcal/mol (M06-2X), and the library copy of that paper is its Just Accepted manuscript.
- **What this check is not.** Whole numbers and counts were not traced by a script, and no second person has read the text. Every check is Claude's.

## References

- Agbaglo, Summers, Cheng and DeYonker, "The influence of model building schemes and molecular dynamics sampling on QM-cluster models: the chorismate mutase case study", *Phys. Chem. Chem. Phys.* 2024, 26, 12467.
- Bursch, Mewes, Hansen and Grimme, "Best-practice DFT protocols for basic molecular computational chemistry", *Angew. Chem. Int. Ed.* 2022, 61, e202205735.
- Claeyssens, Ranaghan, Lawan, Macrae, Manby, Harvey and Mulholland, "Analysis of chorismate mutase catalysis by QM/MM modelling of enzyme-catalysed and uncatalysed reactions", *Org. Biomol. Chem.* 2011, 9, 1578.
- Galbraith and Schaefer, "Concerning the applicability of density functional methods to atomic and molecular negative ions", *J. Chem. Phys.* 1996, 105, 862.
- Goerigk et al., "A look at the density functional theory zoo with the advanced GMTKN55 database for general main group thermochemistry, kinetics and noncovalent interactions", *Phys. Chem. Chem. Phys.* 2017, 19, 32184.
- Ranaghan et al., "Projector-based embedding eliminates density functional dependence for QM/MM calculations of reactions in enzymes and solution", *J. Chem. Inf. Model.* 2019, 59, 2063.
- Rienstra-Kiracofe, Tschumper and Schaefer, "Atomic and molecular electron affinities: photoelectron experiments and theoretical computations", *Chem. Rev.* 2002, 102, 231.
- Szefczyk, Mulholland, Ranaghan and Sokalski, "Differential transition-state stabilization in enzyme catalysis: quantum chemical analysis of interactions in the chorismate mutase reaction and prediction of the optimal catalytic field", *J. Am. Chem. Soc.* 2004, 126, 16148.

The GOCAT gradients of section 7.1 are quoted from the project's committed criteria document, `STAGE6_CRITERIA.txt`, which cites the GOCAT papers.
