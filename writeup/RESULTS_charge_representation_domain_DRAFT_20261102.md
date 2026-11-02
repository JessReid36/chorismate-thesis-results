# Results — the validity domain of the point-charge representation, and what a design achieves inside it

`[DECISION REQUIRED — the section number. I referred to this as §6.3 in working notes, but no
chapter outline in either repo defines a §6.3. WRITEUP_INDEX.md and WRITEUP_PROMPT.md both predate
Stage 6 and number only the Phase 1 Methods (X.0–X.7) and Results A–D. This section needs a place
in the chapter structure before it is numbered; the options are a new Results section in the Phase
2.2 chapter, or an extension of Results D.]`

Drafted 2 November 2026. Every number re-derived from committed energies; the verification log is
appended.

---

## Conditions under which these results were obtained

I evaluated every designed arrangement in this section **in vacuo**, at B3LYP-D3BJ /
def2-SVPD / def2-J / RIJCOSX / TightSCF in ORCA 6.0.1, as frozen single points on the committed
reactant and transition-state geometries of frame 42436. No continuum appears anywhere in this
section. The continuum was removed from Stage 6's evaluation condition by
`phase2.2/cs_stage6/STAGE6_AMENDMENT2_20261027.txt`, which states that from that date every Stage 6
single point evaluating a designed arrangement is run in vacuo.

The charge-free control gives

| quantity | value | source |
|---|---|---|
| E(reactant) | −836.249865855127 Eh | `phase2.2/cs_stage6/d16/def2-SVPD/ctl_R/job.out` |
| E(transition state) | −836.220651545264 Eh | `phase2.2/cs_stage6/d16/def2-SVPD/ctl_TS/job.out` |
| barrier | **18.3323 kcal/mol** | re-derived as (TS − R) × 627.5094740631 |

**Table 1.** The charge-free reference for this section, from `phase2.2/cs_stage6/d16/def2-SVPD/ctl_R/job.out` and `ctl_TS/job.out`.

This 18.3323 kcal/mol is a distinct quantity from the two bare barriers recorded in
`WRITEUP_INDEX.md`. It is a frozen single-point barrier at def2-SVPD in vacuo on frame 42436; the
canonical 17.47 kcal/mol is at def2-SVP under CPCM ε = 4 on the L0 geometry, and the 15.771
kcal/mol figure is an isolated-substrate proxy on a superseded geometry. The three are not
interchangeable and I do not merge them. Every effect reported below is referenced to 18.3323
kcal/mol and to nothing else.

---

## 1. Over what range of designed charge can the representation be read at all?

Each arrangement was classified by the rule designated D6.3, which assigns every run CLEAN,
POLARISED, STRAINED or COLLAPSED against same-basis control medians on the maximum Löwdin charge
deviation, the dipole ratio, the absolute HOMO–LUMO gap, the gap ratio and the SCF cycle ratio. An
arrangement is read only when all of its runs are CLEAN or POLARISED.

Of the nine whole-design conditions evaluated at def2-SVPD, **seven are readable and two are not.**
The two exclusions both fail on the reactant arm of the bare representation:

| condition | Σ\|q\| / e | max\|q\| / e | failing arm | indicator | source |
|---|---|---|---|---|---|
| S6-2 at 1.3000 e | 1.3000 | 0.6500 | `S6-2_bare_F1_R` | STRAINED, gap 0.567 eV | `phase2.2/cs_stage6/d16/DIAGNOSTIC16_RESULT.txt` |
| S6-5 at 1.6166 e | 1.6166 | 0.5389 | `S6-5_bare_M_R` | STRAINED, gap 0.880 eV | `phase2.2/cs_stage6/d17/DIAGNOSTIC17_RESULT.txt` |

**Table 2.** The two conditions whose shielding metric is withheld, and why, from `phase2.2/cs_stage6/d16/DIAGNOSTIC16_RESULT.txt` and `d17/DIAGNOSTIC17_RESULT.txt`.

In both cases the walled arm passes and the bare arm fails. `S6-5_wall_M_R` is CLEAN and
`S6-2_wall_F1_R` is POLARISED, and POLARISED satisfies the readability rule. The exclusions are
therefore a property of the bare point-charge representation at high per-site charge, not of the
walled one.

The per-site ceiling was located directly. `DIAGNOSTIC17_RESULT.txt` READING 3 places the usable
bare single-site charge **between 0.5389 and 0.6500 e**, on one site in one arrangement at one
geometry. The two exclusions above sit at max\|q\| of 0.6500 and 0.5389, at the outer edge of the
sampled region in per-site charge and in total charge respectively.

`[FIGURE 6.N — the accessible design region. Plot Σ|q| against max|q| for all nine conditions from
the committed arrangement files and the Dset table, marking readable points filled and the two
STRAINED points open, with the D17 per-site band 0.5389–0.6500 e shaded. Caption should state that
n ties the two axes together, so the two cannot be varied independently, and that the two
exclusions lie on the frontier.]`

---

## 2. Are the solutions genuine minima?

A readable classification does not establish that the self-consistent-field solution is a minimum
with respect to orbital rotation. I tested this directly, in three stages.

| what was tested | runs | verdict | source |
|---|---|---|---|
| S6-20 along a field ladder, both bases | 20 | stable to Σ\|q\| = 2.88 e; unstable from 4.32 e | `phase2.2/cs_stage6/d20/DIAGNOSTIC20_RESULT.txt` |
| the bare arm of all nine conditions | 18 | ALL STABLE | `phase2.2/cs_stage6/d21/DIAGNOSTIC21_RESULT.txt` |
| the walled and wall-at-zero arms of all nine | 30 | ALL STABLE | `phase2.2/cs_stage6/d22/DIAGNOSTIC22_RESULT.txt` |

**Table 3.** Wavefunction stability across the designed arrangements. All runs carried
`%scf STABPerform true` added to the production head with nothing else changed, and each run's first
converged energy was gated against its own committed production energy to 1 × 10⁻⁶ Eh.

Every leg of every readable condition is therefore a verified minimum: the charge-free control, the
bare arm, the walled arm and the wall-at-zero arm. The region between 2.88 and 4.32 e remains
unmeasured, and every arrangement in this section sits at or below 2.19 e.

The stability margins also separate the two representations sharply. Taking the lowest eigenvalue of
the stability matrix at the reactant geometry, against the control's 0.05655489:

| | bare arm | walled arm |
|---|---|---|
| range over the nine conditions | 0.00137315 – 0.05663975 | 0.04787002 – 0.05667827 |
| span, maximum over minimum | **41.2** | **1.18** |
| correlation with max\|q\| | **−0.697** | **+0.024** |

**Table 4.** Stability margins, from `d21/DIAGNOSTIC21_RESULT.txt` and `d22/DIAGNOSTIC22_RESULT.txt`.

The bare representation's margin degrades with per-site charge and falls to 2 per cent of the
control's value at S6-2 at 1.3000 e. The walled representation's margin lies within 15.4 per cent of
the chargeless control for every condition and shows no dependence on per-site charge. The wall
restores the margin while retaining 94.8 and 94.2 per cent of the effect at the two conditions where
the bare arm is worst, so the restoration is not achieved by screening the charge away.

`[FIGURE 6.N — bare against walled stability margin. Scatter the nine conditions, x = max|q|,
y = E(0) at the reactant, two series, with a horizontal line at the control's 0.05655489. Data from
the two RESULT files. Caption should give both correlations and note the 41.2-fold against
1.18-fold spread.]`

---

## 3. What does a design achieve inside the domain?

| condition | n | Σ\|q\| / e | ddE(bare) | barrier | source (bare arm) |
|---|---|---|---|---|---|
| S6-20 at 1.3000 e | 20 | 1.3000 | −4.9965 | 13.3357 | `d16/def2-SVPD/S6-20_bare_F1_{R,TS}` |
| S6-10 at 1.3000 e | 10 | 1.3000 | −6.1341 | 12.1981 | `d16/def2-SVPD/S6-10_bare_F1_{R,TS}` |
| S6-2 at 1.0777 e | 2 | 1.0777 | −7.5374 | 10.7949 | `d17/def2-SVPD/S6-2_bare_M_{R,TS}` |
| S6-5 at 1.3000 e | 5 | 1.3000 | −8.2544 | 10.0779 | `d16/def2-SVPD/S6-5_bare_F1_{R,TS}` |
| S6-20 at 2.1900 e | 20 | 2.1900 | −8.6626 | 9.6697 | `d16/def2-SVPD/S6-20_bare_F2_{R,TS}` |
| S6-3 at 1.3000 e | 3 | 1.3000 | −8.7724 | 9.5599 | `d16/def2-SVPD/S6-3_bare_F1_{R,TS}` |
| S6-10 at 2.1900 e | 10 | 2.1900 | −10.6714 | 7.6609 | `additivity/def2-SVPD/n10_bare_A_{R,TS}` |

**Table 5.** Barrier change and resulting frozen barrier for the seven readable conditions, in
kcal/mol, in vacuo at def2-SVPD on frame 42436, against the 18.3323 kcal/mol control of Table 1.
All paths relative to `phase2.2/cs_stage6/`.

The designs lower the frozen barrier by **4.9965 to 10.6714 kcal/mol**, giving barriers of **7.6609
to 13.3357 kcal/mol**. Every barrier is positive, so every condition remains physically meaningful
at the frozen geometry.

`[PLACEHOLDER — needs sourcing: the enzyme comparator. The differential transition-state
stabilisation for BsCM is quoted as 7.3 kcal/mol in HANDOVER_20261014.md, attributed to the
abstract of Claeyssens et al. (2011), which is in the Project as 2011_paper.pdf. I have not read
that abstract directly and the figure must be verified against the PDF before it is placed beside
Table 5. ERRATUM 7 records three comparator figures withdrawn for exactly this reason.]`

`[FIGURE 6.N — barrier against Σ|q| for the seven readable conditions, from Table 5, with the
control at 18.3323 marked. Caption should state the conditions and that all points are frozen
single points in vacuo.]`

---

## 4. What the shielding metric measures, and what it does not

The quantity I use to compare the bare and walled representations is

    d_shield = ddE(bare) − ddE(wall)

with the walled arm corrected by subtracting its zero-charge wall run, so that what remains is
attributable to the charge rather than to the projector. Decomposing it:

| condition | n | raw discrepancy | ddE(wall0) | d_shield |
|---|---|---|---|---|
| S6-2 at 1.0777 e | 2 | −0.3442 | −0.0026 | −0.3468 |
| S6-3 at 1.3000 e | 3 | −0.2564 | −0.1815 | −0.4379 |
| S6-5 at 1.3000 e | 5 | **+0.0097** | −0.4407 | −0.4311 |
| S6-10 at 1.3000 e | 10 | **+0.4757** | −0.7187 | −0.2430 |
| S6-10 at 2.1900 e | 10 | **+0.3047** | −0.7187 | −0.4140 |
| S6-20 at 1.3000 e | 20 | **+0.4488** | −0.6190 | −0.1702 |
| S6-20 at 2.1900 e | 20 | **+0.3270** | −0.6190 | −0.2919 |

**Table 6.** d_shield decomposed into the uncorrected bare-minus-walled discrepancy and the
chargeless wall term, in kcal/mol. Re-derived from the committed bare, walled and wall-at-zero arms
listed in Tables 2 and 5.

From five centres upward the uncorrected discrepancy carries the opposite sign to d_shield, and the
sign of the reported quantity is set by the correction. At S6-5 the uncorrected discrepancy is
+0.0097 kcal/mol and the whole of the 0.4311 kcal/mol d_shield is the correction term.

I report d_shield at n ≥ 5 as a residual of two larger terms rather than as a direct measurement.
The correction is physically required, since the projector contributes a chargeless Pauli term that
differs between the two geometries, but its magnitude relative to the residual bears on the
precision of the result and on the parameter dependence discussed below.

`[DECISION REQUIRED — whether d_shield is reported in the thesis as a primary observable or as a
diagnostic. Table 6 shows it is a small residual at n ≥ 5. The alternative is to report the
uncorrected discrepancy and the chargeless term separately, which is more transparent but has no
precedent in the committed pre-registrations.]`

---

## 5. What the domain excludes

At full field the designs leave the domain. `DIAGNOSTIC17_RESULT.txt` records S6-10 at Σ\|q\| =
4.2913 e and S6-20 at Σ\|q\| = 5.6433 e as NOT READABLE, classified CLEAN, COLLAPSED, STRAINED in
both cases. Those arrangements are also above the 4.32 e instability onset of Table 3. They are
therefore outside the domain on two independent measured grounds and I report no barrier for them.

---

## 6. Limits of this section

- Every result is a frozen single point. No geometry was relaxed, so none of these barriers is an
  activation free energy and none accounts for geometric response to the designed field.
- The stability test is restricted-to-restricted. A stable verdict means the solution is a minimum
  under the orbital rotations ORCA's stability analysis spans; it does not establish
  single-reference character. `DIAGNOSTIC19_RESULT.txt` returned DISAGREE on its multireference
  reading and that stands.
- The Pauli wall uses a published pseudopotential outside the domain its authors validated, recorded
  in `STAGE6_ERRATUM7_20261026.txt` E7.8. The chargeless wall term of Table 6 is that
  pseudopotential acting with no charge and no basis functions, so a systematic error in its
  parameters propagates into d_shield at n ≥ 5 close to one for one. The sensitivity has not been
  measured.
- The region 2.88 to 4.32 e in Σ\|q\| is unmeasured for stability.

---

## Sourcing gaps

1. **The section number.** No chapter outline defines §6.3 or any Stage 6 Results section. See the
   decision block at the head of this file.
2. **The enzyme comparator.** The 7.3 kcal/mol differential transition-state stabilisation must be
   read from `2011_paper.pdf` before it is used. Placeholdered in §3.
3. **ECP parameter sensitivity.** Unmeasured, and required for §6's fourth limit to be quantified
   rather than stated. A literature brief on alternative published parameter sets was issued on
   2 November (`claude/ECP_BRIEF_20261102.md`).
4. **A figure of the accessible design region** needs the per-site charge vectors written to a data
   file; they currently exist only inside `relax/ARRANGEMENTS.txt` and are read programmatically.

## Inconsistencies found

1. **`WRITEUP_INDEX.md` states the theory level for all bare and charge work as def2-SVP under
   CPCM ε = 4.** Stage 6's def2-SVPD evaluations are in vacuo, by
   `STAGE6_AMENDMENT2_20261027.txt`. The index predates the amendment and should be updated, or a
   reader will take the barriers in Table 5 to be continuum values.
2. **A third bare-barrier figure now exists.** `WRITEUP_INDEX.md` lists 17.47 (canonical) and
   15.771 (superseded proxy). Table 1's 18.3323 is a third, at a different basis and continuum
   setting. The index's canonical-barrier table should carry it with its conditions, so the three
   are not merged later.
3. **`STAGE6_FINDINGS_20261022.md` reports a bare frozen barrier of 18.4610 kcal/mol** at def2-SVP.
   That is a fourth quantity, differing from Table 1 by basis. Both are correct for their own
   conditions; neither should be quoted without them.

## Verification log

```
Control, in vacuo, B3LYP-D3BJ/def2-SVPD, frame_42436, frozen single points
  R   -836.249865855127   d16/def2-SVPD/ctl_R/job.out
  TS  -836.220651545264   d16/def2-SVPD/ctl_TS/job.out
  barrier = (TS - R) x 627.5094740631 = 18.3323 kcal/mol

Per condition: ddE(bare) = [(E_bare,TS - E_ctl,TS) - (E_bare,R - E_ctl,R)] x 627.5094740631
               barrier   = 18.3323 + ddE(bare)

condition          E_bare_R        E_bare_TS     ddE(bare)   barrier
S6-2 at 1.0777   -836.258538     -836.241336      -7.5374   10.7949
S6-3 at 1.3000   -836.215801     -836.200566      -8.7724    9.5599
S6-5 at 1.3000   -836.272747     -836.256687      -8.2544   10.0779
S6-10 at 1.3000  -836.197018     -836.177579      -6.1341   12.1981
S6-10 at 2.1900  -836.168364     -836.156155     -10.6714    7.6609
S6-20 at 1.3000  -836.236651     -836.215399      -4.9965   13.3357
S6-20 at 2.1900  -836.232942     -836.217533      -8.6626    9.6697

effect range  -10.6714 to -4.9965 kcal/mol
barrier range   7.6609 to 13.3357 kcal/mol; every barrier positive

No disagreement was found between any re-derived barrier and a value asserted in a committed
result file. The two Dset values that DIAGNOSTIC 16 reports independently, 0.2919 at n = 20 and
0.4140 at n = 10, were reproduced to four decimals by the decomposition of Table 6.
```
