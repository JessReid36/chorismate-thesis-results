"""Counts, per folder of phase2.2/cs_stage6, the ORCA inputs (*.inp, at any depth) and how many of
them carry a core potential (the word NewECP, in any case). Run from the top of the results
repository:   python3 phase2.2/cs_stage6/a10/count_walled_inputs.py
For the inputs that carry one it also collects the functional and the basis set of their method lines and
counts those that have a ghost atom (a line that begins with an element symbol and a colon).
It reads committed files only and writes nothing."""
import os, sys
S6 = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "phase2.2", "cs_stage6")
rows = []
bases = {}
ghosts = 0
for d in sorted(os.listdir(S6)):
    p = os.path.join(S6, d)
    if not os.path.isdir(p):
        continue
    n = w = 0
    kinds = set()
    for root, dirs, files in os.walk(p):
        dirs.sort()
        for f in sorted(files):
            if not f.endswith(".inp"):
                continue
            n += 1
            t = open(os.path.join(root, f), errors="replace").read()
            if "newecp" in t.lower():
                w += 1
                for line in t.split("\n"):
                    s = line.split()
                    if s and s[0].endswith(">"):
                        kinds.add(s[0])
                    if s and s[0].startswith("!"):
                        words = line.replace("!", " ").split()
                        key = " ".join(x for x in words if x.upper() in ("B3LYP", "CAM-B3LYP")
                                       or ("def2-" in x.lower() and "/" not in x))
                        bases[key] = bases.get(key, 0) + 1
                if any(l.split() and l.split()[0].endswith(":") and l.split()[0][:-1].isalpha()
                       and len(l.split()[0]) <= 3 for l in t.split("\n")):
                    ghosts += 1
    if n:
        rows.append((d, n, w, " ".join(sorted(kinds))))
print("folder      inputs  with a core potential  centres")
for d, n, w, k in rows:
    print("%-10s  %6d  %6d                 %s" % (d, n, w, k))
late = [r for r in rows if r[0][:1] == "d" and r[0][1:3].isdigit() and int(r[0][1:3]) >= 34]
print("folders d34 to d51: %d inputs, %d with a core potential" % (sum(r[1] for r in late), sum(r[2] for r in late)))
print("all folders: %d inputs, %d with a core potential" % (sum(r[1] for r in rows), sum(r[2] for r in rows)))
print("functional and basis set of the inputs with a core potential:")
for k in sorted(bases):
    print("   %-24s %4d" % (k, bases[k]))
print("inputs with a core potential that also have a ghost atom: %d" % ghosts)
