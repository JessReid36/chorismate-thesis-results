# K2 NEB-TS band — dissociative corroboration (supporting the switch)

ASH NEBTS (Knarr CI-NEB), 10 images, ActiveRegion=QM, K2 MM-surrogate field. Endpoints = committed
converged K2 reactant (C1-C6 5.00) and product (C1-C6 1.57).

## Reading (per-image ORCA final energies + geometry; neb_band_energies.txt)
The band does NOT find a concerted saddle. Through the transition region both bonds are long
simultaneously (O3-C4 6-7 A while C1-C6 stays 4-5 A, closing only late), i.e. a DISSOCIATIVE / slack
path where O3-C4 breaks fully before C1-C6 forms - independent of the 1D-scan artifact (reached from the
full R->P optimisation). Band not fully converged (serial QM/MM NEB, hard interpolation because the
field-relaxed reactant sits open at C1-C6 5.0) - so NOT a barrier number, but the dissociative CHARACTER
corroborates the 1D scan and the endpoint-distortion finding.

## Combined evidence (with K2_SCAN_FINDING + ENDPOINT_VALIDITY_ASSESSMENT)
Three independent lines - endpoint geometry (C1-C6 5.0 vs 3.12 bare), 1D scan (dissociative ridge), NEB
band (dissociative/slack) - all say the certified-optimal K2 frozen-proxy field pre-organises AWAY from
the concerted TS. Motivates the preorganisation-aware certified objective (05b_optimise_realism).
NOT the barrier; barrier deferred to the corrected approach.
