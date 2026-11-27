#!/usr/bin/env python3
"""Independent check of D60's committed result (results 173668c6), with my own parsing: it does not import or call
cs6_d60.py, cs6_d56_prepare.py or cs_opt_milp.py. The searches themselves (MILP) and the random draws are not re-run.
usage: indep_check_d60.py <results repo>"""
import csv, re, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

S6 = Path(sys.argv[1]) / "phase2.2/cs_stage6"
H = 627.5094740631          # kcal/mol per Eh (CODATA 2018)
res = (S6 / "STAGE6_DIAGNOSTIC60_RESULT_20261126.txt").read_text()
ok = bad = 0
def chk(label, cond, extra=""):
    global ok, bad
    ok += bool(cond); bad += not cond
    print(("PASS " if cond else "FAIL ") + label + (("  " + extra) if extra else ""))

def final_E(p):
    v = re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", Path(p).read_text())
    return float(v[-1]) if v else None
def vpot(p):
    L = Path(p).read_text().split("\n")
    n = int(L[0].split()[0])
    return np.array([float(l.split()[3]) for l in L[1:1 + n]])
def col(p):
    return np.array([float(l) for l in Path(p).read_text().split("\n") if l.strip() and not l.startswith("#")])

# --- R60.1 energies and potentials
runs = {"WXV_R": "d37/wB97XV_SV_R", "WXV_TS": "d37/wB97XV_SV_TS", "CAM_R": "d33a/sp_42436_R", "CAM_TS": "d33a/sp_42436_TS"}
tsv = {r["run"]: r for r in csv.DictReader(open(S6 / "d60.tsv"), delimiter="\t")}
for r, ref in runs.items():
    e, e0 = final_E(S6 / "d60" / r / "job.out"), final_E(S6 / ref / "job.out")
    chk("%s energy %.9f equals d60.tsv's" % (r, e), abs(e - float(tsv[r]["energy_Eh"])) < 5e-10)
    chk("%s minus %s = %.2e Eh, within 1e-6" % (r, ref, e - e0), abs(e - e0) <= 1e-6)
    chk("%s energy as printed in the result" % r, ("%.9f" % e) in res)
    t = Path(S6 / "d60" / r / "job.out").read_text()
    chk("%s ORCA TERMINATED NORMALLY" % r, "ORCA TERMINATED NORMALLY" in t)
for r in ("CAM_R", "CAM_TS"):
    dv = float(np.abs(vpot(S6 / "d60" / r / "vpot.out") - vpot(S6 / runs[r] / "vpot.out")).max())
    chk("%s largest potential difference %.2e Eh/e within 1e-4; d60.tsv says %s" % (r, dv, tsv[r]["largest_potential_difference_Eh_per_e"]),
        dv <= 1e-4 and abs(dv - float(tsv[r]["largest_potential_difference_Eh_per_e"])) < 1e-15 + 1e-3 * dv)

# --- the wB97X-V map from its own potentials
a_wxv = (vpot(S6 / "d60/WXV_TS/vpot.out") - vpot(S6 / "d60/WXV_R/vpot.out")) * H
a_wxv_file = col(S6 / "A_f42436_d60_wB97XV.tsv")
chk("the map at wB97X-V from the two potentials equals A_f42436_d60_wB97XV.tsv (largest %.1e kcal/mol/e)" % np.abs(a_wxv - a_wxv_file).max(),
    len(a_wxv) == len(a_wxv_file) == 2626 and np.abs(a_wxv - a_wxv_file).max() < 1e-5)
a_cam = col(S6 / "A_f42436_d33a.tsv"); a_b3 = col(S6 / "A_f42436.tsv")
chk("the working and B3LYP maps have 2626 rows each", len(a_cam) == len(a_b3) == 2626)

# --- sites that admit a charge of size at most 0.25 e (my reading of the site table's header rule)
rows = [l.split("\t") for l in (S6 / "sites_f42436.tsv").read_text().splitlines() if not l.startswith("#")]
hd, rows = rows[0], rows[1:]
ci = {k: hd.index(k) for k in ("x", "y", "z", "q_min_neg", "q_min_pos")}
xyz = np.array([[float(r[ci[k]]) for k in "xyz"] for r in rows])
neg = [r[ci["q_min_neg"]].strip() == "-1.00" for r in rows]
pos = [r[ci["q_min_pos"]].strip() not in ("none", "") and float(r[ci["q_min_pos"]]) <= 0.25 + 1e-12 for r in rows]
keep = np.array([i for i in range(len(rows)) if neg[i] or pos[i]])
chk("sites that admit a charge after the 0.25 e cut: %d (the result says 1488)" % len(keep), len(keep) == 1488)

# --- R60.2 map statistics
for name, m, want in (("wB97X-V", a_wxv_file, (0.9977, 0.9920, 0.1488, 0.3262)), ("B3LYP", a_b3, (0.9763, 0.9358, 0.4588, 1.1773))):
    x, y = a_cam[keep], m[keep]
    got = (np.corrcoef(x, y)[0, 1], spearmanr(x, y)[0], np.abs(y - x).mean(), np.abs(y - x).max())
    chk("%s against the working map: Pearson %.4f, Spearman %.4f, mean %.4f, largest %.4f" % ((name,) + got),
        all(abs(round(g, 4) - w) < 1e-9 for g, w in zip(got, want)))

# --- R60.3 designs: rules, scores on each map, 'same', and the printed columns
D = list(csv.DictReader(open(S6 / "d60_designs.tsv"), delimiter="\t"))
maps = {"working": a_cam, "wB97X-V": a_wxv_file, "B3LYP": a_b3}
colname = {"working": "score_working_map_kcal", "wB97X-V": "score_wB97X-V_map_kcal", "B3LYP": "score_B3LYP_map_kcal"}
groups = {}
worst_rule = worst_score = 0.0
for d in D:
    s = [int(v) for v in d["sites"].split(",")]; q = [float(v) for v in d["charges_e"].split(",")]
    d["S"], d["Q"], d["n"] = s, q, int(d["n"])
    for k, m in maps.items():
        worst_score = max(worst_score, abs(sum(m[i] * v for i, v in zip(s, q)) - float(d[colname[k]])))
    xs = xyz[s]
    dmin = min(np.linalg.norm(xs[i] - xs[j]) for i in range(len(s)) for j in range(i + 1, len(s)))
    okrule = all(abs(abs(v) - 0.25) < 1e-9 for v in q) and sum(q) >= -1e-9 and dmin >= 3.25 - 1e-6 and len(s) == d["n"] \
        and all((neg[i] if v < 0 else pos[i]) for i, v in zip(s, q))
    worst_rule += (not okrule)
    groups.setdefault(d["map"].split()[0], {}).setdefault(d["n"], []).append(d)
chk("every one of the %d designs' scores on all three maps recomputed (largest difference %.1e kcal/mol)" % (len(D), worst_score), worst_score < 1e-5)
chk("every design keeps D56's rules: n charges of exactly 0.25 e, each admitted at its site, sum >= 0, spacing >= 3.25 A (%d break one)" % worst_rule, worst_rule == 0)
key = lambda d: tuple(sorted(zip(d["S"], [round(v, 4) for v in d["Q"]])))
sec3 = res[res.find("R60.3  THE SEARCH"):res.find("R60.4  D56")]
d56 = groups["working"]
found = {}
for mp in ("wB97X-V", "B3LYP"):
    found[mp] = 0
    for n, ds in sorted(groups[mp].items()):
        same = sum(key(d) in {key(e) for e in d56[n]} for d in ds)
        flag = (any(d["same_as_a_D56_design"] == "yes" for d in ds) or same == 0)
        found[mp] += same
        own = min(float(d[colname[mp]]) for d in ds)
        best = min(ds, key=lambda d: float(d[colname[mp]]))
        # the column is D56's first-ranked design scored on this map (the reader: score(mine[0], m)),
        # not the lowest of D56's three; the lowest of the three is printed beside it for the record
        k1 = [e for e in d56[n] if e["rank_at_n"] == "1"]
        assert len(k1) == 1
        d56own = float(k1[0][colname[mp]])
        low3 = min(float(e[colname[mp]]) for e in d56[n])
        if abs(low3 - d56own) > 1e-9:
            print("   (record) %s n=%d: D56's lowest of three on this map is %.4f (%s), its first-ranked %.4f" % (
                mp, n, low3, min(d56[n], key=lambda e: float(e[colname[mp]]))["design"], d56own))
        line = re.search(r"^\s*%d\s+(\d) of 3\s+\d of 3\s+[\d.]+\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)" % n,
                         sec3.split("   B3LYP (its basis")[0] if mp == "wB97X-V" else sec3.split("   B3LYP (its basis")[1], re.M)
        printed = (int(line.group(1)), float(line.group(2)), float(line.group(3)), float(line.group(4)))
        mine = (same, round(own, 4), round(d56own, 4), round(float(best["score_working_map_kcal"]), 4))
        chk("%s n=%d: same %d of 3, its best %.4f, D56's best on its map %.4f, its best on the working map %.4f" % ((mp, n) + mine),
            mine[0] == printed[0] and all(abs(a - b) < 1e-9 for a, b in zip(mine[1:], printed[1:])) and
            sum(d["same_as_a_D56_design"] == "yes" for d in ds) == same)
chk("found again: wB97X-V %d of 27, B3LYP %d of 27 (the result: 17 and 3)" % (found["wB97X-V"], found["B3LYP"]), found["wB97X-V"] == 17 and found["B3LYP"] == 3)

# --- R60.4 consistency of the random-design summary
N = list(csv.DictReader(open(S6 / "d60_null.tsv"), delimiter="\t"))
inc = [r["design"] for r in N if not (float(r["score_working_map_kcal"]) < float(r["kind_i_lowest"]) and float(r["score_working_map_kcal"]) < float(r["kind_ii_lowest"]))]
chk("every design's score is below the lowest random score of both kinds, as 'beats 100.00 %%' needs (%d not)" % len(inc),
    not inc and all(r["beats_kind_i_percent"] == "100.00" and r["beats_kind_ii_percent"] == "100.00" for r in N) and len(N) == 27)
d56s = {e["design"]: float(e["score_working_map_kcal"]) for ds in d56.values() for e in ds}
chk("d60_null.tsv's 27 scores are D56's on the working map", all(abs(d56s[r["design"]] - float(r["score_working_map_kcal"])) < 1e-9 for r in N))
gap10 = d56s["S_n10_k1"] - min(float(r["kind_ii_lowest"]) for r in N if r["n"] == "10")
print("\n(derived) at ten charges D56's best is %.4f kcal/mol below the lowest random design of kind (ii)" % -gap10)
print("checks: %d pass, %d fail" % (ok, bad))
