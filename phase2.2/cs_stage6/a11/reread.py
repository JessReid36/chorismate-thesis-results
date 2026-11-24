#!/usr/bin/env python3
"""The re-read of 24 November 2026 behind AMENDMENT 11: every job.inp and job.out under phase2.2/cs_stage6 is read from
its own text, no report is read. A run shows a SIGN if, against the charge-free run of its level and state, the largest
Loewdin charge on an atom rises by 0.25 e or more, the dipole is 2 times the control's or more (bare runs only: ORCA
counts a walled charge as a nucleus in the dipole), the grid's count of electrons is off by more than 0.02 e, the last
stability analysis is unstable, or more than 0.25 e has left the 24 atoms. These thresholds are Claude's, close to the
committed classifier's and not the same; where they differ from a committed verdict the committed verdict governs.

usage: python3 reread.py <results repo>
"""
"""Index every run under cs_stage6 from its own input and output files (no report is read)."""
import os, re, sys, json, math
S6 = os.path.join(os.path.abspath(sys.argv[1]), "phase2.2", "cs_stage6")
def parse(d):
    inp = open(os.path.join(d, "job.inp"), errors="replace").read()
    r = dict(dir=os.path.relpath(d, S6))
    m = re.search(r"^!(.*)$", inp, re.M); r["bang"] = " ".join(m.group(1).split()) if m else ""
    m = re.search(r"^\*\s*(xyzfile|xyz)\s+(-?\d+)\s+(\d+)\s*(\S*)", inp, re.M)
    r["chg"], r["mult"] = (int(m.group(2)), int(m.group(3))) if m else (None, None)
    geom = inp
    if m and m.group(1) == "xyzfile":
        p = os.path.join(d, m.group(4))
        geom = "\n".join(open(p).read().split("\n")[2:]) if os.path.isfile(p) else ""
    atoms, wall, ghosts, qs = [], [], [], []
    for l in geom.split("\n"):
        f = l.split()
        if len(f) >= 4 and re.fullmatch(r"[A-Z][a-z]?", f[0]):
            try: atoms.append((f[0], float(f[1]), float(f[2]), float(f[3])))
            except ValueError: pass
        elif len(f) >= 5 and re.fullmatch(r"[A-Z][a-z]?>", f[0]):
            wall.append((f[0][:-1], float(f[1]), float(f[2]), float(f[3]), float(f[4])))
        elif len(f) >= 4 and (f[0].endswith(":") or (len(f) > 4 and f[1] == ":")):
            ghosts.append(l.strip()[:60])
        elif len(f) >= 5 and f[0] == "Q":
            qs.append((float(f[1]), float(f[2]), float(f[3]), float(f[4])))
    m = re.search(r'%pointcharges\s+"([^"]+)"', inp)
    if m and os.path.isfile(os.path.join(d, m.group(1))):
        L = open(os.path.join(d, m.group(1))).read().split("\n")[1:]
        for l in L:
            f = l.split()
            if len(f) >= 4: qs.append(tuple(float(x) for x in f[:4]))
    sub = atoms[:24]
    ch = [(w[1], w[2], w[3], w[4], w[0]) for w in wall] + [(q[0], q[1], q[2], q[3], "") for q in qs]
    def nd(p): return min(math.dist(p, a[1:]) for a in sub) if sub else None
    r["natom"] = len(atoms); r["extra_atoms"] = [a[0] for a in atoms[24:]]
    r["ghost"] = len(ghosts) + len(re.findall(r"NewGTO|newgto", inp)) 
    r["charges"] = [(round(c[0], 4), round(nd(c[1:4]), 3) if sub else None, c[4]) for c in ch]
    r["wall"] = sorted(set(w[0] for w in wall)); r["nwall"] = len(wall)
    r["geomkey"] = "%.3f" % sub[0][1] if sub else ""
    r["stab_in"] = "STABPerform" in inp
    po = os.path.join(d, "job.out"); r["out"] = os.path.isfile(po)
    if r["out"]:
        t = open(po, errors="replace").read()
        r["normal"] = "ORCA TERMINATED NORMALLY" in t
        r["conv"] = bool(re.search(r"SCF CONVERGED AFTER", t)) and "SCF NOT CONVERGED" not in t
        e = re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t); r["E"] = float(e[-1]) if e else None
        v = re.findall(r"N\(Total\)\s*:\s*(-?\d+\.\d+)", t); ne = re.findall(r"Number of Electrons\s+NEL\s*\.*\s*(\d+)", t)
        r["nel"] = int(ne[0]) if ne else None; r["count_off"] = round(float(v[-1]) - int(ne[0]), 4) if v and ne else None
        k = t.rfind("LOEWDIN ATOMIC CHARGES"); lw = []
        if k >= 0:
            for l in t[k:].split("\n")[2:]:
                mm = re.match(r"\s*\d+\s*([A-Za-z]{1,2})\s*:\s*(-?\d+\.\d+)", l)
                if not mm: break
                lw.append(float(mm.group(2)))
        r["lw_sum24"] = round(sum(lw[:24]), 4) if len(lw) >= 24 else None
        r["lw_max24"] = round(max(abs(x) for x in lw[:24]), 4) if len(lw) >= 24 else None
        r["lw_rest"] = [round(x, 3) for x in lw[24:]]
        dp = re.findall(r"Magnitude \(Debye\)\s+:\s+(\d+\.\d+)", t); r["dip"] = float(dp[-1]) if dp else None
        st = re.findall(r"wavefunction is (stable|unstable)", t); r["stab"] = st[-1] if st else None
        nb = re.findall(r"Number of basis functions\s*\.+\s*(\d+)", t); r["nbf"] = int(nb[0]) if nb else None
        s2 = re.findall(r"Expectation value of <S\*\*2>\s*:\s*(-?\d+\.\d+)", t); r["s2"] = float(s2[-1]) if s2 else None
    return r
out = []
for top in sorted(os.listdir(S6)):
    dd = os.path.join(S6, top)
    if not os.path.isdir(dd): continue
    for root, dirs, files in os.walk(dd):
        if "job.inp" in files:
            try: out.append(parse(root))
            except Exception as e: out.append(dict(dir=os.path.relpath(root, S6), error=repr(e)))
print(len(out), "inputs indexed;", sum(1 for r in out if r.get("error")), "errors;", sum(1 for r in out if r.get("out")), "with output")

import collections
R = [r for r in out if r["natom"] >= 24 and r["chg"] == -2 and r["mult"] == 1]
def lvl(r): return " ".join(w for w in r["bang"].split() if w not in ("D3BJ", "def2/J", "RIJCOSX", "TightSCF", "D3ZERO"))[:28]
def state(r): return {"46.004": "R", "45.832": "TS"}.get(r["geomkey"], r["geomkey"])
def nz(r): return [c for c in r["charges"] if abs(c[0]) > 1e-9]
for r in R:
    r["top"] = r["dir"].split("/")[0]; r["lvl"] = lvl(r); r["st"] = state(r); r["nz"] = nz(r)
    r["plain"] = not any(k in r["bang"] for k in ("QMMM", "CPCM", "Opt", "EnGrad", "Freq", "DLPNO", "MP2", "FOD", "EOM"))
# controls: no nonzero charge, no wall, no ghost/extra atoms
ctl = {}
for r in R:
    if r["plain"] and not r["nz"] and not r["wall"] and r["natom"] == 24 and not r["ghost"] and r.get("E") is not None and r.get("lw_max24") is not None:
        ctl.setdefault((r["top"], r["lvl"], r["st"]), r); ctl.setdefault((r["lvl"], r["st"]), r)
def judge(r):
    """signs, from the output alone, against the charge-free run of the same level and state"""
    if not r.get("out"): return "no output"
    if not r.get("normal"): return "not normal"
    if not r.get("conv") or r.get("lw_max24") is None: return "not converged"
    c = ctl.get((r["top"], r["lvl"], r["st"])) or ctl.get((r["lvl"], r["st"]))
    if c is None: return "no control"
    s = []
    rise = r["lw_max24"] - c["lw_max24"]; ratio = r["dip"] / c["dip"] if r.get("dip") and c.get("dip") else None
    if rise >= 0.25: s.append("lw+%.2f" % rise)
    if ratio is not None and ratio >= 2: s.append("dip%.1fx" % ratio)
    if r.get("count_off") is not None and abs(r["count_off"]) > 0.02: s.append("cnt%+.2f" % r["count_off"])
    if r.get("stab") == "unstable": s.append("unstable")
    if r.get("lw_sum24") is not None and r["lw_sum24"] > -1.75: s.append("left%+.2f" % (r["lw_sum24"] + 2))
    r["rise"], r["ratio"] = rise, ratio
    return "; ".join(s) if s else "clean"
for r in R: r["j"] = judge(r) if r["plain"] else "skip"

def sig(r):  # the arrangement: charges and where, rounded
    return (r["st"], tuple(sorted((round(q, 3), round(d, 2)) for q, d, e in r["nz"])))
def flag(r):
    """bare: any sign; walled: Loewdin signs only (ORCA's dipole counts a walled charge as a nucleus, so it is not comparable)"""
    j = r["j"]
    if j in ("clean", "no output", "not normal", "not converged", "no control", "skip"): return j
    parts = [p for p in j.split("; ") if not (r["wall"] and p.startswith("dip"))]
    return "; ".join(parts) if parts else "clean"
M = [r for r in R if r["plain"] and len(r["nz"]) >= 1 and r.get("out")]
for r in M:
    r["f"] = flag(r); qs = [q for q, d, e in r["nz"]]
    r["desc"] = "n=%d net=%+.2f pos=%.2f maxq=%.2f dmin=%.2f" % (len(qs), sum(qs), sum(q for q in qs if q > 0), max(abs(q) for q in qs), min(d for q, d, e in r["nz"]))
    r["fn"] = bool(r["ghost"] or r["natom"] > 24)
print("== per folder: runs with charges, and how many show a sign of electrons leaving (walled runs judged on Loewdin signs only)")
g = collections.defaultdict(lambda: [0, 0, 0])
for r in M:
    k = (r["top"], r["lvl"], ",".join(r["wall"]) or "bare", "fn" if r["fn"] else "-", "one" if len(r["nz"]) == 1 else "many")
    g[k][0] += 1; g[k][1] += r["f"] not in ("clean",) and r["f"] not in ("not normal", "not converged", "no control"); g[k][2] += r["f"] in ("not normal", "not converged", "no control")
for k in sorted(g): print("%-14s %-26s %-5s %-2s %-4s runs %-4d signs %-4d unreadable %d" % (k + tuple(g[k])))

ok = lambda r: r["f"] not in ("not normal", "not converged", "no control", "no output")
sg = lambda r: ok(r) and r["f"] != "clean"
mq = lambda r: max(abs(q) for q, d, e in r["nz"])
big = lambda r: "TZVPD" in r["lvl"] or "QZVPPD" in r["lvl"]
A = [r for r in M if not r["wall"] and not r["fn"] and big(r) and "MORead" not in r["bang"] and mq(r) <= 0.2501 and ok(r)]
print("COUNT a  bare, no functions, def2-TZVPD or def2-QZVPPD, largest charge <= 0.25 e: runs %d signs %d" % (len(A), sum(sg(r) for r in A)))
A2 = [r for r in M if not r["wall"] and not r["fn"] and big(r) and "MORead" not in r["bang"] and mq(r) > 0.2501 and ok(r)]
print("COUNT a2 the same, largest charge above 0.25 e: runs %d signs %d" % (len(A2), sum(sg(r) for r in A2)))
Wl = [r for r in M if r["wall"] and ok(r)]
print("COUNT b  walled runs with a charge: runs %d signs %d" % (len(Wl), sum(sg(r) for r in Wl)))
S1 = [r for r in M if not r["wall"] and not r["fn"] and len(r["nz"]) == 1 and mq(r) <= 0.5001 and ok(r)]
print("COUNT c  one bare charge of <= 0.5 e, no functions: runs %d signs %d nearest %.2f to %.2f A" % (len(S1), sum(sg(r) for r in S1), min(r["nz"][0][1] for r in S1), max(r["nz"][0][1] for r in S1)))
Fn = [r for r in M if r["fn"] and mq(r) <= 0.2501 and ok(r)]
print("COUNT d  functions at the charges, largest charge <= 0.25 e: runs %d signs %d: %s" % (len(Fn), sum(sg(r) for r in Fn), ", ".join(sorted(r["dir"] for r in Fn if sg(r)))))
