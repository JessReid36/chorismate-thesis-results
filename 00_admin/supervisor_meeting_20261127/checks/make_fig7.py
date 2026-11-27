"""Figure 7 of the November 2026 work-status document (Claude, 26 Nov 2026), drawn from committed files of the results
repository: d60_designs.tsv and d60_null.tsv. usage: make_fig7.py <.../phase2.2/cs_stage6> <outdir>"""
import csv, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
S6, OUT = Path(sys.argv[1]), Path(sys.argv[2])
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
INK, GREY, LIGHT = "#222222", "#9a9a9a", "#d9d9d9"
BLUE, ORANGE = "#2a6ebb", "#d9822b"
D = list(csv.DictReader(open(S6 / "d60_designs.tsv"), delimiter="\t"))
N = list(csv.DictReader(open(S6 / "d60_null.tsv"), delimiter="\t"))
key = lambda d: (d["sites"], d["charges_e"])
NS = sorted({int(d["n"]) for d in D})
assert NS == [3, 4, 5, 6, 8, 10, 12, 15, 20]
ours = {n: [d for d in D if d["map"].startswith("working") and int(d["n"]) == n] for n in NS}
assert all(len(v) == 3 for v in ours.values())
MAPS = [("wB97X-V", "ωB97X-V/def2-SVPD", BLUE, "o"), ("B3LYP", "B3LYP-D3BJ/def2-SVP", ORANGE, "s")]
found, gap = {}, {}
print("Figure 7")
for m, lab, _, _ in MAPS:
    found[m], gap[m] = [], []
    for n in NS:
        th = [d for d in D if d["map"] == m and int(d["n"]) == n]
        assert len(th) == 3
        f = sum(key(d) in {key(e) for e in ours[n]} for d in th)
        best = min(th, key=lambda d: float(d["score_%s_map_kcal" % m]))
        k1 = [e for e in ours[n] if e["rank_at_n"] == "1"][0]
        g = float(best["score_working_map_kcal"]) - float(k1["score_working_map_kcal"])
        found[m].append(f); gap[m].append(g)
    print("  %s: found again %s (total %d); best on working map minus ours %s" % (m, found[m], sum(found[m]), ["%.4f" % g for g in gap[m]]))
assert sum(found["wB97X-V"]) == 17 and sum(found["B3LYP"]) == 3
x = np.arange(len(NS))
fig = plt.figure(figsize=(9.6, 8.4))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1])
a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
# A: found again
for i, (m, lab, col, _) in enumerate(MAPS):
    xs = x + (-0.19 if i == 0 else 0.19)
    a1.bar(xs, found[m], width=0.36, color=col, label=lab)
    for xi, v in zip(xs, found[m]):
        a1.text(xi, v + 0.05, str(v), ha="center", va="bottom", fontsize=7, color=INK)
a1.set_xticks(x); a1.set_xticklabels(NS); a1.set_ylim(0, 3.4); a1.set_yticks([0, 1, 2, 3])
a1.set_xlabel("number of charges"); a1.set_ylabel("of the search's 3 designs, placed again")
a1.set_title("A. The same designs at another map?", loc="left", fontsize=9.5)
a1.legend(frameon=False, loc="upper right", fontsize=7.5, bbox_to_anchor=(1.0, 1.0))
# B: each map's best, scored on the working map, minus the search's best
for i, (m, lab, col, mk) in enumerate(MAPS):
    xs = x + (-0.12 if i == 0 else 0.12)
    a2.vlines(xs, 0, gap[m], color=col, lw=1.4)
    a2.scatter(xs, gap[m], s=34, color=col, marker=mk, zorder=3, label=lab)
a2.axhline(0, color=GREY, lw=0.8)
a2.set_xticks(x); a2.set_xticklabels(NS); a2.set_ylim(-0.02, 0.34)
a2.set_xlabel("number of charges"); a2.set_ylabel("lowering it gives up (kcal/mol)")
a2.set_title("B. That map's best design, on the working map", loc="left", fontsize=9.5)
a2.legend(frameon=False, loc="upper left", fontsize=7.5)
# C: against random designs
for n_i, n in enumerate(NS):
    z = [r for r in N if int(r["n"]) == n]
    assert len(z) == 3
    r = z[0]
    for off, kind, c in ((-0.22, "i", LIGHT), (0.22, "ii", GREY)):
        med, low = float(r["kind_%s_median" % kind]), float(r["kind_%s_lowest" % kind])
        a3.plot([n_i + off, n_i + off], [med, low], color=c, lw=4, solid_capstyle="butt", zorder=1)
    sc = [float(e["score_working_map_kcal"]) for e in z]
    a3.scatter([n_i] * 3, sc, s=16, color=INK, zorder=3)
    assert all(float(e["beats_kind_i_percent"]) == 100 and float(e["beats_kind_ii_percent"]) == 100 for e in z)
a3.set_xticks(x); a3.set_xticklabels(NS); a3.invert_yaxis()
a3.set_xlabel("number of charges"); a3.set_ylabel("first-order score (kcal/mol); higher up is a larger lowering")
a3.set_title("C. The search's designs against random designs", loc="left", fontsize=9.5)
a3.legend(handles=[Line2D([], [], marker="o", ls="", color=INK, markersize=5, label="the search's 3 designs"),
                   Line2D([], [], color=LIGHT, lw=4, label="random, kind (i): median to best of 10 000"),
                   Line2D([], [], color=GREY, lw=4, label="random, kind (ii): median to best of 10 000")],
          frameon=False, loc="upper left", fontsize=7.5)
a3.set_ylim(1.0, -17.0)
fig.tight_layout(); fig.savefig(OUT / "N7_second_functional_and_random.png", dpi=200); plt.close(fig)
lo = {n: min(float(r["kind_ii_lowest"]) for r in N if int(r["n"]) == n) for n in NS}
worst = {n: max(float(r["score_working_map_kcal"]) for r in N if int(r["n"]) == n) for n in NS}
print("  the search's weakest design minus the best random design of kind (ii): %s" % ", ".join("n %d %.4f" % (n, worst[n] - lo[n]) for n in NS))
