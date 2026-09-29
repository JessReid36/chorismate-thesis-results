# Solvation and the reference state: where the continuum belongs

Status: **decision note, not a decision.** Raises a question for the supervisor.
Written 2026-09-29. Every number below traces to a committed output file or to a
paper in `chorismate-refs`.

---

## 1. What the protocol uses now

Measured from the code repository, 2026-09-29.

| stage | script | environment | continuum |
|---|---|---|---|
| MD sampling | `step09b_tleap_build.sh` | explicit TIP3P, `solvatebox 10.0`, Na+, ff14SB + GAFF, periodic | none |
| reactant opt, scan, product opt, band | `step19a`, `run_scan.sh`, `step19c` | QM/MM electrostatic embedding, 55 680 atoms explicit, 1959 active of which **139 are TIP3P waters** | none |
| in vacuo reference | `s8_invacuo_new.pbs` | gas phase, 24 atoms, no MM charges | none |
| dv potential grid | `s7_additivity`, `s7b`, `s9_frame_sensitivity` | no protein, no explicit water | **CPCM eps = 4.0** |
| design barriers | `oracle/neb_pass.py`, `05d_shell_ladder/.../relax_barrier.py` | point charges as MM, `QMMMTheory`, `embedding="elstat"` | **CPCM eps = 4.0** |

`epsilon 4.0` is the only dielectric anywhere in the repository (67 occurrences,
no others). There is no eps ~ 78 calculation in the production pipeline.

So Phase 1 runs in explicit solvent with no continuum, and Phase 2 runs in a
continuum with no explicit solvent. The two phases do not share an environment.

---

## 2. What the reference-state diagnostic says

`phase2b_charge_design/02_singlepoints/refstate_diagnostic.pbs.out`, extended
2026-09-29 from two environments to three. Committed reactant and TS geometries,
no re-optimisation. Canonical check against the previously committed single
points: MATCH.

| basis | environment | barrier kcal/mol | HOMO(R) Eh | bound? |
|---|---|---|---|---|
| def2-SVP | vacuum | 17.905 | **+0.082179** | **NO** |
| def2-SVP | CPCM eps = 4 | 17.474 | -0.126365 | yes |
| def2-SVP | CPCM eps = 78.4 | 17.244 | -0.192726 | yes |
| def2-SVPD | vacuum | 17.995 | **+0.043788** | **NO** |
| def2-SVPD | CPCM eps = 4 | 17.535 | -0.157280 | yes |
| def2-SVPD | CPCM eps = 78.4 | 17.308 | -0.219268 | yes |

Three findings.

**The bare chorismate dianion is electronically unbound in vacuum at both basis
sets.** A positive HOMO energy means the highest occupied orbital lies above the
vacuum level. Diffuse functions reduce it (+0.082 to +0.044) but do not fix it.
Both continua bind it.

**The barrier is almost insensitive to the dielectric.** Relative to vacuum:
eps = 4 gives -0.431, eps = 78.4 gives -0.661 (def2-SVP). A twenty-fold increase
in dielectric buys a further 0.23 kcal/mol, and **65% of the whole continuum
effect is already present at eps = 4**. The entire span from vacuum to bulk
water is under 0.7 kcal/mol.

**That is despite enormous absolute solvation.** The reactant is stabilised by
-137 kcal/mol at eps = 4 and -182 at eps = 78.4. Almost none of it is
differential: the continuum stabilises reactant and transition state nearly
equally. This is why a continuum cannot be a source of catalysis, and why the
gas-phase reference gives sensible barriers despite the unbound dianion - the
unboundedness largely cancels in the difference.

**Basis sensitivity** is 0.090 (vacuum), 0.061 (eps = 4), 0.064 (eps = 78.4).
def2-SVP is adequate and the SVP / SVPD question is closed.

---

## 3. What the literature says

All from papers held in `chorismate-refs` and read.

**GOCAT never runs point charges and a continuum together.** In Dittner & Hartke
(`acs.jctc.8b00151`) COSMO defines the *target path*; the charges then reproduce
it "not with the COSMO implicit solvent but by our electrostatic GOCAT", and the
optimised charges "clearly mimic the surrounding that the continuum solvent model
provides". In Behrens & Hartke (`s11244-021-01486-1`) the enzyme case takes
crystal structure 1OH0, **removes all water molecules**, selects and caps 20
side chains near the active site, and runs QM/MM with OPLS-AA electrostatic
embedding - **no continuum at all**. The SN2 case uses 20 explicit acetone
molecules as the MM embedding, again with no continuum.

Phase 2 as it stands - point charges *plus* CPCM eps = 4 - matches neither
setting. A continuum alongside the charges supplies the same electrostatic
stabilisation the charges are being optimised to provide.

**Behrens & Hartke flag water removal as a deficiency of their own work**,
wanting "the inclusion of explicit water molecules, as recent studies have
suggested and reiterated their importance for catalytic pathways in, e.g., KSI."
Phase 1 already has 139 explicit waters in the active region.

**Solvent screens applied fields, and a continuum cannot represent it.** Dutta
Dubey, Stuyver, Kalita & Shaik (`jacs.9b13029`) find by MD plus QM/MM that an
applied field organises the solvent, which generates a counter-field opposing
it, giving partial-to-complete screening **proportional to solvent polarity**.
Catalysis emerges only once the applied field exceeds the opposing field of the
organised solvent; they conclude field-mediated catalysis is feasible in bulk
"especially for nonpolar and mildly polar solvents". Water is the most polar
case. A continuum responds isotropically and instantaneously and cannot show
this. **The small continuum number in section 2 is therefore not evidence that
water is harmless to a charge design - it is evidence that a continuum cannot
see the effect that matters.**

**Fully relaxed environments overstate stabilisation.** Li & Hartke
(`cphc.201300323`) note their globally optimised explicit water clusters give
energies "several kcal/mol below available literature data" because the approach
"inherently assumes instantaneous changes in the structure of the water
molecules", making their numbers lower bounds. Relevant to Phase 1 too: the
1959-atom active region relaxes at every NEB image.

---

## 4. The question for the supervisor

Removing the continuum and adding explicit water are **two separate decisions**
with different costs, and they interact.

Removing the continuum alone is well founded by GOCAT practice, but **cannot be
done in isolation**: the bare dianion is unbound in vacuum (section 2), so
designed charges would then be doing two jobs at once - binding the excess
electron density and catalysing the reaction. The optimiser cannot distinguish
them and would likely spend charges on the former.

Adding explicit water solves that and is what Shaik's screening result argues
for, but is a much larger change: every candidate evaluation acquires thousands
of mobile waters.

**Proposed sequencing, for discussion:**

1. **Retain CPCM eps = 4 while the charge-placement machinery is developed.** It
   binds the dianion, and its differential contribution is 0.43 kcal/mol - small
   enough to subtract as a stated constant rather than a confound.
2. **Move to explicit water for candidates actually evaluated**, reusing the
   Phase 1 QM/MM with designed charges replacing the protein's MM charges and
   the waters retained. This is Behrens & Hartke's own trajectory: abstract
   embedding first, real molecular environment second.
3. **Report designs against an explicit-water reference**, not a vacuum one.
   Experimentally the enzyme gives dG# 15.4 against 24.5 in water; Claeyssens
   2011 find 7.3 kcal/mol of TS stabilisation in the enzyme against 1.0 in
   water. Beating vacuum is not beating water.

**Phase 1 needs no change.** Its environment is already explicit-solvent QM/MM
with no continuum, which is the target setting.

**The in vacuo reference should stay as it is.** It is Claeyssens' convention and
preserves comparability; switching to eps = 78.4 would shift every `stab_TS` by
a uniform +0.66 kcal/mol (mean -4.79 to about -4.13) and change no conclusion.
What it needs is a stated caveat, not a change - see section 5.

---

## 5. For the write-up

Record, with the numbers:

- The in vacuo reference is a **gas-phase dianion that is electronically
  unbound**, HOMO +0.082 Eh at def2-SVP. The reference is retained because the
  unboundedness cancels between reactant and TS: the barrier changes by only
  0.66 kcal/mol from vacuum to bulk water. Claeyssens used the same gas-phase
  reference, so the convention is inherited, but it should be stated rather than
  left to be discovered.
- def2-SVP versus def2-SVPD changes the barrier by 0.06-0.09 kcal/mol across all
  three environments. The basis is adequate.
- `epsilon 4.0` is the only dielectric in the repository and has no written
  justification. It is the conventional protein-interior value; say so.

---

## 6. Open, not resolved

- **Where designed charges should sit relative to the CPCM cavity** while the
  continuum is retained. Nothing found in the held literature. Search terms:
  *point charges outside cavity continuum solvation PCM external charges
  screening artifact*.
- **How severely explicit water will screen a designed charge array.** Shaik's
  result is for a small Menshutkin system in bulk solvent under a uniform
  applied field, not for a localised charge array in an enzyme-like arrangement.
  The direction is established; the magnitude for this system is not.
- **Whether an explicit-water uncatalysed reference ensemble is affordable.**
  Claeyssens 2011 ran 24 water pathways. Scoping question for Phase 2.
