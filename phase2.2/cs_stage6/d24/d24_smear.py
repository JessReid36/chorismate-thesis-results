"""D24 (proposed): does a Gaussian-smeared external charge reduce the inter-basis
discrepancy in ddE that D4/D5 measured for bare point charges?

Real system: the committed 24-atom chorismate dianion at frame 42436, R and TS,
with three committed charge vectors spanning the measured domain:
  1.3000 e  inside  (D5 domain is Sum|q| <= 2.8800 e)
  2.8800 e  at the edge
  5.6433 e  outside, and above D20's 4.32 e instability onset

Quantity is the project's own: ddE = [E(TS,q) - E(TS,0)] - [E(R,q) - E(R,0)].
D3BJ is charge-independent at fixed geometry so it cancels exactly in ddE; its
absence here does not affect the comparison.
Metric: |ddE(def2-SVPD) - ddE(def2-SVP)|. D5's criterion is < 1.0 kcal/mol.
"""
import numpy as np, sys, time
from pyscf import gto, dft
from pyscf.qmmm import itrf

H2K = 627.5094740631

def read_xyz(p):
    L = open(p).read().split('\n'); n = int(L[0].split()[0])
    return '\n'.join(L[2:2+n])

def read_pc(p):
    L = [l for l in open(p).read().split('\n') if l.strip()]
    n = int(L[0].split()[0]); q = []; c = []
    for line in L[1:1+n]:
        f = line.split(); q.append(float(f[0])); c.append([float(x) for x in f[1:4]])
    return np.array(q), np.array(c)

GEOM = {'R': read_xyz('reactant_qm.xyz'), 'TS': read_xyz('transition_state_qm.xyz')}
VECS = [('1.3000e_n10', 'pc_1.3000e_n10.pc'),
        ('2.8800e_n10', 'pc_2.8800e_n10.pc'),
        ('5.6433e_n20', 'pc_5.6433e_n20.pc')]
MODELS = [('point', None), ('gauss0.25', 0.25), ('gauss0.50', 0.50), ('gauss1.00', 1.00)]
BASES = ['def2-svp', 'def2-svpd']

def run(basis, state, q=None, coords=None, radius=None):
    m = gto.M(atom=GEOM[state], basis=basis, charge=-2, spin=0,
              unit='Angstrom', verbose=0)
    mf = dft.RKS(m).density_fit(); mf.xc = 'b3lyp'; mf.conv_tol = 1e-8; mf.max_cycle = 200
    if q is not None:
        r = None if radius is None else np.full(len(q), radius)
        mf = itrf.mm_charge(mf, coords, q, radii=r, unit='Angstrom')
    e = mf.kernel()
    if not mf.converged:
        mf = mf.newton(); e = mf.kernel()
    return e, mf.converged

t0 = time.time()
print('=== bare references (no external charges) ===', flush=True)
bare = {}
for b in BASES:
    for s in ('R', 'TS'):
        e, ok = run(b, s)
        bare[(b, s)] = e
        print('  %-10s %-3s %.10f Eh  converged=%s  [%.0fs]' % (b, s, e, ok, time.time()-t0), flush=True)

print('\n=== ddE by charge vector, basis and charge model ===', flush=True)
print('%-14s %-10s %12s %12s %14s %s' % ('vector', 'model', 'ddE_SVP', 'ddE_SVPD', '|inter-basis|', 'conv'), flush=True)
results = {}
for vname, vfile in VECS:
    q, coords = read_pc(vfile)
    for mname, radius in MODELS:
        dd = {}; allok = True
        for b in BASES:
            vals = {}
            for s in ('R', 'TS'):
                e, ok = run(b, s, q, coords, radius)
                vals[s] = e; allok = allok and ok
            dd[b] = ((vals['TS'] - bare[(b, 'TS')]) - (vals['R'] - bare[(b, 'R')])) * H2K
        gap = abs(dd['def2-svpd'] - dd['def2-svp'])
        results[(vname, mname)] = (dd['def2-svp'], dd['def2-svpd'], gap, allok)
        print('%-14s %-10s %12.4f %12.4f %14.4f %s  [%.0fs]'
              % (vname, mname, dd['def2-svp'], dd['def2-svpd'], gap, allok, time.time()-t0), flush=True)
    print('-'*76, flush=True)

print('\n=== reduction in the inter-basis gap, smeared vs point ===', flush=True)
for vname, _ in VECS:
    pg = results[(vname, 'point')][2]
    print('  %s : point %.4f' % (vname, pg), flush=True)
    for mname, _ in MODELS[1:]:
        g = results[(vname, mname)][2]
        print('      %-10s %.4f   (%+.1f%%)' % (mname, g, -100*(1-g/pg) if pg else 0), flush=True)
print('\nD5 criterion for the defensible domain: |inter-basis| < 1.0 kcal/mol', flush=True)
print('total wall time %.0f s' % (time.time()-t0), flush=True)
