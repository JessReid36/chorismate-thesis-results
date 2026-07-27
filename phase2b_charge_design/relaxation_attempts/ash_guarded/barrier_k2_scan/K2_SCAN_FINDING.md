# K2 relaxed-scan barrier (1D O3-C4) — dissociative-ridge result, SUGGESTIVE ONLY

## Result
1D relaxed scan of the breaking bond O3-C4 (1.45 -> 3.00 A, 0.10 step), MM molecular-surrogate K2
field (QM -2, guanidinium/formate + LJ), ActiveRegion=QM. Reactant ref E0 = -837.37630 Eh.
Profile crests at O3-C4 = 2.55 A, +36.5 kcal/mol (vs +17.47 bare-substrate Phase-1 baseline).
At the peak, C1-C6 (the FORMING bond) = 6.084 A - i.e. a DISSOCIATIVE geometry (reacting carbons
flew apart), NOT the concerted Claisen TS (C1-C6 ~2.5; Phase-1 TS was O3-C4 2.11 / C1-C6 2.53).

## STATUS OF THE INTERPRETATION: SUGGESTIVE, NOT CONCLUSIVE
Two explanations are consistent with the C1-C6 blowout, and the 1D scan CANNOT distinguish them:
 (A) PHYSICAL: K2's fixed field genuinely favours a dissociative response - breaking O3-C4 redistributes
     charge, and the field (salt-bridged +1 guanidinium + the -1 sites) is most stabilised when the
     fragment charges splay apart to align with the external charges, so the substrate opens C1-C6 rather
     than puckering to the cyclic TS. If true, the field RESHAPES the reaction coordinate toward a more
     dissociative/asynchronous (possibly stepwise-ionic) mechanism - consistent with OEEF literature
     (Shaik et al.: strong oriented fields switch concerted reactions to stepwise).
 (B) METHOD ARTIFACT: a 1D relaxed scan constraining ONLY O3-C4 is a KNOWN failure mode for CONCERTED
     two-bond reactions - with no incentive to close C1-C6 it can ride a dissociative ridge EVEN WITH NO
     FIELD. The blowout may say nothing about K2 and everything about the unsuitability of a 1D scan here.
We CANNOT tell (A) from (B) using the 1D scan alone. Therefore +36.5 is NOT the K2 barrier and the
"field favours dissociation / optimal-but-unfavourable" reading is a HYPOTHESIS, not a result, at this stage.

## Why the 2D scan is still needed (the discriminating experiment)
A coarse 2D relaxed scan over O3-C4 x C1-C6 (scan2d_k2, 8x7 grid, running) maps the true surface and
distinguishes (A) from (B):
 - If a CONCERTED saddle exists (both bonds ~2.5) with a sensible barrier -> the 1D ridge was artifact (B);
   K2 reacts via the normal path and the question is just barrier height. Hypothesis (A) DISPROVEN.
 - If there is genuinely NO concerted saddle / the lowest path is dissociative -> hypothesis (A) CONFIRMED
   and evidenced: K2 is proxy-optimal but reshapes the pathway. This would be the headline Phase-2b finding
   (the frozen-substrate proxy is blind to MECHANISM change - a real limitation of that design class incl. GOCAT).
NEB-TS (running) independently finds the true R->P path without presupposing the TS, as a second line of evidence.

## Do NOT seed TSOpt from the enzyme (Phase-1) TS
That would presuppose an enzyme-like concerted TS - exactly what is in question. Any TSOpt polish must be
seeded from the NEB climbing image (the field's own TS) or the 2D-scan saddle, never the enzyme TS.

## Status
1D scan retained as method-comparison reference ONLY. +36.5 is NOT the barrier. Verdict deferred to the
2D scan + NEB-TS. Files: k2_scan_profile.txt, k2_scan_traj.xyz, k2_scan.py, k2_scan_stdout.log.
