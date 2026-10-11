# C4: unrelaxed reactants and band ends — what the literature says, and the way forward

- **First version:** 11 October 2026, afternoon. 18 of 35 C4 runs had finished.
- **Revised:** same evening, after reading in full the nine papers added to chorismate-refs (commit 28eec7b).

This is a discussion document. Nothing here is committed or pre-registered yet. It informs one decision — how step 3
should be run (Amendment 2) — and one longer-term question for the Phase 2 redesign.

**Rule followed.** Every literature statement below comes from a full paper in the library (the refs repo or the
project files) and is quoted with its location. Section 7 lists what is still missing; nothing below depends on those
papers.

---

## 1. The short answer

**The problem has a name.** It is the *local-minima problem* of minimisation-based QM/MM (Ryde 2016; Ryde 2017; Senn
& Thiel 2009; Himo 2017; Klähn et al. 2005).

- With hundreds of mobile waters there are effectively endless nearby minima, and a tighter minimisation finds a lower
  one.
- One water changing its hydrogen bonds shifts the energy by about 20 kJ/mol (≈ 5 kcal/mol). That is what C4 is
  seeing.
- Kästner et al. 2007 measured the same thing directly. Optimising an enzyme MD snapshot to standard (loose) criteria
  left the structure 23–24 kJ/mol above the minimum that tighter criteria reach, *in the same local minimum*.
- Phase 1's reactant optimisations started from MD snapshots and used thresholds that were comparable or looser (RMS
  2.0e-4 against 3.0e-4 Eh/bohr; max 1.0e-3 against 4.5e-4).

**Tighter convergence alone does not fix it.** A barrier is meaningful only if two things hold:

- the reactant and the transition state sit in **the same environment basin**;
- both ends are **converged to the same tightness**.

**Chorismate mutase work shows this is achievable.**

- Claeyssens et al. (2005, 2011) built every path outward from one relaxed transition-state structure, "with both the
  MM and QM systems fully and consistently optimized at each step". Re-optimising the reactant then moved it by less
  than 1 kcal/mol.
- Senn et al. (2009) built potential-energy profiles in BsCM forwards and backwards on 10 snapshots, with about 9850
  mobile atoms. The two directions agreed within **1.0 kJ/mol** for every snapshot.
- So, once the path is built consistently, the water network in this enzyme does not stop the end points from agreeing.

**Recommended: a TS-anchored forth-and-back (Amendment 2, §5).** It remains the option most likely to succeed, and the
new papers strengthen the case.

1. Relax the environment tightly around the existing climbing-image (CI) substrate, which is held fixed.
2. Re-optimise the reactant tightly from that environment.
3. Compare the result with the step-2 reactant. If the two agree within 1 kcal/mol, the barrier is consistent;
   otherwise run one more cycle.

This is the alternating scheme of Zhang, Liu & Yang (2000) and Senn & Thiel (2009). It is also Claeyssens' recipe
reduced to two points, and Ryde's (2016) "optimise the MM system for one state and use it for the others" combined with
his forth and back.

**The pre-registered NEB-CI "back" leg moves to a three-frame check.** Run on every frame as written, it would pair
tightly converged end points with a transition state whose surroundings are relaxed only to NEB thresholds. That
biases the barrier high.

**New from the reading — Phase 2 redesign.** The free-energy route (QM/MM-FEP, also called QM/MM-FE) is much closer to
reach than §4 of the first version said.

- The MM environment is *sampled* with the substrate frozen, so its contribution no longer depends on which local
  minimum a minimisation landed in.
- Kästner et al. 2006: QM/MM-FEP "is affordable at any level of QM theory where one can afford the geometry
  optimizations."
- It suits the designs, because designed charges are simply extra MM charges, and the water's response to them is
  sampled rather than frozen.

It is not a C4 fix, because C4 audits a potential-energy barrier against Claeyssens. It is a candidate for validating
the designs, worth a pilot after C4 (§6).

---

## 2. What C4 has shown so far (18 of 35 runs)

**Convergence thresholds** (RMS / max gradient):

| Protocol | Eh/bohr | kcal/mol/Å |
|---|---|---|
| Phase 1 reactant optimisation (ORCA L-Opt defaults) | 2.0e-4 / 1.0e-3 | 0.24 / 1.19 |
| C4 | 3.0e-5 / 1.0e-4 | 0.036 / 0.12 |
| Claeyssens 2005, MM atoms (RMS) | — | 0.10 |
| Zhang, Liu & Yang 2000, MM subsystem (RMS) | — | 0.10 |

Phase 1 was about 2.4× looser than the MM criterion used by both reference groups. C4 is about 2.8× tighter.

**Dips in the band.** In 27 of 30 frames, an image before the CI lies more than 0.5 kcal/mol below image 0, by up to
12.81 kcal/mol (c4_bands.tsv).

- Barrier from image 0: 13.22 ± 4.36 kcal/mol (sd).
- Barrier from the lowest image at or before the CI (k_low; this barrier is B): 17.10 ± 2.57 kcal/mol.

**Step 0 — tight re-optimisation of image 0** (the Phase 1 reactant). Falls in kcal/mol:

| Frame | Fall |
|---|---|
| 23268 | 16.84 |
| 42436 | 16.07 |
| 49592 | 11.24 |
| 44388 | 10.91 |
| 54795 | 10.90 |
| 33320 (no dip) | 11.56 |
| 41786 (no dip) | 4.58 |

That is 19–70 kJ/mol. For an MD-snapshot start, this is the same order as Kästner et al.'s 23–24 kJ/mol (§3.1).

**Step 2 — tight re-optimisation of k_low** (13 frames so far).

- dE_reopt ranges from −1.84 to −11.56 kcal/mol, so every frame fails A1.
- Every frame passes A2 (substrate within 0.11–0.20 Å of MD) and A3 (active region 0.08–0.16 Å RMS from image 0).
- In 10 of 13 frames the most-displaced atom is a water, moved 1.1–4.2 Å — large enough to change hydrogen-bond
  partners.

**Two observations matter for choosing a remedy.**

1. **The band's environment is shared but loose.** On the environment atoms, k_low is 0.022 Å RMS from the CI
   (median), against 0.074 Å for image 0 (GENERATOR_LOG.txt). So B pairs two images in essentially one environment.
   It is a *same-environment* barrier; its weakness is that neither end is a tightly converged stationary point.
2. **The tight minimiser lands in a reproducible basin.**
   - For frames 49592 and 54795, the S0 run (from image 0) and the S2 run (from k_low) started from different band
     images. Both ended at the same structure: RMS 0.003–0.004 Å, ΔE 0.00 kcal/mol.
   - Kästner et al. 2007 report the same behaviour: tightening the criteria reaches "the same local minimum".
   - So a forth-and-back scheme has something stable to converge to.

**What follows.**

- The Phase 1 reactants and band ends are under-relaxed by several kcal/mol, mostly in the water hydrogen-bond
  network.
- E_ci − E_min(S2) is not a barrier: it pairs a tightly relaxed reactant with an unrelaxed transition-state
  environment.
- The image-0 barriers are not barriers from a minimum either. In 27 of 30 frames, image 0 is not even the lowest point
  of its own band.

---

## 3. What the literature says

### 3.1 The problem is known, general, and of the size we see

- **Ryde 2016** (Methods Enzymol. 577, 119), §2.5, p. 130:
  - "it is essential that all distant groups remain in the same local minimum throughout a reaction sequence; otherwise
    the energy will be blurred by irrelevant energy components. For example, the total energy may change by 20 kJ/mol
    if a single water molecule at the periphery changes its hydrogen-bond pattern."
  - For a solvated protein, checking this by eye "is impossible—there are thousands of atoms and essentially an
    infinite number of local minima."
- **Ryde 2017** (10.1021/acs.jctc.7b00826), Introduction: one hydrogen bond far from the active site "affects the
  energy by ~20 kJ/mol in a way that most likely is irrelevant for the reaction."
- **Klähn, Braun-Sand, Rosta & Warshel 2005** (J. Phys. Chem. B 109, 15645), Ras·GAP, five MD configurations:
  - p. 15648: "the absolute energies of the ground state can easily vary by 30 kcal/mol between different protein
    configurations"; for barriers, "the variation is about 6 kcal/mol, which is large but can be used in some
    qualitative considerations. Unfortunately this is only the tip of the iceberg."
  - p. 15649: "energy minimization studies might miss the contribution from the protein reorganization energy", and
    "QM/MM minimization and scanning approaches should involve averaging (and validation) over several protein
    configurations generated by long MD simulations."
- **Kästner, Thiel, Senn, Sherwood & Thiel 2007** (J. Chem. Theory Comput. 3, 1064):
  - p. 1068: "Since many close-lying minima are present in complex systems, different optimizers take different paths
    and may converge to different local minima. This happened in all four cases in Table 1."
  - pp. 1069–1070, PHBH from an MD snapshot: the standard optimisation (max gradient 4.5e-4 au) "yields a minimum that
    is 23-24 kJ mol-1 higher in energy. This is caused by the relatively loose convergence criteria". With criteria 3×
    tighter, it "does reach the same local minimum".
  - p. 1070, by contrast: starting from a structure already optimised near the TS, tighter MM convergence lowered the
    energy by only 0.04 kJ/mol.
  - Conclusion: the problem is largest "for systems in which the MM part as well as the QM part are far from the
    minimum, as is often the case for MD snapshots as starting points."
  - **What this shows.** Phase 1's reactant optimisations were exactly that case: an MD snapshot with loose thresholds.
- **Senn & Thiel 2009** (Angew. Chem. Int. Ed. 48, 1198), §3.1, p. 1206: configuration space "drastically reduces the
  significance of single stationary points." Citing Klähn et al., "at least several 'representative' transition
  states should be considered along with their corresponding minima."
- **Senn, Kästner, Breidung & Thiel 2009** (Can. J. Chem. 87, 1322), p. 1323: a stationary point from minimisation
  "will be just one of very many of similar energy, and one cannot assume it to be the representative structure."
- **Himo 2017** (10.1021/jacs.7b02671), on QM-cluster models: "When one starts to approach models of more than 300
  atoms, however, one issue that arises is the multiple minima problem, and one has to be very careful to assure that
  no artificial movements take place between the various stationary points". The C4 active region has 1959 atoms.

### 3.2 How the chorismate-mutase work avoided it

- **Claeyssens et al. 2005** (Chem. Commun. 5068):
  - p. 5068: full minimisations to RMS gradients below 0.1 kcal/mol/Å (MM) and 0.002 Eh/Å (QM), in a 25 Å sphere with
    the outer 5 Å fixed.
  - p. 5069: each snapshot was "fully optimized … while restraining the reaction coordinate, r, to −0.3 Å". Paths were
    built "by restrained optimizations in both directions … with both the MM and QM systems fully and consistently
    optimized at each step"; reactant re-optimisation gave "energy differences below 1 kcal mol⁻¹".
- **Claeyssens et al. 2011** (Org. Biomol. Chem. 9, 1578; project file 2011_paper.pdf), Methods: the same scheme;
  reactant re-optimisation "gave structures very similar to the lowest energy restrained structures (and energy
  differences less than 1 kcal mol⁻¹)".
  - **The key design point.** Every structure on their path descends from one relaxed transition-state structure.
    Phase 1 instead optimised reactant and product separately and joined them by a band (CLAEYSSENS_COMPARISON.md §3;
    audit item B1).
- **Senn et al. 2009** (Can. J. Chem. 87, 1322), BsCM, SCC-DFTB/CHARMM22, 10 snapshots, about 9850 mobile atoms:
  - p. 1329: structures "were energy-minimized and then subjected to reaction-path calculations … in both the forward
    and backward direction."
  - p. 1332: "The difference between forward and backward scan for a given snapshot is at most 1.0 and 0.5 kJ mol–1
    for Δ‡E and ΔrE". The barriers spread from 21.8 to 38.7 kJ/mol (sd 5.3).
  - **What this shows.** In this enzyme, a consistently built adiabatic path has essentially no hysteresis, even with a
    large mobile water region.
- **Ranaghan et al. 2004** (Org. Biomol. Chem. 2, 968):
  - Methods: restraining the outer regions raised the barrier by 3.0 kcal/mol (AM1 test).
  - Glu78 discussion: a hydrogen bond formed late on the path, "probably because of the limited minimization
    possible". So how much the environment relaxes moves this enzyme's barrier by several kcal/mol.

### 3.3 The remedies, now with their working details

- **Forth and back.**
  - Ryde 2016 (§2.5, p. 130): "run calculations forth and back between each pair of states … until the energy
    differences are constant."
  - **Zhang, Liu & Yang 2000** (J. Chem. Phys. 112, 3483), the earliest worked example:
    - The forward path was mapped from the reactant, then the backward path from the product, with every point
      optimised by their iterative scheme.
    - p. 3490: "the forward reaction path differs very little with the backward reaction path."
  - **Kästner et al. 2006** (J. Chem. Theory Comput. 2, 452), p. 457, showing what forth and back can catch: "Stepwise
    backward optimization resulted in a second minimum … which is 8.5 kJ mol-1 lower than the first local minimum … The
    system thus shows a hysteresis … The hydrogen bonds change but do not contribute to the reaction coordinate."
- **The alternating (and adiabatic) scheme.**
  - Zhang, Liu & Yang 2000, p. 3486. Steps:
    1. optimise the QM part with the MM atoms fixed;
    2. optimise the MM part with the QM atoms fixed;
    3. repeat "until both meet convergence criteria at the same geometry."
  - p. 3489: with MM convergence at RMS < 0.1 kcal/mol/Å for 3008 mobile atoms, it converged in "no more than eight
    cycles", with the energy falling monotonically.
  - Senn & Thiel 2009 (§3.2, p. 1206) describe the same pair of schemes: "adiabatic", where the environment is fully
    relaxed at each step, and "alternating".
  - **This is the logic of the proposed Amendment 2:** the T-step relaxes the environment with the substrate fixed, and
    the R-step relaxes everything.
- **Microiterations** (Kästner et al. 2007). The environment is relaxed with an ESP-charge model of the QM density
  between QM steps; the reported gain is "typically a factor of 2-10".
  - The ORCA 6.0 manual's QM/MM page (faccts.de) mentions a microiterative scheme only in its Gromacs-interface section,
    not for ORCA's own QM/MM optimiser. Unless the 6.0.1 manual on hpc1 says otherwise, it is **not available** to our
    current setup without changing the MM engine.
- **A smaller relaxed region** (Ryde 2016 §2.5; Himo 2017). Fewer minima, but Ryde warns of missing "the dielectric
  relaxation of the surroundings".
  - Cooper & Kästner 2014 (ChemPhysChem 15, 3264), §2: their own standard protocol relaxes "Whole residues … with at
    least one atom within 8 Å" (about 360 atoms) with the rest frozen at MD positions.
- **One environment for all states** (Ryde 2016 §4 item 7). Rod & Ryde 2005 (J. Chem. Theory Comput. 1, 1240), p. 1248,
  show how much this choice can matter:
  - With the MM environment fixed at a reactant-complex configuration, the barriers were 59 (forward) and 47
    (reverse) kJ/mol.
  - With it fixed at a product-complex configuration, they were 26 and 96 kJ/mol.
  - QTCP gave 56 and 78 kJ/mol.
  - "sampling of one complex does not sample important contributions to the free energy of the other complex."
  - **Why this matters.** A fixed-environment barrier is informative, but on its own it is not *the* barrier.

### 3.4 Free energies: the cure, and what it costs

- **Ryde 2016** §2.5, pp. 130–131: "The proper way to cure it is to calculate free energies."
- **QM/MM-FE / QM/MM-FEP** (Zhang, Liu & Yang 2000; Kästner et al. 2006; Senn et al. 2009). How it works:
  - Take the optimised path, freeze the QM atoms at each point, and fit ESP charges to them.
  - Run MM molecular dynamics of the environment.
  - Compute the free-energy step between neighbouring points by exponential averaging of the classical
    interaction-energy change.

  Its main properties, from those papers:
  - **It removes the minimum-dependence of the environment term.** Zhang et al. (p. 3486): when MM rearrangements are
    "too large to be captured by local minimization", the MM energy at a single configuration "may be not related to the
    reaction", but in the FEP scheme "the contribution of the MM subsystem to the free energy change along the reaction
    coordinate will be sampled by molecular dynamics simulations."
  - **Cost.** Kästner et al. 2006 (p. 460): "When ESP charges are used, the computer time required for the geometry
    optimizations exceeds the time required for the MD simulations … QM/MM-FEP is affordable at any level of QM theory
    where one can afford the geometry optimizations."
  - **Accuracy.**
    - Senn et al. 2009, Table 1 (PHBH, AM1): FEP with ESP charges gave 108 kJ/mol, against 101 and 102 from
      thermodynamic integration and umbrella sampling.
    - Kästner et al. 2006 (p. 458): FEP "accounts for some but not all of the differences between optimization on one
      hand and TDI or US on the other hand" (optimisation gave 112.3).
  - **What remains.** The QM path itself still comes from one minimisation. Hu, Lu & Yang 2007 (J. Chem. Theory Comput.
    3, 390), Abstract: QM/MM-FE "depend[s] on the determination of the minimum-energy reaction path, which is based on
    local conformations of the protein/solvent environment".
    - Their minimum-free-energy-path method removes this, but each optimisation step needs 40–128 ps of MD per image
      (p. 398), in custom code.
- **QTCP** (Rod & Ryde 2005, Phys. Rev. Lett. 94, 138302 and J. Chem. Theory Comput. 1, 1240) adds QM/MM single points
  on MM snapshots to correct the classical model.
  - Converged barriers needed ~200–400 snapshots per point (p. 1246; about 20 already gave the barrier height nearly).
  - In 2005, 4000 QM/MM single points cost "approximately 8 CPU days" with PBE/RI (p. 1247).
  - QM/MM-FE was within about 1–10 kJ/mol of QTCP (p. 1249).
- **For chorismate mutase specifically** (Senn et al. 2009, pp. 1332–1334):
  - Mean potential-energy barrier 27.5 ± 1.2 kJ/mol; umbrella-sampling free-energy barrier 36.5 ± 0.8 kJ/mol.
  - The finite-temperature term (−9.0 ± 1.4 kJ/mol, mostly entropy of the tight pericyclic TS) matches experiment
    (TΔS‡ = −11.4 ± 1.5).
  - Conclusions: "QM/MM optimization studies may often provide barriers that are close to the corresponding
    free-energy barriers"; with "an error bar of about 10 kJ mol–1 for (free) energy differences obtained on a single
    snapshot" (p. 1334).
  - **What this means for C4.** A consistently optimised potential-energy barrier is a meaningful quantity for this
    enzyme. That is what C4 should deliver.
- **Direct DFT-level sampling** (Li & Chan 2025, J. Chem. Theory Comput. 21, 803) runs at "~1000 MD steps per day on a
  single GPU". It is out of reach on 8-core CPU jobs.

### 3.5 Why the water must stay mobile once designs are in

- **Dubey et al. 2020** (10.1021/jacs.9b13029): solvent "molecules adjacent to the cavity reorganize as the reaction
  proceeds so that the reacting complex is optimally stabilized at each step". Fixing them "will obviously hamper the
  ability of the solvent to produce such a catalyzing oriented field."
- **Rod & Ryde 2005**, Conclusion: "a significant polarization of the environment occurs as the reaction progresses.
  For that reason relaxation of the MM environment is important".
- **Implication.** Freezing water to suppress local-minimum noise would also remove a real, design-dependent response.
  Freezing is a sensitivity test, never the production protocol for designs.

### 3.6 Combining frames (relevant to step 4, not a fix)

- **Cooper & Kästner 2014** (force-field mimic of QM/MM, cyclophilin A, 65 snapshots), Table 1:
  - free energy (umbrella sampling) 75.9 ± 1.0 kJ/mol;
  - arithmetic mean of minimised barriers 119.9;
  - exponential average 87.5;
  - lowest single barrier 77.1.
- They conclude that an exponential average of a few snapshots "close to the transition state" works best, and that
  "The total energies of the reactant minima are irrelevant for the averaging."
- **For C4.** Step 4's arithmetic mean is reported as a potential-energy barrier (like Claeyssens), not as a free
  energy. Ryde's (2017) cumulant estimate is reported beside it. Nothing needs to change, but the thesis should say
  this.

---

## 4. The options compared

### A. Pre-registered step 3 as written

- **What:** the product is placed in the S2 environment; then NEB-CI back.
- **Literature:** Ryde's forth and back.
- **Cost:** 30 tight product optimisations, 30 NEB-CI runs (167–216 GB each in Phase 1), and step-2 reruns.
- **Main risk:** the CI environment is relaxed only to NEB thresholds while the end points are tight, so the barrier
  is biased high.
- **Verdict:** not on its own.

### B. A, plus a TS-end check after the NEB

- **What:** as A, then relax the environment around the new CI.
- **Literature:** as A, plus Claeyssens' "consistently optimized".
- **Cost:** A plus 30 more optimisations.
- **Main risk:** the same machinery risk as A, at the highest cost.
- **Verdict:** works, but it is the most expensive route.

### C. TS-anchored forth and back (recommended)

- **What:** relax the environment around the existing CI with the substrate fixed; re-optimise the reactant from it;
  compare; cycle.
- **Literature:**
  - Zhang 2000 and Senn & Thiel 2009 (the alternating scheme);
  - Claeyssens 2005/2011 (paths outward from a relaxed TS; reactant check below 1 kcal/mol);
  - Senn et al. 2009 (BsCM forward and backward within 1 kJ/mol);
  - Ryde 2016 §4 item 7 and §2.5.
- **Cost:** about 2 tight optimisations per frame per cycle (20–35 h each). That is roughly 3 days of wall time per
  cycle with the frames in parallel. A full NEB is needed only on the three check frames.
- **Main risks:**
  - The substrate is held at the old CI geometry. This is a second-order error, and it is measured on the check frames.
  - The water may not settle. Senn et al. 2009 make this unlikely for this enzyme.
- **Verdict:** the most likely to succeed.

### D. Full adiabatic mapping (Claeyssens / Senn exactly)

- **What:** restrained optimisations every 0.1–0.2 Å, outward from the TS.
- **Literature:** Claeyssens; Senn et al. 2009; Zhang 2000; Ranaghan 2004.
- **Cost:** about 20 sequential tight optimisations per frame, which is weeks. ORCA 6.0 restrains two distances only,
  not their difference (HANDOFF.md).
- **Main risks:** the cost; and it gives up the NEB-CI saddle point (audit item B2).
- **Verdict:** use it only if C fails because the two-point jump is too large.

### E. Smaller relaxed region (step 5, 6 Å)

- **What:** fewer mobile atoms, so fewer minima.
- **Literature:** Ryde §2.5; Himo 2017; Cooper & Kästner's 8 Å protocol.
- **Cost:** 3 frames.
- **Main risks:** misses dielectric relaxation; changes the model; would mute the water's response to designs.
- **Verdict:** a sensitivity test, as pre-registered.

### F. One environment for all states

- **What:** the barrier with the environment frozen at the reactant's or at the TS's relaxed structure.
- **Literature:** Ryde 2016; Rod & Ryde 2005 (59/47 versus 26/96 kJ/mol).
- **Cost:** 2 single points per frame, almost free inside C.
- **Main risk:** it leaves out reorganisation.
- **Verdict:** report it as an informative bracket only.

### G1. QM/MM-FEP (QM/MM-FE) on the consistent paths

- **What:** frozen-QM ESP charges at each band image, MM MD of the environment, and classical FEP between images.
- **Literature:** Zhang 2000; Kästner 2006; Senn 2009; Rod & Ryde 2005.
- **Cost:**
  - one QM/MM single point per image for the ESP charges;
  - MM MD per image (Kästner et al. 2006 used 10–20 ps per window; Zhang et al. 2000 used 50 ps);
  - a scripted FEP analysis.
  - All of this is within the existing Amber and ORCA setup.
- **Main risks:**
  - The QM path still comes from one minimisation (Hu 2007).
  - A frozen-QM bias of a few kJ/mol (Senn 2009, Table 1).
  - New code: ESP fitting, frozen-substrate MD, and the energy-difference script (cpptraj is broken on the cluster).
- **Verdict:** a strong candidate for validating the designs. Pilot it after C4.

### G2. QTCP or minimum free-energy path

- **What:** G1 plus QM/MM single-point corrections (QTCP), or a path optimised on the free-energy surface (MFEP).
- **Literature:** Rod & Ryde 2005; Hu, Lu & Yang 2007.
- **Cost:**
  - QTCP: about 20–400 QM/MM single points per image.
  - MFEP: 40–128 ps of MD per image per optimisation step, in custom code.
- **Main risk:** much more method work.
- **Verdict:** only if G1 proves insufficient.

### H. Better averaging only (step 4)

- **What:** combine the frames more carefully.
- **Literature:** Ryde 2017; Cooper & Kästner 2014.
- **Cost:** free.
- **Main risk:** it does not fix a single frame.
- **Verdict:** keep as pre-registered.

### Why C over A or B

- Every leg of C is the kind of tight optimisation C4 is already running. 18 have finished so far, and the amended
  start-energy check (M2) passed for all of them.
- A and B add a new NEB-CI per frame. That is the expensive step, and it is the one whose loose environment
  convergence caused the problem.
- C also measures directly how far the transition state's surroundings were from relaxed.
- The literature now supports C's specific structure as well as its aim:
  - Zhang et al. 2000: the alternating scheme converged in at most 8 cycles, and the forward and backward paths agreed.
  - Senn et al. 2009: forward and backward scans in BsCM agreed within 1 kJ/mol.

---

## 5. Recommendation: Amendment 2, TS-anchored forth and back (draft rules)

Exact wording is to be fixed at pre-registration.

### For each frame that fails step 2

1. **T1 — forth to the transition state.**
   - Start from the final band's CI geometry (the converged geometry, per Amendment 1).
   - Hold the substrate (QM atoms 6207–6230) fixed and optimise the other 1935 active atoms to the step-2 thresholds.
   - Report fall_T = E_ci − E(T1).
2. **R2 — back to the reactant.**
   - Start from T1's final coordinates, with the substrate replaced by k_low's substrate from the same band.
   - Optimise all 1959 active atoms to the step-2 thresholds.
3. **Test:** |E(R2) − E(S2 end point)| ≤ 1.0 kcal/mol.
   - This is Ryde's "until the energy differences are constant": the barrier must be the same whichever reactant
     minimum is used. It is also Claeyssens' "less than 1 kcal mol⁻¹".
   - If it holds, **B3 = E(T1) − E(R2)**.
4. **Otherwise, one more cycle.**
   - T2 starts from R2's environment, with the substrate at the CI.
   - R3 starts from T2.
   - The test becomes |E(R3) − E(R2)| ≤ 1.0, and then B3 = E(T2) − E(R3).
5. **Still failing after two cycles:** the frame is *unresolved* and recorded with every number. If more than 3 of the
   30 frames are unresolved, stop and revisit — the pre-registered rule, unchanged.
6. **Guards.**
   - M1 applies to every run.
   - M2 applies to T1 (its first energy must equal E_ci).
   - A2 (substrate within 0.30 Å of MD) applies to every R run.
   - For every T run, report the environment's RMS change and its most-displaced atom.

### The TS-geometry check (replaces the NEB-CI back leg, on a subset fixed now)

- **Frames:** 23268, 42436 and 44388 (the step-5 frames).
- **Procedure:**
  1. Optimise the product in the final T environment.
  2. Run NEB-CI (C5 thresholds) between the final reactant and that product.
  3. Run a T-step on the new CI.
- **Holds if** the resulting barrier is within 1.0 kcal/mol of B3 in at least two of the three frames. Otherwise the
  largest difference is reported as an uncertainty, and the NEB leg is extended to every frame.

### Informative, not barriers (2 single points per frame)

- The substrate at the CI in the final reactant's environment.
- The substrate at the final reactant geometry in the final T environment.

These give the barrier with the environment frozen at either end. Their difference is the environment's reorganisation
contribution. Rod & Ryde 2005 show this bracket can be wide.

### Step 5 (6 Å region)

Its NEB-CI gets the same T-step, so the comparison is on equal terms.

### Reporting

One table per frame, with nothing dropped silently:

- the image-0 barrier;
- B (k_low);
- B3;
- every fall;
- every cycle.

### Why this cannot push the barrier the way we want

- The rules are fixed before any step-3 result exists.
- Both ends are tightened to identical thresholds.
- B3 can come out above or below B.
- The reason for the change is methodological, and it is stated together with the 18 results already seen, as
  Amendment 1 did.

### Cost and timing

- About 60 tight optimisations per cycle, at most two cycles, plus the three-frame NEB check.
- Roughly one to two weeks of wall time.
- Commit the amendment before step 3's inputs are generated; they still wait for step 2 to finish, as pre-registered.

### Smoke test first

The T-step holds QM atoms fixed while their environment moves. The ORCA 6.0 manual does not state whether QM atoms may
be left out of the active atoms. It does list L-Opt fragment options ("Freeze the coordinates of all atoms of the
specified fragments").

- Test both routes in two short jobs, as x67 did.
- Check that the substrate does not move and that the energy and gradients behave.

### A diagnostic that costs nothing (fold into x69)

For every finished run, compare each atom's displacement (start → end) with its distance from the substrate and from
the edge of the active region.

- If the relaxation sits at the periphery, it is Ryde's "irrelevant energy components", and B3 ≈ B is expected.
- If it sits in the first solvation shell, it is real reorganisation around the substrate, and it will matter for the
  designs.
- Kästner et al. 2007's contrast — 23–24 kJ/mol from an MD snapshot, against 0.04 kJ/mol from an already optimised
  structure — suggests most of it is generic snapshot relaxation. The diagnostic tests that.

---

## 6. What this means downstream

- **The Phase 1 barrier.**
  - The image-0 values (13.22 ± 4.36) should not be used as barriers.
  - B (17.10 ± 2.57) is the better current estimate.
  - If B3 ≈ B, B stands with the justification it currently lacks; if not, B3 replaces it.
  - Senn et al. 2009 support quoting a consistently optimised potential-energy barrier for this enzyme. Their
    finite-temperature term (about −9 kJ/mol, ≈ −2.2 kcal/mol) is the size of the gap between a potential-energy
    barrier and the experimental ΔG‡. This belongs in audit item C1, not in C4.
- **The spread.**
  - Changing only the reference point took the sd from 4.36 to 2.57 kcal/mol.
  - Senn et al. 2009 found sd 5.3 kJ/mol (1.3 kcal/mol) for consistent profiles on snapshots 10 ps apart. Claeyssens
    2005 found σ 1.7 kcal/mol.
  - Our frames span 20 ns, so some extra spread is real. Consistent end points should still narrow it, and that matters
    for step 4 (Ryde 2017).
- **Phase 2 redesign.**
  - Whatever passes here becomes the validation protocol for designs: each design paired with the bare substrate in
    the same frame and environment lineage, with water mobile.
  - **Proposed after C4:** a QM/MM-FEP pilot (option G1) on 2–3 frames using the Amendment-2 paths.
    - It gives a free-energy barrier in which the environment is sampled rather than minimised.
    - It is directly comparable with B3 and with Senn et al.'s BsCM free energies.
    - If it works, design charges enter simply as extra MM charges in the MD.
  - This is a deviation from the current Phase 2.2 plan. It should be decided on the pilot's evidence, with its own
    pre-registration.

---

## 7. Papers

### Read in full this evening (chorismate-refs 28eec7b)

| Paper | DOI |
|---|---|
| Klähn et al. 2005 | 10.1021/jp0521757 |
| Zhang, Liu & Yang 2000 | 10.1063/1.480503 |
| Kästner et al. 2007 | 10.1021/ct600346p |
| Senn, Kästner, Breidung & Thiel 2009, Can. J. Chem. 87, 1322 | 10.1139/V09-092 (confirmed on the paper) |
| Rod & Ryde 2005, Phys. Rev. Lett. | 10.1103/PhysRevLett.94.138302 |
| Rod & Ryde 2005, J. Chem. Theory Comput. | 10.1021/ct0501102 |
| Kästner et al. 2006 | 10.1021/ct050252w |
| Hu, Lu & Yang 2007 | 10.1021/ct600240y |
| Cooper & Kästner 2014 | 10.1002/cphc.201402382 |

### Still outstanding — context only; nothing above depends on them

| Paper | DOI |
|---|---|
| Lonsdale, Harvey & Mulholland 2012, Chem. Soc. Rev. 41, 3025 | 10.1039/c2cs15297e |
| van der Kamp & Mulholland 2013, Biochemistry 52, 2708 | 10.1021/bi400215w |
| Ranaghan & Mulholland 2010, Int. Rev. Phys. Chem. 29, 65 | DOI not verified |
| Hu, Söderhjelm & Ryde 2011 | 10.1021/ct100530r |
| Sumner, Söderhjelm & Ryde 2013 | 10.1021/ct400339c |
| Ásgeirsson et al. 2021 (ORCA NEB-TS) | 10.1021/acs.jctc.1c00462 |

Before a QM/MM-FEP pilot is planned, these two would also help:

- Hu & Yang 2008, Annu. Rev. Phys. Chem. 59, 573 — 10.1146/annurev.physchem.59.032607.093618 (DOI from Senn et al.'s
  reference list). A review of free-energy methods for ab initio QM/MM.
- Senn, Thiel & Thiel 2005, J. Chem. Theory Comput. 1, 494 (PHBH thermodynamic integration). DOI not verified.

Earlier requests still open:

- Lin 2013 — 10.1021/ct300715s
- Cohen 2008 — 10.1126/science.1158722
- Chai & Head-Gordon 2008 — 10.1039/b810189b

---

## 8. Library sources used

**Read for the first version.** Ryde 2016 (bs.mie.2016.05.014); Ryde 2017 (acs.jctc.7b00826); Senn & Thiel 2009
(anie.200802019); Himo 2017 (jacs.7b02671); Warshel et al. 2006 (cr0503106); Claeyssens et al. 2005 (b508181e);
Claeyssens et al. 2011 (project file 2011_paper.pdf); Ranaghan et al. 2004 (B313759G); Behrens & Hartke 2021
(s11244-021-01486-1); Dittner 2019 thesis (gocat_2); Dubey et al. 2020 (jacs.9b13029); Li & Chan 2025 (ct4c01698).

**Added in the revision.** jp0521757, 1.480503, ct600346p, v09-092, PhysRevLett.94.138302, ct0501102, ct050252w,
ct600240y, cphc.201402382.

**Checked online.** The ORCA 6.0 manual, QM/MM chapter (faccts.de), for microiterations and frozen atoms.

**C4 numbers.** c4_bands.tsv, C4_CRITERIA.txt, GENERATOR_LOG.txt, and the 18-run analysis output of 11 October.
