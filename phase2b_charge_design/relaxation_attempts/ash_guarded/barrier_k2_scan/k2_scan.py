import sys, openmm
from ash import Fragment, ORCATheory, OpenMMTheory, QMMMTheory, calc_surface

RUN = (len(sys.argv) > 1 and sys.argv[1] == "run")
ORCADIR = "/home/apps2/ORCA/6.0.1"

# canonical repo-verified reactant (relaxed under K2 field). Scan drives O3-C4 from reactant(1.43) to product(~5).
react = Fragment(xyzfile="k2_reactant.xyz", charge=-2, mult=1)
print(">> reactant %d atoms" % react.numatoms)

qmatoms = list(range(24))
guan_q=[0.64]+[-0.80,0.46,0.46]*3; form_q=[0.45,-0.80,-0.80,0.15]
mmcharges=[0.0]*24+guan_q+form_q
LJ={"C":(3.40,0.086),"N":(3.25,0.170),"O":(2.96,0.210),"H":(1.06,0.016)}
els=[l.split()[0] for l in open("k2_reactant.xyz").read().split("\n")[2:2+38]]

orca=ORCATheory(orcadir=ORCADIR,
                orcasimpleinput="! B3LYP D3BJ def2-SVP def2/J RIJCOSX CPCM TightSCF",
                orcablocks="%cpcm epsilon 4.0 end\n%scf MaxIter 300 Guess PModel end",
                numcores=8, autostart=False)
mm=OpenMMTheory(fragment=react, dummysystem=True, platform="CPU", numcores=1,
               autoconstraints=None, rigidwater=False)
lj=openmm.CustomBondForce("4*eps*((sig/r)^12 - (sig/r)^6)")
lj.addPerBondParameter("sig"); lj.addPerBondParameter("eps"); lj.setUsesPeriodicBoundaryConditions(False)
ang=openmm.unit.angstrom; kcal=openmm.unit.kilocalorie_per_mole
for i in range(24):
    si,ei=LJ[els[i]]
    for j in range(24,38):
        sj,ej=LJ[els[j]]
        lj.addBond(i,j,[((si+sj)/2*ang).value_in_unit(openmm.unit.nanometer),
                        (((ei*ej)**0.5)*kcal).value_in_unit(openmm.unit.kilojoule_per_mole)])
lj.setForceGroup(11); mm.system.addForce(lj)
qmmm=QMMMTheory(qm_theory=orca, mm_theory=mm, fragment=react, qmatoms=qmatoms,
                charges=mmcharges, embedding="elstat", qm_charge=-2, qm_mult=1, numcores=8)
print(">> QMMMTheory built | scan method")

if not RUN:
    print("\n=== DRY RUN OK (K2 relaxed scan O3-C4) ===")
    sys.exit(0)

# relaxed scan: drive O3-C4 (atoms 7,8) 1.45 -> 3.00 A in 0.1 steps; surrogates frozen (ActiveRegion=QM)
surf = calc_surface(fragment=react, theory=qmmm,
                    scantype='Relaxed', RC1_type='bond', RC1_indices=[7,8],
                    RC1_range=[1.45, 3.00, 0.10],
                    ActiveRegion=True, actatoms=qmatoms,
                    charge=-2, mult=1)
print(">> scan done:", surf)
