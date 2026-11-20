#!/usr/bin/env python3
"""UNOFFICIAL inspection of a PEEK printout of D44 (levels whose jobs have ended). NOT the committed reader cs6_d44.py:
it applies none of its gates and reads none of the four reliability legs (Loewdin rise, dipole ratio, gap, the
charge-moved judgement). It forms only what the pre-registration defines from energies:
  ddE = (E(TS) - E(TS, control)) - (E(R) - E(R, control)) on di and the level's control di, 627.5094740631 kcal/mol per Eh
  the tolerance: |ddE - working| against 15 % of |working| (working = D43's committed ddE), floor 3.2 kcal/mol
  VDE = E(mo) - E(di) at 27.211386245988 eV per Eh
  the control check at a double hybrid: C_ctl against the committed energy of the same input, 1e-6 Eh
usage: inspect_d44.py <results checkout at 11cba65e> <PEEK printout>"""
import re, sys
from pathlib import Path
RES, TXT = Path(sys.argv[1]) / 'phase2.2/cs_stage6', Path(sys.argv[2]).read_text()
KCAL, EV = 627.5094740631, 27.211386245988
DESIGNS = ['B_n02_q0.50', 'B_n02_q0.75', 'B_n02_q1.00', 'B_n03_q0.75', 'B_n05_q0.50', 'B_n11_q0.25']
COMMITTED = {'PWSV': 'd37/PWPB95_SV_%s/job.out', 'PWTZ': 'd37/PWPB95_TZ_%s/job.out', 'RDSV': 'd37a1/revDSD_RI_SV_%s/job.out', 'RDTZ': 'd37a1/revDSD_RI_TZ_%s/job.out'}
def last_fspe(p):
    v = [l.split()[4] for l in p.read_text(errors='replace').split('\n') if l.startswith('FINAL SINGLE POINT ENERGY')]
    return float(v[-1])
# working level, from the committed table
rows = [l.split('\t') for l in (RES / 'd43.tsv').read_text().split('\n') if l and not l.startswith('#')]
H = {h: i for i, h in enumerate(rows[0])}
work, wvde = {}, {}
for r in rows[1:]:
    if r[H['condition']] in DESIGNS:
        work.setdefault(r[H['condition']], set()).add(float(r[H['ddE_kcal']]))
        wvde[(r[H['condition']], r[H['state']])] = float(r[H['VDE_eV']])
assert all(len(v) == 1 for v in work.values()) and sorted(work) == sorted(DESIGNS)
work = {k: v.pop() for k, v in work.items()}
runs, levels = {}, []
for l in TXT.split('\n'):
    l = l.strip()
    m = re.match(r'LEVEL (\w+) (.*)', l)
    if m:
        levels.append((m.group(1), m.group(2)))
    m = re.match(r'RUN (\S+) (normal E=(\S+) last_stability=(\S+) unstable_verdicts=(\d+) scf_converged=(\d+)|NOT_NORMAL|NO_OUTPUT)$', l)
    if m:
        name = m.group(1)
        runs[name] = dict(ok=m.group(2).startswith('normal'), E=float(m.group(3)) if m.group(3) else None, last=m.group(4), nun=int(m.group(5)) if m.group(5) else None,
                          nconv=int(m.group(6)) if m.group(6) else None, raw=m.group(2))
print('UNOFFICIAL INSPECTION of D44. Not the committed reader; no gate applied; the four reliability legs are NOT read.')
print('Nothing here is a result of D44, and no design passes or fails on it.')
print('runs in the printout: %d, of which ended normally: %d' % (len(runs), sum(r['ok'] for r in runs.values())))
E = lambda n: runs[n]['E'] if n in runs and runs[n]['ok'] else None
for L, note in levels:
    print('\n' + '=' * 100 + '\nLEVEL %s   (%s)' % (L, note))
    mine = {k: v for k, v in runs.items() if k.startswith(L + '_')}
    if not mine:
        continue
    print('  ended normally: %d of %d' % (sum(v['ok'] for v in mine.values()), len(mine)))
    c = {s: E('%s_C_ctl_%s' % (L, s)) for s in ('R', 'TS')}
    for s in ('R', 'TS'):
        if c[s] is None:
            print('  control C_ctl_%s: not available' % s); continue
        ref = last_fspe(RES / (COMMITTED[L] % s)) if L in COMMITTED else None
        print('  control C_ctl_%s: E = %.9f Eh%s' % (s, c[s], '' if ref is None else ';  committed %s = %.9f;  difference %+.2e Eh (%s 1e-6)' % (COMMITTED[L] % s, ref, c[s] - ref, 'within' if abs(c[s] - ref) < 1e-6 else 'OUTSIDE')))
    if None not in c.values():
        print('  charge-free barrier at this level, from the two controls: %.4f kcal/mol' % ((c['TS'] - c['R']) * KCAL))
    b = {s: E('%s_C_bare_%s' % (L, s)) for s in ('R', 'TS')}
    for s in ('R', 'TS'):
        if b[s] is not None and c[s] is not None:
            print('  bare substrate VDE at %s: %+.4f eV (monoanion last stability verdict: %s)' % (s, (b[s] - c[s]) * EV, runs['%s_C_bare_%s' % (L, s)]['last']))
    for s in ('R', 'TS'):
        n = '%s_C_ctlS_%s' % (L, s)
        if n in runs and runs[n]['ok'] and c[s] is not None:
            print('  stability search on the charge-free dianion at %s: unstable verdicts %d, last verdict %s, E(ctlS) - E(ctl) = %+.3e Eh' % (s, runs[n]['nun'], runs[n]['last'], runs[n]['E'] - c[s]))
    print('\n  %-13s %10s %10s %9s %8s  %-15s | %-22s | %s' % ('design', 'ddE', 'working', 'differ', 'percent', 'tolerance (15 %)', 'VDE R, TS (eV); working', 'ds search: R; TS'))
    for d in DESIGNS:
        di = {s: E('%s_%s_di_%s' % (L, d, s)) for s in ('R', 'TS')}
        if None in di.values() or None in c.values():
            why = '; '.join('di_%s %s' % (s, runs.get('%s_%s_di_%s' % (L, d, s), {}).get('raw', 'absent').split(' ')[0]) for s in ('R', 'TS'))
            print('  %-13s %10s %10.4f %9s %8s  %-15s | %-22s | %s' % (d, 'NOT FORMED', work[d], '', '', why, '', ''))
            continue
        dde = ((di['TS'] - c['TS']) - (di['R'] - c['R'])) * KCAL
        diff = dde - work[d]
        tol = 'NOT ASSESSABLE' if abs(work[d]) < 3.2 else ('WITHIN' if abs(diff) < 0.15 * abs(work[d]) else 'OUTSIDE')
        v = []
        for s in ('R', 'TS'):
            mo = E('%s_%s_mo_%s' % (L, d, s))
            v.append('n/a' if mo is None else '%+.3f(%s)' % ((mo - di[s]) * EV, runs['%s_%s_mo_%s' % (L, d, s)]['last'][:6]))
        ds = []
        for s in ('R', 'TS'):
            n = '%s_%s_ds_%s' % (L, d, s)
            if n in runs and runs[n]['ok']:
                ds.append('%d unstable, last %s, dE %+.1e' % (runs[n]['nun'], runs[n]['last'], runs[n]['E'] - di[s]))
            else:
                ds.append('n/a')
        print('  %-13s %10.4f %10.4f %+9.4f %+7.1f%%  %-15s | %s, %s; %+.3f, %+.3f | %s; %s' % (d, dde, work[d], diff, 100 * diff / abs(work[d]), tol, v[0], v[1], wvde[(d, 'R')], wvde[(d, 'TS')], ds[0], ds[1]))
        st = ['%s (%d unstable)' % (runs['%s_%s_di_%s' % (L, d, s)]['last'], runs['%s_%s_di_%s' % (L, d, s)]['nun']) for s in ('R', 'TS')]
        if any(not x.startswith('none') for x in st):
            print('  %-13s di stability, last verdict at R; TS: %s; %s' % ('', st[0], st[1]))
print('\nddE and differ in kcal/mol; negative ddE lowers the barrier. "percent" is differ as a share of |working|.')
print('dE of the ds search is E(ds) - E(di) in Eh: zero means the search ended on the solution whose energy is used.')
