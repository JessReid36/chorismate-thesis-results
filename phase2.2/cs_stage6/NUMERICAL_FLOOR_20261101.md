# The measured numerical reproducibility floor of this project's ORCA runs

**1 November 2026.** Measured from the committed record at zero compute cost. Nothing was re-run.
An addendum of 2 November closes the question left open in consequence 3.

## The number

Two committed runs with a **byte-identical complete input set** can differ in total energy by up to

```
2.194e-11 Eh  =  1.4e-08 kcal/mol  =  96 ULP of a float64 near -836
```

That is the floor. No energy comparison in this project can legitimately be set tighter than it.

## How it was measured

937 committed single-solution production runs were scanned (runs with `STABPerform`, which carry
two solutions, were excluded). Each run was fingerprinted by **every file in its directory that is
not a known ORCA output** — `job.inp`, `pc.pc`, `substrate.xyz`, `system.xyz` are what that rule
actually picked up across the whole record. Outputs were enumerated and excluded; anything
unrecognised counts as input, so an unrecognised file makes two runs look *different* rather than
falsely identical.

That left **14 groups, 24 pairs** with byte-identical inputs, spanning both bases, controls and
designs, across seven trees: `additivity`, `transfer`, `d16`, `d17`, `d18`, `negatives`, and
`qscale`/`sitescan`/`standoff`.

| \|dE\| / Eh | ULP | pairs |
|---|---|---|
| 0.000e+00 | 0 | 8 |
| 9.095e-13 | 4.0 | 5 |
| 1.023e-12 | 4.5 | 2 |
| 1.933e-12 | 8.5 | 1 |
| 2.046e-12 | 9.0 | 3 |
| 2.956e-12 | 13.0 | 2 |
| 7.049e-12 | 31.0 | 1 |
| 7.958e-12 | 35.0 | 1 |
| 2.194e-11 | 96.5 | 1 |

Eight of the 24 are bit-identical. The rest differ by tens of ULP.

## Where it comes from

Not from physics. The widest pair — `additivity/def2-SVPD/n10_wall0_TS` against
`d16/def2-SVPD/S6-10_wall0_TS` — has a byte-identical `job.inp`, the same ORCA 6.0.1, the same 8
MPI ranks, and the same 15 SCF cycles. The difference is the order in which eight processors
summed their contributions. Floating-point addition is not associative, so a parallel reduction
is not bit-reproducible across runs.

## A method error worth recording

The first attempt fingerprinted `job.inp` alone and produced apparent differences of **1e3 Eh**.
That was not a finding: an input that uses `* xyzfile` or `%pointcharges` is byte-identical across
runs that point at *different* geometry and charge files. The `water_probe` and `d19/fod_*` runs
exposed it immediately, because a 2.7e11-ULP "reproducibility floor" is self-evidently wrong.

The lesson generalises: **identical `job.inp` does not mean identical calculation.** Any check that
compares two runs must fingerprint the complete input set. This is the same hazard
`STAGE6_DIAGNOSTIC22_20261101.txt` gates against as GATE 3(b).

## What it bounds

| quantity | value | multiple of the floor |
|---|---|---|
| the floor | 2.194e-11 Eh | 1 |
| `GATE_EH` in D20, D21, D22 | 1e-6 Eh | 4.6e+04 |
| D11.3 budget | 1.067 kcal/mol | ~1.2e+08 (in energy terms) |
| D11.3 `SHIELD_ABS` | 0.05 kcal/mol | ~5.7e+06 |

**No gate in this project has ever been set near the floor.** This was worth checking rather than
assuming: D21's GATE 2 was reported in conversation as agreeing "to 3e-12", which is *below* the
floor and would have been an illegitimate tolerance had it been one. It was not — 3.07e-12 Eh was
the *observed agreement* across its 18 runs, while the tolerance was `GATE_EH = 1e-6`. The
observed agreement sitting at the floor is exactly what the floor predicts.

## Consequences for how results are stated

1. **Never quote an energy agreement as evidence of correctness below ~2e-11 Eh.** Below that,
   agreement is the machine, not the method.
2. **A bit-equality test on energies is not available** in this project. Where bit-equality is
   wanted, test it on *inputs* (bytes), not outputs. D22's GATE 3(a) does exactly this: it compares
   input bytes, where exactness is meaningful.
3. **Stability eigenvalues are a separate question.** Whether `E(0)` reproduces as tightly as a
   total energy is **not known** and is not implied by anything above. D22's READING 3 measures it
   directly, from two runs with byte-identical input, and its tolerance is set from `E(0)`'s print
   resolution rather than from this floor — deliberately, and the pre-registration says so.

## Addendum, 2 November 2026: the scatter is between batches, not within one

Consequence 3 above is now answered. DIAGNOSTIC 22's READING 3 measured it on the two
byte-identical wall-at-zero inputs, which ran in the same PBS job:

```
additivity/def2-SVPD/n10_wall0   vs   d16/def2-SVPD/S6-10_wall0
   R    E(0) +0.05657965  vs  +0.05657965    |diff| 0.00e+00
   TS   E(0) +0.01873019  vs  +0.01873019    |diff| 0.00e+00
```

They agreed **bit-identically**, in the eigenvalue and in every printed digit of READING 1. Yet
their first converged energies differed from their own historical committed values by **7.96e-12**
and **−2.19e-11** Eh (`d22/DIAGNOSTIC22_RESULT.txt`, GATE 2) — the same two magnitudes that head
the table above — while the `d16` copy reproduced its own source exactly, at 0.00e+00.

So the floor is a **between-batch** effect and not a within-batch one. Two runs of the same input
inside one allocation reproduce exactly; the same input run weeks apart does not. That is
consistent with parallel reduction order being fixed within an allocation and varying across
allocations, and it means the floor applies to any comparison against the historical record, which
is what every gate in this project actually performs.

## Provenance

All figures measured from the committed results repo at `bab056a`, and the addendum from
`d22/DIAGNOSTIC22_RESULT.txt` at `0af73ad`. No new runs. Labels per WORKING_RULES.md rule 6: every
number above is **measured from committed files**, except the ULP constant, which is derived
(`2^-52 x 1024` for the binade containing -836).
