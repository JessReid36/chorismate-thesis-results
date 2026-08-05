## [B2-RESOLVED] Barrier under fixed external field — connected-path requirement

**Status: CLOSED (method established).**

Barriers under a fixed external charge field must be computed as follows, or they are invalid:

1. **Stationary-point screen first (GOCAT Eq 3.2/3.3).** Relax reactant AND product under the field.
   Keep only designs whose endpoints CONVERGE to intact minima (reactant: ether intact O3–C4<2.2;
   product: C1–C6 formed <1.9 AND not shattered O3–C4<5.0, ref product O3–C4=2.9). Designs failing this
   are non-catalytic by construction — no barrier is defined.

2. **NEB-CI on a CONNECTED path between the field-relaxed endpoints.** ASH/Knarr NEBTS, 12 images,
   ActiveRegion=True + actatoms=range(24) to freeze the 64 surrogate atoms (anchors the lab frame — this
   is the frame-lock; ORCA %neb Quatern is irrelevant because Knarr is ASH's own band engine). free_end=True,
   maxiter≥200. Barrier = highest band image − reactant image.

**INVALID method (do NOT use):** differencing two INDEPENDENTLY-relaxed endpoint energies,
E_TS(field) − E_react(field). Dominated by the substrate's displacement through the fixed potential (the
substrate sits at different distances from the fixed charges in the R vs TS geometry), giving
physically-impossible ±100–500 kcal/mol values. This is NOT a barrier.

**Also invalid:** using the QM/MM total or the embedded QM energy absolute value — carries a large
non-cancelling substrate–charge interaction offset (~780 kcal/mol for our 8 Å design).

**ASH NEBTS bug found:** interface_knarr.py line 416 uses `TS_guess` (None) instead of `full_TS_guess`
when ActiveRegion + TS_guess_file are combined → crash. Workaround: don't pass TS_guess_file; CI finds
the TS without a seed.

**ORCA input note:** do NOT add `EnGrad` to the simpleinput line for a geometry optimisation — ORCA
rejects it (INPUT ERROR, duplicated keyword). The optimiser computes gradients internally.
