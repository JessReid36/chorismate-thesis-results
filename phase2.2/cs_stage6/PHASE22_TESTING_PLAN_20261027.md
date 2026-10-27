# Phase 2.2 — consolidated testing plan (27 October 2026)

The reasoning behind the sequence of diagnostics from here. Not a criterion: nothing below binds
until it is committed as a dated amendment or pre-registration. `STAGE6_CRITERIA.txt` is not edited.

Every literature figure cited here was grep-verified against the full PDF in `chorismate-refs`.
Two claims that could **not** be verified are marked ⚠ and nothing rests on them.

## 0. What is being looked for

**One arrangement that is genuinely catalytic.** Not a demonstration that the optimiser ranks
arrangements correctly, and not that every n works. An arrangement that fails is a measurement.

Dittner's thesis Table 6.2 (p. 164; the table body does not extract as text and was read by OCR)
gives catalytic ratio against a threshold set by the uncatalysed path:

      method                n = 3     n = 10
      vdW translation       63.8 %    18.6 %
      distance translation  80.2 %    29.7 %
      ESP global            56.2 %     2.8 %
      ESP local             52.9 %     3.8 %
      random initialisation  0.0 %     0.0 %

Two consequences. Success rate **falls sharply with n** in the work this project is built on, so
S6-P catalytic and S6-20 anti-catalytic is the expected shape rather than an anomaly; at fixed
budget more charges is harder. And the **random null is empty** — 1000 initialisations per n, 461
and 349 scored, 0.0 % catalytic at both, best random at n = 3 reaching 444.7 against a 409.1
threshold — so a designed hit is meaningful provided our own null is built the same way.

That table is a Menshutkin reaction at PM7/PBE0 with a fitness bundling barrier and gradients. It
sets expectations; it is not a result about this system.

## 1. Why no design work proceeds yet

No trustworthy oracle. Five defects:

1. **Overpolarisation** — bare charges at 2.8-3.0 A with diffuse functions. Senn & Thiel, five
   corroborating sources. Hypothesis for this system; Diagnostic 11 tests it.
2. **CPCM is the wrong instrument** — settled, `STAGE6_AMENDMENT2_20261027.txt`.
3. **Unbound dianion** — **WITHDRAWN 27 October**, see `STAGE6_PROBE1_ERRATUM1_20261027.txt`. The
   HOMO sign is not the test. Diagnostic 2 committed the VDE on 22 October: -0.3167 eV at def2-SVP
   (metastable) but **+0.5123 eV at ma-def2-SVP (BOUND)** and +0.5013 at def2-SVPD. At the basis
   Stage 6 runs in, the bare dianion is bound and there was never a binding problem to solve. The
   condition the surrogate was FITTED in, def2-SVP, is the metastable one.
4. **Resonance hazard** from negative charges near a dianion (Dreuw & Cederbaum). Suggestive;
   monotone with sum of negative charge across three designs, but confounded with n.
5. **Additivity** — the surrogate is linear; D2's even(q) reaches 15-24 % at q = 1 and D10 implies
   ~129 % of the classical term at n = 20. Established in form, magnitude untested.

## 2. Sequence

      A1  charge model and minimum stand-off      Diagnostic 11      blocks everything
      A2  environment                              NO LONGER BLOCKING - see defect 3. Explicit water
                                                  is affordable (Probe 1: 84 atoms in 7m 24s) and
                                                  wanted on Shaik's screening argument, but a
                                                  gas-phase reference is defensible meanwhile.
      A3  positive control: Arg90                 mostly already satisfied; A3.4 is in D11
      A4  null distribution under the final oracle   decision O10 plus four amendments
      B1  additivity                              needs A1 and A2
      B2  refit a, then calibrate B               needs A1 and A2
      C   the search over n and B                 last

**A3, the positive control, is largely already in hand.** A +1 at Arg90's position lowers the
barrier (-7.68 at def2-SVP vac, -3.86 at ma vac); -1 at the same site raises it (+5.80, D2 C3); the
small-q response is linear (even/|odd| 1.0 % at q = 0.05). What was missing is the far-field zero,
A3.4, now the d1500 rung of Diagnostic 11.

**Benchmarks, verified.** Experiment gives dG# 15.4 kcal/mol in BsCM against 24.5 in solution, a
9.1 kcal/mol difference and 10^6 rate acceleration (b508181e); Claeyssens' B3LYP/6-311+G(2d,p)
reproduces it at 9.4 against 9.1 (B313759G Table 6). **9 kcal/mol is what the real enzyme buys.**
Burschowsky (pnas.1408512111) supplies the premise: "properly positioned active-site charges are
essential in this system and preorganization of the substrate in a reactive conformation
contributes relatively little to catalysis."

⚠ Two figures are NOT to be used as targets. pnas.1408512111's 5.9 kcal/mol for Arg90's
transition-state contribution is introduced with "suggest" and the next sentence records that "This
interpretation has been challenged by Hur and Bruice"; it is also an inference from kcat/Km, not a
fixed-geometry ddE. And STAGE6_CRITERIA.txt's note that Dittner's static designs reached 24-41 % of
his relaxed ones is recorded but not re-derived here: Table 7.1's barrier row was verified (static
16.23 and 13.32 against adaptive 11.00, 5.56 and 3.40, supporting a large gap) but the ratio needs
baselines from printed pp. 185, 192 and 195.

## 3. The budget is a second axis, not a detail

`STAGE6_CRITERIA.txt` states that B = 2.0 e^2 is "the code's default, NOT the calibrated B", and
`CHARGE_MODEL_DECISIONS.md` already lists calibration as pending. B is a GLOBAL sum-of-q-squared
constraint with per-site |q| <= 1: at n = 1 it cannot bind, at n = 2 two unit charges spend it
exactly, and from n = 3 up it binds, so more spheres means weaker spheres. S6-20's twenty charges
share sum q^2 = 2.05, averaging |q| = 0.32.

**"Not enough charges" and "not enough budget" are therefore different hypotheses, and the present
design cannot tell them apart.** Phase C scans n in {1,2,3,5,10,20} against B in {B, 2B, 4B}.

## 4. Controls register

      S6-C in every condition, every time        the reference moving under us
      C-A1.1 wall-only at each rung              the Pauli wall doing work of its own
      C-A1.2 classical plateau                   artefact against real polarisation
      C-A1.3 reproduction of D10's -3.857852     harness drift between sessions
      C-A1.4 the q = -1 arm                      the dianion resonance hazard
      C-A1.5 the def2-SVP repeat                 basis concealment of spill-out
      A3.4 a charge at 15 A                      an oracle that fails to return nothing
      Probe 1 acceptance on S6-C, not on S6-P    choosing an environment by a design's behaviour
      A4 null per (n, B), same oracle and grid   selection over many candidates
      Bonferroni across the 18 cells             multiplicity
      pre-committed confirmation count           confirmation becoming a second selection
      Stage 6 relaxation and G_add at confirmation   frozen-geometry artefacts
      GATE 0 byte-for-byte manifest              measuring something other than what was registered

## 5. Anti-false-positive protocol

1.  The oracle is fixed and validated before any design is scored.
2.  The null uses that same oracle AND grid, and runs before any design is called catalytic.
3.  The success criterion is numeric, pre-registered and multiplicity-corrected. With 18 (n, B)
    cells, a plain 1st-percentile bar in each gives a family-wise false-positive rate near 18 %;
    the corrected bar is the 0.056th percentile, the 6th best of 10 000 draws, holding it at 1 %.
4.  Every reported number comes from the oracle. The surrogate is a search heuristic and is never
    reported as a result.
5.  Selection and confirmation are separate; the confirmation protocol and the NUMBER of candidates
    confirmed are fixed in advance.
6.  Any change of condition invalidates the control and the null; both are re-run.
7.  No criterion is edited. Changes go in dated amendments.
8.  Every n and B tested is reported, including failures.
9.  Percentiles are reported alongside values.
10. **Arg90 is a control, not a discovery.** S6-P is a +1 charge at the position nature already
    uses; it validates the oracle and must never be presented as a de novo designed catalyst.
11. Acceptance tests run on controls, never on the designs they are meant to license.
12. A stopping rule exists. If no cell clears the criterion the result is "no catalytic arrangement
    found within this design space", which is a finding about frozen-path charge design and not a
    licence to widen the grid until something passes.

## 6. Review passes

Three passes were made over this plan before it was committed. They changed, among others: the
r_safe criterion, which was absolute and would have passed automatically at large separation where
every quantity is small; Probe 1's acceptance test, which was circular in choosing an environment by
S6-P's stability and then validating it with S6-P; the addition of the Bonferroni correction; and
the symmetric statement that **fixing the oracle may still leave the designs failing** — nothing
here is evidence that they work.
