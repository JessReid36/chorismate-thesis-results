# Diagnostic 1: what it means, what caused it, and how to proceed

Written 22 October 2026, after `DIAGNOSTIC1_RESULT.txt` returned NOT USABLE AS THEY STAND.

An assessment, not a pre-registration. It changes nothing and fixes nothing.

**The conclusions, stated first.**

1. The reference state is sound. The control's own barrier is stable to 3 per cent between bases.
2. The effect is in the designs' **response** to the charges, not in the reference, and it is large: 28.8 kcal/mol
   for S6-20.
3. **It is not explained by the quadratic polarisation term this project already measured.** That term accounts
   for about 1 to 2 kcal/mol at the designs' distances — an order of magnitude short. Something larger is
   happening, and it only appears when diffuse functions are present.
4. The one condition in which the linear response was measured and found **accurate to 1.1 per cent** had a
   diffuse basis *and* CPCM ε = 4 — that is, the dianion was bound. We have no measurement of response quality in
   vacuo with a diffuse basis, where it is unbound. Diagnostic 1 is the first, and it is bad.
5. So the CPCM question re-opens, not to make a number look better, but because **binding the density may be a
   precondition for the linear surrogate to mean anything at all.** And ORCA's refusal to combine CPCM with QM/MM
   turns out not to block that — Finding 4 proves why.
6. Jessica's instinct about n is correct, derivable, and supported by the source method's own thesis: Behrens 2024
   states that a reaction-specific lower bound on the charge count must exist and that below it the global optimum
   is not reachable, and Dittner & Hartke used 81 charges where we tested at most 20. For a fixed total field the
   neglected quadratic term falls as 1/n. The current budget does the opposite of what that requires.
7. Finding 8's HOMO reading needs qualifying. Two held papers say a positive DFT HOMO is not proof of an unbound
   electron, and the rigorous test - the vertical detachment energy - has never been computed for this dianion.

---

## 1. The correction to my first reading: the reference is fine

My first reading was that the unbound dianion contaminates every `ddE` through the control. Wrong.

| design | n | barrier def2-SVP | barrier ma-def2-SVP | shift |
|---|---|---|---|---|
| S6-C (control) | 0 | 18.461 | 17.894 | **-0.567** |
| S6-P | 1 | 10.785 | 14.036 | +3.251 |
| S6-2 | 2 | 6.078 | 17.484 | +11.407 |
| S6-20 | 20 | **-6.365** | **+22.468** | **+28.833** |

The control moves 3 per cent, and it is independently corroborated: `SOLVATION_DECISION_NOTE.md` measured the bare
barrier in vacuum at def2-SVP against def2-SVPD as 17.905 against 17.995 — **0.090 kcal/mol**. The unboundedness
cancels in a difference between two geometries of the same species, as that note said it would.

It is the designs that move, and they move more the more charge is placed.

---

## 2. What was already measured, and why it does NOT explain this

`PHASE22_PLAN.txt` lists the surrogate stack printed with every optimiser run. Item 2:

> `2. LINEAR electrostatic response, neglecting the measured b*q^2 polarisation term`

"the measured" is literal. `phase2b_charge_design/06b_inner_shell/`, 29 September 2026, placed one bare +1 at four
standoffs on one ray and separated the response into odd and even parts
(`OUTPUT_EXCERPTS_20260929.md`):

| site | d | q·Dv (linear prediction) | odd part | **odd error** | **even part (b at q=1)** | even/\|q·Dv\| |
|---|---|---|---|---|---|---|
| parent_3.0 | 3.0 Å | -4.035 | -4.081 | **-0.046 (1.1 %)** | -0.521 | 12.9 % |
| inner_2.5 | 2.5 Å | -4.806 | -5.764 | -0.958 (19.9 %) | -1.115 | 23.2 % |
| inner_2.0 | 2.0 Å | -5.488 | -12.937 | -7.448 (136 %) | -7.353 | 134 % |
| inner_1.5 | 1.5 Å | -6.397 | -17.233 | -10.836 (169 %) | -10.549 | 165 % |

**At 3.0 Å the linear coefficient the MILP uses is recovered to 1.1 per cent.** The cliff is between 2.5 and 3.0 Å,
exactly where `PHASE22_PLAN.txt` §2.3b had guessed it would be ("beyond, say, 2.5-3 Angstrom").

Every Stage 6 design places its closest sphere at **2.85 to 2.96 Å** (`ARRANGEMENTS.txt`: 2.8466, 2.8486, 2.8817,
2.9234, 2.9596) — just inside 3.0 Å.

### The arithmetic that kills the easy explanation

My first draft of this assessment claimed Diagnostic 1 was the accumulated cost of that neglected `b`. It is not,
and the check is one line. S6-20 has Σq² = 2.048, so:

```
   b(3.0 A) = -0.521   ->   sum b*q^2  =   -1.07 kcal/mol
   b(2.5 A) = -1.115   ->   sum b*q^2  =   -2.28 kcal/mol
   b(2.0 A) = -7.353   ->   sum b*q^2  =  -15.06 kcal/mol      (no sphere is this close)
   Diagnostic 1's measured shift for S6-20          =  +28.83 kcal/mol
```

At the distances the designs actually use, the known quadratic term accounts for 1 to 2 kcal/mol. Diagnostic 1 is
twenty times that, and of the opposite sign. **The neglected `b·q²` term is real and should be restored, but it is
not what Diagnostic 1 found.**

### And note the condition of that measurement

From its own committed inputs:

```
! B3LYP D3BJ def2-SVPD def2/J RIJCOSX CPCM TightSCF
%cpcm epsilon 4.0 end
%pointcharges "pc_parent_3.0_m.pc"
```

**`def2-SVPD` — diffuse — with CPCM ε = 4.** Diffuse functions present *and* the dianion bound (HOMO -0.157 Eh at
that condition, per `SOLVATION_DECISION_NOTE.md`). Under those conditions the response to an external charge at
3.0 Å is linear to 1.1 per cent.

The production pipeline then moved to **def2-SVP, in vacuo** — no diffuse functions and the dianion unbound
(HOMO +0.082 Eh). There is no measurement anywhere in the repository of response quality in the third combination:
**diffuse functions, in vacuo, unbound.** Diagnostic 1 is the first, and it gives 28.8 kcal/mol.

---

## 3. Two measurements in this repository contradict each other, and Diagnostic 1 breaks the tie

One day after the inner-shell test, `s11_probe_scan_result.txt` (30 September) scanned a +1 probe from 1.5 to 10 Å:

> `1. NO ELECTRONIC OVER-POLARISATION ANYWHERE FROM 1.5 TO 10 A, AT FIXED GEOMETRY.`
> `   Loewdin charge shift on the nearest atom is monotone and small, -0.226 e even at`
> `   1.5 A ... The HOMO is pulled down at close range, i.e. the probe binds the unbound`
> `   dianion rather than distorting it.`

Its level, from `s11_probe_distance_scan.py` line 111:

```
LEVEL = "! B3LYP D3BJ def2-SVP def2/J RIJCOSX TightSCF"
```

**def2-SVP, no continuum.** The scan that found nothing wrong at 1.5 Å was run in the one condition that cannot
show it: no diffuse functions, around a density that is unbound and has nowhere to go. The scan that found a 134
per cent effect at 2.0 Å had diffuse functions and a continuum. Both are in the repository, they disagree, and the
production pipeline inherited the reassuring one.

**The project's conclusion that the charge model was electronically safe at short range rests on a measurement made
in a basis that could not have detected the problem.** Diagnostic 1 settles it against that conclusion.

---

## 4. What the effect scales with

Taking the extra diffuse-basis stabilisation of each design's reactant, over and above the control's own:

| design | n | Σq² (the budget) | Σ\|q\| | extra stabilisation at R | per unit Σ\|q\| |
|---|---|---|---|---|---|
| S6-P | 1 | 1.000 | 1.00 | -10.7 | -10.70 |
| S6-2 | 2 | 2.000 | 2.00 | -24.1 | -12.05 |
| S6-20 | 20 | 2.048 | 5.76 | -63.0 | -10.94 |

About **-11 kcal/mol per unit of total absolute charge**, nearly independent of distribution or sign. Correlations
of the barrier shift over the four designs:

```
   Σ|q|    (the L1 norm)         r = +0.9955
   n       (the sphere count)    r = +0.9527
   Σq²     (the L2 budget)       r = +0.8140
```

Four points, so indicative. But note what it rules out: S6-2 and S6-20 have **almost identical Σq²** (2.000 and
2.048) and shifts differing by a factor of 2.5. Whatever this is, it is not a `b·q²` term — those would be equal.
It scales with the L1 norm, is sign-independent, and I do not have a mechanism for it beyond "the basis-set
deficiency grows with total field strength". **That is an admission, not an explanation**, and section 7 is how to
find out.

### Why the budget makes it worse

The pre-registered budget is `Σ q_i² ≤ B`, an L2 ball. For fixed Σq², the L1 norm is **maximised** by spreading
charge over as many sites as possible: `Σ|q| ≤ sqrt(n·B)`. At B = 2.0 that permits Σ|q| of 2.00 at n = 2, 4.47 at
n = 10, 6.32 at n = 20. S6-20 reaches 5.76 of its available 6.32.

A linear objective on an L2 ball does not merely permit that, it prefers it — the optimum of a linear function
over a sphere loads every coordinate with a nonzero coefficient. **The formulation selects for the designs its own
surrogate describes worst.**

`PHASE22_PLAN.txt` saw the mechanism and named the remedy:

> `A linear objective over a box has its optimum at a vertex, so without a field-limiting`
> `constraint every charge saturates at +/-q_max ... s14 prints a warning when its`
> `solutions saturate and offers l1_budget, a total-field constraint sum_i |q_i| <= B, as`
> `the mechanism for interior charges until the unimodality data exists.`

`s14_design_milp.py` implements it (lines 47-48, 185-189, self-test `cfg6`). **`cs_opt_milp.py` — the optimiser
that produced the Stage 6 designs — contains no `l1_budget`; `grep -c` returns 0 against 8 in `s14`.** The
total-field constraint was not carried forward. That is a verifiable regression, and it is the single change that
would have kept the designs out of this regime.

---

## 5. Jessica's question: could it work at some other n? Yes, and the algebra says so

Write the response as the project's own model does:

```
   ddE  =  Σ a_i q_i    +    Σ b_i q_i²    +   Σ dE_LJ
           ^^^^^^^^^^         ^^^^^^^^^^^
           what the MILP      the measured term it neglects
           optimises
```

The useful part is **linear** in charge, so it scales with `Σ|q|`. The neglected part is **quadratic**, so it
scales with `Σq²`. Spread a fixed total field `Q = Σ|q|` equally over n sites, so `q_i = Q/n`:

```
   first order   Σ a_i q_i   ~  Q          independent of n
   second order  Σ b_i q_i²  ~  Q²/n       falls as 1/n
```

**For a fixed total field, the neglected term falls as 1/n.** Many weak charges approximating a smooth external
field is not merely safer than a few strong ones — it is the limit in which the linear surrogate the whole MILP
rests on becomes exact. That is the regime Jessica is pointing at, and it is unreachable under the current budget,
which fixes Σq² and lets Σ|q| grow as sqrt(n) — holding the error constant while growing the field, the exact
inverse of what is wanted.

The measured designs already show it per unit of field:

| design | n | Σ\|q\| | Σq² | **Σq²/Σ\|q\|** (error per unit useful field) |
|---|---|---|---|---|
| S6-P | 1 | 1.00 | 1.000 | 1.000 |
| S6-2 | 2 | 2.00 | 2.000 | 1.000 |
| S6-20 | 20 | 5.76 | 2.048 | **0.355** |

S6-20 is the **cleanest** design per unit of field it applies, by a factor of nearly three. It looks worst only
because it applies 2.9 times more total field. Its problem is Σ|q| = 5.76, not n = 20.

### How many charges, from the project's own calibration

`s11_probe_scan_result.txt` finding 2:

> `2. A BARE +1 UNDERSHOOTS THE REAL ARGININE BY A FACTOR OF 3.5.`
> `   Mean ddE at 3.2 A is -1.53 kcal/mol against Burschowsky's measured differential of`
> `   -5.3 ... So one point charge delivers 29 per cent of what the guanidinium achieves.`
> `   ... It also means a single charge cannot reach the Burschowsky benchmark.`

Taking -1.53 kcal/mol per unit charge at 3.2 Å:

| target | Σ\|q\| needed | at \|q\| ≤ 1.00 | ≤ 0.50 | ≤ 0.25 | ≤ 0.15 |
|---|---|---|---|---|---|
| -5.3 (one Arg90) | 3.5 e | 3 sites | 7 | 14 | 23 |
| -10.0 | 6.5 e | 7 sites | 13 | **26** | **44** |

So "34 or something like that" is the right order of magnitude, and it falls out of the project's own measured
per-charge response combined with a per-site cap small enough to keep the quadratic term negligible.

**What this does not establish.** That such a design exists. The grid must hold 26-44 mutually compatible sites at
≥ 3 Å under the 3.25 Å separation rule, with favourable `a`, and `a` falls off with distance so outer sites buy
less. Whether an admissible distribution reaches a useful reduction is the open question. The firm point is
narrower: **the regime in which the method could work has not been tested, and the current formulation cannot
reach it.**

---

## 6. CPCM: the decision was well-reasoned, and the physics has changed under it

The record is explicit and the reasoning was sound. `PHASE22_PLAN.txt` §2.2:

> `A continuum next to the charges supplies the same electrostatic stabilisation`
> `the charges are being optimised to provide.`

plus literature fidelity: [D2018] uses COSMO only to define the target path, [B2021] uses no continuum at all.
Formalised as D1 in `CHARGE_MODEL_DECISIONS.md` and reaffirmed "Unchanged" at six stage gates.

`SOLVATION_DECISION_NOTE.md` (29 September) had recommended the opposite and was overridden the next day:

> `Removing the continuum alone is well founded by GOCAT practice, but **cannot be`
> `done in isolation**: the bare dianion is unbound in vacuum (section 2), so`
> `designed charges would then be doing two jobs at once - binding the excess`
> `electron density and catalysing the reaction. The optimiser cannot distinguish`
> `them and would likely spend charges on the former.`

That prediction landed as Finding 8, three weeks later. D1 recorded the exposure honestly — "**What stays
exposed.** The polarisation term b is the quantity most affected by an unbound dianion, so WP7 repeats two sites at
def2-SVPD" — and that repeat was never run.

**What is new is this.** The double-counting argument is about *catalytic* stabilisation, and it is quantitatively
small: the measured differential is **0.431 kcal/mol at ε = 4**, against a target reduction of order 10-20. What
the continuum also does is *bind the density* — a different job, as the 29 September note itself distinguished.
And the only evidence we have about whether the linear response is well-behaved comes from the condition where it
was bound: **1.1 per cent at 3.0 Å**. In vacuo with a diffuse basis the response is evidently far worse.

So there is a coherent physical argument that was not available when §2.2 was written: an unbound density is
pathologically polarisable, its response to an external field is not representable in a non-diffuse basis and not
linear in a diffuse one, and a continuum that binds it may be what makes `a_i` a meaningful coefficient at all.

### ORCA's restriction does not block this, and Finding 4 is why

The standing objection is that ORCA 6.0.1 refuses CPCM with QM/MM: "CPCM or SMD or ALPB or ddCOSMO or CPCMX
requested together with QM/MM method. This is not implemented." Dropping CPCM is what made the LJ-bearing site
available (`s13_lj_test.pbs.out`: `PASS: QMMM ran without CPCM`).

But the refusal applies to the `%qmmm` module, not to `%pointcharges` — and the 29 September inner-shell runs
prove it, because they ran CPCM with `%pointcharges` and produced the table in section 2.

And **Finding 4 proves the two are electronically identical.** Same site, same +1: the LJ sphere and the bare point
charge differ by exactly `L`, to 0.0000 kcal/mol, with identical electronic deviation — "necessary, since the
Lennard-Jones term never enters the QM Hamiltonian."

Therefore the electronic part of the design environment can be computed as **bare point charges + CPCM**, which
ORCA permits, with `L` added classically from the committed L matrix. The QM/MM machinery is needed only for the
Lennard-Jones energy, which is a classical quantity computed independently and already committed.

**Scope of that unlock.** It covers the A matrix, the frozen single points and the response measurements — which is
where the problem is. It does **not** cover the relaxations: Finding 4 also says the wall's "entire value is in the
relaxation", where WP4's bare charge collapsed onto O2 at 0.95 Å while its sphere stopped at 2.54 Å. A relaxed
optimisation still needs QM/MM, and therefore still cannot have CPCM in this code.

I am not recommending CPCM. I am saying the reason it was excluded no longer covers the case, the cost of
excluding it is now measured rather than hypothetical, and the choice should be made again on current evidence
with the measurement in section 7 in hand.

---

## 7. The decisive experiment

One measurement separates every branch above, and this project designed it a month ago and never recorded it.
`s11_probe_scan_result.txt` ends:

> `STILL PENDING: the charge-magnitude scan at 3.2 A (q = 0.25, 0.5, 1.0, 1.5), which`
> `fits ddE(q) = a*q + b*q^2 and so measures the linear coefficient the MILP uses and the`
> `differential polarisation it neglects. PBS 414212.`

The companion table in `OUTPUT_EXCERPTS_20260929.md`, headed "Charge-magnitude scaling: does the even part go as
q²?", is **empty**. The scan never produced it.

Run it at site 1690 — S6-P's site, the grid's top-ranked — at q = 0.05, 0.25, 0.50, 1.00, at R and TS, across
**three conditions**:

```
   (i)   def2-SVP      in vacuo     the production condition
   (ii)  ma-def2-SVP   in vacuo     Diagnostic 1's condition
   (iii) ma-def2-SVP   CPCM eps=4   diffuse AND bound - the only condition in which the
                                    linear response has ever been found accurate
```

Bare point charges throughout, so all three are permitted in ORCA and all three are electronically comparable by
Finding 4. 48 single points of about five minutes.

```
   the slope as q -> 0    is a_i, per condition.
                          If (i) and (ii) AGREE, the A matrix is sound and the problem is purely that the designs
                          operate outside the linear regime - a formulation fix, no Stage 5 rerun, sections 4
                          and 5 are the way forward.
                          If they DISAGREE, Stage 5's A column must be re-derived and nothing below it stands.

   the curvature          gives the largest per-site |q| for which the surrogate is valid at this distance, per
                          condition - the number both the L1 budget and any charge cap require, and which no
                          amount of reasoning can supply.

   (iii) against (ii)     answers whether binding the density is what makes the response linear. If (iii) is
                          well-behaved and (ii) is not, that is a physics argument for the design environment,
                          and section 6 becomes a live decision rather than a question.
```

Against the ~750 core-hours of the fourteen relaxations, this is nothing, and it decides whether those relaxations
have a referent at all.

Three cheap companions. First, the **vertical detachment energy** of the bare dianion against its monoanion at
the reactant geometry - two single points - which is the rigorous test of whether the species is bound that §11.3
says the HOMO sign cannot provide, and which no paper held has ever computed for chorismate. Then fold
**def2-SVPD** in as a fourth basis to discharge WP7's never-run guard and to say
whether `ma-def2-SVP` is converged or just the next point on a trend; and repeat the four ADD-* additivity runs at
`ma-def2-SVP`, since Finding 2 measured additivity at def2-SVP only and additivity is what the whole MILP rests on.

---

## 8. The formulation changes, and what they cost

None requires new HPC work. All are free; the question is which are justified.

| change | cost | basis |
|---|---|---|
| minimum sphere-to-substrate distance ≥ 3.0 Å | free, a floor in the grid | the 29 Sept table: linear to 1.1 % at 3.0 Å, 20 % at 2.5 Å; §2.3b's own guess; Stare's r > 3 Å |
| L1 total-field budget `Σ\|q_i\| ≤ B₁` | free; `s14` already implements it; linear, MILP stays a MILP | §4-5, and the plan's own stated remedy |
| per-site charge cap from §7's curvature | free; tightens existing bounds | §7 |
| restore `b·q²` — Tier 2 | non-convex MIQP, Gurobi ≥ 9 or BARON | see below |

On Tier 2 the plan set its own trigger: "Build it only if the ranking-stability test shows the quadratic term
reorders the top designs." Diagnostic 1 shows the neglected terms do more than reorder them — they reverse the sign
of the best one. The trigger is met. But section 2's arithmetic says `b·q²` as measured is not the dominant term
here, so building the MIQP would restore a term worth 1-2 kcal/mol while leaving a 28 kcal/mol effect
unexplained. **Section 7 before Tier 2.**

---

## 9. What is established, and what is not

**Established by measurement:**

- The frozen `ddE` values are not basis-converged; the largest moves 118 per cent and reverses sign.
- The movement is in the designs, not the reference (control stable to 3 per cent, corroborated at 0.090 kcal/mol
  by the independent def2-SVPD comparison).
- The linear coefficient is recovered to 1.1 per cent at 3.0 Å and 20 per cent at 2.5 Å, at def2-SVPD/CPCM(ε = 4).
- Every design places charge at 2.85-2.96 Å, just inside that cliff.
- The known `b·q²` term accounts for 1-2 kcal/mol at those distances, not 28.8.
- The effect scales with `Σ|q|` (r = +0.9955) and not with `Σq²` (S6-2 and S6-20 have equal Σq² and shifts
  differing 2.5-fold).
- `cs_opt_milp.py` has no L1 budget; `s14_design_milp.py` does.
- Findings 3 and 4 are molecular-mechanics identities and are untouched; Finding 7 is about geometry and is
  untouched.

**Not established:**

- **What the 28.8 kcal/mol is.** The dominant mechanism is unidentified. Section 7 is designed to find it.
- Whether `a_i` is basis- or condition-sensitive. The pivotal unknown.
- Whether `ma-def2-SVP` is converged, and whether it is even the better of the two. Neither basis in section 1's
  table is an arbiter: def2-SVP cannot represent the response, while the diffuse set admits the spill-out that
  Marefat Khah et al. 2020 (held) say requires Pauli repulsion to control - which our Lennard-Jones walls, by
  Finding 4, do not provide. The answer is bracketed, and the diffuse number is not automatically the better one.
- Whether the dianion is in fact electronically unbound. The HOMO sign is a weak indicator for DFT orbitals
  (§11.3); the vertical detachment energy is the test and has never been computed for this species.
- Whether additivity survives at a diffuse basis.
- Findings 1, 5 and the magnitudes of 6, 8, 9.
- Whether a large-n, small-q design can reach a useful reduction.

**Open obligations found in the record while checking this:**

- D1: "every final design gets one CPCM (ε = 4) single-point check of its barrier lowering before it is reported."
  No result file or stage report records this ever being run.
- D1 / WP7: "repeats two sites at def2-SVPD". Never run.
- `s11`: the charge-magnitude scan, PBS 414212. Never recorded.
- `step_7b` required preserving CPCM because "every frozen-density number in Phase 2 uses it, so dropping it
  breaks comparability", and `WRITEUP_INDEX.md` marks all seven canonical barrier rows `CPCM eps=4`. §2.2 does not
  address the comparability break. The methods chapter will have to.

---

## 10. What should not happen next

**The fourteen relaxations.** `Loss = ddE(frozen) - ddE(relaxed)`, and `ddE(frozen)` has moved 118 per cent with
its sign reversing. ~750 core-hours measuring a difference against a quantity uncertain by more than its own
magnitude yields a number that cannot be interpreted either way.

**Adopting CPCM because it improves a number.** If it is adopted it must be because section 7 shows the response is
only linear when the density is bound — a statement about the model's validity, not its results. If section 7 shows
(ii) and (iii) behave alike, the §2.2 decision stands untouched.

**Concluding that charge-based design fails.** Nothing here supports that. A single +1 at the top-ranked site
lowers the barrier by 3.9 kcal/mol at the diffuse basis — right sign, and 29 per cent of a real arginine,
consistent with the project's own calibration. What has been shown is that a linear surrogate was applied outside
the regime where its corrections are small, that the optimiser's budget pushes it there, and that the regime where
it could work — many charges, each small, beyond 3 Å, under a total-field budget — is untested and is the regime in
which the surrogate becomes exact.

---

## 11. Literature, from full texts held in `chorismate-refs/`

Every quote below is from a paper in the library, read in full and page-verified against the offsets
`LIBRARY_ERRATUM2_20261021.md` fixes. Requests are listed separately at the end and nothing above rests on them.

### 11.1 The charge count — the source thesis says a reaction-specific lower bound must exist

**Behrens, *From Abstract to Concrete: Advancing the Globally Optimal Catalyst Method*, PhD thesis, Kiel 2024**
(`gocat_1.pdf`), printed pp. 3-4:

> "When GOCATs are optimized for an arbitrary reaction, the required complexity (e.g., the number of point charges)
> is unknown prior to the optimization. ... Thus, with GOCATs that are limited to an absolute charge value of 1 e
> per point charge, **a lower limit that is unique to the reaction in question must exist. If a GOCAT is optimized
> with fewer charges, the globally optimal solution is not obtained.**"

printed p. 61:

> "Naturally, there are lower limits to the number of charges that can still reproduce the needed complexity and
> field strength. But as of now, **there is no way of telling what those are, other than by trial and error.**"

and the one published number, printed pp. 54-55, reducing Dittner's 81-charge Diels-Alder design:

> "It is clear that fewer than 12 charges are not enough to reproduce the reference fitness on re-evaluation."
> "In general, 12 charges, which was taken as the lower limit above, is apparently still insufficient to reliably
> reproduce the reference fitness, so slightly more should be used".

**This is direct support for Jessica's point, from the source method's own thesis.** The charge counts the GOCAT
papers actually use, with no justification given for the count: Dittner & Hartke 2018, N_Ch = 1 and 10; Dittner &
Hartke 2020, N_Ch = 10 on a van der Waals surface, **N_Ch = 81** on a 7.5 Å sphere, and 1800 for the plate
capacitors used as a homogeneous-field reference. Stage 6 tested 1, 2, 3, 5, 10 and 20. The published practice for
a reaction of this kind sits above our ceiling, and the method's own thesis states that below the reaction's
threshold the global optimum is simply not reachable.

### 11.2 Neither of our two bases is an arbiter — and the library holds the paper that says why

**Marefat Khah, Reinholdt, Olsen, Kongsted & Hättig, *Avoiding Electron Spill-Out in QM/MM Calculations on
Excited States with Simple Pseudopotentials*, JCTC 2020** (`acs.jctc.9b01162.pdf`), PDF p. 2 (abstract):

> "QM/MM calculations of electronic excitations **with diffuse basis sets** have often large errors due to
> spill-out of electrons from the quantum subsystem. **The Pauli repulsion of the electrons by the environment has
> to be included to avoid this**"

Their remedy is pseudopotentials on the MM sites. This is excited states rather than barriers, so it is not a
quantitative transfer — but it is the mechanism, and it says plainly that adding diffuse functions to a QM region
embedded in bare MM charges introduces an error of its own. Our charges carry Lennard-Jones parameters, which
Finding 4 proves never enter the QM Hamiltonian, so our MM sites have **no** Pauli repulsion for electrons at all.

So the bracket in section 9 has a citation on both sides: def2-SVP cannot represent the response, `ma-def2-SVP`
can but admits spill-out that nothing in our model opposes. **The true value is bracketed, and the diffuse number
is not automatically the better one.**

### 11.3 The HOMO reading in Finding 8 needs qualifying

Finding 8 reads a positive HOMO as meaning the highest electrons are unbound. Two full texts held say that
inference is not valid for DFT orbitals.

**Rienstra-Kiracofe, Tschumper, Schaefer, Nandi & Ellison, Chem. Rev. 2002, 102, 231-282** (`cr990044u.pdf`),
PDF p. 16 (printed p. 246):

> "the positive HOMO energies obtained with inexact DFT functionals appear to be a manifestation of the fact that
> the exact functional is not known and that approximate basis sets are employed ... it is well-known that hybrid
> functionals alleviate some SIE through their partial incorporation of HF exchange, and often produce negative
> HOMO energies for even anions."

and p. 246 on the inference itself: "Conclusions of unboundedness were based on applications of Koopmans'
theorem—valid for the unknown, exact functionals—to anions with positive HOMO energies, a consequence of electron
SIE in inexact functionals."

**Galbraith & Schaefer, JCP 1996, 105, 862** (`1.471933.pdf`), PDF p. 3 (printed p. 863):

> "While a positive HOMO energy in Hartree–Fock theory would indicate an unbound electron via Koopmans' theorem,
> **the physical significance of the orbitals obtained from density functional methods is questionable.**"

Both concern monoanions with augmented bases, so neither refutes Finding 8 — but both mean the B3LYP HOMO sign is
a weak indicator, not proof. **The rigorous test is the vertical detachment energy against the monoanion, and no
paper held computes the HOMO or the VDE of the chorismate dianion in any basis.** Two extra single points would
settle it; see section 7.

### 11.4 The reference state is well supported, and for this reaction specifically

**Claeyssens, Ranaghan, Manby, Harvey & Mulholland, Chem. Commun. 2005, 5068-5070** (`b508181e.pdf`), p. 5069:

> "Discussion of catalytic effects ideally requires comparison of energy profiles in the enzyme and in solution.
> The barrier in solution, relative to the enzyme-bound conformation, has been found in previous work to be similar
> to that in the gas phase. ... **We use the gas-phase profiles as a convenient and meaningful reference.**"

Their in-vacuo barrier for this dianion is "an average barrier height of 16.2 kcal mol⁻¹ (s = 0.3 kcal mol⁻¹)"; our control gives 18.461 at
def2-SVP and 17.894 at `ma-def2-SVP`, the same range. **Szefczyk, Mulholland, Ranaghan & Sokalski, JACS 2004,
126, 16148** (Project upload, text extraction only), p. 16152, chooses the same: "In the current work, we define
the TS stabilization with respect to the gas-phase reaction".

And on this exact reaction and this exact dianion, **Ranaghan, Ridder, Szefczyk, Sokalski, Hermann &
Mulholland, Org. Biomol. Chem. 2004, 2, 968-980** (`B313759G (1).pdf`) shows the pattern we should be following
rather than a statement about diffuse functions. Verified from the full text: geometries were optimised at
"the ab initio RHF/6-31G(d) QM/MM level", a non-diffuse basis, and the barrier was then **corrected by
diffuse-augmented single points** — "7.4-11.0 kcal mol⁻¹ (MP2/6-31+G(d)//6-31G(d)/CHARMM22) and 12.7-16.1
kcal mol⁻¹ (B3LYP/6-311+G(2d,p)//6-31G(d)/CHARMM22)". A modest basis for the pipeline, diffuse functions as a
correction, is published practice on this reaction.

**A process note on that paper.** My literature search returned a quotation attributed to its p. 970 —
"Diffuse functions were not used, because the 6-31G(d) basis set gives good results, similar to 6-31+G(d), for
this reaction..." — which would have been the single most convenient sentence in this document. **It does not
exist.** The phrase appears nowhere in that paper, nowhere else in `chorismate-refs/`, and nowhere in the Project
text extractions; the word "diffuse" does not occur in the paper at all. It is removed, nothing above rests on it,
and it is recorded here because a fabricated quote that happens to support the conclusion is the most dangerous
kind. Everything else in this section was checked phrase-by-phrase against the PDFs and located to a page.

### 11.5 Additivity, which the whole MILP rests on, is asserted rather than demonstrated

**Sokalski, J. Mol. Catal. 1985, 30, 395-410** (`0304-5102%2885%2985049-5.pdf`), p. 405, states the surrogate our
score is: "the difference of molecular potentials V_TC − V_SC represents the catalytic activity of a single unitary
positive point charge", and extends it to many charges with:

> "Additionally the model may be generalized for multiple point charge representations, **as the nonadditive
> effects are negligible [13]**."

That is a citation, not a demonstration, and ref. 13 is not held. Szefczyk 2004 p. 16157 likewise asserts "As the
electrostatic effects are additive". The only quantification held is **Beker, van der Kamp, Mulholland &
Sokalski, JCTC 2017** (`acs.jctc.6b01131 (2).pdf`), §4.2, and it is a two-subsystem pairwise error in an enzyme,
0.4-0.6 kcal/mol, not a scaling law in the number of charges.

**Nothing in the library addresses how the accuracy of a first-order electrostatic surrogate degrades as more
charges are added.** The `Σ|q|` observation in section 4 is therefore not a known result being rediscovered. It is
unsupported by literature in either direction, which is a reason to measure it properly rather than to trust it.

### 11.6 On a continuum binding a metastable dianion

**Dreuw & Cederbaum, *Multiply Charged Anions in the Gas Phase*, Chem. Rev. 2002, 102, 181-200**
(`cr0104227.pdf`), p. 198:

> "electronically unstable MCAs are tremendously stabilized by the solvent ... the vertical electron detachment
> energy (EDE) of sulfate (SO₄²⁻) increases by about 11.2 eV from −1.6 eV to 9.6 eV in water and the EDE of
> phosphate (PO₄³⁻) by about 14 eV from −5.5 eV to 8.5 eV".

GCOSMO at MP2 on small inorganic ions, so this is the regime and not a number for chorismate. p. 183 is closer to
our species: dicarboxylate dianions "acquire their electronic stability through charge localization at the ends of
the chain in separate electron affine carboxylate groups". p. 196 records a detachment energy changing sign with
basis: "Although the vertical EDE is clearly negative at all levels of theory when the standard DZP basis set is
used, it turns to positive values when diffuse functions are included".

And on def2-SVP for anions, from its authors — **Weigend & Ahlrichs, PCCP 2005, 7, 3297** (`b508541a.pdf`),
p. 3303: "This is a general problem for the description of anionic compounds with small bases"; p. 3302: "as mean
errors for different types of compounds are quite different for DFT/def2-SVP, this combination **should be used
with care**."

### 11.7 Over-polarisation by point charges, from outside the library

**Kałka, Novotný & Stare, *J. Chem. Inf. Model.* 2025, 65(16), 8653-8663, doi:10.1021/acs.jcim.5c01235** (open
access, read in full; **not in `chorismate-refs/` — worth adding**). It names the mechanism — "This artifact is
called electron spill-out as the electron density leaks from the QM region into the MM environment", driven by "an
incorrect, purely attractive potential exerted by positive point charges close to the boundary"; it reports our
Finding 6 as its own symptom — the stabilisation "was sometimes evidently exaggerated (in a minor part of cases,
**leading even to negative activation energies**)"; it puts agreement between point-charge and quantum treatments
at "sufficiently large separations (**r > 3 Å**)", with the discrepancy concentrated at 2.0-3.0 Å, independently of
and in the same place as the 29 September table; and it finds anionic kernels about twice as bad (RMSE ≈ 1-1.5
kcal/mol neutral, 3-7.5 charged; HisA at Q = −2: 5.59). Its basis is 6-31+G\*\* — diffuse. Its cure is
short-range charge damping, with the useful range for charged kernels "not exceed[ing] 2.0 Å".

### 11.8 What the library cannot support, and the requests

Three gaps matter, and no claim above depends on them:

1. **No held paper states that a non-diffuse basis artificially confines a metastable dianion's unbound density
   and thereby makes a barrier change look meaningful when it is not.** That specific claim must not be made. What
   is supported is weaker and assembled from §§11.2, 11.3, 11.6.
2. **No held paper computes the HOMO or the VDE of the chorismate dianion**, in any basis.
3. **No held point-charge design study treats an anionic substrate in a Gaussian basis set.** Dittner & Hartke
   2018 and 2020 are PM7 on neutral substrates; Dubey 2020 is a neutral Menshutkin under an applied field;
   Behrens 2024 §6.3 is the only anionic case and is GFN2-xTB/GBSA, so there is no basis-set question in it at
   all. **There is no published precedent for our basis-and-environment choice on a −2 substrate.** That is worth
   knowing for the methods chapter: the choice has to be defended on measurement, because no precedent carries it.

Requests, with checked identifiers, none of them load-bearing above:

- Sokalski 1985 ref. 13 — the source of "the nonadditive effects are negligible". Identifier not recoverable from
  anything on disk; the reference list of `0304-5102%2885%2985049-5.pdf` would need reading first.
- Beker et al. 2017 ref. 48 — where the nonadditivity error is "discussed in an earlier work". Same.
- Papajak & Truhlar, *J. Chem. Theory Comput.* 2011, **7**, 3027-3034, doi:10.1021/ct200106a — what minimal
  augmentation does and does not recover; bears on whether `ma-def2-SVP` can be an arbiter at all.
- Zheng, Xu & Truhlar, *Theor. Chem. Acc.* 2011, **128**, 295-305, doi:10.1007/s00214-010-0846-z — the ma-def2
  definition.
- Agbaglo et al. 2024 correction, *PCCP* **28**, 8283-8284, doi:10.1039/d6cp90040b — already flagged in
  `literature_position.txt` as held-uncorrected.
- Ranaghan et al., *Mol. Phys.* **101** (2003) 2695-2714 — already `sourcing_gaps.txt` item 5.

Library housekeeping found on the way: `ja9621760.pdf` has no text layer and is the **Supporting Information
only** for Jorgensen 1996 (OPLS-AA), not the main paper, so the sp³-carbon ε that Stage 2 took from it can only be
read from rendered page images. And `ja049376t.pdf` (Szefczyk 2004), `nihms1987271.pdf` (Agbaglo 2024) and
`2011_paper.pdf` (Claeyssens 2011) exist only as Project uploads with no PDF in `chorismate-refs/`; if that repo
is meant to be self-contained they should be added.
