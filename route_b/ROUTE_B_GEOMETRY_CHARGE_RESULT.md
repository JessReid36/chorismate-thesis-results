# Route B (geometry + charge) — status note (honest reconciliation)

## Negative result (unrestrained fields) — from authoritative NEB energy tables
Read from the log frozen/active energy table AND the validated @-line HEI (the two agree).
Supersedes the imprecise "~40-45" in the earlier correction commit.

| Design (unrestrained) | Barrier (kcal/mol) | vs bare 17.47 |
|---|---|---|
| Capacitor (50 charges, uniform <4%) | **29.77** | +12.3 (raised) |
| OEEF-020 (6 charges, moderate) | **46.37** | +28.9 (raised) |

External point-charge fields do NOT catalyse the relaxed free-substrate reaction. The field pries
the substrate apart along the reaction axis (reactant C1-C6 3.12->4.38, product O3-C4 2.90->4.83).
CONFIRMED.

## Route B: geometry + charge — CATALYSIS UNDER HELD NEAR-ATTACK GEOMETRY
Design cradleArg90 = 24-atom chorismate dianion (-2) + 3 external +1 point charges: two counter-
charges neutralising the carboxylate handles + one Arg90 catalytic +1 at the committed ether-O grid
site [57.611,31.443,60.311] (O3 lone-pair direction). Net system +1. Flat-bottom over-stretch walls
hold BOTH reacting bonds (C1-C6<=3.15, O3-C4<=2.95, k=50).

| Run | Barrier (kcal/mol) | Note |
|---|---|---|
| Bare | 17.47 | reference |
| Walls only (control, CONVERGED) | 14.39 | walls give -3.08 (geometric preorganization) |
| Walls + Arg90 charge (field, NEB) | 6.40 | charge gives -8 within walls |
| Walls + Arg90, tighter clamp (clamp2, 3.124/2.902, k=100) | 7.23 | AGREES -> robust to wall choice |

**Result:** under held near-attack geometry, the Arg90 charge lowers the barrier to ~6-7 kcal/mol
(NEB 6.40 and clamp2 7.23 -- two independent NEBs, different wall params, agree). vs bare 17.47.
Decomposition: geometry -3, charge -8, total -11. Robust to the clamp choice.

## CRITICAL: the charge REQUIRES the geometric confinement (honest framing)
The catalysis is "charge + confinement together", NOT "charge catalyses on its own". Evidence:
- **Antisymmetric scan** (xi=d(O3C4)-d(C1C6) held, but C1-C6 NOT held closed): the reaction runs
  ~45 kcal DOWNHILL reactant->product with only a tiny ~10.7 bump -- the Arg90 charge massively
  stabilizes the product/late structures.
- **Free relaxation under the charge**: the reactant opens C1-C6 3.12->3.88 into a non-reactive well
  122 kcal below the reactive geometry.
So without geometric confinement the charge drives the substrate into charge-stabilized non-reactive/
product wells; ONLY when the near-attack geometry is held (both bonds, via the walls) does the charge
lower a proper reaction barrier. This is the Burschowsky coupling made explicit -- and it is exactly
the enzyme's strategy (Arg90 + the active-site geometric scaffold together).

## Status / caveats
- Barrier ~6-7 is from converged CI-NEB HEIs (field 6.40, clamp2 7.23), robust across two clamps.
- The auto-TSOpt on this floppy restrained saddle WANDERS (flat ridge) but maintains ONE negative
  Hessian eigenvalue throughout = genuine TS character. The NEB HEI + one-imaginary-mode is the
  robust read; a polished saddle energy is pending (TSOpt convergence).
- Capacitor(uniform field)+restraint DERAILED (band downhill from held reactant) -- uniform field too
  disruptive to combine with restraint via NEB; the localized Arg90 charge is what works.
- Flag: [exploratory]. Promotable on the two-clamp NEB agreement (6.40/7.23); a polished saddle is
  NOT obtainable on this floppy restrained surface (TSOpt settled as non-convergent -- see below).

## How to read these outputs (recorded to prevent recurrence)
- Barrier = log frozen/active table OR @-line HEI. The two agree; both validated (reproduce 29.77/46.37).
- NEVER read energies from knarr_MEP_FULL.xyz comment lines (Knarr writer artifact, ~-22770 Eh interior).
- Barrier converges over iterations; read the LAST. Single-iteration spikes are transients.
- Both NEBTS caps (maxiter, OptTS_maxiter) default to 100 and both needed raising to 300.
- One negative Hessian eigenvalue in the TSOpt = genuine TS.

## Free-energy status: what the 6.40/7.23 barrier is, and is not (added after deep literature check)
The barriers above are **potential-energy** barriers evaluated under held near-attack geometry. They are
used here as a **relative ranking metric** for comparing charge arrangements -- which is the actual
purpose in this project (rank designs, pick the best), not to assert an absolute activation free energy.

**Why the potential-energy barrier is a valid ranking metric for this reaction:**
- The catalytic mechanism at work (charge + geometric confinement / reactive-center compression) is
  **enthalpically dominated**. Hilvert's conformational-restriction study (J. Am. Chem. Soc.,
  ja992453d) shows compressing the reactive centers ~4.0 -> 3.0 Angstrom lowers the barrier ~24 -> 12
  kcal/mol and states the rate gains "derive mainly from ground-state destabilization in which
  entropic factors do not contribute significantly." Our walls+charge realise exactly this compression.
- Standard transition-state theory describes the chorismate mutase reaction quantitatively
  (Ranaghan/Mulholland), i.e. dynamical recrossing effects are small.
- The intrinsic activation entropy of the (uncatalysed) chorismate Claisen is **modest and roughly
  constant** across designs: experiment gives -T dS-dagger ~= 3.9 kcal/mol (Kast et al.); EVB gives
  dH-dagger = 20.9, T dS-dagger = -3.4, dG-dagger = 24.4 kcal/mol (matching experiment). A roughly
  constant offset shifts all designs together and so barely affects the **ranking**.

**Why this is NOT an absolute dG-dagger claim (honest caveats, deferred to future work):**
1. There is ~3-4 kcal/mol of intrinsic activation entropy (above) that a potential-energy barrier omits.
2. The flat-bottom walls impose the near-attack geometry "for free". Imposing that confinement has a
   real **free-energy cost** (loss of configurational entropy) that the NEB does not capture but a
   proper PMF would. Our number is therefore conditional on the confinement.

**Decision:** report 6.40/7.23 as a potential-energy ranking barrier with the above framing; **defer a
full free-energy (PMF) treatment as future validation** of the absolute dG-dagger. A rigorous PMF is
feasible in principle (xTB-sampled umbrella + DFT reweighting; xTB validated on the dianion, ~325x
faster than DFT) but is blocked on QM/MM-MD thermostat stability with the current dummy-system MM
construction (needs a real MM forcefield + X-H constraints, per the ASH fast-QM/MM-MD tutorial). This
is parked, not required, for the ranking result.
