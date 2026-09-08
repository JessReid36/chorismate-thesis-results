# PHASE1_ENSEMBLE_NOTES.md

Running note for the Phase-1 barrier ensemble. Records what the multiple-frame
QM/MM calculation is for, what has been observed so far, and — deliberately —
what was hypothesised and did not survive testing.

---

## 1. Why the ensemble exists

The Phase-1 barrier of **+16.00 kcal/mol** (`phase1_system_dev/BARRIER_FINAL.md`)
is thoroughly established *as a property of frame 820*: three independent
determinations agree to 0.4 kcal/mol (OptTS 16.00, NEB-CI 15.94, relaxed scan
16.37), both endpoints are frequency-verified over 612 displacements, the saddle
carries one imaginary mode at −313.30 cm⁻¹, and the IRC connects the intended
basins.

What is *not* established by any of that is whether frame 820 is representative.
Those checks are precision, not accuracy: every one would pass identically if the
snapshot were unusual. The literature value the work is compared against
(Claeyssens et al. 2011, 11.3 kcal/mol for BsCM) is explicitly an **average over
multiple QM/MM pathways**, because a single path is not the observable. Frame 820
sits +3.3 kcal/mol above the experimental ΔH‡ of 12.7 with no error bar attached.

The step-12a frame selection had already chosen twelve catalytically competent
frames for exactly this purpose ("Claeyssens-style: N competent reactant frames
for multiple QM/MM paths → barrier distribution"). Only frame 820 was carried
through. Five more are now in progress.

**Scope decision.** Five frames, not twelve. The standard error falls as 1/√n, so
going from n=5 to n=12 improves the sem from roughly ±0.3 to ±0.2 kcal/mol —
against a barrier of 16 and a discrepancy of 3.3, that extra precision changes no
conclusion. The remaining six stay prepared on disk in case the spread turns out
to be large.

**Protocol per frame.** Reactant optimisation → 20-window restrained scan →
product optimisation → NEB-CI. The reduced-region TS optimisation, the
612-displacement frequencies and the IRC are **not** repeated: they exist once, on
frame 820, to establish that the saddle is genuine, and their result licenses the
shortcut — NEB-CI reproduced the fully characterised barrier to 0.06 kcal/mol on
that frame. The proxy is demonstrated on this system, not assumed.

---

## 2. Optimised reactant geometries — five frames plus 820

| Frame | break O3–C4 (Å) | form C1–C6 (Å) | Arg90–O13 at selection (Å) | form at selection (Å) |
|---|---|---|---|---|
| 820 | 1.464 | 3.251 | 3.130 | 3.220 |
| 2450 | 1.472 | 3.295 | 2.788 | 3.407 |
| 4085 | 1.465 | 3.329 | 2.791 | 3.149 |
| 5680 | 1.461 | 3.281 | 2.716 | 3.032 |
| 12485 | 1.484 | 3.155 | 3.130 | 3.461 |
| 19185 | 1.480 | 3.107 | 2.858 | 2.990 |

### Two solid observations

**The breaking bond is invariant.** 1.461–1.484 Å, a spread of 0.023 Å across six
independent MD snapshots. That is optimisation noise. The C4–O3 bond is not a
degree of freedom the enzyme varies.

**The active site imposes the near-attack distance rather than inheriting it.**
The forming C1–C6 distance spans 0.471 Å across the raw MD frames and 0.222 Å
after QM/MM optimisation — a **53% compression**. More directly, the correlation
between the selection-time forming distance and the optimised one is
**r = +0.073 (exact permutation p = 0.894)**, i.e. indistinguishable from zero:
whatever near-attack geometry a snapshot happened to have is erased by the
optimisation.

This is a Phase-1 result in its own right and supports the near-attack
conformation argument independently of any barrier. It is descriptive, not
inferential, and needs no significance test to stand.

### Retracted hypothesis — do not carry this forward

I proposed, on inspection, that Arg90 proximity was *not* setting the near-attack
distance, on the grounds that frames 820 and 12485 share an Arg90–O13 contact of
3.130 Å while sitting at opposite ends of the forming range (3.251 vs 3.155).

That was reading structure into scatter from two points. Exact permutation tests
over all 720 orderings, n = 6:

| relationship | r | p |
|---|---|---|
| Arg90 vs form (optimised) | −0.441 | 0.381 |
| Arg90 vs form (at selection) | +0.494 | 0.297 |
| form at selection vs form optimised | +0.073 | 0.894 |
| Arg90 vs break (optimised) | +0.398 | 0.414 |
| form optimised vs break optimised | −0.807 | 0.064 |

Nothing reaches significance. The only near-miss is form-versus-break, which is
the trivial anticorrelation expected as one bond forms while the other breaks.
**At n = 6 these data cannot distinguish any geometric relationship from noise**,
in either direction. The hypothesis is neither supported nor refuted; it is
untestable with this sample and must not appear in the write-up as either.

The correlation worth testing is barrier-versus-Arg90 once the barriers exist —
that is a different quantity, with a mechanistic prior from the literature, and
`step19b_collect.py` computes it. Even then, n = 6 will support at most a
qualitative statement.

---

## 3. What the +17.47 / +16.00 comparison actually measures

Both barriers use **identical geometries**: `provenance.tsv` shows the bare
single points were extracted from the same `18e` / `18c` / `18f` trajectories that
`BARRIER_FINAL.md` used, without re-optimisation. The only difference is the
environment — the full protein field versus CPCM at ε = 4.

Two consequences for how the numbers may be described:

**+17.47 is not a "no catalysis" reference.** It is the same enzyme-preorganised
substrate in a uniform continuum. Conformational preorganisation — which
Claeyssens values at 0.9–3.6 kcal/mol — is already spent inside it, because the
bare calculation starts from the pseudo-diaxial geometry.

**The difference isolates the structured field.** 17.47 → 16.00 = **1.47
kcal/mol** is the additional effect of the protein's structured electrostatics
over a uniform dielectric. It is *not* comparable to Claeyssens' 6.1, which
contrasts enzyme with explicit water, each substrate relaxed in its own
environment.

This reframing matters for the thesis claim. The design target is not "recover
the enzyme's 6 kcal/mol"; in this model the enzyme's structured-field
contribution is 1.47 kcal/mol, and the Route B result of 6.40–7.23 kcal/mol
already exceeds it on the same geometries against the same reference.

---

## 4. Literature comparison

| Source | Method | Enzyme | Reference |
|---|---|---|---|
| Claeyssens et al. 2011 | B3LYP/6-31G(d)/CHARMM27 | 11.3 (avg) | 17.4 (water) |
| Ranaghan et al. 2004 | B3LYP/6-311+G(2d,p)//6-31G(d)/CHARMM22 | 12.7–16.1 | — |
| Ranaghan et al. 2004 | MP2/6-31+G(d)//6-31G(d)/CHARMM22 | 7.4–11.0 | — |
| Experiment | ΔH‡ | 12.7 ± 0.4 | 20.7 ± 0.4 |
| This work, frame 820 | B3LYP-D3BJ/def2-SVP/CPCM(4), QM = 24 atoms | 16.00 | 17.47 (bare, CPCM 4) |

+16.00 sits inside Ranaghan's B3LYP window, at its top. Candidate reasons for
sitting above Claeyssens' 11.3, in order of likely importance: **single snapshot
versus an average** (the ensemble now under way tests this directly); D3BJ
dispersion, which Claeyssens did not use; ff14SB/GAFF/TIP3P versus CHARMM27; and
the reduced 102-atom movable region. None indicates an error.

**Outstanding:** the comparison to experimental ΔH‡ is not like-for-like. A
potential-energy barrier omits zero-point and thermal corrections. The frame-820
frequencies already exist, so this is arithmetic rather than new computation, and
it should be done before any comparison to 12.7 is quoted.

---

## 5. Open items

- [ ] Complete the five NEB-CI barriers; run `step19b_collect.py`
- [ ] Test barrier vs Arg90–O13 contact across the ensemble (qualitative at n=6)
- [ ] ZPE and thermal correction to frame 820, for a like-for-like ΔH‡ comparison
- [ ] Vacuum / def2-SVPD diagnostic on the bare reference, to establish whether
      the CPCM continuum or the absence of diffuse functions is carrying the
      +17.47 (four single points, seconds each)
- [ ] Decide whether the ensemble mean or frame 820 is quoted as *the* Phase-1
      barrier in the thesis, and state the choice explicitly
