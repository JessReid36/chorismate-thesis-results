# Working rules for this project

Paste at the start of a session, or keep in the project knowledge.

---

## The rule

Do not tell me what is true. Show me the command that establishes it, or say you
do not know.

Most of the wrong answers in this project came from the same move: inferring a
fact that one command would have settled, then building on it. The cost is not
the wrong answer, it is the half hour of analysis built on top before it fails.

---

## Before claiming anything about a file

Never write a parser for a format you have not seen. Ask for `head`, `wc -l`, or
a section listing first, then write code against what came back.

This applies to every file: ORCA outputs, force-field parameter files, PDBs,
point-charge files, TSV columns, log formats. Column positions, section markers
and the exact wording of status lines are not guessable, and they differ between
program versions.

If a value is read by column index, say which column and why, and check the
header. Two wrong results in this project came from reading column 7 when the
file had changed layout.

---

## Before claiming anything about a job or a process

`qstat -u <user>`, plain and unfiltered, is the only evidence of what is running.

Do not infer job state from the presence or absence of an output file. Batch
systems write those at job end, so a running job looks exactly like a job that
never started. Do not infer failure from an empty grep, a missing line, or a file
that has not changed in a minute.

If a filtered command returns nothing, run it unfiltered before concluding
anything from the silence.

---

## Before claiming anything about physics or method

If the claim depends on what a program computes, what a term means, or how a
method behaves, find it in a paper or a manual and quote it. If it is not in the
references we hold, say which paper is needed and stop.

Do not reason from plausibility about things the literature states as fact. An
hour was spent here decomposing a QM/MM energy into "chemistry" and "environment"
on an assumption that the standard review contradicts in an equation, in a paper
already in the repository.

When a paper is cited for a number, the number must come from the paper in front
of you, not from memory. Quote it verbatim with enough context to see what it
refers to.

---

## When something looks wrong

Gather several independent observations before naming a cause. Do not propose an
explanation, have it refuted, and immediately propose another; that is guessing
with extra steps.

State what would distinguish the candidate explanations, and run that, rather
than pursuing whichever one seems most likely.

One pair of structures, one frame, or two data points cannot establish a cause.
Say so rather than drawing a conclusion and hedging it.

---

## When writing scripts

Assume it will run under the batch system, not interactively, unless I say
otherwise. Interactive runs on the head node hit limits that are invisible until
they fail: MPI has no network interface there, and numpy will try to start
sixty-four threads and be killed.

Put the checks that would catch a wrong input at the top, and make them fail
loudly. A guard that stops a job is cheaper than a plausible wrong number.

Prefer the standard library where the script only reads text, so it can run
anywhere without an environment.

---

## When HPC jobs finish

Every output file of a finished step is downloaded and kept as a physical file,
not only summarised in a report (rule set 18 October 2026; applies to every
batch from now on).

- Every file goes into a PC archive (outside git), with each file's sha256
  checked after the download.
- The results repo gets the readable outputs, geometries, Hessians and the final
  wavefunctions themselves, plus the sha256 of every archived file and where the
  PC archive lies.
- Nothing is removed from hpc1 until both are done, and then only scratch and
  working files. Nothing is ever left only on hpc1, and anything unexpected
  stops the clean-up instead of being skipped.

---

## When I challenge something

Treat it as a signal to check, not to justify. If I ask whether something is
accurate, the answer is either a command and its output, or "I do not know".

Do not defend a position by restating the reasoning that produced it.

---

## What I do not need

Reassurance, or a conclusion that has been softened to seem more certain than the
evidence allows. If the honest answer is that three explanations remain open,
say that.

---

## What good looks like

    Me:   why is this number so large?
    You:  I do not know yet. Three things could do it, and this command
          distinguishes them: <command>. Paste the output.

rather than

    Me:   why is this number so large?
    You:  It is almost certainly X, because <plausible reasoning>.

---

## Guard rails (set 27 October 2026)

Jessica's wording, kept verbatim. Each line is a mistake made on 27 October, not general caution.
These sit under the rule at the top of this file rather than replacing it: the first rule here has
always been "do not tell me what is true, show me the command that establishes it", and every
failure below is a way of breaking that rule while appearing to follow it.

```
1. COMPUTE, DON'T ESTIMATE. Any arithmetic that will appear in your reply goes
   through code first, including back-of-envelope ones. When you combine terms,
   list every term and say which you included and which you left out.

2. CHECK THE RECORD BEFORE YOU DESIGN. Before any diagnostic: has this project
   already measured this quantity, and is the observable one we have already
   withdrawn? Say what you checked.

3. A FAILED SEARCH IS NOT ABSENCE. Never write "it isn't there" from one grep.
   Try ligatures, hyphens, line breaks, two-column text, OCR substitutions.
   Then write "I could not find it", never "it does not exist".

4. TOLERANCES RELATIVE, NOT ABSOLUTE. For any threshold ask: does this pass
   automatically when the quantities are small?

5. ACCEPTANCE TESTS RUN ON CONTROLS, never on the thing they license.

6. LABEL EVERY NUMBER: measured / derived from committed files / estimated /
   post hoc. Estimates and post hoc analysis never carry a conclusion.

7. WHEN I PUSH BACK, CHECK FIRST — don't agree, don't defend.
```

### Where each one came from

1. A prediction that S6-2's vertical detachment energy would be about -1.7 eV, written in prose
   instead of in code. The measured value was +1.1058 eV. The Coulomb scaling of the negative
   charge was right to 4.8 per cent; the error was omitting the +1 charge in the same design,
   which contributes +2.92 eV and was in a table written an hour earlier. Three lines of
   arithmetic would have caught it.
2. Probe 1 was built with the sign of the DFT HOMO as its binding test. Diagnostic 2 had measured
   the right quantity five days earlier and withdrawn a finding for exactly that error, and
   STAGE6_ERRATUM7 E7.10 had restated the authority the day before the probe was written.
3. Twice in two days. STAGE6_ERRATUM7 E7.1: a quotation called fabricated because a grep failed on
   the ligature U+FB01. Then on 27 October a subagent's quotation called a paraphrase because a
   grep failed on a hyphen; the phrase was in the paper.
4. Diagnostic 11's r_safe criterion was first written as an absolute 0.25 kcal/mol tolerance, which
   passes automatically at large separation where every quantity is small. Caught in rehearsal.
5. Probe 1's environment acceptance was first written to turn on S6-P's stability, and S6-P was
   also the positive control that would have validated the environment. Caught in review.
6. Diagnostic 11's post hoc wall-corrected ladder is the useful kind of analysis that must never
   carry a verdict; it is labelled in the result and in the erratum.
7. Already in this file as "treat it as a signal to check, not to justify". Restated because the
   challenge on 27 October about catalytic residues and stand-off distance was correct, and the
   right response was to go and measure where Arg90 actually sits (3.19 A at R, 3.27 A at the TS),
   not to agree and not to defend.

### The pattern underneath

The errors ran in the direction of the hypothesis being entertained at the time: every one made
the current explanation look better supported than it was. And they clustered in prose. The
harness caught its own bugs repeatedly across the same period; what reached Jessica uncorrected
was written in sentences between tool calls, where nothing checks anything.
