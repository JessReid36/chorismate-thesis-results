#!/usr/bin/env python3
"""Parse EVERY .inp and .out inside the 134 tarballs and 808 single .xz files,
streaming in memory. Same extraction rules as the loose-file census."""
import re, tarfile, lzma, io
from pathlib import Path
base=Path("/home/claude/jessreid36")
BASES=["def2-TZVPPD","def2-TZVPD","def2-TZVPP","def2-TZVP","def2-SVPD","ma-def2-SVPD","ma-def2-SVP",
       "def2-SVP","6-311++G**","6-311+G(2d,p)","6-31++G**","6-31+G(d)","6-31G(d)",
       "aug-cc-pVTZ","aug-cc-pVDZ","cc-pVTZ","cc-pVDZ","STO-3G"]
FUNCS=["B3LYP","PBE0","PBE","TPSSh","TPSS","M06-2X","wB97X-D3","wB97X","BP86","B97-D3","B97-3c",
       "r2SCAN-3c","PBEh-3c","HF-3c","CAM-B3LYP","BLYP","RI-MP2","MP2","DLPNO-CCSD(T)","CCSD(T)","HF"]
JOBS=["NEB-TS","NEB-CI","NEB","OptTS","Opt","NumFreq","AnFreq","Freq","IRC","EnGrad","MD","Scan","GOAT","SP"]
MISC=["RIJCOSX","def2/J","TightSCF","VeryTightSCF","D3BJ","D4","CPCM","SMD","TightOpt","FOD","Stability","AutoAux"]
IMAG=re.compile(r"^\s*\d+:\s+(-\d+\.\d+)\s+cm\*\*-1\s*\*\*\*imaginary mode\*\*\*", re.M)

def pick(cands, up):
    hit=[c for c in cands if c.upper() in up]
    return [c for c in hit if not any(c.upper() in o.upper() and c!=o for o in hit)]

inp_rows=[]; out_rows=[]
def do_inp(arc, member, t):
    bang=" ".join(l.strip()[1:].strip() for l in t.splitlines() if l.strip().startswith("!"))
    up=bang.upper()
    ecp=sorted(set(re.findall(r"^\s*([A-Z][a-z]?)>\s", t, re.M)))
    eps=re.search(r"epsilon\s+([0-9.]+)", t, re.I)
    cs=re.search(r"coordsys\s+(\w+)", t, re.I)
    ni=re.search(r"NImages\s+(\d+)", t, re.I)
    chg=re.search(r"^\s*\*\s*(?:xyzfile|xyz|pdbfile)\s+(-?\d+)\s+(\d+)", t, re.M|re.I)
    inp_rows.append([arc, member, "+".join(pick(FUNCS,up)) or "-", "+".join(pick(BASES,up)) or "-",
        "+".join(pick(JOBS,up)) or "-", "+".join(pick(MISC,up)) or "-",
        "Y" if "QMMM" in up or "%QMMM" in t.upper() else "-",
        (eps.group(1) if eps else "-"), "+".join(ecp) or "-",
        (cs.group(1) if cs else "-"), (ni.group(1) if ni else "-"),
        (chg.group(1)+"/"+chg.group(2) if chg else "-"), bang[:160] or "-"])

def do_out(arc, member, t):
    fin=re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)
    nopt=t.count("OPTIMIZATION RUN DONE")
    tail=t.rsplit("OPTIMIZATION RUN DONE",1)[-1] if nopt else t
    imf=IMAG.findall(tail)
    out_rows.append([arc, member, "Y" if "ORCA TERMINATED NORMALLY" in t else "-",
        str(nopt), (fin[-1] if fin else "-"), str(len(fin)), str(len(imf)),
        ("|".join(imf[:4]) or "-"), str(len(IMAG.findall(t))),
        "Y" if "THE NEB OPTIMIZATION HAS CONVERGED" in t else "-"])

arcs=[p for p in base.rglob("*.xz") if "/.git/" not in str(p)]
nt=ns=0
for p in arcs:
    rel=str(p.relative_to(base))
    try:
        with tarfile.open(p,"r:xz") as tf:
            nt+=1
            for m in tf.getmembers():
                if not m.isfile(): continue
                if not (m.name.endswith(".inp") or m.name.endswith(".out")): continue
                try: t=tf.extractfile(m).read().decode("utf-8","replace")
                except Exception: continue
                (do_inp if m.name.endswith(".inp") else do_out)(rel, m.name, t)
        continue
    except Exception: pass
    inner=p.name[:-3]
    if not (inner.endswith(".inp") or inner.endswith(".out")): continue
    try:
        with lzma.open(p,"rt",errors="replace") as fh: t=fh.read()
    except Exception: continue
    ns+=1
    (do_inp if inner.endswith(".inp") else do_out)(rel, inner, t)

C=Path("/tmp/claude-0/-home-claude/66cfc225-02c6-53c5-b312-80bd215cd9d7/scratchpad/census")
with open(C/"archived_inputs.tsv","w") as fh:
    fh.write("archive\tmember\tfunctional\tbasis\tjobtype\tmisc\tqmmm\tcpcm_eps\tecp_elements\tcoordsys\tnimages\tchg/mult\tbang\n")
    for r in inp_rows: fh.write("\t".join(x.replace("\t"," ") for x in r)+"\n")
with open(C/"archived_outputs.tsv","w") as fh:
    fh.write("archive\tmember\tterminated_normally\topt_runs_done\tlast_FSPE\tn_FSPE\tn_imag_final\timag_final\tn_imag_allfile\tneb_converged\n")
    for r in out_rows: fh.write("\t".join(x.replace("\t"," ") for x in r)+"\n")
print("tarballs read %d, singles read %d" % (nt,ns))
print("archived inputs parsed : %d" % len(inp_rows))
print("archived outputs parsed: %d" % len(out_rows))
