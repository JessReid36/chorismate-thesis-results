# Stage 1 — Calc_Hess convergence attempt: results table (native-bare path CLOSED)

Same 8 designs as Stage 0, recipe changed to `coordsys cartesian` + `Calc_Hess true` +
`Recalc_Hess 5` + MaxIter 60 (computed analytic Hessian to break the Stage 0 plateau).
Raw outputs: runs/<tag>/job.out. Reference bare-substrate (no field): O3-C4 = 1.472 (R) /
2.902 (P), C1-C6 = 3.124 (R) / 1.583 (P) A.

| Design | Endpt | Conv | Cyc | runtime | trajMin (A) | O3-C4 (A) | C1-C6 (A) | Outcome |
|---|---|---|---|---|---|---|---|---|
| K1 | R | no | 60 | 4h35 | 3.52 | 1.47 | 3.35 | plateau, intact — MAX grad oscillates 0.0017-0.0091 (no trend) |
| K1 | P | no | 60 | 4h44 | 3.87 | 3.50 | 1.57 | plateau, intact |
| K2 | R | no | 60 | 4h37 | 0.93 | 1.53 | 3.18 | IMPLODE (spike MAX grad 0.18) |
| K2 | P | no | 60 | 4h39 | 0.92 | 5.31 | 3.47 | IMPLODE, O3 torn from C4 |
| K3 | R | no | 60 | 4h43 | 0.90 | 1.53 | 3.23 | IMPLODE |
| K3 | P | no | 60 | 2h24 | 0.86 | 5.31 | 3.60 | IMPLODE, O3 torn from C4 |
| K4 | R | no | 60 | 2h29 | 0.93 | 1.85 | 3.34 | IMPLODE (multi-charge) |
| K4 | P | no | 60 | 2h29 | 0.03 | 4.78 | 1.43 | DIVERGE, atom on charge |

## Verdict — the native-bare path is exhausted
- 0/8 converged again, at ~4.5 h/job (Recalc_Hess ~10x slower than Stage 0 for zero gain).
- A full analytic Hessian recomputed every 5 cycles did NOT fix the K1 plateau: MAX gradient
  oscillates 6-30x over tolerance with no downward trend -> the field creates a frustrated,
  shallow surface, NOT a curvature-starved one. More Hessian is a dead end.
- Implosion unchanged for K2/K3/K4 (trajMin 0.03-0.93 A; O3 torn from C4 at products).
- Loose reaction-relevant tolerance is ruled out: K1 bounces above even a 1e-3 threshold, so
  "converging" it would report a non-stationary point.

## Decision
Native bare %pointcharges + %geom Opt cannot deliver relaxed endpoints for these designs.
Both failure modes are outside what %geom can fix (implosion needs a one-sided distance wall;
the frustrated surface needs a restraint-capable optimiser). Shift Tier-2 relaxation to the
ASH wrapper (geomeTRIC/OpenMM restraints + LJ/one-sided walls driving ORCA). See code repo
phase2b_charge_design/DESIGN_DECISIONS.md.
