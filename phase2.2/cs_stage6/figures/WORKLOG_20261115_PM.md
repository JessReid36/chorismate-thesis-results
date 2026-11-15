# Work log: the revision of 15 November 2026, evening

Third revision of `WRITEUP_CONSOLIDATED_20261111.md`. Built at results `21d631b0` and code `512eead`.
Asked for by Jessica at 19:48: enter the findings of the jobs that had just been pushed, and leave
out the results of the other session's job if there were issues with them, saying what the issues are.

## What was entered

- **D41** (results `6613cda3`): DLPNO-CCSD(T)/def2-SVPD barrier 22.8968 kcal/mol; shift to def2-TZVPD
  +0.9635, opposite in sign to all eight functionals; the order of the functionals against the
  benchmark differs between the two basis sets.
- **D37 Amendment 1** (results `9a3baa2d`): revDSD-PBEP86-D4 measured, 21.8414 and 21.4957; the two
  arms ran the same calculation.
- **D40** (results `6c6309af`): detachment energies. The bare dianion is bound under all eight
  functionals. With the charges of each of the five quotable arrangements present it is METASTABLE at
  both states. D40 withdraws nothing; the erratum and the decision are open.

## What was not entered, and why

- **D39** (results `21d631b0`, amendment `00438730`, reader code `512eead`), committed by another
  session. Read in full and reproduced arithmetically from its six raw outputs. Not entered, at
  Jessica's instruction. The questions are listed in Appendix A.8 without its numbers. The checker's
  new check 24 holds the line: no output or table of D39 may be a source, and a block that cites its
  result or amendment may hold no number that is not in another of its sources.

## Steps, in order

1. Fetched both repositories; fast-forwarded the working clones; made `--no-hardlinks` staging clones.
2. Ran the committed `make_figures.py` unchanged on the new commits: 327 controls, none failing; two
   tables changed (a new pair in F1; two run counts).
3. Found that the pool of reference barriers admitted runs by geometry, keyword line and absence of
   charges only, and that the monoanion runs of D39 and D40 were excluded only because the committed
   reader cannot parse an unrestricted output. Added a guard on what ORCA prints of the charge and the
   multiplicity. The guard removed no existing row.
4. Added to `make_figures.py`: the keyword of Amendment 1; D41 (table T11, controls C46 and C47); D37
   Amendment 1 (controls C50); the ninth row and two columns of F11; D40 (tables T12 and T13, figure
   F12, controls C48 and C49); derived values DV300 to DV379; three nodes of the decision tree and two
   changed statuses. 587 controls, none failing.
5. One control disagreed in its last digit on the first run: D41's R41.3 for PWPB95-D3BJ, printed
   -0.6937, came out -0.6936 from the raw energies. Cause: R41.3 is defined on the four-decimal
   barriers of d37.tsv. The comparison is now formed the way the record defines it. The same was done
   for D40's sum of orbital energy and detachment energy (CAM-B3LYP-D3BJ, +0.6568). Neither is an
   error of the record; both are noted in Appendix A.8.
6. Patched `sweep_pass1.py` and `sweep_pass2.py` for the new keyword; re-ran both (118 combinations,
   12112 files, 312 names).
7. Patched the document in four passes (header and sections 2, 3; sections 5, 6, 7; sections 8 to 11;
   the appendices). The patches and the scripts that apply them are kept outside the repositories.
8. Patched the checker: checks 21 to 24, five negative tests, the self-label of revDSD-PBEP86-D4, the
   widening of check 20, the expected commits.
9. Validated on the staging clones; rehearsed the bundle on fresh mirrors.

## Mistakes caught before delivery

- A sentence in section 5 said the record holds no RELIABLE arrangement of zero or positive net
  charge at the corrected level. It does: 8 of D31's 13 RELIABLE conditions. Found on the second
  reading, corrected, and those conditions became the test proposed under H9.
- Item 22 of section 6 called CAM-B3LYP-D3BJ third at def2-SVPD without saying "of the eight"; with
  Amendment 1's functional counted it is fourth. Reworded.
- Under H9, Probe 3's bound designs were first listed as evidence against; two of the three are net
  positive or neutral and are evidence for. Reworded, with Probe 3's own numbers.
- A negative test did not fire on its first run (the data-only label), because the new text carried
  the label twice. The text was changed so that one phrase carries it.

## Numbers given to Jessica in conversation earlier on 15 November and superseded here

Two post hoc numbers were computed in conversation from rounded inputs before this revision. From
unrounded inputs, as `make_figures.py` now does it: B3LYP-D3BJ/def2-SVPD minus the def2-TZVPD
benchmark is -5.5281 (given as -5.5280), and the largest change in a functional's distance between
the two basis sets is +2.2664 (given as +2.2663). Neither was committed anywhere.

## Owed after this revision

Listed in Appendix A.8 under "Owed, and not written".
