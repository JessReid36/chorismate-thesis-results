# X.2 Representation of external charge

## X.2.1 Rationale

I designed the external environment as a set of discrete charged entities rather
than as a continuous field, following the electrostatic account of enzyme
catalysis given by Warshel *et al.* (2006), who attribute catalytic power to "the
preorganized electrostatic environment" of an active site and show that the
catalytic term vanishes "if the environment is randomly oriented toward the TS in
the absence of charge (as is the case in water)".

Warshel *et al.* (2006) also identify the cost of that arrangement, in a section
headed "The Cost of Electrostatic Preorganization Is Paid by the Folding Energy".
An enzyme holds its active-site groups in position by means of the protein fold.
A set of charges placed in free space has no equivalent constraint, which is the
reason the design developed in this thesis carries a second, neutral layer
supplying geometric confinement (Chapter Y).

I retained a charge layer, rather than relying on geometric confinement alone,
on the evidence of Burschowsky *et al.* (2014). They replaced the cationic
active-site Arg90 of *Bacillus subtilis* chorismate mutase with neutral
citrulline and reported a variant that "is a poor catalyst even though it
effectively preorganizes chorismate for the reaction", concluding that an active
site "which is only complementary in shape to a reactive substrate conformer, is
insufficient for effective catalysis".

## X.2.2 Embedding scheme

I treated the external charges by electrostatic embedding, in the classification
of Senn and Thiel (2009), who distinguish "mechanical embedding (model A),
electrostatic embedding (model B), and polarized embedding (models C and D)".
Mechanical embedding was unsuitable because, in that scheme, "the charges in the
outer region do not interact with the QM density, which is thus not directly
influenced (polarized) by the electrostatic environment", and the polarising
effect of the environment on the substrate is the quantity this work optimises.
Polarized embedding would additionally allow the environment to respond to the
substrate, which the designed entities considered here do not do. Senn and Thiel
(2009) describe electrostatic embedding as "the most popular embedding scheme in
use today, certainly for biomolecular applications".

## X.2.3 Electron spill-out

A point charge carries no electron density and therefore exerts no Pauli
repulsion on the quantum subsystem. Laio *et al.* (2002) describe the
consequence: "positively charged classical atoms can act as traps for the
electron if the basis set is flexible enough to allow for this. In fact, the
Pauli repulsion from the electron cloud that would surround the classical atoms
is absent, and therefore, the electron density is over-polarized, at short range,
by an incorrect purely attractive potential, giving rise to the so-called
electron spill-out problem."

The effect is not attributable to field strength. A spherically symmetric charge
distribution produces, at every point outside itself, the field of a point charge
of equal magnitude at its centre. Conferring spatial extent on a charge therefore
alters the short-range interaction with the quantum density without altering the
field imposed on the substrate.

Basis-set extension does not remedy the problem. Laio *et al.* (2002) report that
the effect "can be of relevance also in schemes using localized basis sets,
especially if extended basis sets with diffuse functions are used", and that "the
unphysical nature of the interaction is present at any level of description, and
is doomed to get worse if the basis set is extended". A result that persists
under basis extension is therefore not, on that evidence alone, free of the
artefact.

Senn and Thiel (2009) record the accepted remedy as repulsive rather than
electrostatic, citing Lennard-Jones radii "5-10 % larger than those of the
underlying force field", where "the resulting increased repulsion compensates for
the too strong QM-MM electrostatic attraction which arises from overpolarization
at the boundary".

Spill-out therefore sets the criterion against which the available
representations are assessed in X.2.4: whether the representation excludes the
quantum density from the immediate neighbourhood of the charge.

## X.2.4 Available representations

A charged entity may be introduced into an ORCA calculation by several routes,
differing in whether the entity is treated quantum-mechanically, whether it
excludes the substrate density, and how its charge is distributed in space. I
enumerate them here before selecting among them in X.2.5.

ORCA 6.0.1 provides two native mechanisms for external charge. The first declares
charges as pseudo-atoms in the coordinate block, whereupon the program treats
them "as atoms with no basis functions and nuclear charges equal to the 'Q'
values". The second reads them from an external file specified by
`%pointcharges`, in which each line gives "the magnitude of the point charge (in
atomic units) and its position (in Ångström units)" (ORCA 6.0 manual, §7.2.4).
Neither accepts a width, radius or other parameter conferring spatial extent, so
a charge introduced by either route is a mathematical point and is subject to
spill-out. Spatial extent enters only through the QM/MM interface, in which an
environment particle carries Lennard-Jones parameters alongside its charge; the
force-field parameters for this work are held in `complex_solvated.ORCAFF.prms`.
A charged entity may also be placed in the quantum region itself, in which case
no embedding approximation applies. Separately, ORCA supports a uniform external
electric field for single points, geometry optimisations and transition-state
searches (Neese, 2025).

Six representations follow, summarised in Table X.2.1.

**Table X.2.1** Representations of a designed charged entity, assessed against
the spill-out criterion of X.2.3 and against the monopole objective defined in
X.4. Degrees of freedom are per placed entity. Of the six, only the
quantum-region entity polarises in response to the substrate; the remainder are
rigid. Cost is negligible for representations 1, 2 and 6, low for 3 and 4, and
high for 5.

| # | Representation | Field produced | Excludes QM density | DOF | Monopole exact |
|---|---|---|---|---|---|
| 1 | Point charge | monopole | no | 3 | yes, at fixed density |
| 2 | Point-charge shell | monopole outside shell | no | 3 | yes, outside shell |
| 3 | Charged sphere | monopole outside σ | yes, beyond σ | 3 | yes, outside σ |
| 4 | Molecular surrogate | monopole, dipole, higher | yes | 6 | no |
| 5 | Quantum-region entity | exact | yes, exactly | 6 | no |
| 6 | Uniform field | uniform, unbounded | not applicable | 3 (vector) | not applicable |

The ORCA mechanism realising each is given in the preceding paragraph:
representations 1 and 2 use `%pointcharges` or `Q` pseudo-atoms, 3 and 4 the
QM/MM interface with `complex_solvated.ORCAFF.prms`, 5 the quantum region itself,
and 6 the external-field keyword.

A **point charge** (1) places the full charge at a single position without a
repulsive term. It produces a monopole field and admits an exactly defined
first-order interaction energy, and it is subject to spill-out as described in
X.2.3.

A **point-charge shell** (2) distributes the same total charge over many points
arranged on a sphere. Outside the shell its field is that of a point charge at
the centre, by the same argument as for a continuous distribution. It does not
solve the spill-out problem, because each constituent point remains a bare charge
and the substrate density may still collapse onto any of them; it only moves the
individual singularities outward. I record it because it is the natural attempt
to build spatial extent from the native mechanism alone, and because its failure
to remedy spill-out establishes that the Lennard-Jones term, rather than the
spatial distribution of charge, is what is required.

A **charged sphere** (3) is a single QM/MM particle carrying charge *q* together
with Lennard-Jones parameters σ and ε. Outside σ its field is that of a point
charge of magnitude *q* at the particle centre, and the quantum density is
excluded from the region in which spill-out occurs. Treating such a particle as
its monopole is therefore exact at every point outside σ. The equivalence holds
outside the sphere; at the standoff distances used in this work the substrate
density extends into the region the sphere occupies, so the equivalence is close
rather than exact, and the residual is quantified in X.4.

A **molecular surrogate** (4) represents a guanidinium or carboxylate group as
several QM/MM sites carrying charges and Lennard-Jones parameters. Its field is
not that of a monopole at any single point, it carries a dipole and higher
moments, and its orientation adds three degrees of freedom to each placement.
Beker and Sokalski (2016) compared atomic point-charge and cumulative atomic
multipole descriptions of an enzyme active site and found that, although point
charges performed "reasonably well" for their system, "the difference between
these two models is not systematic, and there is thus no simple correction term
that can be applied to the point-charge calculation to improve the correlation to
the experimental values".

A **quantum-region entity** (5) places the charged group inside the QM region, so
that it carries real electrons, exerts real Pauli repulsion, and polarises in
response to the substrate. No embedding approximation applies, and it is
therefore the reference against which the accuracy of representations 1 to 4 is
properly judged. It also changes the electron count and total charge of the
quantum system, raises the cost steeply with the number of entities placed, and
offers no monopole description at all, so it is unsuited to a screen over many
candidate arrangements.

A **uniform field** (6) imposes a direction and magnitude without occupying a
position. It admits no placement problem, no candidate grid and no combinatorial
search, and so stands apart from the other five. Shaik *et al.* (2016) review
oriented external fields as a catalytic strategy, including the selection between
competing product channels by field orientation relative to the reaction axis.

A seventh option, a charge of finite width represented by a Gaussian rather than
a point, is not available for external charges in ORCA 6.0.1. The program applies
Gaussian charges to the apparent surface charges of the continuum solvation model
(García-Ratés and Neese, 2020), but the mechanism is specific to the cavity
surface and is not exposed for arbitrary external charges.

## X.2.5 Representations selected

I assessed the six representations against four requirements: that the entity
exclude the substrate density, so that any observed polarisation is physical
rather than an artefact of the representation (X.2.3); that its field be
describable by a monopole, so that the screening objective of X.4 is exact for
it; that its placement be tractable over a candidate grid, which excludes
representations whose cost scales steeply or which add orientational degrees of
freedom; and that it correspond to an entity that could plausibly exist in a
designed host.

No single representation satisfies all four. The point charge satisfies the
monopole and tractability requirements but not density exclusion; the molecular
surrogate satisfies density exclusion and plausibility but not the monopole
requirement; the quantum-region entity satisfies every requirement but
tractability. I therefore carried three representations forward, each answering a
different requirement, together with the uniform field as a comparator.

**Point charge, as reference case.** This is the representation for which the
objective of X.4 is exactly the first-order interaction energy, and against which
the others are measured. Its susceptibility to spill-out makes it unsuitable as a
design target but well suited to establishing what the objective predicts in the
absence of any repulsive term.

**Charged sphere, as working representation.** This preserves the exactness of
the monopole description outside σ while excluding the quantum density from the
region in which spill-out occurs, at three degrees of freedom per entity and
negligible additional cost. It is the representation on which the design
screening is performed.

`[DECISION REQUIRED — the Lennard-Jones radius σ for the charged sphere. Options:
(a) adopt the σ of a monatomic ion of comparable charge from the force field in
use; (b) adopt the σ of the carbon centre of the guanidinium surrogate, so that
sphere and surrogate present the same closest approach; (c) treat σ as a scanned
parameter. Option (a) is defensible but arbitrary; (b) makes sphere and surrogate
directly comparable; (c) costs a sweep. The choice sets the innermost usable
standoff and therefore constrains the shell range in X.3.]`

**Molecular surrogate, as validation representation.** This is the only carried
representation corresponding to a group that could exist in a designed host. The
error it introduces into a monopole-based ranking is not correctable by a fixed
offset, following Beker and Sokalski (2016), and is therefore recovered by
explicit verification of top-ranked candidates rather than by adjusting the
score.

**Uniform field, as comparator.** This establishes what an unstructured field
achieves for this reaction, against which a spatially structured arrangement can
be judged.

I did not carry the point-charge shell forward, on the grounds that it reproduces
the spill-out behaviour of a single point charge without conferring any
compensating advantage over the charged sphere. I did not carry the
quantum-region entity forward as a design representation, on grounds of cost,
although it remains available as an accuracy reference should the embedding
approximations of representations 1 to 4 be questioned.

`[DECISION REQUIRED — whether to compute a quantum-region reference for a single
placed entity. Placing one guanidinium in the QM region at a designed site, and
comparing the resulting barrier change against the same entity represented as a
charged sphere and as a molecular surrogate, would bound the embedding error
directly rather than by argument. Cost is one QM/MM calculation with an enlarged
quantum region per geometry. Not required for the screen, but it is the only
route to a quantitative statement about how much the embedding approximation
costs.]`

## X.2.6 Constraints imposed by a dianionic substrate

The substrate carries a net charge of −2 (X.1). Dreuw and Cederbaum (2002)
identify the characteristic instability of small multiply charged anions as
mutual repulsion of the excess charges, which "supports the dissociation of the
molecular framework into two monoanionic fragments".

Two consequences follow for the design. An arrangement acting differentially on
the two carboxylate groups opposes the charge separation that stabilises the
dianion, so dissociation along the framework separating them is the expected mode
of failure under a strong field. Separately, a cation placed near the substrate
stabilises its excess charge while an anion destabilises it, an asymmetry that a
difference-based objective does not measure, since such an objective compares two
states of the substrate rather than assessing whether the substrate is retained.
Both points are recorded here as properties of the substrate. Their consequences
are reported in Chapter Z.

## X.2.7 Pipeline of Operations

`[FIGURE X.2.1 — flowchart of the representation decision. Three parallel
branches from "designed charge entity": point charge → ORCA `.pc` file → no
Pauli wall; charged sphere → QM/MM particle (q, σ, ε) → wall at σ; molecular
surrogate → multi-site QM/MM group → wall plus orientation. A fourth, separate
branch for the uniform field bypassing placement entirely. Annotate each branch
with whether the monopole objective of X.4 is exact for it. No data file
required; this is a schematic.]`

- `design_maxlower_K1.pc` … `design_maxlower_K4.pc` — ORCA point-charge files, one
  line per charge giving magnitude in atomic units and position in Ångström.
  Consumed by `%pointcharges`. These implement the point-charge representation
  and carry no Lennard-Jones term.
- `complex_solvated.ORCAFF.prms` — ORCA force-field parameter file holding the
  charges and Lennard-Jones parameters for all molecular-mechanical sites.
  Supplies the σ and ε that realise a charged sphere or a molecular surrogate.
- `place_surrogates.py` — places a molecular surrogate at a designed grid point
  with its charged terminus oriented toward the substrate centroid. Outputs the
  surrogate coordinates and the corresponding force-field assignment.
- `sp_reactant.inp`, `sp_ts.inp` — ORCA single-point inputs for the unperturbed
  substrate at the reactant and transition-state geometries. Output `.gbw` and
  `.densities` files supply the wavefunctions from which the difference potential
  is evaluated in X.4.

`[PLACEHOLDER — needs sourcing: no committed input file yet implements the
charged-sphere representation. The point-charge and molecular-surrogate routes
are both realised in committed files, but a single QM/MM particle carrying charge
and Lennard-Jones parameters has not been constructed. This should exist before
X.2.5 describes it as the working representation.]`

---

## References

Beker, W. and Sokalski, W.A. (2016) 'Rapid estimation of catalytic efficiency by
cumulative atomic multipole moments: application to ketosteroid isomerase
mutants', *Journal of Chemical Theory and Computation*.
doi:10.1021/acs.jctc.6b01131.

Burschowsky, D., van Eerde, A., Ökvist, M., Kienhöfer, A., Kast, P., Hilvert, D.
and Krengel, U. (2014) 'Electrostatic transition state stabilization rather than
reactant destabilization provides the chemical basis for efficient chorismate
mutase catalysis', *Proceedings of the National Academy of Sciences*, 111(49),
pp. 17516–17521. doi:10.1073/pnas.1408512111.

Dreuw, A. and Cederbaum, L.S. (2002) 'Multiply charged anions in the gas phase',
*Chemical Reviews*, 102(1), pp. 181–200. doi:10.1021/cr0104227.

García-Ratés, M. and Neese, F. (2020) 'Effect of the solute cavity on the
solvation energy and its derivatives within the framework of the Gaussian charge
scheme', *Journal of Computational Chemistry*, 41(9), pp. 922–939.
doi:10.1002/jcc.26139.

Laio, A., VandeVondele, J. and Rothlisberger, U. (2002) 'A Hamiltonian
electrostatic coupling scheme for hybrid Car–Parrinello molecular dynamics
simulations', *Journal of Chemical Physics*, 116(16), pp. 6941–6947.
doi:10.1063/1.1462041.

Neese, F. (2025) 'Software update: the ORCA program system—version 6.0', *WIREs
Computational Molecular Science*, 15(2), e70019. doi:10.1002/wcms.70019.

Senn, H.M. and Thiel, W. (2009) 'QM/MM methods for biomolecular systems',
*Angewandte Chemie International Edition*, 48(7), pp. 1198–1229.
doi:10.1002/anie.200802019.

Shaik, S., Mandal, D. and Ramanan, R. (2016) 'Oriented electric fields as future
smart reagents in chemistry', *Nature Chemistry*, 8(11), pp. 1091–1098.
doi:10.1038/nchem.2651.

Warshel, A., Sharma, P.K., Kato, M., Xiang, Y., Liu, H. and Olsson, M.H.M.
(2006) 'Electrostatic basis for enzyme catalysis', *Chemical Reviews*, 106(8),
pp. 3210–3235. doi:10.1021/cr0503106.

---

## Sourcing gaps

1. **Charged-sphere implementation.** No committed file constructs a single QM/MM
   particle carrying charge and Lennard-Jones parameters. X.2.5 describes this as
   the working representation on the strength of an argument, not a calculation.
2. **The Lennard-Jones radius σ.** Undetermined; flagged as
   `[DECISION REQUIRED]` in X.2.5. It sets the innermost usable standoff and
   therefore constrains the shell range chosen in X.3.
3. **Sphere-to-point equivalence residual.** X.2.5 states the equivalence is
   approximate at the standoff distances used but does not quantify the residual.
   Deferred to X.4.
4. **ORCA manual as a citation.** §7.2.4 is the authoritative statement of the
   point-charge file format, but a software manual is a weak reference. If a
   published description of ORCA's point-charge handling exists it should replace
   this.

## Inconsistencies found

1. **Imaginary-mode count.** `05_qmmm/18c_reduced_region/ts_frequencies_summary.txt`
   tabulates two imaginary modes, −313.30 and −18.65 cm⁻¹, while the header of
   that same file and `phase1_system_dev/BARRIER_FINAL.md` both state "one
   imaginary mode". `WRITEUP_INDEX.md` records the discrepancy as unreconciled.
   Not cited in X.2, but it bears on the transition-state characterisation
   referenced from X.1.
2. **Surrogate correlation r = −0.839.** Asserted in
   `phase2_charge_design/REACTANT_CONFORMER_DECISION.md`, a prose note in the
   superseded development tree, with no committed dataset behind it.
   `WRITEUP_INDEX.md` lists the constrained-geometry re-test as outstanding. I
   have not cited the value in X.2, and the argument for screening at fixed
   geometry is stated in X.4 on other grounds.

## Verification log

No barrier is quoted in X.2. The only numerical claims are the Lennard-Jones
radius increase of "5–10 %" and the charge of −2, both quoted directly from Senn
and Thiel (2009) and from X.1 respectively.
