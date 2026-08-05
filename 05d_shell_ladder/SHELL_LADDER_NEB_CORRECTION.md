# Correction to SHELL_LADDER_NEB_RESULT.md — NEB reading

**Status:** honest reversal of the NEB interpretation in the prior version of SHELL_LADDER_NEB_RESULT.md
(committed in 03feacf). The geometry-ladder, controls, and stationary-point-screen results are unchanged;
only the NEB-under-field interpretation, its numbers, and the conclusion wording are corrected. The
correction was derived by re-reading each committed `neb_screen/bands/<tag>/final_band.txt` directly.

## What the prior version got wrong

1. **"Product ends below reactant → no forward barrier."** This conflated *exothermic* with *barrierless*.
   Every committed band that produced a profile has a clear positive forward peak between the reactant and
   product images. A product image below the reactant image only means the reaction is exothermic under the
   field; the forward barrier is the peak, which exists in all 13 designs that produced a band.

2. **"The bands thrash / no well-behaved MEP / no NEB barrier converges (all PASS designs)."** Four designs
   (7p4, 8p1, 13p0, 15p0) are clean single-peaked minimum-energy paths with moderate residual forces
   (peak MaxF 0.6–1.0 eV/Å) and readable barriers. Only five designs (7p6, 8p6, 8p9, 7p1, 12p0) carry
   forces large enough (peak MaxF 2–10 eV/Å) to be called genuinely under-converged.

3. **Numbers not matching the committed bands.** The prior version cited "peak dE +150 to +700, with ~1e6
   outliers." No committed `final_band.txt` contains such values; the maximum committed peak is +177
   (7p1, 12p0 — both under-converged). The +700/~1e6 figures came from a superseded run or a raw-Knarr
   parse (cf. the interior-energy corruption noted in the archived K2 run d3c047d) and are not part of this
   result.

## Verified per-design barriers (from committed final_band.txt; ΔE vs reactant image, image 0)

| design | peak (kcal/mol) | product ΔE | peak MaxF | class |
|--------|----------------:|-----------:|----------:|-------|
| 7p4  | +77.32  | −2.27  | 1.04 | clean single peak |
| 8p1  | +77.65  | +9.81  | 0.70 | clean single peak |
| 13p0 | +77.55  | −18.10 | 0.59 | clean single peak |
| 15p0 | +37.88  | +8.24  | 0.90 | clean single peak |
| 7p3  | +32.28  | −29.21 | 0.86 | bounded, mildly rugged |
| 8p2  | +50.37  | −21.69 | 0.82 | bounded, mildly rugged |
| 8p5  | +84.31  | −32.15 | 0.84 | bounded, mildly rugged |
| 7p8  | +20.84  | −30.63 | 1.86 | bounded, rugged |
| 7p6  | +36.23  | +10.03 | 3.26 | under-converged (not quoted) |
| 8p6  | +48.48  | −4.16  | 5.10 | under-converged (not quoted) |
| 8p9  | +46.89  | −19.52 | 10.31| under-converged (not quoted) |
| 7p1  | +170.58 | −74.57 | 4.89 | under-converged (not quoted) |
| 12p0 | +177.35 | +9.04  | 5.87 | under-converged (not quoted) |
| 2p0  | —       | —      | —    | no band (close shell, fragmented) |

Every readable peak ≥ +20.8 kcal/mol > +17.47 bare. The four clean designs span +37.9 to +77.7.

## Corrected conclusion (in one line)
The provably-optimal uniform ±1 field admits a connected reaction path but **raises** the barrier well above
bare (anti-catalytic) where the path is clean, and elsewhere fails the stationary-point screen or the
substrate integrity tests. The negative is "path exists, barrier worse," not "no path exists."

## Caveats carried forward
- The four clean bands are moderately, not tightly, converged; their values are approximate (the climbing
  image has not fully climbed, so each is a slight under-estimate of the true saddle). The sign is robust.
- The five under-converged designs must be reconverged before any of their numbers is quoted.
- The NEB runner is not yet committed to the code repo; committing it (with exact images/maxiter/free_end)
  is needed for full repo-only reproducibility.

## Note on the 03feacf commit message
The commit message for 03feacf states "NEB-under-field on pass designs: none converge (no valid path under
field) → no catalytic barrier." That wording is superseded by this correction; commit messages are
immutable, so this note is the record of record. The archived guidance "DO NOT retry with more iterations"
(d3c047d) was written about the K2 corrupt-energy run and does not apply to these readable shell-ladder
bands.
