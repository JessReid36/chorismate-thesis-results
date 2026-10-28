# Where the approach stands, 28 October 2026

Written after Diagnostics 12 and 13 were collected from hpc1, re-measured from their outputs and
committed (results `3bef19b`, code `d408dc2`). Both gates passed on both; the two harnesses agree
to 0.000000 kcal/mol at the eight sites they share. These are now measured numbers in the
repository rather than pasted result files.

**The two verdicts answer the charge-model question, and they do not answer it the way this
morning's `ROUTE_ASSESSMENT_20261028.md` argued.** That assessment's core was already withdrawn
by its own erratum; this supersedes what was left.

---

## 1. What D12 and D13 say, in their own pre-registered words

**Diagnostic 12 — NO DESCRIPTOR IS ADEQUATE:**

> Geometry does not predict the artefact. No screen can be built from the quantities a grid has.
> Every candidate site would need its own QM check, which the grid-and-budget formulation cannot
> absorb. **The charge model must change — not the spacing, and not the surface. Moving the grid
> outward does not help, because what fails is the prediction, not the distance.**

**Diagnostic 13 — PARTIAL:**

> The magnitude dependence is real but site-specific. **A single cap cannot be stated from this
> sample; the screen would have to be per-site, which the grid cannot carry.**
> Fitted exponents span 0.61 to 4.49 (mean 2.47) over 6 sites.

Both carry the same closing limitation, and it is the one that matters most:

> ADDITIVITY … Every run carries ONE charge. A design of twenty-six charges at 0.25 e is not
> twenty-six independent probes … **Nothing here supports a claim that weak charges are safe in a
> many-charge design.**

---

## 2. What that settles for each domain

**GRID — stands. It is not the problem.**
D12 is explicit that moving the surface outward does not help, because the failure is in
prediction and not in distance. So `r_safe = 3.50 Å` is the wrong remedy whatever its value, no
rebuild follows from it, and the standing instruction against a fixed clearance floor is
untroubled. The two Dittner layers, the 2626 sites and the 3.25 Å separation all stand.

**OPTIMISER — sound in form, but it cannot screen.**
The MILP surrogate, Σq² ≤ 2.0, the separation cliques and the A matrix at L1 are all intact, and
Stage 4e established that the A matrix's signs do not follow the method across five levels
including MP2. What D12 removes is the possibility of a screen: no function of grid quantities
separates safe sites from unsafe ones, and a per-site QM check cannot be absorbed into a
grid-and-budget formulation. The optimiser is trustworthy once the charge model is, and not before.

**CHARGE REPRESENTATION — must change.**
Both diagnostics say so independently. A bare point charge with a Lennard-Jones sphere that never
enters the QM Hamiltonian (Finding 4) is not a faithful model at the distances and magnitudes the
grid admits, and nothing available to the grid can tell you where it stops being one.

---

## 3. The problem this leaves

Every candidate replacement currently on the books is blocked.
`HANDOVER_20261026.md` section 8 item 8, verbatim:

> **A charge model with an electron wall.** The ECP route (Marefat Khah) is blocked on the Ne
> table's `lmax`/block inconsistency. Smearing is ruled out by that paper. CPCM was removed for
> cause and D2.3 showed it does not fix the response.

And D12 adds the limit on the one instrument in use: the Ne ECP parameters are used outside their
published octet assumption (`ERRATUM7`), so **"the walled arm is a contrast, not a truth."** The
wall is how the artefact is measured, not a model that may be adopted.

So the position is: the charge model must change, and the three changes that have been considered
are each blocked for a stated reason.

---

## 4. What is actually unmeasured, and bounds everything

**The additivity of the artefact, at any n.** Both D12 and D13 name it as their first limitation.
What is established is the additivity of *ddE* at def2-SVP — 3.1 per cent at n = 2 and 6.1 per cent
at n = 3 (Finding 2), and 108 clean runs in `phase2b_charge_design/07_additivity`. The artefact's
additivity is a different quantity and has never been measured.

It bounds everything above. If the artefact does not add, a many-charge design at small |q| may be
faithful and the problem is confined to probes at large |q|. If it does add, then a 20-charge
design is where the artefact is worst, and every frozen number in Stage 6 is affected. Nothing in
the record distinguishes these, and D13 says plainly that nothing in it supports the optimistic
reading.

---

## 5. Order

1. **Measure the artefact's additivity.** It is the one unmeasured quantity that both diagnostics
   name, it bounds the charge-model decision, and it is a question about designs rather than probes
   — which is where every previous diagnostic has been weakest.
2. **D7 is collected and unread.** `transfer/`, 24 runs, all terminated normally, verified against
   its hpc1 manifest. It asks whether the λ ≤ 0.50 defensible domain transfers from S6-20 to S6-10,
   with a disjoint and exhaustive reading fixed before the runs. It costs an analysis call.
3. **The charge-model decision** then follows, with the ECP, smearing and continuum routes each
   needing their stated block addressed or a fourth route proposed.

Nothing on this list needs new HPC time except item 1.
