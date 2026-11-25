#!/usr/bin/env python3
"""AMENDMENT 13 NOTE 1: the numbers it gives, formed again from committed files.
usage: python3 note_numbers.py <results repository>
1. The Lennard-Jones term of the sphere for each design of D56: the sum of L_f42436.tsv over the design's
   sites (sites numbered from 0, which the committed first-order scores confirm), beside D56's ddE.
2. From the committed relaxations of 3 November (relax/): the imaginary modes of the last frequency block
   of each TS_opt2 output, and the nearest distance from a substrate atom to a sphere at the start and end."""
import csv, math, os, re, sys
S6 = os.path.join(sys.argv[1], "phase2.2/cs_stage6")
def col(p):
    v = []
    for l in open(p):
        if l.startswith("#") or not l.strip():
            continue
        v.append(float(l.rstrip("\n").split("\t")[-1]))
    return v
A, L = col(S6 + "/A_f42436_d33a.tsv"), col(S6 + "/L_f42436.tsv")
assert len(A) == len(L) == 2626
R = list(csv.DictReader(open(S6 + "/d56/DESIGNS.tsv"), delimiter="\t"))
S = {r["design"]: r for r in csv.DictReader(open(S6 + "/d56_survivors.tsv"), delimiter="\t")}
worst = 0.0
print("1. THE SHELL TERM OF EACH DESIGN OF D56 (kcal/mol)")
print("design      sum L    ddE SV     ddE SV + sum L   the design")
for r in R:
    s = [int(x) for x in r["sites"].split(",")]
    q = [float(x) for x in r["charges_e"].split(",")]
    worst = max(worst, abs(sum(A[i] * c for i, c in zip(s, q)) - float(r["first_order_score_kcal"])))
    sl = sum(L[i] for i in s)
    d = float(S[r["design"]]["ddE_SV_kcal"])
    print("%-10s %+.4f  %+9.4f  %+9.4f        %s" % (r["design"], sl, d, d + sl, S[r["design"]]["the_design"]))
print("largest difference between a first-order score formed here and the committed one: %.1e kcal/mol" % worst)
print()
print("2. THE RELAXATIONS OF 3 NOVEMBER (relax/)")
def xyz(p):
    t = open(p).read().split("\n")
    n = int(t[0])
    return [tuple(float(x) for x in l.split()[1:4]) for l in t[2:2 + n]]
for d in ("S6-C", "n10_A"):
    t = open(os.path.join(S6, "relax", d, "TS_opt2", "job.out")).read()
    blk = t.split("VIBRATIONAL FREQUENCIES")[-1]
    im = re.findall(r"^\s*\d+:\s+(-\d+\.\d+) cm\*\*-1\s+\*\*\*imaginary mode\*\*\*", blk, re.M)
    print("%s/TS_opt2: imaginary modes in the last frequency block: %s" % (d, ", ".join(im) if im else "none"))
for job in ("R_opt", "TS_opt2"):
    b = os.path.join(S6, "relax", "n10_A", job)
    st, en = xyz(b + "/combined.xyz"), xyz(b + "/job.xyz")
    ch = st[24:]
    d0 = min(math.dist(a, c) for a in st[:24] for c in ch)
    d1 = min(math.dist(a, c) for a in en[:24] for c in ch)
    print("n10_A/%s: %d spheres; nearest substrate atom to a sphere %.2f A at the start, %.2f A at the end" % (job, len(ch), d0, d1))
