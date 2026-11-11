#!/usr/bin/env python3
"""Figures and tables for WRITEUP_CONSOLIDATED_20261110.md, drawn only from committed files.

    python3 make_figures.py --res <results repo> --code <code repo> --out <this directory> [--tsv-only]

What it does, in order:

  1. loads the COMMITTED readers by path - phase2.2/cs6_audit.py (the classifier and its thresholds),
     phase2.2/cs6_d33b.py (the stability block and the level-shift markers) and phase2.2/cs6_analyse.py
     (the bare / (MM) / (QM/MM) energy convention) - so that every number here is read the way the
     record reads it;
  2. writes one .tsv per figure (F1 .. F9), plus controls.tsv (quantities recomputed from raw outputs
     beside the value the record prints) and derived.tsv (every derived number the write-up quotes, with
     its arithmetic and the files its inputs came from);
  3. unless --tsv-only, draws each figure from its own .tsv as .svg and .png.

Nothing is interpolated, nothing is estimated, and no number is typed in by hand except where the
committed source is itself a printed table, in which case the table is parsed from the committed text
and the file is named in the .tsv's header.  A .tsv is byte-reproducible: running this twice on the same
two commits gives identical files, which is what cs_writeup_check.py tests.
"""
import argparse
import hashlib
import importlib.util
import io
import lzma
import math
import re
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True      # importing the committed readers must leave the code repository untouched

H = 627.5094740631          # kcal/mol per Eh, the project constant
S6 = "phase2.2/cs_stage6"
FUNCS = ["CAM-B3LYP", "WB97X-D3", "B3LYP"]            # longest first: CAM-B3LYP contains B3LYP
BASES = ["DEF2-TZVPD", "MA-DEF2-SVP", "DEF2-SVPD", "DEF2-SVP", "6-31G(D)"]
PRETTY = {"CAM-B3LYP": "CAM-B3LYP", "WB97X-D3": "wB97X-D3", "B3LYP": "B3LYP", "HF": "HF", "MP2": "MP2",
          "DEF2-TZVPD": "def2-TZVPD", "MA-DEF2-SVP": "ma-def2-SVP", "DEF2-SVPD": "def2-SVPD",
          "DEF2-SVP": "def2-SVP", "6-31G(D)": "6-31G(d)"}


def stop(msg):
    print("STOP: %s" % msg, file=sys.stderr)
    raise SystemExit(1)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def text_of(p):
    p = Path(p)
    if p.suffix == ".xz":
        return lzma.open(str(p), "rt", errors="replace").read()
    return p.read_text(errors="replace")


def keyword_line(t):
    """The first '!' line of the INPUT FILE echo of an ORCA output."""
    i, j = t.find("INPUT FILE"), t.find("****END OF INPUT****")
    if i < 0 or j < 0:
        return ""
    for m in re.finditer(r"^\|\s*\d+>\s?(.*)$", t[i:j], re.M):
        if m.group(1).lstrip().startswith("!"):
            return m.group(1).strip()
    return ""


def level_of(t):
    kw = keyword_line(t).upper().split()
    f = next((x for x in FUNCS + ["HF", "MP2"] if x in kw), "?")
    b = next((x for x in BASES if x in kw), "?")
    d = "D3BJ" if "D3BJ" in kw else "-"
    cp = "CPCM" if "CPCM" in kw else "-"
    return f, b, d, cp, ("QMMM" in kw)


def echoed_coords(t, n=24):
    k = t.find("CARTESIAN COORDINATES (ANGSTROEM)")
    if k < 0:
        return None
    rows = []
    for l in t[k:].splitlines()[2:]:
        f = l.split()
        if len(f) != 4:
            break
        try:
            rows.append((f[0], float(f[1]), float(f[2]), float(f[3])))
        except ValueError:
            break
    return rows


def dist_signature(rows, n=24):
    """Sorted interatomic distances of the first n real atoms: invariant to translation and rotation, so
    a geometry is recognised by what it is and not by the name of the directory it sits in."""
    at = [r for r in rows if r[0] in ("C", "H", "O")][:n]
    if len(at) != n:
        return None
    d = []
    for i in range(n):
        for j in range(i + 1, n):
            d.append(math.dist(at[i][1:], at[j][1:]))
    return sorted(d)


def same_geom(a, b, tol=2e-4):
    return a is not None and b is not None and len(a) == len(b) and max(abs(x - y) for x, y in zip(a, b)) < tol


def read_xyz_rows(p):
    ls = Path(p).read_text().splitlines()
    n = int(ls[0].split()[0])
    out = []
    for l in ls[2:2 + n]:
        f = l.split()
        out.append((f[0], float(f[1]), float(f[2]), float(f[3])))
    return out


def charges_of(d):
    """The designed charges of a run directory: from pc.pc, or from inline ECP-centre lines (Ne>, Ar>, He>)
    of job.inp.  Returns (list of charges, representation)."""
    d = Path(d)
    pc = d / "pc.pc"
    inp = d / "job.inp"
    q, rep = [], "none"
    if pc.is_file():
        ls = pc.read_text().split("\n")
        n = int(ls[0].split()[0])
        q = [float(l.split()[0]) for l in ls[1:1 + n]]
        rep = "pc"
    if inp.is_file():
        e = [float(m.group(2)) for m in re.finditer(r"^\s*(Ne|Ar|He)>\s+(-?\d+\.\d+)\s", inp.read_text(), re.M)]
        if e:
            if q:
                stop("%s carries charges both in pc.pc and on ECP centres" % d)
            q, rep = e, "wall"
    return q, rep


def fmt(x, nd):
    return ("%." + str(nd) + "f") % x


def write_tsv(path, header_lines, cols, rows):
    with open(path, "w", newline="\n") as f:
        for h in header_lines:
            f.write("# " + h + "\n")
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


class Derived:
    """The registry of every derived number the write-up quotes."""

    def __init__(self):
        self.rows = []
        self.ids = set()

    def add(self, did, value, label, expression, inputs):
        if did in self.ids:
            stop("derived id %s used twice" % did)
        self.ids.add(did)
        self.rows.append((did, value, label, expression, inputs))
        return value


# --------------------------------------------------------------------------------------------------
# the data
# --------------------------------------------------------------------------------------------------
def build(res, code, out):
    res, code, out = Path(res), Path(code), Path(out)
    audit = load(code / "phase2.2" / "cs6_audit.py", "audit")
    d33b = load(code / "phase2.2" / "cs6_d33b.py", "d33b")
    analyse = load(code / "phase2.2" / "cs6_analyse.py", "analyse")
    if abs(analyse.H - H) > 0 or abs(d33b.H2KCAL - H) > 0:
        stop("the committed readers do not share this script's Hartree conversion")
    root = res / S6
    DV = Derived()
    controls = []          # (id, quantity, recomputed, record value, record file, abs diff, tolerance, verdict)

    def control(cid, what, mine, rec, recfile, tol, nd):
        diff = abs(mine - rec)
        controls.append((cid, what, fmt(mine, nd), fmt(rec, nd), recfile, "%.2e" % diff, "%.1e" % tol,
                         "PASS" if diff <= tol else "FAIL"))
        return diff <= tol

    def run(d):
        """One committed single point, through the committed readers."""
        p = Path(d) / "job.out"
        if not p.is_file():
            return None
        t = p.read_text(errors="replace")
        c = audit.read(t)
        if c is None:
            return None
        c["shifted"] = any(re.search(x, t) for x in d33b.SHIFT)
        c["stab"] = d33b.stability(t)
        c["level"] = level_of(t)
        c["sig"] = dist_signature(echoed_coords(t) or [])
        c["nfinal"] = len(re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t))
        return c

    # ---- the reference geometries of frame 42436, by content -----------------------------------
    ref = {st: dist_signature(read_xyz_rows(root / "d33a" / ("sp_42436_%s" % st) / "substrate.xyz"))
           for st in ("R", "TS")}

    def state_of(c):
        for st in ("R", "TS"):
            if same_geom(c["sig"], ref[st]):
                return st
        return None

    # ============================ F1: the reference barrier at each level ========================
    # every charge-free single point on frame 42436's frozen geometries anywhere under cs_stage6
    pool = {}
    ndirs = 0
    for jo in sorted(root.rglob("job.out")):
        d = jo.parent
        rel = d.relative_to(res).as_posix()
        ndirs += 1
        q, rep = charges_of(d)
        if q:
            continue
        inp = d / "job.inp"
        if inp.is_file() and re.search(r"^\s*(Ne|Ar|He)>", inp.read_text(), re.M):
            continue                               # a wall-only control is not a bare substrate
        c = run(d)
        if c is None or not c["norm"] or c["notconv"] or c["npc"]:
            continue
        f, b, disp, cp, qmmm = c["level"]
        if qmmm or f == "?" or b == "?":
            continue
        if c["nopt"] or c["nfinal"] != 1:
            continue                               # an optimisation's last energy is not at the frozen geometry
        st = state_of(c)
        if st is None:
            continue
        pool.setdefault((f, b, disp, cp), {}).setdefault(st, []).append((rel, c))
    f1 = []
    barrier = {}
    for key in sorted(pool, key=lambda k: (FUNCS[::-1].index(k[0]) if k[0] in FUNCS else 9,
                                           ["DEF2-SVP", "MA-DEF2-SVP", "DEF2-SVPD", "DEF2-TZVPD"].index(k[1]), k[3])):
        g = pool[key]
        if set(g) != {"R", "TS"}:
            continue
        eR = sorted(set(round(c["E"], 9) for _, c in g["R"]))
        eT = sorted(set(round(c["E"], 9) for _, c in g["TS"]))
        spread = max(max(eR) - min(eR), max(eT) - min(eT))
        # the first path in sorted order is the one quoted; the spread over the duplicates is reported
        rR, cR = g["R"][0]
        rT, cT = g["TS"][0]
        bar = (cT["E"] - cR["E"]) * H
        barrier[key] = bar
        f1.append((PRETTY[key[0]], PRETTY[key[1]], key[2], key[3], cR["nb"], fmt(cR["E"], 9), fmt(cT["E"], 9),
                   fmt(bar, 6), len(g["R"]), len(g["TS"]), "%.1e" % spread, fmt(cR["homo"], 4), rR, rT))
    write_tsv(out / "F1_reference_barrier.tsv",
              ["F1. Barrier E(TS)-E(R) of the bare substrate (no charges, no wall, in vacuo unless CPCM), frozen geometries of",
               "frame 42436, recomputed from every charge-free committed single point under %s." % S6,
               "Geometry is recognised by its interatomic distances against d33a/sp_42436_{R,TS}/substrate.xyz, not by directory name.",
               "n_R, n_TS: how many committed runs give that energy; spread_Eh: the largest disagreement among them.",
               "Energies through the committed phase2.2/cs6_audit.py read(); conversion %.10f kcal/mol per Eh." % H],
              ["functional", "basis", "dispersion", "solvation", "nbasis", "E_R_Eh", "E_TS_Eh", "barrier_kcal",
               "n_R", "n_TS", "spread_Eh", "HOMO_R_eV", "example_R", "example_TS"], f1)

    def bar_of(f, b, cp="-"):
        for k, v in barrier.items():
            if k[0] == f and k[1] == b and k[3] == cp:
                return v
        stop("no reference barrier for %s/%s" % (f, b))

    # controls on the reference barrier
    control("C01", "reference barrier, B3LYP-D3BJ/def2-SVP, frame 42436", bar_of("B3LYP", "DEF2-SVP"), 18.461014,
            S6 + "/STAGE6_DIAGNOSTIC27_RESULT_20261105.txt", 5e-7, 6)
    control("C02", "reference barrier, B3LYP-D3BJ/def2-SVPD", bar_of("B3LYP", "DEF2-SVPD"), 18.332256,
            S6 + "/STAGE6_DIAGNOSTIC27_RESULT_20261105.txt", 5e-7, 6)
    control("C03", "reference barrier, B3LYP-D3BJ/def2-TZVPD", bar_of("B3LYP", "DEF2-TZVPD"), 17.304571,
            S6 + "/STAGE6_DIAGNOSTIC27_RESULT_20261105.txt", 5e-7, 6)
    control("C04", "corrected reference, CAM-B3LYP-D3BJ/def2-SVPD (D33 stage A)", bar_of("CAM-B3LYP", "DEF2-SVPD"),
            26.8248, S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 5e-5, 4)
    control("C05", "reference barrier, B3LYP-D3BJ/ma-def2-SVP (D1 control)", bar_of("B3LYP", "MA-DEF2-SVP"), 17.8938,
            S6 + "/diffuse/DIAGNOSTIC1_RESULT.txt", 5e-5, 4)

    # ---- the frozen half, through the committed read_run convention ------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="cswu_"))
    try:
        with tarfile.open(root / "frozen" / "sp_outputs.tar.xz", "r:xz") as tf:
            tf.extractall(tmp, filter="data")
        arr = {}
        for line in (root / "frozen" / "frozen.tsv").read_text().splitlines()[1:]:
            f = line.split("\t")
            arr[f[0]] = dict(n=int(f[1]), dde=float(f[2]), score=float(f[3]))
        E, OLD = {}, {}
        for name in ["S6-C"] + list(arr):
            nsph = 0 if name == "S6-C" else arr[name]["n"]
            for st in ("R", "TS"):
                d = tmp / name / ("%s_sp" % st)
                src = root / "relax" / name / ("%s_sp" % st)
                shutil.copy(src / "combined.xyz", d / "combined.xyz")
                e_tot, e_mm, _g = analyse.read_run(d, nsph)
                E[(name, st)] = (e_tot, e_mm)
                OLD[(name, st)] = run(d)
        b0 = (E[("S6-C", "TS")][0] - E[("S6-C", "R")][0]) * H
        control("C06", "production reference barrier from the frozen control S6-C (cs6_analyse.read_run)", b0, 18.4610,
                S6 + "/frozen/FROZEN_REPORT.txt", 5e-5, 4)
        f7 = []
        worst = 0.0
        for i, name in enumerate(arr):
            dde = ((E[(name, "TS")][0] - E[("S6-C", "TS")][0]) - (E[(name, "R")][0] - E[("S6-C", "R")][0])) * H
            ok = control("C07.%02d" % (i + 1), "ddE(frozen) %s" % name, dde, arr[name]["dde"],
                         S6 + "/frozen/frozen.tsv", 5e-7, 6)
            worst = max(worst, abs(dde - arr[name]["dde"]))
            prm = root / "relax" / name / "R_sp" / "site.ORCAFF.prms"
            qs = sphere_charges(prm, arr[name]["n"])
            f7.append((name, arr[name]["n"], fmt(sum(abs(x) for x in qs), 4), fmt(sum(qs), 4),
                       fmt(max(abs(x) for x in qs), 4), fmt(dde, 6), fmt(arr[name]["dde"], 6),
                       fmt(arr[name]["score"], 6), fmt(dde / arr[name]["score"], 4),
                       fmt(100.0 * -dde / b0, 2)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_d34_in = len(list((root / "d34").rglob("job.inp")))
    n_d34_out = len(list((root / "d34").rglob("job.out")))

    # ============================ DIAGNOSTIC 34: the production arrangements at the corrected level ===========
    # Both arms are read here from the 44 raw outputs through the committed readers, the way cs6_d34.py reads them:
    # energies by cs6_analyse.read_run (QM/MM total, and the (MM) Lennard-Jones term), legs by cs6_audit.read,
    # stability and shift by cs6_d33b.  Arm 1 is the lift; arm 2 is the same job with the stability analysis.
    D34R = S6 + "/STAGE6_DIAGNOSTIC34_RESULT_20261110.txt"
    D34T = S6 + "/d34.tsv"
    rec34 = {}
    for l in (root / "d34.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        if len(f) >= 6:
            rec34[(f[0], f[1])] = dict(n=int(f[2]), sumq=float(f[3]), verdict=f[4], dde=float(f[5]), rise=f[8] if len(f) > 8 else "",
                                       dip=f[9] if len(f) > 9 else "", quotable=f[10] if len(f) > 10 else "")
    X = {}
    for arm in ("a1", "a2"):
        for name in ["S6-C"] + list(arr):
            nsph = 0 if name == "S6-C" else arr[name]["n"]
            for st in ("R", "TS"):
                d = root / "d34" / ("%s_%s_%s" % (arm, name, st))
                c = run(d)
                if c is None or not c["norm"] or c["notconv"]:
                    stop("%s did not read as a normally terminated, converged run" % d)
                c["Etot"], c["Emm"], _g = analyse.read_run(d, nsph)
                X[(arm, name, st)] = c
    for k, arm in enumerate(("a1", "a2")):
        bar = (X[(arm, "S6-C", "TS")]["Etot"] - X[(arm, "S6-C", "R")]["Etot"]) * H
        control("C2%d" % k, "DIAGNOSTIC 34 arm %s control barrier, CAM-B3LYP-D3BJ/def2-SVPD" % arm[1], bar, 26.8248,
                D34R if arm == "a1" else S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 5e-5, 4)

    def legs(get, name):
        """rise and dipole ratio per state against the same level's control, and whether a shift was engaged."""
        o = {}
        for st in ("R", "TS"):
            g, c = get(name, st), get("S6-C", st)
            o[st] = dict(rise=g["maxlw"] - c["maxlw"], dip=g["dip"] / c["dip"], shifted=g["shifted"], gap=g["gap"], cgap=c["gap"],
                         stab=g["stab"])
        return o

    def verdict4(lg):
        """The committed four-leg verdict, stability on the LAST analysis (AMENDMENT 5), as cs6_d33b.py applies it."""
        flagged = held = False
        for st in ("R", "TS"):
            x = lg[st]
            if x["rise"] >= audit.D_LW or x["dip"] >= audit.R_DIP:
                flagged = True
            if x["shifted"] or x["gap"] is None or x["cgap"] is None:
                held = True
            elif x["gap"] < audit.GAP_ABS and x["gap"] < audit.R_GAP * x["cgap"]:
                flagged = True
            if not x["stab"]["ran"]:
                held = True
            elif x["stab"]["last"] == "UNSTABLE":
                flagged = True
        return "UNRELIABLE" if flagged else ("INCONCLUSIVE" if held else "RELIABLE")

    t3, dde34 = [], {}
    r27 = {}
    k = (root / "STAGE6_DIAGNOSTIC34_RESULT_20261110.txt").read_text()
    for m in re.finditer(r"^\s+(\S+)\s+(R|TS)\s+([+-]\d\.\d{9})\s+([+-]\d+\.\d{6})\s*$", k, re.M):
        r27[(m.group(1), m.group(2))] = float(m.group(3))
    flag34 = {}
    cur = None
    for line in k[k.find("R34.8."):k.find("R34.9.")].splitlines():
        m = re.match(r"^\s+(\S+)\s+\d+\s+\d+\.\d{4} e\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)", line)
        if m:
            cur = m.group(1)
        m = re.match(r"^\s+flag: (R|TS) relocation: rise ([+-]\d+\.\d{4})", line)
        if m and cur:
            flag34[(cur, m.group(1))] = float(m.group(2))
    worst_corr = (0.0, "")
    for i, name in enumerate(arr):
        qs = sphere_charges(root / "relax" / name / "R_sp" / "site.ORCAFF.prms", arr[name]["n"])
        lgA = legs(lambda a, st: OLD[(a, st)], name)
        lg1 = legs(lambda a, st: X[("a1", a, st)], name)
        lg2 = legs(lambda a, st: X[("a2", a, st)], name)
        d = {}
        for arm in ("a1", "a2"):
            d[arm] = ((X[(arm, name, "TS")]["Etot"] - X[(arm, "S6-C", "TS")]["Etot"]) -
                      (X[(arm, name, "R")]["Etot"] - X[(arm, "S6-C", "R")]["Etot"])) * H
        dde34[name] = d
        corr = {st: X[("a2", name, st)]["Etot"] - X[("a1", name, st)]["Etot"] for st in ("R", "TS")}
        for st in ("R", "TS"):
            if abs(corr[st]) > worst_corr[0]:
                worst_corr = (abs(corr[st]), "%s %s" % (name, st))
            control("C27.%02d%s" % (i + 1, st[0]), "arm 2 minus arm 1 energy, %s %s (R34.7), Eh" % (name, st), corr[st],
                    r27[(name, st)], D34R, 5e-10, 9)
            if (name, st) in flag34:
                control("C28.%02d%s" % (i + 1, st[0]), "arm 2 Loewdin rise, %s %s (R34.8 flag)" % (name, st), lg2[st]["rise"],
                        flag34[(name, st)], D34R, 5e-5, 4)
        control("C22.%02d" % (i + 1), "ddE arm 1 %s (d34.tsv B1)" % name, d["a1"], rec34[("B1", name)]["dde"], D34T, 5e-7, 6)
        control("C23.%02d" % (i + 1), "ddE arm 2 %s (d34.tsv B2)" % name, d["a2"], rec34[("B2", name)]["dde"], D34T, 5e-7, 6)
        control("C24.%02d" % (i + 1), "stage A largest Loewdin rise %s (d34.tsv A)" % name,
                max(lgA["R"]["rise"], lgA["TS"]["rise"]), float(rec34[("A", name)]["rise"]), D34T, 5e-5, 4)
        control("C25.%02d" % (i + 1), "stage A largest dipole ratio %s (d34.tsv A)" % name,
                max(lgA["R"]["dip"], lgA["TS"]["dip"]), float(rec34[("A", name)]["dip"]), D34T, 5e-5, 4)
        v2 = verdict4(lg2)
        control("C29.%02d" % (i + 1), "arm 2 four-leg verdict %s recomputed (%s) against d34.tsv (%s): 0 = same" % (name, v2, rec34[("B2", name)]["verdict"]),
                0.0 if v2 == rec34[("B2", name)]["verdict"] else 1.0, 0.0, D34T, 0.0, 0)
        st2 = X[("a2", name, "R")]["stab"], X[("a2", name, "TS")]["stab"]
        t3.append((name, arr[name]["n"], fmt(sum(abs(x) for x in qs), 4), fmt(sum(qs), 4),
                   fmt(max([x for x in qs if x > 0] or [0.0]), 4), fmt(min([x for x in qs if x < 0] or [0.0]), 4),
                   fmt(lgA["R"]["rise"], 4), fmt(lgA["TS"]["rise"], 4), "yes" if (lgA["R"]["shifted"] or lgA["TS"]["shifted"]) else "no",
                   rec34[("A", name)]["verdict"], fmt(arr[name]["dde"], 6),
                   fmt(lg1["R"]["rise"], 4), fmt(lg1["TS"]["rise"], 4), fmt(lg1["R"]["dip"], 2), fmt(lg1["TS"]["dip"], 2),
                   "yes" if (lg1["R"]["shifted"] or lg1["TS"]["shifted"]) else "no", fmt(d["a1"], 6),
                   fmt(lg2["R"]["rise"], 4), fmt(lg2["TS"]["rise"], 4), fmt(lg2["R"]["dip"], 2), fmt(lg2["TS"]["dip"], 2),
                   "yes" if (lg2["R"]["shifted"] or lg2["TS"]["shifted"]) else "no",
                   "%s/%s" % (st2[0]["first"], st2[1]["first"]), "%s/%s" % (st2[0]["last"], st2[1]["last"]),
                   "%s/%s" % (st2[0]["nneg"], st2[1]["nneg"]), rec34[("B2", name)]["verdict"], fmt(d["a2"], 6),
                   fmt(corr["R"], 9), fmt(corr["TS"], 9), fmt(d["a2"] - d["a1"], 4), rec34[("B2", name)]["quotable"]))
    control("C26", "largest arm 2 minus arm 1 correction (%s), Eh (R34.7)" % worst_corr[1], worst_corr[0], 8.584e-02, D34R, 5e-6, 5)
    order34 = sorted(range(len(t3)), key=lambda i: (float(t3[i][2]), t3[i][0]))
    write_tsv(out / "T3_d34_arms.tsv",
              ["T3. DIAGNOSTIC 34, every arrangement at three readings, frame 42436, frozen geometries, QM/MM single points with the MM Lennard-Jones term.",
               "A_*: the committed frozen outputs, B3LYP-D3BJ/def2-SVP (stage A; POST HOC by its own words; no stability analysis exists).",
               "a1_*: arm 1, CAM-B3LYP-D3BJ/def2-SVPD, no stability analysis.  a2_*: arm 2, the same with the stability analysis; verdict on the LAST analysis.",
               "rise = largest |Loewdin charge| minus the same quantity in the SAME reading's control S6-C at the same state; threshold D_LW = %.2f e." % audit.D_LW,
               "dip = dipole magnitude over the control's; threshold R_DIP = %.1f.  corr = arm 2 energy minus arm 1 energy, Eh." % audit.R_DIP,
               "Recomputed from frozen/sp_outputs.tar.xz and d34/ through cs6_audit.read, cs6_d33b.stability and cs6_analyse.read_run;",
               "A_verdict, a2_verdict and quotable are the committed strings of d34.tsv, not re-judged (controls C29 re-judge arm 2 and compare)."],
              ["arrangement", "n", "sum_abs_q_e", "sum_q_e", "largest_positive_q_e", "most_negative_q_e",
               "A_rise_R", "A_rise_TS", "A_shifted", "A_verdict", "A_ddE_kcal",
               "a1_rise_R", "a1_rise_TS", "a1_dip_R", "a1_dip_TS", "a1_shifted", "a1_ddE_kcal",
               "a2_rise_R", "a2_rise_TS", "a2_dip_R", "a2_dip_TS", "a2_shifted", "a2_stab_first_R/TS", "a2_stab_last_R/TS",
               "a2_negative_eigenvalues_R/TS", "a2_verdict", "a2_ddE_kcal", "corr_R_Eh", "corr_TS_Eh", "ddE_a2_minus_a1_kcal", "quotable"],
              [t3[i] for i in order34])
    # S6-P and ADD-s1690_qp10000: one charge, one site, with and without the Lennard-Jones term
    twin = []
    for lab, get in (("B3LYP-D3BJ/def2-SVP (frozen)", lambda a, st: E[(a, st)]),
                     ("CAM-B3LYP-D3BJ/def2-SVPD arm 1", lambda a, st: (X[("a1", a, st)]["Etot"], X[("a1", a, st)]["Emm"])),
                     ("CAM-B3LYP-D3BJ/def2-SVPD arm 2", lambda a, st: (X[("a2", a, st)]["Etot"], X[("a2", a, st)]["Emm"]))):
        for st in ("R", "TS"):
            p_, a_ = get("S6-P", st), get("ADD-s1690_qp10000", st)
            twin.append((lab, st, fmt(p_[0] - p_[1], 9), fmt(a_[0] - a_[1], 9), "%.1e" % abs((p_[0] - p_[1]) - (a_[0] - a_[1])),
                         fmt(p_[1], 9), fmt(a_[1], 9)))
    write_tsv(out / "T4_twin_arrangements.tsv",
              ["T4. S6-P and ADD-s1690_qp10000: the same +1 charge at the same site, without and with the MM Lennard-Jones term.",
               "E_QM = QM/MM total minus the (MM) term, Eh, by cs6_analyse.read_run. The two agree at every level and state;",
               "the arrangements differ only in E_MM."],
              ["reading", "state", "E_QM_S6-P_Eh", "E_QM_ADD-s1690_qp10000_Eh", "abs_diff_Eh", "E_MM_S6-P_Eh", "E_MM_ADD-s1690_qp10000_Eh"], twin)
    f7 = [r + (t[4], t[5], t[16], t[26], t[25], t[30]) for r, t in zip(f7, t3)]
    write_tsv(out / "F7_production_designs.tsv",
              ["F7. The production (frozen-half) arrangements at three readings, frame 42436, frozen geometries, QM/MM single points.",
               "ddE_recomputed: B3LYP-D3BJ/def2-SVP, from frozen/sp_outputs.tar.xz (record = frozen/frozen.tsv).",
               "ddE_arm1: CAM-B3LYP-D3BJ/def2-SVPD, DIAGNOSTIC 34 arm 1 (no stability analysis). ddE_arm2: arm 2 (stability analysis, last solution).",
               "verdict_arm2, quotable: the committed strings of d34.tsv. D34 marks the ddE of an UNRELIABLE arrangement not quotable.",
               "Sigma|q|, Sigma q and the largest charges from each arrangement's committed relax/<name>/R_sp/site.ORCAFF.prms.",
               "pct_of_reference = -ddE_recomputed / the 18.4610-level reference barrier recomputed from S6-C, in per cent."],
              ["arrangement", "n", "sum_abs_q_e", "sum_q_e", "max_abs_q_e", "ddE_recomputed_kcal", "ddE_record_kcal",
               "score_kcal", "ratio_ddE_over_score", "pct_of_reference", "largest_positive_q_e", "most_negative_q_e",
               "ddE_arm1_kcal", "ddE_arm2_kcal", "verdict_arm2", "quotable"], f7)

    # ============================ F8 and the D33 stage A controls =================================
    a_old = [float(l.split("\t")[0]) for l in (root / "A_f42436.tsv").read_text().splitlines()
             if l and not l.startswith("#") and not l.lower().startswith("a")]
    a_new = [float(l.split("\t")[0]) for l in (root / "A_f42436_d33a.tsv").read_text().splitlines()
             if l and not l.startswith("#") and not l.lower().startswith("a")]
    if len(a_old) != len(a_new):
        stop("the two A matrices have %d and %d rows" % (len(a_old), len(a_new)))
    write_tsv(out / "F8_A_matrix.tsv",
              ["F8. a_i = V_TS(r_i) - V_R(r_i), kcal/mol per e, at every site of sites_f42436.tsv, frame 42436, bare substrate in vacuo.",
               "a_old: %s/A_f42436.tsv (B3LYP-D3BJ/def2-SVP).  a_new: %s/A_f42436_d33a.tsv (CAM-B3LYP-D3BJ/def2-SVPD, D33 stage A)." % (S6, S6)],
              ["site", "a_old", "a_new", "a_new_minus_a_old"],
              [(i, fmt(o, 6), fmt(n, 6), fmt(n - o, 6)) for i, (o, n) in enumerate(zip(a_old, a_new))])
    pear = pearson(a_old, a_new)
    # The committed reader (phase2.2/cs6_d33a.py, lines 124-127) ranks the sites by DESCENDING |a| and correlates
    # those ranks; that is what its "rank 0.863979" is.  It is reproduced here by the same definition, and the
    # rank correlation of the SIGNED a is computed beside it, because the two are different numbers.
    spear_abs = pearson(ranks([-abs(x) for x in a_old]), ranks([-abs(x) for x in a_new]))
    spear_signed = pearson(ranks(a_old), ranks(a_new))
    control("C08", "A matrix, Pearson correlation of a, new against old (R33.1)", pear, 0.977520,
            S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 5e-7, 6)
    control("C09", "A matrix, rank correlation of |a|, new against old (R33.1 'rank')", spear_abs, 0.863979,
            S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 5e-7, 6)
    dmax = max(range(len(a_old)), key=lambda i: abs(a_new[i] - a_old[i]))
    control("C10", "A matrix, largest change (site %d)" % dmax, a_new[dmax] - a_old[dmax], -1.8590,
            S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 5e-5, 4)
    top_old = set(sorted(range(len(a_old)), key=lambda i: -abs(a_old[i]))[:20])
    top_new = set(sorted(range(len(a_new)), key=lambda i: -abs(a_new[i]))[:20])
    control("C14", "A matrix, overlap of the twenty largest |a| (R33.1 'top-20 overlap')", float(len(top_old & top_new)), 17.0,
            S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt", 0.0, 0)

    # ============================ F3 and F4: the (n, q) grid, bare beside walled ==================
    ctl31 = {st: run(root / "d31" / ("ctl_%s" % st)) for st in ("R", "TS")}
    for st in ("R", "TS"):
        if sha(root / "d31" / ("ctl_%s" % st) / "job.out") != d33b.CTL_SHA[st]:
            stop("d31/ctl_%s/job.out is not the output D33 names by sha256" % st)
    grid = []
    stab_counts = {}
    for dn, arm_label in (("d31", "bare"), ("d32", "walled")):
        nrun = nfirst_unst = nlast_unst = 0
        conds = {}
        for jo in sorted((root / dn).rglob("job.out")):
            d = jo.parent
            c = run(d)
            if c is None:
                stop("%s did not read through the committed classifier" % d)
            nrun += 1
            if c["stab"]["first"] == "UNSTABLE":
                nfirst_unst += 1
            if c["stab"]["last"] == "UNSTABLE":
                nlast_unst += 1
            rel = d.relative_to(root / dn).as_posix()
            if rel.startswith("ctl_"):
                continue
            m = re.match(r"^(A|B|wall0)/(n\d+(?:_q\d\.\d\d)?)_(R|TS)$", rel)
            if not m:
                stop("unexpected run directory %s/%s" % (dn, rel))
            conds.setdefault((m.group(1), m.group(2)), {})[m.group(3)] = (d, c)
        stab_counts[dn] = (nrun, nfirst_unst, nlast_unst)
        for (arm, name), g in sorted(conds.items()):
            if set(g) != {"R", "TS"}:
                stop("%s/%s/%s lacks a state" % (dn, arm, name))
            q, rep = charges_of(g["R"][0])
            qT, _ = charges_of(g["TS"][0])
            if q != qT:
                stop("%s/%s/%s: the R and TS charge vectors differ" % (dn, arm, name))
            rise = {st: g[st][1]["maxlw"] - ctl31[st]["maxlw"] for st in ("R", "TS")}
            dipr = {st: g[st][1]["dip"] / ctl31[st]["dip"] for st in ("R", "TS")}
            dde = ((g["TS"][1]["E"] - ctl31["TS"]["E"]) - (g["R"][1]["E"] - ctl31["R"]["E"])) * H
            grid.append((arm_label, arm, name, len(q), fmt(sum(abs(x) for x in q), 4), fmt(max([abs(x) for x in q] or [0.0]), 4),
                         fmt(rise["R"], 4), fmt(rise["TS"], 4), fmt(max(rise.values()), 4),
                         fmt(dipr["R"], 3), fmt(dipr["TS"], 3),
                         "yes" if (g["R"][1]["shifted"] or g["TS"][1]["shifted"]) else "no",
                         "%s/%s" % (g["R"][1]["stab"]["first"], g["TS"][1]["stab"]["first"]),
                         "%s/%s" % (g["R"][1]["stab"]["last"], g["TS"][1]["stab"]["last"]),
                         fmt(dde, 4)))
    write_tsv(out / "F4_relocation.tsv",
              ["F4. Loewdin relocation of every DIAGNOSTIC 31 (bare point charges) and DIAGNOSTIC 32 (the same charges on argon ECP centres) condition,",
               "CAM-B3LYP-D3BJ/def2-SVPD, frame 42436 frozen geometries, in vacuo. rise = largest |Loewdin charge| minus the same quantity in",
               "d31's charge-free control at the same state, through the committed phase2.2/cs6_audit.py read(); threshold D_LW = %.2f e." % audit.D_LW,
               "shifted: a level shift or TRAH was engaged in either state (markers of phase2.2/cs6_d33b.py), which makes the gap leg unreadable.",
               "ddE is REPORTED FOR COMPLETENESS ONLY and is not a result: no committed document quotes a ddE for these conditions."],
              ["arm", "family", "condition", "n", "sum_abs_q_e", "max_abs_q_e", "rise_R_e", "rise_TS_e", "rise_max_e",
               "dipole_ratio_R", "dipole_ratio_TS", "shifted", "stability_first_R/TS", "stability_last_R/TS", "ddE_kcal"], grid)
    # control: the twelve q = 1.00 rows of R32.1
    r32 = parse_r32_1((root / "STAGE6_DIAGNOSTIC32_RESULT_20261109.txt").read_text())
    gl = {(r[0], r[1] + "/" + r[2]): float(r[8]) for r in grid}
    k = 0
    for cond, (bare, walled) in r32.items():
        k += 1
        control("C11.%02d" % k, "Loewdin rise, bare, %s (R32.1)" % cond, gl[("bare", cond)], bare,
                S6 + "/STAGE6_DIAGNOSTIC32_RESULT_20261109.txt", 5e-5, 4)
        control("C12.%02d" % k, "Loewdin rise, walled, %s (R32.1)" % cond, gl[("walled", cond)], walled,
                S6 + "/STAGE6_DIAGNOSTIC32_RESULT_20261109.txt", 5e-5, 4)

    # F3: the verdict per cell, parsed from the committed results (not re-judged here)
    f3 = parse_grid_verdicts((root / "STAGE6_DIAGNOSTIC31_RESULT_20261107.txt").read_text(),
                             (root / "STAGE6_DIAGNOSTIC32_RESULT_20261109.txt").read_text(),
                             (root / "STAGE6_DIAGNOSTIC32_ERRATUM1_20261109.txt").read_text())
    write_tsv(out / "F3_nq_grid.tsv",
              ["F3. Verdict per (n, q) cell, bare (DIAGNOSTIC 31) beside walled (DIAGNOSTIC 32), CAM-B3LYP-D3BJ/def2-SVPD, frame 42436.",
               "Parsed from the committed result documents; nothing is re-judged here.",
               "d31_verdict: R31.1 (family A) and R31.2 (family B) of STAGE6_DIAGNOSTIC31_RESULT_20261107.txt.",
               "d32_pairing: R32.1 and R32.3 of STAGE6_DIAGNOSTIC32_RESULT_20261109.txt; d32_verdict follows from the pairing by D32.4's definitions.",
               "erratum1_posthoc: the nine conditions STAGE6_DIAGNOSTIC32_ERRATUM1_20261109.txt E1.4 lists as moving to INCONCLUSIVE on the last-analysis",
               "reading. That re-reading labels itself POST HOC and NOT A REPLACEMENT VERDICT."],
              ["family", "n", "q_e", "d31_verdict", "d32_pairing", "d32_verdict", "erratum1_posthoc"], f3)

    # ============================ F5: the distance ladder =========================================
    f5 = parse_d11((root / "standoff" / "DIAGNOSTIC11_RESULT.txt").read_text(),
                   (root / "STAGE6_DIAGNOSTIC11_ERRATUM1_20261027.txt").read_text())
    write_tsv(out / "F5_distance_ladder.tsv",
              ["F5. DIAGNOSTIC 11: one +1 charge moved out along one axis from site 1690, B3LYP-D3BJ/ma-def2-SVP, in vacuo, frame 42436.",
               "Parsed from standoff/DIAGNOSTIC11_RESULT.txt (the ladder and control C-A1.1); distances in A from the rung table of",
               "STAGE6_DIAGNOSTIC11_ERRATUM1_20261027.txt E11.4. d_shield = ddE(wall) - ddE(bare). bar = max(10 %% of |ddE(bare)|, 0.05).",
               "The wall is a neon ECP centre whose parameters STAGE6_ERRATUM7 records as used outside their published assumption."],
              ["rung", "d_A", "ddE_bare_kcal", "ddE_wall_kcal", "d_shield_kcal", "bar_kcal", "classical_kcal", "ratio",
               "wall_status", "wall_only_ddE_kcal", "wall_only_verdict"], f5)

    # ============================ F6: predicted against measured ==================================
    f6 = []
    for r in f7:
        f6.append(("B3LYP-D3BJ/def2-SVP", "frozen half (QM/MM, LJ spheres)", r[0], r[1], r[2], r[7], r[5], r[8], rec34[("A", r[0])]["verdict"]))
    b33 = parse_d33b((root / "STAGE6_DIAGNOSTIC33_STAGEB_RESULT_20261109.txt").read_text())
    designs = {}
    for l in (root / "designs_d33b.tsv").read_text().splitlines():
        if l.startswith("#") or l.startswith("name") or not l.strip():
            continue
        f = l.split("\t")
        designs[f[0]] = dict(n=int(f[1]), arm=f[3], sumq=float(f[4]), band=f[5], score=float(f[6]),
                             q=[float(x) for x in f[8].split(",")])
    k = 0
    for name, d in designs.items():
        got = {st: run(root / "d33b" / ("%s_%s" % (name, st))) for st in ("R", "TS")}
        dde = ((got["TS"]["E"] - ctl31["TS"]["E"]) - (got["R"]["E"] - ctl31["R"]["E"])) * H
        k += 1
        control("C13.%02d" % k, "ddE %s (D33 stage B)" % name, dde, b33[name]["dde"],
                S6 + "/STAGE6_DIAGNOSTIC33_STAGEB_RESULT_20261109.txt", 5e-5, 4)
        f6.append(("CAM-B3LYP-D3BJ/def2-SVPD", "D33 stage B (%s)" % ("argon ECP centres" if d["arm"] == "wall" else "bare point charges"),
                   name, d["n"], fmt(d["sumq"], 4), fmt(d["score"], 6), fmt(dde, 6), fmt(dde / d["score"], 4), b33[name]["verdict"]))
    write_tsv(out / "F6_predicted_vs_measured.tsv",
              ["F6. The optimiser's linear score (sum a_i q_i + sum L_i) against the measured ddE, kcal/mol, frame 42436, frozen geometries.",
               "Two levels of theory that must not be joined by a trend line: the frozen half at B3LYP-D3BJ/def2-SVP (frozen/frozen.tsv, recomputed)",
               "and DIAGNOSTIC 33 stage B at CAM-B3LYP-D3BJ/def2-SVPD (designs_d33b.tsv for the score; ddE recomputed against d31's control).",
               "verdict: for stage B, its committed verdict. For the frozen half, DIAGNOSTIC 34 stage A's reading of the readable legs (d34.tsv),",
               "which is POST HOC by its own words and is not a reliability verdict: no frozen output carries a stability analysis."],
              ["level", "set", "design", "n", "sum_abs_q_e", "score_kcal", "ddE_kcal", "ratio_ddE_over_score", "verdict"], f6)

    # ============================ F2: Stage 4e ====================================================
    f2, fits = parse_stage4e((res / "phase2.2" / "cs_stage4e" / "STAGE4E_REPORT.txt").read_text())
    write_tsv(out / "F2_stage4e.tsv",
              ["F2. Stage 4e: eleven barrier-change quantities at five levels, kcal/mol, QM part, frame 41786 (not 42436).",
               "Parsed from phase2.2/cs_stage4e/STAGE4E_REPORT.txt. L1 B3LYP-D3BJ/def2-SVP; L2 B3LYP/6-31G(d); L3 HF/6-31G(d);",
               "L4 MP2/6-31G(d) (the reference); L5 wB97X-D3/def2-SVP. fit rows: L4 = k x level over the eleven values, with the report's residual."],
              ["kind", "quantity", "L1", "L2", "L3", "L4", "L5"], f2 + fits)

    # stage 4e's own bare barriers at the five levels (frame 41786), from the raw compressed outputs
    s4e = []
    for lv in ("L1", "L2", "L3", "L4", "L5"):
        e = {}
        for st in ("R", "TS"):
            t = text_of(res / "phase2.2" / "cs_stage4e" / ("%s_bare_%s" % (lv, st)) / "job.out.xz")
            if "****ORCA TERMINATED NORMALLY****" not in t:
                stop("stage 4e %s bare %s did not terminate normally" % (lv, st))
            e[st] = float(re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)[-1])
            kw = keyword_line(t)
        s4e.append((lv, kw.lstrip("! ").strip(), fmt(e["R"], 9), fmt(e["TS"], 9), fmt((e["TS"] - e["R"]) * H, 4)))
    write_tsv(out / "F1b_stage4e_bare_barrier.tsv",
              ["F1b. Barrier of the bare substrate at Stage 4e's five levels, FRAME 41786 (a different frame from F1), in vacuo,",
               "from phase2.2/cs_stage4e/L<k>_bare_{R,TS}/job.out.xz, last FINAL SINGLE POINT ENERGY of each."],
              ["level", "keyword_line", "E_R_Eh", "E_TS_Eh", "barrier_kcal"], s4e)

    # ============================ derived numbers =================================================
    A33 = S6 + "/STAGE6_DIAGNOSTIC33_STAGEA_RESULT_20261109.txt"
    B33 = S6 + "/STAGE6_DIAGNOSTIC33_STAGEB_RESULT_20261109.txt"
    D27 = S6 + "/STAGE6_DIAGNOSTIC27_RESULT_20261105.txt"
    D28 = S6 + "/STAGE6_DIAGNOSTIC28_RESULT_20261105.txt"
    DV.add("DV01", fmt(26.8248 - 18.461014, 4), "derived", "26.8248 - 18.461014", "%s ; %s R27.1" % (A33, D27))
    DV.add("DV02", fmt(18.332256 - 18.461014, 4), "derived", "18.332256 - 18.461014", "%s R27.1" % D27)
    DV.add("DV03", fmt(26.8248 - 18.332256, 4), "derived", "26.8248 - 18.332256", "%s ; %s R27.1" % (A33, D27))
    DV.add("DV04", fmt(1.2307 - (-0.5123), 4), "derived", "1.2307 - (-0.5123)", "%s R28.1" % D28)
    DV.add("DV05", fmt(-0.5123 - (-0.5918), 4), "derived", "-0.5123 - (-0.5918)", "%s R28.1" % D28)
    DV.add("DV06", fmt(26.8248 + (-14.3612), 4), "derived", "26.8248 + (-14.3612)", "%s ; %s" % (A33, B33))
    DV.add("DV07", fmt(100 * 14.3612 / 26.8248, 1), "derived", "100 * 14.3612 / 26.8248", "%s ; %s" % (A33, B33))
    DV.add("DV08", fmt(26.8248 + (-15.2781), 4), "derived", "26.8248 + (-15.2781)", "%s ; %s" % (A33, B33))
    DV.add("DV09", fmt(100 * 15.2781 / 26.8248, 1), "derived", "100 * 15.2781 / 26.8248", "%s ; %s" % (A33, B33))
    # reference barriers that the record prints nowhere, recomputed from raw outputs
    k = 20
    for (f, b, cp) in (("CAM-B3LYP", "DEF2-SVP", "-"), ("CAM-B3LYP", "DEF2-TZVPD", "-"), ("WB97X-D3", "DEF2-SVP", "-"),
                       ("WB97X-D3", "DEF2-SVPD", "-"), ("WB97X-D3", "DEF2-TZVPD", "-"), ("B3LYP", "MA-DEF2-SVP", "CPCM"),
                       ("B3LYP", "DEF2-SVPD", "-"), ("CAM-B3LYP", "DEF2-SVPD", "-")):
        key = next((kk for kk in barrier if kk[0] == f and kk[1] == b and kk[3] == cp), None)
        if key is None:
            continue
        ex = [r for r in f1 if r[0] == PRETTY[f] and r[1] == PRETTY[b] and r[3] == cp][0]
        DV.add("DV%02d" % k, fmt(barrier[key], 4), "recomputed from raw outputs",
               "(E_TS - E_R) * %.10f" % H, "%s ; %s" % (ex[12] + "/job.out", ex[13] + "/job.out"))
        k += 1
    for i, r in enumerate(s4e):
        DV.add("DV%02d" % (30 + i), r[4], "recomputed from raw outputs", "(E_TS - E_R) * %.10f, stage 4e %s, frame 41786" % (H, r[0]),
               "phase2.2/cs_stage4e/%s_bare_R/job.out.xz ; phase2.2/cs_stage4e/%s_bare_TS/job.out.xz" % (r[0], r[0]))
    # Sigma q of the D33 stage B designs, from the committed designs file
    for i, (name, d) in enumerate(designs.items()):
        DV.add("DV%02d" % (40 + i), "%+.2f" % sum(d["q"]), "derived", "sum of the charges of %s" % name, S6 + "/designs_d33b.tsv")
    DV.add("DV46", str(sum(1 for d in designs.values() if abs(sum(d["q"])) < 5e-7)), "derived",
           "number of the six stage B designs whose charges sum to zero", S6 + "/designs_d33b.tsv")
    DV.add("DV47", str(sum(1 for r in f7 if abs(float(r[3])) < 5e-5)), "derived",
           "number of the ten frozen arrangements whose charges sum to zero", S6 + "/relax/*/R_sp/site.ORCAFF.prms")
    # the linear estimate
    rat = [float(r[7]) for r in f6 if r[0].startswith("CAM") and r[8] != "UNRELIABLE"]
    DV.add("DV50", "%.2f" % min(rat), "derived", "smallest ddE/score over the five stage B designs not flagged UNRELIABLE", "%s ; %s/designs_d33b.tsv" % (B33, S6))
    DV.add("DV51", "%.2f" % max(rat), "derived", "largest ddE/score over the five stage B designs not flagged UNRELIABLE", "%s ; %s/designs_d33b.tsv" % (B33, S6))
    ratf = [float(r[8]) for r in f7]
    DV.add("DV52", "%.2f" % min(ratf), "derived", "smallest ddE/score over the ten frozen arrangements", S6 + "/frozen/frozen.tsv")
    DV.add("DV53", "%.2f" % max(ratf), "derived", "largest ddE/score over the ten frozen arrangements", S6 + "/frozen/frozen.tsv")
    DV.add("DV54", fmt(spear_signed, 6), "recomputed from committed files", "Spearman rank correlation of the SIGNED a_i, old against new",
           "%s/A_f42436.tsv ; %s/A_f42436_d33a.tsv" % (S6, S6))
    # run counts, from what is on disk
    k = 60
    for dn in ("d16", "d17", "d18", "d19", "d20", "d21", "d22", "d23", "d27", "d28", "d30", "d31", "d32", "d33a", "d33b",
               "standoff", "sitescan", "qscale", "cpcm", "additivity", "negatives", "negatives_armA", "transfer", "vde_probe",
               "vde_designs", "water_probe"):
        n_out = len(list((root / dn).rglob("job.out")))
        DV.add("DV%02d" % k, str(n_out), "count", "number of committed job.out files under %s/%s" % (S6, dn), "%s/%s" % (S6, dn))
        k += 1
    DV.add("DV90", str(n_d34_in), "count", "number of committed job.inp files under %s/d34" % S6, S6 + "/d34")
    DV.add("DV91", str(n_d34_out), "count", "number of committed job.out files under %s/d34" % S6, S6 + "/d34")
    DV.add("DV92", str(len(a_new)), "count", "number of sites (rows of A_f42436_d33a.tsv)", S6 + "/A_f42436_d33a.tsv")
    n4e = len(list((res / "phase2.2" / "cs_stage4e").glob("L[1-5]_*/job.out.xz")))
    DV.add("DV93", str(n4e), "count", "number of committed job.out.xz under phase2.2/cs_stage4e/L<k>_*", "phase2.2/cs_stage4e")
    DV.add("DV94", str(len(arr) * 2 + 2), "count", "frozen single points: two states for each of the ten arrangements and the control",
           S6 + "/frozen/frozen.tsv")
    for dn in ("d31", "d32"):
        nrun, nf, nl = stab_counts[dn]
        DV.add("DV95%s" % dn[-1], str(nf), "recomputed from raw outputs", "runs of %s whose FIRST stability analysis is unstable" % dn, "%s/%s" % (S6, dn))
        DV.add("DV96%s" % dn[-1], str(nl), "recomputed from raw outputs", "runs of %s whose LAST stability analysis is unstable" % dn, "%s/%s" % (S6, dn))
    DV.add("DV97", str(sum(1 for r in grid if r[0] == "walled" and r[1] != "wall0" and float(r[8]) < audit.D_LW)), "recomputed from raw outputs",
           "charged walled conditions of d32 whose larger Loewdin rise is below D_LW", S6 + "/d32")
    DV.add("DV98", str(sum(1 for r in grid if r[0] == "walled" and r[1] != "wall0")), "count", "charged walled conditions of d32 (two states each)", S6 + "/d32")
    DV.add("DV104", str(sum(1 for r in f7 if abs(float(r[4]) - 1.0) < 5e-5)), "derived",
           "number of the ten frozen arrangements whose largest |q| is 1.0000 e", S6 + "/relax/*/R_sp/site.ORCAFF.prms")
    # ---------------- DIAGNOSTIC 34 ----------------
    T3 = "figures/T3_d34_arms.tsv (recomputed from %s/d34 and %s/frozen/sp_outputs.tar.xz)" % (S6, S6)
    col = {h: i for i, h in enumerate(["arrangement", "n", "sum_abs_q_e", "sum_q_e", "largest_positive_q_e", "most_negative_q_e",
           "A_rise_R", "A_rise_TS", "A_shifted", "A_verdict", "A_ddE_kcal", "a1_rise_R", "a1_rise_TS", "a1_dip_R", "a1_dip_TS", "a1_shifted",
           "a1_ddE_kcal", "a2_rise_R", "a2_rise_TS", "a2_dip_R", "a2_dip_TS", "a2_shifted", "a2_stab_first", "a2_stab_last", "a2_nneg",
           "a2_verdict", "a2_ddE_kcal", "corr_R_Eh", "corr_TS_Eh", "ddE_a2_minus_a1_kcal", "quotable"])}

    def g(r, name):
        return r[col[name]]

    def over(r, pre):
        return max(float(g(r, pre + "_rise_R")), float(g(r, pre + "_rise_TS"))) >= audit.D_LW
    inwin = [r for r in t3 if float(g(r, "sum_abs_q_e")) <= d33b.CONV]
    DV.add("DV110", str(len(inwin)), "derived", "arrangements of DIAGNOSTIC 34 at or below %.2f e" % d33b.CONV, T3)
    DV.add("DV111", str(sum(1 for r in inwin if g(r, "a2_verdict") == "UNRELIABLE")), "derived",
           "of those, UNRELIABLE in arm 2 (d34.tsv)", T3 + " ; " + D34T)
    DV.add("DV112", str(sum(1 for r in inwin if g(r, "a2_verdict") == "RELIABLE")), "derived", "of those, RELIABLE in arm 2 (d34.tsv)", T3 + " ; " + D34T)
    DV.add("DV113", str(sum(1 for r in t3 if over(r, "a1"))), "recomputed from raw outputs",
           "arrangements whose arm 1 Loewdin rise is at or over D_LW in either state", T3)
    DV.add("DV114", str(sum(1 for r in t3 if over(r, "a2"))), "recomputed from raw outputs",
           "arrangements whose arm 2 Loewdin rise is at or over D_LW in either state", T3)
    DV.add("DV115", str(sum(1 for r in t3 if over(r, "A"))), "recomputed from raw outputs",
           "arrangements whose old-level (stage A) Loewdin rise is at or over D_LW in either state", T3)
    DV.add("DV116", str(sum(1 for r in t3 if over(r, "a1") != over(r, "a2"))), "recomputed from raw outputs",
           "arrangements whose arm 1 and arm 2 relocation flags differ", T3)
    DV.add("DV117", fmt(max(max(float(g(r, "a1_rise_R")), float(g(r, "a1_rise_TS"))) for r in t3), 4), "recomputed from raw outputs",
           "largest arm 1 Loewdin rise", T3)
    DV.add("DV118", fmt(max(max(float(g(r, "A_rise_R")), float(g(r, "A_rise_TS"))) for r in t3), 4), "recomputed from raw outputs",
           "largest old-level (stage A) Loewdin rise", T3)
    unst = [r for r in t3 if "UNSTABLE" in g(r, "a2_stab_first")]
    DV.add("DV119", str(len(unst)), "recomputed from raw outputs", "arrangements whose arm 2 first SCF solution is unstable in either state", T3)
    DV.add("DV120", str(sum(g(r, "a2_stab_first").split("/").count("UNSTABLE") for r in t3)), "recomputed from raw outputs",
           "arm 2 runs whose first SCF solution is unstable", T3)
    nn = sorted(set(x for r in unst for x in g(r, "a2_nneg").split("/")))
    DV.add("DV121", "/".join(nn), "recomputed from raw outputs", "distinct numbers of negative eigenvalues among those first solutions", T3)
    DV.add("DV122", fmt(worst_corr[0] * H, 4), "recomputed from raw outputs", "largest |arm 2 minus arm 1| energy, %s, x %.10f" % (worst_corr[1], H), T3)
    DV.add("DV123", fmt(worst_corr[0], 9), "recomputed from raw outputs", "largest |arm 2 minus arm 1| energy, %s, Eh" % worst_corr[1], T3)
    flips = [g(r, "arrangement") for r in t3 if float(g(r, "a1_ddE_kcal")) * float(g(r, "a2_ddE_kcal")) < 0]
    DV.add("DV124", str(len(flips)), "recomputed from raw outputs", "arrangements whose ddE changes sign between arm 1 and arm 2 (%s)" % ", ".join(flips), T3)
    DV.add("DV125", fmt(max(float(g(r, "ddE_a2_minus_a1_kcal")) for r in t3), 4), "recomputed from raw outputs",
           "largest ddE(arm 2) - ddE(arm 1)", T3)
    DV.add("DV126", str(sum(1 for r in t3 if g(r, "a2_verdict") == "RELIABLE")), "derived", "arrangements RELIABLE in arm 2 (d34.tsv)", D34T)
    DV.add("DV127", str(sum(1 for r in t3 if g(r, "a2_verdict") == "UNRELIABLE")), "derived", "arrangements UNRELIABLE in arm 2 (d34.tsv)", D34T)
    DV.add("DV128", str(sum(1 for r in t3 if float(g(r, "largest_positive_q_e")) == 0.0)), "derived",
           "arrangements of DIAGNOSTIC 34 carrying no positive charge", S6 + "/relax/*/R_sp/site.ORCAFF.prms")
    DV.add("DV129", str(sum(1 for r in t3 if float(g(r, "largest_positive_q_e")) == 0.0 and g(r, "a2_verdict") == "RELIABLE")), "derived",
           "of those, RELIABLE in arm 2", T3 + " ; " + D34T)
    DV.add("DV130", fmt(max(max(float(g(r, "a2_rise_R")), float(g(r, "a2_rise_TS"))) for r in t3 if float(g(r, "largest_positive_q_e")) == 0.0), 4),
           "recomputed from raw outputs", "largest arm 2 Loewdin rise among the arrangements with no positive charge", T3)
    DV.add("DV131", str(len(t3) - 1), "derived", "distinct electronic systems among the ten arrangements: S6-P and ADD-s1690_qp10000 are one",
           "figures/T4_twin_arrangements.tsv")
    DV.add("DV132", "%.1e" % max(float(r[4]) for r in twin), "recomputed from raw outputs",
           "largest |E_QM(S6-P) - E_QM(ADD-s1690_qp10000)| over three readings and two states, Eh", "figures/T4_twin_arrangements.tsv")
    DV.add("DV133", str(sum(1 for r in t3 if g(r, "A_shifted") == "yes")), "recomputed from raw outputs",
           "arrangements whose old-level run engaged a level shift in either state", T3)
    DV.add("DV134", str(sum(1 for r in t3 if g(r, "a1_shifted") == "yes")), "recomputed from raw outputs",
           "arrangements whose arm 1 run engaged a level shift or TRAH in either state", T3)
    rel = [r for r in t3 if g(r, "a2_verdict") == "RELIABLE"]
    chg = [float(g(r, "a1_ddE_kcal")) - float(g(r, "A_ddE_kcal")) for r in rel]
    DV.add("DV135", fmt(min(chg), 4), "derived", "most negative ddE(arm 1) - ddE(old level) among the RELIABLE arrangements", T3 + " ; " + S6 + "/frozen/frozen.tsv")
    DV.add("DV136", fmt(max(chg), 4), "derived", "least negative ddE(arm 1) - ddE(old level) among the RELIABLE arrangements", T3 + " ; " + S6 + "/frozen/frozen.tsv")
    DV.add("DV137", str(sum(1 for r in t3 if abs(float(g(r, "sum_q_e"))) < 5e-5 and g(r, "a2_verdict") == "RELIABLE")), "derived",
           "arrangements with charges summing to zero that are RELIABLE in arm 2", T3 + " ; " + D34T)
    DV.add("DV138", str(sum(1 for r in t3 if float(g(r, "sum_abs_q_e")) > d33b.CONV)), "derived", "arrangements above %.2f e" % d33b.CONV, T3)
    # ---------------- the largest positive charge against the verdict (POST HOC tabulation; section 11) ----------------
    tab = []
    for r in t3:
        tab.append(("D34 arm 2", "LJ sphere, QM/MM", g(r, "arrangement"), g(r, "n"), g(r, "largest_positive_q_e"), g(r, "most_negative_q_e"),
                    g(r, "a2_verdict")))
    for name, d in designs.items():
        tab.append(("D33 stage B", "argon ECP centre" if d["arm"] == "wall" else "bare point charge", name, d["n"],
                    fmt(max([x for x in d["q"] if x > 0] or [0.0]), 4), fmt(min([x for x in d["q"] if x < 0] or [0.0]), 4), b33[name]["verdict"]))
    for r in f3:
        cname = ("n%02d" % int(r[1])) if r[0] == "A" else ("n%02d_q%s" % (int(r[1]), r[2]))
        qs, _rep = charges_of(root / "d31" / r[0] / (cname + "_R"))
        tab.append(("D31", "bare point charge", "%s/%s" % (r[0], cname), len(qs), fmt(max([x for x in qs if x > 0] or [0.0]), 4),
                    fmt(min([x for x in qs if x < 0] or [0.0]), 4), r[3]))
    write_tsv(out / "T5_positive_charge_vs_verdict.tsv",
              ["T5. POST HOC. The largest positive charge of every design classified at CAM-B3LYP-D3BJ/def2-SVPD on frame 42436, against its committed verdict.",
               "D34 arm 2: d34.tsv, charges from relax/<name>/R_sp/site.ORCAFF.prms. D33 stage B: its result and designs_d33b.tsv.",
               "D31: its result (R31.1, R31.2), charges from d31/<family>/<condition>_R/pc.pc.",
               "The designs differ in site, sign pattern, n and representation as well as magnitude; this table is a tabulation, not a test."],
              ["diagnostic", "representation", "design", "n", "largest_positive_q_e", "most_negative_q_e", "verdict"], tab)
    two = [t for t in tab if t[0] != "D31" and t[1] != "argon ECP centre"]
    lo = [t for t in two if float(t[4]) <= 0.50]
    hi = [t for t in two if float(t[4]) >= 0.55]
    DV.add("DV140", str(len(two)), "derived", "non-walled designs of D34 arm 2 and D33 stage B together", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV141", str(len(lo)), "derived", "of those, largest positive charge at most +0.50 e", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV142", str(sum(1 for t in lo if t[6] == "UNRELIABLE")), "derived", "of DV141, UNRELIABLE", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV143", str(len(hi)), "derived", "of DV140, largest positive charge at or above +0.55 e", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV144", str(sum(1 for t in hi if t[6] != "UNRELIABLE")), "derived", "of DV143, not UNRELIABLE", "figures/T5_positive_charge_vs_verdict.tsv")
    d31t = [t for t in tab if t[0] == "D31"]
    DV.add("DV145", str(len(d31t)), "derived", "DIAGNOSTIC 31 conditions tabulated", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV146", str(sum(1 for t in d31t if float(t[4]) >= 0.55 and t[6] == "RELIABLE")), "derived",
           "DIAGNOSTIC 31 conditions with largest positive charge at or above +0.55 e that are RELIABLE", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV147", str(sum(1 for t in d31t if float(t[4]) <= 0.50 and t[6] == "UNRELIABLE")), "derived",
           "DIAGNOSTIC 31 conditions with largest positive charge at most +0.50 e that are UNRELIABLE", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV148", str(sum(1 for t in d31t if float(t[4]) == 1.0)), "derived",
           "DIAGNOSTIC 31 conditions that carry a +1.00 e charge", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV149", str(sum(1 for t in d31t if float(t[4]) == 0.0)), "derived",
           "DIAGNOSTIC 31 conditions with no positive charge", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV150", str(2 * 2), "derived", "2 sign-swapped single spheres (site 1690 at -1.00 e, site 678 at +1.00 e) x 2 states", T3)
    # ---------------- DIAGNOSTIC 2: both signs of a bare charge at site 1690 (POST HOC reading; section 11) ----------------
    # D2 scanned +q and -q at one site and reported energies.  Its outputs also carry the Loewdin charges and the
    # dipole, so the relocation and dipole legs can be read for both signs at one site.  No stability analysis exists.
    D2R = S6 + "/qscan/DIAGNOSTIC2_RESULT.txt"
    tmp2 = Path(tempfile.mkdtemp(prefix="cswu_d2_"))
    t6, nneg_runs, nneg_fire, npos_fire = [], 0, 0, 0
    try:
        with tarfile.open(root / "qscan" / "outputs" / "qscan_outputs.tar.xz", "r:xz") as tf:
            tf.extractall(tmp2, filter="data")
        d2rec = {}
        for cm in re.finditer(r"^(C\d)  (\S+)  (in vacuo|CPCM[^\n]*)\n(.*?)\n\s+a_est", (root / "qscan" / "DIAGNOSTIC2_RESULT.txt").read_text(), re.M | re.S):
            for m in re.finditer(r"^\s+(\d\.\d\d)\s+(-?\d+\.\d{4})\s+(-?\d+\.\d{4})\s", cm.group(4), re.M):
                d2rec[(cm.group(1), m.group(1))] = (cm.group(2), float(m.group(2)), float(m.group(3)))
        for cond in ("C1", "C3", "C5"):                # the three in-vacuo conditions; C2 and C4 add a continuum
            ctl = {st: run(tmp2 / cond / ("bare_%s" % st)) for st in ("R", "TS")}
            for mag in ("0050", "0250", "0500", "1000"):
                qv = "%d.%s" % (int(mag[0]), mag[1:3])
                for sign, col in (("p", 1), ("m", 2)):
                    c = {st: run(tmp2 / cond / ("q%s%s_%s" % (sign, mag, st))) for st in ("R", "TS")}
                    if any(x is None or not x["norm"] or x["notconv"] for x in list(c.values()) + list(ctl.values())):
                        stop("a DIAGNOSTIC 2 output of %s q%s%s did not read as a normally terminated, converged run" % (cond, sign, mag))
                    rise = {st: c[st]["maxlw"] - ctl[st]["maxlw"] for st in ("R", "TS")}
                    dip = {st: c[st]["dip"] / ctl[st]["dip"] for st in ("R", "TS")}
                    dde = ((c["TS"]["E"] - ctl["TS"]["E"]) - (c["R"]["E"] - ctl["R"]["E"])) * H
                    level, rec_p, rec_m = d2rec[(cond, qv)]
                    control("C30.%s%s%s" % (cond[1], sign, mag), "DIAGNOSTIC 2 ddE, %s, q = %s%s e at site 1690" % (cond, "+" if sign == "p" else "-", qv),
                            dde, rec_p if sign == "p" else rec_m, D2R, 5e-5, 4)
                    fire = [st for st in ("R", "TS") if rise[st] >= audit.D_LW or dip[st] >= audit.R_DIP]
                    if sign == "m":
                        nneg_runs += 2
                        nneg_fire += len(fire)
                    else:
                        npos_fire += len(fire)
                    t6.append((cond, "B3LYP-D3BJ/%s" % level, ("+" if sign == "p" else "-") + qv + "00", fmt(rise["R"], 4), fmt(rise["TS"], 4),
                               fmt(dip["R"], 2), fmt(dip["TS"], 2), fmt(dde, 4), "/".join(fire) or "none"))
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)
    write_tsv(out / "T6_d2_both_signs_site_1690.tsv",
              ["T6. POST HOC. DIAGNOSTIC 2's charge scan at site 1690, bare point charge, frame 42436, frozen, in vacuo: the relocation and dipole",
               "legs for both signs, recomputed from qscan/outputs/qscan_outputs.tar.xz through cs6_audit.read. D2's own result reports energies only.",
               "rise = largest |Loewdin charge| minus the same condition's charge-free control; dip = dipole magnitude over the control's.",
               "legs_fired: the states in which rise >= D_LW (0.25 e) or dip >= R_DIP (2.0). No stability analysis exists for these runs, and the",
               "functional is the retired one, so this is two legs of four at another level: it is not a verdict."],
              ["condition", "level", "q_e", "rise_R", "rise_TS", "dip_R", "dip_TS", "ddE_kcal", "legs_fired"], t6)
    T6 = "figures/T6_d2_both_signs_site_1690.tsv"
    c5 = {r[2]: r for r in t6 if r[0] == "C5"}
    DV.add("DV151", fmt(max(float(c5["+1.0000"][3]), float(c5["+1.0000"][4])), 4), "recomputed from raw outputs",
           "DIAGNOSTIC 2, def2-SVPD, q = +1.0000 e at site 1690: larger Loewdin rise of the two states", T6)
    DV.add("DV152", fmt(max(float(c5["-1.0000"][3]), float(c5["-1.0000"][4])), 4), "recomputed from raw outputs",
           "DIAGNOSTIC 2, def2-SVPD, q = -1.0000 e at site 1690: larger Loewdin rise of the two states", T6)
    DV.add("DV153", fmt(max(float(c5["+1.0000"][5]), float(c5["+1.0000"][6])), 2), "recomputed from raw outputs",
           "DIAGNOSTIC 2, def2-SVPD, q = +1.0000 e: larger dipole ratio of the two states", T6)
    DV.add("DV154", fmt(max(float(c5["-1.0000"][5]), float(c5["-1.0000"][6])), 2), "recomputed from raw outputs",
           "DIAGNOSTIC 2, def2-SVPD, q = -1.0000 e: larger dipole ratio of the two states", T6)
    DV.add("DV155", str(nneg_runs), "derived", "negative-charge single points in DIAGNOSTIC 2's three in-vacuo conditions (4 magnitudes x 2 states x 3)", T6)
    DV.add("DV156", str(nneg_fire), "recomputed from raw outputs", "of those, runs firing the Loewdin or the dipole leg", T6)
    DV.add("DV157", str(npos_fire), "recomputed from raw outputs",
           "positive-charge single points of the same conditions firing the Loewdin or the dipole leg (%s)"
           % ", ".join("%s %s" % (r[0], r[2]) for r in t6 if r[2].startswith("+") and r[8] != "none"), T6)
    # ---------------- DIAGNOSTIC 12: its sign arm, and its sites beyond r_safe (readings of its committed tables) ----------------
    D12R = S6 + "/sitescan/DIAGNOSTIC12_RESULT.txt"
    t12 = (root / "sitescan" / "DIAGNOSTIC12_RESULT.txt").read_text()
    m = re.search(r"r_safe = (\d\.\d\d) A", (root / "STAGE6_DIAGNOSTIC11_ERRATUM1_20261027.txt").read_text())
    if not m:
        stop("DIAGNOSTIC 11's Erratum 1 does not state r_safe")
    r_safe = float(m.group(1))
    arm12 = t12[t12.index("C-A12.2"):t12.index("BASIS ARM")]
    sg = [(float(x.group(3)), float(x.group(4))) for x in
          re.finditer(r"^\s+(\d+)\s+(\d\.\d{3})\s+([+-]\d+\.\d{4})\s+([+-]\d+\.\d{4})\s*$", arm12, re.M)]
    tab12 = t12[t12.index("THE 36 SITES"):t12.index("WHICH DESCRIPTOR")]
    st12 = [(float(x.group(2)), x.group(3)) for x in
            re.finditer(r"^\s+(\d+)\s+\S+\s+(\d\.\d{3})\s+.*\s(FAIL|VOID|pass)\s*$", tab12, re.M)]
    if len(sg) != 10 or len(st12) != 36:
        stop("DIAGNOSTIC 12's result gave %d sign-arm rows and %d sites, expected ten and 36" % (len(sg), len(st12)))
    far = [x for x in st12 if x[0] > r_safe]
    DV.add("DV158", fmt(max(abs(x[1]) for x in sg), 4), "derived", "DIAGNOSTIC 12 sign arm (C-A12.2): largest |d_shield| at q = -1", D12R)
    DV.add("DV159", fmt(max(abs(x[0]) for x in sg), 4), "derived", "DIAGNOSTIC 12 sign arm (C-A12.2): largest |d_shield| at q = +1", D12R)
    DV.add("DV160", str(len(sg)), "derived", "sites in DIAGNOSTIC 12's sign arm", D12R)
    DV.add("DV161", str(len(far)), "derived", "DIAGNOSTIC 12 sites whose nearest substrate atom is beyond r_safe = %.2f A" % r_safe, D12R)
    DV.add("DV162", str(sum(1 for x in far if x[1] == "FAIL")), "derived", "of those, FAIL by DIAGNOSTIC 11's tolerance", D12R)
    DV.add("DV163", str(sum(1 for x in sg if abs(x[0]) > abs(x[1]))), "derived",
           "sign-arm sites at which |d_shield(+1)| exceeds |d_shield(-1)|", D12R)
    # run counts of the experiments section 11 proposes: arithmetic on quantities the record fixes
    DV.add("DV101", str(len(f5) * 2 * 2), "derived", "%d rungs of DIAGNOSTIC 11's ladder x 2 signs x 2 states" % len(f5),
           S6 + "/standoff/DIAGNOSTIC11_RESULT.txt")
    n_post = sum(1 for r in f3 if r[6] != "-")
    DV.add("DV102", str(n_post * 2), "derived", "%d conditions of ERRATUM 1 E1.4 x 2 states" % n_post,
           S6 + "/STAGE6_DIAGNOSTIC32_ERRATUM1_20261109.txt")
    n_elig = sum(1 for nm, d in designs.items() if d["arm"] == "bare" and b33[nm]["verdict"] == "RELIABLE" and d["sumq"] <= d33b.CONV)
    DV.add("DV103", str(n_elig * 2), "derived", "%d bare stage B designs that are RELIABLE and at or below %.2f e x 2 states" % (n_elig, d33b.CONV),
           B33 + " ; " + S6 + "/designs_d33b.tsv")
    write_tsv(out / "derived.tsv",
              ["Every derived number WRITEUP_CONSOLIDATED_20261110.md quotes: its value as printed, its label, the arithmetic and the inputs' files.",
               "Produced by make_figures.py; cs_writeup_check.py regenerates this file and compares it byte for byte."],
              ["id", "value", "label", "expression", "inputs"], DV.rows)
    write_tsv(out / "controls.tsv",
              ["Quantities the record prints, recomputed here from raw committed outputs through the committed readers.",
               "A control FAILS if |recomputed - record| exceeds the tolerance, which is half a unit in the record's last printed place."],
              ["id", "quantity", "recomputed", "record", "record_file", "abs_diff", "tolerance", "verdict"], controls)
    bad = [c for c in controls if c[-1] != "PASS"]
    return dict(controls=controls, bad=bad, ndirs=ndirs)


def sphere_charges(prm, n):
    """The n sphere charges of an arrangement: the last n atom rows of its ORCA force-field file.
    Each atom row of the $atoms block reads: index  type  charge ..."""
    ls = Path(prm).read_text().splitlines()
    k = next(i for i, l in enumerate(ls) if l.strip().startswith("$atoms"))
    cnt = int(ls[k + 1].split()[0])
    rows = ls[k + 2:k + 2 + cnt]
    return [float(r.split()[2]) for r in rows[-n:]]


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def parse_r32_1(t):
    out = {}
    k = t.find("the Loewdin rise, without the wall and with it:")
    for l in t[k:].splitlines()[3:]:
        m = re.match(r"^\s+((?:A|B)/n\d+(?:_q\d\.\d\d)?)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+\d+\.\d+x", l)
        if not m:
            if out:
                break
            continue
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    if len(out) != 12:
        stop("R32.1's rise table gave %d rows, expected 12" % len(out))
    return out


def parse_grid_verdicts(t31, t32, e1):
    rows = []
    v31 = {}
    for m in re.finditer(r"^\s+(\d+)\s+(\d+\.\d\d)\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)\s", t31, re.M):
        v31[("A", int(m.group(1)), "1.00")] = m.group(3)
    k = t31.find("R31.2")
    for l in t31[k:t31.find("R31.3")].splitlines():
        m = re.match(r"^\s+(\d+)\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)\s+(RELIABLE|UNRELIABLE|INCONCLUSIVE)", l)
        if m:
            for q, v in zip(("0.25", "0.50", "0.75", "1.00"), m.groups()[1:]):
                v31[("B", int(m.group(1)), q)] = v
    p32 = {}
    for m in re.finditer(r"^\s+(A|B)/n(\d+)(?:_q(\d\.\d\d))?\s+(RELIABLE|UNRELIABLE)\s+(RELIABLE|UNRELIABLE)\s+(RESCUED|STILL UNRELIABLE|UNCHANGED|BROKEN BY THE WALL|INCONCLUSIVE)\s*$", t32, re.M):
        p32[(m.group(1), int(m.group(2)), m.group(3) or "1.00")] = m.group(6)
    k = t32.find("R32.3")
    for l in t32[k:t32.find("R32.4")].splitlines():
        m = re.match(r"^\s+(\d+)\s+(UNCHANGED|STILL UNRELIABLE|INCONCLUSIVE|RESCUED|BROKEN BY THE WALL)\s+(UNCHANGED|STILL UNRELIABLE|INCONCLUSIVE|RESCUED|BROKEN BY THE WALL)\s+(UNCHANGED|STILL UNRELIABLE|INCONCLUSIVE|RESCUED|BROKEN BY THE WALL)", l)
        if m:
            for q, v in zip(("0.25", "0.50", "0.75"), m.groups()[1:]):
                p32[("B", int(m.group(1)), q)] = v
    k = e1.find("nine conditions move from UNRELIABLE to INCONCLUSIVE")
    blk = e1[k:e1.find("the primary becomes", k)]
    post = set()
    for m in re.finditer(r"(A|B)/n(\d+)(?:_q(\d\.\d\d))?", blk):
        post.add((m.group(1), int(m.group(2)), m.group(3) or "1.00"))
    if len(post) != 9:
        stop("ERRATUM 1 E1.4 gave %d conditions, expected nine" % len(post))
    w = {"RESCUED": "RELIABLE", "UNCHANGED": None, "STILL UNRELIABLE": "UNRELIABLE", "BROKEN BY THE WALL": "UNRELIABLE",
         "INCONCLUSIVE": "INCONCLUSIVE"}
    for key in sorted(v31, key=lambda k: (k[0], k[2], k[1])):
        if key not in p32:
            stop("no DIAGNOSTIC 32 pairing for %s" % (key,))
        pair = p32[key]
        v32 = w[pair] if w[pair] is not None else v31[key]
        rows.append((key[0], key[1], key[2], v31[key], pair, v32, "INCONCLUSIVE (post hoc)" if key in post else "-"))
    if len(rows) != 30:
        stop("the (n, q) grid has %d cells, expected 30" % len(rows))
    return rows


def parse_d11(t, e):
    dist = {}
    k = e.find("rung    d / A")
    for l in e[k:].splitlines()[1:]:
        m = re.match(r"^\s+(d\w+)\s+(\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+\.\d+)\s*$", l)
        if m:
            dist[m.group(1)] = m.group(2)
        elif dist:
            break
    w0 = {}
    k = t.find("d / A    ddE(wall, q=0)   verdict")
    for l in t[k:].splitlines()[1:]:
        m = re.match(r"^\s+(d\w+)\s+([+-]\d+\.\d+)\s+(NOT INERT|inert)\s*$", l)
        if m:
            w0[m.group(1)] = (m.group(2), m.group(3))
        elif w0:
            break
    rows = []
    k = t.find("d / A   ddE bare   ddE wall   d_shield   bar      classical  ratio   wall")
    for l in t[k:].splitlines()[1:]:
        m = re.match(r"^\s+(d\w+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([+-]\d+\.\d+)\s+(\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+\.\d+)\s+(VOID|ok)\s*$", l)
        if m:
            r = m.group(1)
            rows.append((r, dist[r]) + m.groups()[1:] + w0[r])
        elif rows:
            break
    if len(rows) != 5:
        stop("DIAGNOSTIC 11's ladder gave %d rungs, expected five" % len(rows))
    return rows


def parse_d33b(t):
    out = {}
    for m in re.finditer(r"^\s+((?:bare|wall)_n\d+_q\d\.\d\d)\s+(\d+)\s+(\d+\.\d\d) e\s+(confirmed|outside)\s+(UNRELIABLE|RELIABLE|INCONCLUSIVE)\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)\s+(\d+\.\d\d)", t, re.M):
        out[m.group(1)] = dict(n=int(m.group(2)), sumq=float(m.group(3)), band=m.group(4), verdict=m.group(5),
                               dde=float(m.group(6)), score=float(m.group(7)), ratio=float(m.group(8)))
    if len(out) != 6:
        stop("the stage B result gave %d designs, expected six" % len(out))
    return out


def parse_stage4e(t):
    rows, fits = [], []
    sec = "first-order"
    for l in t.splitlines():
        if l.strip().startswith("polarisation part"):
            sec = "polarisation"
            continue
        if l.strip().startswith("levels:"):
            sec = None
        m = re.match(r"^\s{2}(\S.*?)\s+(?:[KC]\s+)?([+-]\d+\.\d{3})\s+([+-]\d+\.\d{3})\s+([+-]\d+\.\d{3})\s+([+-]\d+\.\d{3})\s+([+-]\d+\.\d{3})\s*$", l)
        if m and sec:
            name = re.sub(r"\s+[KC]$", "", m.group(1).strip())
            rows.append((sec if sec == "polarisation" else ("residue alone" if "alone" in name else "a at probe site"),
                         name) + m.groups()[1:])
        m = re.match(r"^\s+(L[1235]) (\S+)\s+k (\d\.\d{3})\s+residual (\d\.\d{3})", l)
        if m:
            fits.append(("fit k", m.group(1) + " " + m.group(2)) + tuple(m.group(3) if x == m.group(1) else "-" for x in ("L1", "L2", "L3", "L4", "L5")))
            fits.append(("fit residual", m.group(1) + " " + m.group(2)) + tuple(m.group(4) if x == m.group(1) else "-" for x in ("L1", "L2", "L3", "L4", "L5")))
    eleven = [r for r in rows if r[0] != "polarisation"]
    if len(eleven) != 11 or len(fits) != 8:
        stop("stage 4e's report gave %d quantities and %d fit rows, expected eleven and eight" % (len(eleven), len(fits)))
    return rows, fits


# F9: the programme as a decision tree.  Each node carries the verbatim words of the committed document
# that gives its status, so the diagram can be checked against the record by string search.
F9 = [
    # id, parent, approach, status, source file (under the results repo), verbatim words
    ("N0", "-", "frozen-geometry design: charges on a grid, chosen by a linear objective", "in use; relaxed half has no committed result",
     S6 + "/STAGE6_DIAGNOSTIC33_20261109.txt", "Stage 6's relaxed half has no committed\n   result"),
    ("N1", "N0", "bare point charges", "inside r_safe: not interpretable",
     S6 + "/standoff/DIAGNOSTIC11_RESULT.txt", "No design measured inside r_safe is interpretable."),
    ("N2", "N1", "move the charges out past r_safe (route a)", "open; D12 says it does not help",
     S6 + "/sitescan/DIAGNOSTIC12_RESULT.txt", "Moving the grid outward does not help,"),
    ("N3", "N1", "cap the charge magnitude", "PARTIAL; envelope is in (n, q), not a cap",
     S6 + "/qscale/DIAGNOSTIC13_RESULT.txt", "A single cap cannot be"),
    ("N4", "N1", "scalar budget on the charges", "ruled out; budget withdrawn",
     S6 + "/STAGE6_DIAGNOSTIC29_RESULT_20261105.txt", "NO SCALAR IN THE SET ORDERS RELOCATION."),
    ("N5", "N1", "continuum solvation (CPCM)", "NOT RECOVERED; removed by Amendment 2",
     S6 + "/cpcm/DIAGNOSTIC10_RESULT.txt", "VERDICT PER D10.3: NOT RECOVERED"),
    ("N6", "N1", "Gaussian-smeared charge", "EXPLORATORY; unquotable",
     S6 + "/STAGE6_DIAGNOSTIC27_RESULT_20261105.txt", "DIAGNOSTIC 24 as a whole remains EXPLORATORY and\nunquotable"),
    ("N7", "N1", "real ions as QM atoms (Na+, K+)", "INCONCLUSIVE; ghost control failed",
     S6 + "/pauli/DIAGNOSTIC3_RESULT.txt", "VERDICT PER D3.3: INCONCLUSIVE"),
    ("N8", "N1", "fractional charge behind a core ECP (the wall, route b)", "NOT ADOPTED, not calibrated; rescues unit charge at n <= 3",
     S6 + "/STAGE6_DIAGNOSTIC33_20261109.txt", "THE WALL IS NOT ADOPTED AND IS NOT CALIBRATED."),
    ("N9", "N8", "per-site artefact bound (Dsum against Dset)", "verdicts are a property of the parameter set",
     S6 + "/d23/DIAGNOSTIC23_RESULT.txt", "A PROPERTY OF THE PARAMETER SET"),
    ("N10", "N0", "point charges with a classical Lennard-Jones term", "L reproduced; adds no electronic repulsion",
     S6 + "/frozen/FROZEN_REPORT.txt", "agreement is a check of the grid's own\n  arithmetic and of the force field it was handed, not of any physics."),
    ("N11", "N0", "linear A-matrix objective", "retired level; corrected matrix measured, under-predicts",
     S6 + "/STAGE6_DIAGNOSTIC33_20261109.txt", "The optimiser's objective is at the retired level of theory."),
    ("N12", "N11", "production barriers at the corrected level (D34)", "measured: 3 of ten quotable, 7 UNRELIABLE",
     S6 + "/STAGE6_DIAGNOSTIC34_RESULT_20261110.txt",
     "R34.9. quotable corrected barriers: ADD-s540_qm06500 -3.3985, ADD-s678_qm07625 -4.1567, ADD-s678_qm10000 -5.3701"),
]


def build_f9(res, out):
    rows = []
    for nid, parent, approach, status, src, words in F9:
        t = " ".join((Path(res) / src).read_text(errors="replace").split())
        if " ".join(words.split()) not in t:
            stop("F9 node %s: the quoted words are not in %s" % (nid, src))
        rows.append((nid, parent, approach, status, src, " ".join(words.split())))
    write_tsv(Path(out) / "F9_decision_tree.tsv",
              ["F9. The programme as a decision tree. Each node's 'words' are verbatim (whitespace-normalised) from 'source',",
               "and make_figures.py refuses to write this file if any is not found there."],
              ["node", "parent", "approach", "status", "source", "words"], rows)


# --------------------------------------------------------------------------------------------------
# the drawings
# --------------------------------------------------------------------------------------------------
def read_tsv(p):
    rows = []
    cols = None
    for l in Path(p).read_text().splitlines():
        if l.startswith("#") or not l.strip():
            continue
        f = l.split("\t")
        if cols is None:
            cols = f
            continue
        rows.append(dict(zip(cols, f)))
    return rows


def draw(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch

    out = Path(out)
    INK, MUTE, GRID = "#1a1a1a", "#666666", "#d9d9d9"
    C1, C2, C3, C4 = "#1b6ca8", "#c8553d", "#3a7d44", "#7a5195"      # also told apart by marker and hatch
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK,
                         "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "cswu", "font.family": "DejaVu Sans", "axes.titlesize": 9.5,
                         "axes.titleweight": "bold", "legend.frameon": False})

    def save(fig, name):
        fig.savefig(out / (name + ".svg"), metadata={"Date": None})
        fig.savefig(out / (name + ".png"), dpi=200, metadata={"Software": None})
        plt.close(fig)

    # ---- F1
    r1 = [r for r in read_tsv(out / "F1_reference_barrier.tsv") if r["solvation"] == "-"]
    r1b = read_tsv(out / "F1b_stage4e_bare_barrier.tsv")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw={"width_ratios": [3, 2]}, sharey=True)
    order = ["def2-SVP", "ma-def2-SVP", "def2-SVPD", "def2-TZVPD"]
    sty = {"B3LYP": (C1, "o", "-"), "CAM-B3LYP": (C2, "s", "--"), "wB97X-D3": (C3, "^", ":")}
    for f, (col, mk, ls) in sty.items():
        pts = sorted([(order.index(r["basis"]), float(r["barrier_kcal"])) for r in r1 if r["functional"] == f])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], ls=ls, marker=mk, color=col, ms=6, lw=1.2,
                label="%s%s" % (f, "-D3BJ" if f != "wB97X-D3" else ""))
        for x, y in pts:
            below = (f == "CAM-B3LYP")
            ax.annotate("%.2f" % y, (x, y), textcoords="offset points", xytext=(0, -13 if below else 7), ha="center",
                        fontsize=7.5, color=col)
    ax.set_xticks(range(4)); ax.set_xticklabels(order); ax.set_xlim(-0.35, 3.35); ax.set_ylim(0, 42)
    ax.set_ylabel("E(TS) − E(R), bare substrate (kcal/mol)")
    ax.set_title("Frame 42436, frozen geometries, in vacuo")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.legend(loc="lower center", fontsize=8, ncol=3, bbox_to_anchor=(0.5, 0.05))
    ax.set_xlabel("basis set (a line joins one functional across bases; nothing is implied between functionals)")
    xs = range(len(r1b))
    bx.bar(xs, [float(r["barrier_kcal"]) for r in r1b], color="#bdbdbd", edgecolor=INK, hatch="//", width=0.6)
    for x, r in zip(xs, r1b):
        bx.annotate(r["barrier_kcal"], (x, float(r["barrier_kcal"])), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=7.5)
    lab = {"L1": "B3LYP-D3BJ\ndef2-SVP", "L2": "B3LYP\n6-31G(d)", "L3": "HF\n6-31G(d)", "L4": "MP2\n6-31G(d)", "L5": "wB97X-D3\ndef2-SVP"}
    bx.set_xticks(list(xs)); bx.set_xticklabels([lab[r["level"]] for r in r1b], fontsize=7.5)
    bx.set_title("Frame 41786 (Stage 4e): a different frame")
    bx.grid(axis="y", color=GRID, lw=0.6)
    fig.tight_layout(); save(fig, "F1_reference_barrier")

    # ---- F2
    r2 = read_tsv(out / "F2_stage4e.tsv")
    q = [r for r in r2 if r["kind"] in ("residue alone", "a at probe site")]
    kfit = {r["quantity"].split()[0]: float(r[r["quantity"].split()[0]]) for r in r2 if r["kind"] == "fit k"}
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    lv = {"L1": (C1, "o", "L1 B3LYP-D3BJ/def2-SVP"), "L2": (C4, "D", "L2 B3LYP/6-31G(d)"), "L3": (C2, "s", "L3 HF/6-31G(d)"),
          "L5": (C3, "^", "L5 wB97X-D3/def2-SVP")}
    lo, hi = -9.0, 8.0
    for k, (col, mk, lb) in lv.items():
        ax.scatter([float(r[k]) for r in q], [float(r["L4"]) for r in q], marker=mk, s=26, facecolors="none" if mk != "o" else col,
                   edgecolors=col, linewidths=1.1, label="%s  (k = %.3f)" % (lb, kfit[k]), zorder=3)
        ax.plot([lo, hi], [kfit[k] * lo, kfit[k] * hi], color=col, lw=0.8, ls={"L1": "-", "L2": "-.", "L3": "--", "L5": ":"}[k])
    ax.plot([lo, hi], [lo, hi], color=MUTE, lw=0.6); ax.text(hi - 0.2, hi - 0.9, "y = x", color=MUTE, fontsize=7.5, ha="right")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel("barrier change at the level shown (kcal/mol)")
    ax.set_ylabel("barrier change at L4, MP2/6-31G(d) (kcal/mol)")
    ax.set_title("Stage 4e: eleven quantities, fitted L4 = k × level")
    ax.grid(color=GRID, lw=0.6); ax.legend(fontsize=7.5, loc="upper left")
    fig.tight_layout(); save(fig, "F2_stage4e")

    # ---- F3
    r3 = read_tsv(out / "F3_nq_grid.tsv")
    ns = [1, 2, 3, 5, 10, 20]
    cols3 = [("B", "0.25"), ("B", "0.50"), ("B", "0.75"), ("B", "1.00"), ("A", "1.00")]
    face = {"RELIABLE": ("#d5ead8", "", "#d5ead8"), "UNRELIABLE": ("#f7ddd6", "///", "#e3a797"),
            "INCONCLUSIVE": ("#f1f1f1", "..", "#b5b5b5")}
    plt.rcParams["hatch.linewidth"] = 0.5
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharey=True)
    for ax, key, title in ((axes[0], "d31_verdict", "bare point charges (DIAGNOSTIC 31)"),
                           (axes[1], "d32_verdict", "argon ECP centres (DIAGNOSTIC 32, committed verdict)")):
        for r in r3:
            x = cols3.index((r["family"], r["q_e"])); y = ns.index(int(r["n"]))
            fc, ht, hc = face[r[key]]
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=fc, edgecolor=hc, hatch=ht, lw=0))
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor="none", edgecolor=INK, lw=0.6))
            word = {"RELIABLE": "reliable", "UNRELIABLE": "UNRELIABLE", "INCONCLUSIVE": "inconclusive"}[r[key]]
            box = dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.2)
            post = key == "d32_verdict" and r["erratum1_posthoc"] != "-"
            ax.text(x + 0.5, y + (0.66 if post else 0.5), word, ha="center", va="center", fontsize=7.0, bbox=box)
            if post:
                ax.text(x + 0.5, y + 0.27, "Erratum 1, post hoc:\ninconclusive", ha="center", va="center", fontsize=5.6,
                        color="#333333", bbox=box)
        ax.set_xlim(0, 5); ax.set_ylim(0, 6)
        ax.set_xticks([i + 0.5 for i in range(5)]); ax.set_xticklabels(["0.25", "0.50", "0.75", "1.00", "1.00\n(optimiser's\nunit designs)"], fontsize=8)
        ax.set_yticks([i + 0.5 for i in range(6)]); ax.set_yticklabels([str(n) for n in ns])
        ax.set_xlabel("charge on each sphere, |q| (e)"); ax.set_title(title)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    axes[0].set_ylabel("number of spheres, n")
    fig.tight_layout(); save(fig, "F3_nq_grid")

    # ---- F4
    r4 = [r for r in read_tsv(out / "F4_relocation.tsv") if r["family"] != "wall0"]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for arm, col, mk, lb in (("bare", C2, "s", "bare point charges (D31)"), ("walled", C1, "o", "same charges on argon ECP centres (D32)")):
        pts = [(float(r["sum_abs_q_e"]), float(r["rise_max_e"])) for r in r4 if r["arm"] == arm]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker=mk, s=28, facecolors="none" if arm == "bare" else col,
                   edgecolors=col, linewidths=1.1, label=lb, zorder=3)
    ax.axhline(0.25, color=INK, lw=0.9, ls="--"); ax.text(0.26, 0.27, "D_LW = 0.25 e", fontsize=8, va="bottom")
    ax.set_xscale("log"); ax.set_xlabel("Σ|q| (e), logarithmic")
    ax.set_ylabel("Loewdin rise over the charge-free control (e),\nlarger of the two states")
    ax.set_title("Relocation against total charge: no threshold in Σ|q|")
    ax.grid(color=GRID, lw=0.6); ax.legend(fontsize=8, loc="center right")
    fig.tight_layout(); save(fig, "F4_relocation")

    # ---- F5
    r5 = read_tsv(out / "F5_distance_ladder.tsv")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.6, 4.0))
    d = [float(r["d_A"]) for r in r5]
    ax.plot(d, [float(r["ddE_bare_kcal"]) for r in r5], marker="s", color=C2, mfc="none", lw=1.1, label="bare +1 point charge")
    ax.plot(d, [float(r["ddE_wall_kcal"]) for r in r5], marker="o", color=C1, lw=1.1, ls="--", label="same charge behind a neon ECP wall")
    void = [r for r in r5 if r["wall_status"] == "VOID"]
    for r in void:
        ax.annotate("wall not inert:\nrung voided", (float(r["d_A"]), float(r["ddE_wall_kcal"])), textcoords="offset points",
                    xytext=(8, -4), fontsize=7.5, color=MUTE)
    ax.axvline(3.50, color=INK, lw=0.9, ls=":"); ax.text(3.56, -2.4, "r_safe = 3.50 Å", fontsize=8)
    ax.set_xlabel("stand-off distance d of the charge (Å)"); ax.set_ylabel("ddE (kcal/mol)")
    ax.set_title("The ladder (points joined for the eye; five rungs measured)"); ax.grid(color=GRID, lw=0.6); ax.legend(fontsize=8, loc="lower right")
    bx.plot(d, [abs(float(r["d_shield_kcal"])) for r in r5], marker="D", color=C4, lw=1.1, label="|d_shield| = |ddE(wall) − ddE(bare)|")
    bx.plot(d, [float(r["bar_kcal"]) for r in r5], marker="_", color=INK, lw=0.9, ls="--", ms=10, label="tolerance: max(10 % of |ddE(bare)|, 0.05)")
    bx.axvline(3.50, color=INK, lw=0.9, ls=":"); bx.text(3.55, 2.0, "r_safe = 3.50 Å", fontsize=8)
    bx.set_yscale("log"); bx.set_xlabel("stand-off distance d of the charge (Å)"); bx.set_ylabel("kcal/mol, logarithmic")
    bx.set_title("The shielding term against its tolerance"); bx.grid(color=GRID, lw=0.6, which="both"); bx.legend(fontsize=7.5, loc="lower left")
    fig.tight_layout(); save(fig, "F5_distance_ladder")

    # ---- F6
    r6 = read_tsv(out / "F6_predicted_vs_measured.tsv")
    dv = {r["id"]: r["value"] for r in read_tsv(out / "derived.tsv")}
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4), sharex=True, sharey=True)
    lo, hi = -27.0, 0.0
    for ax, lev, title, band in ((axes[0], "B3LYP-D3BJ/def2-SVP", "Frozen half, B3LYP-D3BJ/def2-SVP (old level)", ("DV52", "DV53")),
                                 (axes[1], "CAM-B3LYP-D3BJ/def2-SVPD", "D33 stage B, CAM-B3LYP-D3BJ/def2-SVPD", ("DV50", "DV51"))):
        rr = [r for r in r6 if r["level"] == lev]
        a, b = float(dv[band[0]]), float(dv[band[1]])
        ax.fill_between([lo, hi], [a * lo, a * hi], [b * lo, b * hi], color="#dddddd", zorder=1,
                        label="measured/predicted from %s to %s" % (dv[band[0]], dv[band[1]]))
        ax.plot([lo, hi], [lo, hi], color=MUTE, lw=0.7, zorder=2); ax.text(lo + 0.6, lo + 2.0, "y = x", color=MUTE, fontsize=7.5)
        mk = {"NOT FLAGGED (3 LEGS)": ("o", C1, False), "NOT FLAGGED (2 LEGS, GAP DARK)": ("s", C1, False),
              "RELIABLE": ("o", C3, True), "INCONCLUSIVE": ("D", MUTE, False), "UNRELIABLE": ("x", C2, True)}
        words = {"NOT FLAGGED (3 LEGS)": "not flagged on 3 legs (post hoc; no verdict)",
                 "NOT FLAGGED (2 LEGS, GAP DARK)": "not flagged on 2 legs, gap dark (post hoc)"}
        seen = set()
        for r in rr:
            m, col, fill = mk[r["verdict"]]
            lb = words.get(r["verdict"], r["verdict"].lower()) if r["verdict"] not in seen else None
            seen.add(r["verdict"])
            if m == "x":
                ax.scatter(float(r["score_kcal"]), float(r["ddE_kcal"]), marker=m, color=col, s=42, zorder=4, label=lb)
            else:
                ax.scatter(float(r["score_kcal"]), float(r["ddE_kcal"]), marker=m, s=30, facecolors=col if fill else "none",
                           edgecolors=col, zorder=4, label=lb)
            if lev.startswith("CAM"):
                off = (-6, -11) if r["design"].startswith("wall_n02") else (5, 4)
                ax.annotate(r["design"].replace("_", " "), (float(r["score_kcal"]), float(r["ddE_kcal"])), textcoords="offset points",
                            xytext=off, fontsize=6.8, ha="right" if off[0] < 0 else "left")
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_title(title); ax.grid(color=GRID, lw=0.6)
        ax.set_xlabel("linear score Σ a·q + Σ L (kcal/mol)"); ax.legend(fontsize=7.2, loc="lower right")
    axes[0].set_ylabel("measured ddE (kcal/mol)")
    fig.tight_layout(); save(fig, "F6_predicted_vs_measured")

    # ---- F7
    r7 = read_tsv(out / "F7_production_designs.tsv")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.6, 5.0), gridspec_kw={"width_ratios": [3, 2]})
    order = sorted(range(len(r7)), key=lambda i: (float(r7[i]["sum_abs_q_e"]), r7[i]["arrangement"]))
    names = [r7[i]["arrangement"] for i in order]
    ys = list(range(len(order)))[::-1]
    for y, i in zip(ys, order):
        r = r7[i]
        vals = [float(r["ddE_recomputed_kcal"]), float(r["ddE_arm1_kcal"]), float(r["ddE_arm2_kcal"])]
        ax.plot([min(vals), max(vals)], [y, y], color=GRID, lw=1.0, zorder=1)
        ax.scatter(vals[0], y, marker="o", s=34, facecolors="none", edgecolors=MUTE, linewidths=1.1, zorder=3)
        ax.scatter(vals[1], y, marker="s", s=30, facecolors="none", edgecolors=C4, linewidths=1.1, zorder=3)
        if r["verdict_arm2"] == "RELIABLE":
            ax.scatter(vals[2], y, marker="D", s=34, color=C3, zorder=4)
        else:
            ax.scatter(vals[2], y, marker="x", s=46, color=C2, linewidths=1.6, zorder=4)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(ys); ax.set_yticklabels(["%s   (n = %s, Σ|q| = %s e)" % (n, r7[i]["n"], r7[i]["sum_abs_q_e"]) for n, i in zip(names, order)], fontsize=7.6)
    ax.set_xlabel("ddE (kcal/mol); each level against its own reference barrier")
    ax.set_title("Ten production arrangements at three readings")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="none", mec=MUTE, label="old level, B3LYP-D3BJ/def2-SVP (no four-leg verdict)"),
                       Line2D([], [], marker="s", ls="", mfc="none", mec=C4, label="arm 1, CAM-B3LYP-D3BJ/def2-SVPD, first SCF solution"),
                       Line2D([], [], marker="D", ls="", color=C3, label="arm 2, with stability analysis: RELIABLE"),
                       Line2D([], [], marker="x", ls="", color=C2, mew=1.6, label="arm 2: UNRELIABLE (not quotable)")],
              fontsize=7.4, loc="lower left", bbox_to_anchor=(0.0, 1.07), ncol=2)
    ax.grid(axis="x", color=GRID, lw=0.6)
    r3d = read_tsv(out / "T3_d34_arms.tsv")
    by = {r["arrangement"]: r for r in r3d}
    for y, n in zip(ys, names):
        r = by[n]
        a_ = max(float(r["A_rise_R"]), float(r["A_rise_TS"]))
        b_ = max(float(r["a1_rise_R"]), float(r["a1_rise_TS"]))
        c_ = max(float(r["a2_rise_R"]), float(r["a2_rise_TS"]))
        bx.plot([a_, max(b_, c_)], [y, y], color=GRID, lw=1.0, zorder=1)
        bx.scatter(a_, y, marker="o", s=34, facecolors="none", edgecolors=MUTE, linewidths=1.1, zorder=3)
        bx.scatter(b_, y, marker="s", s=30, facecolors="none", edgecolors=C4, linewidths=1.1, zorder=3)
        bx.scatter(c_, y, marker="D" if r["a2_verdict"] == "RELIABLE" else "x", s=34 if r["a2_verdict"] == "RELIABLE" else 46,
                   color=C3 if r["a2_verdict"] == "RELIABLE" else C2, zorder=4)
    bx.axvline(0.25, color=INK, lw=0.9, ls="--"); bx.text(0.28, 4.5, "D_LW = 0.25 e", fontsize=7.6, va="center")
    bx.set_yticks(ys); bx.set_yticklabels([]); bx.set_ylim(ax.get_ylim())
    bx.set_xlabel("Loewdin rise over the same reading's control (e),\nlarger of the two states")
    bx.set_title("The relocation leg at the same three readings")
    bx.grid(axis="x", color=GRID, lw=0.6)
    fig.tight_layout(); save(fig, "F7_production_designs")

    # ---- F8
    r8 = read_tsv(out / "F8_A_matrix.tsv")
    xo = [float(r["a_old"]) for r in r8]; xn = [float(r["a_new"]) for r in r8]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    ax.scatter(xo, xn, s=3, color=C1, alpha=0.45, linewidths=0, rasterized=True)
    lo, hi = -9.0, 10.0
    ax.plot([lo, hi], [lo, hi], color=MUTE, lw=0.7); ax.text(hi - 0.3, hi - 1.3, "y = x", color=MUTE, fontsize=7.5, ha="right")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel("a_i, B3LYP-D3BJ/def2-SVP (kcal/mol per e)"); ax.set_ylabel("a_i, CAM-B3LYP-D3BJ/def2-SVPD (kcal/mol per e)")
    ax.set_title("Every site, before and after"); ax.grid(color=GRID, lw=0.6)
    dd = [n - o for o, n in zip(xo, xn)]
    bx.hist(dd, bins=60, color="#bdbdbd", edgecolor=INK, lw=0.3)
    bx.axvline(0, color=INK, lw=0.8)
    bx.set_xlabel("a_new − a_old (kcal/mol per e)"); bx.set_ylabel("number of sites"); bx.set_title("The change, site by site")
    bx.grid(axis="y", color=GRID, lw=0.6)
    fig.tight_layout(); save(fig, "F8_A_matrix")

    # ---- F9
    r9 = read_tsv(out / "F9_decision_tree.tsv")
    kids = {}
    for r in r9:
        kids.setdefault(r["parent"], []).append(r["node"])
    by = {r["node"]: r for r in r9}
    pos = {}
    ycur = [0]

    def place(n, depth):
        ch = kids.get(n, [])
        if not ch:
            pos[n] = (depth, ycur[0]); ycur[0] += 1
        else:
            for c in ch:
                place(c, depth + 1)
            pos[n] = (depth, sum(pos[c][1] for c in ch) / len(ch))
    place("N0", 0)
    fig, ax = plt.subplots(figsize=(13.0, 6.6))
    W, Hh, DX = 3.6, 0.8, 4.0
    maxdepth = max(p[0] for p in pos.values())
    tone = {"in use": "#e8eef5", "open": "#fff4d6", "not": "#f2cfc7", "none": "#eeeeee"}

    def tint(s):
        s = s.lower()
        if s.startswith(("ruled out", "inconclusive", "exploratory", "not recovered", "inside r_safe", "not adopted", "verdicts are")):
            return tone["not"]
        if s.startswith(("open", "partial", "pre-registered", "retired")):
            return tone["open"]
        return tone["in use"]
    import textwrap
    for n, (dx, y) in pos.items():
        x = dx * DX
        r = by[n]
        ax.add_patch(FancyBboxPatch((x, -y - Hh / 2), W, Hh, boxstyle="round,pad=0.02,rounding_size=0.08", facecolor=tint(r["status"]),
                                    edgecolor=INK, lw=0.7))
        ax.text(x + 0.1, -y + 0.17, "\n".join(textwrap.wrap(r["approach"], 40)), fontsize=7.0, va="center", fontweight="bold")
        ax.text(x + 0.1, -y - 0.2, "\n".join(textwrap.wrap(r["status"], 50)), fontsize=6.4, va="center", color="#333333")
        if r["parent"] in pos:
            px, py = pos[r["parent"]]
            ax.plot([px * DX + W, px * DX + W + 0.3, px * DX + W + 0.3, x], [-py, -py, -y, -y], color=INK, lw=0.7)
    ax.set_xlim(-0.2, maxdepth * DX + W + 0.2); ax.set_ylim(-ycur[0] + 0.3, 0.7); ax.axis("off")
    ax.set_title("The programme as a decision tree: each approach and the record's own status for it", loc="left")
    fig.tight_layout(); save(fig, "F9_decision_tree")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tsv-only", action="store_true")
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    r = build(a.res, a.code, a.out)
    build_f9(a.res, a.out)
    print("controls: %d, failing: %d; run directories walked under %s: %d" % (len(r["controls"]), len(r["bad"]), S6, r["ndirs"]))
    for c in r["bad"]:
        print("   FAIL  %s  %s  recomputed %s  record %s" % (c[0], c[1], c[2], c[3]))
    if not a.tsv_only:
        draw(a.out)
        print("figures drawn")
    return 1 if r["bad"] else 0


if __name__ == "__main__":
    sys.exit(main())
