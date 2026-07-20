# Step 7b — Charge representation for relaxed-geometry validation: options tested and rejected

Bare external point charges cannot be used for relaxed geometry optimisation of this system
(see step 7: four of eight designs collapsed, a substrate oxygen reaching 0.879 A from a
designed +1). This note records what was tested as a replacement.

## Requirement

Any replacement must: supply Pauli repulsion so the approach stops at a physical distance;
preserve CPCM epsilon = 4 (every frozen-density number in Phase 2 uses it, so dropping it
breaks comparability); work for both Opt and OptTS with NumFreq; and not require inventing
parameters that cannot be defended.

## Rejected: QM/MM with Lennard-Jones parameters

ORCA aborts on input validation:
  "CPCM or SMD or ALPB or ddCOSMO or CPCMX requested together with QM/MM method.
   This is not implemented. ===> : Switch off solvation method."
Not lifted in ORCA 6.1. This was the preferred fix on physical grounds — MM sites carry both
a charge and LJ parameters, which is exactly the missing Pauli wall — but it is unavailable
while CPCM is required.

Incidental: ORCA's force field (ORCAFF.prms via orca_mm -makeff) uses UFF non-bonded
parameters. Verified against Rappe's published values: C 0.105/3.851, N 0.069/3.660,
O 0.060/3.500, H 0.044/2.886, all exact. The length column is R_min, not sigma.
orca_mm -makeff cannot generate a force field for free-floating charge sites: it runs an
internal xtb geometry optimisation which fails on disconnected atoms.

## Rejected: Gaussian-smeared or finite-width external charges

Not supported. The .pc format is strictly four columns (charge, x, y, z) with no width
field, and ORCA's Gaussian-charge machinery exists only inside CPCM for solvation cavity
surface charges. Unavailable in 6.0.1 and 6.1.

## Rejected: ghost atoms

Basis functions without electrons provide no Pauli repulsion — there is nothing to enforce
orthogonality against. They may worsen spill-out by giving the density additional variational
freedom centred on the attractive charge (the same mechanism as basis-set superposition
error). Not tested computationally; rejected on theory.

## Rejected: capped effective core potentials

ORCA supports coreless ECP embedding via the "Atom>" syntax, which the manual describes as
accounting for "otherwise neglected repulsive terms at the border". This is the mechanism
embedded-cluster methods use to prevent spill-out onto positive charges, and it is
CPCM-compatible, so it was the leading candidate.

Availability, tested against water: SDD and HayWadt are accepted for Na and Mg;
LANL2, CRENBL, def2-SD, dhf-ECP and SK-MCDHF-RSC are all rejected with
"Requested ECP not available for element".

The centre is genuinely electron-free. Water alone and water plus a capped Na centre both
report 10 electrons and basis dimension 24, so the cap adds neither electrons nor basis
functions.

However, a distance scan of the ECP contribution gives non-physical energies. Water with a
+1 at varying separation, capped minus bare, in Ha:

  d(A)     bare            capped
  4.0     -76.317116     -547.522507
  3.5     -76.316049     -350.734435
  3.0     -76.314503     -169.295330
  2.5     -76.312458      -96.163138
  2.2     -76.311187     -113.680865
  2.0     -76.310456     -222.908913
  1.8     -76.309828     -649.305068
  1.5     -76.308052    -5138.399414

The capped column is non-monotonic with a turning point near 2.5 A, is more negative at
larger separation over part of the range, and reaches thousands of Hartree for a three-atom
system. Two explanations were tested and eliminated: the SCF converges normally (DIIS error
1.25e-6 against a 1e-6 tolerance, ORCA TERMINATED NORMALLY), and the results are unchanged
under NoAutoStart with unique filenames, so they are not an artefact of a stale initial guess.

Working explanation, not independently confirmed: a stock SDD ECP is not a repulsive wall.
It replaces sodium's ten core electrons and is net attractive to valence density — that is
how it binds Na's own 3s electron. With no basis functions at the centre to accommodate that
density, the solute's tails are variationally drawn into an unbounded attractive hole.
Embedded-cluster practice uses purpose-built repulsive capping potentials or ab initio model
potentials, which ORCA's library does not ship. Making this route work would require custom
ECP parameterisation, which is out of scope.

## Rejected: increasing the standoff distance

Rejected on scientific rather than technical grounds. Excluding the inner grid shell would
place every designed charge beyond 4.19 A from any atom centre, while BsCM's own charged
residues sit at 2.63-3.43 A (Arg90 2.63, Lys60' 2.71, Glu78 3.08, Arg7 3.19, Arg63' 3.43).
A design space that excludes the region the enzyme actually uses makes the enzyme comparison
circular.

## Selected: molecular surrogates

Replace each designed unit charge with the real ionised group it represents:
methylguanidinium for +1, acetate for -1, placed in the QM region and Cartesian-frozen while
the substrate relaxes. This is standard practice in theozyme and QM-cluster enzyme modelling,
and for this system the surrogates are not analogies — Arg90's side chain is a guanidinium
and Glu78's is a carboxylate.

Advantages: real core electrons give genuine Pauli repulsion; the salt-bridge stopping
distance is physically correct (the structural consensus places Arg-carboxylate contacts at
2.6-3.0 A); CPCM works normally; no invented parameters.

Costs to disclose: additional electrons and basis functions, hence basis-set superposition
error (estimate by counterpoise); each surrogate requires an orientation to be chosen, which
is a genuine free parameter; and the interaction is no longer purely electrostatic, since the
surrogate polarises.

## Reframing that follows from this

The collapse is partly physical. A real guanidinium placed where a designed +1 sits should
pull a chorismate carboxylate into a salt bridge. The point-charge model is therefore valid
down to roughly 2.7 A and unphysical only below it. The objective is not to prevent inward
motion but to make it stop in the right place.

Protocol consequence: the bare reference barrier must be recomputed with the same surrogate
centres present and their charges neutralised, or the comparison conflates the design's field
with the mere presence of the surrogates.
