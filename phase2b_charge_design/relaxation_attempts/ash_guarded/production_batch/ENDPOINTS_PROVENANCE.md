# Phase-2b relaxed endpoints — provenance & verification

All geometries: 24 QM substrate atoms (0-23) + design-specific MM surrogates, relaxed under each
design's fixed field with the calibrated MM molecular-surrogate method (QM -2, guanidinium/formate
+ explicit QM-MM LJ, loose conv gmax 6-8e-3). Reacting atoms (0-based): C1=0, O3=7, C4=8, C6=12.
Break O3-C4, form C1-C6.

## Reactant endpoints (all CONVERGED)
| design | file | source HPC run | O3-C4 | C1-C6 | note |
|---|---|---|---|---|---|
| K1 | k1_mmsurr_final.xyz | mmsurr_k1 (136 steps) | 1.43 | 4.26 | benign, no salt bridge |
| K2 | k2_mmsurr_final.xyz | mmsurr (loose, 241 steps) | 1.43 | 5.00 | calibrated vs full-QM |
| K3 | k3_mmsurr_final.xyz | mmsurr_k3 (182 steps) | 1.44 | 4.00 | salt bridge 1.886 |
| K4 | k4_mmsurr_final.xyz | mmsurr_k4 (314 steps, gmax8e-3) | 1.45 | 5.04 | mixed rep, salt bridge 1.853 |

## Product endpoints (K1-K3 CONVERGED; K4 pending)
| design | file | source HPC run | O3-C4 | C1-C6 | verified |
|---|---|---|---|---|---|
| K1 | k1_product_final.xyz | prod_k1 (145 steps) | 3.65 | 1.56 | product-like OK |
| K2 | k2_product_final.xyz | prod_k2 (209 steps) | 5.13 | 1.57 | product-like OK |
| K3 | k3_product_final.xyz | prod_k3 (198 steps) | 5.17 | 1.57 | product-like OK |
| K4 | (pending)          | prod_k4 (running)     | -    | -    | - |

## Barrier calculation (these endpoints feed it)
Barrier(K) = E(TS,K) - E(reactant,K). TS located per design (separate fixed field each).
Method pilot on K2: NEB-TS vs relaxed-scan+TSOpt, compared for cost & outcome before scaling to K1/K3/K4.
Phase-1 baseline (bare substrate, no design): barrier +17.47 kcal/mol (committed 02_singlepoints).
