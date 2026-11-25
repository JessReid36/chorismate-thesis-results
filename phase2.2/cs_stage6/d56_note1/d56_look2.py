"""UNOFFICIAL LOOK at D56: the committed reader's own functions, applied to whatever outputs exist so far.

It reads only. It writes nothing into either repository. It runs none of the reader's gates, so nothing it prints
is a result: the result is what cs6_d56.py prints at H1. usage: d56_look2.py --res R --code C --look T
(T/d56 holds a copy of the committed inputs of d56 with the outputs fetched from hpc1 beside them)."""
import argparse, importlib.util, os, sys

ap = argparse.ArgumentParser()
for a_ in ("res", "code", "look"):
    ap.add_argument("--" + a_, required=True)
a = ap.parse_args()
res, code, look = (os.path.abspath(x) for x in (a.res, a.code, a.look))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


P = os.path.join(code, "phase2.2")
rd = load(os.path.join(P, "cs6_d56.py"), "look_reader")
S6 = os.path.join(res, rd.S)
M = dict((k, load(os.path.join(P, fn), "look_" + k)) for k, fn in (
    ("d40", "cs6_d40.py"), ("d33b", "cs6_d33b.py"), ("audit", "cs6_audit.py"), ("r53", "cs6_d53.py"),
    ("p47", "cs6_d47_prepare.py"), ("p56", "cs6_d56_prepare.py")))
p47, p56 = M["p47"], M["p56"]
_out = sys.stdout
sys.stdout = open(os.devnull, "w")
try:
    F, designs, runs = p56.build(S6, code, designs_from=os.path.join(S6, "d56", "DESIGNS.tsv"))
finally:
    sys.stdout = _out
geom = dict((st, p47.read_geom(os.path.join(S6, p47.GEOM[st]))) for st in ("R", "TS"))
D = os.path.join(look, "d56")
RUN, ended, unended, absent, changed = {}, 0, [], 0, []
for r in runs:
    d = os.path.join(D, r["run"])
    for fn in ("job.inp", "pc.pc"):
        k = "%s/%s" % (r["run"], fn)
        if k in F and (not os.path.isfile(os.path.join(d, fn)) or open(os.path.join(d, fn)).read() != F[k]):
            changed.append(k)
    x = rd.read_run(M, d, r["kind"])
    x.update(r)
    RUN[r["run"]] = x
    po = os.path.join(d, "job.out")
    if not os.path.isfile(po):
        absent += 1
    elif "ORCA TERMINATED NORMALLY" in open(po, errors="replace").read():
        ended += 1
    else:
        unended.append(r["run"])
LV = [lv for lv, _, _, _ in p56.LEVELS]
C = dict(((lv, k, st), RUN["%s_C_%s_%s" % (lv, k, st)]) for lv in LV for k in ("ctl", "bare") for st in ("R", "TS"))
say = lambda t="": print(t)
f4 = lambda v: "--" if v is None else "%+.3f" % v
say("UNOFFICIAL LOOK 2 at D56. These are not results. The result is only what H1 prints.")
say("The committed reader's own functions (cs6_d56.py and the scripts it loads), without its gates.")
say("runs: %d in all; %d ended normally; %d with no output yet; %d with an output that has not ended normally" % (
    len(runs), ended, absent, len(unended)))
if unended:
    say("   not ended normally (running now, or cut short): " + " ".join(unended))
if changed:
    say("   WARNING: %d input file(s) in the look folder are not the committed ones, e.g. %s" % (len(changed), changed[0]))
for lv in LV:
    cs = [C[(lv, "ctl", st)]["status"] for st in ("R", "TS")]
    say("control at %s: %s" % (lv, "measured" if all(s == "measured" for s in cs) else "NOT COMPLETE (%s)" % ", ".join(cs)))
say()
say("four = the four legs (where the electrons sit, dipole, gap, stability). fifth = the last electron stays bound.")
say("ddE = change of the barrier, kcal/mol. rise = largest Loewdin rise on an atom against the control, e (flag at %.2f)." % M["audit"].D_LW)
say("dip = dipole against the control (flag at %.1fx). word = the committed rule applied to what exists so far." % M["audit"].R_DIP)
say()
tally = {}
for d_ in designs:
    charges = list(zip(d_["q"], d_["xyz"]))
    o = {}
    for lv in LV:
        di = dict((st, RUN["%s_%s_di_%s" % (lv, d_["name"], st)]) for st in ("R", "TS"))
        mo = dict((st, RUN["%s_%s_mo_%s" % (lv, d_["name"], st)]) for st in ("R", "TS"))
        ctl = dict((st, C[(lv, "ctl", st)]) for st in ("R", "TS"))
        four, z = rd.four_legs(M, di, ctl, geom, charges)
        fifth, fw = rd.fifth_leg(di, mo)
        o[lv] = dict(four=four, z=z, fifth=fifth, fw=fw, dde=rd.dde_of(di, ctl), di=di, mo=mo)
    agree = rd.agreement(o["TZ"]["dde"], o["SV"]["dde"])
    at_tz = rd.at_level(o["TZ"]["four"], o["TZ"]["fifth"], o["TZ"]["fw"], agree)
    work = "PASSES THE FIVE LEGS" if o["SV"]["four"] == "RELIABLE" and o["SV"]["fifth"] == "PASSED" else (
        "FAILS" if o["SV"]["four"] == "UNRELIABLE" or any(o["SV"]["fw"][st][1] == "METASTABLE" for st in ("R", "TS")) else "OPEN")
    word = "SURVIVOR" if work == "PASSES THE FIVE LEGS" and at_tz == "PASSES" else (
        "NOT A SURVIVOR: FAILS" if "FAILS" in (work, at_tz) else "NOT A SURVIVOR: OPEN")
    missing = [k for k in ("%s_%s_%s_%s" % (lv, d_["name"], c, st) for lv in LV for c in ("di", "mo") for st in ("R", "TS"))
               if RUN[k]["status"] != "measured"]
    if word == "NOT A SURVIVOR: OPEN" and missing:
        word = "NOT YET (runs not finished or not read)"
    tally[word] = tally.get(word, 0) + 1
    say("%s   %s   (TZ against SV: %s)" % (d_["name"], word, agree))
    for lv in LV:
        q = o[lv]
        g = lambda key, fmt: "/".join("--" if q["z"][st].get(key) is None else fmt % q["z"][st][key] for st in ("R", "TS"))
        bd = "/".join("--" if q["fw"][st][0] is None else "%+.2f" % q["fw"][st][0] for st in ("R", "TS"))
        say("   %s ddE %8s | four %-14s rise R/TS %s e, dip %s | fifth %s, bound R/TS %s eV" % (
            lv, f4(q["dde"]), q["four"], g("rise", "%+.3f"), g("ratio", "%.2fx"), q["fifth"], bd))
        for st in ("R", "TS"):
            z = q["z"][st]
            if z["flags"]:
                say("        %s FLAGS: %s" % (st, "; ".join(z["flags"])[:140]))
            if z["held"]:
                say("        %s held: %s" % (st, "; ".join(z["held"])[:140]))
    if missing:
        say("   not measured yet: " + " ".join(missing)[:200])
say()
say("TALLY so far (unofficial): " + "; ".join("%s: %d" % (k, tally[k]) for k in sorted(tally)))
say("LOOK2 read only. Nothing was written into either repository.")
