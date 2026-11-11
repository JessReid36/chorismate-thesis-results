#!/usr/bin/env python3
"""Completeness pass 1 (by file) for WRITEUP_CONSOLIDATED_20261110.md.

    python3 sweep_pass1.py --res <results repo> --code <code repo> --out <this directory>

Enumerates EVERY committed *.inp and *.out in both repositories - loose, .xz-compressed, or a member of a
committed tar archive - and extracts the ORCA keyword line(s) from each input AND from the INPUT FILE echo
of each output.  A method or basis counts as RUN only if it stands on such a keyword line; a name that
merely occurs somewhere in an output (ORCA's credits banner names dozens) does not.

Writes, byte-reproducibly:
  T1_levels_of_theory.tsv   one row per (method, basis, dispersion, solvation, embedding, job type, special)
  T1b_keyword_tokens.tsv    every token that occurs on any keyword line, with how many files carry it
  T1c_levels_summary.tsv    the same collapsed to (method, basis), which is the table the write-up prints
  T1d_file_census.tsv       how many inputs and outputs were found, by container, program and termination
  T1e_totals.tsv            the four totals the write-up quotes
"""
import hashlib
import io
import lzma
import os
import re
import subprocess
import sys
import tarfile

ECHO = re.compile(r"^\|\s*\d+>\s?(.*)$")


def classify_software(text, kind):
    head = text[:200000]
    if "O   R   C   A" in head or "* O   R   C   A *" in head:
        return "ORCA"
    if kind == "out":
        if "Amber" in head and ("sander" in head.lower() or "pmemd" in head.lower()):
            return "AMBER"
        if "x T B" in head or "xtb version" in head.lower():
            return "xtb"
        if "Psi4" in head or "PSI4" in head:
            return "Psi4"
        if "Entering Gaussian System" in head:
            return "Gaussian"
        if "ASH" in head and "QM/MM" in head:
            return "ASH"
        return "unknown"
    # inputs
    if re.search(r"^\s*!", text, re.M) or re.search(r"^\s*\*\s*(xyz|xyzfile|int|pdbfile)", text, re.M | re.I):
        return "ORCA"
    if "&cntrl" in text or "&qmmm" in text:
        return "AMBER"
    if "$coord" in text or "$chrg" in text:
        return "xtb"
    return "unknown"


def orca_input_lines(text, kind):
    """Return the list of input lines: the file itself for an input, the
    INPUT FILE echo for an output."""
    if kind == "inp":
        return text.splitlines()
    lines = []
    inside = False
    for ln in text.splitlines():
        if not inside:
            if "INPUT FILE" in ln:
                inside = True
            continue
        if "****END OF INPUT****" in ln:
            break
        m = ECHO.match(ln)
        if m:
            lines.append(m.group(1))
    return lines


def summarise(lines):
    bang = []
    blocks = []
    flags = set()
    cur_block = None
    keep = {'scf': [], 'cpcm': [], 'basis': [], 'method': [], 'mp2': [], 'geom': []}
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        s_nocomment = s.split("#", 1)[0].strip()
        if s_nocomment.startswith("!"):
            bang.append(s_nocomment[1:].strip())
            continue
        m = re.match(r"^%\s*(\w+)", s_nocomment)
        if m:
            cur_block = m.group(1).lower()
            blocks.append(cur_block)
            rest = s_nocomment[m.end():].strip()
            if cur_block in keep and rest:
                keep[cur_block].append(' '.join(rest.split()))
            if cur_block == 'pointcharges':
                flags.add('pointcharges-file')
            if re.search(r'\bend\s*$', rest, re.I) and cur_block not in ('geom',):
                cur_block = None
            # one-line block payloads worth keeping
            if cur_block in ("pointcharges", "maxcore"):
                pass
            continue
        low = s_nocomment.lower()
        if low == 'end':
            cur_block = None
            continue
        if cur_block in keep and low != 'end':
            keep[cur_block].append(' '.join(s_nocomment.split()))
        if cur_block == "basis" or cur_block is None:
            if low.startswith("newecp") or "newecp" in low:
                flags.add("NewECP")
            if low.startswith("newgto") or "newgto" in low:
                flags.add("NewGTO")
            if low.startswith("newauxgto") or "newauxjgto" in low:
                flags.add("NewAuxGTO")
            if low.startswith("ecp"):
                flags.add("ECP{" + " ".join(s_nocomment.split()[1:3]) + "}")
        if cur_block == "scf":
            if "stabperform" in low:
                flags.add("StabPerform=" + low.split()[-1])
            if low.startswith("shift") or "levelshift" in low:
                flags.add("LevelShift")
            if "stabrestartuhfifunstable" in low:
                flags.add("StabRestart=" + low.split()[-1])
            if low.startswith("guess"):
                flags.add("Guess=" + low.split()[-1])
            if "moinp" in low:
                flags.add("MOInp")
        if cur_block == "cpcm":
            if low.startswith("epsilon"):
                flags.add("eps=" + low.split()[-1])
            if "smd" in low:
                flags.add("SMD")
        if cur_block == "method":
            if "functional" in low or "exchange" in low or "correlation" in low or "acm" in low or "rangesep" in low:
                flags.add("method:" + " ".join(low.split()))
        if cur_block == "pointcharges":
            flags.add("pointcharges-file")
        # coordinate-line markers
        if re.match(r"^\*\s*(xyz|xyzfile|int|pdbfile)", low):
            flags.add("coords:" + " ".join(low.split()[1:4]))
        # embedded point charges and ghost / ECP-only centres in the geometry
        toks = s_nocomment.split()
        if toks and toks[0].upper() == "Q" and len(toks) >= 5:
            flags.add("inlineQ")
        if toks and toks[0].endswith(">") and len(toks) >= 5:
            flags.add("ECPcentre:" + toks[0])
        if toks and toks[0].endswith(":") and len(toks) >= 4:
            flags.add("ghost:" + toks[0])
    for k, v in keep.items():
        if v:
            if k == 'geom':
                v = [x for x in v if not re.match(r'^\{', x)][:6]
            flags.add('blk[' + k + ']=' + ' / '.join(v)[:400])
    return bang, sorted(set(blocks)), sorted(flags)


def handle(path, container, kind, raw, out):
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = ""
    sw = classify_software(text, kind)
    term = "-"
    if kind == "out" and sw == "ORCA":
        if "ORCA TERMINATED NORMALLY" in text:
            term = "normal"
        elif "ORCA finished by error termination" in text or "aborting the run" in text.lower():
            term = "error"
        else:
            term = "incomplete"
    bang, blocks, flags = ([], [], [])
    if sw == "ORCA":
        bang, blocks, flags = summarise(orca_input_lines(text, kind))
    kw = " || ".join(bang)
    out.write("\t".join([path, container, kind, sw, term, str(len(bang)), kw,
                         ",".join(blocks), ";".join(flags), hashlib.sha256(raw).hexdigest()]) + "\n")


def kind_of(name):
    base = name
    if base.endswith(".xz"):
        base = base[:-3]
    if base.endswith(".inp"):
        return "inp"
    if base.endswith(".out"):
        return "out"
    return None


METHODS = ["CAM-B3LYP", "B3LYP", "WB97X-D3", "MP2", "R2SCAN-3C", "HF-3C", "B97-3C", "XTB2", "HF"]
BASES_ = ["DEF2-SVPD", "MA-DEF2-SVP", "DEF2-TZVPD", "DEF2-SVP", "6-31G(D)"]
JOBS = ["NEB-TS", "NEB-CI", "OPTTS", "L-OPT", "OPT", "NUMFREQ", "FREQ", "IRC", "ENGRAD", "MD"]
PRETTY_ = {"WB97X-D3": "wB97X-D3", "R2SCAN-3C": "r2SCAN-3c", "HF-3C": "HF-3c", "B97-3C": "B97-3c", "XTB2": "XTB2 (GFN2-xTB)",
           "DEF2-SVPD": "def2-SVPD", "MA-DEF2-SVP": "ma-def2-SVP", "DEF2-TZVPD": "def2-TZVPD", "DEF2-SVP": "def2-SVP",
           "6-31G(D)": "6-31G(d)"}


def area(path, cont):
    p = path if cont in ("-", "xz") else cont
    parts = p.split("/")
    if parts[0] == "phase2.2":
        if len(parts) > 2 and parts[1] == "cs_stage6":
            return "phase2.2/cs_stage6/" + parts[2]
        return "phase2.2/" + parts[1]
    return "/".join(parts[:2])


def phase(a):
    if a.startswith("phase2.2/cs_stage6"):
        return "cs_stage6"
    if a.startswith("phase2.2/cs_stage"):
        return a.split("/")[1]
    if a.startswith("phase2.2/"):
        return "phase 2.2 before the stages"
    if a.startswith("phase2b"):
        return "phase 2b"
    if a.startswith("phase2_"):
        return "phase 2"
    return "phase 1 and admin"


def parse(kw, flags):
    toks = [t.upper() for t in kw.replace("||", " ").split()]
    meth = [m for m in METHODS if m in toks]
    basis = [b for b in BASES_ if b in toks]
    job = [j for j in JOBS if j in toks]
    disp = "D3BJ" if "D3BJ" in toks else ("in functional" if "WB97X-D3" in toks else "-")
    emb = []
    if "QMMM" in toks:
        emb.append("QM/MM")
    if "MM" in toks:
        emb.append("MM only")
    if "pointcharges-file" in flags:
        emb.append("point-charge file")
    solv = "-"
    if "CPCM" in toks:
        m = re.search(r"blk\[cpcm\]=epsilon ([0-9.]+)", flags)
        solv = "CPCM eps %s" % (m.group(1) if m else "?")
    ecp = sorted(set(re.findall(r"ECPcentre:(\w+)>", flags)))
    special = []
    if ecp:
        special.append("ECP centres " + "+".join(ecp))
    if "StabPerform=true" in flags or "STABPerform true" in flags:
        special.append("stability analysis")
    if "FOD" in toks:
        special.append("FOD")
    m = "+".join(PRETTY_.get(x, x) for x in meth) or ("(none: !FOD default)" if "FOD" in toks else ("(none: MM only)" if "MM" in toks else "(none)"))
    return (m, "+".join(PRETTY_.get(x, x) for x in basis) or "-", disp, solv, "+".join(emb) or "-",
            "+".join(job) or "SP", ", ".join(special) or "-")


def main():
    import argparse, collections, io as _io
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for repo, tag in ((a.res, "results"), (a.code, "code")):
        files = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
        buf = _io.StringIO()
        for f in sorted(x for x in files if x):
            full = os.path.join(repo, f)
            if re.search(r"\.tar(\.xz|\.gz)?$|\.tgz$", f):
                with tarfile.open(full, "r:*") as tf:
                    for m in tf:
                        if not m.isfile():
                            continue
                        k = kind_of(m.name)
                        if not k:
                            continue
                        data = tf.extractfile(m).read()
                        if m.name.endswith(".xz"):
                            data = lzma.decompress(data)
                        handle(m.name, f, k, data, buf)
                continue
            k = kind_of(f)
            if not k:
                continue
            with open(full, "rb") as fh:
                data = fh.read()
            cont = "-"
            if f.endswith(".xz"):
                data = lzma.decompress(data)
                cont = "xz"
            handle(f, cont, k, data, buf)
        for line in buf.getvalue().splitlines():
            p = line.split("\t")
            rows.append(dict(repo=tag, path=p[0], cont=p[1], kind=p[2], sw=p[3], term=p[4], nbang=int(p[5]), kw=p[6],
                             blocks=p[7], flags=p[8], sha=p[9]))
    out = a.out
    # ---- the file census
    cen = collections.Counter()
    for r in rows:
        c = r["cont"] if r["cont"] in ("-", "xz") else "tar member"
        cen[(r["repo"], {"-": "loose", "xz": "single .xz", "tar member": "tar member"}[c], r["kind"], r["sw"], r["term"])] += 1
    with open(os.path.join(out, "T1d_file_census.tsv"), "w", newline="\n") as f:
        f.write("# Every committed *.inp / *.out found by sweep_pass1.py, by repository, container, kind, program and termination.\n")
        f.write("# 'unknown' outputs are PBS job logs, orca_vpot potential files and sqm outputs; they carry no ORCA banner.\n")
        f.write("repo\tcontainer\tkind\tprogram\ttermination\tn_files\n")
        for key in sorted(cen):
            f.write("\t".join(key) + "\t%d\n" % cen[key])
    # ---- the token census
    tin, tout = collections.Counter(), collections.Counter()
    for r in rows:
        if r["sw"] != "ORCA" or not r["nbang"]:
            continue
        for t in sorted(set(x.upper() for x in r["kw"].replace("||", " ").split())):
            (tin if r["kind"] == "inp" else tout)[t] += 1
    with open(os.path.join(out, "T1b_keyword_tokens.tsv"), "w", newline="\n") as f:
        f.write("# Every token on any ORCA keyword line ('!' line) of any committed input or of the INPUT FILE echo of any committed output,\n")
        f.write("# upper-cased, with the number of files carrying it. A method or basis absent from this file was never asked for by any input.\n")
        f.write("token\tn_input_files\tn_output_echoes\n")
        for t in sorted(set(tin) | set(tout)):
            f.write("%s\t%d\t%d\n" % (t, tin[t], tout[t]))
    # ---- the level table
    agg = collections.defaultdict(lambda: dict(inp_paths=0, inp=set(), ok=set(), bad=set(), areas=collections.Counter()))
    for r in rows:
        if r["sw"] != "ORCA" or not r["nbang"]:
            continue
        key = parse(r["kw"], r["flags"])
        g = agg[key]
        if r["kind"] == "inp":
            g["inp_paths"] += 1
            g["inp"].add(r["sha"])
        elif r["term"] == "normal":
            g["ok"].add(r["sha"])
        else:
            g["bad"].add(r["sha"])
        g["areas"][area(r["path"], r["cont"])] += 1
    with open(os.path.join(out, "T1_levels_of_theory.tsv"), "w", newline="\n") as f:
        f.write("# Pass 1. One row per distinct (method, basis, dispersion, solvation, embedding, job type, special) found on a keyword line.\n")
        f.write("# n_input_files counts input files by path (loose and archived copies both count); the 'unique' columns count distinct file contents (sha256),\n")
        f.write("# so an output committed both loose and inside an archive counts once. A run = one unique normally-terminated output.\n")
        f.write("method\tbasis\tdispersion\tsolvation\tembedding\tjob_type\tspecial\tn_input_files\tn_inputs_unique\tn_outputs_normal_unique\tn_outputs_not_normal_unique\tareas\n")
        for key in sorted(agg, key=lambda k: (-len(agg[k]["ok"]), k)):
            g = agg[key]
            f.write("\t".join(key) + "\t%d\t%d\t%d\t%d\t%s\n" % (g["inp_paths"], len(g["inp"]), len(g["ok"]), len(g["bad"]),
                    "; ".join("%s(%d)" % kv for kv in sorted(g["areas"].items(), key=lambda kv: (-kv[1], kv[0])))))
    summ = collections.defaultdict(lambda: dict(ok=set(), bad=set(), inp=0, jobs=set(), ph=collections.Counter(), solv=set(), spec=set()))
    for key, g in agg.items():
        s = summ[(key[0], key[1])]
        s["ok"] |= g["ok"]; s["bad"] |= g["bad"]; s["inp"] += g["inp_paths"]; s["jobs"].add(key[5])
        if key[3] != "-":
            s["solv"].add(key[3])
        for x in key[6].split(", "):
            if x != "-":
                s["spec"].add(x)
        for ar, n in g["areas"].items():
            s["ph"][phase(ar)] += n
    with open(os.path.join(out, "T1c_levels_summary.tsv"), "w", newline="\n") as f:
        f.write("# Pass 1, collapsed to (method, basis). runs = unique normally-terminated outputs; not_normal = unique outputs that did not\n")
        f.write("# terminate normally (not evidence); input_files = input files by path. where: which part of the record carries them.\n")
        f.write("method\tbasis\truns\tnot_normal\tinput_files\tjob_types\tsolvation\tspecial\twhere\n")
        for key in sorted(summ, key=lambda k: (-len(summ[k]["ok"]), k)):
            s = summ[key]
            f.write("%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\n" % (key[0], key[1], len(s["ok"]), len(s["bad"]), s["inp"],
                    ", ".join(sorted(s["jobs"])), ", ".join(sorted(s["solv"])) or "-", "; ".join(sorted(s["spec"])) or "-",
                    "; ".join("%s" % k for k, _ in sorted(s["ph"].items(), key=lambda kv: (-kv[1], kv[0])))))
    n_orca = sum(1 for r in rows if r["sw"] == "ORCA")
    with open(os.path.join(out, "T1e_totals.tsv"), "w", newline="\n") as f:
        f.write("# Pass 1 totals.\n")
        f.write("quantity\tvalue\n")
        f.write("input and output files found (loose, .xz and tar members, both repositories)\t%d\n" % len(rows))
        f.write("of which ORCA inputs or ORCA outputs\t%d\n" % n_orca)
        f.write("distinct (method, basis, dispersion, solvation, embedding, job type, special) combinations\t%d\n" % len(agg))
        f.write("distinct (method, basis) pairs\t%d\n" % len(summ))
    print("files: %d (ORCA %d); distinct levels: %d; (method, basis) pairs: %d" % (len(rows), n_orca, len(agg), len(summ)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
