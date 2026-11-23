"""UNOFFICIAL: read a pasted printout of block LOOK (D52) and say which way the runs so far lean, by the readings of the
committed pre-registration. Not the reader, not a result. usage: python3 look_read.py <file with the printout>"""
import importlib.util, re, sys
EV = 27.211386245988
sp = importlib.util.spec_from_file_location("ex", "/home/claude/work/stage39/code/phase2.2/cs6_d52_expected.py"); ex = importlib.util.module_from_spec(sp); sp.loader.exec_module(ex)
SYS = ("s1", "pc", "pf", "t3", "f4", "x6"); SETS = ("X2", "X3"); ASK = {"i12": 12.0, "i20": 20.0, "i40": 40.0}
R = {}
for l in open(sys.argv[1], errors="replace").read().split("\n"):
    l = l.strip().lstrip(">").strip()
    m = re.match(r"(ONE6_\S+) \| (\d) \|(.*)", l)
    if not m:
        continue
    f = [x.strip() for x in m.group(3).split("|")]
    run = m.group(1); p = run.split("_")
    d = dict(run=run, normal=m.group(2) == "1", level=p[1], set=p[2], rung=p[3] if p[1] != "HF" else "", sys=p[-1], time=f[5] if len(f) > 5 else "")
    try:
        e, u = float(f[0]), float(f[1])
        d.update(B=-(e - u) * EV, E=e, enuc=u, count=float(f[2]) if f[2] else None, acc=float(f[3]) if f[3] else None, pts=f[4])
        d["ok"] = d["normal"] and (d["rung"] not in ASK or (d["acc"] is not None and abs(d["acc"] - ASK[d["rung"]]) < 0.0015))
    except (ValueError, IndexError):
        d["ok"] = False
    R[run] = d
def B(level, s, rung, k):
    r = R.get("ONE6_HF_%s_%s" % (s, k) if level == "HF" else "ONE6_%s_%s_%s_%s" % (level, s, rung, k))
    return r["B"] if r and r["ok"] else None
def C(level, s, rung, k):
    r = R.get("ONE6_%s_%s_%s_%s" % (level, s, rung, k)); return r["count"] if r and r["ok"] else None
f4 = lambda v, fmt="%+.4f": "   -   " if v is None else fmt % v
print("outputs in the printout: %d; ended normally and as asked: %d; not: %s" % (len(R), sum(1 for r in R.values() if r["ok"]), ", ".join(r["run"] for r in R.values() if not r["ok"]) or "none"))
nz = [abs(r["enuc"]) for r in R.values() if r["ok"]]; print("largest nuclear repulsion printed: %.1e Eh" % max(nz) if nz else "")
print("\nHartree-Fock: ORCA minus PySCF in the same functions (tolerance 0.001), and the limit minus ORCA (tolerance 0.05)")
for s in SETS:
    print("  %s  " % s + "  ".join("%s %s / %s" % (k, f4(None if B("HF", s, None, k) is None else B("HF", s, None, k) - ex.HF[(s, k)], "%+.5f"),
                                               f4(None if B("HF", s, None, k) is None else ex.LIMIT[k] - B("HF", s, None, k))) for k in SYS))
for lv in ("CAM", "WXV", "WMV", "RDS"):
    print("\n%s: B minus the limit, eV (count of electrons in brackets); PySCF expected for CAM: X2 %s | X3 %s" % (
        lv, " ".join("%+.4f" % (ex.CAM[("X2", k)][0] - ex.LIMIT[k]) for k in SYS), " ".join("%+.4f" % (ex.CAM[("X3", k)][0] - ex.LIMIT[k]) for k in SYS)) if lv == "CAM"
          else "\n%s: B minus the limit, eV (count of electrons in brackets)" % lv)
    for s in SETS:
        for rg in ("g2", "z1", "i12", "i20", "i40"):
            vals = [(B(lv, s, rg, k), C(lv, s, rg, k)) for k in SYS]
            if any(v is not None for v, _ in vals):
                print("  %s %-3s " % (s, rg) + "  ".join("%s %s (%s)" % (k, f4(None if v is None else v - ex.LIMIT[k]), f4(c, "%.4f")) for k, (v, c) in zip(SYS, vals)))
    for s in SETS:
        d = [None if None in (B(lv, s, "i20", k), B(lv, s, "i12", k)) else B(lv, s, "i20", k) - B(lv, s, "i12", k) for k in SYS]
        if any(v is not None for v in d):
            print("  %s grid, i20 minus i12 (tolerance 0.005): " % s + "  ".join("%s %s" % (k, f4(v)) for k, v in zip(SYS, d)))
    d = [None if None in (B(lv, "X2", "i20", k), B(lv, "X3", "i20", k)) else B(lv, "X2", "i20", k) - B(lv, "X3", "i20", k) for k in SYS]
    if any(v is not None for v in d):
        print("  X2 minus X3 at i20 (tolerance 0.05): " + "  ".join("%s %s" % (k, f4(v)) for k, v in zip(SYS, d)))
    e = [None if B(lv, "X3", "i20", k) is None else B(lv, "X3", "i20", k) - ex.LIMIT[k] for k in SYS]
    if all(v is not None for v in e):
        w = max(e, key=abs); print("  largest distance from the limit in X3 at i20: %+.4f eV (%s)" % (w, SYS[e.index(w)]))
    elif any(v is not None for v in e):
        print("  X3 at i20 is measured at %d of 6 systems so far" % sum(1 for v in e if v is not None))
g, z, i = R.get("ONE6_CAM_X2_g2_s1"), R.get("ONE6_CAM_X2_z1_s1"), R.get("ONE6_CAM_X2_i12_s1")
if g and z and i and g["ok"] and z["ok"] and i["ok"]:
    print("\nhydrogen-only grid: z1 minus i12 %.2e Eh, z1 minus g2 %.2e Eh, i12 minus g2 %.2e Eh; points g2 %s, i12 %s, z1 %s" % (z["E"] - i["E"], z["E"] - g["E"], i["E"] - g["E"], g["pts"], i["pts"], z["pts"]))
else:
    print("\nhydrogen-only grid: not all three runs are measured")
print("\nrun times, longest five: " + ", ".join("%s %s" % (r["run"], r["time"]) for r in sorted(R.values(), key=lambda r: -sum(int(a) * b for a, b in zip(re.findall(r"\d+", r["time"] or "0h0m0s")[:3], (3600, 60, 1))))[:5]))
