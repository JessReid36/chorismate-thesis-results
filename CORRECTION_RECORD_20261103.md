# Correction record — 3 November 2026

Enzyme QM/MM barrier reconciliation. Closes the `RECONCILE before writing` block that had
stood in WRITEUP_INDEX.md since mid-October, and corrects two committed files that were
never updated after PHASE1_AUDIT_CHECKLIST item A7 was resolved on 12 October 2026.

## Verdict

The Phase-1 enzyme barrier is **+16.00 kcal/mol** (exactly +15.9995), reaction energy
**-13.15** (exactly -13.1520). Unchanged from `phase1_system_dev/BARRIER_FINAL.md`.
Nothing in the science changed; three files disagreed with it and now do not.

## What was re-derived, and how

Last `FINAL SINGLE POINT ENERGY (QM/MM)` taken from each raw ORCA output:

| Species | Energy (Eh) | Source |
|---|---|---|
| Reactant | -1076.130494943784 | `05_qmmm/18e_reactant_reduced/reactant_reduced.out` |
| TS | -1076.104998186095 | `05_qmmm/18c_reduced_region/ts_reduced.out` |
| Product | -1076.151454007164 | `05_qmmm/18f_product_reduced/product_reduced.out` |

Conversion 627.5094740631 kcal/mol per Eh. All three in the same 102-atom reduced active
region (counted from `active_reduced.txt`: 102) on the common frozen bulk.

Independent corroboration of the TS energy: frame 22 of 22 in
`ts_reduced.QMRegion_trj.xyz` reads -1076.104998186095 — identical to the last
FINAL SINGLE POINT ENERGY. Frame 1 reads -1076.104782, the pre-optimisation value;
reading frame 1 instead would have given a barrier 0.14 kcal/mol too low.

## Why +15.08 was wrong

It subtracted the 102-atom-region TS from a ~1959-atom-region reactant (-1076.129034 Eh).
Mixed active regions. The reactant mismatch alone accounts for **0.9168 kcal/mol** — the
whole of the 16.00 vs 15.08 gap. The TS was never at fault.

The **15.3** value was never committed to either repository and has no traceable source file.

## Why the second imaginary mode was not real

`ts_frequencies_summary.txt` listed -313.30 and -18.65 cm^-1, both flagged imaginary, and
WRITEUP_INDEX.md asked whether the TS was a clean first-order saddle.

Those two values are the **starting Hessian**, printed by ORCA before optimisation cycle 1
(at E = -1076.104782 Eh, the frame-1 energy). In `ts_reduced.out`, `*** OPTIMIZATION RUN DONE ***`
is at line 96542. Imaginary modes before that line: two (-313.30, -18.65). After it, in the
converged NumFreq: **one**, at **-313.07 cm^-1**.

The reduced-region TS is a clean first-order saddle. Reactant and product NumFreq both
terminated normally with zero imaginary modes.

This also releases the ensemble write-up: A7 noted that `step19b_collect.py` relies on the
frame-820 saddle being fully characterised. It is.

## Files changed

1. `05_qmmm/18c_reduced_region/ts_frequencies_summary.txt` — frequency table replaced with
   the converged NumFreq; footer barrier corrected 15.08 -> 16.00. Superseded values retained
   in the file, explicitly labelled, so the provenance is not lost.
2. `WRITEUP_INDEX.md` — canonical-barrier row 15.3 -> 16.00 with real source files;
   RECONCILE block replaced with the resolution; model_fidelity entry flagged STALE NUMBERS.
3. `checks/verify_barrier_18c_18e_18f.sh` — NEW. Re-runnable, reproduces every number above.
4. `notes/model_fidelity_validation_framework.md` — stale duplicate replaced with the canonical
   code-repo content (see addendum below), with a do-not-edit-independently banner.

## Addendum: the source of the stale 15.3, found

An earlier draft of this record claimed the CODE repo's
`notes/model_fidelity_validation_framework.md` was stale. **That was wrong, and the error is worth
recording because it is the exact failure this audit exists to catch: the claim was carried over
from a summary note without opening the file.**

The facts, verified:

- The **code repo** copy is CORRECT. It carries 16.00, the triplet 16.37 / 15.94 / 16.00, agreement
  "to within about half a kcal/mol", and 3.3 kcal/mol above the DH! comparator. It was corrected on
  **2026-07-22** in commit `cb5cb5e` ("consistent 102-atom reduced-region barrier +16.00 / rxn E
  -13.15 (supersedes mixed-region +15.08)... [retained-final]"). Blob `52dc260f`, **byte-identical on
  all three code branches** — so the branch question never bore on it at all.
- The **results repo** copy is a STALE DUPLICATE, never updated after that correction. It still
  carries 15.3, the triplet 16.6 / 15.2 / 15.3, "roughly 1 kcal/mol", and 2.6 kcal/mol above DH!.
  It predates even the first correction (`820a30f`, 15 July, which moved the file to 15.08/16.37/15.94),
  so it is the ORIGINAL draft (`515a43b`) preserved by duplication.

**This is where WRITEUP_INDEX.md's 15.3 came from.** The index cited
`notes/model_fidelity_validation_framework.md`, and in the results repo that path resolved to the
pre-correction draft. Not the experimental DG! 15.4, not the mixed-region 15.08, not the stalled
15.2 drift — the original un-corrected number, kept alive for three and a half months by a duplicate
file that nobody had reason to re-read.

**Fix applied:** the results-repo copy is replaced with the canonical code-repo content, with a
header banner naming the canonical home and warning against editing the mirror independently.

**Recommended follow-up:** consider deleting the results-repo duplicate entirely and citing the code
repo path, since a mirror that can silently diverge is the root cause here. Left in place for now
because WRITEUP_INDEX.md and other notes point at it.

## Branch ruling (from the provenance audit, same date)

- `main` (`ad09dfe`) is a strict ANCESTOR of both other branches — the common trunk. No separate pin needed.
- `tier1-realism` (`f0cbdb0`) and `rebuild-cleanroom` (`acf133b`) are SIBLINGS forked at `e860bd7`;
  rebuild-cleanroom was never merged back.
- **`tier1-realism` @ `f0cbdb0` is authoritative** for the write-up. `rebuild-cleanroom` @ `acf133b`
  is a frozen source cited by SHA for `07_rebuild` only.
- Across all three branches only TWO files differ at a shared path: `.gitignore` and
  `phase1_system_dev/step12b_extract.sh`. Everything else is additive or disjoint.
- **Do not merge** the branches: the two `07_rebuild/L3_solver/` sets are disjoint (9 vs 73 files,
  no shared filenames) and git would union them without conflict, destroying design attribution.

## Still outstanding

Five open provenance items are recorded at the foot of WRITEUP_INDEX.md as **P1-P5**. The one that
could still affect a reported number is **P1**: `step12b_extract.sh` on `main`/`rebuild-cleanroom`
indexes a single trajectory via `np.memmap` with no bounds check, so a frame index beyond that
file's length returns wrong coordinates silently rather than erroring. Which reported barriers (if
any) used extension-segment frames cannot be determined without `selection_manifest.tsv`.

Also still outstanding: `phase1_system_dev/BARRIER_FINAL.md` (code repo) quotes the transition
vector as -313.30 cm^-1, the starting-Hessian value. Should read **-313.07**. Single-line fix on
`tier1-realism`, not included here because this bundle only touches the results repo.

`phase1_system_dev/BARRIER_FINAL.md` quotes the transition vector as -313.30 cm^-1, which is
the starting-Hessian value. Should read **-313.07**. Same branch caveat.

## Verification

    cd ~/Desktop/chorismate-thesis-results && bash checks/verify_barrier_18c_18e_18f.sh

Expected: barrier +15.9995, reaction energy -13.1520, 102 atoms, one imaginary mode -313.07.
