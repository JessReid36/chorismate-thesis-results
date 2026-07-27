# K2 NEB-TS run 395444 — second attempt, did NOT converge (dissociative corroboration, 3rd line)

Job: k2_nebts, PBS 395444. Dir: 07_stage0/stage1/nebts_k2/ (working tree). Design: K2 mu=0 = the
un-penalised certified frozen-proxy optimum (24 QM -2 + 14 MM = guanidinium + formate, 38 atoms/image).
This is the "bare K-charges, no realism" barrier anchor (the BEFORE for 05b_optimise_realism).

## Verdict: NOT CONVERGED (not a barrier number)
Knarr CI-NEB hit the iteration cap: "Maximum number of iterations reached (100). Stopping optimization."
/ "Knarr failed to converge during the maxiter=100 given." Per-image ORCA SCFs are HEALTHY (each image
converges in 16-28 SCF iterations), so the failure is the BAND (path) not the electronics - same as the
earlier NEB attempt (see NEB_FINDING.md).

## knarr_MEP_FULL.xyz energies are CORRUPT again - do NOT quote them
The comment-line energies are unusable: interior images read dE ~ -1.3e7 kcal/mol (unit/parse artifact),
image 11 reads +1137.89 kcal/mol (unphysical). Only image 0 (reference, -837.3759 Eh) is sane. As before,
trust per-image image_N/orca.out FINAL SINGLE POINT ENERGY, NOT the Knarr comment line. Because the band
is unconverged AND the energies are corrupt, NO barrier is read from this run.

## Geometry IS readable and is the point: DISSOCIATIVE path (3rd independent line)
Tracing O3-C4 / C1-C6 across the (unconverged) band:
  img 0  : O3-C4 1.43  C1-C6 5.00   (distorted-open reactant, as known)
  img 2-7: O3-C4 2.9 -> 6.5 -> 7.5  C1-C6 3.9-5.1  (BOTH bonds long together)
  img 11 : O3-C4 5.13 (ether fully broken/dissociated)  C1-C6 1.57 (formed)
The path breaks O3-C4 all the way to 5-7.5 A (fragmenting the substrate) instead of the concerted route
where O3-C4 and C1-C6 exchange through a compact ~2.5 A TS. Dissociative, not concerted.

## Combined evidence - now THREE independent lines say the same thing
1. Endpoint geometry: K2 mu=0 relaxed reactant C1-C6 = 5.00 vs 3.12 bare (ENDPOINT_VALIDITY_ASSESSMENT).
2. 1D relaxed scan: dissociative ridge, crest +36.5 at C1-C6 = 6.08 (K2_SCAN_FINDING; suggestive only).
3. NEB bands (both attempts, incl. 395444): dissociative/slack, O3-C4 -> 6-7.5 A mid-band, unconverged.
All three: the un-penalised certified-optimal K2 frozen-proxy field pre-organises the substrate AWAY from
the concerted near-attack TS. The un-penalised K2 field HAS NO CLEAN CONCERTED BARRIER - that is the
pathology, not a measurement failure.

## Consequence for the thesis (do not mis-frame)
The "before" for the 05b preorganisation fix is GEOMETRIC (relaxed C1-C6: 5.0 A for K2 mu=0), NOT a NEB
barrier - because the mu=0 design does not admit a clean concerted barrier, which is precisely WHY it
needed the preorganisation penalty. The real arbiter is the 05b Step-3 relaxed validation of the K2 mu=100
PREORGANISED design (two +1, D~0): does its relaxed C1-C6 come back into [2.6,3.5]? That is the after.
DO NOT RETRY this NEB with more iterations - the surface is frustrated/dissociative; more Knarr iterations
will not manufacture a concerted saddle that the field does not support.
