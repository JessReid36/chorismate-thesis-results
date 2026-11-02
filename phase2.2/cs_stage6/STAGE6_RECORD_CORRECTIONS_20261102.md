# Stage 6: three corrections to the record

**2 November 2026.** Repository at `6e1ed18`. Every figure below is recomputed from the
committed raw files by `cs6_y47.py`; none is transcribed from a result file's rounded print
except where a correction is explicitly about that print. No pre-registration, criterion or
committed result file is edited by this note.

---

## C1  A margin computed from four-decimal prints instead of from the energies

DIAGNOSTIC 16 READING 3 asks whether the cooperativity grows with n. Its rule and its
figures, as `d16/DIAGNOSTIC16_RESULT.txt` prints them: excess at n = 20 of +0.1071,
excess at n = 10 of +0.1640, "difference in excess -0.0569 against tol
0.0500".

Subtracting the two printed excesses gives a margin of 0.0069. Recomputed
from the raw energies across the four trees that hold the arms:

```
n = 20 F2   signed sum -0.184836   Dset -0.291925   excess +0.107089
n = 10 A    signed sum -0.249866   Dsum 0.352089   Dset -0.413978   excess +0.164112
difference  -0.057022        margin against tol 0.0500 = 0.007022
```

**The margin is 0.0070 kcal/mol, not 0.0069.** The committed
result file is not wrong -- it prints a correctly rounded -0.0569 -- but any margin obtained
by subtracting its four-decimal prints inherits up to 1e-4 of rounding, which is 1.4 per cent
of the margin itself. Wherever this project has quoted 0.0069, the figure is
0.0070.

The three thin margins on which the arrangement-comparing verdicts rest, all from the
energies or from the files' own exact statements:

| verdict | rule | margin |
|---|---|---|
| D16 READING 1 "FALLS WITH n" | Dset monotone over n = 3, 5, 10, 20; tol max(10% of largest, 0.05) | 0.0068 (the n = 3 -> n = 5 step) |
| D16 READING 3 "COOPERATIVITY FALLS" | excess(n=20) - excess(n=10), tol 0.0500 | **0.0070** |
| D15 READING 1 "NOT BOUNDED" | Dset 0.4140 - Dsum 0.3521 = +0.0619, tol 0.0500 | 0.0119 |

The term subtracted to obtain these Dset values is 0.18 to 0.72 kcal/mol and, by
`DSHIELD_DECOMPOSITION_ERRATUM1_20261102.md` E1.2, moves by 0.5 to 0.8 under a change of
basis alone. All three verdicts should be reported as properties of this parameter set and
this basis until a both-arms parameter experiment has been run.

---

## C2  The 1.067 kcal/mol figure, and DIAGNOSTIC 12's verdict counts

**Where 1.067 comes from.** From `STAGE6_DIAGNOSTIC17_20261030.txt` onward the number is
called "DIAGNOSTIC 11.3's budget", but D11.3 states a *relative* rule, which D12 prints as:

> PASS means |d_shield| <= max(0.10 x |ddE bare|, 0.05 kcal/mol) - Diagnostic 11's

1.067 is that rule's value at D12 sites 1988 and 1991, where |ddE(bare)| = 10.6673. Both
sites are **VOID**: their walled result was disqualified and entered no fit. It is the
largest tolerance among the 13 voided sites, and not the largest in the table.

| verdict | sites | largest tolerance |
|---|---|---|
| FAIL | 20 | 1.564 at site 2330 (\|ddE bare\| 15.6416) |
| VOID | 13 | **1.067** at site 1991 (\|ddE bare\| 10.6673) |
| pass | 3 | 0.411 at site 2373 |

In prose files the number occurs exactly once before D17, in `sitescan/DIAGNOSTIC12_RESULT.txt`.
**Nothing in the record states that D17 took it from there, so the origin is located, not
documented.** Either way it is one voided site's ten per cent tolerance, not a pre-registered
absolute budget for a meaningful barrier change, and calling it a "budget" implies a
pre-registration that was never made. Where a fixed figure is wanted, it should be named as
"D12's largest voided-site tolerance, 1.067 kcal/mol" or replaced by D11.3's relative rule
applied to the arm in hand.

**The verdict counts.** The file's own summary line, immediately below its 36-row table,
reads `23 live, 3 pass, 20 fail, 13 voided`, and the table carries
36 rows. A review of this record reported "FAIL 12, VOID 13, pass 2" from a regex
that required a four-digit site identifier; that pattern matches only 27 of the
36 rows and drops every short identifier, including one of the three passes
(sites 2373, 55, 1043). The counts above are the file's
own. The 1.067 conclusion is unaffected: it survives a parse of all 36 rows.

---

## C3  The projector's inertness, and when the pseudopotential entered the record

**Inertness, over every walled output rather than thirty.** `ECP_BRIEF_20261102.md` reported
the Ne> centres contributing no basis functions and no electrons from DIAGNOSTIC 22's thirty
runs. Across every committed output whose input bears `NewECP`, compressed ones included:

| basis | basis functions | NEL | runs |
|---|---|---|---|
| def2-SVP    | 264 | 118 | 117 |
| def2-SVPD   | 402 | 118 | 258 |
| def2-TZVPD  | 682 | 118 | 28 |
| ma-def2-SVP | 328 | 118 | 256 |

558 uncompressed and 101 compressed outputs, **659 normally terminated
walled runs at three bases**, each basis count equal to that basis's own charge-free control
and NEL 118 throughout. The Stage 4b and 4c outputs are committed as `job.out.xz`
(167 of the 417 compressed outputs under `phase2.2/`); a scan that
reads only `job.out` sees 558 of them and misses def2-TZVPD entirely.

4 walled or Arm B runs did not terminate normally:

| file | ECP form | basis |
|---|---|---|
| `cs_stage4b/B_ecp_svp_q0/job.out.xz` | block %basis NewECP | def2-SVP |
| `cs_stage4b/B_ecp_svpd_q0/job.out.xz` | block %basis NewECP | def2-SVPD |
| `cs_stage4b/B_noecp_svp_qm1/job.out.xz` | no ECP | def2-SVP |
| `cs_stage4b/B_noecp_svp_qp1/job.out.xz` | no ECP | def2-SVP |

Stage 4b Amendment 1's commit message records all four: "four Arm B runs aborted (ORCA: no
ECP on a zero-charge or ECP-less Ne> centre)".

**Provenance.** 661 committed inputs under `phase2.2/` bear `NewECP`, with
1589 declarations -- 1577 inline on `Ne>` coordinate lines and
12 in block form inside `%basis` -- and **exactly one distinct
parameter block** in both forms. The block entered the record at:

```
483c142 2026-10-08 Charged sphere Stage 4b pre-registered: Arm A safe-region map for the bare sphere (2.674-3.50 A, q to +1, def2-SVP vs def2-SVPD); Arm B coreless ECP sphere (Ne-type, Marefat Khah 2020) at contact with controls - criteria in STAGE4B_CRITERIA.txt, committed before running (code 7797706) [retained-final]
```

in block form, on the Stage 4b pre-registration. The inline form that every later stage uses
arrived with Stage 4b Amendment 1. Any statement that the block "first appears" in
`cs_stage4b/B2_inline_svp_q0/job.inp` is an artefact of alphabetical ordering (`B2_` sorts
before `B_`), not of history.
