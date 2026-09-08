# GRID_DESIGN_DECISIONS.md

Working note for the candidate-grid section of the methods chapter. Records the
design choices, the numbers behind them, and what the prose must say.

**Framing.** The chapter presents the grid as built and the comparison that
justified the placement method. It does not present a development history.
Earlier grids were initial development and are not referenced in the write-up,
in results, or in the submission manifest.

---

## 1. Two parameters, not one

Grid construction separates two requirements that are easy to conflate:

- **Resolution** — how finely a charge can be positioned. A property of the
  grid. Set by `--r-min`, and finer is better, limited only by problem size.
- **Separation** — how close two placed charges may sit. A property of the
  physical species being placed: roughly 3.5 Å centre-to-centre for formate,
  4.5 Å for guanidinium. Enforced as a constraint in the optimiser.

Keeping them separate makes the minimum separation an explicit, defensible model
parameter that can be varied per species, rather than an artefact of how the
grid was thinned. The grid is a menu of positions; the physics of how close two
groups may approach is stated in the optimisation problem.

---

## 2. The grid, as built

`02_grid_poisson.py --r-min 1.0 --shells 3.0 4.0 5.0 --density 6.0 --seed 0`

Union signed distance field over the pooled 72 atoms of the reactant, TS and
product; Bondi radii; 0.30 Å voxel; 5.0 Å margin. Shells extracted by marching
cubes at additive offsets of 3, 4 and 5 Å, sampled area-proportionally at 6.0
points Å⁻², then thinned globally by Poisson-disk elimination to a guaranteed
1.0 Å minimum.

- **1448 candidate positions** — 365 / 479 / 604 on the 3, 4 and 5 Å shells
- NN spacing: min 1.0001, mean 1.0652 ± 0.0578 Å (CV 0.0542)
- standoff 2.993 – 5.047 Å; every shell closed (χ = 2)
- all 1448 outward normals verified unit-length
- **exactly reproducible**: identical output on two machines with different
  numpy versions, from the seed alone

### Resolution is adequate on its own terms

An arbitrary position on the shells sits on average **0.529 Å** from the nearest
available site (p95 0.878, max 1.236), measured against a dense, independently
seeded reference set.

Combined with the measured Δv gradient (mean 0.185, p95 0.586, max 1.072
kcal mol⁻¹ Å⁻¹ per +1e), discretisation costs **0.098 kcal/mol typically and
0.514 kcal/mol in the steepest regions** — 2.5% and 13% of the best achievable
single-charge effect (−3.847 kcal/mol). The grid therefore resolves position
finely enough that discretisation is not a limiting approximation.

Note for the prose: finer resolution does **not** buy a better single site. It
buys better positioning for *combinations*, where several charges must each sit
near their own optimum at once.

### Placement capacity

| separation | independent sites | species |
|---|---|---|
| 3.0 Å | 73 | — |
| 3.5 Å | 50 | formate / acetate |
| 4.5 Å | 32 | guanidinium |
| 6.0 Å | 18 | — |

### Optimiser cost

Exclusion constraints are needed only for pairs closer than the separation
threshold: 41,442 pairs at 3.5 Å, 72,531 at 4.5 Å. Comfortable for HiGHS.

---

## 3. Shell choice

Shells at 3, 4 and 5 Å. The offsets are measured from the substrate van der
Waals surface **to a point**; a molecular surrogate carries its own radius, so a
guanidinium carbon at 2 Å standoff would place its hydrogens through the
substrate surface. A 3 Å minimum standoff is the closest a real charged side
chain can approach, and the grid is built to be usable by the species actually
being placed.

---

## 4. Placement method: Poisson-disk, justified against CVT

Restricted centroidal Voronoi tessellation with Lloyd relaxation is the natural
alternative and is used elsewhere in the group. Both grids were built from
identical shell meshes and identical dense clouds with the same seed, matched
shell by shell at 365 / 479 / 604, so the comparison isolates the placement
algorithm.

| | N | min NN | mean NN | CV | cond | max 1/r | pairs<1.0 Å | res. mean |
|---|---|---|---|---|---|---|---|---|
| **Poisson-disk** | 1448 | **1.000** | 1.065 | **0.054** | **81,832** | **1.000** | **0** | 0.529 |
| CVT global | 1448 | 0.552 | 1.028 | 0.112 | 2,230,234 | 1.811 | 299 | 0.527 |
| CVT per-shell | 1448 | 0.552 | 1.028 | 0.112 | 255,473 | 1.811 | 300 | 0.527 |

**Coverage is identical** — resolution 0.529 vs 0.527 Å. Coverage was the only
axis on which CVT could have won.

**The difference is entirely in close pairs.** CVT produces 299 site pairs
closer than 1.0 Å where Poisson produces none, and worst-case inter-site
coupling is 81% higher. Lloyd minimises the *variance* of the spacing but places
no lower bound on any individual pair, because it moves seeds to centroids and a
centroid has no notion of a minimum distance.

**CVT also loses on CV, the metric it exists to minimise** (0.112 vs 0.054). The
reason is structural: CVT is a *surface* method, while this grid is three
concentric surfaces about 1 Å apart with ~1.07 Å spacing — for many sites the
nearest neighbour lies on an adjacent shell, which surface-restricted relaxation
cannot see. Pooling the cloud (global mode) improves the conditioning but cannot
impose a floor.

**Caveat to state fairly:** for a *single* surface, CVT is likely the better
choice. The result here is specific to multiple closely spaced concentric shells.

**Reporting caution:** the condition number depends on the smallest eigenvalue
and so swings on a handful of near-degenerate pairs — the two CVT variants
differ ninefold in `cond` despite identical min NN and CV. Quote the
pairs<0.8 Å / pairs<1.0 Å counts alongside it, never `cond` alone.

---

## 5. Envelope: union of R, TS and P

The designed charges are static while the substrate reacts, so every site must
clear the substrate at every point along the path.

Measured at production settings (shells 3/4/5 Å, r_min 1.0 Å, density 6.0,
voxel 0.30 Å). Each single-geometry grid is tested against the geometries it did
not include, at the intended 3 Å floor.

| envelope | sites | min standoff vs the omitted geometries | sites below the 3 Å floor |
|---|---|---|---|
| reactant only | 1402 | 2.345 Å | 177 (12.6%) |
| TS only | 1415 | 2.533 Å | 298 (21.1%) |
| product only | 1405 | 2.104 Å | 234 (16.7%) |
| **union R+TS+P** | **1448** | — | **0 by construction** |

The union *gains* 3.3% in site count over reactant-only while removing 177 path
clashes — it is not a trade-off at all at these settings. No single geometry
dominates: the reactant binds the constraint at 50.4% of sites, the product at
31.6%, the TS at 18.0%.

**On mobile charges.** Substrate motion is small — mean per-atom displacement
0.222 Å R→TS, 0.391 Å R→P, max 1.195 Å — so a charge allowed 1–2 Å of relaxation
would absorb it, and a reactant-only envelope would be defensible. But
Σqᵢ·Δv(rᵢ) is evaluated at *fixed* rᵢ; if a charge relaxes, the screening score
no longer corresponds to the validated design, and the linear deterministic
screen is the central novelty. Keep both, staged: fixed union grid for the
screen, restrained relaxation at validation. Relaxation is self-correcting
anyway — a surrogate that would clash relaxes away from it.

---

## 6. Orientation of surrogates

A surrogate has 3 translational and 3 rotational degrees of freedom; the screen
cannot carry the rotational ones without losing linearity.

- **Screen as a monopole.** Net charge against Δv is first order; orientation
  enters through the dipole and higher moments only.
- **Orient along the shell normal at placement.** A charged residue points its
  charged face at the substrate. This removes two of three rotational DOF; the
  residual spin about the normal is weak for near-symmetric groups such as
  guanidinium. `grid_poisson_sites.tsv` carries the normal for this purpose.
- **Refine along the Δv gradient** where it matters — align the group dipole so
  its positive end lies toward more negative Δv.
- **Relax orientation at validation**, not during the screen.

**Magnitude of the approximation.** With a mean Δv gradient of 0.185
kcal mol⁻¹ Å⁻¹ and guanidinium nitrogens ~2.3 Å off centre, orientation can
swing the interaction by roughly 0.4 kcal/mol, up to ~1.2 in the steepest
regions. State it as a screening approximation rather than ignoring it.

---

## 7. The difference-potential map

`orca_vpot` against the committed reactant and TS densities at all 1448 sites.
No new SCF: the potentials come from the same wavefunctions that define the bare
barrier, verified to 10⁻⁶ Eh before evaluation. Row order recorded separately and
checked on assembly, since `orca_vpot` returns values positionally with no site
identifiers.

- Δv ∈ [−0.005564, +0.006130] Eh = [−3.491, +3.847] kcal/mol per +1e
- mean −0.000045 Eh, sd 0.002001 Eh
- **903 / 1448 (62.4%) stabilising** (Δv < 0)
- local gradient: mean 0.185, p95 0.586, max 1.072 kcal mol⁻¹ Å⁻¹ per +1e

| shell | sites | max \|Δv\| (kcal/mol per +1e) | stabilising |
|---|---|---|---|
| 3.0 Å | 365 | 3.847 | 232 (63.6%) |
| 4.0 Å | 479 | 2.719 | 299 (62.4%) |
| 5.0 Å | 604 | 2.053 | 372 (61.6%) |

Most stabilising site: idx 1107, shell 3 Å, (56.9884, 30.7825, 61.0617),
−0.005564 Eh = −3.491 kcal/mol per +1e.

**Best achievable single charge: −3.847 kcal/mol**, from a −1 charge at the most
*destabilising* site rather than a +1 at the most stabilising one. Worth phrasing
carefully when stating the ceiling.

Two points for the prose:

1. **The ceiling is modest.** No single unit charge lowers the barrier by more
   than about 3.8 kcal/mol at first order, against a bare barrier of 17.47.
   Meaningful catalysis requires several charges acting together, or a mechanism
   beyond first-order electrostatics.
2. **The near-balance of stabilising and destabilising sites** (62.4%) reflects
   the differential character of Δv. The map is not a claim that the region
   around the substrate is favourable; it identifies which regions *distinguish*
   the transition state from the reactant.

---

## 8. Prose to write

0. **X.3 — voxel convergence.** Section 9 above; the analytic-ground-truth
   framing is the defensible one and worth stating explicitly.
1. **X.3 — grid construction.** Union envelope, SDF, shells at 3/4/5 Å,
   area-proportional sampling, global Poisson thinning at 1.0 Å. State the
   resolution/separation distinction as a design choice.
2. **X.3 — resolution adequacy.** 0.529 Å mean placement error → 0.098 kcal/mol
   typical, 0.514 steep-region, i.e. 2.5% and 13% of the achievable
   single-charge effect. Self-contained; no comparison to anything earlier.
3. **X.3 — separation as a model parameter.** Species-dependent, tunable,
   enforced in the optimiser. Capacity table; constraint counts.
4. **X.3 — shell choice.** Why 3 Å is the innermost usable standoff for a
   molecular surrogate.
5. **X.3 — placement method.** The CVT comparison table and the surface-method
   explanation, with the single-surface caveat and the `cond` reporting caution.
6. **X.3 — normals and orientation.** Monopole screening approximation stated
   with its ~0.4 kcal/mol magnitude.
7. **X.3 — envelope justification.** Union vs single-geometry table; the
   mobile-charge argument and why the screen stays fixed.
8. **X.4 — the Δv map.** All statistics from section 7 above.
9. **X.4 — the ceiling argument** and the differential-character point.
10. **Reproducibility.** Identical output across machines from the seed alone.

---

## 9. Voxel convergence

The SDF lattice spacing is a purely numerical parameter, so the grid is only
defensible if the result does not depend on it. Halving it, 0.30 → 0.20 Å
(278,070 → 910,248 voxels), at production settings:

| shell | area coarse | area fine | Δ area | offset coarse | offset fine |
|---|---|---|---|---|---|
| 3.0 Å | 649.0 | 649.8 | +0.11% | 2.998 ± 0.006 | 2.999 ± 0.003 |
| 4.0 Å | 844.6 | 845.2 | +0.07% | 3.998 ± 0.005 | 3.999 ± 0.003 |
| 5.0 Å | 1065.1 | 1065.7 | +0.05% | 4.998 ± 0.004 | 4.999 ± 0.002 |

Error against the **analytic** surface (the union-of-spheres SDF is analytic, so
the true shell is exactly SDF = d and error is measurable against ground truth
rather than against the other mesh):

| shell | coarse mean / p95 / max | fine mean / p95 / max |
|---|---|---|
| 3.0 Å | 0.0046 / 0.0071 / 0.0790 | 0.0021 / 0.0030 / 0.0482 |
| 4.0 Å | 0.0037 / 0.0056 / 0.0636 | 0.0017 / 0.0024 / 0.0424 |
| 5.0 Å | 0.0032 / 0.0045 / 0.0635 | 0.0015 / 0.0020 / 0.0307 |

Grid outcome: 1448 sites coarse vs 1421 fine (−1.86%, consistent with the
stochastic sampling draw), coverage 0.5241 vs 0.5348 Å, min NN 1.0001 in both.

**Converged.** Worst coarse-lattice error is 0.0790 Å against a site spacing of
1.0 Å and a positioning resolution of 0.53 Å — roughly 8% of the spacing and 15%
of the resolution, so the lattice is not the limiting approximation. The 0.30 Å
lattice is retained.

---

## 10. Open items

- [ ] Retire the earlier grid and its Δv map from the submission manifest —
      development, not method, and must not appear in the bundle
- [ ] Commit the build package, both grids, the comparison, the validation
      tests, the Δv job and its output; add manifest rows
- [ ] Re-run all downstream experiments on this grid
