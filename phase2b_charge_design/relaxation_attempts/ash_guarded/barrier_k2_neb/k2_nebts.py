import sys, openmm
from ash import Fragment, ORCATheory, OpenMMTheory, QMMMTheory, NEBTS

RUN = (len(sys.argv) > 1 and sys.argv[1] == "run")
ORCADIR = "/home/apps2/ORCA/6.0.1"

# --- converged K2 endpoints (reactant + product), 38 atoms each: 24 substrate + 14 surrogate ---
react = Fragment(xyzfile="k2_reactant.xyz", charge=-2, mult=1)
prod  = Fragment(xyzfile="k2_product.xyz",  charge=-2, mult=1)
print(">> endpoints: reactant %d atoms, product %d atoms" % (react.numatoms, prod.numatoms))

qmatoms = list(range(24))
guan_q = [0.64] + [-0.80,0.46,0.46]*3
form_q = [0.45,-0.80,-0.80,0.15]
mmcharges = [0.0]*24 + guan_q + form_q
LJ = {"C":(3.40,0.086),"N":(3.25,0.170),"O":(2.96,0.210),"H":(1.06,0.016)}
els = [l.split()[0] for l in open("k2_reactant.xyz").read().split("\n")[2:2+38]]

orca = ORCATheory(orcadir=ORCADIR,
                  orcasimpleinput="! B3LYP D3BJ def2-SVP def2/J RIJCOSX CPCM TightSCF",
                  orcablocks="%cpcm epsilon 4.0 end\n%scf MaxIter 300 Guess PModel end",
                  numcores=8, autostart=False)

# MM layer built on the REACTANT fragment (surrogate positions identical R and P -> field is fixed)
mm = OpenMMTheory(fragment=react, dummysystem=True, platform="CPU", numcores=1,
                  autoconstraints=None, rigidwater=False)
lj = openmm.CustomBondForce("4*eps*((sig/r)^12 - (sig/r)^6)")
lj.addPerBondParameter("sig"); lj.addPerBondParameter("eps"); lj.setUsesPeriodicBoundaryConditions(False)
ang=openmm.unit.angstrom; kcal=openmm.unit.kilocalorie_per_mole
for i in range(24):
    si,ei=LJ[els[i]]
    for j in range(24,38):
        sj,ej=LJ[els[j]]
        sig=((si+sj)/2*ang).value_in_unit(openmm.unit.nanometer)
        eps=(((ei*ej)**0.5)*kcal).value_in_unit(openmm.unit.kilojoule_per_mole)
        lj.addBond(i,j,[sig,eps])
lj.setForceGroup(11); mm.system.addForce(lj)
print(">> MM + LJ wall built")

qmmm = QMMMTheory(qm_theory=orca, mm_theory=mm, fragment=react,
                  qmatoms=qmatoms, charges=mmcharges, embedding="elstat",
                  qm_charge=-2, qm_mult=1, numcores=8)
print(">> QMMMTheory built | QM -2 | NEB-TS pilot")

# reacting atoms + first-shell neighbours for the partial Hessian on the TS
partial_H = [0,7,8,12, 3,4,10,13,17]   # C1,O3,C4,C6 + ring/carboxyl neighbours

if not RUN:
    print("\n=== DRY RUN OK (K2 NEB-TS) — endpoints loaded, QM/MM+LJ built. Re-run with 'run'. ===")
    sys.exit(0)

# ASH NEB-TS: CI-NEB then geomeTRIC eigenvector-following saddle refinement.
# ActiveRegion = QM atoms only (surrogates frozen); serial (QM/MM can't image-parallelize); ORCA parallelized.
result = NEBTS(reactant=react, product=prod, theory=qmmm,
               images=10, CI=True,
               ActiveRegion=True, actatoms=qmatoms,
               runmode='serial',
               printlevel=1)
print(">> NEB-TS done. Saddle energy:", getattr(result,'saddle_energy', 'see output'))
try:
    result.saddlepoint_fragment.write_xyzfile(xyzfilename="k2_ts.xyz")
    print(">> TS geometry -> k2_ts.xyz")
except Exception as e:
    print(">> (saddle fragment attribute differs; check output):", e)
