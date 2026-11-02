# What d_shield is actually made of

**2 November 2026, revised the same day.** Everything here is **measured from committed files** in
the results repo at `0af73ad`. No new runs. **This note re-reads committed results; it does not
edit any of them.**

> **This note's first version got DIAGNOSTIC 14 backwards.** It claimed the chargeless wall's
> non-additivity accounted for "half to seven tenths" of D14's superadditive excess, with the same
> sign. The exact decomposition, now complete, shows the opposite: the charge-free term **opposes**
> the excess and partially cancels it, so D14's cooperativity is **larger** than it reported, not
> smaller. The error came from comparing one component's magnitude against a net that is a
> *difference* of components, without computing the other component or checking its sign. The
> corrected analysis is in §4.

## 1. The decomposition, and its validation

From `cs6_d17.py` and `cs6_additivity.py`, with every energy referenced to the charge-free control
and the walled arm corrected by its zero-charge wall term:

```
Dset = [ ddE(bare) - ddE(wall, raw) ]  +  ddE(wall0)
         \_____ raw discrepancy _____/     \_ chargeless wall term _/
```

| condition | n | max\|q\| | ddE(bare) | raw disc. | ddE(wall0) | Dset |
|---|---|---|---|---|---|---|
| S6-2_D17 | 2 | 0.6500 | −7.5374 | **−0.3442** | −0.0026 | −0.3468 |
| S6-3_D16 | 3 | 0.5389 | −8.7724 | **−0.2564** | −0.1815 | −0.4379 |
| S6-5_D16 | 5 | 0.4333 | −8.2544 | **+0.0097** | −0.4407 | −0.4311 |
| S6-10_D16 | 10 | 0.1632 | −6.1341 | **+0.4757** | −0.7187 | −0.2430 |
| S6-10_D15 | 10 | 0.5000 | −10.6714 | **+0.3047** | −0.7187 | −0.4140 |
| S6-20_D16F1 | 20 | 0.1241 | −4.9965 | **+0.4488** | −0.6190 | −0.1702 |
| S6-20_D16F2 | 20 | 0.2090 | −8.6626 | **+0.3270** | −0.6190 | −0.2919 |

**The decomposition is validated against committed results**: summing the single-charge arms of
S6-20 at F2 gives ΣDset_i = −0.1848, which is DIAGNOSTIC 16's reported `|signed sum| 0.1848`, and
the resulting excess of −0.1071 is its reported `+0.1071`. For S6-10 at A the excess comes out
−0.1641 against the reported +0.1640. All 20 and all 10 singles were recovered.

**For n ≥ 5 the raw discrepancy has the opposite sign to the reported Dset.** Uncorrected, the
walled arm gives a *stronger* effect than the bare charge; the reported shielding appears only
after `ddE(wall0)` is subtracted. At S6-5_D16 the raw discrepancy is **+0.0097 kcal/mol** and the
entire 0.4311 Dset is the correction.

The physics of correcting is sound: the projector contributes a chargeless Pauli/steric term that
differs between R and TS, and isolating the screening requires removing it. d_shield is a
meaningful quantity. What this note records is that at n ≥ 5 it is a small residual whose sign is
set by a term larger than itself.

## 2. The chargeless wall term depends on the positions, not the count

An earlier claim that it "grows with the number of centres" was **wrong**. Over 36 committed
def2-SVPD wall-at-zero arms:

| centres | ddE(wall0), kcal/mol |
|---|---|
| 1 (26 arms) | −0.2551 … +0.1118, both signs |
| 2 | −0.0652, −0.0026 |
| 3 | −0.1815, −0.0117 |
| 4 | **+0.1003** |
| 5 | −0.4407 |
| 6 | **−0.8218** ← largest magnitude in the record |
| 10 | −0.7187, −0.7187 |
| 20 | −0.6190 |

n = 4 is positive; n = 6 is the most negative of all; n = 20 is smaller in magnitude than n = 6.
A single chargeless centre alone can move the barrier by up to 0.2551 kcal/mol.

## 3. C-A1.1 applied to these arms

`cs11_standoff.py`, `cs12_sites.py` and `cs13_qscale.py` require `|ddE(wall, q=0)| ≤ 0.30` and
**VOID** a walled result that fails:

```
S6-2_wall0    -0.0026  inert        S6-10_wall0   -0.7187  NOT INERT  (2.4x)
S6-3_wall0    -0.1815  inert        S6-20_wall0   -0.6190  NOT INERT  (2.1x)
S6-5_wall0    -0.4407  NOT INERT    n10_wall0     -0.7187  NOT INERT
n6neg_wall0   -0.8218  NOT INERT  (2.7x)
```

**No committed rule is broken** — C-A1.1 governs D11/D12/D13, and `cs6_d17.py` and
`cs6_additivity.py` impose no inertness gate, using `wall0` as a subtracted correction instead. But
the same quantity that voids a probe rung in one module is silently subtracted in another, and that
asymmetry is nowhere recorded.

## 4. DIAGNOSTIC 14's superadditivity is real, charge-mediated, and UNDERSTATED

Both constituent terms are strongly **sub**-additive, and they pull in opposite directions:

**S6-20 at F2 (n = 20), all 20 singles complete**

| term | collective | sum of singles | non-additivity |
|---|---|---|---|
| raw (charge-mediated) | +0.3270 | +0.5089 | **−0.1818** |
| z (charge-free) | −0.6190 | −0.6937 | **+0.0747** |
| Dset = raw + z | −0.2919 | −0.1848 | **−0.1071** |

**S6-10 at A (n = 10), all 10 singles complete**

| term | collective | sum of singles | non-additivity |
|---|---|---|---|
| raw (charge-mediated) | +0.3047 | +0.5520 | **−0.2473** |
| z (charge-free) | −0.7187 | −0.8019 | **+0.0832** |
| Dset = raw + z | −0.4140 | −0.2499 | **−0.1641** |

The charge-mediated non-additivity is the **larger** term and carries the **same sign** as the net
excess. The charge-free term **opposes** it, cancelling 41% of it at n = 20 and 34% at n = 10.

So the charge cooperativity is **−0.1818** at n = 20 and **−0.2473** at n = 10, against D14's
reported excess of −0.1071 and −0.1641 — roughly **1.7× and 1.5× larger than reported**.
DIAGNOSTIC 14's verdict is strengthened, not weakened, and the reported figure is a lower bound on
the charge-mediated effect.

**This does not require an erratum on D14.** Its arithmetic and its verdict are correct as stated;
the quantity it reported is simply a net of two opposing non-additivities, and the charge-mediated
part is larger than the net. That is new information, not a correction to it.

## 5. Single sites: raw and z very nearly cancel

For every one of the 20 single-charge arms of S6-20 at F2, `raw_i ≈ −z_i`, leaving a tiny residual:

```
s673   raw +0.1749   z -0.2227   Dset_i -0.0477      s590   raw +0.1851   z -0.2220   Dset_i -0.0370
s615   raw +0.1008   z -0.1204   Dset_i -0.0197      s762   raw +0.1273   z -0.1481   Dset_i -0.0209
s52    raw +0.0042   z -0.0012   Dset_i +0.0029      s688   raw +0.0059   z -0.0064   Dset_i -0.0005
```

Largest single-site \|Dset_i\| is **0.0477 kcal/mol**. So a *single* charge behind a wall, corrected
for the wall's own effect, reproduces a bare point charge almost exactly — and the collective Dset
of −0.29 to −0.41 is therefore a genuine **many-body** quantity, not a sum of per-site errors. This
is independent support for DIAGNOSTIC 12's conclusion that no per-site descriptor can predict it.

## 6. DIAGNOSTIC 16 READING 1, "Dset FALLS WITH n"

Literally correct: 0.4379, 0.4311, 0.2430, 0.1702 for n = 3, 5, 10, 20 at Σ\|q\| 1.3 e. Decomposed,
the raw discrepancy does **not** fall — it rises through zero near n = 5 (−0.2564, +0.0097, +0.4757,
+0.4488). If the reading were taken to mean the bare point charge's error shrinks as charge is
spread, the decomposition does not support that: raw agreement is best near n ≈ 5 and worsens in
both directions.

## 7. The proportionality hypothesis is withdrawn

The pattern noticed on 1 November — Dset a roughly constant 3.4–5.8% of the effect — is a
cancellation between a raw term and a correction term that vary independently and have opposite
signs for n ≥ 5. `|ddE(wall0)|/|ddE(bare)|` alone runs 5.3% to 12.4%. **No diagnostic should be
built on it.**

## 8. What this means for ERRATUM 7, stated carefully

A chargeless ECP centre is the borrowed Marefat Khah Ne parameters in their purest form: no charge,
no basis functions (nbasis 402, NEL 118, identical to the bare control), nothing but the projector.
So the parameters bear directly on `ddE(wall0)`, which is 0.44–0.82 kcal/mol in magnitude and sets
Dset's absolute value at n ≥ 5.

But §4 shows the charge-free term is the **smaller** of the two non-additivities. So parameter
sensitivity threatens **Dset's absolute value**, not DIAGNOSTIC 14's cooperativity conclusion. The
experiment worth pre-registering is still: how far does `ddE(wall0)` move when the ECP parameters
are varied across published alternatives? Wall-at-zero arms only, six position sets × two states ×
each parameter set. It needs real published parameter sets, which requires a literature pass first.

## 9. What is not affected

- **DIAGNOSTIC 22's result stands untouched.** Stability is independent of this decomposition.
- **The barriers stand.** ddE(bare) and the frozen barriers of 7.66–13.34 kcal/mol involve no
  wall0 term.
- **DIAGNOSTIC 3 stands**, including its INCONCLUSIVE verdict.
- **DIAGNOSTIC 14's verdict stands** and is strengthened (§4).
- The readable and stable domain boundaries stand: they rest on D6.3 classes and stability.

## 10. Labels

Every number is **measured from committed files**. The decomposition identity is exact by
construction and reproduces DIAGNOSTIC 16's committed `|signed sum|` and excess for both rows where
they are reported. §4's split into charge-mediated and charge-free non-additivity is **new and
exact**, not post hoc inference. §6's re-reading of D16 READING 1 is **post hoc** and not quotable
until pre-registered.
