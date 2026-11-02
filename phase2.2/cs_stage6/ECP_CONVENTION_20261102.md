# Experiment 0: the pseudopotential convention, closed — and one of the three sets cannot be validated

**2 November 2026.** No HPC time. Every number here is measured by
`chorismate-thesis-code/phase2.2/cs6_exp0.py` and printed in
`phase2.2/cs_stage6/exp0/EXPERIMENT0_RESULT.txt`, committed alongside this note; nothing is
transcribed from a prior document. Quotations are from `chorismate-refs/ct9b01162_si_001.pdf`
read directly, and from the ORCA 6.0 and NWChem manuals as marked.

```
VERDICTS: CONVENTION CONFIRMED | Ne AND He VALIDATED | Ar NOT VALIDATED
```

This answers the first open item of `claude/ECP_ASSESSMENT_20261102.md`: *whether ORCA reads the
power-of-r column the way TURBOMOLE does.* It mattered because if the convention were wrong, every
walled number in the Stage 6 record used a different potential from the published one — including
DIAGNOSTIC 22's inverted finding that the walled arm is the better-behaved estimate.

---

## 1. The convention is ORCA's own, documented, and the parameters agree with it

Three independent lines, none of them an ORCA run.

**(a) ORCA's manual, cross-checked against third-party listings of the same potential.** The ORCA
6.0 manual (§7.5) names the fourth column "the radial power n_kl" and gives no equation. But its
worked example is a *published* potential, V with SD(10,MDF), whose s channel it writes [quoted]:

```
  s 2
    1  14.4900000000  178.4479710000  2
    2   6.5240000000   19.8313750000  2
```

basis-set-exchange carries those exact primitives in **three** sets — Stuttgart RSC 1997, Stuttgart
RSC 1997 ECP, and Grimme vDZP — and all three list them in NWChem format as:

```
V S
2      14.490000000          178.447971000
2       6.524000000           19.831375000
```

Same exponents, same coefficients, same potential, and the power column reads **2** in every
listing. NWChem documents its radial form explicitly [quoted]:

```
U_l(r) = r^(-2) * sum_k A_lk * r^(n_lk) * exp(-B_lk r^2)
```

and states that the shift is "in accordance with most of the ECP literature and implementations",
so n = 2 means **r⁰**. ORCA's column is NWChem's column.

**(b) The published Ne parameters reproduce their own fitting target under r⁰ and not under r².**
Table S2 states the parameters were fitted so that a centre carrying zero electrons reproduces
neutral Ne's 3s3p3d4s4p4d orbital energies in d-aug-cc-pwCV5Z "within 6 digits". Building
`T + V_ECP` for a centre with no electrons and no nuclear charge — the nuclear-attraction matrix is
gated to zero at 1e-10 before use — and diagonalising per angular momentum against all-electron RHF:

| level | HF reference (Eh) | T + V_ECP, r⁰ | difference |
|---|---|---|---|
| 3s | +0.050620645 | +0.050620828 | +1.84e-07 |
| 4s | +0.297303259 | +0.297302911 | −3.48e-07 |
| 3p | +0.050786389 | +0.050786402 | +1.30e-08 |
| 4p | +0.218529646 | +0.218529647 | +3.07e-10 |
| 3d | +0.246022728 | +0.246021961 | −7.67e-07 |
| 4d | +0.820031407 | +0.820031129 | −2.78e-07 |

Max |deviation| **7.670e-07 Eh** under r⁰ against **1.495e-01 Eh** under r² — five orders of
magnitude apart. The published claim reproduces; the literal reading of the column does not.

**(c) The fitting basis is confirmed at the same time.** The agreement is sharply best at the
doubly augmented basis, which is independent evidence that the SI's "d-aug" is meant as written and
that the even-tempered construction used here is close to the authors':

| basis for Ne | nao | max dev, r⁰ | max dev, r² |
|---|---|---|---|
| aug-cc-pwCV5Z | 181 | 1.099e-01 | 3.434e-01 |
| **d-aug (one even-tempered shell)** | 217 | **7.670e-07** | 1.495e-01 |
| t-aug (two) | 253 | 5.224e-05 | 1.969e-02 |

**Conclusion.** The operator ORCA was given is the authors' operator.
`STAGE6_ERRATUM7_20261026.txt` E7.8's concern is confirmed to be about domain of applicability
only, not about transcription.

---

## 2. The three parameter sets are not equally checkable

With a test the published sets must pass, all three were put through it on the basis and target
shells each one's own SI caption names:

| set | target shells (SI) | fitting basis (SI) | precision claimed | max dev, r⁰ | max dev, r² | verdict |
|---|---|---|---|---|---|---|
| He (Table S1) | 2s2p3s3p | d-aug-cc-pV5Z | "within 6 digits" | **1.381e-06** | 7.136e-02 | VALIDATED |
| Ne (Table S2) | 3s3p3d4s4p4d | d-aug-cc-pwCV5Z | "within 6 digits" | **7.670e-07** | 1.495e-01 | VALIDATED |
| Ar (Table S3) | 4s4p4d5s5p5d | aug-cc-pV(6+d)Z | **NONE STATED** | **3.067e-03** | 7.954e-01 | **NOT VALIDATED** |

**Table S3 differs from S1 and S2 in three ways**, all read from the SI page directly: a different
and only singly augmented basis; a d target of 4d/5d rather than the first two unoccupied d levels;
and no precision claim at all — S1 and S2 both say "within 6 digits", S3's caption simply ends.

Ar was tried on every basis available, under both readings of its d target:

| basis | aug level | nao | d = 3d,4d | d = 4d,5d |
|---|---|---|---|---|
| aug-cc-pV(5+d)Z | aug | 136 | 1.096e-02 | 2.521e-01 |
| aug-cc-pV(5+d)Z | d-aug | 172 | **3.067e-03** | 6.215e-03 |
| aug-cc-pV6Z | aug | 193 | 5.404e-03 | 2.174e-01 |
| aug-cc-pV6Z | d-aug | 242 | 4.944e-03 | 1.450e-02 |
| aug-cc-pV5Z | aug / d-aug | 131 / 167 | 1.096e-02 / 5.998e-03 | 3.517e-01 / 2.111e-02 |
| aug-cc-pwCV5Z | aug / d-aug | 217 / 253 | 1.398e-02 / 5.690e-03 | 3.481e-01 / 2.741e-02 |

The best cell is 3.067e-03 Eh, three orders worse than He and Ne. `aug-cc-pV(6+d)Z` as named is not
in basis-set-exchange, so the SI's exact basis could not be built; the eight combinations above span
131 to 253 functions and the residual never approaches 1e-06. The committed result file uses
aug-cc-pV(5+d)Z for Ar and labels it a substitute.

**Truncated precision is excluded as the cause.** Ar's parameters carry 4–5 significant figures
where Ne's carry 6. Twenty-four draws, each coefficient and exponent moved within half a unit of its
last quoted digit, give a residual range of **3.063e-03 to 3.071e-03** — a spread of 7.3e-06, some 400 times
too small to account for the discrepancy. The parameters as published simply do not
reproduce the stated target in any basis available here.

**What that leaves.** Either the named 6-zeta basis behaves very differently from eight nearby
alternatives, or the Ar fit is looser than He's and Ne's — which is consistent with its caption
being the only one of the three to claim no precision. This cannot be decided without
`aug-cc-pV(6+d)Z`.

---

## 3. What this changes for the parameter-sensitivity experiment

1. **He is a verified comparator; Ar is not.** A difference measured against He is a difference
   between two operators each confirmed to be the one its authors published. A difference measured
   against Ar carries, on top of that, an unquantified 3e-03 Eh discrepancy between the Ar block and
   its own fitting target. The two must be reported separately, and an Ar result must not be
   described as "the published Ar operator" without this note.
2. **The bracketing argument weakens on one side.** He and Ar were argued to bracket Ne in Gaussian
   spread and s-channel strength (2.42 / 54.51 / 275.0), so a flat response to both would be
   informative. That holds for He. For Ar the operator being run is not demonstrably the one the
   bracket was argued about.

This does not stop the experiment and does not change its cost. It changes what its Ar column may
be called.

---

## 4. One correction to the ECP assessment

`claude/ECP_ASSESSMENT_20261102.md` §3 describes the fitting target of all three sets as "lowest HF
virtual orbital energies per l of the neutral rare-gas atom, with zero electrons". For He and Ne
that is exact. For Ar it is not: the SI names a different basis, a d target that skips the first
unoccupied d level, and no precision. The first Ar test run here inherited that generalisation and
was wrong by a factor of two in its residual; reading Table S3 from the PDF fixed it. The parameter
digits the assessment quotes are correct in all three cases — the generalisation is in the target
description, not the numbers.

---

## 5. Method, and what was not done

`T + V_ECP` is built with PySCF for a centre whose ECP `nelec` equals the element's Z, so the
effective nuclear charge and the electron count are both zero; the script stops if either is not.
Eigenvalues are collapsed into distinct levels before comparison — an earlier version indexed
degenerate components and reported 3p as 4p and 3d as 4d, testing four distinct levels while
claiming six.

**Not done: no ORCA run.** The convention is established documentarily and by the physics of the
fit, not by executing ORCA. A stronger end-to-end check remains available at no HPC cost —
reproduce one committed walled `FINAL SINGLE POINT ENERGY` with an independent code under the r⁰
reading, calibrated against the charge-free control arm so that method differences are separated
from operator differences. That would test ORCA's ECP *integrals*, a different question from its
input convention, and would catch a projector normalisation or sign difference that this experiment
cannot.
