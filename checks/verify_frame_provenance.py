#!/usr/bin/env python3
"""Verify that every selected MD frame was extracted from the correct trajectory.

Why this exists: step12b_extract.sh on branches main/rebuild-cleanroom reads only
04_amber_md/10c_production/prod.nc and indexes it via np.memmap with NO bounds check,
so a frame index >= 20000 would silently return wrong coordinates. The tier1-realism
version routes indices >= 20000 into 10d_production_extend/prod_ext.nc correctly.

This check does not trust provenance prose. It measures the forming-bond C6-C1 distance
in each committed .rst7 and compares it with the value recorded in that frame's selection
manifest. A frame read from the wrong trajectory cannot reproduce its manifest distance.

Run from the results repo root:  python3 checks/verify_frame_provenance.py
Expected: 45 OK, 0 MISMATCH (15 from prod.nc, 30 from prod_ext.nc).
"""
import glob, math, os, sys

Q = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '05_qmmm')
FRAMEDIR = os.path.join(Q, '12_frame_selection', 'frames')
BOUNDARY = 20000          # frames in prod.nc; confirmed by 12b_nac_select.log
ATOM_I, ATOM_J = 6208, 6220   # the forming C6-C1 pair, 1-based AMBER indices
TOL = 0.006               # manifest values are printed to 3 dp
MANIFESTS = ['selection_manifest.tsv',
             'selection_manifest_nac_extra.tsv',
             'selection_manifest_ext_renumbered.tsv']

def read_rst7(path):
    L = open(path).read().split('\n')
    n = int(L[1].split()[0]); vals = []
    for line in L[2:]:
        s = line.rstrip('\n')
        for i in range(0, len(s.rstrip()), 12):
            t = s[i:i+12].strip()
            if t:
                try: vals.append(float(t))
                except ValueError: pass
        if len(vals) >= 3 * n: break
    if len(vals) < 3 * n:
        raise ValueError('%s: short read (%d of %d coords)' % (path, len(vals), 3*n))
    return [(vals[3*i], vals[3*i+1], vals[3*i+2]) for i in range(n)]

man = {}
for name in MANIFESTS:
    p = os.path.join(Q, '12_frame_selection', name)
    if not os.path.exists(p):
        print('WARNING: missing manifest %s' % name); continue
    for ln in open(p).read().strip().split('\n'):
        if ln.startswith('#') or not ln.strip(): continue
        c = ln.split('\t')
        if len(c) >= 6:
            try: man[int(c[1])] = (float(c[5]), name)
            except ValueError: pass

print('frames in manifests: %d   atom pair %d-%d   boundary %d\n'
      % (len(man), ATOM_I, ATOM_J, BOUNDARY))
print('%-8s %-10s %-10s %-9s %-12s %s' % ('frame','manifest','measured','diff','source','verdict'))
ok = bad = miss = 0
for fr in sorted(man):
    val, _ = man[fr]
    g = glob.glob(os.path.join(FRAMEDIR, 'frame_%05d_*.rst7' % fr))
    if not g:
        print('%-8d %-10.3f %-10s %-9s %-12s NO RST7' % (fr, val, '-', '-', '-')); miss += 1; continue
    c = read_rst7(g[0])
    m = math.dist(c[ATOM_I-1], c[ATOM_J-1])
    diff = m - val
    src = 'prod.nc' if fr < BOUNDARY else 'prod_ext.nc'
    v = 'OK' if abs(diff) < TOL else 'MISMATCH'
    ok += v == 'OK'; bad += v == 'MISMATCH'
    print('%-8d %-10.3f %-10.3f %+-9.3f %-12s %s' % (fr, val, m, diff, src, v))
n_ext = sum(1 for fr in man if fr >= BOUNDARY)
print('\nTOTAL: %d OK, %d MISMATCH, %d missing' % (ok, bad, miss))
print('extension-segment frames (>= %d) checked: %d' % (BOUNDARY, n_ext))
if bad or miss:
    print('\nFAIL - a frame does not match its manifest. Do not quote barriers from it.'); sys.exit(1)
print('PASS - every frame reproduces its manifest distance; extraction used the two-trajectory router.')
