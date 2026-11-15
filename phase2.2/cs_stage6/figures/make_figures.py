#!/usr/bin/env python3
"""Figures and tables for WRITEUP_CONSOLIDATED_20261111.md, drawn only from committed files.

    python3 make_figures.py --res <results repo> --code <code repo> --out <this directory> [--tsv-only]

What it does, in order:

  1. loads the COMMITTED readers by path - phase2.2/cs6_audit.py (the classifier and its thresholds),
     phase2.2/cs6_d33b.py (the stability block and the level-shift markers) and phase2.2/cs6_analyse.py
     (the bare / (MM) / (QM/MM) energy convention) - so that every number here is read the way the
     record reads it;
  2. writes one .tsv per figure (F1 .. F12) and per table (T3 .. T13), plus controls.tsv (quantities recomputed from raw outputs
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
FUNCS = ["CAM-B3LYP", "WB97X-D3", "B3LYP"]            # the three functionals of the record up to DIAGNOSTIC 34
# every method keyword that heads a committed charge-free single point on frame 42436, as ORCA's keyword line
# spells it in upper case.  A keyword line is split on white space and matched token by token, so WB97X-V is not
# WB97X-D3 and RI-PWPB95 is not PW6B95.
METHODS = ["DLPNO-CCSD(T)", "CAM-B3LYP", "WB97X-D3", "WB97M-V", "WB97X-V", "PW6B95", "M062X", "RI-PWPB95",
           "REVDSD-PBEP86-D4/2021", "B3LYP", "HF", "MP2"]
# REVDSD-PBEP86-D4/2021 is the keyword DIAGNOSTIC 37's Amendment 1 ran.  The keyword D37 itself tried,
# RI-REVDSD-PBEP86-D4/2021, was rejected by ORCA, left no normally terminated output, and is not in this list.
# the order of the rows of F1: the record's three functionals first, as before, then the rest
METHOD_ORDER = ["B3LYP", "CAM-B3LYP", "WB97X-D3", "PW6B95", "RI-PWPB95", "REVDSD-PBEP86-D4/2021", "WB97M-V", "M062X", "WB97X-V",
                "HF", "MP2", "DLPNO-CCSD(T)"]
BASIS_ORDER = ["6-31G(D)", "DEF2-SVP", "MA-DEF2-SVP", "DEF2-SVPD", "DEF2-TZVPD"]
BASES = ["DEF2-TZVPD", "MA-DEF2-SVP", "DEF2-SVPD", "DEF2-SVP", "6-31G(D)"]
PRETTY = {"CAM-B3LYP": "CAM-B3LYP", "WB97X-D3": "wB97X-D3", "B3LYP": "B3LYP", "HF": "HF", "MP2": "MP2",
          "WB97M-V": "wB97M-V", "WB97X-V": "wB97X-V", "PW6B95": "PW6B95", "M062X": "M06-2X", "RI-PWPB95": "PWPB95",
          "DLPNO-CCSD(T)": "DLPNO-CCSD(T)", "REVDSD-PBEP86-D4/2021": "revDSD-PBEP86-D4",
          "DEF2-TZVPD": "def2-TZVPD", "MA-DEF2-SVP": "ma-def2-SVP", "DEF2-SVPD": "def2-SVPD",
          "DEF2-SVP": "def2-SVP", "6-31G(D)": "6-31G(d)"}
EV = 27.211386245988        # eV per Eh (CODATA 2018)


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
    f = next((x for x in METHODS if x in kw), "?")
    b = next((x for x in BASES if x in kw), "?")
    d = "D3BJ" if "D3BJ" in kw else ("D3ZERO" if "D3ZERO" in kw else "-")
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
        c["chmult"] = (sorted(set(re.findall(r"^\s*Total Charge\s+Charge\s+\.+\s+(-?\d+)\s*$", t, re.M))),
                       sorted(set(re.findall(r"^\s*Multiplicity\s+Mult\s+\.+\s+(\d+)\s*$", t, re.M))))
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
        if c["chmult"] != (["-2"], ["1"]):
            continue                               # the pool is the dianion, a closed-shell singlet: a monoanion on the
                                                   # same geometry at the same keywords (D39, D40) is another species
        st = state_of(c)
        if st is None:
            continue
        pool.setdefault((f, b, disp, cp), {}).setdefault(st, []).append((rel, c))
    f1 = []
    barrier = {}
    for key in sorted(pool, key=lambda k: (METHOD_ORDER.index(k[0]), BASIS_ORDER.index(k[1]), k[3])):
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
                   fmt(bar, 6), len(g["R"]), len(g["TS"]), "%.1e" % spread, fmt(cR["homo"], 4), rR, rT,
                   fmt(cT["homo"], 4), "yes" if (cR["shifted"] or cT["shifted"]) else "no"))
    write_tsv(out / "F1_reference_barrier.tsv",
              ["F1. Barrier E(TS)-E(R) of the bare substrate (no charges, no wall, in vacuo unless CPCM), frozen geometries of",
               "frame 42436, recomputed from every charge-free committed single point under %s." % S6,
               "Geometry is recognised by its interatomic distances against d33a/sp_42436_{R,TS}/substrate.xyz, not by directory name.",
               "n_R, n_TS: how many committed runs give that energy; spread_Eh: the largest disagreement among them.",
               "Energies through the committed phase2.2/cs6_audit.py read(); conversion %.10f kcal/mol per Eh." % H,
               "functional: the method of the keyword line (PWPB95 is run as RI-PWPB95, M06-2X as M062X; HF, MP2 and DLPNO-CCSD(T)",
               "are not functionals).  The energy is the last FINAL SINGLE POINT ENERGY, which for MP2, PWPB95 and DLPNO-CCSD(T)",
               "includes the correlation part.  HOMO_*_eV is the highest occupied orbital of the self-consistent-field step;",
               "level_shift: whether a level shift or TRAH was engaged in either run, in which case the record does not quote it.",
               "Only runs that ORCA reports as total charge -2 and multiplicity 1 are pooled: the monoanion single points of",
               "DIAGNOSTICS 39 and 40 stand on the same geometries at the same keyword lines and are not the bare dianion.",
               "revDSD-PBEP86-D4 is DIAGNOSTIC 37 Amendment 1 (keyword revDSD-PBEP86-D4/2021); its two arms ran the same calculation,",
               "so n_R and n_TS are 2.  DLPNO-CCSD(T)/def2-SVPD is DIAGNOSTIC 41: the reactant is d38/N, the transition state d41/T."],
              ["functional", "basis", "dispersion", "solvation", "nbasis", "E_R_Eh", "E_TS_Eh", "barrier_kcal",
               "n_R", "n_TS", "spread_Eh", "HOMO_R_eV", "example_R", "example_TS", "HOMO_TS_eV", "level_shift"], f1)

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
    rep4 = (res / "phase2.2" / "cs_stage4e" / "STAGE4E_REPORT.txt").read_text()
    f2, fits = parse_stage4e(rep4)

    def set_of(kind, name):                    # the report marks each row C (beside a carboxylate), K (control) or nothing
        if kind not in ("residue alone", "a at probe site"):
            return "-"
        m = re.search(r"^\s*%s\s+([CK])?\s*[+-]\d" % re.escape(name), rep4, re.M)
        if not m:
            stop("Stage 4e's report has no row for %s" % name)
        return m.group(1) or "-"
    f2 = [tuple(r) + (set_of(r[0], r[1]),) for r in f2]
    fits = [tuple(r) + ("-",) for r in fits]
    write_tsv(out / "F2_stage4e.tsv",
              ["F2. Stage 4e: eleven barrier-change quantities at five levels, kcal/mol, QM part, frame 41786 (not 42436).",
               "Parsed from phase2.2/cs_stage4e/STAGE4E_REPORT.txt. L1 B3LYP-D3BJ/def2-SVP; L2 B3LYP/6-31G(d); L3 HF/6-31G(d);",
               "L4 MP2/6-31G(d) (the reference); L5 wB97X-D3/def2-SVP. fit rows: L4 = k x level over the eleven values, with the report's residual.",
               "set: C, beside a carboxylate, and K, control, as the report marks the rows; its sign test is on these."],
              ["kind", "quantity", "L1", "L2", "L3", "L4", "L5", "set"], f2 + fits)
    DV.add("DV182", str(sum(1 for r in f2 if r[-1] == "C")), "count", "Stage 4e quantities the report marks C, beside a carboxylate", "figures/F2_stage4e.tsv")
    DV.add("DV183", str(sum(1 for r in f2 if r[-1] == "K")), "count", "Stage 4e quantities the report marks K, control", "figures/F2_stage4e.tsv")

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
        # the same level on frame 42436's geometries: DIAGNOSTIC 35, whose inputs are Stage 4e's own
        d35 = {}
        for st in ("R", "TS"):
            c = run(root / "d35" / ("%s_%s" % (lv, st)))
            if c is None or not c["norm"] or c["notconv"] or c["npc"] or state_of(c) != st:
                stop("d35/%s_%s is not a normally terminated, converged, charge-free run on frame 42436's %s geometry" % (lv, st, st))
            if keyword_line((root / "d35" / ("%s_%s" % (lv, st)) / "job.out").read_text(errors="replace")) != kw:
                stop("d35/%s_%s does not carry Stage 4e's keyword line" % (lv, st))
            d35[st] = c["E"]
        b41, b42 = (e["TS"] - e["R"]) * H, (d35["TS"] - d35["R"]) * H
        s4e.append((lv, kw.lstrip("! ").strip(), fmt(e["R"], 9), fmt(e["TS"], 9), fmt(b41, 4),
                    fmt(d35["R"], 9), fmt(d35["TS"], 9), fmt(b42, 4), fmt(b42 - b41, 4), b41, b42))
    rank41 = [r[0] for r in sorted(s4e, key=lambda r: r[9])]
    rank42 = [r[0] for r in sorted(s4e, key=lambda r: r[10])]
    write_tsv(out / "F1b_stage4e_bare_barrier.tsv",
              ["F1b. Barrier of the bare substrate at Stage 4e's five levels at TWO frames, in vacuo.",
               "frame 41786: phase2.2/cs_stage4e/L<k>_bare_{R,TS}/job.out.xz (Stage 4e's own runs; its reactant is NEB band image 0).",
               "frame 42436: %s/d35/L<k>_{R,TS}/job.out (DIAGNOSTIC 35; the same input file on the Stage 6 geometries)." % S6,
               "Last FINAL SINGLE POINT ENERGY of each.  difference = frame 42436 minus frame 41786.",
               "Lowest barrier first: frame 41786 %s; frame 42436 %s." % (" ".join(rank41), " ".join(rank42))],
              ["level", "keyword_line", "E_R_41786_Eh", "E_TS_41786_Eh", "barrier_41786_kcal",
               "E_R_42436_Eh", "E_TS_42436_Eh", "barrier_42436_kcal", "difference_kcal"], [r[:9] for r in s4e])
    # controls: both columns against the table DIAGNOSTIC 35's own reader committed
    D35T = S6 + "/d35.tsv"
    rec35 = {}
    for l in (root / "d35.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        rec35[f[0]] = (float(f[2]), float(f[3]), float(f[4]), float(f[5]))
    for i, r in enumerate(s4e):
        control("C40.%02d" % (2 * i + 1), "barrier, Stage 4e level %s, frame 41786 (d35.tsv)" % r[0], r[9], rec35[r[0]][0], D35T, 5e-7, 6)
        control("C40.%02d" % (2 * i + 2), "barrier, Stage 4e level %s, frame 42436 (d35.tsv)" % r[0], r[10], rec35[r[0]][1], D35T, 5e-7, 6)

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
    # DV20 to DV26 keep the levels they were first given.  wB97X-D3/def2-SVP did not exist at frame 42436 until
    # DIAGNOSTIC 35 and has its own row in DV210 onward, so that no earlier identifier changes its meaning.
    for (f, b, cp) in (("CAM-B3LYP", "DEF2-SVP", "-"), ("CAM-B3LYP", "DEF2-TZVPD", "-"),
                       ("WB97X-D3", "DEF2-SVPD", "-"), ("WB97X-D3", "DEF2-TZVPD", "-"), ("B3LYP", "MA-DEF2-SVP", "CPCM"),
                       ("B3LYP", "DEF2-SVPD", "-"), ("CAM-B3LYP", "DEF2-SVPD", "-")):
        key = next((kk for kk in barrier if kk[0] == f and kk[1] == b and kk[3] == cp), None)
        if key is None:
            stop("no charge-free pair for %s/%s %s" % (f, b, cp))
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
    # ============================ F10: the highest occupied orbital by functional (DIAGNOSTIC 28) ==============
    # Why B3LYP was retired for the dianion.  The twelve charge-free orbital energies are recomputed from the raw
    # outputs through the committed reader and compared with DIAGNOSTIC 28's committed table; the detachment energy is
    # recomputed from Probe 3's monoanion and the dianion it was paired with.
    D28T, P3R = S6 + "/d28/d28.tsv", S6 + "/vde_designs/PROBE3_RESULT.txt"

    def raw_text(d):
        q = Path(d) / "job.out"
        return q.read_text(errors="replace") if q.is_file() else lzma.open(str(q) + ".xz", "rt", errors="replace").read()
    rec28, lrx = {}, {}
    for l in (root / "d28" / "d28.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        if len(f) >= 6 and f[5] == "yes":
            rec28[(f[0], f[2], f[3])] = float(f[4])
            lrx[f[0]] = f[1]
    f10, k10 = [], 0
    for key, shown, pat in (("B3LYP", "B3LYP-D3BJ", "d27/%s/ctl_%s"), ("CAM-B3LYP", "CAM-B3LYP-D3BJ", "d28/CAM-B3LYP/%s/ctl_%s"),
                            ("wB97X-D3", "wB97X-D3", "d28/wB97X-D3/%s/ctl_%s")):
        for b in ("def2-SVPD", "def2-TZVPD"):
            for st in ("R", "TS"):
                rel = pat % (b, st)
                c = audit.read(raw_text(root / rel))
                if c is None or not c["norm"] or c["notconv"] or c["npc"] != 0:
                    stop("%s/%s is not a normally terminated, converged, charge-free run" % (S6, rel))
                if (key, b, st) not in rec28:
                    stop("d28.tsv has no quotable row for %s %s %s" % (key, b, st))
                k10 += 1
                control("C31.%02d" % k10, "highest occupied orbital, %s/%s %s (eV)" % (shown, b, st), c["homo"], rec28[(key, b, st)], D28T, 1.0e-4, 4)
                f10.append([shown, lrx[key], b, st, c["homo"], rec28[(key, b, st)], "%s/%s" % (S6, rel)])
    tm = raw_text(root / "vde_designs" / "S6-C_mono")       # open-shell, which the committed reader does not parse
    if "ORCA TERMINATED NORMALLY" not in tm:
        stop("Probe 3's monoanion output did not terminate normally")
    vde = (float(re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", tm)[-1]) - audit.read(raw_text(root / "cpcm" / "S6-C_R_vac"))["E"]) * EV
    m = re.search(r"S6-C\s+0\s+0\.00 e\s+\+(\d\.\d{4})\s+bound", (root / "vde_designs" / "PROBE3_RESULT.txt").read_text())
    if not m:
        stop("Probe 3's result does not print the bare dianion's detachment energy")
    m_p3 = m
    control("C32", "detachment energy of the bare dianion, monoanion minus dianion (eV)", vde, float(m.group(1)), P3R, 1.0e-4, 4)
    target = -float(m.group(1))
    write_tsv(out / "F10_homo_by_functional.tsv",
              ["F10. Highest occupied orbital of the BARE substrate (no charges), frame 42436, frozen geometries, in vacuo.",
               "homo_eV: recomputed from the raw output through the committed phase2.2/cs6_audit.py read(); d28_eV: DIAGNOSTIC 28's committed d28/d28.tsv.",
               "target_eV: minus Probe 3's detachment energy, E(monoanion) - E(dianion), B3LYP-D3BJ/ma-def2-SVP, at the reactant geometry.",
               "It is a computed energy difference and not an experiment; recomputed here it is %s eV." % fmt(vde, 4),
               "minus_target_eV = d28_eV - target_eV, DERIVED here from the committed values; positive means the orbital sits too high.",
               "Reactant rows only: Probe 3 measured the detachment energy at the reactant and says nothing about the transition state.",
               "DIAGNOSTIC 28 says of itself that it does not establish which functional is correct."],
              ["functional", "long_range_exact_exchange", "basis", "state", "homo_eV", "d28_eV", "target_eV", "minus_target_eV", "raw_output"],
              [(r[0], r[1], r[2], r[3], fmt(r[4], 4), fmt(r[5], 4), fmt(target, 4), fmt(r[5] - target, 4) if r[3] == "R" else "-", r[6]) for r in f10])
    F10T = "figures/F10_homo_by_functional.tsv"
    prim = {r[0]: r[5] - target for r in f10 if r[2] == "def2-SVPD" and r[3] == "R"}
    DV.add("DV170", "%.4f" % abs(prim["B3LYP-D3BJ"]), "derived", "B3LYP-D3BJ/def2-SVPD, reactant: highest occupied orbital minus the target (eV); above it", F10T)
    DV.add("DV171", "%.4f" % abs(prim["CAM-B3LYP-D3BJ"]), "derived", "CAM-B3LYP-D3BJ/def2-SVPD, reactant: target minus highest occupied orbital (eV); below it", F10T)
    DV.add("DV172", "%.4f" % abs(prim["wB97X-D3"]), "derived", "wB97X-D3/def2-SVPD, reactant: target minus highest occupied orbital (eV); below it", F10T)
    DV.add("DV173", str(len(f10)), "count", "charge-free orbital energies recomputed for F10 and compared with d28.tsv", F10T)
    DV.add("DV174", str(sum(1 for r in f10 if r[0] == "B3LYP-D3BJ" and r[5] > 0)), "count", "of the four B3LYP-D3BJ values, those above the vacuum level", F10T)
    DV.add("DV175", str(sum(1 for r in f10 if r[0] != "B3LYP-D3BJ" and r[5] < 0)), "count", "of the eight values of the other two functionals, those below the vacuum level", F10T)
    DV.add("DV180", str(len(list((root / "d35").rglob("job.inp")))), "count", "number of committed job.inp files under %s/d35" % S6, S6 + "/d35")
    DV.add("DV181", str(len(list((root / "d35").rglob("job.out"))) + len(list((root / "d35").rglob("job.out.xz")))), "count",
           "number of committed job.out files under %s/d35" % S6, S6 + "/d35")

    # ============================ DIAGNOSTICS 35 to 38: the level of theory, measured ==============
    # D35 is in F1b above.  D36 is the correlated benchmark for the bare barrier, D37 five further functionals on the
    # same two geometries, D38 a probe of whether an embedding charge reaches the correlated step.  Every number is
    # re-read here from the raw outputs and compared with the table the diagnostic's own reader committed.
    D35R = S6 + "/STAGE6_DIAGNOSTIC35_RESULT_20261111.txt"
    D36R = S6 + "/STAGE6_DIAGNOSTIC36_RESULT_20261114.txt"
    D36T, D37T, D38T = S6 + "/d36.tsv", S6 + "/d37.tsv", S6 + "/d38.tsv"
    FL = r"\s+\.\.\.\s+(-?\d+\.\d+)"
    CC_LABELS = [("E(0)", r"^E\(0\)" + FL), ("E(CORR)(strong-pairs)", r"^E\(CORR\)\(strong-pairs\)" + FL),
                 ("E(CORR)(weak-pairs)", r"^E\(CORR\)\(weak-pairs\)" + FL), ("E(CORR)(corrected)", r"^E\(CORR\)\(corrected\)" + FL),
                 ("E(CCSD)", r"^E\(CCSD\)" + FL), ("Triples Correction (T)", r"^Triples Correction \(T\)" + FL),
                 ("E(CCSD(T))", r"^E\(CCSD\(T\)\)" + FL), ("T1 diagnostic", r"^T1 diagnostic" + FL)]

    def cc(d):
        """The coupled-cluster quantities of one DLPNO-CCSD(T) output.  A label ORCA prints more than once must print
        the same value each time; otherwise which one to take would be a choice, and this stops instead."""
        d = Path(d)
        t = (d / "job.out").read_text(errors="replace")
        c = run(d)
        if c is None or not c["norm"] or c["notconv"] or c["level"][0] != "DLPNO-CCSD(T)":
            stop("%s is not a normally terminated, converged DLPNO-CCSD(T) run" % d)
        o = {"c": c, "E": c["E"], "homo": c["homo"], "rel": d.relative_to(res).as_posix()}
        for lab, pat in CC_LABELS:
            v = sorted(set(re.findall(pat, t, re.M)))
            if len(v) != 1:
                stop("%s prints %s with %d distinct values" % (d, lab, len(v)))
            o[lab] = float(v[0])
        n = sorted(set(re.findall(r"^Number of Triples that are to be computed\s+\.\.\.\s+(\d+)", t, re.M)))
        if len(n) != 1:
            stop("%s does not print one number of triples" % d)
        o["triples"] = int(n[0])
        pcs = sorted(set(re.findall(r"Reading point charge file\s+\.\.\.\s+ok \((\d+) point charges\)", t)))
        if len(pcs) > 1:
            stop("%s reports the point-charge file more than one way" % d)
        o["npc_printed"] = pcs[0] if pcs else "none read"
        return o

    # ---- DIAGNOSTIC 36 -------------------------------------------------------------------------------------
    B36 = {st: cc(root / "d36a2" / ("B_%s" % st)) for st in ("R", "TS")}
    for st in ("R", "TS"):
        if state_of(B36[st]["c"]) != st:
            stop("d36a2/B_%s is not on frame 42436's %s geometry" % (st, st))
        x = B36[st]
        control("C43.%s1" % ("1" if st == "R" else "2"), "DIAGNOSTIC 36 arm B %s: E(0) + E(CORR)(corrected) against E(CCSD), Eh" % st,
                x["E(0)"] + x["E(CORR)(corrected)"], x["E(CCSD)"], x["rel"] + "/job.out", 2e-9, 9)
        control("C43.%s2" % ("1" if st == "R" else "2"), "DIAGNOSTIC 36 arm B %s: E(CCSD) + (T) against E(CCSD(T)), Eh" % st,
                x["E(CCSD)"] + x["Triples Correction (T)"], x["E(CCSD(T))"], x["rel"] + "/job.out", 2e-9, 9)
        control("C43.%s3" % ("1" if st == "R" else "2"), "DIAGNOSTIC 36 arm B %s: the last FINAL SINGLE POINT ENERGY against E(CCSD(T)), Eh" % st,
                x["E"], x["E(CCSD(T))"], x["rel"] + "/job.out", 1e-9, 9)
    rec36 = {}
    for l in (root / "d36.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        rec36[f[0]] = (f[1], float(f[2]), float(f[3]), float(f[4]))
    arm36 = {"B": (B36["R"]["E"], B36["TS"]["E"])}
    for arm in ("C", "H"):
        e = {}
        for st in ("R", "TS"):
            c = run(root / "d36" / ("%s_%s" % (arm, st)))
            if c is None or not c["norm"] or c["notconv"] or c["npc"] or state_of(c) != st:
                stop("d36/%s_%s is not a normally terminated, converged, charge-free run on frame 42436" % (arm, st))
            e[st] = c
        arm36[arm] = (e["R"]["E"], e["TS"]["E"])
        if arm == "H":
            H36 = e
    k = 0
    for arm in ("C", "H", "B"):
        eR, eT = arm36[arm]
        for what, mine, rec, tol, nd in (("E(R), Eh", eR, rec36[arm][1], 1e-9, 9), ("E(TS), Eh", eT, rec36[arm][2], 1e-9, 9),
                                         ("barrier, kcal/mol", (eT - eR) * H, rec36[arm][3], 1e-6, 6)):
            k += 1
            control("C41.%02d" % k, "DIAGNOSTIC 36 arm %s, %s (d36.tsv)" % (arm, what), mine, rec, D36T, tol, nd)
    t36 = (root / "STAGE6_DIAGNOSTIC36_RESULT_20261114.txt").read_text()
    t7, k = [], 0
    for lab, shown in (("E(0)", "E(0), Hartree-Fock"), ("E(CORR)(strong-pairs)", None), ("E(CORR)(weak-pairs)", None),
                       ("E(CORR)(corrected)", None), ("E(CCSD)", None), ("Triples Correction (T)", None), ("E(CCSD(T))", None)):
        shown = shown or lab
        vR, vT = B36["R"][lab], B36["TS"][lab]
        t7.append((shown, fmt(vR, 9), fmt(vT, 9), fmt((vT - vR) * H, 4)))
        m = re.search(r"^\s+" + re.escape(shown) + r"\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$", t36, re.M)
        if not m:
            stop("DIAGNOSTIC 36's result does not print the row %s" % shown)
        for what, mine, rec, tol, nd in (("R, Eh", vR, float(m.group(1)), 1e-9, 9), ("TS, Eh", vT, float(m.group(2)), 1e-9, 9),
                                         ("TS minus R, kcal/mol", (vT - vR) * H, float(m.group(3)), 6e-5, 4)):
            k += 1
            control("C45.%02d" % k, "DIAGNOSTIC 36 R36.1, %s, %s" % (shown, what), mine, rec, D36R, tol, nd)
    for st in ("R", "TS"):
        m = re.search(r"^\s+%s\s+(0\.\d{9})\s*$" % st, t36, re.M)
        if not m:
            stop("DIAGNOSTIC 36's result does not print the T1 diagnostic of %s" % st)
        k += 1
        control("C45.%02d" % k, "DIAGNOSTIC 36 R36.4, T1 diagnostic, %s" % st, B36[st]["T1 diagnostic"], float(m.group(1)), D36R, 1e-9, 9)
    bench = (B36["TS"]["E(CCSD(T))"] - B36["R"]["E(CCSD(T))"]) * H
    t7.append(("T1 diagnostic", fmt(B36["R"]["T1 diagnostic"], 9), fmt(B36["TS"]["T1 diagnostic"], 9), "-"))
    t7.append(("triples computed", B36["R"]["triples"], B36["TS"]["triples"], "-"))
    t7.append(("highest occupied orbital of arm B's own reference, eV", fmt(B36["R"]["homo"], 4), fmt(B36["TS"]["homo"], 4), "-"))
    t7.append(("arm H: HF/def2-TZVPD, a separate run", fmt(arm36["H"][0], 9), fmt(arm36["H"][1], 9), fmt((arm36["H"][1] - arm36["H"][0]) * H, 4)))
    t7.append(("highest occupied orbital of arm H, eV", fmt(H36["R"]["homo"], 4), fmt(H36["TS"]["homo"], 4), "-"))
    t7.append(("arm C: CAM-B3LYP-D3BJ/def2-TZVPD, the control", fmt(arm36["C"][0], 9), fmt(arm36["C"][1], 9), fmt((arm36["C"][1] - arm36["C"][0]) * H, 4)))
    write_tsv(out / "T7_d36_benchmark.tsv",
              ["T7. DIAGNOSTIC 36: DLPNO-CCSD(T)/def2-TZVPD (AutoAux, TightSCF, TightPNO) on the bare substrate, frame 42436, frozen geometries, in vacuo.",
               "Arm B is read from %s/d36a2/B_{R,TS}/job.out (the third attempt; the first two failed on resources and committed no output);" % S6,
               "arms H and C from %s/d36/{H,C}_{R,TS}/job.out.  Each label is read where ORCA prints it; a label printed more than once" % S6,
               "must print one value.  barrier = (TS - R) x %.10f kcal/mol per Eh.  Controls C41, C43 and C45 compare with d36.tsv and the result." % H,
               "23.8603 is an electronic energy difference between two frozen gas-phase geometries.  It is NOT the experimental number:",
               "the record's anchors, 24.5 and 20.7 kcal/mol, are a free energy and an enthalpy in water (ERRATUM 7, E7.11)."],
              ["quantity", "R", "TS", "TS_minus_R_kcal"], t7)

    # ---- DIAGNOSTIC 37, and the two tests side by side (F11) ---------------------------------------------
    POOLKEY = {"B3LYP-D3BJ": "B3LYP", "CAM-B3LYP-D3BJ": "CAM-B3LYP", "wB97X-D3": "WB97X-D3", "wB97M-V": "WB97M-V", "wB97X-V": "WB97X-V",
               "PW6B95-D3BJ": "PW6B95", "M06-2X-D3(0)": "M062X", "PWPB95-D3BJ": "RI-PWPB95"}
    rec37, notmeas = {}, []
    for l in (root / "d37.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        if f[8] == "NOT MEASURED":
            if f[0] not in notmeas:
                notmeas.append(f[0])
            continue
        rec37[(f[0], f[2])] = dict(kind=f[1], eR=float(f[3]), eT=float(f[4]), bar=float(f[5]), hR=float(f[6]), hT=float(f[7]), status=f[8])
    f1row = {(r[0], r[1]): r for r in f1 if r[3] == "-"}
    k = 0
    for (fn, bs), v in rec37.items():
        r = f1row.get((PRETTY[POOLKEY[fn]], bs))
        if r is None:
            stop("no charge-free pair on frame 42436 for %s/%s" % (fn, bs))
        for what, mine, rec, tol, nd in (("E(R), Eh", float(r[5]), v["eR"], 1e-8, 8), ("E(TS), Eh", float(r[6]), v["eT"], 1e-8, 8),
                                         ("barrier, kcal/mol", float(r[7]), v["bar"], 6e-5, 4),
                                         ("highest occupied orbital, R, eV", float(r[11]), v["hR"], 1.5e-4, 4),
                                         ("highest occupied orbital, TS, eV", float(r[14]), v["hT"], 1.5e-4, 4)):
            k += 1
            control("C42.%02d" % k, "DIAGNOSTIC 37, %s/%s, %s (d37.tsv)" % (fn, bs, what), mine, rec, D37T, tol, nd)
    # ---- DIAGNOSTIC 41: the correlated barrier at the production basis, def2-SVPD ------------------------------
    # One new single point, the transition state (d41/T).  The reactant leg is DIAGNOSTIC 38's run N, as committed.
    D41R, D41T = S6 + "/STAGE6_DIAGNOSTIC41_RESULT_20261115.txt", S6 + "/d41.tsv"
    S41 = {"R": cc(root / "d38" / "N"), "TS": cc(root / "d41" / "T")}
    for st in ("R", "TS"):
        x = S41[st]
        if (state_of(x["c"]) != st or x["c"]["level"][1] != "DEF2-SVPD" or x["c"]["npc"] or x["npc_printed"] != "none read"
                or x["c"]["chmult"] != (["-2"], ["1"])):
            stop("%s is not a charge-free DLPNO-CCSD(T)/def2-SVPD dianion single point on frame 42436's %s geometry" % (x["rel"], st))
        j = "1" if st == "R" else "2"
        control("C46.%s1" % j, "DIAGNOSTIC 41 %s leg: E(0) + E(CORR)(corrected) against E(CCSD), Eh" % st,
                x["E(0)"] + x["E(CORR)(corrected)"], x["E(CCSD)"], x["rel"] + "/job.out", 2e-9, 9)
        control("C46.%s2" % j, "DIAGNOSTIC 41 %s leg: E(CCSD) + (T) against E(CCSD(T)), Eh" % st,
                x["E(CCSD)"] + x["Triples Correction (T)"], x["E(CCSD(T))"], x["rel"] + "/job.out", 2e-9, 9)
        control("C46.%s3" % j, "DIAGNOSTIC 41 %s leg: the last FINAL SINGLE POINT ENERGY against E(CCSD(T)), Eh" % st,
                x["E"], x["E(CCSD(T))"], x["rel"] + "/job.out", 1e-9, 9)
    rec41 = {}
    for l in (root / "d41.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        rec41[f[0]] = tuple(float(v) for v in f[1:6])
    t41 = (root / "STAGE6_DIAGNOSTIC41_RESULT_20261115.txt").read_text()
    s411 = t41[t41.index("R41.1 "):t41.index("R41.2 ")]
    s412 = t41[t41.index("R41.2 "):t41.index("R41.3 ")]
    s413 = t41[t41.index("R41.3 "):t41.index("R41.4 ")]
    bench_sv = (S41["TS"]["E(CCSD(T))"] - S41["R"]["E(CCSD(T))"]) * H
    t11, k = [], 0
    for lab, shown in (("E(0)", "E(0), Hartree-Fock"), ("E(CORR)(strong-pairs)", None), ("E(CORR)(weak-pairs)", None),
                       ("E(CORR)(corrected)", None), ("E(CCSD)", None), ("Triples Correction (T)", None), ("E(CCSD(T))", None)):
        shown = shown or lab
        vR, vT = S41["R"][lab], S41["TS"][lab]
        bsv, btz = (vT - vR) * H, (B36["TS"][lab] - B36["R"][lab]) * H
        t11.append((shown, fmt(vR, 9), fmt(vT, 9), fmt(bsv, 4), fmt(btz, 4), "%+.4f" % (btz - bsv)))
        for what, mine, rec, tol, nd in (("R, Eh", vR, rec41[shown][0], 1e-9, 9), ("TS, Eh", vT, rec41[shown][1], 1e-9, 9),
                                         ("barrier at def2-SVPD, kcal/mol", bsv, rec41[shown][2], 6e-5, 4),
                                         ("barrier at def2-TZVPD, kcal/mol", btz, rec41[shown][3], 6e-5, 4),
                                         ("def2-TZVPD minus def2-SVPD, kcal/mol", btz - bsv, rec41[shown][4], 6e-5, 4)):
            k += 1
            control("C47.%02d" % k, "DIAGNOSTIC 41, %s, %s (d41.tsv)" % (shown, what), mine, rec, D41T, tol, nd)
        m = re.search(r"^\s+" + re.escape(shown) + r"\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$", s411, re.M)
        if not m:
            stop("DIAGNOSTIC 41's result does not print the row %s in R41.1" % shown)
        for what, mine, rec, tol, nd in (("R, Eh", vR, float(m.group(1)), 1e-9, 9), ("TS, Eh", vT, float(m.group(2)), 1e-9, 9),
                                         ("TS minus R, kcal/mol", bsv, float(m.group(3)), 6e-5, 4)):
            k += 1
            control("C47.%02d" % k, "DIAGNOSTIC 41 R41.1, %s, %s" % (shown, what), mine, rec, D41R, tol, nd)
        if lab in ("E(0)", "E(CORR)(corrected)", "E(CCSD)", "Triples Correction (T)", "E(CCSD(T))"):
            m = re.search(r"^\s+" + re.escape(shown) + r"\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([+-]\d+\.\d+)\s*$", s412, re.M)
            if not m:
                stop("DIAGNOSTIC 41's result does not print the row %s in R41.2" % shown)
            k += 1
            control("C47.%02d" % k, "DIAGNOSTIC 41 R41.2, %s, def2-TZVPD minus def2-SVPD, kcal/mol" % shown, btz - bsv, float(m.group(3)), D41R, 6e-5, 4)
    for st, tag in (("TS", "d41/T, transition state, def2-SVPD"), ("R", "d38/N, reactant, def2-SVPD")):
        m = re.search(r"^\s+" + re.escape(tag) + r"\s+(0\.\d{9})\s*$", t41, re.M)
        if not m:
            stop("DIAGNOSTIC 41's result does not print the T1 diagnostic of %s" % tag)
        k += 1
        control("C47.%02d" % k, "DIAGNOSTIC 41 R41.4, T1 diagnostic, %s" % st, S41[st]["T1 diagnostic"], float(m.group(1)), D41R, 1e-9, 9)
    for st, tag in (("TS", "d41/T, transition state"), ("R", "d38/N, reactant")):
        m = re.search(r"^\s+" + re.escape(tag) + r"\s+(-?\d+\.\d{4}) eV\s*$", t41, re.M)
        if not m:
            stop("DIAGNOSTIC 41's result does not print the highest occupied orbital of %s" % tag)
        k += 1
        control("C47.%02d" % k, "DIAGNOSTIC 41 R41.5, highest occupied orbital of the Hartree-Fock reference, %s, eV" % st,
                S41[st]["homo"], float(m.group(1)), D41R, 1.5e-4, 4)
    r413 = {}
    for fn in POOLKEY:
        m = re.search(r"^\s+" + re.escape(fn) + r"\s+(\d+\.\d{4})\s+([+-]\d+\.\d{4})\s+([+-]\d+\.\d{4})\s*$", s413, re.M)
        if not m:
            stop("DIAGNOSTIC 41's result does not print %s in R41.3" % fn)
        # R41.3 is defined on the COMMITTED def2-SVPD barriers, the four-decimal values of d37.tsv that the pre-registration
        # lists (controls C42 hold each of them against the raw outputs), minus the benchmark; so it is formed that way here
        sv = rec37[(fn, "def2-SVPD")]["bar"]
        if abs(sv - float(m.group(1))) > 0:
            stop("DIAGNOSTIC 41's R41.3 does not print d37.tsv's def2-SVPD barrier for %s" % fn)
        k += 1
        control("C47.%02d" % k, "DIAGNOSTIC 41 R41.3, %s/def2-SVPD barrier minus the def2-SVPD benchmark, kcal/mol" % fn,
                sv - bench_sv, float(m.group(2)), D41R, 6e-5, 4)
        r413[fn] = sv - bench_sv
    t11.append(("T1 diagnostic", fmt(S41["R"]["T1 diagnostic"], 9), fmt(S41["TS"]["T1 diagnostic"], 9), "-", "-", "-"))
    t11.append(("T1 diagnostic at def2-TZVPD (DIAGNOSTIC 36)", fmt(B36["R"]["T1 diagnostic"], 9), fmt(B36["TS"]["T1 diagnostic"], 9), "-", "-", "-"))
    t11.append(("triples computed", S41["R"]["triples"], S41["TS"]["triples"], "-", "-", "-"))
    t11.append(("highest occupied orbital of the Hartree-Fock reference, eV", fmt(S41["R"]["homo"], 4), fmt(S41["TS"]["homo"], 4), "-", "-", "-"))
    write_tsv(out / "T11_d41_benchmark_svpd.tsv",
              ["T11. DIAGNOSTIC 41: DLPNO-CCSD(T)/def2-SVPD (AutoAux, TightSCF, TightPNO) on the bare substrate, frame 42436, frozen geometries, in vacuo.",
               "The reactant leg is DIAGNOSTIC 38's run N (%s/d38/N/job.out), as committed; the transition state is %s/d41/T/job.out." % (S6, S6),
               "The two legs were run in different jobs.  barrier = (TS - R) x %.10f kcal/mol per Eh." % H,
               "barrier_TZVPD_kcal: the same component of DIAGNOSTIC 36's barrier, recomputed here from %s/d36a2/B_{R,TS}/job.out." % S6,
               "shift: def2-TZVPD minus def2-SVPD.  Controls C46 and C47 compare with d41.tsv and with the result's printed tables.",
               "22.8968 is NOT a converged barrier and must not be quoted as the in vacuo barrier (D41.1); it is NOT the experimental number (D41.2).",
               "Two basis sets do not make an extrapolation, and none is attempted (D41.5)."],
              ["quantity", "R_d38N", "TS_d41T", "barrier_SVPD_kcal", "barrier_TZVPD_kcal", "shift_TZVPD_minus_SVPD_kcal"], t11)

    # ---- DIAGNOSTIC 37, Amendment 1: revDSD-PBEP86-D4, which D37 could not run, run two ways ---------------------
    D37A1R, D37A1T = S6 + "/STAGE6_DIAGNOSTIC37_AMENDMENT1_RESULT_20261115.txt", S6 + "/d37a1.tsv"
    rec37a = {}
    for l in (root / "d37a1.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        rec37a[(f[0], f[1])] = dict(eR=float(f[2]), eT=float(f[3]), bar=float(f[4]), hR=float(f[5]), hT=float(f[6]), ri=f[7], status=f[8], entered=f[9])
    A1, k = {}, 0
    for arm in ("RI", "K"):
        for bs, tag in (("def2-SVPD", "SV"), ("def2-TZVPD", "TZ")):
            e = {}
            for st in ("R", "TS"):
                d = root / "d37a1" / ("revDSD_%s_%s_%s" % (arm, tag, st))
                c = run(d)
                if (c is None or not c["norm"] or c["notconv"] or c["npc"] or state_of(c) != st or c["level"][0] != "REVDSD-PBEP86-D4/2021"
                        or PRETTY[c["level"][1]] != bs or c["chmult"] != (["-2"], ["1"]) or c["shifted"] or c["nfinal"] != 1):
                    stop("%s is not a normally terminated, converged, charge-free revDSD-PBEP86-D4/%s dianion run on frame 42436" % (d, bs))
                e[st] = c
            A1[(arm, bs)] = e
            v = rec37a[(arm, bs)]
            if v["status"] != "measured":
                stop("d37a1.tsv does not mark arm %s at %s as measured" % (arm, bs))
            for what, mine, rec, tol, nd in (("E(R), Eh", e["R"]["E"], v["eR"], 1e-8, 8), ("E(TS), Eh", e["TS"]["E"], v["eT"], 1e-8, 8),
                                             ("barrier, kcal/mol", (e["TS"]["E"] - e["R"]["E"]) * H, v["bar"], 6e-5, 4),
                                             ("highest occupied orbital, R, eV", e["R"]["homo"], v["hR"], 1.5e-4, 4),
                                             ("highest occupied orbital, TS, eV", e["TS"]["homo"], v["hT"], 1.5e-4, 4)):
                k += 1
                control("C50.%02d" % k, "DIAGNOSTIC 37 Amendment 1, arm %s, %s, %s (d37a1.tsv)" % (arm, bs, what), mine, rec, D37A1T, tol, nd)
    if [a for a in ("RI", "K") if rec37a[(a, "def2-SVPD")]["entered"] == "yes" and rec37a[(a, "def2-TZVPD")]["entered"] == "yes"] != ["RI"]:
        stop("d37a1.tsv does not enter arm RI, and arm RI alone")
    cam37a = {}
    for st in ("R", "TS"):
        c = run(root / "d37a1" / ("CAM_SV_%s" % st))
        if (c is None or not c["norm"] or c["notconv"] or c["npc"] or state_of(c) != st or c["level"][:2] != ("CAM-B3LYP", "DEF2-SVPD")
                or c["chmult"] != (["-2"], ["1"])):
            stop("d37a1/CAM_SV_%s is not the CAM-B3LYP-D3BJ/def2-SVPD control on frame 42436" % st)
        cam37a[st] = c
    k += 1
    control("C50.%02d" % k, "DIAGNOSTIC 37 Amendment 1, the control: CAM-B3LYP-D3BJ/def2-SVPD barrier, run again", (cam37a["TS"]["E"] - cam37a["R"]["E"]) * H,
            26.8248, D37A1R, 5e-5, 4)
    rsd_sv = (A1[("RI", "def2-SVPD")]["TS"]["E"] - A1[("RI", "def2-SVPD")]["R"]["E"]) * H
    rsd_tz = (A1[("RI", "def2-TZVPD")]["TS"]["E"] - A1[("RI", "def2-TZVPD")]["R"]["E"]) * H
    rsd_k_sv = (A1[("K", "def2-SVPD")]["TS"]["E"] - A1[("K", "def2-SVPD")]["R"]["E"]) * H
    rsd_k_tz = (A1[("K", "def2-TZVPD")]["TS"]["E"] - A1[("K", "def2-TZVPD")]["R"]["E"]) * H
    m = re.search(r"revDSD-PBEP86-D4, arm RI, def2-TZVPD: (\d+\.\d{4}), which is ([+-]\d+\.\d{4}) from the benchmark\.",
                  (root / "STAGE6_DIAGNOSTIC37_AMENDMENT1_RESULT_20261115.txt").read_text())
    if not m:
        stop("DIAGNOSTIC 37 Amendment 1's result does not print its test 2")
    k += 1
    control("C50.%02d" % k, "DIAGNOSTIC 37 Amendment 1 R-A1.6, revDSD-PBEP86-D4/def2-TZVPD barrier minus the benchmark, kcal/mol", rsd_tz - bench,
            float(m.group(2)), D37A1R, 6e-5, 4)

    target_eV = -float(m_p3.group(1))
    f11 = []
    for fn in POOLKEY:
        tz, sv = f1row[(PRETTY[POOLKEY[fn]], "def2-TZVPD")], f1row[(PRETTY[POOLKEY[fn]], "def2-SVPD")]
        if tz[15] == "yes" or sv[15] == "yes":
            stop("a level shift was engaged in a bare run of %s; its orbital energy may not be quoted" % fn)
        f11.append([fn, rec37[(fn, "def2-TZVPD")]["kind"], float(sv[7]), float(tz[7]), float(tz[7]) - float(sv[7]), float(tz[7]) - bench,
                    rec37[(fn, "def2-SVPD")]["hR"], rec37[(fn, "def2-SVPD")]["hR"] - target_eV])
    f11.sort(key=lambda r: r[3])
    # the ninth row: revDSD-PBEP86-D4 from Amendment 1, arm RI, the arm d37a1.tsv enters
    rsd = ["revDSD-PBEP86-D4", "amendment 1", rsd_sv, rsd_tz, rsd_tz - rsd_sv, rsd_tz - bench, rec37a[("RI", "def2-SVPD")]["hR"],
           rec37a[("RI", "def2-SVPD")]["hR"] - target_eV]
    if any(A1[("RI", b)][s]["shifted"] for b in ("def2-SVPD", "def2-TZVPD") for s in ("R", "TS")):
        stop("a level shift was engaged in a bare run of revDSD-PBEP86-D4; its orbital energy may not be quoted")
    f11x = sorted(f11 + [rsd], key=lambda r: r[3])

    def svd(r):
        """The def2-SVPD barrier, at the four decimals the record commits it with, minus DIAGNOSTIC 41's benchmark (R41.3's definition)."""
        return float(fmt(r[2], 4)) - bench_sv
    write_tsv(out / "F11_two_tests.tsv",
              ["F11. Nine functionals on the two tests the record holds for the bare substrate, frame 42436, frozen geometries, in vacuo.",
               "Test 1 (DIAGNOSTIC 28's): the highest occupied orbital at def2-SVPD, reactant, against zero and against minus Probe 3's",
               "detachment energy.  homo_eV is the committed value of d37.tsv, and of d37a1.tsv for revDSD-PBEP86-D4; controls C42 and C50 recompute it.",
               "Test 2: the def2-TZVPD barrier minus DIAGNOSTIC 36's DLPNO-CCSD(T)/def2-TZVPD barrier, %s kcal/mol, recomputed here." % fmt(bench, 4),
               "DIAGNOSTIC 36 pre-registered this comparison for three functionals (kind = committed).  For the five of DIAGNOSTIC 37",
               "(kind = candidate) it is POST HOC: DIAGNOSTIC 36's result says so, and DIAGNOSTIC 37's own test 2 is NOT EVALUATED.",
               "For revDSD-PBEP86-D4 (kind = amendment 1) DIAGNOSTIC 37's Amendment 1 fixed test 2 before its own number existed and after",
               "the benchmark's did (DA1.3).  D37's own table marks it NOT MEASURED; the amendment measured it, and its arm RI is the entry.",
               "minus_SVPD_benchmark_kcal: the def2-SVPD barrier, at its four committed decimals, minus DIAGNOSTIC 41's DLPNO-CCSD(T)/def2-SVPD",
               "barrier, %s kcal/mol, recomputed here." % fmt(bench_sv, 4),
               "DIAGNOSTIC 41 fixed that comparison for the eight when their barriers were known and its benchmark was not (R41.3), and says",
               "it is still not the comparison DIAGNOSTIC 36 pre-registered.  For revDSD-PBEP86-D4 it is POST HOC.",
               "SVPD_minus_TZVPD_benchmark_kcal: the def2-SVPD barrier minus the def2-TZVPD benchmark.  POST HOC for all nine: no committed",
               "document defines it.  No score combines the tests.  Neither benchmark is the experimental number, and neither is a converged",
               "absolute barrier (DIAGNOSTIC 36, D36.2 and D36.3; DIAGNOSTIC 41, D41.1 and D41.2)."],
              ["functional", "kind", "barrier_SVPD_kcal", "barrier_TZVPD_kcal", "basis_shift_kcal", "minus_benchmark_kcal", "homo_SVPD_R_eV",
               "homo_minus_target_eV", "minus_SVPD_benchmark_kcal", "SVPD_minus_TZVPD_benchmark_kcal"],
              [(r[0], r[1], fmt(r[2], 4), fmt(r[3], 4), fmt(r[4], 4), "%+.4f" % r[5], "%+.4f" % r[6], "%+.4f" % r[7],
                "%+.4f" % svd(r), "%+.4f" % (r[2] - bench)) for r in f11x])

    # ---- DIAGNOSTIC 38 -------------------------------------------------------------------------------------
    rec38 = {}
    for l in (root / "d38.tsv").read_text().splitlines()[1:]:
        f = l.split("\t")
        rec38[f[0]] = (f[1], float(f[2]), float(f[3]), float(f[4]), float(f[5]), float(f[6]))
    X38, t8, k = {}, [], 0
    for rn in ("N", "B0", "B1", "A0", "A1"):
        x = cc(root / "d38" / rn)
        if state_of(x["c"]) != "R":
            stop("d38/%s is not on frame 42436's reactant geometry" % rn)
        pcf = root / "d38" / rn / "charge.pc"
        if pcf.is_file():
            ls = pcf.read_text().split("\n")
            if int(ls[0].split()[0]) != 1:
                stop("d38/%s/charge.pc does not hold exactly one charge" % rn)
            x["q"], x["xyz"] = "%.6f" % float(ls[1].split()[0]), " ".join(ls[1].split()[1:4])
        else:
            x["q"], x["xyz"] = "-", "-"
        X38[rn] = x
        for what, lab, j, tol, nd in (("E(0), Eh", "E(0)", 1, 1e-9, 9), ("E(CORR)(corrected), Eh", "E(CORR)(corrected)", 2, 1e-9, 9),
                                      ("E(CCSD(T)), Eh", "E(CCSD(T))", 3, 1e-9, 9), ("T1 diagnostic", "T1 diagnostic", 4, 1e-9, 9),
                                      ("highest occupied orbital, eV", "homo", 5, 1.5e-4, 4)):
            k += 1
            control("C44.%02d" % k, "DIAGNOSTIC 38 run %s, %s (d38.tsv)" % (rn, what), x[lab], rec38[rn][j], D38T, tol, nd)
    for rn in ("N", "B0", "B1", "A0", "A1"):
        x, n = X38[rn], X38["N"]
        t8.append((rn, x["q"], x["xyz"], fmt(x["E(0)"], 9), fmt(x["E(CORR)(corrected)"], 9), fmt(x["Triples Correction (T)"], 9),
                   fmt(x["E(CCSD(T))"], 9), fmt(x["T1 diagnostic"], 9), "%+.4f" % x["homo"], x["npc_printed"],
                   "%+.9f" % (x["E(0)"] - n["E(0)"]), "%+.9f" % (x["E(CORR)(corrected)"] - n["E(CORR)(corrected)"]),
                   "%+.9f" % (x["E(CCSD(T))"] - n["E(CCSD(T))"])))
    write_tsv(out / "T8_d38_probe.tsv",
              ["T8. DIAGNOSTIC 38: DLPNO-CCSD(T)/def2-SVPD (AutoAux, TightSCF, TightPNO) at frame 42436's REACTANT geometry only, with one",
               "external point charge (charge.pc).  A MECHANISM PROBE: no transition state, so no barrier and no ddE.",
               "N: no charge.  B0, A0: a charge of zero at the position of B1, A1 (the inertness check).  B1: +1 e at site 1690",
               "(ADD-s1690_qp10000).  A1: -1 e at site 678 (ADD-s678_qm10000).  d*_vs_N: this run minus run N, Eh.",
               "A1 is NOT INTERPRETABLE by the diagnostic's pre-registered gate G38.10: its highest occupied orbital is at or above zero.",
               "point_charges_printed: the count on ORCA's line 'Reading point charge file ... ok (n point charges)' in the output."],
              ["run", "charge_e", "position_A", "E0_Eh", "E_CORR_corrected_Eh", "triples_T_Eh", "E_CCSDT_Eh", "T1", "HOMO_eV",
               "point_charges_printed", "dE0_vs_N_Eh", "dE_CORR_vs_N_Eh", "dE_CCSDT_vs_N_Eh"], t8)

    # ---- derived numbers of the four diagnostics -----------------------------------------------------------
    F1B, T7, T8, F11 = "figures/F1b_stage4e_bare_barrier.tsv", "figures/T7_d36_benchmark.tsv", "figures/T8_d38_probe.tsv", "figures/F11_two_tests.tsv"
    dif = [r[10] - r[9] for r in s4e]
    by35 = {r[0]: r for r in s4e}
    DV.add("DV190", "%+.4f" % min(dif), "recomputed from raw outputs", "smallest (frame 42436 minus frame 41786) barrier over Stage 4e's five levels", F1B)
    DV.add("DV191", "%+.4f" % max(dif), "recomputed from raw outputs", "largest (frame 42436 minus frame 41786) barrier over Stage 4e's five levels", F1B)
    DV.add("DV192", fmt(max(dif) - min(dif), 4), "derived", "DV191 - DV190", F1B)
    DV.add("DV193", "%+.4f" % (by35["L5"][10] - by35["L4"][10]), "recomputed from raw outputs", "wB97X-D3/def2-SVP minus MP2/6-31G(d), frame 42436", F1B)
    DV.add("DV194", "%+.4f" % (by35["L1"][10] - by35["L4"][10]), "recomputed from raw outputs", "B3LYP-D3BJ/def2-SVP minus MP2/6-31G(d), frame 42436", F1B)
    DV.add("DV195", str(sum(1 for a, b in zip(rank41, rank42) if a != b)), "derived", "Stage 4e levels whose rank by barrier differs between the two frames (%s)"
           % ", ".join(a for a, b in zip(rank41, rank42) if a != b), F1B)
    DV.add("DV196", "%+.4f" % (by35["L3"][10] - by35["L4"][10]), "recomputed from raw outputs", "HF/6-31G(d) minus MP2/6-31G(d), frame 42436", F1B)
    DV.add("DV197", "%+.4f" % (by35["L2"][10] - by35["L4"][10]), "recomputed from raw outputs", "B3LYP/6-31G(d) minus MP2/6-31G(d), frame 42436", F1B)
    comp = {r[0]: r for r in t7}
    DV.add("DV220", fmt(bench, 4), "recomputed from raw outputs", "(E(CCSD(T)) at TS - at R) x %.10f, DLPNO-CCSD(T)/def2-TZVPD" % H, T7)
    DV.add("DV221", comp["E(0), Hartree-Fock"][3], "recomputed from raw outputs", "the E(0) part of the benchmark barrier", T7)
    DV.add("DV222", comp["E(CCSD)"][3], "recomputed from raw outputs", "the barrier at the CCSD level, before the triples", T7)
    DV.add("DV223", comp["Triples Correction (T)"][3], "recomputed from raw outputs", "the triples correction's part of the benchmark barrier", T7)
    DV.add("DV224", fmt(100.0 * abs(float(comp["Triples Correction (T)"][3])) / bench, 1), "derived", "100 x |DV223| / DV220, per cent", T7)
    DV.add("DV225", comp["E(CORR)(corrected)"][3], "recomputed from raw outputs", "the CCSD correlation energy's part of the benchmark barrier", T7)
    hfH = (arm36["H"][1] - arm36["H"][0]) * H
    DV.add("DV226", fmt(hfH, 4), "recomputed from raw outputs", "HF/def2-TZVPD barrier, arm H", T7)
    DV.add("DV227", fmt(abs(hfH - (B36["TS"]["E(0)"] - B36["R"]["E(0)"]) * H), 4), "derived", "|arm H barrier - arm B's E(0) barrier|", T7)
    DV.add("DV228", str(len(list((root / "d36a2").rglob("job.out")))), "count", "committed outputs of arm B, under %s/d36a2" % S6, S6 + "/d36a2")
    DV.add("DV229", str(len(list((root / "d36").glob("B_*/job.out"))) + len(list((root / "d36a1").rglob("job.out")))), "count",
           "committed outputs of arm B's first two attempts, under %s/d36/B_* and %s/d36a1" % (S6, S6), S6 + "/d36 ; " + S6 + "/d36a1")
    DV.add("DV218", fmt(B36["TS"]["T1 diagnostic"] - B36["R"]["T1 diagnostic"], 9), "derived", "T1 diagnostic, TS minus R", T7)
    for i, r in enumerate(f11):
        DV.add("DV%d" % (230 + i), "%+.4f" % r[5], "recomputed from raw outputs" if r[1] == "committed" else "recomputed from raw outputs; POST HOC",
               "%s/def2-TZVPD barrier minus DV220" % r[0], F11)
    bt = [r[3] for r in f11]
    DV.add("DV238", fmt(max(bt) - min(bt), 2), "derived; POST HOC", "largest minus smallest def2-TZVPD barrier of the eight functionals", F11)
    DV.add("DV239", "%.0f" % (100.0 * (bench - min(bt)) / (max(bt) - min(bt))), "derived; POST HOC",
           "100 x (DV220 - smallest) / (largest - smallest), per cent", F11)
    near = [r[0] for r in f11 if abs(r[5]) < 3.0]
    DV.add("DV240", str(len(near)), "derived; POST HOC", "functionals of the eight within 3 kcal/mol of DV220 (%s)" % ", ".join(near), F11)
    DV.add("DV241", "%+.4f" % min(r[4] for r in f11), "recomputed from raw outputs", "largest def2-SVPD to def2-TZVPD lowering of the barrier among the eight", F11)
    DV.add("DV242", "%+.4f" % max(r[4] for r in f11), "recomputed from raw outputs", "smallest def2-SVPD to def2-TZVPD lowering of the barrier among the eight", F11)
    cl3 = sorted(f11, key=lambda r: abs(r[7]))[:3]
    DV.add("DV243", fmt(min(r[3] for r in cl3), 4), "derived; POST HOC", "smallest def2-TZVPD barrier among the three functionals nearest the orbital target (%s)"
           % ", ".join(r[0] for r in cl3), F11)
    DV.add("DV244", fmt(max(r[3] for r in cl3), 4), "derived; POST HOC", "largest def2-TZVPD barrier among the same three", F11)
    DV.add("DV245", str(sum(1 for r in f11 if r[6] < 0)), "derived", "functionals of the eight whose highest occupied orbital is below zero at def2-SVPD, reactant", F11)
    DV.add("DV246", str(len(f11)), "count", "functionals with a committed barrier at def2-SVPD and def2-TZVPD on frame 42436", F11)
    DV.add("DV247", str(sum(1 for r in f11 if r[1] == "candidate")), "count", "of those, candidates of DIAGNOSTIC 37 (measured)", D37T)
    DV.add("DV248", str(len(notmeas)), "count", "candidates of DIAGNOSTIC 37 marked NOT MEASURED (%s)" % ", ".join(notmeas), D37T)
    DV.add("DV249", str(sum(1 for r in f11 if abs(r[5]) < 3.0 and r[6] < 0)), "derived; POST HOC",
           "functionals within 3 kcal/mol of DV220 whose highest occupied orbital is also below zero (%s)"
           % ", ".join(r[0] for r in f11 if abs(r[5]) < 3.0 and r[6] < 0), F11)
    n38 = X38["N"]
    for i, rn in enumerate(("B1", "A1")):
        x = X38[rn]
        DV.add("DV%d" % (250 + 3 * i), "%+.9f" % (x["E(0)"] - n38["E(0)"]), "recomputed from raw outputs", "E(0) of run %s minus run N, Eh" % rn, T8)
        DV.add("DV%d" % (251 + 3 * i), "%+.9f" % (x["E(CORR)(corrected)"] - n38["E(CORR)(corrected)"]), "recomputed from raw outputs",
               "E(CORR)(corrected) of run %s minus run N, Eh" % rn, T8)
        DV.add("DV%d" % (252 + 3 * i), "%+.9f" % (x["E(CCSD(T))"] - n38["E(CCSD(T))"]), "recomputed from raw outputs", "E(CCSD(T)) of run %s minus run N, Eh" % rn, T8)
    DV.add("DV256", "%.0f" % (abs(X38["B1"]["E(CORR)(corrected)"] - n38["E(CORR)(corrected)"]) / 1e-6), "derived", "|DV251| / 1e-6 Eh, the gate's threshold", T8)
    DV.add("DV257", "%.0f" % (100.0 * 1.8400 / 5.3701), "derived", "100 x 1.8400 / 5.3701, per cent", "%s ; %s" % (D36R, D34R))
    DV.add("DV258", "%.0f" % (100.0 * 1.8400 / 3.3985), "derived", "100 x 1.8400 / 3.3985, per cent", "%s ; %s" % (D36R, D34R))
    inert = max(abs(X38[z][lab] - n38[lab]) for z in ("B0", "A0") for lab in ("E(0)", "E(CORR)(corrected)", "E(CCSD(T))"))
    DV.add("DV259", "%.2e" % inert, "recomputed from raw outputs", "largest |zero-charge run minus run N| over E(0), E(CORR)(corrected) and E(CCSD(T)), Eh", T8)
    DV.add("DV260", "%+.4f" % ((X38["B1"]["E(CORR)(corrected)"] - n38["E(CORR)(corrected)"]) * H), "derived", "DV251 x %.10f, kcal/mol" % H, T8)
    DV.add("DV261", "%+.4f" % ((X38["A1"]["E(CORR)(corrected)"] - n38["E(CORR)(corrected)"]) * H), "derived", "DV254 x %.10f, kcal/mol" % H, T8)
    DV.add("DV262", str(sum(1 for rn in ("B0", "B1", "A0", "A1") if X38[rn]["npc_printed"] == "1")), "count",
           "DIAGNOSTIC 38 outputs with a charge file that print 'Reading point charge file ... ok (1 point charges)'", S6 + "/d38")
    DV.add("DV263", str(len(X38)), "count", "committed outputs of DIAGNOSTIC 38", S6 + "/d38")
    DV.add("DV264", str(len(list((root / "d37").glob("*/job.out")))), "count", "committed job.out files under %s/d37" % S6, S6 + "/d37")
    n37ok = sum(1 for q in (root / "d37").glob("*/job.out") if "****ORCA TERMINATED NORMALLY****" in q.read_text(errors="replace"))
    DV.add("DV265", str(n37ok), "count", "of those, normally terminated", S6 + "/d37")
    DV.add("DV266", str(sum(1 for r in f1 if r[3] == "-")), "count", "method and basis combinations of F1 in vacuo (the rows Figure F1 draws)",
           "figures/F1_reference_barrier.tsv")
    DV.add("DV267", str(len(list((root / "d37").glob("*/job.out"))) - n37ok), "count", "DV264 - DV265: outputs of DIAGNOSTIC 37 that did not terminate normally",
           S6 + "/d37")
    # DIAGNOSTIC 39: counts of its committed files only.  Its result is committed and is NOT ENTERED in the revision of
    # 15 November 2026 (evening); no number of it is read anywhere in this script.
    DV.add("DV290", str(len(list((root / "d39").rglob("job.inp")))), "count", "number of committed job.inp files under %s/d39" % S6, S6 + "/d39")
    DV.add("DV291", str(len(list((root / "d39").rglob("job.out")))), "count", "number of committed job.out files under %s/d39" % S6, S6 + "/d39")

    # ---- derived numbers of DIAGNOSTIC 41 and of DIAGNOSTIC 37's Amendment 1 ---------------------------------
    T11, comp41 = "figures/T11_d41_benchmark_svpd.tsv", {r[0]: r for r in t11}
    DV.add("DV300", fmt(bench_sv, 4), "recomputed from raw outputs", "(E(CCSD(T)) at TS, d41/T - at R, d38/N) x %.10f, DLPNO-CCSD(T)/def2-SVPD" % H, T11)
    DV.add("DV301", comp41["E(0), Hartree-Fock"][3], "recomputed from raw outputs", "the E(0) part of the def2-SVPD correlated barrier", T11)
    DV.add("DV302", comp41["E(CCSD)"][3], "recomputed from raw outputs", "the def2-SVPD barrier at the CCSD level, before the triples", T11)
    DV.add("DV303", comp41["Triples Correction (T)"][3], "recomputed from raw outputs", "the triples correction's part of the def2-SVPD correlated barrier", T11)
    DV.add("DV304", comp41["E(CORR)(corrected)"][3], "recomputed from raw outputs", "the CCSD correlation energy's part of the def2-SVPD correlated barrier", T11)
    DV.add("DV305", comp41["E(CCSD(T))"][5], "recomputed from raw outputs", "DV220 - DV300: the correlated barrier, def2-TZVPD minus def2-SVPD", T11)
    DV.add("DV306", comp41["E(0), Hartree-Fock"][5], "recomputed from raw outputs", "the E(0) part of DV305", T11)
    DV.add("DV307", comp41["E(CORR)(corrected)"][5], "recomputed from raw outputs", "the CCSD correlation energy's part of DV305", T11)
    DV.add("DV308", comp41["E(CCSD)"][5], "recomputed from raw outputs", "DV305 at the CCSD level, before the triples", T11)
    DV.add("DV309", comp41["Triples Correction (T)"][5], "recomputed from raw outputs", "the triples correction's part of DV305", T11)
    DV.add("DV310", fmt(abs((bench - bench_sv) - (-1.0)), 4), "derived", "|DV305 - (-1.0)|: the distance DIAGNOSTIC 41's pre-registered rule reads", T11)
    DV.add("DV311", fmt(100.0 * abs(float(comp41["Triples Correction (T)"][3])) / bench_sv, 1), "derived", "100 x |DV303| / DV300, per cent", T11)
    DV.add("DV312", fmt(S41["TS"]["T1 diagnostic"] - S41["R"]["T1 diagnostic"], 9), "derived", "T1 diagnostic at def2-SVPD, TS minus R", T11)
    DV.add("DV313", str(sum(1 for r in f11 if (r[4] < 0) != ((bench - bench_sv) < 0))), "derived",
           "functionals of DIAGNOSTIC 37's eight whose def2-SVPD to def2-TZVPD shift has the sign opposite to DV305", F11)
    for i, fn in enumerate(POOLKEY):
        DV.add("DV%d" % (314 + i), "%+.4f" % r413[fn], "recomputed from raw outputs", "%s/def2-SVPD barrier minus DV300" % fn, F11)
    DV.add("DV322", "%+.4f" % svd(rsd), "recomputed from raw outputs; POST HOC", "revDSD-PBEP86-D4/def2-SVPD barrier minus DV300", F11)
    nine = sorted(f11 + [rsd], key=lambda r: r[3])
    n3tz = [r[0] for r in nine if abs(r[5]) < 3.0]
    DV.add("DV323", str(len(n3tz)), "derived; POST HOC", "functionals of the nine within 3 kcal/mol of DV220 at def2-TZVPD (%s)" % ", ".join(n3tz), F11)
    n3sv = [r[0] for r in nine if abs(svd(r)) < 3.0]
    DV.add("DV324", str(len(n3sv)), "derived; POST HOC", "functionals of the nine within 3 kcal/mol of DV300 at def2-SVPD (%s)" % ", ".join(n3sv), F11)
    chg = [float("%.4f" % svd(r)) - float("%.4f" % r[5]) for r in f11]       # from the two columns as F11_two_tests.tsv prints them
    DV.add("DV325", "%+.4f" % min(chg), "derived", "smallest (def2-SVPD distance from DV300) minus (def2-TZVPD distance from DV220) among DIAGNOSTIC 37's eight", F11)
    DV.add("DV326", "%+.4f" % max(chg), "derived", "largest such difference among the eight", F11)
    DV.add("DV327", str(len(nine)), "count", "functionals with a committed barrier at def2-SVPD and def2-TZVPD on frame 42436, Amendment 1's entry included", F11)
    near_sv = sorted(nine, key=lambda r: abs(svd(r)))
    DV.add("DV328", "%+.4f" % svd(near_sv[0]), "derived; POST HOC" if near_sv[0][0] == "revDSD-PBEP86-D4" else "recomputed from raw outputs",
           "the smallest def2-SVPD distance from DV300 among the nine (%s)" % near_sv[0][0], F11)
    near_tz = sorted(nine, key=lambda r: abs(r[5]))
    DV.add("DV329", ", ".join(r[0] for r in near_tz[:3]), "derived; POST HOC", "the three of the nine nearest DV220 at def2-TZVPD, nearest first", F11)
    for i, fn in enumerate(list(POOLKEY) + ["revDSD-PBEP86-D4"]):
        r = next(x for x in nine if x[0] == fn)
        DV.add("DV%d" % (330 + i), "%+.4f" % (r[2] - bench), "derived; POST HOC", "%s/def2-SVPD barrier minus DV220, the def2-TZVPD benchmark" % fn, F11)
    near_mx = sorted(nine, key=lambda r: abs(r[2] - bench))
    DV.add("DV339", ", ".join(r[0] for r in near_mx[:3]), "derived; POST HOC", "the three of the nine whose def2-SVPD barrier is nearest DV220, nearest first", F11)
    DV.add("DV340", fmt(rsd_sv, 4), "recomputed from raw outputs", "revDSD-PBEP86-D4/def2-SVPD barrier, arm RI of DIAGNOSTIC 37 Amendment 1", F11)
    DV.add("DV341", fmt(rsd_tz, 4), "recomputed from raw outputs", "revDSD-PBEP86-D4/def2-TZVPD barrier, arm RI", F11)
    DV.add("DV342", "%+.4f" % (rsd_tz - rsd_sv), "recomputed from raw outputs", "DV341 - DV340", F11)
    DV.add("DV343", "%+.4f" % (rsd_tz - bench), "recomputed from raw outputs", "DV341 - DV220; test 2 as Amendment 1 fixed it (DA1.3)", F11)
    DV.add("DV344", "%+.4f" % rsd[7], "derived", "revDSD-PBEP86-D4/def2-SVPD, reactant: highest occupied orbital (d37a1.tsv) minus the target, eV", F11)
    DV.add("DV345", "%+.4f" % (rsd_sv - rsd_k_sv), "recomputed from raw outputs", "arm RI minus arm K, def2-SVPD barrier, kcal/mol", S6 + "/d37a1")
    DV.add("DV346", "%+.4f" % (rsd_tz - rsd_k_tz), "recomputed from raw outputs", "arm RI minus arm K, def2-TZVPD barrier, kcal/mol", S6 + "/d37a1")
    DV.add("DV347", "%.1e" % max(abs(A1[("RI", b)][s]["E"] - A1[("K", b)][s]["E"]) for b in ("def2-SVPD", "def2-TZVPD") for s in ("R", "TS")),
           "recomputed from raw outputs", "largest |arm RI - arm K| over the four total energies, Eh", S6 + "/d37a1")
    both_tz = [r[0] for r in nine if abs(r[5]) < 3.0 and r[6] < 0]
    DV.add("DV372", str(len(both_tz)), "derived; POST HOC",
           "functionals of the nine within 3 kcal/mol of DV220 at def2-TZVPD whose highest occupied orbital is also below zero at def2-SVPD, reactant (%s)"
           % ", ".join(both_tz), F11)
    both_sv = [r[0] for r in nine if abs(svd(r)) < 3.0 and r[6] < 0]
    DV.add("DV373", str(len(both_sv)), "derived; POST HOC",
           "functionals of the nine within 3 kcal/mol of DV300 at def2-SVPD whose highest occupied orbital is also below zero at def2-SVPD, reactant (%s)"
           % ", ".join(both_sv), F11)
    DV.add("DV348", str(len(list((root / "d37a1").glob("*/job.out")))), "count", "number of committed job.out files under %s/d37a1" % S6, S6 + "/d37a1")
    DV.add("DV349", str(sum(1 for q in (root / "d37a1").glob("*/job.out") if "****ORCA TERMINATED NORMALLY****" in q.read_text(errors="replace"))),
           "count", "of those, normally terminated", S6 + "/d37a1")

    # ============================ DIAGNOSTIC 40: detachment energies at the density-functional level ==========
    # VDE = E(monoanion) - E(dianion) at the same geometry with the same external charges.  The monoanion single points
    # are unrestricted, which the committed cs6_audit.read does not parse, so they are read here by the rule of DIAGNOSTIC
    # 40's own reader: a plain or point-charge run gives the last FINAL SINGLE POINT ENERGY; a QM/MM run gives the (QM/MM)
    # total, which must be the QM energy plus the (MM) term.  <S**2> is read where ORCA prints it; stability and the shift
    # markers are those of cs6_d33b.  Each dianion energy is that of the committed run d40.tsv names as the source, read
    # through the committed readers; that the pair is one geometry with one set of charges is checked here, by content.
    D40R, D40T = S6 + "/STAGE6_DIAGNOSTIC40_RESULT_20261115.txt", S6 + "/d40.tsv"
    CHG = r"^\s*Total Charge\s+Charge\s+\.+\s+(-?\d+)\s*$"
    MUL = r"^\s*Multiplicity\s+Mult\s+\.+\s+(\d+)\s*$"

    def mono(d, kind):
        d = Path(d)
        t = (d / "job.out").read_text(errors="replace")
        if "****ORCA TERMINATED NORMALLY****" not in t or "SCF NOT CONVERGED" in t or not re.search(r"SCF CONVERGED AFTER\s+\d+\s+CYCLES", t):
            stop("%s is not a normally terminated, converged run" % d)
        if (sorted(set(re.findall(CHG, t, re.M))), sorted(set(re.findall(MUL, t, re.M)))) != (["-1"], ["2"]):
            stop("%s is not a monoanion doublet" % d)
        qm = re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)
        mm = re.findall(r"FINAL SINGLE POINT ENERGY \(MM\)\s+(-?\d+\.\d+)", t)
        tot = re.findall(r"FINAL SINGLE POINT ENERGY \(QM/MM\)\s+(-?\d+\.\d+)", t)
        if kind == "qmmm":
            if not (len(qm) == len(mm) == len(tot) == 1) or abs(float(qm[0]) + float(mm[0]) - float(tot[0])) > 1e-9:
                stop("%s does not print one QM, one (MM) and one (QM/MM) energy that add up" % d)
            e, emm = float(tot[0]), float(mm[0])
        else:
            if mm or tot or len(qm) != 1:
                stop("%s is not a plain single point with one final energy" % d)
            e, emm = float(qm[0]), 0.0
        s2 = re.findall(r"Expectation value of <S\*\*2>\s*:\s*(\d+\.\d+)", t)
        if len(s2) != 1:
            stop("%s prints <S**2> %d times" % (d, len(s2)))
        return dict(E=e, Emm=emm, s2=float(s2[0]), stab=d33b.stability(t), shifted=any(re.search(x, t) for x in d33b.SHIFT),
                    level=level_of(t), sig=dist_signature(echoed_coords(t) or []), rel=d.relative_to(res).as_posix())

    def same_files(a, b, names):
        return all((Path(a) / n).is_file() and (Path(b) / n).is_file() and sha(Path(a) / n) == sha(Path(b) / n) for n in names)

    t40 = (root / "STAGE6_DIAGNOSTIC40_RESULT_20261115.txt").read_text()
    rec40, hdr40 = {}, None
    for l in (root / "d40.tsv").read_text().splitlines():
        f = l.split("\t")
        if hdr40 is None:
            hdr40 = f
            continue
        rec40[f[1]] = dict(zip(hdr40, f + [""] * (len(hdr40) - len(f))))
    if any(v["status"] != "measured" for v in rec40.values()):
        stop("d40.tsv holds a run that is not marked measured")
    A40 = [("A_B3LYP", "B3LYP-D3BJ"), ("A_CAM", "CAM-B3LYP-D3BJ"), ("A_wB97XD3", "wB97X-D3"), ("A_wB97MV", "wB97M-V"), ("A_wB97XV", "wB97X-V"),
           ("A_PW6B95", "PW6B95-D3BJ"), ("A_M062X", "M06-2X-D3(0)"), ("A_PWPB95", "PWPB95-D3BJ")]
    B40 = [("bare", "plain", None), ("ADD-s540_qm06500", "qmmm", "d34"), ("ADD-s678_qm07625", "qmmm", "d34"), ("ADD-s678_qm10000", "qmmm", "d34"),
           ("bare_n05_q0.50", "pc", "d33b"), ("bare_n11_q0.25", "pc", "d33b")]
    FILES40 = {"plain": ("substrate.xyz",), "pc": ("substrate.xyz", "pc.pc"), "qmmm": ("combined.xyz", "site.ORCAFF.prms")}
    if len(rec40) != len(A40) + 2 * len(B40):
        stop("d40.tsv holds %d runs, expected %d" % (len(rec40), len(A40) + 2 * len(B40)))

    def pair(rn, kind, st):
        """(monoanion, dianion energy, the dianion's reading) for one run of DIAGNOSTIC 40."""
        mo = mono(root / "d40" / rn, kind)
        src = root / rec40[rn]["source"]
        di = run(src)
        if di is None or not di["norm"] or di["notconv"] or di["chmult"] != (["-2"], ["1"]):
            stop("%s is not a normally terminated, converged dianion run" % src)
        if not same_files(root / "d40" / rn, src, FILES40[kind]):
            stop("%s and %s do not hold the same geometry and charges, byte for byte" % (rn, rec40[rn]["source"]))
        if state_of(mo) != st or state_of(di) != st or mo["level"][:4] != di["level"][:4] or mo["level"][4] != di["level"][4]:
            stop("%s and its source are not one level of theory on frame 42436's %s geometry" % (rn, st))
        if kind == "qmmm":
            nat = int((src / "combined.xyz").read_text().split()[0])
            etot, emm, _g = analyse.read_run(src, nat - 24)
            if abs(emm - mo["Emm"]) > 1e-12:
                stop("%s and its source do not carry the same (MM) term" % rn)
            edi = etot
        else:
            edi = di["E"]
        return mo, edi, di

    s402 = t40[t40.index("R40.2 "):t40.index("R40.3 ")]
    s404 = t40[t40.index("R40.4 "):t40.index("R40.5 ")]
    s406 = t40[t40.index("R40.6 "):t40.index("R40.7 ")]
    t12, k40 = [], 0
    for rn, fn in A40:
        mo, edi, di = pair(rn, "plain", "R")
        if PRETTY[mo["level"][0]] != PRETTY[POOLKEY[fn]] or mo["level"][1] != "DEF2-SVPD":
            stop("%s is not %s/def2-SVPD" % (rn, fn))
        v = (mo["E"] - edi) * EV
        r = rec40[rn]
        for what, mine, rec, tol, nd in (("E(monoanion), Eh", mo["E"], float(r["E_mono_Eh"]), 1e-8, 8), ("E(dianion), Eh", edi, float(r["E_di_Eh"]), 1e-8, 8),
                                         ("detachment energy, eV", v, float(r["VDE_eV"]), 6e-5, 4), ("<S**2> of the monoanion", mo["s2"], float(r["S2"]), 1e-6, 6),
                                         ("highest occupied orbital of the dianion, eV", di["homo"], float(r["homo_di_eV"]), 1.5e-4, 4)):
            k40 += 1
            control("C48.%02d" % k40, "DIAGNOSTIC 40 part A, %s, %s (d40.tsv)" % (fn, what), mine, rec, D40T, tol, nd)
        # the orbital energy DIAGNOSTIC 40 sets beside the detachment energy is the committed one of d37.tsv ("Each orbital
        # energy read here is the one d37.tsv carries"); controls C42 hold it against the raw output.  The sum is formed the same way.
        hrec = rec37[(fn, "def2-SVPD")]["hR"]
        m = re.search(r"^\s+" + re.escape(fn) + r"\s+(-\d+\.\d{8})\s+(-\d+\.\d{8})\s+([+-]\d+\.\d{4})\s+(\d\.\d{6})\s+([+-]\d+\.\d{4})\s+([+-]\d+\.\d{4})\s*$", s402, re.M)
        if not m:
            stop("DIAGNOSTIC 40's result does not print %s in R40.2" % fn)
        for what, mine, rec, tol, nd in (("detachment energy, eV", v, float(m.group(3)), 6e-5, 4), ("<S**2> of the monoanion", mo["s2"], float(m.group(4)), 1e-6, 6),
                                         ("the orbital energy it is set beside, eV", hrec, float(m.group(5)), 1e-9, 4),
                                         ("orbital energy plus detachment energy, eV", hrec + v, float(m.group(6)), 6e-5, 4)):
            k40 += 1
            control("C48.%02d" % k40, "DIAGNOSTIC 40 R40.2, %s, %s" % (fn, what), mine, rec, D40R, tol, nd)
        t12.append((fn, rn, rec40[rn]["source"], fmt(mo["E"], 8), fmt(edi, 8), "%+.4f" % v, fmt(mo["s2"], 6), "%+.4f" % hrec, "%+.4f" % (hrec + v), v))
    write_tsv(out / "T12_d40_bare_functionals.tsv",
              ["T12. DIAGNOSTIC 40, part A: the detachment energy of the BARE dianion at the reactant, frame 42436, def2-SVPD, in vacuo, by functional.",
               "VDE = E(monoanion) - E(dianion) at one geometry, in eV at %.12f eV per Eh; positive means bound.  Vertical, not adiabatic." % EV,
               "E_mono is the last FINAL SINGLE POINT ENERGY of %s/d40/<run>/job.out (unrestricted Kohn-Sham); E_di is that of the committed" % S6,
               "dianion run named in source, through the committed phase2.2/cs6_audit.py read().  Controls C48 compare with d40.tsv.",
               "HOMO_di_eV: the committed dianion's highest occupied orbital, as d37.tsv carries it.  HOMO_plus_VDE_eV is zero for a functional whose orbital energy",
               "equals minus its own detachment energy.  These monoanions are NOT analysed for stability, so each value is an upper bound",
               "in that sense (D40.3).  <S**2> is reported and not corrected; the ideal value is 0.75.",
               "The comparison with a coupled-cluster value (R40.3) is NOT EVALUATED: DIAGNOSTIC 40 leaves it to a dated addendum."],
              ["functional", "run", "source", "E_mono_Eh", "E_di_Eh", "VDE_eV", "S2", "HOMO_di_eV", "HOMO_plus_VDE_eV"], [r[:9] for r in t12])

    t13, vde40 = [], {}
    for name, kind, where in B40:
        for st in ("R", "TS"):
            rn = "B_%s_%s" % (name, st)
            mo, edi, di = pair(rn, kind, st)
            if mo["level"][:2] != ("CAM-B3LYP", "DEF2-SVPD"):
                stop("%s is not CAM-B3LYP/def2-SVPD" % rn)
            if not mo["stab"]["ran"] or mo["stab"]["first"] is None or mo["stab"]["last"] is None:
                stop("%s carries no readable stability analysis" % rn)
            v = (mo["E"] - edi) * EV
            word = "BOUND" if v > 0 else "METASTABLE"
            r = rec40[rn]
            if r["word"] != word or r["stab_first"] != mo["stab"]["first"] or r["stab_last"] != mo["stab"]["last"]:
                stop("%s: d40.tsv says %s, %s/%s; read here %s, %s/%s" % (rn, r["word"], r["stab_first"], r["stab_last"], word, mo["stab"]["first"], mo["stab"]["last"]))
            for what, mine, rec, tol, nd in (("E(monoanion), Eh", mo["E"], float(r["E_mono_Eh"]), 1e-8, 8), ("E(dianion), Eh", edi, float(r["E_di_Eh"]), 1e-8, 8),
                                             ("detachment energy, eV", v, float(r["VDE_eV"]), 6e-5, 4), ("<S**2> of the monoanion", mo["s2"], float(r["S2"]), 1e-6, 6)):
                k40 += 1
                control("C48.%02d" % k40, "DIAGNOSTIC 40 part B, %s %s, %s (d40.tsv)" % (name, st, what), mine, rec, D40T, tol, nd)
            m = re.search(r"^\s+" + re.escape(name) + r"\s+" + st + r"\s+([+-]\d+\.\d{4})\s+(BOUND|METASTABLE)\s+(\d\.\d{6})\s+(\w+)/(\w+)\s+(yes|no)\s+(yes|no)\s*$", s404, re.M)
            if not m:
                stop("DIAGNOSTIC 40's result does not print %s %s in R40.4" % (name, st))
            if (m.group(2), m.group(4), m.group(5)) != (word, mo["stab"]["first"], mo["stab"]["last"]) or (m.group(6) == "yes" or m.group(7) == "yes") != mo["shifted"]:
                stop("%s: DIAGNOSTIC 40's R40.4 and the raw output do not give one reading" % rn)
            for what, mine, rec, tol, nd in (("detachment energy, eV", v, float(m.group(1)), 6e-5, 4), ("<S**2> of the monoanion", mo["s2"], float(m.group(3)), 1e-6, 6)):
                k40 += 1
                control("C48.%02d" % k40, "DIAGNOSTIC 40 R40.4, %s %s, %s" % (name, st, what), mine, rec, D40R, tol, nd)
            q, _rep = charges_of(root / "d40" / rn)
            if kind == "qmmm":
                nat = int((root / "d40" / rn / "combined.xyz").read_text().split()[0])
                q = sphere_charges(root / "d40" / rn / "site.ORCAFF.prms", nat - 24)
            vde40[(name, st)] = dict(v=v, word=word, E=edi, mo=mo, nq=len(q), sumq=sum(q), maxq=max(q) if q else 0.0, minq=min(q) if q else 0.0)
    # the lowering each arrangement is quoted with, recomputed from the committed dianion outputs against the charge-free control
    # of the same diagnostic: D34 arm 2's S6-C for its three, D31's control for the two of D33 stage B
    QUOTED = {"ADD-s540_qm06500": -3.3985, "ADD-s678_qm07625": -4.1567, "ADD-s678_qm10000": -5.3701, "bare_n05_q0.50": -14.3612, "bare_n11_q0.25": -13.0007}
    ctl40 = {"d34": {st: X[("a2", "S6-C", st)]["Etot"] for st in ("R", "TS")}, "d33b": {st: run(root / "d31" / ("ctl_%s" % st))["E"] for st in ("R", "TS")}}
    for i, (name, kind, where) in enumerate(B40[1:]):
        dde = ((vde40[(name, "TS")]["E"] - ctl40[where]["TS"]) - (vde40[(name, "R")]["E"] - ctl40[where]["R"])) * H
        if not re.search(r"^\s+%s\s+quoted lowering %s kcal/mol" % (re.escape(name), re.escape("%.4f" % QUOTED[name])), t40, re.M):
            stop("DIAGNOSTIC 40's result does not quote %.4f for %s" % (QUOTED[name], name))
        control("C49.%d" % (i + 1), "DIAGNOSTIC 40 R40.7, %s: the quoted lowering, recomputed from the committed dianion outputs, kcal/mol" % name,
                dde, QUOTED[name], D40R, 6e-5, 4)
        vde40[(name, "R")]["dde"] = vde40[(name, "TS")]["dde"] = dde
        m = re.search(r"^\s+" + re.escape(name) + r"\s+([+-]\d+\.\d{4})\s+([+-]\d+\.\d{4})\s*$", s406, re.M)
        if not m:
            stop("DIAGNOSTIC 40's result does not print %s in R40.6" % name)
        for j, st in enumerate(("R", "TS")):
            control("C49.%d" % (6 + 2 * i + j), "DIAGNOSTIC 40 R40.6, %s %s: detachment energy minus the bare substrate's at the same state, eV" % (name, st),
                    vde40[(name, st)]["v"] - vde40[("bare", st)]["v"], float(m.group(1 + j)), D40R, 6e-5, 4)
    for name, kind, where in B40:
        for st in ("R", "TS"):
            x = vde40[(name, st)]
            mo = x["mo"]
            t13.append((name, st, "B_%s_%s" % (name, st), rec40["B_%s_%s" % (name, st)]["source"], x["nq"], "%+.4f" % x["sumq"] if x["nq"] else "-",
                        "%+.4f" % x["maxq"] if x["nq"] else "-", "%+.4f" % x["minq"] if x["nq"] else "-",
                        fmt(mo["E"], 8), fmt(x["E"], 8), "%+.4f" % x["v"], x["word"], fmt(mo["s2"], 6), mo["stab"]["first"], mo["stab"]["last"],
                        "yes" if mo["shifted"] else "no", "%+.4f" % (x["v"] - vde40[("bare", st)]["v"]) if name != "bare" else "-",
                        "%.4f" % x["dde"] if "dde" in x else "-"))
    write_tsv(out / "T13_d40_arrangements.tsv",
              ["T13. DIAGNOSTIC 40, part B: the detachment energy with each arrangement's charges present, CAM-B3LYP-D3BJ/def2-SVPD, frame 42436,",
               "both states, with the stability analysis on the monoanion.  The five arrangements are those whose lowering the record held quotable.",
               "VDE = E(monoanion) - E(dianion) at the same geometry with the same external charges, eV at %.12f eV per Eh." % EV,
               "word: BOUND if VDE is above zero, METASTABLE if it is at or below zero (the convention of Probe 2 and of DIAGNOSTIC 40).",
               "Where VDE is negative its SIGN is the reading and its size is not (D40.4): a METASTABLE species has no bound state to converge to.",
               "E_mono: %s/d40/<run>/job.out; for a QM/MM run the (QM/MM) total.  E_di: the committed dianion run named in source" % S6,
               "(cs6_analyse.read_run for a QM/MM run).  The (MM) Lennard-Jones term is the same in both and cancels.  Controls C48: d40.tsv.",
               "stab_first/stab_last: the monoanion's first and last stability analysis (cs6_d33b.stability).  shift: TRAH or a level shift engaged.",
               "dVDE_vs_bare_eV: this row's VDE minus the bare substrate's at the same state.  REPORTED, NOT INTERPRETED (R40.6).",
               "quoted_ddE_kcal: the lowering the record quotes for the arrangement, recomputed here from the committed dianion outputs (controls C49).",
               "Probe 2: a ddE measured where the dianion is METASTABLE 'is not a barrier effect and must not be reported as one'.",
               "DIAGNOSTIC 40 withdraws nothing and changes no verdict (D40.1).  One basis, one frame, vertical; all five sit inside r_safe."],
              ["arrangement", "state", "run", "source", "n_charges", "sum_q_e", "largest_q_e", "most_negative_q_e", "E_mono_Eh", "E_di_Eh", "VDE_eV", "word",
               "S2", "stab_first", "stab_last", "shift", "dVDE_vs_bare_eV", "quoted_ddE_kcal"], t13)
    f12 = [("A: bare dianion, reactant, by functional", r[0], "R", r[5], "BOUND" if r[9] > 0 else "METASTABLE", "-") for r in sorted(t12, key=lambda r: r[9])]
    f12 += [("B: CAM-B3LYP-D3BJ, with the arrangement's charges", r[0], r[1], r[10], r[11], r[17]) for r in t13]
    write_tsv(out / "F12_detachment_energy.tsv",
              ["F12. DIAGNOSTIC 40: detachment energies, E(monoanion) - E(dianion), def2-SVPD, frame 42436, frozen geometries.  Positive means bound.",
               "Panel A: the bare dianion at the reactant, one run per functional, no stability analysis (rows of T12_d40_bare_functionals.tsv).",
               "Panel B: CAM-B3LYP-D3BJ with each arrangement's charges present, both states, monoanion stable on its first and last analysis",
               "(rows of T13_d40_arrangements.tsv).  METASTABLE: at or below zero.  Where the value is negative its sign is the reading, not its size.",
               "quoted_ddE_kcal: the lowering the record quotes for the arrangement.  DIAGNOSTIC 40 withdraws nothing and changes no verdict."],
              ["panel", "row", "state", "VDE_eV", "word", "quoted_ddE_kcal"], f12)
    T12N, T13N = "figures/T12_d40_bare_functionals.tsv", "figures/T13_d40_arrangements.tsv"
    DV.add("DV350", str(len(list((root / "d40").rglob("job.inp")))), "count", "number of committed job.inp files under %s/d40" % S6, S6 + "/d40")
    DV.add("DV351", str(len(list((root / "d40").rglob("job.out")))), "count", "number of committed job.out files under %s/d40" % S6, S6 + "/d40")
    DV.add("DV352", str(len(t12) + len(t13)), "count", "monoanion single points of DIAGNOSTIC 40 read here: %d of part A, %d of part B" % (len(t12), len(t13)), S6 + "/d40")
    arr5 = [n for n, _k, _w in B40[1:]]
    DV.add("DV353", str(sum(1 for n in arr5 if all(vde40[(n, s)]["word"] == "METASTABLE" for s in ("R", "TS")))), "recomputed from raw outputs",
           "of the five quotable arrangements, those METASTABLE at both states, CAM-B3LYP-D3BJ/def2-SVPD", T13N)
    DV.add("DV354", str(sum(1 for n in arr5 for s in ("R", "TS") if vde40[(n, s)]["word"] == "METASTABLE")), "recomputed from raw outputs",
           "of the ten arrangement-states (five arrangements, two states), those METASTABLE", T13N)
    DV.add("DV355", "%+.4f" % min(r[9] for r in t12), "recomputed from raw outputs", "smallest detachment energy of the bare dianion among the eight functionals, eV (%s)"
           % min(t12, key=lambda r: r[9])[0], T12N)
    DV.add("DV356", "%+.4f" % max(r[9] for r in t12), "recomputed from raw outputs", "largest detachment energy of the bare dianion among the eight functionals, eV (%s)"
           % max(t12, key=lambda r: r[9])[0], T12N)
    DV.add("DV357", str(sum(1 for r in t12 if r[9] > 0)), "recomputed from raw outputs", "functionals of the eight at which the bare dianion is bound at the reactant", T12N)
    neg = [vde40[(n, s)]["v"] for n in arr5 for s in ("R", "TS")]
    DV.add("DV358", "%+.4f" % max(neg), "recomputed from raw outputs", "the detachment energy nearest zero among the ten arrangement-states, eV", T13N)
    DV.add("DV359", "%+.4f" % min(neg), "recomputed from raw outputs", "the most negative detachment energy among the ten arrangement-states, eV", T13N)
    DV.add("DV360", fmt(max(vde40[(n, s)]["mo"]["s2"] for n, _k, _w in B40 for s in ("R", "TS")), 6), "recomputed from raw outputs",
           "largest <S**2> among the twelve monoanions of part B (ideal 0.75)", T13N)
    DV.add("DV361", fmt(max(float(r[6]) for r in t12), 6), "recomputed from raw outputs", "largest <S**2> among the eight monoanions of part A (ideal 0.75)", T12N)
    DV.add("DV362", str(sum(1 for n, _k, _w in B40 for s in ("R", "TS") if vde40[(n, s)]["mo"]["stab"]["first"] != "STABLE" or vde40[(n, s)]["mo"]["stab"]["last"] != "STABLE")),
           "recomputed from raw outputs", "monoanions of part B whose first or last stability analysis is not STABLE", T13N)
    DV.add("DV363", str(sum(1 for n, _k, _w in B40 for s in ("R", "TS") if vde40[(n, s)]["mo"]["shifted"])), "recomputed from raw outputs",
           "monoanions of part B in which TRAH or a level shift was engaged", T13N)
    DV.add("DV364", "%+.4f" % vde40[("bare", "TS")]["v"], "recomputed from raw outputs", "detachment energy of the bare dianion at the transition state, CAM-B3LYP-D3BJ/def2-SVPD, eV", T13N)
    DV.add("DV365", "%+.4f" % vde40[("bare", "R")]["v"], "recomputed from raw outputs", "detachment energy of the bare dianion at the reactant, CAM-B3LYP-D3BJ/def2-SVPD, eV", T13N)
    DV.add("DV366", "%.1e" % abs(mono(root / "d40" / "A_CAM", "plain")["E"] - vde40[("bare", "R")]["mo"]["E"]), "recomputed from raw outputs",
           "|E(A_CAM) - E(B_bare_R)|: one species at one level, without and with the stability analysis, Eh", S6 + "/d40")
    DV.add("DV367", str(len(arr5)), "count", "arrangements of part B other than the bare substrate", T13N)
    cam_a = next(r for r in t12 if r[0] == "CAM-B3LYP-D3BJ")
    DV.add("DV368", cam_a[8], "derived", "CAM-B3LYP-D3BJ/def2-SVPD, reactant: highest occupied orbital plus its own detachment energy, eV", T12N)
    DV.add("DV369", "%+.4f" % min(float(r[8]) for r in t12), "derived", "smallest highest-occupied-orbital-plus-detachment-energy among the eight, eV (%s)"
           % min(t12, key=lambda r: float(r[8]))[0], T12N)
    DV.add("DV370", "%+.4f" % max(float(r[8]) for r in t12), "derived", "largest highest-occupied-orbital-plus-detachment-energy among the eight, eV (%s)"
           % max(t12, key=lambda r: float(r[8]))[0], T12N)


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
    d31net = []
    for r in f3:
        cname = ("n%02d" % int(r[1])) if r[0] == "A" else ("n%02d_q%s" % (int(r[1]), r[2]))
        qs, _rep = charges_of(root / "d31" / r[0] / (cname + "_R"))
        tab.append(("D31", "bare point charge", "%s/%s" % (r[0], cname), len(qs), fmt(max([x for x in qs if x > 0] or [0.0]), 4),
                    fmt(min([x for x in qs if x < 0] or [0.0]), 4), r[3]))
        d31net.append((r[3], sum(qs)))
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
    # the net charge of DIAGNOSTIC 31's RELIABLE conditions: what a binding test of arrangements that are not net negative could
    # be run on without a new dianion single point (section 11).  Charges from d31/<family>/<condition>_R/pc.pc, as T5 reads them.
    rel31 = [s for v, s in d31net if v == "RELIABLE"]
    DV.add("DV374", str(len(rel31)), "derived", "DIAGNOSTIC 31 conditions that are RELIABLE", "figures/T5_positive_charge_vs_verdict.tsv")
    DV.add("DV375", str(sum(1 for s in rel31 if s > -5e-5)), "derived", "of DV374, those whose charges sum to zero or more",
           S6 + "/d31/<family>/<condition>_R/pc.pc")
    DV.add("DV376", str(sum(1 for s in rel31 if s <= -5e-5)), "derived", "of DV374, those whose charges sum to less than zero",
           S6 + "/d31/<family>/<condition>_R/pc.pc")
    DV.add("DV377", str(2 * sum(1 for s in rel31 if s > -5e-5)), "derived", "2 x DV375: monoanion single points for those conditions at both states",
           S6 + "/d31/<family>/<condition>_R/pc.pc")
    DV.add("DV378", "%+.4f" % min(rel31), "derived", "smallest net charge among DIAGNOSTIC 31's RELIABLE conditions, e", S6 + "/d31/<family>/<condition>_R/pc.pc")
    DV.add("DV379", "%+.4f" % max(rel31), "derived", "largest net charge among DIAGNOSTIC 31's RELIABLE conditions, e", S6 + "/d31/<family>/<condition>_R/pc.pc")
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
    # ---------------- T5 counted the way DIAGNOSTIC 38's pre-registration counts it (its section 3) ----------------
    T5N = "figures/T5_positive_charge_vs_verdict.tsv"
    pos = [t for t in tab if float(t[4]) > 0.0]
    DV.add("DV200", str(len(tab)), "count", "designs tabulated in T5", T5N)
    DV.add("DV201", str(len(pos)), "derived", "of those, carrying at least one positive charge", T5N)
    DV.add("DV202", str(sum(1 for t in pos if t[6] == "RELIABLE")), "derived", "of DV201, RELIABLE", T5N)
    DV.add("DV203", str(sum(1 for t in tab if t[6] == "RELIABLE")), "derived", "designs of T5 that are RELIABLE", T5N)
    # ---------------- T9: the highest occupied orbital with the charges present (DATA ONLY; POST HOC) ----------------
    # The record holds that the sign of a functional's highest occupied orbital is not a test of whether an anion is
    # bound (DIAGNOSTIC 2; Probe 1 Erratum 1; Probe 2: "THE HOMO IS NOT THE TEST").  It is tabulated here because
    # DIAGNOSTIC 38's pre-registered gate G38.10 reads it, and because no detachment energy exists at this level.
    t9 = []
    for t in tab:
        if t[0] == "D34 arm 2":
            dd = {st: root / "d34" / ("a2_%s_%s" % (t[2], st)) for st in ("R", "TS")}
        elif t[0] == "D33 stage B":
            dd = {st: root / "d33b" / ("%s_%s" % (t[2], st)) for st in ("R", "TS")}
        else:
            dd = {st: root / "d31" / ("%s_%s" % (t[2], st)) for st in ("R", "TS")}
        cs = {}
        for st in ("R", "TS"):
            c = run(dd[st])
            if c is None or not c["norm"] or c["notconv"] or c["level"][0] != "CAM-B3LYP" or c["level"][1] != "DEF2-SVPD":
                stop("%s is not a normally terminated, converged CAM-B3LYP/def2-SVPD run" % dd[st])
            cs[st] = c
        sh = cs["R"]["shifted"] or cs["TS"]["shifted"]
        hi = max(cs["R"]["homo"], cs["TS"]["homo"])
        t9.append((t[0], t[1], t[2], t[3], t[4], t[5], t[6], "%+.4f" % cs["R"]["homo"], "%+.4f" % cs["TS"]["homo"],
                   "yes" if sh else "no", "unreadable" if sh else ("above zero" if hi >= 0.0 else "below zero"), hi, sh))
    write_tsv(out / "T9_orbital_with_charges.tsv",
              ["T9. DATA ONLY, POST HOC. The highest occupied orbital of the substrate with each design's charges present, for every design of T5,",
               "CAM-B3LYP-D3BJ/def2-SVPD, frame 42436, frozen geometries; read from the raw outputs through the committed phase2.2/cs6_audit.py read().",
               "THE RECORD HOLDS THAT THIS IS NOT A TEST OF WHETHER THE DIANION IS BOUND: the test is the detachment energy (DIAGNOSTIC 2,",
               "Probe 1 Erratum 1, Probe 2), and no detachment energy exists at this level for any of these designs.",
               "level_shift: a level shift or TRAH was engaged in either state, in which case the printed orbital energies are not the",
               "converged ones and reading is 'unreadable'.  reading: whether the larger of the two states' values is at or above zero.",
               "The charge-free control at this level is -0.5918 eV at the reactant and -0.3849 eV at the transition state.",
               "verdict is the committed four-leg verdict of T5, not re-judged; no committed criterion uses the orbital energy of a charged run."],
              ["diagnostic", "representation", "design", "n", "largest_positive_q_e", "most_negative_q_e", "verdict", "HOMO_R_eV", "HOMO_TS_eV",
               "level_shift", "reading"], [r[:11] for r in t9])
    T9N = "figures/T9_orbital_with_charges.tsv"
    relb = [r for r in t9 if r[6] == "RELIABLE"]
    DV.add("DV204", str(sum(1 for r in relb if r[10] == "below zero")), "derived; POST HOC; data only",
           "RELIABLE designs of T5 whose highest occupied orbital is below zero in both states, no level shift engaged", T9N)
    DV.add("DV205", str(sum(1 for r in relb if r[10] == "above zero")), "derived; POST HOC; data only",
           "RELIABLE designs of T5 whose highest occupied orbital is at or above zero in at least one state, no level shift engaged", T9N)
    DV.add("DV206", str(sum(1 for r in relb if r[10] == "unreadable")), "derived; POST HOC; data only",
           "RELIABLE designs of T5 in which a level shift was engaged, so the orbital energy is not read", T9N)
    quot = [r for r in t9 if (r[0] == "D34 arm 2" and r[6] == "RELIABLE") or (r[0] == "D33 stage B" and r[2] in ("bare_n05_q0.50", "bare_n11_q0.25"))]
    if len(quot) != 5 or any(r[6] != "RELIABLE" or r[12] for r in quot):
        stop("the five quotable designs were not found RELIABLE and unshifted in T9")
    DV.add("DV207", str(len(quot)), "count", "designs with a quotable lowering at the corrected level: three of DIAGNOSTIC 34, two of DIAGNOSTIC 33 stage B", T9N)
    DV.add("DV208", str(sum(1 for r in quot if float(r[7]) >= 0 and float(r[8]) >= 0)), "derived; POST HOC; data only",
           "of DV207, highest occupied orbital at or above zero in BOTH states", T9N)
    DV.add("DV209", "%+.4f" % min(min(float(r[7]), float(r[8])) for r in quot), "recomputed from raw outputs; POST HOC; data only",
           "lowest highest-occupied-orbital energy among the five quotable designs, either state, eV", T9N)
    DV.add("DV210", "%+.4f" % max(max(float(r[7]), float(r[8])) for r in quot), "recomputed from raw outputs; POST HOC; data only",
           "highest highest-occupied-orbital energy among the five quotable designs, either state, eV", T9N)
    d34neg = [r for r in t9 if r[0] == "D34 arm 2" and r[6] == "RELIABLE"]
    DV.add("DV211", "%+.4f" % min(float(r[7]) for r in d34neg), "recomputed from raw outputs; POST HOC; data only",
           "lowest reactant highest-occupied-orbital energy among DIAGNOSTIC 34's three RELIABLE arrangements, eV", T9N)
    DV.add("DV212", "%+.4f" % max(float(r[7]) for r in d34neg), "recomputed from raw outputs; POST HOC; data only",
           "highest reactant highest-occupied-orbital energy among DIAGNOSTIC 34's three RELIABLE arrangements, eV", T9N)
    s678 = [r for r in t9 if r[0] == "D34 arm 2" and r[2] == "ADD-s678_qm10000"][0]
    DV.add("DV213", s678[7], "recomputed from raw outputs; POST HOC; data only",
           "highest occupied orbital of ADD-s678_qm10000, reactant, CAM-B3LYP-D3BJ/def2-SVPD, QM/MM with the Lennard-Jones term, eV", T9N)
    DV.add("DV214", str(2 * len(quot)), "derived", "5 quotable designs x 2 states: monoanion partners for a detachment energy at the corrected level", T9N)
    wl = [r for r in t9 if r[1] == "argon ECP centre" and r[6] == "RELIABLE"]
    DV.add("DV215", str(sum(1 for r in wl if r[10] == "below zero")), "derived; POST HOC; data only",
           "RELIABLE walled designs of DIAGNOSTIC 33 stage B whose highest occupied orbital is below zero in both states (of %d)" % len(wl), T9N)
    # ---------------- how much rests on the Loewdin threshold of 0.25 e (POST HOC) ----------------
    F4N = "figures/F4_relocation.tsv"
    for i, (lab, sel) in enumerate((("bare (DIAGNOSTIC 31)", [r for r in grid if r[0] == "bare"]),
                                    ("walled (DIAGNOSTIC 32)", [r for r in grid if r[0] == "walled" and r[1] != "wall0"]))):
        ris = sorted(float(r[8]) for r in sel)
        under, over_ = [x for x in ris if x < audit.D_LW], [x for x in ris if x >= audit.D_LW]
        DV.add("DV%d" % (270 + 4 * i), str(len(over_)), "recomputed from raw outputs; POST HOC", "charged %s conditions whose larger Loewdin rise is at or over %.2f e"
               % (lab, audit.D_LW), F4N)
        DV.add("DV%d" % (271 + 4 * i), fmt(max(under), 4), "recomputed from raw outputs; POST HOC", "largest such rise below %.2f e, %s" % (audit.D_LW, lab), F4N)
        DV.add("DV%d" % (272 + 4 * i), fmt(min(over_), 4), "recomputed from raw outputs; POST HOC", "smallest such rise at or over %.2f e, %s" % (audit.D_LW, lab), F4N)
        DV.add("DV%d" % (273 + 4 * i), fmt(audit.D_LW - max(under), 4), "derived; POST HOC", "%.2f - DV%d" % (audit.D_LW, 271 + 4 * i), F4N)
    wris = [float(r[8]) for r in grid if r[0] == "walled" and r[1] != "wall0"]
    bris = [float(r[8]) for r in grid if r[0] == "bare"]
    for i, cut in enumerate((0.24, 0.20, 0.15, 0.10)):
        DV.add("DV%d" % (280 + i), str(sum(1 for x in wris if x < cut)), "derived; POST HOC",
               "charged walled conditions whose larger Loewdin rise would be below a threshold of %.2f e" % cut, F4N)
    write_tsv(out / "T10_loewdin_thresholds.tsv",
              ["T10. POST HOC. How many charged conditions of DIAGNOSTIC 31 (bare) and DIAGNOSTIC 32 (walled) have their larger Loewdin rise",
               "below a threshold, for the committed threshold D_LW = %.2f e and four lower ones.  The rises are those of F4_relocation.tsv." % audit.D_LW,
               "The committed classifier uses %.2f e only; the other rows change no verdict and are a measure of how much rests on that number." % audit.D_LW],
              ["set", "threshold_e", "n_conditions", "n_below", "n_at_or_over"],
              [(lab, "%.2f" % cut, len(v), sum(1 for x in v if x < cut), sum(1 for x in v if x >= cut))
               for lab, v in (("bare (D31)", bris), ("walled (D32)", wris)) for cut in (audit.D_LW, 0.24, 0.20, 0.15, 0.10)])
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
    ("N13", "N0", "correlated benchmark, bare barrier (D36)",
     "measured: 23.8603 at DLPNO-CCSD(T)/def2-TZVPD; adopts no level",
     S6 + "/STAGE6_DIAGNOSTIC36_RESULT_20261114.txt", "THE BARRIER IS 23.8603 kcal/mol."),
    ("N14", "N13", "five further functionals (D37)",
     "measured; read against the benchmark post hoc only; the sixth NOT MEASURED until Amendment 1",
     S6 + "/STAGE6_DIAGNOSTIC37_RESULT_20261111.txt", "No score combines them and none is defined."),
    ("N15", "N13", "charges in the correlated step (D38)",
     "measured: yes, on the one interpretable arm; licenses the coupled-cluster test of ddE only",
     S6 + "/STAGE6_DIAGNOSTIC38_RESULT_20261115.txt", "THE EMBEDDING CHARGE REACHES THE CORRELATION TREATMENT."),
    ("N16", "N15", "detachment energy at that level (D39)", "open: result committed; NOT ENTERED in this revision",
     S6 + "/STAGE6_DIAGNOSTIC39_20261115.txt", "THE DETACHMENT ENERGY AT THE BENCHMARK LEVEL"),
    ("N17", "N13", "benchmark at the production basis (D41)",
     "measured: 22.8968 at def2-SVPD; its basis shift opposes the functionals'",
     S6 + "/STAGE6_DIAGNOSTIC41_RESULT_20261115.txt", "THE BARRIER AT def2-SVPD IS 22.8968 kcal/mol."),
    ("N18", "N14", "revDSD-PBEP86-D4 (D37 Amendment 1)",
     "measured: 21.4957 at def2-TZVPD, -2.3646 from the benchmark",
     S6 + "/STAGE6_DIAGNOSTIC37_AMENDMENT1_RESULT_20261115.txt",
     "revDSD-PBEP86-D4, arm RI, def2-TZVPD: 21.4957, which is -2.3646 from the benchmark."),
    ("N19", "N12", "is the dianion bound? (D40)",
     "METASTABLE at both states for all five quotable arrangements; withdraws nothing",
     S6 + "/STAGE6_DIAGNOSTIC40_RESULT_20261115.txt", "It withdraws nothing and changes no verdict (D40.1):"),
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

    # ---- F1.  One row per method, one marker per basis, so that a method is read along its row and the methods are
    # read against one another down the page.  Black, grey and white with a different shape for each basis: nothing
    # depends on colour.  The vertical line is DIAGNOSTIC 36's correlated barrier at def2-TZVPD.
    r1 = [r for r in read_tsv(out / "F1_reference_barrier.tsv") if r["solvation"] == "-"]
    r1b = read_tsv(out / "F1b_stage4e_bare_barrier.tsv")
    bsty = {"6-31G(d)": ("D", "white", 5.5), "def2-SVP": ("o", "white", 6.0), "ma-def2-SVP": ("v", "white", 6.0),
            "def2-SVPD": ("s", "#9a9a9a", 5.5), "def2-TZVPD": ("o", INK, 6.5)}
    border = list(bsty)

    def rowname(r):
        return r["functional"] + {"D3BJ": "-D3BJ", "D3ZERO": "-D3(0)", "-": ""}[r["dispersion"]]
    rows1 = {}
    for r in r1:
        rows1.setdefault(rowname(r), {})[r["basis"]] = float(r["barrier_kcal"])
    bench = rows1["DLPNO-CCSD(T)"]["def2-TZVPD"]

    def largest(d):
        return d[max(d, key=border.index)]
    names1 = sorted(rows1, key=lambda n: largest(rows1[n]))
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(9.6, 7.4), gridspec_kw={"height_ratios": [len(names1), 5.6]}, sharex=True)
    for y, n in enumerate(names1):
        d = rows1[n]
        ax.plot([min(d.values()), max(d.values())], [y, y], color=MUTE, lw=0.7, zorder=1)
        for b in border:
            if b in d:
                mk, fc, ms = bsty[b]
                ax.plot([d[b]], [y], marker=mk, ms=ms, mfc=fc, mec=INK, mew=0.9, ls="none", zorder=3)
        ax.text(max(d.values()) + 0.45, y, "%.2f" % largest(d), va="center", fontsize=7.5, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.axvline(bench, color=INK, lw=0.9, ls="--", zorder=0)
    ax.text(bench + 0.25, len(names1) - 0.42, "DLPNO-CCSD(T)/def2-TZVPD, %.2f:\nan electronic energy in vacuo,\nnot the experimental number" % bench,
            fontsize=7.2, va="top")
    ax.set_yticks(range(len(names1))); ax.set_yticklabels(names1); ax.set_ylim(-0.7, len(names1) - 0.3)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_title("Frame 42436, frozen geometries, in vacuo: the barrier of the bare substrate by method and basis")
    for b in border:
        mk, fc, ms = bsty[b]
        ax.plot([], [], marker=mk, ms=ms, mfc=fc, mec=INK, mew=0.9, ls="none", label=b)
    ax.legend(loc="lower right", fontsize=7.5, ncol=1, title="basis; the number is the value\nat the row's largest basis", title_fontsize=7.2)
    lab = {"L1": "B3LYP-D3BJ/def2-SVP", "L2": "B3LYP/6-31G(d)", "L3": "HF/6-31G(d)", "L4": "MP2/6-31G(d)", "L5": "wB97X-D3/def2-SVP"}
    ordb = sorted(r1b, key=lambda r: float(r["barrier_42436_kcal"]))
    for y, r in enumerate(ordb):
        a, b = float(r["barrier_41786_kcal"]), float(r["barrier_42436_kcal"])
        bx.plot([a, b], [y, y], color=MUTE, lw=0.9, zorder=1)
        bx.plot([a], [y], marker="o", ms=6, mfc="white", mec=INK, mew=0.9, ls="none", zorder=3)
        bx.plot([b], [y], marker="o", ms=6, mfc=INK, mec=INK, mew=0.9, ls="none", zorder=3)
        bx.text(b + 0.45, y, "%.2f  (%+.2f)" % (b, b - a), va="center", fontsize=7.5, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    bx.axvline(bench, color=INK, lw=0.9, ls="--", zorder=0)
    bx.plot([], [], marker="o", ms=6, mfc="white", mec=INK, mew=0.9, ls="none", label="frame 41786 (Stage 4e; reactant is a band image)")
    bx.plot([], [], marker="o", ms=6, mfc=INK, mec=INK, mew=0.9, ls="none", label="frame 42436 (DIAGNOSTIC 35; the Stage 6 geometries)")
    bx.legend(loc="lower right", fontsize=7.5)
    bx.set_yticks(range(len(ordb))); bx.set_yticklabels(["%s  %s" % (r["level"], lab[r["level"]]) for r in ordb])
    bx.set_ylim(-0.7, len(ordb) - 0.3); bx.grid(axis="x", color=GRID, lw=0.6)
    bx.set_title("Stage 4e's five levels at two frames: the number is frame 42436, with its change from frame 41786")
    bx.set_xlabel("E(TS) − E(R), bare substrate (kcal/mol)")
    bx.set_xlim(14.5, 46.5)
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
    # name each group of four markers.  A group sits at one height, its L4 value.  Labels go on the empty side of the
    # diagonal and are pushed apart where groups are closer than a line of text; a displaced label gets a leader.
    def name_of(r):
        nm = r["quantity"].replace(" alone", "") if r["kind"] == "residue alone" else "a, site %s" % re.match(r"a\((\d+)\)", r["quantity"]).group(1)
        return nm + (" (%s)" % r["set"] if r["set"] in ("C", "K") else "")

    def spread(ys, gap):
        o = list(ys)
        for i in range(1, len(o)):
            o[i] = max(o[i], o[i - 1] + gap)
        i = 0
        while i < len(o):                       # recentre each run of labels that had to be pushed
            j = i
            while j + 1 < len(o) and o[j + 1] - o[j] <= gap + 1e-9:
                j += 1
            sh = sum(ys[i:j + 1]) / (j - i + 1) - sum(o[i:j + 1]) / (j - i + 1)
            for t in range(i, j + 1):
                o[t] += sh
            i = j + 1
        return o
    for sign in (1, -1):
        grp = sorted([r for r in q if sign * float(r["L4"]) > 0], key=lambda r: float(r["L4"]))
        ylab = spread([float(r["L4"]) for r in grp], 0.56)
        for r, yl in zip(grp, ylab):
            y0 = float(r["L4"]); xs = [float(r[k]) for k in lv]
            if sign > 0:
                xa, ha, xd = min(min(xs), y0) - 0.45, "right", min(xs) - 0.14
            else:
                xa, ha, xd = max(max(xs), y0) + 0.45, "left", max(xs) + 0.14
            if abs(yl - y0) > 0.08:
                ax.plot([xa + (0.06 if sign > 0 else -0.06), xd], [yl, y0], color=MUTE, lw=0.5, zorder=2)
            ax.text(xa, yl, name_of(r), ha=ha, va="center", fontsize=7.2, color=INK, zorder=5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.85))
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
        if s.startswith(("ruled out", "inconclusive", "exploratory", "not recovered", "inside r_safe", "not adopted", "verdicts are",
                         "metastable")):
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


    # ---- F10: the highest occupied orbital of the bare dianion by functional.  Black and grey: each functional has
    # its own labelled column, so nothing here depends on colour.
    r10 = read_tsv(out / "F10_homo_by_functional.tsv")
    tgt = float(r10[0]["target_eV"])
    MINUS = "\u2212"
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    ax.axhspan(0, 2.2, facecolor="#f1f1f1", edgecolor="#c9c9c9", hatch="////", lw=0, zorder=0)
    ax.axhline(0, color=INK, lw=1.0, zorder=2)
    ax.axhline(tgt, color=INK, lw=1.0, ls=(0, (5, 3)), zorder=2)
    ax.text(2.62, 0.05, "vacuum level, 0 eV", ha="right", va="bottom", fontsize=8, color=INK)
    ax.text(-0.72, tgt - 0.07, ("where it should sit: %+.4f eV\n(minus the detachment energy, Probe 3)" % tgt).replace("-", MINUS),
            ha="left", va="top", fontsize=8, color=INK, linespacing=1.25)
    ax.text(-0.72, 2.05, "above the vacuum level: the electron is not bound", ha="left", va="top", fontsize=8.5, color=INK,
            style="italic", bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.text(-0.72, -1.72, "below it: bound", ha="left", va="bottom", fontsize=8.5, color=INK, style="italic")
    off = {("def2-SVPD", "TS"): 0.20, ("def2-TZVPD", "R"): 0.30, ("def2-TZVPD", "TS"): 0.40}
    mk = {("def2-SVPD", "TS"): dict(marker="o", mfc="white"), ("def2-TZVPD", "R"): dict(marker="^", mfc=MUTE),
          ("def2-TZVPD", "TS"): dict(marker="^", mfc="white")}
    funcs = []
    for r in r10:
        if r["functional"] not in [f[0] for f in funcs]:
            funcs.append((r["functional"], r["long_range_exact_exchange"]))
    for i, (fn, _x) in enumerate(funcs):
        p0 = float(next(r for r in r10 if r["functional"] == fn and r["basis"] == "def2-SVPD" and r["state"] == "R")["d28_eV"])
        ax.plot([i - 0.30, i + 0.08], [p0, p0], color=INK, lw=3.2, solid_capstyle="butt", zorder=4)
        ax.text(i - 0.34, p0, ("%+.4f" % p0).replace("-", MINUS), ha="right", va="center", fontsize=9, color=INK, fontweight="bold")
        for r in r10:
            if r["functional"] == fn and (r["basis"], r["state"]) in off:
                ax.plot([i + off[(r["basis"], r["state"])]], [float(r["d28_eV"])], ls="none", ms=6.5, mec=MUTE, mew=1.1, zorder=4,
                        **mk[(r["basis"], r["state"])])
        d = p0 - tgt
        if abs(d) > 0.3:
            ax.annotate("", xy=(i - 0.11, p0), xytext=(i - 0.11, tgt), arrowprops=dict(arrowstyle="<->", color=MUTE, lw=0.9, shrinkA=0, shrinkB=1.5), zorder=3)
            ax.text(i - 0.07, (p0 + tgt) / 2 + (0.15 if d > 0 else -0.05), "%.4f eV\ntoo %s" % (abs(d), "high" if d > 0 else "low"), ha="left",
                    va="center", fontsize=8, color=INK, bbox=dict(facecolor="white", edgecolor="none", pad=1.0, alpha=0.9))
        else:
            ax.text(i - 0.30, p0 - 0.10, "%.4f eV too %s" % (abs(d), "high" if d > 0 else "low"), ha="left", va="top", fontsize=8, color=INK)
    hd = [plt.Line2D([], [], color=INK, lw=3.2, label="def2-SVPD, reactant (D28's primary reading)"),
          plt.Line2D([], [], ls="none", marker="o", mfc="white", mec=MUTE, mew=1.1, ms=6.5, label="def2-SVPD, transition state"),
          plt.Line2D([], [], ls="none", marker="^", mfc=MUTE, mec=MUTE, mew=1.1, ms=6.5, label="def2-TZVPD, reactant"),
          plt.Line2D([], [], ls="none", marker="^", mfc="white", mec=MUTE, mew=1.1, ms=6.5, label="def2-TZVPD, transition state")]
    ax.legend(handles=hd, loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, fontsize=8, handlelength=1.6, columnspacing=1.6, borderaxespad=0)
    ax.set_xlim(-0.8, 2.7); ax.set_ylim(-1.8, 2.2)
    ax.set_xticks(range(len(funcs))); ax.set_xticklabels(["%s\n%s" % f for f in funcs])
    ax.set_xlabel("functional, and its fraction of long-range exact exchange")
    ax.set_ylabel("highest occupied orbital of the bare dianion (eV)")
    ax.set_yticks([-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0])
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=1); ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    fig.tight_layout(); save(fig, "F10_homo_by_functional")

    # ---- F11: the two tests the record holds for a functional, side by side.  One row per functional, the same order
    # in both panels.  Black and white only.  A filled marker is a comparison DIAGNOSTIC 36 pre-registered; an open one
    # is post hoc.  No score combines the panels and none is drawn.
    r11 = read_tsv(out / "F11_two_tests.tsv")
    bench11 = float([r for r in read_tsv(out / "T7_d36_benchmark.tsv") if r["quantity"] == "E(CCSD(T))"][0]["TS_minus_R_kcal"])
    bench11sv = float([r for r in read_tsv(out / "T11_d41_benchmark_svpd.tsv") if r["quantity"] == "E(CCSD(T))"][0]["barrier_SVPD_kcal"])
    tgt11 = float(r11[0]["homo_SVPD_R_eV"]) - float(r11[0]["homo_minus_target_eV"])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.6, 5.2), gridspec_kw={"width_ratios": [1.25, 1]}, sharey=True)
    for y, r in enumerate(r11):
        pre = r["kind"] == "committed"
        mk11 = dict(marker="D", ms=6.2, mfc=INK) if r["kind"] == "amendment 1" else dict(marker="o", ms=7, mfc=INK if pre else "white")
        sv, tz, hm = float(r["barrier_SVPD_kcal"]), float(r["barrier_TZVPD_kcal"]), float(r["homo_SVPD_R_eV"])
        ax.plot([sv, tz], [y, y], color=MUTE, lw=0.7, zorder=1)
        ax.plot([sv], [y], marker="s", ms=5, mfc="#9a9a9a", mec=INK, mew=0.8, ls="none", zorder=3)
        ax.plot([tz], [y], mec=INK, mew=1.1, ls="none", zorder=4, **mk11)
        ax.text(max(sv, tz) + 0.5, y, ("%+.2f | %+.2f" % (float(r["minus_benchmark_kcal"]), float(r["minus_SVPD_benchmark_kcal"]))).replace("-", MINUS),
                va="center", fontsize=7.6, zorder=5, bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
        bx.plot([hm], [y], mec=INK, mew=1.1, ls="none", zorder=4, **mk11)
        bx.text(hm + (0.12 if hm < 0.9 else -0.12), y, "%+.2f" % hm, va="center", ha="left" if hm < 0.9 else "right", fontsize=7.8,
                zorder=5, bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.axvline(bench11, color=INK, lw=0.9, ls="--", zorder=0)
    ax.axvline(bench11sv, color=INK, lw=1.0, ls=":", zorder=0)
    ax.text(bench11 + 0.3, -1.52, "DLPNO-CCSD(T)/def2-TZVPD, %.2f;\nnot the experimental number" % bench11, fontsize=7.0, va="bottom", ha="left")
    ax.text(bench11sv - 0.3, -1.52, "DLPNO-CCSD(T)/def2-SVPD,\n%.2f (D41)" % bench11sv, fontsize=7.0, va="bottom", ha="right")
    ax.set_yticks(range(len(r11))); ax.set_yticklabels([r["functional"] for r in r11]); ax.set_ylim(-1.6, len(r11) - 0.2)
    ax.set_xlim(14.5, 37.0); ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_xlabel("E(TS) − E(R), bare substrate (kcal/mol).  The two numbers: the def2-TZVPD barrier\nminus the def2-TZVPD benchmark | the def2-SVPD barrier minus the def2-SVPD benchmark")
    ax.set_title("Test 2: the barrier against the correlated benchmark")
    ax.plot([], [], marker="o", ms=7, mfc=INK, mec=INK, ls="none", label="def2-TZVPD; comparison pre-registered (D36)")
    ax.plot([], [], marker="o", ms=7, mfc="white", mec=INK, mew=1.1, ls="none", label="def2-TZVPD; comparison post hoc (D37's five)")
    ax.plot([], [], marker="D", ms=6.2, mfc=INK, mec=INK, ls="none", label="def2-TZVPD; fixed by D37 Amendment 1, benchmark known")
    ax.plot([], [], marker="s", ms=5, mfc="#9a9a9a", mec=INK, mew=0.8, ls="none", label="def2-SVPD, the production basis")
    ax.plot([], [], color=INK, lw=0.9, ls="--", label="benchmark at def2-TZVPD (D36)")
    ax.plot([], [], color=INK, lw=1.0, ls=":", label="benchmark at def2-SVPD (D41)")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=7.0, frameon=False, columnspacing=1.6, handlelength=2.2)
    bx.axvline(0.0, color=INK, lw=0.9, zorder=0); bx.axvline(tgt11, color=INK, lw=0.9, ls="--", zorder=0)
    bx.text(0.04, len(r11) - 0.45, "vacuum level", fontsize=7.0, va="top")
    bx.text(tgt11 - 0.04, -1.52, "minus the detachment\nenergy, %.4f eV" % tgt11, fontsize=7.0, va="bottom", ha="right")
    bx.set_xlim(-2.4, 1.9); bx.grid(axis="x", color=GRID, lw=0.6)
    bx.set_xlabel("highest occupied orbital, def2-SVPD, reactant (eV)")
    bx.set_title("Test 1: the orbital against the detachment energy")
    fig.tight_layout(rect=(0, 0.075, 1, 1)); save(fig, "F11_two_tests")

    # ---- F12: DIAGNOSTIC 40's detachment energies.  Black, grey and white.  The reading is the side of zero a marker
    # stands on; the numbers are printed in a column of their own so that no label covers a marker.
    r12 = read_tsv(out / "F12_detachment_energy.tsv")
    pa = [r for r in r12 if r["panel"].startswith("A")]
    pb = [r for r in r12 if r["panel"].startswith("B")]
    names_b = []
    for r in pb:
        if r["row"] not in names_b:
            names_b.append(r["row"])
    fig, (bx, ax) = plt.subplots(2, 1, figsize=(9.4, 7.2), gridspec_kw={"height_ratios": [len(names_b) + 1.3, len(pa) + 0.5]}, sharex=True)
    XL, XR, XV = -2.3, 2.75, 1.55
    for a_ in (ax, bx):
        a_.axvspan(XL, 0, facecolor="#f1f1f1", edgecolor="#c9c9c9", hatch="////", lw=0, zorder=0)
        a_.axvline(0, color=INK, lw=1.0, zorder=2)
        a_.grid(axis="x", color=GRID, lw=0.6, zorder=1); a_.set_axisbelow(True)
        a_.tick_params(axis="y", length=0)
    nb = len(names_b)
    for i, n in enumerate(names_b):
        y = nb - 1 - i
        v = {r["state"]: float(r["VDE_eV"]) for r in pb if r["row"] == n}
        bx.plot([v["R"], v["TS"]], [y, y], color=MUTE, lw=0.8, zorder=3)
        bx.plot([v["R"]], [y], marker="o", ms=7, mfc=INK, mec=INK, mew=1.0, ls="none", zorder=5)
        bx.plot([v["TS"]], [y], marker="o", ms=7, mfc="white", mec=INK, mew=1.1, ls="none", zorder=4)
        bx.text(XV, y, ("R %+.4f    TS %+.4f" % (v["R"], v["TS"])).replace("-", MINUS), va="center", ha="left", fontsize=7.8, color=INK)
    lab_b = []
    for n in names_b:
        q = next(r["quoted_ddE_kcal"] for r in pb if r["row"] == n)
        lab_b.append("bare substrate\nno charges" if n == "bare" else ("%s\nquoted lowering %s kcal/mol" % (n, q)).replace("-0", MINUS + "0").replace("-1", MINUS + "1")
                     .replace("-3", MINUS + "3").replace("-4", MINUS + "4").replace("-5", MINUS + "5"))
    bx.set_yticks([nb - 1 - i for i in range(nb)]); bx.set_yticklabels(lab_b, fontsize=7.6)
    bx.set_ylim(-0.6, nb - 0.5 + 0.95)
    bx.text(XL + 0.05, nb - 0.5 + 0.82, "METASTABLE: at or below zero", fontsize=8.5, style="italic", va="top", ha="left",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    bx.text(0.05, nb - 0.5 + 0.82, "BOUND: above zero", fontsize=8.5, style="italic", va="top", ha="left")
    bx.plot([], [], marker="o", ms=7, mfc=INK, mec=INK, ls="none", label="reactant (R)")
    bx.plot([], [], marker="o", ms=7, mfc="white", mec=INK, mew=1.1, ls="none", label="transition state (TS)")
    bx.legend(loc="upper right", fontsize=7.6, ncol=1, borderaxespad=0.2)
    bx.set_title("Part B. With each arrangement's charges present: CAM-B3LYP-D3BJ, both states", loc="left")
    na = len(pa)
    for i, r in enumerate(pa):
        y = na - 1 - i
        v = float(r["VDE_eV"])
        ax.plot([0, v], [y, y], color=MUTE, lw=0.8, zorder=3)
        ax.plot([v], [y], marker="o", ms=7, mfc=INK, mec=INK, mew=1.0, ls="none", zorder=5)
        ax.text(XV, y, ("R %+.4f" % v).replace("-", MINUS), va="center", ha="left", fontsize=7.8, color=INK)
    ax.set_yticks([na - 1 - i for i in range(na)]); ax.set_yticklabels([r["row"] for r in pa], fontsize=7.8)
    ax.set_ylim(-0.6, na - 0.4)
    ax.set_title("Part A. The bare dianion at the reactant, by functional (monoanion not analysed for stability)", loc="left")
    ax.set_xlim(XL, XR)
    ax.set_xticks([-2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5])
    ax.set_xlabel("detachment energy, E(monoanion) " + MINUS + " E(dianion), def2-SVPD (eV)\nwhere it is negative, the sign is the reading and the size is not")
    fig.tight_layout(); save(fig, "F12_detachment_energy")


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
