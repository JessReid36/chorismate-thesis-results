#!/usr/bin/env python3
"""Parse EVERY ORCA input in the repos. Complete, not sampled. Emits one TSV row per input."""
import re, sys, os
from pathlib import Path

ROOTS = [Path("/home/claude/jessreid36/chorismate-thesis-results"),
         Path("/home/claude/jessreid36/chorismate-thesis-code"),
         Path("/home/claude/jessreid36/consolidated_works")]

BASES = ["def2-TZVPPD","def2-TZVPD","def2-TZVPP","def2-TZVP","def2-SVPD","ma-def2-SVPD","ma-def2-SVP",
         "def2-SVP","def2-QZVPP","6-311++G**","6-311+G(2d,p)","6-31++G**","6-31+G(d)","6-31G(d)",
         "aug-cc-pVTZ","aug-cc-pVDZ","cc-pVTZ","cc-pVDZ","STO-3G","def2-mTZVPP"]
FUNCS = ["B3LYP","PBE0","PBE","TPSSh","TPSS","M06-2X","M062X","wB97X-D3","wB97X-V","wB97X","BP86",
         "B97-D3","B97-3c","r2SCAN-3c","PBEh-3c","HF-3c","CAM-B3LYP","revPBE","BLYP","MP2","RI-MP2",
         "DLPNO-CCSD(T)","CCSD(T)","XTB","GFN2-XTB","HF"]
JOBS = ["NEB-TS","NEB-CI","NEB","OptTS","Opt","Freq","NumFreq","AnFreq","IRC","SP","EnGrad","MD","Scan","GOAT"]
MISC = ["RIJCOSX","RIJDX","RI-JK","def2/J","def2/JK","TightSCF","VeryTightSCF","NormalSCF","SloppySCF",
         "D3BJ","D3ZERO","D4","CPCM","SMD","TightOpt","LooseOpt","Grid","DefGrid2","DefGrid3",
         "NumGrad","AutoAux","FOD","UKS","UHF","NoFrozenCore","FrozenCore","KDIIS","SOSCF","Stability"]

def classify(p):
    s = str(p)
    for k in ("/.git/",): 
        if k in s: return None
    return s

rows=[]
for root in ROOTS:
    if not root.is_dir(): continue
    for p in root.rglob("*.inp"):
        if "/.git/" in str(p): continue
        try: t = p.read_text(errors="replace")
        except Exception: continue
        bang = " ".join(l.strip()[1:].strip() for l in t.splitlines() if l.strip().startswith("!"))
        up = bang.upper()
        basis = [b for b in BASES if b.upper() in up]
        # longest-match only (def2-SVP inside def2-SVPD)
        basis = [b for b in basis if not any(b.upper() in o.upper() and b!=o for o in basis)]
        func  = [f for f in FUNCS if re.search(r"(?<![A-Z0-9-])"+re.escape(f.upper())+r"(?![A-Z0-9])", up)]
        func  = [f for f in func if not any(f.upper() in o.upper() and f!=o for o in func)]
        job   = [j for j in JOBS if re.search(r"(?<![A-Z0-9-])"+re.escape(j.upper())+r"(?![A-Z0-9-])", up)]
        job   = [j for j in job if not any(j.upper() in o.upper() and j!=o for o in job)]
        misc  = [m for m in MISC if m.upper() in up]
        misc  = [m for m in misc if not any(m.upper() in o.upper() and m!=o for o in misc)]
        # blocks
        has_qmmm   = "QMMM" in up or "%QMMM" in t.upper()
        pc = re.search(r"(?:PointCharges|Pointcharges)\s+\"?([^\"\n]+)", t, re.I)
        eps = re.search(r"epsilon\s+([0-9.]+)", t, re.I)
        cpcm_kd = "KEEPDENS" in t.upper()
        newecp = len(re.findall(r"NewECP", t, re.I))
        ecp_el = sorted(set(re.findall(r"^\s*([A-Z][a-z]?)>\s", t, re.M)))
        coordsys = re.search(r"coordsys\s+(\w+)", t, re.I)
        projtr = re.search(r"ProjectTR\s+(\w+)", t, re.I)
        nimages = re.search(r"NImages\s+(\d+)", t, re.I)
        chg = re.search(r"^\s*\*\s*(?:xyzfile|xyz)\s+(-?\d+)\s+(\d+)", t, re.M|re.I)
        geom = re.search(r"^\s*\*\s*xyzfile\s+-?\d+\s+\d+\s+(\S+)", t, re.M|re.I)
        nprocs = re.search(r"nprocs\s+(\d+)", t, re.I)
        rows.append([
            str(p.relative_to(p.parts[0] and Path("/home/claude/jessreid36"))),
            "+".join(func) or "-", "+".join(basis) or "-", "+".join(job) or "-",
            "+".join(misc) or "-",
            "Y" if has_qmmm else "-",
            (pc.group(1).strip() if pc else "-"),
            (eps.group(1) if eps else "-"),
            "Y" if cpcm_kd else "-",
            str(newecp), "+".join(ecp_el) or "-",
            (coordsys.group(1) if coordsys else "-"),
            (projtr.group(1) if projtr else "-"),
            (nimages.group(1) if nimages else "-"),
            (chg.group(1)+"/"+chg.group(2) if chg else "-"),
            (geom.group(1) if geom else "-"),
            (nprocs.group(1) if nprocs else "-"),
            bang[:200] or "-",
        ])

hdr=["path","functional","basis","jobtype","misc","qmmm","pointcharges","cpcm_eps","keepdens",
     "n_newecp","ecp_elements","coordsys","projecttr","nimages","chg/mult","geomfile","nprocs","bang_line"]
out=Path("/tmp/claude-0/-home-claude/66cfc225-02c6-53c5-b312-80bd215cd9d7/scratchpad/census/all_inputs.tsv")
with open(out,"w") as fh:
    fh.write("\t".join(hdr)+"\n")
    for r in rows: fh.write("\t".join(str(x).replace("\t"," ") for x in r)+"\n")
print("parsed %d inputs -> %s" % (len(rows), out))
