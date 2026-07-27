# Evidence backing the switch to a realism-augmented certified optimiser

One-page summary of the committed numbers that justify augmenting the certified Tier-1 with realism +
a preorganisation objective term. All numbers traceable to committed files (paths below).

## The pathology (why frozen-proxy certified-optimal != catalytic)
| quantity | bare substrate | certified-optimal K2, relaxed | source (committed) |
|---|---|---|---|
| forming bond C1-C6 (reactant) | 3.12 A | 5.00 A (opened AWAY from TS) | production_batch/ENDPOINTS_PROVENANCE.md |
| near-attack window / TS C1-C6 | 2.6-3.5 A / ~2.5 A | - | 01_geometry (Phase-1 R/TS/P) |
| 1D O3-C4 scan barrier (K2) | +17.47 (baseline) | +36.5 kcal/mol, peak C1-C6 6.08 A (dissociative) | barrier_k2_scan/K2_SCAN_FINDING.md |
| NEB band character | concerted (bare) | dissociative/slack | barrier_k2_neb/ |

## Reading (conservative)
- Endpoints are chemically VALID (single molecules, correct R/P bonding) - not an artefact
  (production_batch/ENDPOINT_VALIDITY_ASSESSMENT.md). The distortion is physical.
- The 1D scan +36.5 is an UPPER BOUND / suggestive only (1D scan is a known failure mode for concerted
  reactions); the DEFENSIBLE, method-independent statement is the ENDPOINT GEOMETRY: the certified-optimal
  K2 field pre-organises the reactant's forming bond to 5.0 A, FURTHER from the reactive geometry than the
  bare substrate (3.12 A). That alone motivates a preorganisation-aware objective.
- Root cause: a few bare monopoles over-polarise the flexible dianion. GOCAT's own charge model already
  bounds/neutralises/spaces charges; our fix is a LINEAR preorganisation term in a CERTIFIABLE objective.

## What this justifies (not a failure - a directed correction)
Switch from "certified-optimal on frozen Dv" to "certified-optimal on frozen Dv + linear preorganisation
term + realism constraints", preserving the g=0.000 certificate. See 05b_optimise_realism/PLAN.md.
