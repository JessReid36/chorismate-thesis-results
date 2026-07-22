# Stage 0 — bare-field endpoint relaxation: results table (why we shift gears)

Native ORCA 6.0.1 `%pointcharges` + CPCM(eps=4) + Opt (`coordsys cartesian`), NO guard.
8 jobs = 4 max-lowering designs x {reactant, product}. All capped at 72 geometry cycles.
Raw outputs: runs/<tag>/job.out (this directory). Metrics parsed from the FINAL geometry of
each job.out. Reference bare-substrate (no field, converged): O3-C4 = 1.472 (R) / 2.902 (P),
C1-C6 = 3.124 (R) / 1.583 (P) Angstrom.

| Design | Endpt | Conv | Cyc | Final MAX grad (Eh/Bohr) | min atom-charge (A) | O3-(+1) (A) | O3-C4 (A) | C1-C6 (A) | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| K1 | R | no | 72 | 0.00219            | 8.21 | -    | 1.46 | 3.41 | plateau, intact (no +1 in design) |
| K1 | P | no | 72 | 0.00217            | 7.61 | -    | 3.60 | 1.57 | plateau, intact |
| K2 | R | no | 72 | 0.01210            | 0.98 | 1.72 | 1.54 | 3.11 | IMPLODE (O3 -> +1) |
| K2 | P | no | 72 | 0.00396            | 1.05 | 1.05 | 5.70 | 3.75 | IMPLODE, O3 torn from C4 |
| K3 | R | no | 72 | 0.01975            | 0.97 | 1.81 | 1.51 | 3.28 | IMPLODE (O3 -> +1) |
| K3 | P | no | 72 | 0.01881            | 1.06 | 1.06 | 5.92 | 4.04 | IMPLODE, O3 torn from C4 |
| K4 | R | no | 72 | 0.00537            | 1.03 | 4.06 | 3.90 | -    | IMPLODE (multi-charge collapse) |
| K4 | P | no | 72 | ~4767 (diverged)   | 0.01 | 0.75 | 5.25 | 1.58 | DIVERGE, atom on charge |

## Verdict
- 0 / 8 converged (all hit the 72-cycle cap): bare `coordsys cartesian` cannot tighten the
  gradient in the fixed field even without implosion (K1 plateaus at ~0.0022 vs 3e-4 tol).
- 6 / 8 imploded: every design carrying the +1 at 3.84 A from ether O3 (K2, K3, K4, both
  endpoints) collapsed; a nucleus reached 0.01-1.06 A of an external charge from a >=3.5 A start.
  Product endpoints tear O3 off C4 (O3-C4 5.25-5.92 A vs 2.90 bare).
- K1 (lone -1, far) is the only geometrically intact design - and still did not converge.
- K4_product diverged outright (MAX grad ~4767 Eh/Bohr; atom 0.01 A from the +1).

## Why we shift gears (-> guarded Stage 1)
Bare native `%pointcharges` is not viable for endpoint relaxation. Two independent fixes,
applied uniformly to all designs:
1. Convergence: keep `coordsys cartesian` (must relax the field-induced rigid-body force -
   redundant internals cannot) + computed Hessian (Calc_Hess true, Recalc_Hess) -> targets the
   K1-type plateau.
2. Implosion: detected via min atom-charge distance (< 2 A) and retained as a ranking FAILURE
   (register G1), not rescued into a fabricated barrier -> covers K2/K3/K4.
