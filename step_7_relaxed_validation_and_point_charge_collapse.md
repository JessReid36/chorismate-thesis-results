# Step 7 — Relaxed-geometry validation, and the discovery that bare point charges collapse

## Verified from committed files (previously asserted from summaries only)

- **Bare barrier +15.771 kcal/mol confirmed.** E_R = -836.365884, E_TS = -836.340751,
  both SCF-converged, identical theory lines (B3LYP D3BJ def2-SVP def2/J RIJCOSX CPCM
  KeepDens), both charge -2. Re-derives to +15.771 against the value in use.
- **Polarisation results confirmed**, with one correction: the net-free polarised value is
  **-14.009**, not -14.014 as previously quoted. The two polarisation runs also used
  marginally different bare barriers (15.771 vs 15.766); immaterial but should be
  reconciled before publication.
- **The K=2 validity check already existed.** step_4_1.pbs.out records with-charge
  barriers of +3.570 (net-neutral) and +1.757 (net-free) — both positive, so the barrier
  survives full electronic response at K=2. The frozen model UNDERSTATES the lowering by
  1.31 and 2.66 kcal/mol; it is conservative, not optimistic.
- **Grid geometry measured, not assumed.** Shell labels 2/3/4 denote Angstroms beyond the
  van der Waals surface, equal to 3.19-3.70, 4.19-4.70 and 5.20-5.63 A from the nearest
  atom centre. The grid floor is 1.7 A beyond vdW. All candidate positions are therefore
  already beyond the 2.5-3.0 A standoff that the literature treats as SCF-safe.
- **Enzyme residue standoffs measured** (TS-frame charge centres vs pooled R+TS+P
  substrate): Arg90 2.63, Lys60' 2.71, Glu78 3.08, Arg7 3.19, Arg63' 3.43 A. Three of five
  sit inside the grid's own floor, so the design space does not reach where the enzyme
  places its most important charges.

## Retracted

- **"More charges do worse" is not supported by the committed data.** sol_discrete.npz gives
  net-neutral K=2/4/6/8 = -10.888 / -21.466 / -28.715 / -35.896 kcal/mol: monotonically
  larger with K. The recorded 92.8% / 89.6% figures are *per-charge efficiency*
  (100 / 98.6 / 87.9 / 82.4%), which was narrated as a statement about the total. The
  correct claim is that marginal return per charge declines, not that more charges are worse.
  An independent solver reproduced all eight committed values to 0.0002 kcal/mol, so the
  optimiser formulation, grid, Dv column, 2.5 A exclusion and certificate are all confirmed.
- **All committed K>2 values imply negative barriers** (K=4 -> -5.70, K=6 -> -12.94,
  K=8 -> -20.13 kcal/mol) and should never have been quoted as results. The frozen-density
  objective is a first-order expansion with no lower bound. K=2 is the only charge count at
  which the frozen prediction is physically meaningful.
- **The shell-restricted sweep answered a non-problem.** It was built on a misreading of the
  1.7 A grid floor as an atom-centre distance; it is a vdW-surface distance. Its conclusion
  ("more charges earn their keep because of the standoff") is withdrawn.

## The distributed-design reformulation

The maximum-lowering objective always concentrates charge in the strongest field lobe and
adds lowering without limit. Replaced by: **minimise the largest single-charge contribution**,
subject to the total effect lying in a band (at least the enzyme's 9.1 kcal/mol, at most
BARE - 5.0 so the predicted barrier stays positive by construction). Still linear, so the
optimality certificate survives.

Results on the 252-point grid, all certified gap 0.0000, all barriers held at +6.54 to +6.67:

| K | max contribution | ideal (target/K) | spread | shells used |
|---|---|---|---|---|
| 2 | 4.678 | 4.550 | 1.03 | 22 |
| 3 | 3.163 | 3.033 | 1.07 | 222 |
| 4 | 2.301 | 2.275 | 1.03 | 3244 |
| 5 | 1.865 | 1.820 | 1.07 | 43432 |
| 6 | 1.593 | 1.517 | 1.10 | 443233 |
| 7 | 1.354 | 1.300 | 1.08 | 2224233 |
| 8 | 1.180 | 1.137 | 1.06 | 24423343 |

Max contribution lands within 1-5% of perfect equalisation at every K, so the separation
constraint and field shape cost almost nothing. From K=4 onward the designs recruit all
three shells concurrently — the first mixed-shell arrangements in the project. Under the
maximum-lowering objective mixing was always available and never chosen; it is the
objective, not the constraint, that produces distribution.

## The collapse

Relaxed reactant optimisations with the designed charges as bare ORCA point charges
(%pointcharges) collapse: a substrate oxygen migrates onto a designed +1 and ends inside
its own van der Waals radius.

| design | closest approach | beyond vdW | cycles |
|---|---|---|---|
| K=2 concentrated | 0.879 (O to +1) | -0.641 | 147 (converged) |
| K=2 distributed | 0.991 (O to +1) | -0.529 | 21 |
| K=3 | 1.062 (O to +1) | -0.458 | 19 |
| K=7 | 1.284 (O to +1) | -0.236 | 7 |
| K=5 | 2.203 (H to -1) | +1.003 | 20 |
| K=6 | 2.882 (H to -1) | +1.682 | 21 |
| K=8 | 3.150 (O to +1) | +1.630 | 7 |
| K=4 | 4.820 (O to +1) | +3.300 | 20 |

Four of eight collapsed; three more were drifting inward when killed. **Every collapse is a
substrate oxygen falling onto a designed +1**; the two designs whose closest contact is a
hydrogen approaching a -1 both stayed clear. The converged K=2 concentrated run reported an
energy 249 kcal/mol below what the frozen calculation implies, and it converged normally —
nothing in the standard output flags it.

Diagnosis and eliminations:
- **Not bodily translation.** ORCA projects overall translation out of the optimisation
  gradient; the substrate centroid is identical to three decimals (21.716, 40.374, 57.141)
  in every run, collapsed or not. It is a local motion of one flexible arm.
- **Not reproducible in small rigid probes.** Neutral water with a +1 at 2.0 A moved 0.006 A;
  formate (-1) moved 0.094 A. Substrate flexibility and net charge -2 both matter.
- The cause is the missing Pauli wall: a bare point charge is an unbounded 1/r attractor.
- A .pc charge also receives no CPCM cavity, so its interaction with the substrate is
  unscreened at short range, amplifying the effect relative to a real ion.

## Method options evaluated

Dead ends, documented so they are not revisited:
- **Ghost atoms** — basis functions without electrons give no Pauli repulsion and may worsen
  spill-out by giving density somewhere to go.
- **QM/MM with Lennard-Jones parameters** — ORCA aborts: "CPCM or SMD or ALPB or ddCOSMO or
  CPCMX requested together with QM/MM method. This is not implemented." Not lifted in 6.1.
- **Gaussian-smeared external charges** — the .pc format is four columns (charge, x, y, z)
  with no width field; ORCA's Gaussian-charge machinery exists only inside CPCM for cavity
  surface charges.
- **orca_mm -makeff for free-floating charge sites** — fails, because it runs an internal xtb
  geometry optimisation that cannot handle disconnected atoms.
- **Increasing the standoff** — rejected on scientific grounds: it would exclude the region
  2.63-3.43 A where BsCM places its own charged residues, making the enzyme comparison
  circular.

Incidental finding: ORCA's own force field (ORCAFF.prms via orca_mm -makeff) uses UFF
non-bonded parameters — C 0.105/3.851, N 0.069/3.660, O 0.060/3.500, H 0.044/2.886, matching
Rappe's published x_I and D_I exactly. The length column is R_min, not sigma.

## Reframing: the collapse is partly physical

A real arginine guanidinium placed where a designed +1 sits *should* pull a chorismate
carboxylate into a salt bridge; the structural consensus places Arg-carboxylate contacts at
2.6-3.0 A. So inward motion is correct down to roughly the salt-bridge distance, and the
artefact is only the sub-van-der-Waals penetration below it. The requirement is not to
prevent approach but to make it stop in the right place.

## Chosen route

Capped ECPs: a repulsive, electron-free pseudopotential co-located with each designed +1,
using ORCA's coreless-ECP embedding (Atom> syntax), Cartesian-constrained. This is the
mechanism embedded-cluster methods use to prevent spill-out onto positive charges; it
preserves CPCM epsilon = 4 and works for both Opt and OptTS/NumFreq. Only cations need
capping. Fallback if the cap proves too soft: molecular surrogates (methylguanidinium for
+1, acetate for -1) in the QM region, which is standard theozyme practice and needs no
invented parameters.

Required protocol change: the bare reference barrier must be recomputed with the same
centres present and the field switched off, or the comparison conflates the design's field
with the mere presence of the caps.

## Mandatory diagnostic

A collapsed run converges and reports a plausible-looking number. pcdist.py must be run on
every relaxed result before its energy is used for anything. Any design whose closest
approach falls below ~0.5 A beyond van der Waals is diverging and should be killed rather
than left to finish.
