#!/usr/bin/env python3
"""
sp_cleanup.py - hpc1 side of x77: the outputs of the SP runs of 05_qmmm/24_sp_barriers - smoke test 1 (f42436_r8,
f42436_r6; exploratory since SP Amendment 1) and smoke test 2 (f42436_r8_a1, f42436_r6_a1; SP Amendment 1) - kept as
physical files before anything is removed from hpc1. Run by x77_sp.sh on the PC over ssh (python3 - MODE ...); Python
3.6, standard library plus the qstat, qselect, tar and xz commands. Replaces x76's smoke1_cleanup.py (batch 1 stays as
x76 made it).

THE RULE (Jessica, 18 October 2026): every output file of a finished step is downloaded and kept as a physical file,
not only reported. Here that means:
  1. every regular file of every staged step goes into a PC archive (x77_sp.sh fetches it and checks each file's
     sha256 against this script's inventory before anything is committed or deleted);
  2. the results repo gets the readable outputs, geometries, Hessians and final wavefunctions themselves, plus the
     sha256 of every file in the PC archive;
  3. a file is removed from hpc1 only after (1) and (2), and only if it is scratch or a working file (below); nothing
     is left only on hpc1, and anything unexpected (below) stops the staging instead of being skipped.

  status SD                     read-only: each job of the four runs (SUBMITTED, qstat), each step's record, and what
                                would happen to the files of every step whose job has ended
  files SD                      read-only: every file and link of the four runs (size and mtime, or "link"), and any folder
                                named after one of them that is not one of them (RUN_..., e.g. SP_AMENDMENT1 A1.5's
                                RUN_stop1); x77_sp.sh checks these against the batches, so that no file is missed
  stage SD OUT N ITEM [...]     non-destructive (writes only in OUT): ITEM = RUN/STEP (RUN/_run = the run folder's own
                                files), whose job must have ended, or +PATH=SHA256 (a file of an earlier batch that x76
                                left on hpc1, staged again with this batch; its sha256 must still be the recorded one)
  delete SD OUT EXPECT_DEL EXPECT_IND EXPECT_XZ EXPECT_STEPS
                                deletes the files in OUT/DELETE_CHECKSUMS.sha256, and replaces by its committed .xz copy
                                each file in OUT/INDIV.sha256 that is text over 50 MB in a step folder and no Hessian
                                (the others there - final wavefunctions, Hessians, job outputs - stay as they are) - only
                                if the four lists (with OUT/STEPS.txt) are the committed ones (sha256 = EXPECT_*), every
                                staged .xz to be used decompresses to its original, every file acted on lies in a step of
                                this batch whose job is the one the batch recorded (not a run folder generated again,
                                SP_AMENDMENT1 A1.5) and has ended, every file to delete is of a deletable kind and no
                                step's final wavefunction, and each file's sha256 still matches. Logs each action as it is taken (OUT/DELETED.log), then
                                lists what is left (OUT/REMAINING.tsv). x77_sp.sh checks the PC archives against their
                                committed sha256, and that every listed file is in them, before it calls this.

What happens to each file of a staged step (every regular file also goes into the PC archive):
  git_text   text up to 50 MB: committed in one tar.xz per run and step, with a sha256 manifest; stays on hpc1.
             Includes ORCA outputs and inputs, geometries (.xyz, .pdb), QM-region trajectories, Hessians (*.hess, all
             steps), gradients, optimiser and property files, CSV energies, records, job outputs, basis-set files
  git_xz     text over 50 MB, and the wavefunction and densities of each step's final state (*.gbw, *.densities of a
             non-alternation step; of the final cycle's core step in an alternation: the record's cycles=K, or for a step
             without that record the highest-numbered core step that passed): committed as .xz; on hpc1 a text file over
             50 MB in a step folder (no Hessian) is replaced by that same .xz at deletion, everything else stays as it is
  git_asis   files the job already compressed (*.xz up to 95 MB, passing xz -t): committed as they are; stay on hpc1
  pc_keep    on the PC (archive) and in the manifest, not in git; stay on hpc1: active-region trajectories
             (*.activeRegion_trj.xyz, also as the job compressed them; too large for git in number), full-system
             trajectories over 20 MB, MD-format files (*.dcd, *.mdrestart), binary files of no other kind, a job's .xz
             over 95 MB
  pc_delete  on the PC (archive) and in the manifest, then deleted on hpc1 - scratch and working files only: ORCA
             scratch (*.tmp, *.tmp.N), the optimiser's working Hessians (*.appr.hess, *.carthess), and the wavefunctions
             and densities of intermediate states (*.gbw, *.gbwN, *.densities not covered by git_xz; SCF restart files)
  link       symbolic links (the force field): recorded with their target and the target's sha256
Text of no other kind goes to git_text (or git_xz over 50 MB). What stops the staging: a non-regular file, an .xz
failing xz -t, a file next to its own .xz, a git file over 95 MB after compression; a step folder may hold only cycle
folders cKK_env / cKK_core, and only in an alternation step of a smoke-test-2 run.
"""
import hashlib, os, re, shutil, subprocess, sys, time

RUNS = ("f42436_r8", "f42436_r6", "f42436_r8_a1", "f42436_r6_a1")
A1_RUNS = ("f42436_r8_a1", "f42436_r6_a1")
JOBS = (("job_ts", ("ts",)), ("job_ts_freq_irc", ("ts_freq", "irc")), ("job_r_irc", ("r_irc",)),
        ("job_r_irc_freq", ("r_irc_freq",)), ("job_p_irc", ("p_irc",)), ("job_p_irc_freq", ("p_irc_freq",)),
        ("job_r0", ("r0",)), ("job_r0_freq", ("r0_freq",)))
ALT = ("ts", "r_irc", "p_irc", "r0")                    # the alternations of SP Amendment 1 (smoke-test-2 runs)
STEP_JOB = dict((s, j) for j, ss in JOBS for s in ss)
FIRST_STEP = dict((ss[0], j) for j, ss in JOBS)
STEPS = [s for j, ss in JOBS for s in ss]
CYC_RE = re.compile(r"^c\d\d_(env|core)$")
NATOMS = 55680
MB = 1000000
ARCH_MAX, TRJ_MAX, GIT_MAX = 50 * MB, 20 * MB, 95 * MB
SCRATCH_RE = re.compile(r"(\.tmp|\.tmp\.[^/]*)$")
WORKHESS_RE = re.compile(r"(\.appr\.hess|\.carthess)$")
WFN_RE = re.compile(r"(\.gbw\d*|\.densities)$")
MDFMT_RE = re.compile(r"(\.dcd|\.mdrestart)$")
CATS = ("git_text", "git_xz", "git_asis", "pc_keep", "pc_delete", "link")
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
    still in the queue writes its output into one of the four run folders (whatever SUBMITTED says)"""
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
def xz_ok(p): return run(["xz", "-t", p]).returncode == 0
def record(sd, run_, step):
    p = os.path.join(sd, run_, step, "STAGE_RESULT.txt")
    if not os.path.isfile(p): return {}
    return dict(l.rstrip("\n").split("=", 1) for l in open(p) if "=" in l)
def final_core(sd, run_, step):
    """the cycle folder of an alternation's final state: cKK_core with K = the record's cycles (a converged step); for a
    step without that record the highest-numbered core folder whose own record says status=PASS, or failing that the
    highest-numbered core folder present; None outside the alternations"""
    if run_ not in A1_RUNS or step not in ALT: return None
    k = record(sd, run_, step).get("cycles", "")
    if k.isdigit(): return "c%02d_core" % int(k)
    d = os.path.join(sd, run_, step)
    C = sorted(n for n in os.listdir(d) if re.match(r"^c\d\d_core$", n)) if os.path.isdir(d) else []
    P = [c for c in C if record(sd, run_, os.path.join(step, c)).get("status") == "PASS"]
    return P[-1] if P else (C[-1] if C else None)
def step_files(sd, run_, step):
    """the files of RUN/STEP (absolute paths; in an alternation also those of its cycle folders); _run = the run
    folder's own files except job outputs; the job's output goes with its first step"""
    rd = os.path.join(sd, run_)
    if os.path.islink(rd) or not os.path.isdir(rd): die("%s is a link or missing" % run_)
    if step == "_run":
        return sorted(os.path.join(rd, n) for n in os.listdir(rd)
                      if not os.path.isdir(os.path.join(rd, n)) and not re.match(r"job_\w+\.pbs\.out$", n))
    d = os.path.join(rd, step)
    if os.path.islink(d) or not os.path.isdir(d): die("%s/%s is a link or missing" % (run_, step))
    F = []
    for n in sorted(os.listdir(d)):
        p = os.path.join(d, n)
        if os.path.isdir(p) and not os.path.islink(p):
            if not (run_ in A1_RUNS and step in ALT and CYC_RE.match(n)):
                die("%s/%s holds the folder %s: not expected" % (run_, step, n))
            for m in sorted(os.listdir(p)):
                q = os.path.join(p, m)
                if os.path.isdir(q) and not os.path.islink(q): die("%s/%s/%s holds the folder %s: not expected" % (run_, step, n, m))
                F.append(q)
        else:
            F.append(p)
    if step in FIRST_STEP:
        o = os.path.join(rd, FIRST_STEP[step] + ".pbs.out")
        if os.path.lexists(o): F.append(o)
    return sorted(F)
def classify(sd, run_, step, path, fin):
    """(category, reason) for one file of a staged step; fin = final_core(...) of that step"""
    n = os.path.basename(path); d = os.path.dirname(path)
    if os.path.islink(path): return "link", "link"
    if not os.path.isfile(path): die("%s is not a regular file: tell Claude" % path)
    size = os.path.getsize(path)
    if n.endswith(".activeRegion_trj.xyz.xz"):
        if not xz_ok(path): die("%s fails xz -t: tell Claude" % path)
        return "pc_keep", "active-region trajectory as the job compressed it (PC archive only)"
    if n.endswith(".xz"):
        if not xz_ok(path): die("%s fails xz -t: tell Claude" % path)
        if size > GIT_MAX: return "pc_keep", "a job's .xz over 95 MB (PC archive only)"
        return "git_asis", "compressed by the job"
    if os.path.lexists(path + ".xz"): die("%s and its .xz both exist: tell Claude" % path)
    if SCRATCH_RE.search(n): return "pc_delete", "ORCA scratch"
    if WORKHESS_RE.search(n): return "pc_delete", "the optimiser's working Hessian"
    if MDFMT_RE.search(n): return "pc_keep", "MD-format trajectory or restart (PC archive only)"
    if WFN_RE.search(n):
        cyc = os.path.basename(d) if CYC_RE.match(os.path.basename(d)) else None
        final = re.search(r"\.(gbw|densities)$", n) and (cyc is None or cyc == fin)
        if final: return "git_xz", "wavefunction or densities of the step's final state"
        return "pc_delete", "wavefunction or densities of an intermediate state"
    if n.endswith(".activeRegion_trj.xyz"): return "pc_keep", "active-region trajectory (PC archive only)"
    if n.endswith("_trj.xyz") and not n.endswith(".QMRegion_trj.xyz") and first_int(path) == NATOMS and size > TRJ_MAX:
        return "pc_keep", "full-system trajectory over 20 MB (PC archive only)"
    if n.endswith(".densitiesinfo") and size <= MB: return "git_text", "densities index"
    if is_binary(path): return "pc_keep", "binary file of no other kind (PC archive only)"
    return ("git_xz", "text over 50 MB") if size > ARCH_MAX else ("git_text", "text")
def size_or_none(p):
    try: return 0 if os.path.islink(p) else os.path.getsize(p)
    except FileNotFoundError: return None                                    # a running job removed it meanwhile
def step_record(sd, run_, step):
    R = record(sd, run_, step)
    if not R: return "no record"
    return R.get("status", "?") + ("" if "reason" not in R else ": " + R["reason"][:90])
def job_end(sd, run_, j):
    p = os.path.join(sd, run_, j + ".pbs.out")
    if not os.path.isfile(p): return "no job output"
    t = open(p, errors="replace").read()
    marks = [l.strip() for l in t.splitlines() if re.match(r"^\s*(SP_\S+_(PASS|FAIL)|=>> PBS:)", l)]
    return ("; ".join(marks[-3:]) or "no PASS/FAIL line") + ("" if "end_job=" in t else " (no end_job line)")
def gb(b): return "%.2f GB" % (b / 1e9)
def rel_ok(p):
    """a path relative to system_development that names a file (or a file of a cycle folder) in a step folder of the
    four runs: (run, step, cycle folder or None)"""
    q = p.split("/")
    if "/".join(q[:2]) != REL0 or len(q) not in (5, 6) or q[2] not in RUNS or q[3] not in STEP_JOB: return None
    if any(x in ("", ".", "..") for x in q): return None
    if len(q) == 6:
        if not (q[2] in A1_RUNS and q[3] in ALT and CYC_RE.match(q[4])): return None
        return q[2], q[3], q[4]
    return q[2], q[3], None

def files(sd):
    root = root_of(sd)
    for run_ in RUNS:
        rd = os.path.join(sd, run_)
        if os.path.islink(rd) or not os.path.isdir(rd): die("%s is a link or missing" % run_)
        for dp, dn, fn in os.walk(rd):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                if os.path.islink(p): print("F\t%s\tlink\t-" % os.path.relpath(p, root)); continue
                try: st = os.stat(p)
                except FileNotFoundError: continue
                print("F\t%s\t%d\t%s" % (os.path.relpath(p, root), st.st_size,
                                          time.strftime("%Y-%m-%dT%H:%M", time.localtime(st.st_mtime))))
    for n in sorted(os.listdir(sd)):
        if n not in RUNS and any(n.startswith(r + "_") for r in RUNS): print("D\t%s" % n)

def status(sd):
    S = states(sd)
    print("== jobs of the four runs (SUBMITTED, qstat now)")
    for run_ in RUNS:
        for j, ss in JOBS:
            jid, st = S[(run_, j)]
            print("  %-13s %-16s %-18s %-6s %s" % (run_, j, jid, st, job_end(sd, run_, j)))
    print("== steps: record, and what would happen to their files if their job has ended (every file also goes to the PC)")
    tot = {}; out = []
    for run_ in RUNS:
        for step in ["_run"] + STEPS:
            ended = step == "_run" or S[(run_, STEP_JOB[step])][1] == "ended"
            fin = final_core(sd, run_, step) if step != "_run" else None
            C = {}
            for p in step_files(sd, run_, step):
                s = size_or_none(p)
                if s is None: continue
                c, why = classify(sd, run_, step, p, fin) if ended else ("not yet", "")
                for D in (C, tot): D.setdefault(c, [0, 0]); D[c][0] += 1; D[c][1] += s
            print("  %-13s %-11s %-30s %s" % (run_, step, step_record(sd, run_, step) if step != "_run" else "-",
                  "; ".join("%s %d (%s)" % (c, v[0], gb(v[1])) for c, v in sorted(C.items()))))
            out.append("STEPSTATE %s/%s %s" % (run_, step, "ended" if ended else "active"))
    print("== totals: " + "; ".join("%s %d files %s" % (c, v[0], gb(v[1])) for c, v in sorted(tot.items())))
    print("\n".join(out))

def stage(sd, out, n, items):
    root = root_of(sd)
    if os.path.exists(out): die("%s exists" % out)
    S = states(sd)
    want, extra = [], []
    for x in items:
        if x.startswith("+"):
            p, h = x[1:].rsplit("=", 1)
            t = rel_ok(p)
            if not t: die("an earlier batch's file outside a step folder of the four runs: " + p)
            a = os.path.join(root, p)
            if os.path.islink(a) or not os.path.isfile(a): die("%s is missing or not a regular file" % p)
            if sha(a) != h: die("%s has changed since its batch recorded it" % p)
            jid, st = S[(t[0], STEP_JOB[t[1]])]
            if st != "ended": die("%s belongs to %s (%s), still in the queue (%s)" % (p, STEP_JOB[t[1]], jid, st))
            extra.append((t[0], t[1], a))
            continue
        run_, step = x.split("/")
        if run_ not in RUNS or (step != "_run" and step not in STEP_JOB): die("unknown step %s" % x)
        if step != "_run" and S[(run_, STEP_JOB[step])][1] != "ended":
            jid, st = S[(run_, STEP_JOB[step])]
            die("%s: job %s (%s) is still in the queue (%s)" % (x, STEP_JOB[step], jid, st))
        want.append((run_, step))
    rel = lambda p: os.path.relpath(p, root)
    cats = dict((c, []) for c in CATS)
    seen = set()
    for run_, step in want:
        fin = final_core(sd, run_, step) if step != "_run" else None
        for p in step_files(sd, run_, step):
            c, why = classify(sd, run_, step, p, fin)
            cats[c].append((run_, step, p, why)); seen.add(p)
    for run_, step, p in extra:
        if p in seen: die("%s is both in a staged step and an earlier batch's file" % rel(p))
        c, why = classify(sd, run_, step, p, final_core(sd, run_, step))
        if c in ("pc_delete", "link"): die("%s from an earlier batch would be %s: tell Claude" % (rel(p), c))
        cats[c].append((run_, "+extra", p, why + " (left on hpc1 by an earlier batch)")); seen.add(p)
    need = sum(size_or_none(p) or 0 for c in ("git_text", "git_xz", "git_asis") for (r, s, p, w) in cats[c]) + 2 * 10**9
    vfs = os.statvfs(os.path.dirname(os.path.abspath(out)))
    if vfs.f_bavail * vfs.f_frsize < need:
        die("the stage needs up to %s and %s has only %s free" % (gb(need), os.path.dirname(out), gb(vfs.f_bavail * vfs.f_frsize)))
    os.makedirs(out + "/work")
    try:
        build(sd, root, out, n, want, extra, cats, S, rel)
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    print(open(out + "/SUMMARY.txt").read(), end="")
    print("staged in %s (nothing in %s was changed)" % (out, sd))

def xz_file(src, dst):
    for level in XZ_LEVELS:                                          # the login node limits memory: one thread
        with open(dst, "wb") as fo:
            if subprocess.run(["xz", level, "-T1", "-c", src], stdout=fo).returncode == 0: return
    die("xz %s failed" % src)

def build(sd, root, out, n, want, extra, cats, S, rel):
    M = {}
    shm = lambda p: sha(p, M)
    staged = set(p for L in cats.values() for (r, s, p, w) in L)
    catof = dict((p, c) for c, L in cats.items() for (r, s, p, w) in L)
    with open(out + "/inventory.tsv", "w") as fh:            # every file of the four run folders
        fh.write("# the four SP run folders, listed %s; size, mtime, path (relative to system_development), category in "
                 "batch %s (- = not in this batch), sha256 (batch files; for a link: link:TARGET:SHA256 of the target)\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), n))
        for run_ in RUNS:
            for dp, dn, fn in os.walk(os.path.join(sd, run_)):
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
    # git text: one tar.xz per run and step (the earlier batches' files: per run, "extra")
    built = []; groups = {}
    for (r, s, p, w) in cats["git_text"]:
        groups.setdefault((r, "extra" if s == "+extra" else ("run" if s == "_run" else s)), []).append(p)
    for (r, s), L in sorted(groups.items()):
        name = "%s/%s/hpc_text_outputs_%s_%s.tar.xz" % (REL0, r, n, s)
        lst = out + "/work/list_%s_%s" % (r, s)
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
        for (r, s, p, w) in cats["git_text"]:
            g = "extra" if s == "+extra" else ("run" if s == "_run" else s)
            fh.write("%s/%s/hpc_text_outputs_%s_%s.tar.xz\t%d\t%s\n" % (REL0, r, n, g, os.path.getsize(p), rel(p)))
    # git, one by one: text over 50 MB, final wavefunctions and densities
    with open(out + "/individual.tsv", "w") as f1, open(out + "/INDIV.sha256", "w") as f2, \
         open(out + "/INDIV_XZ.sha256", "w") as f3:
        for (r, s, p, w) in cats["git_xz"]:
            q = out + "/indiv/" + rel(p) + ".xz"
            os.makedirs(os.path.dirname(q), exist_ok=True)
            xz_file(p, q)
            if os.path.getsize(q) > GIT_MAX: die("%s.xz is over 95 MB: tell Claude" % rel(p))
            f1.write("%d\t%s\t%s\n" % (os.path.getsize(p), rel(p), w))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
            f3.write("%s  %s.xz\n" % (sha(q), rel(p)))
    with open(out + "/as_is.tsv", "w") as f1, open(out + "/AS_IS.sha256", "w") as f2:   # compressed by the jobs
        for (r, s, p, w) in cats["git_asis"]:
            q = out + "/asis/" + rel(p)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copyfile(p, q)
            if sha(q) != shm(p): die("copying %s failed" % rel(p))
            f1.write("%d\t%s\n" % (os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
    with open(out + "/delete.tsv", "w") as f1, open(out + "/DELETE_CHECKSUMS.sha256", "w") as f2:
        for (r, s, p, w) in cats["pc_delete"]:
            f1.write("%s\t%d\t%s\n" % (w, os.path.getsize(p), rel(p)))
            f2.write("%s  %s\n" % (shm(p), rel(p)))
    with open(out + "/pc_keep.tsv", "w") as fh:
        for (r, s, p, w) in cats["pc_keep"]: fh.write("%s\t%d\t%s\n" % (w, os.path.getsize(p), rel(p)))
    with open(out + "/links.tsv", "w") as fh:
        for (r, s, p, w) in cats["link"]: fh.write("%s\t%s\n" % (rel(p), os.readlink(p)))
    # the PC archive: every regular file of the batch, one list per run (x77_sp.sh streams each with tar)
    for run_ in RUNS:
        L = sorted(rel(p) for c in CATS if c != "link" for (r, s, p, w) in cats[c] if r == run_)
        if L:
            with open(out + "/PCLIST_%s.txt" % run_, "w") as fh: fh.write("".join(x + "\n" for x in L))
    with open(out + "/STEPS.txt", "w") as fh:
        for run_, step in want:
            jid, st = ("-", "-") if step == "_run" else S[(run_, STEP_JOB[step])]
            fh.write("%s/%s\t%s\t%s\t%s\n" % (run_, step, STEP_JOB.get(step, "-"), jid,
                                               step_record(sd, run_, step) if step != "_run" else "-"))
    with open(out + "/EXTRAS.txt", "w") as fh:
        for run_, step, p in extra: fh.write("%s\t%s\n" % (rel(p), catof[p]))
    with open(out + "/SUMMARY.txt", "w") as fh:
        for c in CATS:
            L = cats[c]
            fh.write("%-9s %5d files %12d bytes\n" % (c, len(L), sum(size_or_none(p) or 0 for (r, s, p, w) in L)))
    for script, runs, fname, extra_args in (("sp_report.py", ("f42436_r8", "f42436_r6"), "SP_REPORT.txt", None),
                                            ("spa_report.py", A1_RUNS, "SPA_REPORT.txt", ["smoke", sd, "42436"])):
        rp = os.path.join(sd, script)                  # the runs' own read-only reports, whatever they print
        txt = ""
        for args in ([os.path.join(sd, x) for x in runs],) + ((extra_args,) if extra_args else ()):
            if os.path.isfile(rp):
                try:
                    r = subprocess.run([sys.executable, rp] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1800)
                    rep, code = r.stdout.decode(errors="replace"), r.returncode
                except subprocess.TimeoutExpired:
                    rep, code = "%s did not finish within 30 min\n" % script, "timeout"
            else:
                rep, code = "%s not found in %s\n" % (script, sd), "-"
            txt += "# python3 %s %s, run %s on hpc1, exit code %s (read-only)\n" % (
                script, " ".join(os.path.relpath(a, sd) if a.startswith(sd + "/") else a for a in args),
                time.strftime("%Y-%m-%dT%H:%M:%S%z"), code) + rep
        open(out + "/" + fname, "w").write(txt)
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
def deletable(p):
    """only these kinds may be removed from hpc1: scratch and working files"""
    n = os.path.basename(p)
    return bool(SCRATCH_RE.search(n) or WORKHESS_RE.search(n) or WFN_RE.search(n))
def replaceable(p):
    """a git_xz file that is replaced by its .xz on hpc1: text over 50 MB in a step folder, no Hessian; the final
    wavefunctions and densities, Hessians and job outputs stay as they are"""
    n = os.path.basename(p)
    return bool(rel_ok(p)) and not WFN_RE.search(n) and not n.endswith(".hess")
def delete(sd, out, expect_del, expect_ind, expect_xz, expect_steps):
    root = root_of(sd); rroot = os.path.realpath(root)
    if not os.path.isfile(out + "/DONE"): die("%s has no finished stage" % out)
    if os.path.exists(out + "/DELETE.done"): die("the deletion of %s has run already (DELETE.done)" % out)
    if os.path.exists(out + "/DELETE.lock"): die(LOCKMSG % (out, out))
    D = read_checked(out + "/DELETE_CHECKSUMS.sha256", expect_del, "DELETE_CHECKSUMS.sha256")
    I = read_checked(out + "/INDIV.sha256", expect_ind, "INDIV.sha256")
    XZ = dict((p[:-3], h) for h, p in read_checked(out + "/INDIV_XZ.sha256", expect_xz, "INDIV_XZ.sha256"))
    if set(p for h, p in I) != set(XZ): die("INDIV.sha256 and INDIV_XZ.sha256 list different files")
    b = open(out + "/STEPS.txt", "rb").read()                    # RUN/STEP, job, job id, record - as staged
    if hashlib.sha256(b).hexdigest() != expect_steps: die("STEPS.txt is not the committed one")
    SJ = dict((r.split("\t")[0], r.split("\t")[2]) for r in b.decode().splitlines() if r.count("\t") >= 3)
    S = states(sd)
    R = [(h, p) for h, p in I if replaceable(p)]
    for h, p in D + R:                                           # every path acted on: where it is, whose it is, what it is
        t = rel_ok(p)
        if not t: die("listed path is not a file in a step folder of the four runs: " + p)
        a = os.path.join(root, p)
        if os.path.islink(a) or os.path.realpath(os.path.dirname(a)) != os.path.join(rroot, os.path.dirname(p)):
            die("listed path is a link or lies under a link: " + p)
        key = "%s/%s" % (t[0], t[1])
        if key not in SJ: die("%s is not in a step of this batch (STEPS.txt)" % p)
        jid, st = S[(t[0], STEP_JOB[t[1]])]
        if jid != SJ[key]:
            die("%s's job is now %s, but the batch recorded %s: the run folder was generated again since the batch was "
                "staged (SP_AMENDMENT1 A1.5?). Nothing was deleted: tell Claude" % (key, jid, SJ[key]))
        if st != "ended": die("%s belongs to %s (%s), still in the queue (%s)" % (p, STEP_JOB[t[1]], jid, st))
    for h, p in D:
        if not deletable(p): die("a file of a kind that is never deleted is on the deletion list: " + p)
        if rel_ok(p)[2] is None and re.search(r"\.(gbw|densities)$", p): die("a step's final wavefunction is on the deletion list: " + p)
    done = {}                                                    # an interrupted run's log: carried on, not repeated
    if os.path.exists(out + "/DELETED.log"):
        for l in open(out + "/DELETED.log"):
            f = l.split()
            if f: done[f[-1]] = f[0]
    todo_i = [(h, p) for h, p in R if done.get(p) != "COMPRESSED"]
    for h, p in todo_i:                                          # every staged .xz checked before anything is removed
        a = os.path.join(root, p); q = out + "/indiv/" + p + ".xz"
        if os.path.lexists(a) and sha(a) == h:
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
        if os.path.lexists(a + ".xz"):
            if not os.path.islink(a + ".xz") and sha(a + ".xz") == XZ[p]:    # an interrupted run placed it: finish that
                s = os.path.getsize(a); os.remove(a); note("COMPRESSED %d %s" % (s, p)); c += 1
                freed += s - os.path.getsize(a + ".xz"); continue
            note("SKIPPED_XZ_EXISTS %s" % p); skip += 1; continue
        shutil.copyfile(q, a + ".xz.part")
        if sha(a + ".xz.part") != XZ[p]: os.remove(a + ".xz.part"); die("copying %s.xz failed" % p)
        os.rename(a + ".xz.part", a + ".xz")
        s = os.path.getsize(a); os.remove(a); note("COMPRESSED %d %s" % (s, p)); c += 1
        freed += s - os.path.getsize(a + ".xz")
    for h, p in I:
        if not replaceable(p) and done.get(p) != "KEPT": note("KEPT %s" % p)          # committed as .xz, stays as it is
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
    print("deleted %d files, compressed %d files in place, %s freed by this run; skipped (changed since recorded) %d; "
          "see %s/DELETED.log" % (n, c, gb(freed), skip, out))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "status": status(a[1])
    elif len(a) == 2 and a[0] == "files": files(a[1])
    elif len(a) >= 5 and a[0] == "stage": stage(a[1], a[2], a[3], a[4:])
    elif len(a) == 7 and a[0] == "delete": delete(a[1], a[2], a[3], a[4], a[5], a[6])
    else: die("usage: status SD | files SD | stage SD OUT N ITEM ... | delete SD OUT EXPECT_DEL EXPECT_IND EXPECT_XZ EXPECT_STEPS")
