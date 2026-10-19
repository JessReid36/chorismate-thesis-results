#!/usr/bin/env python3
"""
x_check.py C4DIR - C4's machinery check X, repeated from the committed files (C4_CRITERIA.txt: "every atom outside the
active region is where start.xyz put it (2e-6 A)"; in each job c4_extract.py checked it and printed extract=ok).
Reads, per run folder S*/ in C4DIR, reopt.xyz (ORCA's last full-system geometry) and start.xyz, and C4DIR/active_atoms.txt
(0-based indices). Prints one line: the number of runs and the largest coordinate change of an atom outside the active
region. Standard library; deterministic. Exit 1 if any run lacks a file, has the wrong atom count, or exceeds 2e-6 A.
"""
import glob, os, sys
C = sys.argv[1]
NATOMS = 55680
ACT = set(int(x) for x in open(os.path.join(C, "active_atoms.txt")).read().split())
def xyz(p):
    L = open(p).read().splitlines(); n = int(L[0].split()[0])
    R = [tuple(float(v) for v in l.split()[1:4]) for l in L[2:2 + n]]
    if n != NATOMS or len(R) != NATOMS: sys.exit("x_check: %s holds %d atoms, expected %d" % (p, len(R), NATOMS))
    return R
runs = sorted(d for d in glob.glob(os.path.join(C, "S*")) if os.path.isdir(d))
worst, where = 0.0, "-"
for d in runs:
    for f in ("reopt.xyz", "start.xyz"):
        if not os.path.isfile(os.path.join(d, f)): sys.exit("x_check: no %s in %s" % (f, d))
    R, S = xyz(os.path.join(d, "reopt.xyz")), xyz(os.path.join(d, "start.xyz"))
    m = max(max(abs(a - b) for a, b in zip(R[i], S[i])) for i in range(NATOMS) if i not in ACT)
    if m > worst: worst, where = m, os.path.basename(d)
print("X from the committed geometries: %d runs; largest coordinate change of an atom outside the active region %.1e A "
      "(limit 2e-6)" % (len(runs), worst))
sys.exit(1 if worst > 2e-6 else 0)
