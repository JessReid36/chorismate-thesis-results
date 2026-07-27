# K2 relaxed-scan barrier (O3-C4 distinguished coordinate) — result + caveat

Method: ASH calc_surface, Relaxed scan of the breaking bond O3-C4 (atoms 7-8) from 1.45 to 3.00 A
(0.10 step), MM molecular-surrogate field (QM -2, guanidinium/formate + LJ), ActiveRegion=QM.
Script: barrier_k2_scan/k2_scan.py. Reactant reference E0 = -837.37630 Eh (O3-C4 1.45).

RESULT: profile crests at O3-C4 = 2.55 A, barrier(scan) = +36.5 kcal/mol.
Bare-substrate Phase-1 baseline = +17.47 kcal/mol.
=> Under this 1D scan, the K2 design does NOT lower the barrier; it roughly DOUBLES it.

CAVEAT (important - why this is an UPPER BOUND, not the barrier):
A 1D relaxed scan along O3-C4 alone forces the breaking bond to stretch while C1-C6 relaxes
passively. The chorismate->prephenate Claisen TS is CONCERTED (O3-C4 breaks as C1-C6 forms
together). Driving only O3-C4 can ride a higher ridge than the true saddle, overestimating the
barrier. The scan peak (2.55 A) is a TS GUESS; the value is refined by TSOpt (P-RFO from the peak,
concerted saddle) and cross-checked by NEB-TS (full concerted path). Do NOT quote +36.5 as the K2
barrier - it is the scan upper bound pending TSOpt/NEB.

STATUS: TS guess extracted for TSOpt polish; NEB-TS running in parallel. Barrier verdict deferred
to the refined TS. Kept as reference for the method comparison (scan vs NEB cost-vs-outcome).
