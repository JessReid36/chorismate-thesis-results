# Optimiser stage: the decisions (20 October 2026)

Written as a draft for Jessica and her supervisor, revised after an independent review, and decided by Jessica on 20 October 2026. The decisions are summarised in `CHARGE_MODEL_DECISIONS.md` under "Update: the optimiser stage decided (20 October 2026)"; this document holds the reasoning and the citations behind them.

**Status (20 October 2026): Jessica has decided.** She agreed to all ten recommendations and to both changes, with one amendment: decision 7's re-scored pool is the best **20** for now, to be widened to 100 later if wanted, and the short list is option **(b)**, the top ~10 overall plus the best of each carried-forward n. The text below is amended to match. Each decision is now:
- appended to `phase2.2/CHARGE_MODEL_DECISIONS.md`;
- fixed in the optimiser-stage pre-registration before any design is read (plan update, Stage 4d section: "fixed in the optimiser-stage pre-registration").

**Two decisions change what the committed records say.** They are marked **CHANGE** and need explicit sign-off:
- Decision 2: where the reactant-gradient term sits. The plan update §4 item 5 and §5 require it in the design objective; this draft puts it in the re-scoring stage, not inside the MILP.
- Decision 3: the electronic screens' thresholds are fixed earlier than planned. The plan update after Stage 4c fixes them "when validation is pre-registered", which comes after the optimiser stage.

**What it answers.** The ten open questions of the optimiser brief of 15 October 2026 (kept with the Project notes, not in this repo).

**Its sources.**
- **The library** (chorismate-refs 28eec7b, plus Szefczyk et al. 2004 from the Project), cited by page.
- **The project's committed records.**

Where a recommendation goes beyond what the papers did, it is marked as this draft's proposal. Every recommendation states its direction: whether it moves designs towards or away from a lower barrier, and compared with what.

**Inputs the optimiser receives** (fixed by Stage 5):
- the sites of the two-layer grid, each with the charges it admits;
- a = V_TS − V_R per site and frame;
- L (the sphere's Lennard-Jones energy, TS minus R) per site and frame;
- the 3.25 Å minimum distance between spheres.

Production frames are the SP package's complete frames. For code testing only, the development set on the 30 Phase 1 band frames is used: `dev_sites_a2.tsv` (Stage 5 Amendment 2; same sites as `dev_sites.tsv`), `dev_L.tsv` (unchanged by the amendment), and `A_dev.tsv` from x87. `site_effect_map/` shows the development set.

---

## 0. The optimiser in plain words

The optimiser is a **search with rules**. It has three parts.

1. **What it may choose (the decision variables).**
   - For every grid site: is there a sphere here, yes or no? This is a *binary* variable, 0 or 1. A site that admits two separate charge ranges gets one yes/no for each range, and at most one may be "yes".
   - If there is a sphere, what is its charge? This is a *continuous* variable, any number within the range chosen.
2. **What it is trying to make small (the objective).** The design's score: the change in barrier the spheres cause, averaged over the frames, plus a penalty for frames where the design does worse than its average. Lower is better, so "worse" means above the average.
3. **What it must obey (the constraints).** For example:
   - exactly n spheres;
   - no two spheres closer than 3.25 Å;
   - each charge within the range its site admits;
   - a limit on how much charge the design may use in total (the *budget*).

**Why it is a MILP.** Every quantity in the score and the rules is a number times a decision, added up. That makes the problem a **mixed-integer linear program (MILP)**: "mixed-integer" because some decisions are yes/no, "linear" because everything is a sum of numbers times decisions. The one rule that is not of that kind, a budget on squared charges (decision 3), is replaced by many straight-line rules, so the problem stays a MILP.

**How the solver works.** A solver such as HiGHS, which the project already uses, does not try every combination; there are far too many. Instead it:
- solves easier relaxed versions of the problem, in which the yes/no decisions may take fractional values;
- uses those to rule out whole families of combinations at once;
- keeps two numbers: the best design found so far, and a proven bound below which no design can go.

**The optimality gap** is the difference between those two numbers. When it is zero, the best design found is provably the best possible *for that score and those rules*. It is not proven to be the best catalyst. That distinction matters for decision 8.

---

## 1. Corrections to our own records found in the library

These change no result. They should be fixed in the records before anything relies on them.

1. **"±0.751 e" is not a charge.**
   - What our records say:
     - the plan update after Stage 4c: Dittner & Hartke's Fig. 11 design "has charges within +-0.751 e";
     - the s14 docstring: Fig. 11 "finds charges at +/-0.751, NOT saturated".
   - What the paper shows: ±0.751 e is the colour-scale range in the Fig. 11 caption (Dittner & Hartke 2018, manuscript p. 35, PDF p. 36). The charges labelled in that figure are at most 0.193 e. The largest labelled in the paper's main figures is 0.294 e (Fig. 8, p. 30).
   - The paper prints no charge bounds in its main text. Dittner's thesis gives the usual bounds as [−1, +1] e (pp. 10 and 19).
2. **Behrens' σ = 3.55 Å is a sphere-to-sphere value.**
   - It is the σ of the repulsion between two quasi-atoms (Behrens' thesis, p. 60, footnote 1, Eq. 5.6).
   - The quasi-atom's Lennard-Jones term with the substrate is only said to mimic an sp³ carbon; no numbers are given.
   - STAGE5_CRITERIA uses 3.55 Å as the analogue of the sphere–sphere spacing, which is correct.
   - The Project's library index ("fixed sp3-C LJ, σ = 3.55 Å") is imprecise.
3. **HANDOFF §5 B5's "−0.11 and +0.09 e" are one-charge values.**
   - They come from Dittner & Hartke's N_Ch = 1 runs (2018, manuscript pp. 23–24; thesis p. 136). Their ten-charge designs carry labelled charges up to 0.29 e.
   - Scaling B5's own measurement (1.124 kcal/mol at unit charges) bilinearly gives about 0.1 kcal/mol at 0.3 e and about 1.1 kcal/mol at ±1 e.
   - Re-scoring (decision 7) measures this term exactly, so nothing breaks. But B5's "fifty times below the resolution limit" holds only for very small charges.
4. **The Sokalski catalytic-field papers impose no budget or normalisation.**
   - The "optimal catalytic field" is a map of the effect of a unit charge (+1 or −1) at each point (Sokalski 1985 p. 405; Szefczyk et al. 2004 Fig. 6, p. 16155).
   - None of the four papers optimises charge sizes.

---

## 2. The decisions at a glance

| # | Question | Recommendation | Direction | Waits on |
|---|---|---|---|---|
| 1 | Polarisation (b) | Not in the MILP score. The pool is re-scored with full def2-SVP single points, which contain b and the cross terms exactly. | None on ranking as measured. This was measured on eight widely separated arrangements; near-ties may reorder, which is why the pool is re-scored. Frozen magnitudes are 10–31 % too small until re-scored. | — |
| 2 | Preorganisation (**CHANGE**) | The reactant-gradient term enters the re-scoring objective, computed per design. It does not enter the MILP. Its threshold and weight come from Stage 6. | Compared with the committed plan (term inside the objective): the MILP pool may hold stronger-pulling designs, which is towards a lower frozen barrier. The re-scoring term acts against them. | Stage 6 |
| 3 | Budget (+ **CHANGE** in timing) | Σq² ≤ B. B is set by the plan's two electronic screens on stress-test designs, before any optimised design is read. | A smaller B acts against a lower barrier. The criterion is independent of any barrier, but taking the largest B it allows is the most permissive choice: towards a lower barrier compared with any smaller B. The straight-line stand-in for q² loosens the budget by at most 0.0025 e² per sphere: towards a lower barrier, and reported. | Stage 6, calibration |
| 4 | Total charge | Not forced to zero. Reported with every design. | Compared with neutrality: towards a lower barrier (more cations near O3). | — |
| 5 | Combining frames | The mean over all complete frames plus λ × semi-deviation. λ is tied to the 95 % confidence interval: 0.94, 1.03 and 1.17 at 30, 25 and 20 frames. | Neutral to conservative: the penalty only adds. | final F |
| 6 | Number of spheres | Solve n = 3, 4, … Stop at the first n whose best design fails to beat the best at n − 1 by more than both the frame spread and the method uncertainty. | Neutral. | — |
| 7 | Pool and short list | Per n, the 10 best distinct designs. The **20** best of the pool re-scored on every frame (Jessica, 20 October; widened to 100 later if wanted). Short list **(b)**: the top ~10 overall plus the best of each carried-forward n. | Neutral. Re-scoring 20 rather than 100 narrows the window for reordering; stated as a limitation. | — |
| 8 | "Optimal" | Report the solver's gap as a property of the score; never "optimal catalyst"; follow the 2 September fork. | None. | — |
| 9 | Path validity | No path constraints in the MILP. Path validity is tested by the relaxed chain (A2.5). | Neutral. | — |
| 10 | Null distribution | Random designs under the same rules: random sites with random charges inside the budget, and random sites with their best charges. 10 000 of each per n at first order; 50 in total with full single points. | Neutral. | — |
| — | Negative spheres | Settled by the two-layer grid (Stage 5). The MILP gives each site one yes/no per admitted charge range. | As stated in Stage 5. | — |

---

## 3. The decisions

### Decision 1. Polarisation (b): in the score, or only in re-scoring

**The question in plain words.** A sphere's charge does two things to the substrate:
- It interacts with the substrate's charge as it is. That is a, the first-order term, linear in q.
- It pulls on the electron cloud, which responds. That is b q², the polarisation term, the same for +q and −q.

Two spheres also polarise jointly, which adds a cross term.

**What the library does.**
- **GOCAT never separates the terms.** Every fitness evaluation is a full QM/MM calculation, so polarisation is always in the score (Dittner's thesis pp. 47–50; Behrens' thesis §3.6.1).
  - Dittner uses a first-order potential estimate only inside one search step, never as the score (thesis p. 82).
  - The price is a full QM calculation per evaluation: about 4·10⁸ single points for one ten-charge database (thesis p. 157).
- **The catalytic-field papers use exactly our first-order score** as their working model (Sokalski 1985 eq. 19, p. 404; Szefczyk 2004 eq. 14, p. 16153; Beker & Sokalski 2020 eq. 2).
  - Sokalski's first-order model agrees with the ab initio values on the large effects (Table 2, p. 406; kcal/mol, ab initio against model d):
    - H₂O(A): −12.69 against −11.00;
    - OH⁻(A): −50.37 against −49.67;
    - H₂O(C′): 21.24 against 20.01.
  - It does less well on small ones: H₂O(B) is −0.59 against −2.20.
  - The higher-order terms are comparable in size but largely cancel (Sokalski Table 1, p. 401; Szefczyk pp. 16156 and 16159).
  - Beker et al. 2017 (Just Accepted copy, letter-numbered page G) find polarisation "quite significant" but cancelling or systematic.

**What our data say.**
- Stage 4c at def2-SVP: polarisation adds 10–31 % beyond the first-order prediction, with rank correlation 1.000 (plan update, Tier 2).
- That was measured on eight arrangements spread over about −23 to +23 kcal/mol. The plan itself warns that an optimiser's top ~10 will be closer together, and close designs can swap.
- The cross term reaches 1.124 kcal/mol at unit charges (HANDOFF §5 B5).

**The two options.**
- **(a) b in the score.** b is negative where polarisation adds to the effect, as in Stage 4c. A negative b q² term curves the score downwards in q, so it pushes charges to ±1 even harder, and the problem becomes non-convex: HiGHS, as used here, takes no quadratic objective at all. The cross terms would add a product for every pair of sites: millions of terms.
- **(b) Linear score, then re-score the pool.** Run full def2-SVP single points with the spheres at R and TS. These contain a, b and every cross term exactly at the frozen geometry.

**Recommendation: (b).** This is Jessica's leaning of 15 October and the plan's existing decision after Stage 4c.

**Why it is more likely to succeed.** It keeps the problem solvable, and re-scoring catches any reordering the extra terms cause. Decision 7 re-scores the best 20 of the pool for that reason, widened to 100 later if wanted.

**Direction.** Frozen magnitudes are 10–31 % too small before re-scoring. They are never quoted as results. On ranking there is no direction as measured, with the near-tie caveat above.

### Decision 2. Preorganisation: what stops a frozen design from falling apart when the substrate relaxes (CHANGE)

**The question in plain words.**
- The score holds the enzyme's substrate geometries fixed. In validation the spheres stay frozen but the substrate moves.
- A design that pulls hard on the substrate can move it away from the geometry the score assumed, and lose or reverse its effect.
- Our records show it:
  - one free sphere opened the forming C1–C6 bond from 3.16 to 4.27 Å;
  - a Phase 2b two-charge design opened it from 3.12 to 5.00 Å (plan update §4, item 5).

**What the committed plan says.** Plan update §4 item 5 judges that adding a reactant-gradient (preorganisation) term to the design objective is more likely to deliver catalytic designs than frozen-frame optimisation alone. It states that the optimiser stage "must include it". §5's optimiser row lists "a reactant-gradient term".

**What the library does.**
- **Dittner & Hartke 2018 and Dittner's thesis** use a quadratic penalty on gradient norms above 10 kcal mol⁻¹ Å⁻¹ at their reactant, TS and product frames (2018, manuscript p. 13; thesis pp. 86–88; weights in the ESI, thesis p. 303).
  - It is one of only two terms still active at their optimum (2018, manuscript pp. 13–14).
  - It suppresses designs whose large charges leave uncompensated gradients. Symmetric designs with large charges escape it (2018, manuscript p. 31).
- **Frozen-path designs relaxed afterwards** were often "overfitted": loose convergence, or a different reaction altogether (thesis ESI p. S63, printed p. 361; and p. 211).
- **Dittner & Hartke 2020** call the fixed path an "unrealistic assumption" that "allowed for only small catalytic effects" (abstract). Once the path relaxes inside each evaluation, they drop the gradient criteria: only the final barrier counts (p. 114106-6).
- **Behrens** shows that on a fixed path the gradient penalty is minimised by keeping charges away from the substrate (thesis p. 67). His threshold β ≈ 10 kcal mol⁻¹ Å⁻¹ is "somewhat arbitrarily chosen" (Eq. 3.2).

**Why the published form does not transfer as it is.**
- Dittner's frames are stationary points of his own reference path.
- Ours are enzyme geometries evaluated in vacuo, where the bare substrate already has a gradient. An absolute threshold therefore has no meaning for us.
- What carries over is the gradient the design **adds**: the design's gradient minus the bare substrate's at the same geometry, as an RMS value, the measure Behrens' fitness uses.

**Why it cannot go inside the MILP.**
- To first order the added force from a sphere is linear in q, so a linear cap is possible in principle.
- But it needs each site's unit-charge force on every substrate atom, including the electrons' response: one SCF with a gradient for each of 2769 sites × 30 frames × R and TS, about 166 000 calculations.
- The nuclear part alone is cheap, but it ignores electronic screening, which is large here.

**Recommendation (CHANGE: where the term sits, not whether there is one).**
- The reactant-gradient term enters the **design objective at the re-scoring step**, where it costs one gradient per design.
- The re-scoring single points are run as energy-plus-gradient calculations (ORCA EnGrad). The extra cost over an energy-only single point is to be measured with one test job before the cost is quoted.
- The re-scored ranking (decision 7) becomes: mean + λ × semi-deviation + κ × max(0, G_add,R − G₀)² summed over frames. This is Dittner's and Behrens' quadratic form above a threshold.
  - The TS gradient is recorded too; the plan names the reactant.
- **G₀ and κ come from Stage 6.** Stage 6 (planned before the optimiser stage) relaxes arrangements with the spheres frozen and compares frozen with relaxed effects. It should test whether G_add,R predicts the loss of effect.
  - Stage 6 is planned for 2–3 spheres. Applying its threshold to up to 20 spheres is an extrapolation. This draft suggests Stage 6 also relaxes a few development-set designs at larger n (for example n = 5, 10, 20), chosen and fixed in Stage 6's own pre-registration.
  - If Stage 6 can fix no threshold, G_add,R is reported for every design without a penalty, and this is stated as a limitation of the short list.
- **Inside the MILP**, strength is limited by the budget (decision 3).

**Why this is more likely to succeed than the alternatives.**
- A term inside the MILP is unaffordable, or else crude: the nuclear-only part.
- A term at re-scoring uses the real gradient of each design, and is calibrated by relaxations rather than guessed.
- It keeps the plan's judgement (a reactant-gradient term in the objective) while moving where it is applied.

**Direction.**
- Compared with the committed plan (a term inside the objective the MILP searches), the MILP's pool may contain stronger-pulling designs than it otherwise would: towards a lower frozen barrier at that step.
- The re-scoring term then penalises them: against a lower frozen barrier, and towards designs whose effect survives relaxation.
- Designs filtered out before re-scoring cannot come back. The pool per n (10 distinct designs) and the 20 re-scored limit this; re-scoring 20 rather than 100 narrows it further, which is stated with the short list.

### Decision 3. The budget: what stops every charge going to ±1

**The question in plain words.**
- With a linear score, the best charge at any site is always one of its limits. Halfway is never better than all the way.
- Without a further rule, every sphere takes a full charge, the search only chooses sites and signs, and "more charges, lower barrier" is built in (s14 docstring, and recorded in the Project notes).
- A budget limits the total. The choice is its form, then its size.

**What the library does.**
- **GOCAT has no budget.** It uses bounds per charge, a minimum distance, and usually neutrality (Dittner's thesis pp. 10 and 19; Behrens' thesis p. 4).
  - What holds their charges down is the penalties: the gradient penalty for asymmetric designs (2018, manuscript p. 31), and, for the uniform-field plates, gradient, reactant-destabilisation and frame-shift penalties together (thesis p. 202).
  - Their labelled charges stay well inside ±1 (section 1).
- **Dittner's thesis suggests penalty terms on charge values as future work**, to simplify needlessly complex designs, not for electronic validity (pp. 227–228; p. 166).
- **The catalytic-field papers have no budget** (section 1).
  - Beker & Sokalski 2020 call the catalytic field the solution of the inverse problem: the "complementary charge distribution of optimal molecular environment" (manuscript p. 7, PDF p. 8).
- **The field literature reports field strengths for uniform external fields on other systems,** none transferable to point charges around this dianion. Strong fields change the chemistry:
  - bond heterolysis and a switch to a stepwise mechanism (Shaik et al. 2016, pp. 1092 and 1095–1096);
  - loss of the product minimum (Dubey et al. 2020, p. 19).

**What our data say.**
- **Phase 2b** (bare point charges, earlier geometries; a reference only, since Phase 2 is redone) recorded two outcomes (`OPTIMISER_FORK_AND_WRITEUP_SCOPE.md` §2, items 3–4):
  - a linear objective drove charges to ±1 and the designs fragmented;
  - a convex quadratic penalty gave fractional charges, at most 0.06–0.29 e, that did not fragment.
- **Stage 4c:**
  - the most strongly polarising arrangement changed electronic state at def2-TZVPD;
  - net-negative arrangements raised the substrate's highest occupied orbital from the bare +2.33 eV to +4.6 to +6.5 eV;
  - net-positive ones lowered it (E1 −0.47, E8 −5.24 eV) (`cs_stage4c/exploratory/STAGE4C_EXPLORATORY_REPORT.txt`).
- The bare dianion is already unbound in vacuum: HOMO +0.082 Eh at def2-SVP (CHARGE_MODEL_DECISIONS).

**The three forms.**
- **(a) Total |q| budget, Σ|q_i| ≤ B.**
  - One budget row, plus one helper variable and two rows per site (s14 has it).
  - Its best designs sit at corners: a few charges at ±1, perhaps one partial charge, the rest at zero. This is the behaviour that fragmented in Phase 2b.
- **(b) Sum-of-squares budget, Σq_i² ≤ B.** B is in e². The charge-like quantity is √B, the length of the vector of charges.
  - This draft's observation: on a fixed set of sites, if no charge sits at a bound and the frame penalty is left out (λ = 0), the best charges are proportional to −a, and the best score is −√B × √(Σ a²).
    - Strong sites then get large charges and weak sites small ones, which is the magnitude pattern of Sokalski's unit-charge map.
    - Adding sites helps less and less.
  - On this grid many sites admit one sign only, or a minimum positive charge. Where −a has the wrong sign for a site, or the proportional charge is below the site's minimum, that site's charge sits at a bound instead. The frame penalty also shifts the charges. So the proportional pattern is the shape of the solution, not an exact rule.
  - HiGHS cannot take q² directly. It is replaced by 21 straight lines lying on or below the curve q² (tangents at q = −1.0, −0.9, …, +1.0), and the highest of them stands in for q².
    - Because the lines lie below the curve, the true Σq² of a design can exceed B by at most 0.0025 e² per sphere: 0.05 e² at n = 20.
    - The true Σq² is reported with every design.
- **(c) A cap on the field at each substrate atom.**
  - Linear, and the closest physical analogue of GOCAT's gradient limit.
  - But it needs 8640 dense rows over 2769 sites, about 24 million entries, and the library gives no basis for its size.
  - Instead, the field at each atom is reported for every re-scored design.

**Recommendation: (b), Σq² ≤ B.**

Writing a penalty on charge values as a budget is this draft's choice; Dittner proposes such penalties for a different purpose.

**How B is sized, without any designed barrier:**
1. **The two screens.** Use the two electronic screens the plan names (plan update, after Stage 4c), both measured against the bare substrate at the same geometry, basis and level:
   - the HOMO–LUMO gap;
   - the shift of the substrate's Hirshfeld charges.

   A third screen is possible if wanted, and would be this draft's addition: the shift of the HOMO. An absolute rule such as "HOMO below zero" cannot be used, because the bare substrate already fails it.
2. **Stress-test designs.** For each trial value of B, build designs that use the whole budget as close to the substrate as the grid allows. These are the hardest cases for electronic validity, and they are built without any reference to the barrier.
   - Random designs alone would mostly put charge far away and pass too easily.
   - The number of designs per B, the B values, the frames used and the pass rate are fixed in the pre-registration.
   - An estimate for the supervisor: 20 designs at each of 5 values of B, on 5 frames at R and TS, is 1000 single points, about 17 node-hours at Stage 4d's energy-only timing.
3. **The rule.** B is the largest value at which the stress-test designs pass both screens at the pre-registered rate.

**CHANGE in timing.** Steps 1–3 need the screens' thresholds before the optimiser runs. The plan fixes them later, in the validation pre-registration, which comes after the optimiser stage. This draft brings that part forward into the optimiser-stage pre-registration, written before any design is read. This is a change to the plan's order and needs sign-off.

**Why (b) is more likely to succeed.**
- (a) reproduces the behaviour that fragmented in Phase 2b.
- (b) reproduces the one that held.
- Tying B to the substrate staying electronically intact links the budget to a physical failure the validation screens look for.

**Direction.**
- A smaller B weakens designs: against a lower barrier.
- The criterion is independent of any barrier. Taking the largest B it allows is the most permissive choice: towards a lower barrier compared with any smaller B.
- Form (b) prefers many moderate charges to a few full ones: against a lower frozen barrier compared with an unbudgeted ±1 design.
- The straight-line stand-in loosens the budget slightly: towards a lower barrier, by at most 0.0025 e² per sphere.

### Decision 4. Total charge: neutral or free

**What the library does.**
- **GOCAT imposed neutrality to remove an artificial freedom in its database, not for the energy.**
  - Unconstrained runs gave strongly charged designs. Clustered by the potential at the atoms, those designs reduced to essentially one direction: a constant shift of the potential (2018, manuscript pp. 25–26; thesis ESI pp. 330–331).
  - Neutrality also screened out some extreme environments at the DFT level (thesis p. 162).
- **Scope.** Dittner's Diels–Alder runs "always enforced" neutrality (thesis p. 181), as did all three 2020 models. Other runs did not (thesis pp. 90, 148 and 159).
- **Behrens' molecular designs carried +2, +2, +1 and 0.** He notes, citing Dittner, that only differences of potential between atoms matter (thesis p. 82).
- **Sokalski found a charged OH⁻ shell far more catalytic than a neutral one** (1985, pp. 402–403).
- **Szefczyk's 13-residue chorismate-mutase model** (residues listed on p. 16153) counts to net +4.

**What our score already does.**
- A potential constant over the substrate adds the same amount at R and TS, because the substrate carries the same total charge (−2) at both. So it cancels from a.
- The constant-shift part of GOCAT's artificial freedom is therefore absent from our score.
- The general degeneracy is fully present: many charge patterns give nearly the same score. That is what decision 7's enumeration of distinct designs is for.

**What our data say.**
- Net-negative arrangements raise the substrate's highest occupied orbital; net-positive ones lower it (Stage 4c, decision 3).
- Forcing neutrality would make the optimiser place compensating anions wherever they cost least. They add negative potential around a dianion, which is the electronically risky direction.

**Recommendation.** Do not force neutrality (Jessica's leaning of 15 October). Report the net charge with every design. The electronic screens (decision 3) and the relaxation term (decision 2) cover what neutrality would otherwise have guarded.

**Direction.** Compared with neutrality, a free total admits more cations near O3: towards a lower barrier. This is stated with the results.

### Decision 5. Combining frames

**What the library does.**
- **For estimating a barrier from snapshots,** the exponential average is preferred but badly conditioned once the spread exceeds about 7 kJ/mol (Ryde 2017, abstract and Table 2). The minimum is not robust (Ryde p. 7; Cooper & Kästner p. 4).
- **For comparing alternatives, the arithmetic mean gives the most stable results,** though the absolute barriers are inaccurate (Ryde p. 7 and Fig. 5).
- **No paper in the library uses a spread penalty in a design score.** GOCAT uses one path per design; a frame-wise GOCAT is only proposed (Dittner's thesis p. 230).
- **Two reviews favour narrow distributions,** qualitatively:
  - Hennefarth & Alexandrova 2022 (author manuscript, concluding paragraph);
  - Fried & Boxer 2017, p. 13.21.

**What our records fix.**
- SP Amendment 2 A2.3 defines the Phase 1 barrier as the arithmetic mean of B_sp over the complete frames.
- It compares ensembles, including the enzyme against a design, by the difference of means with its 95 % confidence interval.

**Recommendation.** The score of a design is

  **mean over frames of ΔΔE_f + λ × semi-deviation**

where:
- **ΔΔE_f = Σ_i (a_if q_i + L_if z_i)** is the frame's frozen score.
- **The semi-deviation** is (1/F) Σ_f max(0, ΔΔE_f − mean): the average amount by which frames come out above (worse than) the mean. It never penalises a design for being better on some frames (s14 docstring).
- **λ is not tuned. It is tied to the 95 % confidence interval** (this draft's derivation):
  - for normally spread values, the semi-deviation is σ/√(2π) ≈ 0.399 σ;
  - the 95 % CI half-width of a mean over F frames is t(0.975, F−1) × σ/√F;
  - so λ = t(0.975, F−1) / (0.399 √F) makes the score approximately the least favourable end of the design's 95 % CI;
  - λ = 0.94 at F = 30, 1.03 at F = 25, 1.17 at F = 20. It is computed from the package's final F.
  - The normal assumption only sets the size of λ, and need not hold exactly. A2.3's cumulant estimate is different: it needs positive evidence of normality before use.
- **Frames:** every complete package frame, weighted equally. Cooper & Kästner's "well-chosen snapshots" is advice for estimating a free energy, not for designing against an ensemble.

**Why this is more likely to succeed.**
- The mean is what the comparison with the enzyme uses, and the most stable statistic for ranking.
- The penalty makes the optimiser seek what validation tests: an effect that is reliably negative across frames.

**Direction.** Neutral to conservative: the penalty only adds.

### Decision 6. Number of spheres n, and when to stop

**What the library does.**
- **Behrens: trial and error** is the only way (thesis pp. 51 and 62).
  - Fewer than 12 charges could not reproduce his 81-charge design (p. 54).
  - At 30 charges they cancelled one another again (p. 57).
- **Dittner: a plateau.** The best score drops, then levels off. Beyond that, more charges give only more intricate surroundings (thesis pp. 192–193 and p. 224).
- **Neither gives a stopping rule.**

**What our records fix.**
- Jessica intends to test n from 3 to about 20 for this system herself (her stated intention, Project notes).
- With a budget, gains should shrink as n grows.
- The best score at n cannot be worse than at n − 1, except through the extra sphere's L term: a design at n can repeat the n − 1 design and add one sphere with q = 0 where L is about zero.

**Recommendation.** Solve n = 3, 4, 5, … in turn. Stop at the first n whose best design does not beat the best at n − 1 by more than both of these:
- **(i) The frame spread.** The half-width of the paired 95 % interval of the per-frame differences. Paired, because both designs are scored on the same frames.
  - Both designs were chosen as the best on those same frames, so the difference is biased in their favour and the interval is descriptive, not a true 95 % test. This is stated.
- **(ii) The method and basis uncertainty, as a fraction of the score.**
  - The records give about 12 % against MP2 (Stage 4e) and up to 23 % or 3.2 kcal/mol per arrangement across bases (Stage 4c, plan update).
  - The fraction to use (for example 15 %) is fixed in the pre-registration.

Every n before the stopping point goes forward. The time each solve takes is to be measured on the development set, not assumed.

**Empty or neutral spheres.**
- n counts spheres, whatever their charge.
- A sphere may carry q = 0 where its site admits it (the anion/neutral layer). It then acts only through L.
- Behrens' dispersion-only entities show such spheres can matter (thesis pp. 38 and 49).
- The number of neutral spheres is reported.

**Direction.** Neutral.

### Decision 7. The pool, re-scoring and the short list

**What the library does.**
- **Dittner** clustered thousands of designs by their potential at the atoms. He took the best of each cluster and the one nearest its centre forward (2018, manuscript pp. 11 and 18; thesis p. 159).
- **Behrens** filtered 3000 candidates to 37 and found four kinds of solution; one failed at the higher level (thesis pp. 79 and 82).

**Our problem.**
- The frames agree on a favourable region of about 20 sites beside O3 but cannot order the sites within it (HANDOFF §5).
- On a 0.5 Å grid, s14's exclusion of the exact previous set of sites would return the same design shifted by 0.5 Å, again and again.

**Recommendation.**
1. **Distinct designs per n.** After each design is found, add a rule for each earlier design: the new design must place at least one sphere more than 1.5 Å from every sphere of that earlier design. In MILP form, the spheres within 1.5 Å of that design's spheres number at most n − 1.
   - Why the radius is 1.5 Å: it is less than half the 3.25 Å spacing. So no new sphere can be within 1.5 Å of two earlier spheres, and no 1.5 Å neighbourhood can hold two new spheres. The rule therefore forbids exactly the "shifted copies" of each earlier design: designs in which every sphere sits within 1.5 Å of a different sphere of that design.
   - What it allows: with several earlier designs, a new design can still copy most of one earlier design and most of another. Up to n − 1 spheres may be near-copies.
   - "Within 1.5 Å" includes exactly 1.5 Å.
   - The rule ignores charges: designs on the same sites with different charges count as the same.
   - This is a variant, by this draft, of the standard no-good cut (Balas & Jeroslow 1972).
   - Take the 10 best distinct designs per n carried forward.
2. **Re-scoring.**
   - Take the **20** best of the pool by frozen score (Jessica, 20 October). Re-score each on every frame, at R and TS, with full def2-SVP single points with the spheres.
   - Run them as energy-plus-gradient calculations for decision 2.
   - At 30 frames that is about 1200 calculations: about 20 node-hours at Stage 4d's energy-only timing (54–61 s per sphere single point on 8 cores), plus the gradient overhead, to be measured.
   - **Widening later.** 100 would be about 6000 calculations and about 100 node-hours. The pool is kept, so the extra 80 can be re-scored later without redoing anything. Whether 20 was enough is checked by how much the re-scored ranking differs from the frozen one over those 20: if re-scoring reorders them substantially, the window is widened before the short list is fixed.
   - Rank by the re-scored objective of decision 2, which is decision 5's score plus the relaxation term.
3. **The short list.** The committed records say validation takes the top ~10 per charge count (`OPTIMISER_FORK_AND_WRITEUP_SCOPE.md` §1 and §3 step 3). That coverage is part of what replaced the optimality certificate.
   - **Chosen (Jessica, 20 October): the top ~10 overall, plus the best of each carried-forward n.** About 10 to 28 designs.
   - The records' wider reading (the top ~10 per carried-forward n, up to 180 designs) is not taken. The difference is recorded here because that coverage was part of what replaced the optimality certificate: the short list is narrower than the records envisaged, and every n still contributes its best design.
   - The cost per design depends on the validation medium, which is decided in Phase 2.2 (A2.5).

**Direction.** Neutral. Re-scoring can move designs either way.

### Decision 8. What "optimal" means

**What the library does.**
- GOCAT never claims a global optimum (Dittner's thesis pp. 23, 74, 224 and 230; Behrens' thesis p. 15). Behrens notes that exact methods are taken to work only for small systems (p. 15).
- Dittner reports several near-equal "global optima" on his fitness surface (thesis p. 154).

**What our records fix.**
- On 2 September Jessica dropped the optimality certificate as a thesis claim (`OPTIMISER_FORK_AND_WRITEUP_SCOPE.md` §1).
- s14's docstring calls its result "certified" but already carries the right caveat: a certified optimum of the surrogate, "NOT a certified optimal catalyst".

**Recommendation.**
- Follow the fork. Each solve reports its gap as a property of that solve: "the best design for this score and these rules, gap X".
- The word "certified" is not carried into the new code or the write-up as a claim, and "optimal catalyst" is never used.

**Direction.** None.

### Decision 9. Path validity

**What the library does.**
- Dittner showed that scoring two or three frames on a frozen path can give misleading zero or negative barriers, because the highest point can move to another frame. His frozen scores therefore used the whole path (thesis pp. 90–91).
- His relaxed version drops strict unimodality and relaxes the path instead (2020, p. 114106-6).

**What our records fix.** SP Amendment 2 A2.5 says every barrier compared with the enzyme's comes from the same relaxed chain:
- a TS with one imaginary mode;
- an IRC whose ends are the reactant and product of the same reaction;
- B = E(TS) − E(R_IRC).

Frozen-field scores "stay screening numbers". Path validity is therefore tested in validation, on the relaxed path, which is where Dittner's later work also moved it.

**Recommendation.**
- No path constraints in the MILP. They would need potentials at every IRC image of every frame (new compute) to police a frozen path that validation replaces.
- Report the electrostatic part of each design's frozen change in reaction energy, Σ q (V_P − V_R), from the product-side potentials Stage 5 keeps (AP). Stage 5 produces no Lennard-Jones term at P, so this is not the full reaction-energy change.

**Direction.** Neutral for the optimiser.

### Decision 10. The null distribution

**What the library does.**
- In Dittner's benchmark, runs started from random designs only did far worse (thesis Table 6.1, p. 151).
- At the DFT level, none of 1000 random designs was catalytic, against 3–80 % of designs carried over from the PM7 optimisation (Table 6.2, p. 164).
- Uniform-field plates served as a further baseline (pp. 201–203).

**What our records fix.** Random arrangements under the same grid, charge bounds, spacing and budget: many at first order, a subset with full single points. Every design is reported with its place in that distribution. The numbers drawn are fixed in the optimiser-stage pre-registration (plan update, Stage 4d section).

**Recommendation.** Two kinds of random design per n, under the same n, admitted charges, spacing and budget.

**(i) Random sites and random charges.**
- Sites are added at random, respecting the spacing.
- Each sphere gets a random admitted range.
- The vector of charges is drawn uniformly inside the budget, then each charge is moved to the nearest value its range admits.
- A design is redrawn only if that pushes Σq² above B; the acceptance rate is reported.
- Sites whose minimum charge alone exceeds the remaining budget are skipped.
- The exact sampling rule is a pre-registered choice. It shapes the distribution, so it is stated.
- Drawing charges uniformly over their full ranges and rejecting those over budget would almost never be accepted at 20 spheres.

**(ii) Random sites with their best charges.**
- The optimiser chooses only the charges on random sites, which tests whether choosing the sites matters.
- When no bound is active this has a direct formula (decision 3). Otherwise it is a small problem of its own: about 180 000 small solves in all.

**Numbers.**
- 10 000 of each kind per n at first order.
- 50 in total, spread over n, re-scored with full single points.

Each design's percentile in (i) and (ii) is reported.

**Direction.** Neutral.

---

## 4. The MILP for the two-layer grid

This section translates the decisions into the solver's terms, for the new optimiser code. s14 is the reference. The new code adds L, the two charge ranges per site, the spacing as cliques, the Σq² budget, and distinct-design enumeration.

**Sites and their admitted charges** (development counts from `dev_sites_a2.tsv`, after Stage 5 Amendment 2):

| Site class | Admitted charges | Yes/no choices |
|---|---|---|
| anion/neutral layer, positive from 0 (1274) | one interval, [−1, +1] | 1 |
| anion/neutral layer, positive from p = 0.50–1.00 (50) | [−1, 0] or [p, +1] | 2 |
| anion/neutral layer, no positive (217, beside H8) | [−1, 0] | 1 |
| cation layer beside H8 (277; Stage 5 Amendment 2: positive only) | +1 | 1 |
| cation layer, positive only (951, at the oxygens) | [p, +1], p = 0.25–1.00 | 1 |

That gives 2819 yes/no variables on the development grid (`exploratory/dev_sites_a2.tsv`). Before Stage 5 Amendment 2 (20 October 2026), the 277 cation-layer sites beside H8 also admitted [−1, 0], which gave 3096.

**Variables, per site i:**
- **y_i,r:** one yes/no for each admitted range r. At most one may be "yes".
- **q_i,r:** the charge in that range, with lo_r·y_i,r ≤ q_i,r ≤ hi_r·y_i,r. It is forced to 0 when y_i,r = 0. For a positive range, lo is p_i.
- **z_i = Σ_r y_i,r** (is there a sphere) and **q_i = Σ_r q_i,r** (its charge).
- **s_i ≥ 0:** the stand-in for q_i², kept at or above the 21 lines s_i ≥ 2c·q_i − c² for c = −1.0, −0.9, …, +1.0.

**Variables, per frame f:**
- **d_f = Σ_i a_if q_i + Σ_i L_if z_i:** the frame's frozen score.
- **d̄ = (1/F) Σ_f d_f:** the mean.
- **u_f ≥ d_f − d̄, u_f ≥ 0:** how far frame f comes out above the mean.

**Objective, minimised:** d̄ + (λ/F) Σ_f u_f.

**Rules:**
- **Number of spheres:** Σ_i z_i = n.
- **Budget:** Σ_i s_i ≤ B.
- **Spacing.**
  - On the development grid, 266 037 pairs of sites lie closer than 3.25 Å. Each site has a median of 193 such neighbours.
  - One rule per pair (z_i + z_j ≤ 1) is valid but weak. Instead, the pairs are grouped into **cliques**: sets of sites all within 3.25 Å of one another, so at most one of them can hold a sphere. Then Σ_{i∈K} z_i ≤ 1 for each clique K.
  - The cliques are built greedily:
    1. Take the close pairs in site order.
    2. For each pair not yet covered, start a clique from it.
    3. Repeatedly add the common neighbour that has the most neighbours among the remaining candidates (ties by site number).
  - On the development grid this gives 6916 cliques (mean size 53.6, about 371 000 entries) covering every close pair. The 266 037 pairwise rules would have 532 074 entries. Other greedy variants give different counts; an independent run gave 4305.
  - The cliques forbid exactly the designs the pairwise rules forbid. But the solver's relaxed versions come much closer to the real answer, so it finishes faster.
- **Distinct designs (decision 7):** one rule per earlier design.

**Solver.** HiGHS through scipy.optimize.milp, as in s14 and Phase 2b's solver choice. Every solve records its time limit, gap and status. The input files' sha256 are checked before solving.

**What is tested on the development set.**
- **Code checks.** s14's self-tests, extended:
  - a one-sphere case with a closed-form answer;
  - the spacing, range and budget rules never violated;
  - the stand-in for q² within its 0.0025 e² bound;
  - with λ = 0 and no bound active, charges proportional to −a on a fixed set of sites;
  - with bounds active, the optimality conditions checked directly.
- **Time and gap** for n up to 20.

**What is not done.** No setting (B, λ, n range, pool size, number of tangent lines) is chosen by the barriers its designs reach on the development set:
- B comes from the electronic-screen calibration;
- λ comes from the confidence interval;
- the rest are fixed above.

---

## 5. Order of work

1. **Jessica decides** on each row of section 2, including the two changes.
2. **The code.** The optimiser code is written and tested on the development set, and delivered as a bundle with its tests. Nothing it produces there is a result.
3. **Stage 6**, already planned before the optimiser stage. It relaxes arrangements and measures frozen against relaxed. It also tests the relaxation term of decision 2, with the larger-n designs suggested there.
4. **The optimiser-stage pre-registration**, written before any design is read. It fixes:
   - every value above: λ from F, the stopping fractions, pool sizes, sampling rules and null sample sizes;
   - G₀ and κ from Stage 6;
   - the electronic screens' thresholds, brought forward (decision 3);
   - the B-calibration procedure;
   - the code's sha256.
5. **The calibration of B,** by the pre-registered procedure. B is recorded before any optimised design is read.
6. **Production,** on the Stage 5 production inputs once the SP package is FINAL.

## 6. Papers this draft relies on that are not in the library

These are optimisation-method references, needed only to cite the method choices; no decision above rests on reading them. The DOIs are from the publishers' pages; please confirm them on download.

| Paper | Used for | DOI |
|---|---|---|
| Konno & Yamazaki 1991, Management Science 37, 519–531 | Deviation measures written as linear programs; s14 cites it | 10.1287/mnsc.37.5.519 |
| Ogryczak & Ruszczyński 1999, European Journal of Operational Research 116, 33–50 | The semi-deviation as a risk measure (decision 5) | 10.1016/S0377-2217(98)00167-2 |
| Huangfu & Hall 2018, Mathematical Programming Computation 10, 119–142 | HiGHS, the solver | 10.1007/s12532-017-0130-5 |
| Balas & Jeroslow 1972, SIAM Journal on Applied Mathematics, "Canonical cuts on the unit hypercube" | No-good cuts (decision 7) | 10.1137/0123007 |
