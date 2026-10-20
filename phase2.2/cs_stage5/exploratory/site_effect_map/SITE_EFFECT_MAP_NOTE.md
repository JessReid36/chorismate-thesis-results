# Site-effect map (development set, exploratory)

`phase2.2/cs_stage5/exploratory/site_effect_map/chorismate_site_effect_map.html` is an interactive page. It shows where, around the substrate, a charged sphere lowers or raises the reaction barrier, and how strongly. It is a picture of the development set built for designing the optimiser. **It is not a result and nothing in it is quoted as one.** The file is self-contained: open it in any browser, offline included. Offline, the text falls back to the system font; everything else is unchanged.

Built 20 October 2026 by `phase2.2/site_effect_map/` (code tier1-realism f070222), and rebuilt byte for byte on Jessica's PC before it was committed (`BUILD_RECORD.txt`).

## What is plotted

**The quantity.** Each point is a sphere centre on the development grid. Its colour and size give the first-order change in barrier for a sphere of charge q at that site:

- change in barrier = q × a, with a = V_TS − V_R, the substrate's electrostatic potential at the site at the transition state minus that at the reactant;
- averaged over the 30 Phase 1 band frames.

Because the change is first order at frozen geometry, a −1 sphere has exactly the opposite effect of a +1 sphere at the same place. The steric term L and polarisation are not included. Green means close to no effect; red means a large one (|change| up to 7.5 kcal/mol on the scale).

**The layout.** Two rows: spheres that lower the barrier, and spheres that raise it. Each row pairs a 3D view (where) with a ranking (how much, with ±1 sd across the 30 frames as a band). The two 3D views turn together and share one box, so the molecule sits in the same place at the same scale everywhere. Clicking a point pins that site: it turns purple in 3D, is ringed in the ranking, and a dotted line joins it to its nearest substrate atom.

**The controls.**

| Control | Options |
|---|---|
| Sphere charge | +1 e, −1 e, or both overlaid |
| Substrate shown | Reactant or transition state (the enzyme residues follow) |
| Layer | Both, cation layer, anion/neutral layer |
| Spheres | All sites, or the strongest 50 per row |
| Enzyme residues | Show or hide |

## The sites

These are the 2769 development sites of `exploratory/dev_sites_a2.tsv`, with the admissions of Stage 5 Amendment 2: charges ≤ 0 only on the anion/neutral layer. There are 1541 sites on the anion/neutral layer and 1228 on the cation layer.

| Sphere | Sites that admit it | Lower the barrier | Raise it | Strongest lowering | Strongest raising |
|---|---|---|---|---|---|
| +1 e | 2552 | 1339 | 1213 | −7.14 kcal/mol | +7.53 kcal/mol |
| −1 e | 1541 | 722 | 819 | −4.86 kcal/mol | +4.93 kcal/mol |

- The 217 anion/neutral-layer sites beside H8 admit no positive charge.
- Of the 50 strongest +1 sites that lower the barrier, 36 are nearest the ether oxygen O3. Of the 50 strongest that raise it, all are nearest a ring carboxylate oxygen (34 at O6, 16 at O5).
- The strongest +1 lowering site varies from −9.84 to −4.97 kcal/mol across the 30 frames. The median sd across frames is 0.9 kcal/mol.

## The substrate

The page draws frame 20000, the alignment reference, at its reactant (NEB image 0) or transition state (the climbing image), from `phase2.2/aligned/frame_20000/`. In the transition state, dashed lines mark the bond that breaks, O3–C4 (2.08 Å), and the one that forms, C1–C6 (2.44 Å). The grid encloses R, TS and P of all 30 frames, so some sites sit off this one frame's surface.

## The enzyme residues

**Which.** The six charged active-site residues that Stage 4d analyses after Szefczyk et al. (2004):

- Arg90, Arg7, Glu78 and Arg116 of chain B (residues 217, 134, 205 and 243 in the system's numbering);
- Arg63′ and Lys60′ of chain A (63 and 60). The prime marks the other subunit.

Each side chain is drawn from CA outwards with its hydrogens, as ball and stick in the substrate's colours, with nitrogen teal. Labels use the 3D axis titles' font and size (IBM Plex Sans, 11).

**Extracted exactly as the substrate.** The substrate the page draws is frame 20000's NEB image 0 (R) and climbing image (TS). The residues come from the same two structures:

- `05_qmmm/19_ensemble/frame_20000/neb_MEP.activeRegion_trj.xyz.xz` (image 0);
- `neb_NEB-CI_converged.activeRegion.xyz.xz` (the climbing image).

These hold the 1959 optimised atoms ORCA wrote around the substrate. They were brought down from hpc1 by x89 (results 9880ac3) and checked there against their recorded sha256. They are placed with frame 20000's committed alignment transform. Check: in all 30 frames, at R and at TS, the substrate inside these structures, placed with that frame's transform, equals the aligned substrate within 5×10⁻⁹ Å.

**What they show.** The expected contact network:

- Arg90 hydrogen-bonds the ether O3 (1.80 Å at R, 1.75 Å at TS) and O2;
- Arg7 bridges O1 and O2;
- Arg63′ binds the ring carboxylate (O5, O6);
- Glu78 takes the hydroxyl hydrogen H8 (1.53 Å);
- Arg116 and Lys60′ sit about 7 Å from the substrate.

The residues move only a little between R and TS: at frame 20000 the charge centres move 0.00–0.05 Å and single atoms up to 0.07 Å. The median over the 30 frames is at most 0.09 Å per residue. Across the 30 frames, a charge centre varies by 0.6 Å (Arg90) to 3.0 Å (Lys60′), rms.

**Colour: the literature's ranking of catalytic importance.** Each residue's carbons and sticks are coloured by rank, red (1, most) to green (6, least), on the page's ramp. The rank is also printed in each label, so nothing depends on colour alone.

| Rank | Residue | Szefczyk et al. 2004, Table 1: MP2 differential TS stabilisation | Claeyssens et al. 2011, Table 3: electrostatic TS stabilisation, mean ± sd over 16 pathways |
|---|---|---|---|
| 1 | Arg90 | −9.06 | 6.0 ± 0.8 |
| 2 | Arg7 | −5.90 | 3.1 ± 0.5 |
| 3 | Glu78 | −3.57 | 2.1 ± 0.3 |
| 4 | Arg116 | −2.45 | 1.0 ± 0.9 |
| 5 | Arg63′ | −1.40 | −0.6 ± 0.5 |
| 6 | Lys60′ | +1.39 (raises the barrier) | not reported |

All values are in kcal/mol. In Szefczyk's column, negative lowers the barrier; in Claeyssens', positive stabilises the TS. The sources are Szefczyk, Mulholland, Ranaghan & Sokalski, J. Am. Chem. Soc. 2004, 126, 16148 (10.1021/ja049376t), and Claeyssens et al., Org. Biomol. Chem. 2011, 9, 1578 (10.1039/c0ob00691b). Both were read in full from the library.

Szefczyk et al. order their residues by the MP2 value. Claeyssens et al. give the same order for the five they report, and `prep.py` stops if the two disagree.

Caveats, also on the page:

- Glu78's value depends strongly on the hydroxyl's orientation and distance (−8.70 to +7.33 kcal/mol, Szefczyk Tables 2–3).
- Arg63's sign changes between Szefczyk's theory levels, and on average it slightly destabilises the TS in Claeyssens'.
- At the simplest electrostatic levels Arg7 edges out Arg90.
- This is the literature's ranking, not this project's. Stage 4d at frame 41786 differs in sign for Arg7 and Arg116 (`cs_stage4d/STAGE4D_REPORT.txt`, PC2).

Not used for the ranking:

- Agbaglo et al. 2024: their F-SAPT energies rank binding to the substrate, not catalysis.
- Mutagenesis: as quoted in these papers, it covers Arg90, Arg7 and Glu78 only.

## Inputs

| Input | Results commit |
|---|---|
| `phase2.2/cs_stage5/exploratory/dev_sites_a2.tsv` (sites, layers, admitted charges; sha256 43be59bc…) | 269f54b |
| `phase2.2/cs_stage5/exploratory/dev_A/A_dev.tsv` (a for each site and frame) | 6edfbb1 |
| `phase2.2/aligned/frame_N/` (substrate R and TS, transforms) | c923910 |
| `05_qmmm/19_ensemble/frame_N/neb_MEP.activeRegion_trj.xyz.xz`, `neb_NEB-CI_converged.activeRegion.xyz.xz` | 9880ac3 |
| `05_qmmm/19_ensemble/frame_N/neb.inp` (active-atom lists) | 0bee292 |
| `03_amber/tleap_build/complex_solvated.prmtop` (names, charges, elements) | 05c878e |

Plotly is plotly.js-dist-min 2.35.2 (MIT licence), inlined. The sha256 of its `plotly.min.js` is pinned in `build.py`.

## Limits

- Exploratory and development-set only: the sites, A and frames are the development ones, not Stage 5 production.
- First order at frozen geometry: no relaxation, no polarisation, no steric term L.
- A design is judged only by a relaxed NEB-CI barrier, never by this picture.
- The residues are for orientation. They show where the enzyme puts its own charges in one frame, and they are not grid sites.

## Rebuilding

From the code repo, with the results repo and `plotly.min.js` (plotly.js-dist-min 2.35.2):

```
python3 phase2.2/site_effect_map/residues.py <results_repo> <work_dir>
python3 phase2.2/site_effect_map/prep.py     <results_repo> <work_dir>
python3 phase2.2/site_effect_map/build.py    <work_dir> <plotly.min.js>
```

This writes `residues.json`, `RESIDUES_LOG.txt`, `data.json`, `site_effect_map.html` (Plotly from the CDN) and `chorismate_site_effect_map.html` (the committed offline page). Built with python 3.13 / numpy 2.5.3 and python 3.12.3 / numpy 1.26.4, the page is byte-identical.

## History (20 October 2026)

1. The map first used the Stage 5 Amendment 2 admissions, so −1 spheres sit on one layer only (1541 sites).
2. A first residue layer drew squares at charge centres averaged over the MD snapshots each frame's optimisation started from. It was withdrawn: those were not the structures the substrate comes from. The squares sat 0.5–2.8 Å from the positions now drawn.
3. The residues were redrawn as ball and stick from the NEB structures (x89), at R and TS.
4. They were coloured by the literature's ranking.

The 3D axis titles now carry their units ("x / Å"), which a style setting had been overwriting.
