#!/usr/bin/env python3
"""
c4_collect.py - hpc1 side of x80: the outputs of C4's re-optimisation runs (05_qmmm/23_c4_reactant: S0_<frame> and
S2_<frame> of runs.tsv, and any M1 continuation <run>_c) kept as physical files (Jessica's rule of 18 October 2026),
before C4's analysis is run on them and before anything is removed from hpc1 (C4_CLOSURE.txt). Run by x80_c4.sh on the
PC over ssh (python3 - MODE ...); Python 3.6, standard library plus the qstat, qselect, tar and xz commands.

  status CD                     read-only: every run's job (in the queue or ended, and how its output ends) and what
                                would happen to its files
  files CD                      read-only: every file and link of every run folder (size and mtime, or "link"), and any
                                folder in CD named like a run that is not one; x80_c4.sh checks these against the
                                batches, so that a file written after its batch is never missed
  stage CD OUT N RUN [...]      non-destructive (writes only in OUT): the listed runs, whose jobs must have ended

What happens to each file of a staged run (every regular file also goes into the PC archive):
  git_text   text up to 50 MB: committed in one tar.xz per run, with a sha256 manifest; stays on hpc1. ORCA input and
             output, the job script and its output, the energy CSV, geometries (start.xyz, reopt.xyz, final_active.xyz,
             PDB), gradients, property and other text files
  git_xz     text over 50 MB, and the run's final wavefunction and densities (reopt.gbw, reopt.densities): committed
             one by one as .xz; stay on hpc1 as they are
  git_asis   files the job already compressed (*.xz up to 95 MB, passing xz -t): committed as they are
  pc_keep    on the PC (archive) and in the manifest, not in git; stay on hpc1: the trajectory (reopt_trj.dcd, which a
             run killed by the walltime keeps for its M1 continuation), other MD-format files, full-system trajectories
             over 20 MB, binary files of no other kind, a job's .xz over 95 MB
  scratch    ORCA scratch (*.tmp, *.tmp.N) and SCF intermediates (*.gbwN): on the PC (archive) and in the manifest; not
             deleted by x80 (x80 deletes nothing)
  link       symbolic links (the force field): recorded with their target and the target's sha256
Anything unexpected stops the staging: a folder inside a run folder, a non-regular file, an .xz failing xz -t, a file
next to its own .xz, a git file over 95 MB after compression.
"""
import hashlib, os, re, shutil, subprocess, sys, time

REL0 = "05_qmmm/23_c4_reactant"
NATOMS = 55680
MB = 1000000
ARCH_MAX, TRJ_MAX, GIT_MAX = 50 * MB, 20 * MB, 95 * MB
SCRATCH_RE = re.compile(r"(\.tmp|\.tmp\.[^/]*|\.gbw\d+)$")
FINAL_WFN = ("reopt.gbw", "reopt.densities")
MDFMT_RE = re.compile(r"(\.dcd|\.mdrestart)$")
CATS = ("git_text", "git_xz", "git_asis", "pc_keep", "scratch", "link")
RUN_RE = re.compile(r"^S[02]_\d+(_c)?$")
TIMEOUT = 300
XZ_LEVELS = ("-6", "-3")      # single-threaded: -6 needs about 94 MiB, -3 about 32 MiB (the login node limits memory)

def die(msg): print("STOP: " + msg); sys.stdout.flush(); sys.exit(1)
def sha(p, memo=None):
    if memo is not None and p in memo: return memo[p]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    if memo is not None: memo[p] = h.hexdigest()
    return h.hexdigest()
def run(cmd, **kw):
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT, **kw)
    except FileNotFoundError:
        die("%s is not available here" % cmd[0])
    except subprocess.TimeoutExpired:
        die("%s did not answer within %d s" % (" ".join(cmd), TIMEOUT))
def root_of(cd):
    cd = os.path.abspath(cd)
    if not cd.endswith("/" + REL0): die("%s is not .../%s" % (cd, REL0))
    return cd[:-len(REL0) - 1]
def runs_of(cd):
    """the runs of runs.tsv, then any M1 continuation <run>_c of one of them that exists"""
    p = os.path.join(cd, "runs.tsv")
    if not os.path.isfile(p): die("%s/runs.tsv is missing" % cd)
    R = [l.split("\t")[0] for l in open(p) if l.strip() and not l.startswith("#")]
    if len(R) != 35 or len(set(R)) != 35 or not all(RUN_RE.match(r) and not r.endswith("_c") for r in R):
        die("runs.tsv does not list the 35 C4 runs")
    C = [r + "_c" for r in R if os.path.isdir(os.path.join(cd, r + "_c"))]
    return R + C
def strays(cd, runs):
    """folders in CD named like a run that are not runs (and run folders that are links)"""
    out = []
    for n in sorted(os.listdir(cd)):
        if n in runs:
            if os.path.islink(os.path.join(cd, n)): out.append(n + " (a link)")
        elif n.startswith(("S0_", "S2_")): out.append(n)
    return out

# ---- jobs
def qstat_f(jid):
    """(state, attributes) of one job: 'ended' when PBS says it does not know it or that it has finished; any other
    qstat failure stops everything, so a job is never taken as ended because qstat could not be asked"""
    r = run(["qstat", "-f", jid])
    o, e = r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    if r.returncode != 0:
        if re.search(r"Unknown Job Id|Job has finished", e + o): return "ended", {}
        die("qstat -f %s failed: %s" % (jid, (e + o).strip()[:200]))
    A = {}; key = None
    for l in o.splitlines():                       # PBS wraps long values onto lines that start with a tab
        if l.startswith("\t") and key: A[key] += l.strip(); continue
        m = re.match(r"\s+([\w.]+) = (.*)$", l)
        if m: key = m.group(1); A[key] = m.group(2).strip()
    st = A.get("job_state")
    if not st: die("qstat -f %s printed no job_state" % jid)
    return ("ended" if st == "F" else st), A
def user_jobs():
    """ids of this user's jobs in the queue: qselect, or the first column of qstat -u where qselect is missing"""
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
    if not user: die("cannot tell the user name for qselect")
    try:
        r = subprocess.run(["qselect", "-u", user], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT)
        if r.returncode != 0: die("qselect -u %s failed: %s" % (user, r.stderr.decode(errors="replace").strip()[:200]))
        return r.stdout.decode().split()
    except FileNotFoundError:
        r = run(["qstat", "-u", user])
        if r.returncode != 0: die("qstat -u %s failed: %s" % (user, r.stderr.decode(errors="replace").strip()[:200]))
        ids = re.findall(r"^(\d+\.\S+)\s", r.stdout.decode(errors="replace"), re.M)
        if any(i.endswith("*") for i in ids): die("qstat -u shows shortened job ids; qselect is needed")
        return ids
    except subprocess.TimeoutExpired:
        die("qselect did not answer within %d s" % TIMEOUT)
def states(cd, runs):
    """run -> (job id or -, state): a job of this user in the queue whose output goes into the run folder makes the run
    active; otherwise the run has ended if its job output exists, and has not started if it does not"""
    S = dict((r, ("-", None)) for r in runs)
    for jid in user_jobs():
        st, A = qstat_f(jid)
        if st == "ended": continue
        out = A.get("Output_Path", "").split(":", 1)[-1]
        wd = A.get("Variable_List", "")
        for r in runs:
            d = os.path.join(cd, r) + "/"
            if out.startswith(d) or ("PBS_O_WORKDIR=" + d.rstrip("/")) in wd.split(","):
                S[r] = (jid, st)
    for r in runs:
        if S[r][1] is None:
            S[r] = ("-", "ended" if os.path.isfile(os.path.join(cd, r, "reopt.pbs.out")) else "not started")
    return S
def job_end(cd, r):
    p = os.path.join(cd, r, "reopt.pbs.out")
    if not os.path.isfile(p): return "no job output"
    t = open(p, errors="replace").read()
    marks = [l.strip() for l in t.splitlines()
             if re.match(r"^\s*(C4_REOPT_\w+|extract=\w+|orca_exit=\S+|FAIL .*|=>> PBS:.*|PBS: job killed.*)", l)]
    return ("; ".join(marks[-4:]) or "no mark") + ("" if re.search(r"^end=", t, re.M) else " (no end= line)")

# ---- files
def is_binary(p):
    with open(p, "rb") as f: return b"\0" in f.read(1 << 20)
def first_int(p):
    with open(p, "rb") as f: l = f.readline(200).split()
    try: return int(l[0])
    except (IndexError, ValueError): return None
def xz_ok(p): return run(["xz", "-t", p]).returncode == 0
def run_files(cd, r):
    rd = os.path.join(cd, r)
    if os.path.islink(rd) or not os.path.isdir(rd): die("%s is a link or missing" % r)
    F = []
    for n in sorted(os.listdir(rd)):
        p = os.path.join(rd, n)
        if os.path.isdir(p) and not os.path.islink(p): die("%s holds the folder %s: not expected; tell Claude" % (r, n))
        F.append(p)
    return F
def classify(path):
    n = os.path.basename(path)
    if os.path.islink(path): return "link", "link"
    if not os.path.isfile(path): die("%s is not a regular file: tell Claude" % path)
    size = os.path.getsize(path)
    if n.endswith(".xz"):
        if not xz_ok(path): die("%s fails xz -t: tell Claude" % path)
        if size > GIT_MAX: return "pc_keep", "a job's .xz over 95 MB (PC archive only)"
        return "git_asis", "compressed by the job"
    if os.path.lexists(path + ".xz"): die("%s and its .xz both exist: tell Claude" % path)
    if SCRATCH_RE.search(n): return "scratch", "ORCA scratch or SCF intermediate (PC archive only)"
    if MDFMT_RE.search(n): return "pc_keep", "MD-format trajectory or restart (PC archive only; the M1 continuation may need it)"
    if n in FINAL_WFN: return "git_xz", "the run's final wavefunction or densities"
    if n.endswith("_trj.xyz") and first_int(path) == NATOMS and size > TRJ_MAX:
        return "pc_keep", "full-system trajectory over 20 MB (PC archive only)"
    if is_binary(path): return "pc_keep", "binary file of no other kind (PC archive only)"
    return ("git_xz", "text over 50 MB") if size > ARCH_MAX else ("git_text", "text")
def size_or_none(p):
    try: return 0 if os.path.islink(p) else os.path.getsize(p)
    except FileNotFoundError: return None
def gb(b): return "%.2f GB" % (b / 1e9)

def files(cd):
    root = root_of(cd); runs = runs_of(cd)
    for r in runs:
        rd = os.path.join(cd, r)
        if os.path.islink(rd) or not os.path.isdir(rd): print("M\t%s" % r); continue
        for dp, dn, fn in os.walk(rd):
            dn.sort()
            for d in dn: print("S\t%s" % os.path.relpath(os.path.join(dp, d), root))
            for f in sorted(fn):
                p = os.path.join(dp, f)
                if os.path.islink(p): print("F\t%s\tlink\t-" % os.path.relpath(p, root)); continue
                try: st = os.stat(p)
                except FileNotFoundError: continue
                print("F\t%s\t%d\t%s" % (os.path.relpath(p, root), st.st_size,
                                          time.strftime("%Y-%m-%dT%H:%M", time.localtime(st.st_mtime))))
    for n in strays(cd, runs): print("D\t%s" % n)

def status(cd):
    runs = runs_of(cd); S = states(cd, runs)
    st = strays(cd, runs)
    if st: print("NOTE: folders named like a run that are not runs of runs.tsv (or are links): " + ", ".join(st))
    print("== runs: job (in the queue, or ended), how its output ends, and what would happen to its files once it has ended")
    tot = {}; out = []
    for r in runs:
        jid, s = S[r]
        C = {}
        if s == "ended":
            for p in run_files(cd, r):
                z = size_or_none(p)
                if z is None: continue
                c, why = classify(p)
                for D in (C, tot): D.setdefault(c, [0, 0]); D[c][0] += 1; D[c][1] += z
        print("  %-10s %-14s %-12s %-62s | %s" % (r, jid, s, "; ".join("%s %d (%s)" % (c, v[0], gb(v[1])) for c, v in sorted(C.items())),
              job_end(cd, r)))
        out.append("RUNSTATE %s %s" % (r, "ended" if s == "ended" else "active"))
    print("== totals (ended runs): " + "; ".join("%s %d files %s" % (c, v[0], gb(v[1])) for c, v in sorted(tot.items())))
    print("\n".join(out))

def stage(cd, out, n, want):
    root = root_of(cd); runs = runs_of(cd)
    if os.path.exists(out): die("%s exists" % out)
    st = strays(cd, runs)
    if st: die("folders named like a run that are not runs of runs.tsv (or are links): %s: tell Claude" % ", ".join(st))
    S = states(cd, runs)
    for r in want:
        if r not in runs: die("unknown run %s" % r)
        if S[r][1] != "ended": die("%s: its job (%s) is %s" % (r, S[r][0], S[r][1]))
    if len(set(want)) != len(want): die("a run is listed twice")
    rel = lambda p: os.path.relpath(p, root)
    cats = dict((c, []) for c in CATS)
    for r in want:
        for p in run_files(cd, r):
            c, why = classify(p)
            cats[c].append((r, p, why))
    need = sum(size_or_none(p) or 0 for c in ("git_text", "git_xz", "git_asis") for (r, p, w) in cats[c]) + 2 * 10**9
    vfs = os.statvfs(os.path.dirname(os.path.abspath(out)))
    if vfs.f_bavail * vfs.f_frsize < need:
        die("the stage needs up to %s and %s has only %s free" % (gb(need), os.path.dirname(out), gb(vfs.f_bavail * vfs.f_frsize)))
    os.makedirs(out + "/work")
    try:
        build(cd, root, out, n, want, cats, S, rel, runs)
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    print(open(out + "/SUMMARY.txt").read(), end="")
    print("staged in %s (nothing in %s was changed)" % (out, cd))

def xz_file(src, dst):
    for level in XZ_LEVELS:                                          # the login node limits memory: one thread
        with open(dst, "wb") as fo:
            if subprocess.run(["xz", level, "-T1", "-c", src], stdout=fo).returncode == 0: return
    die("xz %s failed" % src)

def build(cd, root, out, n, want, cats, S, rel, runs):
    M = {}
    shm = lambda p: sha(p, M)
    staged = set(p for L in cats.values() for (r, p, w) in L)
    catof = dict((p, c) for c, L in cats.items() for (r, p, w) in L)
    with open(out + "/inventory.tsv", "w") as fh:                 # every file of every run folder
        fh.write("# the C4 run folders, listed %s; size, mtime, path (relative to system_development), category in batch %s "
                 "(- = not in this batch), sha256 (batch files; for a link: link:TARGET:SHA256 of the target)\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), n))
        for r in runs:
            for dp, dn, fn in os.walk(os.path.join(cd, r)):
                dn.sort()
                for f in sorted(fn):
                    p = os.path.join(dp, f)
                    if os.path.islink(p):
                        t = os.path.realpath(p)
                        th = shm(t) if (p in staged and os.path.isfile(t)) else "-"
                        if p in staged and th == "-": die("the link %s points to no file" % rel(p))
                        fh.write("0\t-\t%s\t%s\tlink:%s:%s\n" % (rel(p), catof.get(p, "-"), os.readlink(p), th)); continue
                    try: st = os.stat(p)
                    except FileNotFoundError:
                        if p in staged: die("%s vanished while being staged" % rel(p))
                        continue
                    fh.write("%d\t%s\t%s\t%s\t%s\n" % (st.st_size, time.strftime("%Y-%m-%dT%H:%M", time.localtime(st.st_mtime)),
                             rel(p), catof.get(p, "-"), shm(p) if p in staged else "-"))
    built = []; groups = {}
    for (r, p, w) in cats["git_text"]: groups.setdefault(r, []).append(p)
    for r, L in sorted(groups.items()):
        name = "%s/%s/hpc_text_outputs_%s.tar.xz" % (REL0, r, n)
        lst = out + "/work/list_%s" % r
        with open(lst, "w") as fh: fh.write("".join(rel(p) + "\n" for p in L))
        os.makedirs(os.path.dirname(out + "/arch/" + name), exist_ok=True)
        for level in XZ_LEVELS:
            with open(out + "/arch/" + name, "wb") as fo:
                t = subprocess.Popen(["tar", "-cf", "-", "--no-recursion", "-T", lst], cwd=root, stdout=subprocess.PIPE)
                x = subprocess.Popen(["xz", level, "-T1", "-c"], stdin=t.stdout, stdout=fo); t.stdout.close()
                ok = x.wait() == 0; ok = (t.wait() == 0) and ok
            if ok: break
        else:
            die("building %s failed" % name)
        with open(out + "/arch/" + name[:-len(".tar.xz")] + ".MANIFEST.sha256", "w") as fh:
            fh.write("".join("%s  %s\n" % (shm(p), rel(p)) for p in L))
        sz = os.path.getsize(out + "/arch/" + name)
        if sz > GIT_MAX: die("%s is %d bytes (GitHub's limit is 100 MB): tell Claude" % (name, sz))
        built.append((name, len(L), sz))
    with open(out + "/ARCHIVES_BUILT.tsv", "w") as fh: fh.write("".join("%s\t%d\t%d\n" % b for b in built))
    with open(out + "/archives.tsv", "w") as fh:
        for (r, p, w) in cats["git_text"]:
            fh.write("%s/%s/hpc_text_outputs_%s.tar.xz\t%d\t%s\n" % (REL0, r, n, os.path.getsize(p), rel(p)))
    with open(out + "/individual.tsv", "w") as f1, open(out + "/INDIV.sha256", "w") as f2, \
         open(out + "/INDIV_XZ.sha256", "w") as f3:
        for (r, p, w) in cats["git_xz"]:
            q = out + "/indiv/" + rel(p) + ".xz"
            os.makedirs(os.path.dirname(q), exist_ok=True)
            xz_file(p, q)
            if os.path.getsize(q) > GIT_MAX: die("%s.xz is over 95 MB: tell Claude" % rel(p))
            f1.write("%d\t%s\t%s\n" % (os.path.getsize(p), rel(p), w))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
            f3.write("%s  %s.xz\n" % (sha(q), rel(p)))
    with open(out + "/as_is.tsv", "w") as f1, open(out + "/AS_IS.sha256", "w") as f2:
        for (r, p, w) in cats["git_asis"]:
            q = out + "/asis/" + rel(p)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copyfile(p, q)
            if sha(q) != shm(p): die("copying %s failed" % rel(p))
            f1.write("%d\t%s\n" % (os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
    with open(out + "/pc_keep.tsv", "w") as fh:
        for c in ("pc_keep", "scratch"):
            for (r, p, w) in cats[c]: fh.write("%s\t%d\t%s\t%s\n" % (w, os.path.getsize(p), rel(p), c))
    with open(out + "/links.tsv", "w") as fh:
        for (r, p, w) in cats["link"]: fh.write("%s\t%s\n" % (rel(p), os.readlink(p)))
    for r in want:                                   # the PC archive: every regular file of the run
        L = sorted(rel(p) for c in CATS if c != "link" for (q, p, w) in cats[c] if q == r)
        if L:
            with open(out + "/PCLIST_%s.txt" % r, "w") as fh: fh.write("".join(x + "\n" for x in L))
    with open(out + "/RUNS.txt", "w") as fh:
        for r in want: fh.write("%s\t%s\t%s\n" % (r, S[r][0], job_end(cd, r)))
    with open(out + "/SUMMARY.txt", "w") as fh:
        for c in CATS:
            L = cats[c]
            fh.write("%-9s %5d files %12d bytes\n" % (c, len(L), sum(size_or_none(p) or 0 for (r, p, w) in L)))
    shutil.rmtree(out + "/work")
    open(out + "/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "status": status(a[1])
    elif len(a) == 2 and a[0] == "files": files(a[1])
    elif len(a) >= 5 and a[0] == "stage": stage(a[1], a[2], a[3], a[4:])
    else: die("usage: status CD | files CD | stage CD OUT N RUN ...")
