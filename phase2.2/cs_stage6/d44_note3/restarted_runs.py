"""Which committed ORCA outputs began from orbitals that an earlier attempt had left in the run's folder, and what
the one of them that ended normally shares with a run begun from ORCA's own starting guess.
Run from the top of the results repository:   python3 phase2.2/cs_stage6/d44_note3/restarted_runs.py
It reads committed files only and writes nothing."""
import csv, os, re, sys
S6 = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "phase2.2", "cs_stage6")
outs = []
for root, dirs, files in os.walk(S6):
    dirs.sort()
    if "job.out" in files:
        outs.append(os.path.join(root, "job.out"))
outs.sort()
found, guesses = [], {}
for f in outs:
    t = open(f, errors="replace").read()
    g = re.findall(r"INITIAL GUESS: (.*)", t)
    first = g[0].strip() if g else "(none printed)"
    guesses[first] = guesses.get(first, 0) + 1
    if "The File: job.gbw exists" in t:
        found.append(os.path.relpath(os.path.dirname(f), S6))
print("job.out files under phase2.2/cs_stage6: %d" % len(outs))
print("the first INITIAL GUESS each prints:")
for k in sorted(guesses):
    print("   %-20s %5d" % (k, guesses[k]))
print('outputs that print "The File: job.gbw exists": %d' % len(found))
for r in found:
    print("   " + r)

def text(run):
    return open(os.path.join(S6, "d44", run, "job.out"), errors="replace").read().split("\n")

def first_scf(run):
    """the last iteration energy before the first SCF CONVERGED line, and that line's cycle count"""
    e = None
    for l in text(run):
        m = re.match(r"^\s*\d+\s+(-\d{3}\.\d{6,})", l)
        if m:
            e = m.group(1)
        m = re.search(r"SCF CONVERGED AFTER\s+(\d+) CYCLES", l)
        if m:
            return e, int(m.group(1))
    return None, None

print("")
print("how each of them ended (the last line that says so), in d44/:")
for r in found:
    run = os.path.basename(r)
    ls = text(run)
    end = [l.strip(" *") for l in ls if "ORCA TERMINATED NORMALLY" in l or "SCF NOT CONVERGED AFTER" in l
           or "Stability equations did not converge" in l]
    end = [re.sub(r"^\[file .*?\]: ", "", x) for x in end]
    print("   %-26s %s" % (run, end[-1] if end else "(no such line)"))

print("")
print("the two logs of job RDTZ, the lines of these runs:")
for name in ("run_RDTZ.pbs.out.part1", "run_RDTZ.pbs.out"):
    for l in open(os.path.join(S6, "d44", name), errors="replace").read().split("\n"):
        if any(l.startswith(os.path.basename(r) + " ") for r in found) or "job killed" in l or l.startswith("host="):
            print("   %-23s %s" % (name, l))

print("")
print("the first SCF of each ds run of level RDTZ against the SCF of its di run (same input but for the stability")
print("analysis). Energies in Eh, as printed in the iteration tables; cycles: of the first SCF of the ds run.")
rows = list(csv.DictReader(open(os.path.join(S6, "d44.tsv")), delimiter="\t"))
for x in rows:
    if x["level_key"] != "RDTZ":
        continue
    di, ds = x["di_run"], x["ds_run"]
    ed, nd = first_scf(di)
    es, ns = first_scf(ds)
    g = [l for l in text(ds) if "INITIAL GUESS:" in l]
    gs = g[0].split(":")[1].strip() if g else "?"
    if ed is None or es is None:
        print("   %-26s %-16s not formed" % (ds, gs))
        continue
    print("   %-26s %-16s cycles %3d  ds %s  di %s  ds minus di %+.1e" % (ds, gs, ns, es, ed, float(es) - float(ed)))

print("")
print("d44.tsv, the row of B_n05_q0.50 at RDTZ, R:")
for x in rows:
    if x["level_key"] == "RDTZ" and x["design"] == "B_n05_q0.50" and x["state"] == "R":
        for k in ("di_run", "di_status", "E_di_Eh", "lowdin_rise_e", "dipole_ratio", "ds_run", "ds_status", "E_ds_Eh",
                  "E_ds_minus_E_di_Eh", "ds_stab_first", "ds_stab_last", "ds_S2", "ds_lowdin_rise_e", "ds_dipole_ratio",
                  "search", "flags", "held", "mo_run", "mo_status", "VDE_eV", "word", "four_legs", "fifth_leg", "ddE_kcal",
                  "agreement", "at_this_level", "cross_check"):
            print("   %-22s %s" % (k, x[k]))
print("")
print("formed again here from d44.tsv, without any number of the ds run (B_n05_q0.50 at RDTZ):")
z = {x["state"]: x for x in rows if x["level_key"] == "RDTZ" and x["design"] == "B_n05_q0.50"}
EV, KC = 27.211386245988, 627.5094740631
f = lambda st, k: float(z[st][k])
dde = ((f("TS", "E_di_Eh") - f("TS", "E_control_Eh")) - (f("R", "E_di_Eh") - f("R", "E_control_Eh"))) * KC
print("   ddE from E_di and E_control: %+.4f kcal/mol   (table: %s)" % (dde, z["R"]["ddE_kcal"]))
for st in ("R", "TS"):
    print("   VDE at %-2s from E_mo and E_di: %+.4f eV   (table: %s)" % (st, (f(st, "E_mo_Eh") - f(st, "E_di_Eh")) * EV, z[st]["VDE_eV"]))
print("   flags of the di run at R:  rise %s e (flagged at 0.25), dipole %sx (flagged at 2.0)" % (z["R"]["lowdin_rise_e"], z["R"]["dipole_ratio"]))
print("   flags of the di run at TS: rise %s e, dipole %sx" % (z["TS"]["lowdin_rise_e"], z["TS"]["dipole_ratio"]))
print("")
print("d44.tsv, the monoanion runs among them:")
for x in rows:
    if x["level_key"] == "RDTZ" and os.path.join("d44", x["mo_run"]) in found:
        print("   %-26s mo_status %-13s four_legs %-11s fifth_leg %-26s agreement %-8s at_this_level %s" % (
            x["mo_run"], x["mo_status"], x["four_legs"], x["fifth_leg"], x["agreement"], x["at_this_level"]))
