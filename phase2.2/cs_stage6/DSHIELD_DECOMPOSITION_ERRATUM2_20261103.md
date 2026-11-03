# DSHIELD_DECOMPOSITION_20261102.md — ERRATUM 2

**3 November 2026.** Corrects `phase2.2/cs_stage6/DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md`
E1.3. Neither the note nor ERRATUM 1 is edited. One correction, measured by DIAGNOSTIC 23.

## E2.1  The bound on the propagation factor is withdrawn

ERRATUM 1's E1.3 reads:

> "Running the zero-charge arm alone measures that change in `ddE(wall0)` and then assumes it
> reaches `d_shield` one for one — which is the hypothesis under test. The propagation factor is
> undetermined and lies between 0 and 1."

The withdrawal of the zero-charge-only design stands and is strengthened. **The bound does not.**
DIAGNOSTIC 23 measured the factor at both published alternative parameter sets over all seven
readable conditions:

```
He   -9.314, +0.235, +0.294, +0.413, +0.517, +0.704, +2.279
Ar   -1.542, -0.453, +0.088, +0.139, +0.155, +0.245, +0.613
```

`f = dd/dz = 1 − d(wall,raw)/dz` lies in [0, 1] only if the charged walled arm responds in the
same direction as, and no more strongly than, the zero-charge arm. At S6-2 under He the
zero-charge arm moves −0.0145 kcal/mol and the charged arm −0.1500, ten times as far; at S6-3
they move in opposite directions. The sign argument in E1.3 needed the magnitudes ordered too,
and they are not.

**Why the withdrawal is strengthened rather than merely preserved.** E1.3 withdrew the
zero-charge-only sweep because it would measure `dz` and assume `f`. Since `dz` is now known to
bound `dd` neither in magnitude nor in sign, no assumption about `f` could have rescued that
design. See `STAGE6_DIAGNOSTIC23_ERRATUM1_20261103.txt` E23.2 and E23.3.

## E2.2  What E1.2 gains

E1.2 recorded that the chargeless wall term is strongly basis-dependent, 5 to 19 times larger at
def2-SVPD than at def2-SVP with sign changes at two arrangements. DIAGNOSTIC 23 adds the
companion statement for the parameters: the term moves by −0.9608 to +0.4687 kcal/mol across the
two alternative published sets, and the charged arm moves independently of it. Both the basis and
the parameter set move this term by more than its own magnitude.

## E2.3  What is not corrected

E1.1's max\|q\| corrections and the decomposition itself are unaffected. Every ddE, raw
discrepancy, chargeless term and Dset in the note's own table stands as printed for the Ne
parameter set, which is what it reports. What DIAGNOSTIC 23 adds is that those Dset values are
parameter-set properties at the 37 to 42 per cent level, and that three of the four verdicts built
by comparing them across arrangements reverse under an alternative published set
(`STAGE6_D15_D16_NOTE1_20261103.txt`).
