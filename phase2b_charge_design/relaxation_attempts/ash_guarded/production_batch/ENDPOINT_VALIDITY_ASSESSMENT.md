# K2 endpoint validity assessment (before trusting any barrier)

Prompted by the NEB slack band + 1D-scan dissociative ridge: are the endpoints themselves correct,
or is a bad endpoint poisoning both barrier methods? Checked connectivity + bonding of both K2 endpoints.

## Result: endpoints are CHEMICALLY VALID
- K2 reactant (k2_mmsurr_final.xyz): SINGLE connected molecule. O3-C4 bonded (1.434), C1-C6 NOT bonded
  (5.004). Correct chorismate reactant - ether intact, ring not closed.
- K2 product (k2_product_final.xyz): SINGLE connected molecule. O3-C4 broken (5.130), C1-C6 bonded
  (1.572). Correct prephenate-like product - ether broken, new C-C formed.
Neither is fragmented or artifactual. Both are legitimate reactant/product minima. Endpoints are NOT the
problem; they are correct. (Same endpoints feed the scan and NEB, so this validates both inputs.)

## What the assessment DOES reveal (physical, not an error): the field pre-organises AWAY from the TS
C1-C6 (the forming bond) across the stages:
  bare-substrate reactant (Phase-1): C1-C6 = 3.124  -> TS 2.526  (must close 0.60 A)
  K2 field-relaxed reactant:         C1-C6 = 5.004  -> concerted TS ~2.5 (must close ~2.5 A)
K2's field holds the reacting carbons ~2 A FURTHER APART than the bare substrate. The field-relaxed
reactant is a correct minimum, but it sits FURTHER from the concerted TS than the bare substrate does.
=> The field pre-organises the substrate in the WRONG direction for the concerted Claisen: the molecule
must do MORE work (close a 2.5 A C1-C6 gap vs 0.6 A) to reach the pericyclic TS. A mechanism for the
field being ANTI-catalytic / mechanism-reshaping on the concerted path. This is visible in the endpoint
GEOMETRIES themselves, independent of any barrier number, and is consistent with the 1D-scan dissociative
ridge and the NEB slack band (both struggle to close C1-C6).

## Refined hypothesis (geometrically grounded, not just from the artifact-prone scan)
K2 (optimal on the frozen-substrate proxy) relaxes the ACTUAL reactant into an open conformer poorly
disposed toward the concerted TS - the field pre-organises the substrate AWAY from the reactive geometry.
This is the empirical motivation for the realism-augmented certified optimiser with a preorganisation
objective term (see code repo: phase2b_charge_design/05b_optimise_realism/PLAN.md).

## Status
Endpoints validated (correct minima, right bonding). NEB left running as cross-check. This finding, plus
K2_SCAN_FINDING (1D +36.5, dissociative ridge) and the NEB band (dissociative/slack), are the three
independent lines backing the switch. See ../SWITCH_EVIDENCE.md.
