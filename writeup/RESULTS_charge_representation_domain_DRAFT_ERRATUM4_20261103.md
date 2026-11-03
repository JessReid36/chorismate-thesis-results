# Results draft, ERRATUM 4 — the charge vectors are a file, and two statements about them are stale

**3 November 2026.** `RESULTS_charge_representation_domain_DRAFT_20261102.md` is corrected in place,
as ERRATUM 1 established and ERRATA 2 and 3 continued. Two changes, both in text that describes
where data lives rather than what it says. **No measured quantity changes and no committed result
file is edited.**

---

## E4.1 Sourcing gaps item 4 is closed

**Before:**

> 4. **A figure of the accessible design region** needs the per-site charge vectors written to a data
>    file; they currently exist only inside `relax/ARRANGEMENTS.txt` and are read
>    programmatically. Writing them out would also have prevented the max\|q\| error this draft
>    was corrected for.

**After**: the item records that the vectors are now two files in `phase2.2/cs_stage6/`, written from
each bare arm's committed `pc.pc` by `phase2.2/cs6_charges.py`, with their README. The figure is no
longer blocked on anything.

## E4.2 The figure instruction names its source

**Before**, the last sentence of the FIGURE 6.N placeholder read:

> Take max\|q\| from each bare arm's committed pc.pc, not from any
> summary table.]`

**After**: it points at `CHARGE_VECTORS_SUMMARY_20261103.tsv`, which is that reading, performed once
and checked. The instruction's intent is unchanged — the figure must not be drawn from a remembered
table — and it is now satisfiable from one file whose own provenance is recorded.

## E4.3 What this erratum does not claim

- **The vectors are not new.** They are the bytes the committed ORCA inputs carry. The nine max|q|
  values re-derive to the nine figures this draft's own verification log states, string for string,
  which is gated rather than asserted: `cs6_y55.py` refuses to write if one of them disagrees.
- **The two post-hoc correlations stay post hoc.** −0.775 and +0.338 over nine points at one basis
  and one frame are not findings, and a data file does not make them findings. The pre-registered
  test remains a max|q| ladder at fixed Σ|q|.
- **ERRATUM 1's correction stands as written.** This erratum removes the conditions that allowed
  that error, it does not revisit it.
