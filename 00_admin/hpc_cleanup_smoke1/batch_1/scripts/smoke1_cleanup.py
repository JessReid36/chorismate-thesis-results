#!/usr/bin/env python3
"""
smoke1_cleanup.py - hpc1 side of the clean-up of SP smoke test 1 (05_qmmm/24_sp_barriers/f42436_r8 and f42436_r6,
exploratory since SP Amendment 1). Run by x76_smoke1.sh on the PC over ssh (python3 - MODE ...); Python 3.6, standard
library plus the qstat, qselect, tar and xz commands. It follows the 7 October 2026 clean-up (results
00_admin/hpc_cleanup_20261007): the outputs are committed first, with the sha256 of every file to be deleted, and
afterwards only files on that committed list whose sha256 still matches are deleted.

  status SD                         read-only: each job of both runs (SUBMITTED, qstat), each step's record, and what
                                    the clean-up would do with the files of every step whose job has ended
  stage SD OUT N STEP [STEP ...]    non-destructive (writes only in OUT): for the steps given as RUN/STEP (RUN/_run =
                                    the run folder's own files), all of whose jobs must have ended - text files in one
                                    tar.xz per run with a sha256 manifest of its members, text files over 50 MB
                                    compressed one by one, and the sha256 of every file to be deleted
  delete SD OUT EXPECT_DEL EXPECT_IND EXPECT_XZ
                                    deletes the files in OUT/DELETE_CHECKSUMS.sha256 and replaces those in
                                    OUT/INDIV.sha256 by their .xz copies, but only if the three lists are the committed
                                    ones (their sha256 = EXPECT_*), every staged .xz decompresses to its original, no
                                    listed file belongs to a job still in the queue, lies outside a step folder of the
                                    two runs or is a frequency Hessian, and each file's sha256 still matches its
                                    record. Logs every action as it is taken (OUT/DELETED.log), then OUT/REMAINING.tsv

What happens to each file of a staged step (by name, size and content, in this order):
  keep     links; frequency Hessians (*.hess in the *_freq and irc steps); the minimisations' own *.hess, if any;
           basis-set scratch (*.basN); any binary file of no known kind; an .xz over 95 MB or one that fails xz -t;
           a text file whose .xz already exists; a full-system trajectory without a matching activeRegion
           trajectory - neither committed nor deleted (sha256 recorded)
  as_is    files the job already compressed (*.xz, tested with xz -t): committed as they are, kept on hpc1
  delete   *.tmp, *.tmp.N, *.appr.hess, *.carthess, *.gbw, *.gbwN, *.densities, *.dcd, *.mdrestart; the TS searches'
           own Hessians (*.hess in the ts step); full-system trajectories (*_trj.xyz whose frames hold all 55680
           atoms) over 20 MB, only where the step's activeRegion trajectory holds at least as many complete frames
           and the step's start.xyz is there: ORCA moves no atom outside ActiveAtoms, so every frame is start.xyz
           with that frame's active atoms
  archive  every other text file, and the small binary *.densitiesinfo (archived on 7 October too): committed in the
           run's archive, kept on hpc1
  compress text files over 50 MB: committed as .xz; on hpc1 replaced by that same .xz when the deletion runs
Departures from 7 October (stated in each batch's README): full-system trajectories, the TS searches' own Hessians and
*.tmp.N files are deleted (7 October kept optimisation trajectories and every .hess but *.appr.hess, and its pattern
missed *.tmp.N); these TS searches ended without converging.
"""
import hashlib, os, re, shutil, subprocess, sys, time

RUNS = ("f42436_r8", "f42436_r6")
JOBS = (("job_ts", ("ts",)), ("job_ts_freq_irc", ("ts_freq", "irc")), ("job_r_irc", ("r_irc",)),
        ("job_r_irc_freq", ("r_irc_freq",)), ("job_p_irc", ("p_irc",)), ("job_p_irc_freq", ("p_irc_freq",)),
        ("job_r0", ("r0",)), ("job_r0_freq", ("r0_freq",)))
STEP_JOB = dict((s, j) for j, ss in JOBS for s in ss)
FIRST_STEP = dict((ss[0], j) for j, ss in JOBS)
STEPS = [s for j, ss in JOBS for s in ss]
NATOMS = 55680
MB = 1000000
ARCH_MAX, TRJ_MAX, GIT_MAX = 50 * MB, 20 * MB, 95 * MB
DELETE_RE = re.compile(r"(\.tmp|\.tmp\.[^/]*|\.appr\.hess|\.carthess|\.gbw\d*|\.densities|\.dcd|\.mdrestart)$")
REL0 = "05_qmmm/24_sp_barriers"
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
def root_of(sd):
    sd = os.path.abspath(sd)
    if not sd.endswith("/" + REL0): die("%s is not .../%s" % (sd, REL0))
    return sd[:-len(REL0) - 1]

# ---- jobs
def jobs_of(sd, run_):
    """job name -> id, from the run's SUBMITTED"""
    p = os.path.join(sd, run_, "SUBMITTED")
    if os.path.exists(os.path.join(sd, run_, "SUBMITTED.partial")): die("%s/SUBMITTED.partial exists" % run_)
    if not os.path.isfile(p): die("%s/SUBMITTED is missing" % run_)
    J = dict(l.split()[:2] for l in open(p) if l.strip())
    if sorted(J) != sorted(j for j, s in JOBS): die("%s/SUBMITTED does not list the eight jobs" % run_)
    return J
def qstat_f(jid):
    """(state, attributes) of one job: state 'ended' when PBS says it does not know it or that it has finished; any
    other qstat failure stops everything, so a job is never taken as ended because qstat could not be asked"""
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
def states(sd):
    """(run, job) -> (id, state). A job counts as active if its SUBMITTED id is in the queue, or if any job of this user
    still in the queue writes its output into one of the two run folders (whatever SUBMITTED says)"""
    S = {}
    for run_ in RUNS:
        J = jobs_of(sd, run_)
        for j, ss in JOBS: S[(run_, j)] = (J[j], qstat_f(J[j])[0])
    for jid in user_jobs():
        st, A = qstat_f(jid)
        if st == "ended": continue
        out = A.get("Output_Path", "").split(":", 1)[-1]
        for run_ in RUNS:
            d = os.path.join(sd, run_) + "/"
            if out.startswith(d):
                m = re.match(r"(job_\w+)\.pbs\.out$", out[len(d):])
                j = m.group(1) if m else None
                if j not in dict(JOBS): die("job %s writes %s, which is no job of %s" % (jid, out, run_))
                if S[(run_, j)][1] == "ended": S[(run_, j)] = (jid, st)
    return S

# ---- files
def is_binary(p):
    with open(p, "rb") as f: return b"\0" in f.read(1 << 20)
def first_int(p):
    with open(p, "rb") as f: l = f.readline(200).split()
    try: return int(l[0])
    except (IndexError, ValueError): return None
def nlines(p):
    n = 0
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): n += b.count(b"\n")
    return n
def xz_ok(p): return run(["xz", "-t", p]).returncode == 0
def classify(step, path):
    """(category, reason) for one file of a staged step"""
    n = os.path.basename(path); d = os.path.dirname(path)
    if os.path.islink(path): return "keep", "link"
    if not os.path.isfile(path): return "keep", "not a regular file: left in place"
    size = os.path.getsize(path)
    if n.endswith(".xz"):
        if size > GIT_MAX: return "keep", "an .xz over 95 MB: left in place"
        return ("as_is", "compressed by the job") if xz_ok(path) else ("keep", "an .xz that fails xz -t: left in place")
    if os.path.lexists(path + ".xz"): return "keep", "its .xz exists already: left in place"
    if DELETE_RE.search(n): return "delete", "scratch, approximate Hessian, wavefunction or densities"
    if re.search(r"\.bas\d+$", n): return "keep", "basis-set scratch, left in place as on 7 October"
    if n.endswith(".hess"):
        if step.endswith("_freq") or step == "irc": return "keep", "frequency Hessian"
        if step == "ts": return "delete", "the TS search's own Hessian"
        return "keep", "a minimisation's Hessian: left in place"
    if n.endswith("_trj.xyz") and first_int(path) == NATOMS and size > TRJ_MAX:
        act = os.path.join(d, n[:-len("_trj.xyz")] + ".activeRegion_trj.xyz")
        if not (os.path.isfile(act) and not os.path.islink(act) and os.path.isfile(os.path.join(d, "start.xyz"))):
            return "keep", "full-system trajectory without an activeRegion trajectory and start.xyz: left in place"
        na = first_int(act)
        if not na: return "keep", "full-system trajectory; its activeRegion trajectory is unreadable: left in place"
        ff, fa = nlines(path) // (NATOMS + 2), nlines(act) // (na + 2)
        if fa < ff: return "keep", "full-system trajectory with more frames (%d) than its activeRegion trajectory (%d): left in place" % (ff, fa)
        return "delete", "full-system trajectory over 20 MB (%d frames; the activeRegion trajectory holds %d)" % (ff, fa)
    if n.endswith(".densitiesinfo") and size <= MB: return "archive", "densities index (archived as on 7 October)"
    if is_binary(path): return "keep", "binary file of no known kind: left in place"
    return ("compress", "text over 50 MB") if size > ARCH_MAX else ("archive", "text")
def step_files(sd, run_, step):
    """the files of RUN/STEP (absolute paths); _run = the run folder's own files except job outputs"""
    rd = os.path.join(sd, run_)
    if os.path.islink(rd) or not os.path.isdir(rd): die("%s is a link or missing" % run_)
    if step == "_run":
        return sorted(os.path.join(rd, n) for n in os.listdir(rd)
                      if not os.path.isdir(os.path.join(rd, n)) and not re.match(r"job_\w+\.pbs\.out$", n))
    d = os.path.join(rd, step)
    if os.path.islink(d) or not os.path.isdir(d): die("%s/%s is a link or missing" % (run_, step))
    sub = [n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)) and not os.path.islink(os.path.join(d, n))]
    if sub: die("%s/%s holds folders (%s): not expected" % (run_, step, ", ".join(sub)))
    F = [os.path.join(d, n) for n in os.listdir(d)]
    if step in FIRST_STEP:                                                   # the job's output goes with its first step
        o = os.path.join(rd, FIRST_STEP[step] + ".pbs.out")
        if os.path.lexists(o): F.append(o)
    return sorted(F)
def size_or_none(p):
    try: return 0 if os.path.islink(p) else os.path.getsize(p)
    except FileNotFoundError: return None                                    # a running job removed it meanwhile
def step_record(sd, run_, step):
    p = os.path.join(sd, run_, step, "STAGE_RESULT.txt")
    if not os.path.isfile(p): return "no record"
    R = dict(l.rstrip("\n").split("=", 1) for l in open(p) if "=" in l)
    return R.get("status", "?") + ("" if "reason" not in R else ": " + R["reason"][:90])
def job_end(sd, run_, j):
    p = os.path.join(sd, run_, j + ".pbs.out")
    if not os.path.isfile(p): return "no job output"
    t = open(p, errors="replace").read()
    marks = [l.strip() for l in t.splitlines() if re.match(r"^\s*(SP_\S+_(PASS|FAIL)|=>> PBS:)", l)]
    return ("; ".join(marks[-3:]) or "no PASS/FAIL line") + ("" if "end_job=" in t else " (no end_job line)")
def gb(b): return "%.2f GB" % (b / 1e9)

def status(sd):
    S = states(sd)
    print("== jobs of smoke test 1 (SUBMITTED, qstat now)")
    for run_ in RUNS:
        for j, ss in JOBS:
            jid, st = S[(run_, j)]
            print("  %-10s %-16s %-18s %-6s %s" % (run_, j, jid, st, job_end(sd, run_, j)))
    print("== steps: record, and what the clean-up would do with their files if their job has ended")
    tot = {}; out = []
    for run_ in RUNS:
        for step in ["_run"] + STEPS:
            ended = step == "_run" or S[(run_, STEP_JOB[step])][1] == "ended"
            C = {}
            for p in step_files(sd, run_, step):
                s = size_or_none(p)
                if s is None: continue
                c, why = classify(step, p) if ended else ("not yet", "")
                for D in (C, tot): D.setdefault(c, [0, 0]); D[c][0] += 1; D[c][1] += s
                if c == "keep" and why not in ("link", "frequency Hessian"):
                    print("  KEEP %s/%s/%s (%s)" % (run_, step, os.path.basename(p), why))
            print("  %-10s %-11s %-34s %s" % (run_, step, step_record(sd, run_, step) if step != "_run" else "-",
                  "; ".join("%s %d (%s)" % (c, v[0], gb(v[1])) for c, v in sorted(C.items()))))
            out.append("STEPSTATE %s/%s %s" % (run_, step, "ended" if ended else "active"))
    print("== totals: " + "; ".join("%s %d files %s" % (c, v[0], gb(v[1])) for c, v in sorted(tot.items())))
    print("\n".join(out))

def stage(sd, out, n, steps):
    root = root_of(sd)
    if os.path.exists(out): die("%s exists" % out)
    S = states(sd)
    want = []
    for x in steps:
        run_, step = x.split("/")
        if run_ not in RUNS or (step != "_run" and step not in STEP_JOB): die("unknown step %s" % x)
        if step != "_run" and S[(run_, STEP_JOB[step])][1] != "ended":
            jid, st = S[(run_, STEP_JOB[step])]
            die("%s: job %s (%s) is still in the queue (%s)" % (x, STEP_JOB[step], jid, st))
        want.append((run_, step))
    rel = lambda p: os.path.relpath(p, root)
    cats = {"archive": [], "compress": [], "as_is": [], "delete": [], "keep": []}
    for run_, step in want:
        for p in step_files(sd, run_, step):
            c, why = classify(step, p)
            cats[c].append((run_, step, p, why))
    os.makedirs(out + "/work")
    try:
        build(sd, root, out, n, want, cats, S, rel)
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    print(open(out + "/SUMMARY.txt").read(), end="")
    for (r, s, p, w) in cats["keep"]:
        if w not in ("link", "frequency Hessian"): print("  kept on hpc1: %s (%s)" % (rel(p), w))
    print("staged in %s (nothing in %s was changed)" % (out, sd))

def build(sd, root, out, n, want, cats, S, rel):
    M = {}
    shm = lambda p: sha(p, M)
    staged = set(p for L in cats.values() for (r, s, p, w) in L)
    catof = dict((p, c) for c, L in cats.items() for (r, s, p, w) in L)
    with open(out + "/inventory.tsv", "w") as fh:            # every file of both run folders, all steps
        fh.write("# both run folders of smoke test 1, listed %s; size, mtime, path (relative to system_development), "
                 "category in batch %s (- = not in this batch), sha256 (batch files only; link target for links)\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), n))
        for run_ in RUNS:
            for dp, dn, fn in os.walk(os.path.join(sd, run_)):
                dn.sort()
                for f in sorted(fn):
                    p = os.path.join(dp, f)
                    if os.path.islink(p):
                        fh.write("0\t-\t%s\t%s\tlink:%s\n" % (rel(p), catof.get(p, "-"), os.readlink(p))); continue
                    try: st = os.stat(p)
                    except FileNotFoundError:
                        if p in staged: die("%s vanished while being staged" % rel(p))
                        continue                                         # a running job removed it meanwhile
                    fh.write("%d\t%s\t%s\t%s\t%s\n" % (st.st_size, time.strftime("%Y-%m-%dT%H:%M", time.localtime(st.st_mtime)),
                             rel(p), catof.get(p, "-"), shm(p) if p in staged else "-"))
    built = []                                                   # one archive per run, members relative to system_development
    for run_ in RUNS:
        L = [p for (r, s, p, w) in cats["archive"] if r == run_]
        if not L: continue
        name = "%s/%s/hpc_text_outputs_%s.tar.xz" % (REL0, run_, n)
        lst = out + "/work/list_" + run_
        with open(lst, "w") as fh: fh.write("".join(rel(p) + "\n" for p in L))
        os.makedirs(os.path.dirname(out + "/arch/" + name), exist_ok=True)
        for level in XZ_LEVELS:                                  # the login node limits memory: one thread
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
        fh.write("".join("%s/%s/hpc_text_outputs_%s.tar.xz\t%d\t%s\n" % (REL0, r, n, os.path.getsize(p), rel(p))
                         for (r, s, p, w) in cats["archive"]))
    with open(out + "/individual.tsv", "w") as f1, open(out + "/INDIV.sha256", "w") as f2, \
         open(out + "/INDIV_XZ.sha256", "w") as f3:                # text files over 50 MB, compressed one by one
        for (r, s, p, w) in cats["compress"]:
            q = out + "/indiv/" + rel(p) + ".xz"
            os.makedirs(os.path.dirname(q), exist_ok=True)
            for level in XZ_LEVELS:
                with open(q, "wb") as fo:
                    if subprocess.run(["xz", level, "-T1", "-c", p], stdout=fo).returncode == 0: break
            else:
                die("xz %s failed" % rel(p))
            if os.path.getsize(q) > GIT_MAX: die("%s.xz is over 95 MB: tell Claude" % rel(p))
            f1.write("%d\t%s\n" % (os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
            f3.write("%s  %s.xz\n" % (sha(q), rel(p)))
    with open(out + "/as_is.tsv", "w") as f1, open(out + "/AS_IS.sha256", "w") as f2:   # compressed by the jobs
        for (r, s, p, w) in cats["as_is"]:
            q = out + "/asis/" + rel(p)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copyfile(p, q)
            if sha(q) != shm(p): die("copying %s failed" % rel(p))
            f1.write("%d\t%s\n" % (os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
    with open(out + "/delete.tsv", "w") as f1, open(out + "/DELETE_CHECKSUMS.sha256", "w") as f2:
        for (r, s, p, w) in cats["delete"]:
            f1.write("%s\t%d\t%s\n" % (w, os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
    with open(out + "/keep.tsv", "w") as fh:
        for (r, s, p, w) in cats["keep"]:
            fh.write("%s\t%s\t%s\n" % (w, rel(p), ("link:" + os.readlink(p)) if os.path.islink(p) else shm(p)))
    with open(out + "/STEPS.txt", "w") as fh:
        for run_, step in want:
            jid, st = ("-", "-") if step == "_run" else S[(run_, STEP_JOB[step])]
            fh.write("%s/%s\t%s\t%s\t%s\n" % (run_, step, STEP_JOB.get(step, "-"), jid,
                                               step_record(sd, run_, step) if step != "_run" else "-"))
    with open(out + "/SUMMARY.txt", "w") as fh:
        for c in ("archive", "compress", "as_is", "delete", "keep"):
            L = cats[c]
            fh.write("%-8s %5d files %12d bytes\n" % (c, len(L), sum(size_or_none(p) or 0 for (r, s, p, w) in L)))
    rp = os.path.join(sd, "sp_report.py")       # smoke test 1's own report (read-only), whatever it prints
    if os.path.isfile(rp):
        try:
            r = subprocess.run([sys.executable, rp] + [os.path.join(sd, x) for x in RUNS], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=1800)
            rep, code = r.stdout.decode(errors="replace"), r.returncode
        except subprocess.TimeoutExpired:
            rep, code = "sp_report.py did not finish within 30 min\n", "timeout"
    else:
        rep, code = "sp_report.py not found in %s\n" % sd, "-"
    with open(out + "/SP_REPORT.txt", "w") as fh:
        fh.write("# python3 sp_report.py %s, run %s on hpc1, exit code %s (smoke test 1 as it stood; read-only)\n"
                 % (" ".join(RUNS), time.strftime("%Y-%m-%dT%H:%M:%S%z"), code) + rep)
    shutil.rmtree(out + "/work")
    open(out + "/DONE", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")

# ---- deletion
def xz_sha(q):
    """sha256 of the decompressed content of an .xz file, streamed"""
    h = hashlib.sha256()
    x = subprocess.Popen(["xz", "-dc", q], stdout=subprocess.PIPE)
    for b in iter(lambda: x.stdout.read(1 << 20), b""): h.update(b)
    return h.hexdigest() if x.wait() == 0 else None
LOCKMSG = ("%s/DELETE.lock exists: a deletion is running, or an earlier one was interrupted. Its actions so far are in "
           "DELETED.log; when no deletion is running, remove the lock (rm %s/DELETE.lock) and run delete again: it "
           "carries on from the log")
def read_checked(p, expect, what):
    """the list's lines, parsed from the very bytes whose sha256 is checked"""
    b = open(p, "rb").read()
    if hashlib.sha256(b).hexdigest() != expect: die("%s is not the committed one" % what)
    L = []
    for l in b.decode().splitlines():
        if not l: continue
        if l[64:66] != "  " or not re.match(r"^[0-9a-f]{64}$", l[:64]): die("%s: malformed line" % what)
        L.append((l[:64], l[66:]))
    return L
def delete(sd, out, expect_del, expect_ind, expect_xz):
    root = root_of(sd); rroot = os.path.realpath(root)
    if not os.path.isfile(out + "/DONE"): die("%s has no finished stage" % out)
    if os.path.exists(out + "/DELETE.done"): die("the deletion of %s has run already (DELETE.done)" % out)
    if os.path.exists(out + "/DELETE.lock"): die(LOCKMSG % (out, out))
    D = read_checked(out + "/DELETE_CHECKSUMS.sha256", expect_del, "DELETE_CHECKSUMS.sha256")
    I = read_checked(out + "/INDIV.sha256", expect_ind, "INDIV.sha256")
    XZ = dict((p[:-3], h) for h, p in read_checked(out + "/INDIV_XZ.sha256", expect_xz, "INDIV_XZ.sha256"))
    if set(p for h, p in I) != set(XZ): die("INDIV.sha256 and INDIV_XZ.sha256 list different files")
    S = states(sd)
    for h, p in D + I:                                           # every listed path: where it is, whose it is, what it is
        q = p.split("/")
        if len(q) != 5 or "/".join(q[:2]) != REL0 or q[2] not in RUNS or q[3] not in STEP_JOB or q[4] in ("", ".", ".."):
            die("listed path is not a file in a step folder of the two runs: " + p)
        if p.endswith(".hess") and (q[3].endswith("_freq") or q[3] == "irc"): die("a frequency Hessian is listed: " + p)
        a = os.path.join(root, p)
        if os.path.islink(a) or os.path.realpath(os.path.dirname(a)) != os.path.join(rroot, os.path.dirname(p)):
            die("listed path is a link or lies under a link: " + p)
        jid, st = S[(q[2], STEP_JOB[q[3]])]
        if st != "ended": die("%s belongs to %s (%s), still in the queue (%s)" % (p, STEP_JOB[q[3]], jid, st))
    done = {}                                                    # an interrupted run's log: carried on, not repeated
    if os.path.exists(out + "/DELETED.log"):
        for l in open(out + "/DELETED.log"):
            f = l.split()
            if f: done[f[-1]] = f[0]
    todo_i = [(h, p) for h, p in I if done.get(p) != "COMPRESSED"]
    for h, p in todo_i:                                          # every staged .xz checked before anything is removed
        a = os.path.join(root, p); q = out + "/indiv/" + p + ".xz"
        if os.path.lexists(a) and sha(a) == h and not os.path.lexists(a + ".xz"):
            if sha(q) != XZ[p]: die("the staged %s.xz is not the committed one (nothing was deleted by this run)" % p)
            if xz_sha(q) != h: die("the staged %s.xz does not decompress to the original (nothing was deleted by this run)" % p)
    try:                                                         # nothing is removed without the lock
        lock = os.open(out + "/DELETE.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        die(LOCKMSG % (out, out))
    os.write(lock, (time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n").encode()); os.close(lock)
    log = open(out + "/DELETED.log", "a")
    def note(line):
        log.write(line + "\n"); log.flush(); os.fsync(log.fileno())
    n = c = skip = 0; freed = 0
    for h, p in D:
        if done.get(p) == "DELETED": continue
        a = os.path.join(root, p)
        if not os.path.lexists(a): note("ABSENT %s" % p); continue
        if sha(a) != h: note("SKIPPED_CHANGED %s" % p); skip += 1; continue
        s = os.path.getsize(a); os.remove(a); note("DELETED %d %s" % (s, p)); n += 1; freed += s
    for h, p in todo_i:
        a = os.path.join(root, p); q = out + "/indiv/" + p + ".xz"
        if not os.path.lexists(a): note("ABSENT %s" % p); continue
        if sha(a) != h: note("SKIPPED_CHANGED %s" % p); skip += 1; continue
        if os.path.lexists(a + ".xz"): note("SKIPPED_XZ_EXISTS %s" % p); skip += 1; continue
        shutil.copyfile(q, a + ".xz.part")
        if sha(a + ".xz.part") != XZ[p]: os.remove(a + ".xz.part"); die("copying %s.xz failed" % p)
        os.rename(a + ".xz.part", a + ".xz")
        s = os.path.getsize(a); os.remove(a); note("COMPRESSED %d %s" % (s, p)); c += 1
        freed += s - os.path.getsize(a + ".xz")
    log.close()
    with open(out + "/REMAINING.tsv.part", "w") as fh:
        for run_ in RUNS:
            for dp, dn, fn in os.walk(os.path.join(sd, run_)):
                dn.sort()
                for f in sorted(fn):
                    p = os.path.join(dp, f)
                    s = "link" if os.path.islink(p) else size_or_none(p)
                    if s is not None: fh.write("%s\t%s\n" % (s, os.path.relpath(p, root)))
    os.rename(out + "/REMAINING.tsv.part", out + "/REMAINING.tsv")
    open(out + "/DELETE.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")
    os.remove(out + "/DELETE.lock")
    print("deleted %d files, compressed %d outputs in place, %s freed by this run; skipped (changed since recorded) %d; "
          "see %s/DELETED.log" % (n, c, gb(freed), skip, out))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "status": status(a[1])
    elif len(a) >= 5 and a[0] == "stage": stage(a[1], a[2], a[3], a[4:])
    elif len(a) == 6 and a[0] == "delete": delete(a[1], a[2], a[3], a[4], a[5])
    else: die("usage: status SD | stage SD OUT N RUN/STEP ... | delete SD OUT EXPECT_DEL EXPECT_IND EXPECT_XZ")
