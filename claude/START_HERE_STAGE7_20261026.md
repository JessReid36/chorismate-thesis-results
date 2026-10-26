# START HERE — Phase 2.2, Stage 7

Second version, 26 October 2026. The first was corrected after the session given it found an error in it; what
the error was is in §7, because that matters more than the correction.

---

## 0. First: can you read the repository?

Everything below requires reading files under `~/Desktop/chorismate-thesis-results` and
`~/Desktop/chorismate-thesis-code` on Jessica's computer. A fresh session has no access to them by default.

**If you cannot list those directories, stop and say so.** Ask Jessica to either link the desktop app to this
chat, or attach the folder. Then begin.

**Do not proceed on this file, the handover, or any `*_RESULT.txt` alone.** They are summaries. A session that
works from them without the outputs will reproduce whatever error they contain, and §7 is a list of the errors
they have contained so far.

---

## 1. The task

**Write Stage 7 of the Phase 2.2 charge design.** That is the work.

What Stage 7 must settle, and the state of each:

| | |
|---|---|
| **The per-site charge cap** | Must be stated as a **magnitude AND a distance**. The withdrawn `q_quad = 0.80 e` conflated them: at 2.96 Å a single +0.80 e collapses the density, but at 1.5 Å and 2.0 Å a single charge collapses it too. Largest CLEAN single charge at 2.96 Å is **+0.65 e**, which is an upper bound, not a measured cap — nothing was run between 0.65 and 0.80. |
| **The total-charge budget** | **OPEN. Do not set it. See §2** — B has never been calibrated, and the pocket figure the first version rested on is contradicted by the committed measurement. |
| **Σq² ≤ 2.00** | Keep as the **shaping** constraint only — it stops the optimiser concentrating charge on one site. Do not present it as the budget. Record the reason: Σq² is not invariant to how finely a charged group is discretised and Σ\|q\| is. |
| **No 3.0 Å clearance floor** | A standing instruction. Real enzyme residues do not sit at a fixed distance, and adopting 3.0 Å because other papers use it was explicitly rejected. |
| **The λ ≤ 0.50 domain** | Either **tested on a second design** or declared untested on the face of the document. It was measured on S6-20 only, one frame, fixed geometry. |
| **The uncertainties** | The 11% basis and 19–25% environment sensitivities carried explicitly. |

It is pre-registered work: write it, commit it **before** anything runs against it, and never edit it afterwards
— changes go in a dated amendment or erratum.

---

## 2. The budget is an open decision for Jessica. Do not pre-register a number.

The first version of this file told Stage 7 to use **Σ\|q\| ≤ 6.0 e**. That was wrong in three separate ways,
and all three must be understood before the budget is touched.

**(a) It inverts the measurement.** The defensible domain is **Σ\|q\| ≤ 2.880 e** — inside it the two bases agree
to 0.9757 kcal/mol and every run is CLEAN; above it runs are STRAINED and COLLAPSED. A budget of 6.0 e would
authorise the optimiser to spend charge precisely where the model is known to fail.

**(b) The figure has no committed source, and the committed measurement says something else.** The 6.0 e came
from Claude's reasoning in conversation on 23 October — before Diagnostics 4, 5 and 6 existed — on the basis
that the pocket has "six charged residues at ±1". That basis was a conflation. **Six** is the number of
*literature-ranked catalytic* residues drawn in the site-effect map, which is a ranking, not a charge budget.
What the repository actually measures is in `phase2_charge_design/08_validate/step_6_4_overlay_result.txt`:

> Active site within 12 A of substrate resid 383: **12 charged residues, 6 cationic / 5 anionic, net +1.**
> Inner shell (<=4.5 A): Arg217, Arg63, Arg134 (cations) + Glu205 (anion) — cation-dominated.

So the pocket carries **twelve** charged residues at 12 Å with a **net of +1**, and **four** within 4.5 Å. Three
things follow. The 6.0 e figure is not the pocket's charge by any reading. The *net* charge is +1, not 6, so a
Σ\|q\| budget and a net-charge constraint are different quantities and must not be conflated. And that file
carries two caveats of its own on its face: the geometry is a **placeholder** ("distances shift on real TS"),
and its arithmetic does not close — 6 cationic + 5 anionic is 11, not the 12 it reports. **Resolve that
inconsistency before using any count from it.**

("30 to 35 mutually separated sites" is likewise absent from every committed file. Re-derive it from
`cs_stage6/sites_f42436.tsv` and `r_min = 3.25 Å` if it is needed.)

**(c) It changes a pre-registered form, not just a number.** `OPTIMISER_DECISIONS_20261020.md` **decision 3**
fixes the budget as **Σq² ≤ B**, having considered and *not* chosen Σ\|q\| ≤ B — that is option (a) in its
decision 3, which `s14_design_milp.py` implements and `cs_opt_milp.py` does not. Switching to Σ\|q\| is a change
of form and needs a dated amendment to that file, with its literature basis, **and** a code change.

### And the part the question uncovered

**B has never been calibrated, and the procedure that was supposed to calibrate it has not been run.**

- `OPTIMISER_DECISIONS_20261020.md` decision 3: "B is set by the plan's two electronic screens on stress-test designs, before any optimised design is read", scheduled to **"Stage 6, calibration"**. The same file carries a section on "The calibration of B, by the pre-registered procedure".
- `relax/ARRANGEMENTS.txt` SETTINGS: `B = 2.00 e^2 (the code default, NOT the calibrated B)`.
- `STAGE6_CRITERIA.txt`: B = 2.00 "is a code-test value and not the calibrated B".
- But Stage 6 as pre-registered produces **G0 and κ** — the preorganisation threshold and weight — **not B**. The calibration decision 3 scheduled for Stage 6 was never written into Stage 6.

So the budget in every committed Stage 6 design is a code default, and has been throughout. **Read decision 3
and its calibration section in full before doing anything with B.**

And the collapse finding bears directly on that procedure: the electronic screens run on *stress-test* designs,
and if those carry charge like the six committed designs did, the screens would themselves run in the collapsed
regime. **The pre-registered B-calibration route may need re-reading against Diagnostic 6 before it is run.**

### The three options, and a recommendation

1. **Pause the budget.** Stage 7 states the measured validity domain, records that B is uncalibrated and that the pre-registered calibration route must be re-read against D6, and leaves the budget to a dated amendment once that is done.
2. **Calibrate B now** by decision 3's procedure, re-read against D6 first.
3. **Change the form to Σ\|q\|** by dated amendment to OPTIMISER_DECISIONS, with the literature basis and the code change.

**Recommended: (1).** It is the only one that does not require a decision Stage 7 is not yet entitled to make,
and it leaves both others open. (3) is the largest change and the least supported — the catalytic-field papers
and GOCAT impose no budget at all (decision 3 §1 and Dittner's thesis pp. 10, 19), so there is no literature
pressure toward Σ\|q\| specifically.

**This is Jessica's decision, not yours. Put the three options to her with your own reading and wait.**

---

## 3. What is NOT the task

**The ~90 SP-package jobs on hpc1 are Phase 1 and are not your task.** They are live, and they are context only.

Two things only:

1. **Watch `419762 sa200008ts`.** At the 26 October snapshot it had used 133 of its 176 h walltime. If it is killed, the five jobs held behind it never start — PBS `afterok` requires exit 0. Check with a plain `qstat -u 18660916` and report. Do nothing further.
2. **If a frame's package completes**, say so and stop. The procedure is pre-registered in `05_qmmm/24_sp_barriers/SP_PLAN.txt` and its amendments and must be read in full first.

Details in `claude/HANDOVER_20261026.md` §4. That handover leads with the SP package, and a session given it
alone anchored on Phase 1 frames instead of the charge design. **That was a sequencing fault in the handover,
not a change of priority.**

---

## 4. Read this before writing anything

In this order. **In full. Do not skim.** The largest failure in this project was six diagnostics reading
energies only while the SCF cycle count and the HOMO–LUMO gap sat unread in the same output files for weeks.

**(a) Context, once:** `claude/HANDOVER_20261026.md`. A map, not evidence.

**(b) The pre-registrations, in full, in order.** These bind Stage 7 and are never edited:

```
phase2.2/PHASE22_PLAN.txt                       and PHASE22_PLAN_UPDATE_20261009.md
phase2.2/OPTIMISER_DECISIONS_20261020.md        <- decision 3 and the B calibration: read first, see section 2
phase2.2/CHARGE_MODEL_DECISIONS.md
phase2.2/STAGE6_DECISIONS_20261021.md
phase2.2/LIBRARY_ERRATUM1_20261020.md           LIBRARY_ERRATUM2_20261021.md
phase2.2/cs_stage5/STAGE5_CRITERIA.txt
phase2.2/cs_stage6/STAGE6_CRITERIA.txt          STAGE6_AMENDMENT1.txt
                                                STAGE6_ERRATUM1.txt  STAGE6_ERRATUM2.txt
                                                STAGE6_ERRATUM3_20261026.txt
phase2.2/cs_stage6/STAGE6_DIAGNOSTIC1_20261022.txt
                   STAGE6_DIAGNOSTIC2_20261022.txt  STAGE6_DIAGNOSTIC2_AMENDMENT1_20261022.txt
                   STAGE6_DIAGNOSTIC3_20261022.txt  STAGE6_DIAGNOSTIC3_NOTE1_20261022.txt
                   STAGE6_DIAGNOSTIC4_20261023.txt
                   STAGE6_DIAGNOSTIC5_20261026.txt  STAGE6_DIAGNOSTIC6_20261026.txt
phase2.2/cs_stage6/STAGE6_ASSESSMENT_20261022.md    STAGE6_FINDINGS_20261022.md
```

**(c) The outputs — §5. Re-derive; do not read the reports and move on.**

**(d) The literature.** `chorismate-refs/` holds 77 papers. In full before using them:

- `acs.jctc.9b01162.pdf` — Marefat Khah et al., JCTC 2020. The electron spill-out paper the whole Stage 6 finding rests on. Read it yourself; do not take any paraphrase, including this file's.
- `1.3484283.pdf` — Rappoport & Furche, JCP 133, 134105. def2-SVPD, "property-optimized"; the p. 9 caveat about "(small) anions" matters here.
- the chorismate-mutase mechanism and barrier papers, for what a defensible barrier reduction looks like.

**A claim from a paper must come from the full paper in `chorismate-refs/`** — not an abstract, not a search
result, not memory. If a paper is missing, give its checked DOI and **wait** until it is committed. One paper is
not a standard; three or more independent sources are.

**(e) The last two months of history**, for how this state was arrived at. 165 commits in results, 79 in code:

```
git -C ~/Desktop/chorismate-thesis-results log --since=2026-08-26 --date=short \
    --format='%ad %h %s' -- phase2.2 | tac
git -C ~/Desktop/chorismate-thesis-code    log --since=2026-08-26 --date=short \
    --format='%ad %h %s' | tac
```

The commit messages are long on purpose: they carry the reasoning, the rejected alternatives and the literature
basis. Read them, not just the diffs. The Phase 2.2 lineage in that window: `cs_stage4` → `4b` → `4c` → `4d` →
`4e` → `cs_stage5` → `cs_stage6`, plus `s11_probe_scan`, `s13_lj_test`, `s15_dv2`, `wp1_lj_combining`,
`wp4_s13_rerun`, `wp5_rigid_scan`.

---

## 5. Reference the outputs, not the reports

**Every `*_RESULT.txt`, every `*_REPORT.txt`, the assessment and this file are interpretations, and
interpretations in this project have been wrong repeatedly** — see §7.

**Re-derive before citing.** Both analysis scripts are read-only and take seconds:

```
python3 ~/Desktop/chorismate-thesis-code/phase2.2/cs6_audit.py  ~/Desktop/chorismate-thesis-results /tmp/d6check
python3 ~/Desktop/chorismate-thesis-code/phase2.2/cs6_decomp.py ~/Desktop/chorismate-thesis-results /tmp/d5check
```

Confirm they reproduce `cs_stage6/DIAGNOSTIC6_RESULT.txt` and `cs_stage6/field/DIAGNOSTIC5_RESULT.txt`. **If they
do not, that is the finding and Stage 7 waits.**

**Open the `job.out` files yourself** for the runs the errata name, and read the cycle count, the gap, the dipole
and the Loewdin charges with your own eyes. Each archive has a `*.MANIFEST.sha256` beside it; check members
against it.

```
phase2.2/cs_stage6/frozen/sp_outputs.tar.xz               S6-C/P/2/3/5/10/20, R and TS, def2-SVP
phase2.2/cs_stage6/field/outputs/field_outputs.tar.xz     the 16 lambda-scan points
phase2.2/cs_stage6/qrefine/outputs/qrefine_outputs.tar.xz qp0650, qp0800 - the q_quad withdrawal
phase2.2/cs_stage6/qscan/outputs/qscan_outputs.tar.xz     93 runs, C1-C5
phase2.2/cs_stage6/pauli/outputs/pauli_outputs.tar.xz     M2 Na+, M3 K+ - the Diagnostic 3 withdrawal
phase2.2/cs_stage6/a_matrix_outputs.tar.xz                the A matrix's finite differences
phase2.2/cs_stage6/diffuse/outputs/diff_outputs.tar.xz    Diagnostic 1
```

### Which committed file supplies each figure

Verify each against the file before using it. Paths are under `phase2.2/` unless shown otherwise.

| figure | committed source |
|---|---|
| `q_quad = 0.80 e` (**withdrawn**) | `cs_stage6/qrefine/DIAGNOSTIC2_AMENDMENT1_RESULT.txt`; withdrawn by `cs_stage6/STAGE6_ERRATUM3_20261026.txt` E3.1 |
| `b = −1.532 kcal/mol per e²` (stands) | same file; derived at q = ±0.50, both CLEAN |
| `+0.65 e` largest CLEAN single charge at 2.96 Å | `cs_stage6/DIAGNOSTIC6_RESULT.txt` (`qp0650` absent from its not-clean list); raw gap 1.535 eV in `qrefine/outputs/qrefine_outputs.tar.xz` |
| `2.96 Å` site 1690 to O3 (R) | `cs_stage6/relax/ARRANGEMENTS.txt` — "R: closest sphere-to-substrate 2.9596 A (to O3)" |
| collapse at 1.5 Å and 2.0 Å, one charge, def2-SVPD | `cs_stage6/DIAGNOSTIC6_RESULT.txt`, the `06b_inner_shell` rows |
| `Σ\|q\| = 2.880 e`, largest single charge `0.275 e` at λ = 0.50 | `cs_stage6/field/FIELD_PLAN.tsv`; `cs_stage6/field/DIAGNOSTIC5_RESULT.txt` |
| `ddE = −10.657 / −11.633 kcal/mol` | `cs_stage6/field/DIAGNOSTIC5_RESULT.txt` and `field/DIAGNOSTIC4_RESULT.txt` tables |
| `\|Δ\| = 0.9757 kcal/mol` | `cs_stage6/field/DIAGNOSTIC5_RESULT.txt` D5.3(d) |
| 11% basis sensitivity | `cs_stage6/STAGE6_ASSESSMENT_20261022.md`; `cs_stage6/STAGE6_FINDINGS_20261022.md` |
| 19–25% environment sensitivity | same two files |
| `B = 2.00 e²`, "the code default, NOT the calibrated B" | `cs_stage6/relax/ARRANGEMENTS.txt` SETTINGS; `cs_stage6/STAGE6_CRITERIA.txt` ("a code-test value and not the calibrated B") |
| `r_min = 3.25 Å`, `λ = 0.94` | `cs_stage6/relax/ARRANGEMENTS.txt` SETTINGS |
| Σq² ≤ B as the pre-registered budget **form** | `OPTIMISER_DECISIONS_20261020.md` decision 3 |
| B from "two electronic screens on stress-test designs" | `OPTIMISER_DECISIONS_20261020.md` decision 3 and its B-calibration section |
| the four D6 verdicts and their thresholds | `cs_stage6/STAGE6_DIAGNOSTIC6_20261026.txt` D6.3 |
| the pocket's charged residues | `phase2_charge_design/08_validate/step_6_4_overlay_result.txt` — **12 charged residues, 6 cationic / 5 anionic, net +1** within 12 Å; **4** within 4.5 Å. Carries a placeholder-geometry caveat, and its 6 + 5 does not sum to 12 |
| **`Σ\|q\| ≤ 6.0 e` / "six charged residues at ±1"** | **NO COMMITTED SOURCE, AND CONTRADICTED.** Claude's reasoning in conversation, 23 Oct 2026, conflating the six *literature-ranked* residues of the site-effect map with a charge budget. See §2 |
| `cs_opt_milp.py` has no `l1_budget` (`grep -c` 0 against 8 in `s14`) | `cs_stage6/STAGE6_ASSESSMENT_20261022.md` |
| **"30 to 35 mutually separated sites"** | **NO COMMITTED SOURCE.** Same origin. Re-derive from `cs_stage6/sites_f42436.tsv` and `r_min = 3.25 Å` if it is needed. |

**Never state a figure that is not in a committed file. If you cannot find it, say you cannot find it.**

---

## 6. Open questions — do not assume answers

- **B has never been calibrated** and the pre-registered route may need re-reading against D6. §2.
- **`phase2b_charge_design/06_charge_tests` has 764 committed entries and no output archive of its own.** Its point-charge files are named `pc_most_stabilising_q025_p.pc`, `q050`, `_m`/`_p` — single site, q ≤ 0.50, consistent with the representation having been validated below its collapse threshold. **Whether its ORCA outputs are committed anywhere, and so whether Diagnostic 6 covered them, is NOT established.** Find out before citing that folder.
- **Diagnostic 6 filters to 118 electrons**, so the Na⁺ (128 e) and K⁺ (136 e) runs behind the Diagnostic 3 withdrawal were never classified by it. Those figures are hand-read. Extending the audit is an open item.
- **Does the λ ≤ 0.50 domain transfer to a second design?** Untested. Scaling S6-10 as Diagnostic 4 scaled S6-20 is 16 single points in one restartable job.
- **The 9 SP frames absent from the queue** — finished or never submitted, from hpc1, not by inference. Context only.
- **The three climbing-image folders** `f{20000,44388,59999}_r8_ci_a1` — purpose not established here.

---

## 7. Why this file is on its second version

The first version was given to a session which, lacking repository access, read it and asked three questions
rather than proceeding. All three were well-founded:

1. whether the budget inversion was intended, and whether `OPTIMISER_DECISIONS` needs a dated amendment;
2. whether Σ\|q\| ≤ 6.0 and Σq² ≤ 2.00 were both meant to stand;
3. which committed file supplies each figure.

The answers are §2 and §5. **It found an error that the author of the brief had not seen**: a budget more than
twice the measured domain, resting on a figure with no committed source, changing a pre-registered form. Asking
instead of proceeding was the correct behaviour and is the behaviour expected here.

Σ\|q\| ≤ 6.0 and Σq² ≤ 2.00 are mutually consistent — Σ\|q\| = 6 over 18 centres is Σq² = 2.00 exactly, which is
why they were paired — but that was a coincidence of a figure that turned out to be wrong, so it carries no
weight. They are also jointly wrong given the domain: at Σ\|q\| = 2.880 e over 18 centres, Σq² = 0.46 e², so if
the measured domain binds, Σq² ≤ 2.00 is slack by a factor of four and constrains nothing.

The honesty record in `claude/HANDOVER_20261026.md` §10 lists the errors found in the work this brief summarises:
a fabricated quotation, two wrong diagnoses of Diagnostic 1, a classifier that condemned 616 of 832 healthy runs,
a gap quoted as 0.630 that the record gives as 0.629, and five further corrections in `STAGE6_ERRATUM3` E3.5.
**Read it before trusting any summary, this one included.**

---

## 8. How to work

`claude/HANDOVER_20261026.md` §11 has the bundle pattern, the three-pass rule and the HPC procedure. In short:
three passes before Jessica runs anything; code committed before it is run; outputs committed as physical files
with a sha256 manifest **before** anything is measured from them; plain unfiltered `qstat -u 18660916` as the
only evidence of job state; the explicit `git push` line every time; the full command line from download to run
with every bundle; and a running work log — one bullet per step, with file names, reasoning and result.

Explain the maths and the optimisation plainly and in detail. Never shape a calculation or a theory to get a
lower barrier. **Never assume, and never state what you have not checked.**
