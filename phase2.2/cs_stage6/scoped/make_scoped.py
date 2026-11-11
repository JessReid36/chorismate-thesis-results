#!/usr/bin/env python3
"""Tables of the scoped report (WRITEUP_SCOPED_20261111.md): what the record holds at each level of theory.

Everything is read from committed files of the results repository; nothing is estimated.
  S1_inputs_by_directory.tsv   every committed *.inp under phase2.2/cs_stage6, by directory and by keyword-line level
  S2_remeasure.tsv             the level-dependent claims measured at another level, with what a like-for-like repeat costs
  derived.tsv                  every number the report states that is not printed in a committed document (rows SVnn)

usage: make_scoped.py --res <results repo> --out <dir>
"""
import argparse, collections, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
S6 = "phase2.2/cs_stage6"
PROD = "CAM-B3LYP-D3BJ/def2-SVPD"
FUNC = ["DLPNO-CCSD(T)", "CCSD(T)", "CAM-B3LYP", "WB97X-D3", "WB97X-V", "WB97X", "B3LYP", "PBE0", "M062X", "RI-MP2", "MP2", "UHF", "RHF", "HF"]
BAS = ["MA-DEF2-SVP", "DEF2-TZVPD", "DEF2-TZVPP", "DEF2-TZVP", "DEF2-SVPD", "DEF2-SVP", "6-31G(D)", "6-31+G(D)", "AUG-CC-PVDZ", "AUG-CC-PVTZ", "CC-PVDZ", "CC-PVTZ"]
SHOW = {"WB97X-D3": "wB97X-D3", "MA-DEF2-SVP": "ma-def2-SVP", "DEF2-TZVPD": "def2-TZVPD", "DEF2-SVPD": "def2-SVPD", "DEF2-SVP": "def2-SVP", "6-31G(D)": "6-31G(d)"}


def stop(msg):
    sys.exit("STOP: " + msg)


def level_of(text):
    kw = " ".join(l.strip()[1:] for l in text.splitlines() if l.strip().startswith("!"))
    toks = [t.upper() for t in kw.split()]
    fn = next((x for x in FUNC if x in toks), None)
    bs = next((x for x in BAS if x in toks), None)
    if fn is None or bs is None:
        return "other keyword line: " + " ".join(kw.split())[:40]
    return "%s/%s" % (fn + "-D3BJ" if ("D3BJ" in toks and fn in ("B3LYP", "CAM-B3LYP")) else SHOW.get(fn, fn), SHOW.get(bs, bs))


def xyz(p):
    ls = Path(p).read_text().split("\n")
    return [(l.split()[0],) + tuple(round(float(x), 5) for x in l.split()[1:4]) for l in ls[2:2 + int(ls[0])]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res, out = Path(a.res).resolve(), Path(a.out)
    root = res / S6
    out.mkdir(parents=True, exist_ok=True)
    tracked = subprocess.run(["git", "-C", str(res), "ls-files", "-z", S6], capture_output=True, text=True, check=True).stdout.split("\0")
    by = collections.defaultdict(collections.Counter)
    for f in tracked:
        if f.endswith(".inp"):
            rel = f[len(S6) + 1:]
            by[rel.split("/")[0] if "/" in rel else "(top level)"][level_of((res / f).read_text(errors="replace"))] += 1
    rows = []
    for top in sorted(by):
        c = by[top]; n = sum(c.values()); p = c.get(PROD, 0)
        rows.append((top, n, p, "throughout" if p == n else ("partly" if p else "other"), "; ".join("%s %d" % kv for kv in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))))
    with open(out / "S1_inputs_by_directory.tsv", "w") as fh:
        fh.write("# S1. Every committed *.inp under %s (git ls-files), by top-level directory and by the level on its keyword lines.\n" % S6)
        fh.write("# Production level, as the convention in use since D30 has it: %s. class: throughout, partly or other.\n" % PROD)
        fh.write("# Inputs held only inside archives are not seen by this sweep; frozen/ holds its outputs in an archive and no loose input.\n")
        fh.write("directory\tinputs\tat_production_level\tclass\tlevels\n")
        for r in rows:
            fh.write("%s\t%d\t%d\t%s\t%s\n" % r)
    n_at = lambda d, lv: by[d].get(lv, 0)
    DV = []
    add = lambda i, v, kind, what, src: DV.append((i, str(v), kind, what, src))
    S1 = "scoped/S1_inputs_by_directory.tsv"
    add("SV01", len(rows), "count", "directories under %s that hold at least one committed *.inp" % S6, S1)
    add("SV02", sum(r[3] == "throughout" for r in rows), "count", "of those, directories at the production level throughout", S1)
    add("SV03", sum(r[3] == "partly" for r in rows), "count", "directories partly at the production level", S1)
    add("SV04", sum(r[3] == "other" for r in rows), "count", "directories with no input at the production level", S1)
    tot, atp = sum(r[1] for r in rows), sum(r[2] for r in rows)
    add("SV05", tot, "count", "committed *.inp under %s" % S6, S1)
    add("SV06", atp, "count", "of those, inputs at the production level", S1)
    add("SV07", "%.1f" % (100.0 * atp / tot), "derived", "inputs at the production level as a percentage of all: 100 x %d / %d" % (atp, tot), S1)
    B, MA, SVP, SVPD = "B3LYP-D3BJ/", "B3LYP-D3BJ/ma-def2-SVP", "B3LYP-D3BJ/def2-SVP", "B3LYP-D3BJ/def2-SVPD"
    for i, d, lv in (("SV10", "standoff", MA), ("SV11", "standoff", SVP), ("SV12", "qscale", MA), ("SV13", "sitescan", MA), ("SV14", "sitescan", SVP),
                     ("SV15", "pauli", SVP), ("SV16", "pauli", SVPD), ("SV17", "additivity", SVPD), ("SV18", "additivity", SVP), ("SV19", "d16", SVPD),
                     ("SV20", "d17", SVPD), ("SV21", "d23", SVPD), ("SV22", "relax", SVP), ("SV23", "a_matrix", SVP), ("SV24", "d33a", PROD),
                     ("SV25", "d31", PROD), ("SV26", "d32", PROD), ("SV27", "d33b", PROD), ("SV28", "d34", PROD), ("SV29", "d28", PROD), ("SV30", "d30", PROD)):
        add(i, n_at(d, lv), "count", "committed inputs under %s/%s at %s" % (S6, d, lv), S1)
    add("SV31", sum(by["d28"].values()), "count", "committed inputs under %s/d28, all levels" % S6, S1)
    add("SV32", sum(by["d30"].values()), "count", "committed inputs under %s/d30, all levels" % S6, S1)
    add("SV33", n_at("additivity", SVPD) + n_at("d16", SVPD) + n_at("d17", SVPD), "derived", "additivity, d16 and d17 at %s: %d + %d + %d" % (SVPD, n_at("additivity", SVPD), n_at("d16", SVPD), n_at("d17", SVPD)), S1)
    # the frame: every substrate.xyz of three directories against frame 42436's stationary points
    ref = {s: xyz(root / "d33a" / ("sp_42436_%s" % s) / "substrate.xyz") for s in ("R", "TS")}
    k, bad = 40, 0
    for d in ("standoff", "qscale", "sitescan"):
        n = 0
        for p in sorted((root / d).rglob("substrate.xyz")):
            g = xyz(p); n += 1
            bad += 0 if g in (ref["R"], ref["TS"]) else 1
        add("SV%d" % k, n, "count", "substrate.xyz files under %s/%s compared, atom for atom at five decimals, with d33a/sp_42436_{R,TS}/substrate.xyz" % (S6, d), "%s/%s" % (S6, d)); k += 1
    add("SV43", bad, "count", "of those, files matching neither frame 42436's reactant nor its transition state", S6 + "/d33a")
    am = sorted(p for p in root.glob("STAGE6_AMENDMENT*.txt"))
    add("SV50", len(am), "count", "Stage 6 amendments committed (STAGE6_AMENDMENT*.txt)", S6)
    add("SV51", sum(len(re.findall("CAM-B3LYP", p.read_text(errors="replace"), re.I)) for p in am + [root / "STAGE6_CRITERIA.txt"]), "count",
        "occurrences of the string CAM-B3LYP in those amendments and in STAGE6_CRITERIA.txt", S6)
    # D34 at three readings, from the first report's committed table (itself recomputed from raw outputs; the checker recomputes it again)
    t3 = [l.split("\t") for l in (root / "figures" / "T3_d34_arms.tsv").read_text().splitlines() if l.strip() and not l.startswith("#")]
    h, t3 = t3[0], [dict(zip(t3[0], r)) for r in t3[1:]]
    mx = lambda a_, b_: max(max(float(r[a_]), float(r[b_])) for r in t3)
    T3 = "figures/T3_d34_arms.tsv"
    add("SV60", sum(1 for r in t3 if max(float(r["a1_rise_R"]), float(r["a1_rise_TS"])) >= 0.25), "count", "D34 arrangements whose arm 1 Loewdin rise reaches 0.25 e in either state", T3)
    add("SV61", sum(1 for r in t3 if max(float(r["A_rise_R"]), float(r["A_rise_TS"])) >= 0.25), "count", "D34 arrangements whose rise at B3LYP-D3BJ/def2-SVP reaches 0.25 e in either state", T3)
    add("SV62", "%.4f" % mx("a1_rise_R", "a1_rise_TS"), "recomputed from raw outputs", "largest arm 1 Loewdin rise, e", T3)
    add("SV63", "%.4f" % mx("A_rise_R", "A_rise_TS"), "recomputed from raw outputs", "largest Loewdin rise at B3LYP-D3BJ/def2-SVP, e", T3)
    add("SV64", "%.4f" % mx("a2_rise_R", "a2_rise_TS"), "recomputed from raw outputs", "largest arm 2 Loewdin rise, e", T3)
    add("SV65", sum(1 for r in t3 if r["a2_verdict"] == "UNRELIABLE"), "count", "D34 arrangements UNRELIABLE in arm 2", T3)
    add("SV66", sum(1 for r in t3 if r["a2_verdict"] == "RELIABLE"), "count", "D34 arrangements RELIABLE in arm 2", T3)
    add("SV67", sum(1 for r in t3 if (max(float(r["a1_rise_R"]), float(r["a1_rise_TS"])) >= 0.25) != (max(float(r["a2_rise_R"]), float(r["a2_rise_TS"])) >= 0.25)), "count",
        "D34 arrangements on which arm 1 and arm 2 differ about the Loewdin threshold", T3)
    add("SV68", len(t3), "count", "D34 production arrangements", T3)
    for i, d in (("SV70", "d35"), ("SV72", "d36")):
        add(i, len(list((root / d).rglob("job.inp"))), "count", "committed job.inp files under %s/%s" % (S6, d), "%s/%s" % (S6, d))
        add("SV%d" % (int(i[2:]) + 1), len(list((root / d).rglob("job.out"))) + len(list((root / d).rglob("job.out.xz"))), "count", "committed job.out files under %s/%s" % (S6, d), "%s/%s" % (S6, d))
    # S2: the level-dependent claims measured elsewhere, in the order of what each gates
    REM = [("r_safe = 3.50 A", "D11", "standoff", MA, "which grid sites are admissible, and so the choice between routes (a) and (b)"),
           ("which descriptor predicts the artefact; whether moving the grid outward helps", "D12", "sitescan", MA, "route (a), and any screen applied before a design is run"),
           ("how the artefact grows with the size of the charge (verdict PARTIAL)", "D13", "qscale", MA, "any cap on the size of a single charge"),
           ("whether a designed charge needs Pauli repulsion", "D3", "pauli", SVP + " and " + SVPD, "the Lennard-Jones sphere as the representation of a charge"),
           ("whether the artefact is additive over charges", "D14, D16, D17", "additivity, d16, d17", SVPD, "any per-site screen or budget built from single-charge runs"),
           ("how the wall's effect depends on its species", "D23", "d23", SVPD, "the species of wall used by route (b)"),
           ("the relaxed half of the Stage 6 designs", "Stage 6 criteria", "relax", SVP, "Stage 6's own purpose, the relaxation")]
    with open(out / "S2_remeasure.tsv", "w") as fh:
        fh.write("# S2. Level-dependent claims of the record that were measured at a level other than %s.\n" % PROD)
        fh.write("# like_for_like_runs: the committed inputs of those directories at the level named, counted in S1; a repeat at the production level\n")
        fh.write("# with the same design costs that many single points. Ordered by what each claim gates.\n")
        fh.write("order\tclaim\tmeasured_by\tdirectories\tlevel_measured_at\tlike_for_like_runs\tgates\n")
        for i, (claim, who, dirs, lv, gates) in enumerate(REM, 1):
            n = sum(n_at(d.strip(), x.strip()) for d in dirs.split(",") for x in lv.split(" and "))
            fh.write("%d\t%s\t%s\t%s\t%s\t%d\t%s\n" % (i, claim, who, dirs, lv, n, gates))
    with open(out / "derived.tsv", "w") as fh:
        fh.write("# Every number the scoped report states that is not printed in a committed document. Produced by scoped/make_scoped.py.\n")
        fh.write("id\tvalue\tkind\twhat\tsource\n")
        for r in DV:
            fh.write("\t".join(r) + "\n")
    print("scoped tables written: %d directories, %d inputs, %d at the production level; %d derived rows" % (len(rows), tot, atp, len(DV)))


if __name__ == "__main__":
    main()
