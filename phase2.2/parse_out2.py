#!/usr/bin/env python3
"""Status + key results from EVERY loose output, with file-type classification and
imaginary modes counted ONLY after the last OPTIMIZATION RUN DONE (the project's reading rule)."""
import re
from pathlib import Path
ROOTS=[Path("/home/claude/jessreid36/chorismate-thesis-results"),
       Path("/home/claude/jessreid36/chorismate-thesis-code"),
       Path("/home/claude/jessreid36/consolidated_works")]
base=Path("/home/claude/jessreid36")
IMAG=re.compile(r"^\s*\d+:\s+(-\d+\.\d+)\s+cm\*\*-1\s*\*\*\*imaginary mode\*\*\*", re.M)
rows=[]
for root in ROOTS:
    if not root.is_dir(): continue
    for p in sorted(root.rglob("*.out")):
        if "/.git/" in str(p): continue
        try: t=p.read_text(errors="replace")
        except Exception: continue
        head=t[:4000]
        if "O   R   C   A" in head or "ORCA" in head[:800]: kind="orca"
        elif re.match(r"^\s*\d+\s*\n\s*-?\d+\.\d+\s+-?\d+\.\d+\s+-?\d+\.\d+\s+-?\d+\.\d+", t): kind="vpot"
        elif p.name.endswith(".pbs.out") or "PBS" in head.upper(): kind="scheduler"
        else: kind="other"
        norm = "ORCA TERMINATED NORMALLY" in t
        fin=re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)
        nopt=t.count("OPTIMIZATION RUN DONE")
        # imaginary modes in the FINAL frequency block only
        tail = t.rsplit("OPTIMIZATION RUN DONE",1)[-1] if nopt else t
        imag_final = IMAG.findall(tail)
        imag_all   = IMAG.findall(t)
        rows.append([str(p.relative_to(base)), kind, "Y" if norm else "-",
                     str(nopt), (fin[-1] if fin else "-"), str(len(fin)),
                     str(len(imag_final)), ("|".join(imag_final[:4]) or "-"),
                     str(len(imag_all)), str(p.stat().st_size)])
out=Path("/tmp/claude-0/-home-claude/66cfc225-02c6-53c5-b312-80bd215cd9d7/scratchpad/census/all_outputs.tsv")
with open(out,"w") as fh:
    fh.write("path\tkind\tterminated_normally\topt_runs_done\tlast_FSPE\tn_FSPE\tn_imag_final\timag_final\tn_imag_allfile\tbytes\n")
    for r in rows: fh.write("\t".join(r)+"\n")
print("parsed %d outputs" % len(rows))
