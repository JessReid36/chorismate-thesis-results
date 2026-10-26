# START HERE — Phase 2.2, Stage 7

## 1. The task

**Write Stage 7 of the Phase 2.2 charge design.** That is the work. Everything else in this file exists to stop
you starting it before you are entitled to.

Stage 7 needs, at minimum:

- the per-site charge cap restated as a **magnitude and a distance**, because the collapse threshold depends on both and the withdrawn `q_quad = 0.80 e` conflated them;
- Σ\|q\| ≤ 6.0 e, with the six-charged-residue basis stated on its face;
- Σq² ≤ 2.00 retained as the **shaping** constraint, with the reason recorded: Σq² is not invariant to how finely a charged group is discretised and Σ\|q\| is, and Σ\|q\| = 6 over 18 centres gives Σq² = 2.00 exactly;
- **no 3.0 Å clearance floor** — a standing instruction. Real enzyme residues do not sit at a fixed distance, and adopting 3.0 Å because other papers use it was explicitly rejected;
- the λ ≤ 0.50 domain either **tested on a second design** or declared untested on the face of the document;
- the 11% basis and 19–25% environment uncertainties carried explicitly.

It is pre-registered work: write it, commit it **before** anything is run against it, and never edit it
afterwards — changes go in a dated amendment or erratum.

## 2. What is NOT the task

**The ~90 SP-package jobs on hpc1 are Phase 1 and they are not your task.** They are live and they are
context. Do not analyse them, do not plan around them, do not propose work on them unless Jessica asks.

Two things only:

1. **Watch `419762 sa200008ts`.** At the 26 October snapshot it had used 133 of its 176 h walltime. If it is killed, the five jobs held behind it never start, because PBS `afterok` requires exit 0. Check with a plain `qstat -u 18660916` and tell Jessica what you see. Do not act further.
2. **If a frame's package completes**, say so and stop. The completion procedure is pre-registered in `05_qmmm/24_sp_barriers/SP_PLAN.txt` and its amendments and must be read in full before any result is touched.

Details are in `claude/HANDOVER_20261026.md` §4. That handover put the SP package in §1 and §4, which caused an
earlier session to anchor on frames instead of charges. **That was a sequencing error in the handover, not a
change of priority.** Phase 2.2 is the thread being continued.

## 3. Read this before writing anything

In this order. **In full. Do not skim.** The single largest failure in this project was six diagnostics reading
energies only while the SCF cycle count and the HOMO–LUMO gap sat unread in the same output files for weeks.

**(a) Context, once:** `claude/HANDOVER_20261026.md`. It is a map, not evidence.

**(b) The pre-registrations, in full, in order.** These bind Stage 7 and are never edited:

```
phase2.2/PHASE22_PLAN.txt                       and PHASE22_PLAN_UPDATE_20261009.md
phase2.2/cs_stage5/STAGE5_CRITERIA.txt
phase2.2/cs_stage6/STAGE6_CRITERIA.txt          STAGE6_AMENDMENT1.txt
                                                STAGE6_ERRATUM1.txt  STAGE6_ERRATUM2.txt
                                                STAGE6_ERRATUM3_20261026.txt
phase2.2/cs_stage6/STAGE6_DIAGNOSTIC1_20261022.txt
                   STAGE6_DIAGNOSTIC2_20261022.txt  STAGE6_DIAGNOSTIC2_AMENDMENT1_20261022.txt
                   STAGE6_DIAGNOSTIC3_20261022.txt  STAGE6_DIAGNOSTIC3_NOTE1_20261022.txt
                   STAGE6_DIAGNOSTIC4_20261023.txt
                   STAGE6_DIAGNOSTIC5_20261026.txt  STAGE6_DIAGNOSTIC6_20261026.txt
phase2.2/cs_stage6/STAGE6_ASSESSMENT_20261022.md
phase2.2/OPTIMISER_DECISIONS_20261020.md        CHARGE_MODEL_DECISIONS.md
                   STAGE6_DECISIONS_20261021.md
                   LIBRARY_ERRATUM1_20261020.md LIBRARY_ERRATUM2_20261021.md
```

**(c) The outputs — see §4. Re-derive; do not read the reports and move on.**

**(d) The literature.** `chorismate-refs/` holds 77 papers. Read these in full before using them:

- `acs.jctc.9b01162.pdf` — Marefat Khah et al., JCTC 2020. The electron spill-out paper the whole Stage 6 finding rests on. Read it yourself; do not take this file's paraphrase.
- `1.3484283.pdf` — Rappoport & Furche, JCP 133, 134105. def2-SVPD, "property-optimized"; the caveat on p. 9 about "(small) anions" matters here.
- the chorismate-mutase mechanism and barrier papers, for what a defensible barrier reduction looks like.

**A claim from a paper must come from the full paper in `chorismate-refs/`** — not an abstract, not a search
result, not memory. If a paper is missing, give its checked DOI and **wait** until it is committed. One paper is
not a standard; three or more independent sources are.

**(e) The last two months of repository history**, for how the current state was arrived at. 165 commits in
results, 79 in code:

```
git -C ~/Desktop/chorismate-thesis-results log --since=2026-08-26 --date=short \
    --format='%ad %h %s' -- phase2.2 | tac
git -C ~/Desktop/chorismate-thesis-code    log --since=2026-08-26 --date=short \
    --format='%ad %h %s' | tac
```

The commit messages here are long on purpose and carry the reasoning, the rejected alternatives and the
literature basis. They are the record of why, and they are worth reading rather than skipping to the diffs. The
Phase 2.2 lineage in that window: `cs_stage4` → `4b` → `4c` → `4d` → `4e` → `cs_stage5` → `cs_stage6`, plus
`s11_probe_scan`, `s13_lj_test`, `s15_dv2`, `wp1_lj_combining`, `wp4_s13_rerun`, `wp5_rigid_scan`.

## 4. Reference the outputs, not the reports

**Every `*_RESULT.txt`, every `*_REPORT.txt`, the assessment and the handover are interpretations, and
interpretations in this project have been wrong repeatedly.** The honesty record in `HANDOVER_20261026.md` §10
lists the ones found so far, including a fabricated quotation, two wrong diagnoses of Diagnostic 1, a classifier
that condemned 616 of 832 healthy runs, and a figure quoted as 0.630 that the record gives as 0.629.

So, before Stage 7 cites a number:

**Re-derive it.** Both analysis scripts are read-only, take seconds, and touch nothing:

```
python3 ~/Desktop/chorismate-thesis-code/phase2.2/cs6_audit.py  ~/Desktop/chorismate-thesis-results /tmp/d6check
python3 ~/Desktop/chorismate-thesis-code/phase2.2/cs6_decomp.py ~/Desktop/chorismate-thesis-results /tmp/d5check
```

Confirm they reproduce `DIAGNOSTIC6_RESULT.txt` and `field/DIAGNOSTIC5_RESULT.txt`. If they do not, **that is the
finding** and Stage 7 waits.

**Open the actual `job.out` files** for the runs the errata name, out of the committed archives, and read the
SCF cycle count, the HOMO–LUMO gap, the dipole and the Loewdin charges with your own eyes:

```
phase2.2/cs_stage6/frozen/sp_outputs.tar.xz        S6-C/P/2/3/5/10/20, R and TS, def2-SVP
phase2.2/cs_stage6/field/outputs/field_outputs.tar.xz   the 16 lambda-scan points
phase2.2/cs_stage6/qrefine/outputs/qrefine_outputs.tar.xz  qp0650, qp0800 - the q_quad withdrawal
phase2.2/cs_stage6/qscan/outputs/qscan_outputs.tar.xz      93 runs, C1-C5
phase2.2/cs_stage6/pauli/outputs/pauli_outputs.tar.xz      M2 Na+, M3 K+ - the Diagnostic 3 withdrawal
phase2.2/cs_stage6/a_matrix_outputs.tar.xz                 the A matrix's finite differences
phase2.2/cs_stage6/diffuse/outputs/diff_outputs.tar.xz     Diagnostic 1
```

Every archive has a `*.MANIFEST.sha256` beside it. Check members against it.

**Never state a figure that is not in a committed file.** If you cannot find it, say you cannot find it.

## 5. Open questions to settle while reading — do not assume answers

- **`phase2b_charge_design/06_charge_tests` has 764 committed entries and no output archive of its own.** Its point-charge files are named `pc_most_stabilising_q025_p.pc`, `q050`, `_m`/`_p` — single site, q ≤ 0.50, which is consistent with the finding that the representation was validated below its collapse threshold. **Whether its ORCA outputs are committed anywhere, and whether Diagnostic 6 therefore covered them, is NOT established.** Find out before citing that folder.
- **The 9 SP frames absent from the queue** — finished or never submitted. From hpc1, not by inference. (Context only; see §2.)
- **The three climbing-image folders** `f{20000,44388,59999}_r8_ci_a1` — what they are for is not established here.
- **Diagnostic 6 filters to 118 electrons**, so the Na⁺ (128 e) and K⁺ (136 e) runs behind the Diagnostic 3 withdrawal were never classified by it. Those figures are hand-read. Extending the audit is an open item.
- **Does the λ ≤ 0.50 domain transfer to a second design?** Untested. Scaling S6-10 as Diagnostic 4 scaled S6-20 is 16 single points in one restartable job.

## 6. How to work

`claude/HANDOVER_20261026.md` §11 has the bundle pattern, the three-pass checking rule and the HPC procedure.
In short: three passes before Jessica runs anything; code committed before it is run; outputs committed as
physical files with a sha256 manifest **before** anything is measured from them; plain unfiltered
`qstat -u 18660916` as the only evidence of job state; the explicit `git push` line given every time; the full
command line from download to run given with every bundle; and a running work log, one bullet per step, with
file names, reasoning and result.

Explain the maths and the optimisation plainly and in detail. Never shape a calculation or a theory to get a
lower barrier. Never assume, and never state what you have not checked.
