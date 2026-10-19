#!/usr/bin/env python3
"""
pkg_waves.py - the SP package's submission in waves (05_qmmm/24_sp_barriers/SP_AMENDMENT2.txt A2.10). Runs on hpc1,
sent by x84 from the PC. Python 3.6, standard library, plus df, stat, du, ps, quota (lfs on Lustre), qselect, qstat and
each run folder's submit.sh (qsub).

  status                       read-only (from standard input: python3 -I -u - status): each run folder's state and its
                               jobs' PBS states, the waves so far, the free disk and the quota where SD is, PBS's limits
                               and queues, and whether and how big the next wave is. Exit 0
  submit SCRIPT_SHA RUN=SHA... (from a file whose sha256 is SCRIPT_SHA) the same, then the next wave if it may go now;
                               each RUN=SHA is the sha256 of that run folder's committed GENERATOR_LOG.txt, and a run
                               folder is submitted only if its log has that sha256, every file and link the log records
                               is as recorded, and nothing else is in the folder but DO_NOT_SUBMIT. Exit 0: a wave was
                               submitted; 3: no wave may go yet (wait; nothing changed); 1: a stop (tell Claude)

A2.10: "at most three alternation jobs of one run folder run at once ... so a run folder may need up to about 11 GB at
once, and A1.6's check wants 20 GB free before each alternation step. Before submission the bundle measures the free
space and the quota on hpc1 and submits at most (the smaller of the two, less 20 GB) / 11 GB run folders at a time, in
frame-number order, the next wave when a wave's alternation jobs have ended; the waves are reported."

Here:
- GB as the job scripts count it: their check is df -Pk's Available >= 20 * 1000000 (KiB), so 1 GB = 10^6 KiB.
- Free space: df -Pk's Available for SD.
- Quota left: the smallest of (a) what quota(1) reports for SD's filesystem, user and group (lfs quota on Lustre), and
  (b) hpc1's documented quota, 1 TB for paid users (https://www.sun.ac.za/hpc: "Paid users are granted unlimited CPU and
  a 1TB disk quota."), less the usage of the home folder (du -skx). (b) is always measured, because on hpc1 quota(1) has
  printed nothing. A quota line naming a filesystem that is neither SD's nor another mounted one stops it.
- Wave size: floor((min(free, quota left) - 20 GB) / 11 GB), capped by the run folders left and by the per-user limits on
  queued jobs, cores and memory that the PBS server, its default queue (where qsub puts a job without -q) and the queues
  the jobs are routed to set, so that no qsub is refused part-way through a wave. The free disk and the jobs' states are
  read after the (slow) usage measurement. If no queue would take the jobs, it stops.
- The next wave goes only when every alternation job (job_ts, job_r_irc, job_p_irc, job_r0) of every earlier wave has
  ended (PBS no longer has it queued, held, running or exiting), no other job of the user runs from SD, no other submit
  run of this script is going (ps), and every ended package job's output is on hpc1. If any package job's output reports
  a full disk or quota, it stops (tell Claude).
- Frame-number order; at a frame with both, the md run folder before the ci one.
- A run folder is submitted by removing its DO_NOT_SUBMIT (written by x83) and running its own submit.sh. Each wave is
  recorded in SD/package_waves/wave_N.txt. Nothing is deleted apart from those markers.
- A PBS query that fails stops everything: a job is never taken as ended because PBS could not be asked.
"""
import hashlib, os, re, shutil, subprocess, sys, time

ROOT = "/home/18660916/system_development"
HOME = "/home/18660916"
SD = ROOT + "/05_qmmm/24_sp_barriers"
SDTAG = "05_qmmm/24_sp_barriers"
USER = "18660916"
MD = ("20000 21634 23268 24883 26495 33320 34991 36665 38344 40485 41786 43087 43738 44388 45688 46990 47641 48292 "
      "49592 50892 52192 53493 54144 54795 55446 56098 57397 58698 59999").split()
CI = ("20000", "44388", "59999")
RUNS = []
for f in MD:
    RUNS.append("f%s_r8_a1" % f)
    if f in CI: RUNS.append("f%s_r8_ci_a1" % f)
ALT = ("job_ts", "job_r_irc", "job_p_irc", "job_r0")
JOBS = ("job_ts", "job_ts_freq_irc", "job_r_irc", "job_r_irc_freq", "job_p_irc", "job_p_irc_freq", "job_r0", "job_r0_freq")
GBK = 1000000                                # KiB in one GB, as the job scripts count
RESERVE = 20 * GBK; PER_RUN = 11 * GBK
DOC_QUOTA = 10 ** 12 // 1024                 # 1 TB in KiB
DOC_SRC = ("1 TB for paid users (https://www.sun.ac.za/hpc; taken as yours, since your use is far beyond the free tier's "
           "1000 CPU hours and 10 GB)")
DISKFAIL = re.compile(r"^SP_\S*_FAIL (less than \d+ GB free|machinery stop: the disk filled)"   # e.g. SP_ts/c03_env_FAIL
                      r"|No space left on device|Disk quota exceeded|Errno 28\b|Errno 122\b")
PRED = {"job_ts_freq_irc": "job_ts", "job_r_irc": "job_ts_freq_irc", "job_r_irc_freq": "job_r_irc",   # afterok, submit.sh
        "job_p_irc": "job_ts_freq_irc", "job_p_irc_freq": "job_p_irc", "job_r0_freq": "job_r0"}
WD = os.path.join(SD, "package_waves")
WAIT, STOP = 3, 1

def die(m): print("STOP: " + m); sys.stdout.flush(); sys.exit(STOP)
def gb(k): return "%.1f GB" % (k / GBK)
def run(cmd, timeout=180):
    env = dict(os.environ, LC_ALL="C")
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
        return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    except (FileNotFoundError, PermissionError): return None, "", "not found"
    except subprocess.TimeoutExpired: return None, "", "timed out after %d s" % timeout
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def key(jid): return jid.strip().split(".")[0]
def membytes(v):
    """PBS size ('250gb', '2tb', '1048576kb', '100mw') in bytes, or None"""
    m = re.match(r"^(\d+)([kmgtp]?)([bw]?)$", v.strip().lower())
    if not m: return None
    return int(m.group(1)) * 1024 ** "_kmgtp".index(m.group(2) or "_") * (8 if m.group(3) == "w" else 1)
def secs(v):
    """PBS walltime ('176:00:00', '7:00:00:00' or seconds) in seconds, or None"""
    p = v.strip().split(":")
    if not all(x.isdigit() for x in p) or len(p) > 4: return None
    s = 0
    for x, mult in zip(reversed(p), (1, 60, 3600, 86400)): s += int(x) * mult
    return s

# ---- PBS
def qstat_f(jid):
    """None if the job has ended (PBS: unknown, finished, or state F), else its attributes; any other failure stops"""
    rc, o, e = run(["qstat", "-f", jid])
    if rc is None: die("qstat could not be run (%s)" % e.strip())
    if rc != 0:
        if re.search(r"Unknown Job Id|Job has finished", e + o): return None
        die("qstat -f %s failed (exit %s): %s" % (jid, rc, (e + o).strip()[:200]))
    A = {}; k = None
    for l in o.splitlines():                # PBS wraps long values onto lines that start with a tab
        if l.startswith("\t") and k: A[k] += l[1:]; continue
        m = re.match(r"\s+([\w.]+) = (.*)$", l)
        if m: k = m.group(1); A[k] = m.group(2).rstrip()
        else: k = None
    if not A.get("job_state"): die("qstat -f %s printed no job_state" % jid)
    return None if A["job_state"] == "F" else A
def submitted(r):
    J = {}
    for l in open(os.path.join(SD, r, "SUBMITTED")):
        t = l.split()
        if len(t) == 2 and t[0] in JOBS and t[0] not in J: J[t[0]] = t[1]
        elif l.strip(): die("%s/SUBMITTED has an unexpected line: %s" % (r, l.strip()[:120]))
    if sorted(J) != sorted(JOBS): die("%s/SUBMITTED does not list the eight jobs: tell Claude" % r)
    return J
def ended_labels(r):
    """{job: (label, lines)} for the ended jobs of run folder r (JS[r][job] == 'ended'), in submit.sh's order:
    DISK  its output reports a full disk or quota (an SP_..._FAIL line of the job scripts' disk checks, or an
          out-of-space error from Python, xz or the shell);
    FAIL  its output has another SP_..._FAIL line;
    killed  its output lacks the job scripts' end_job= line (PBS ended it: walltime, deletion);
    ended   otherwise;
    skip  no output, and the job it needs (afterok) failed or was itself skipped or killed: PBS deleted it unrun;
    NOOUT no output otherwise (not delivered yet, or lost)"""
    out = {}
    for j in JOBS:
        if JS[r][j] != "ended": continue
        p = os.path.join(SD, r, j + ".pbs.out")
        if not os.path.exists(p):
            pl = out.get(PRED.get(j), ("",))[0]
            out[j] = ("skip" if pl in ("DISK", "FAIL", "killed", "skip") else "NOOUT", [])
            continue
        T = open(p, errors="replace").read().splitlines()
        disk = [l.strip() for l in T if DISKFAIL.search(l)]
        fail = [l.strip() for l in T if l.startswith("SP_") and "_FAIL" in l.split()[0]]
        if disk: out[j] = ("DISK", disk)
        elif fail: out[j] = ("FAIL", fail)
        elif not any(l.startswith("end_job=") for l in T): out[j] = ("killed", [])
        else: out[j] = ("ended", [])
    return out
def res_need(r):
    """(ncpus, bytes of memory, [(walltime s, ncpus, mem bytes)]) asked by the eight job scripts of run folder r"""
    nc = 0; mem = 0; req = []
    for j in JOBS:
        txt = open(os.path.join(SD, r, j + ".pbs")).read()
        m = re.search(r"^#PBS -l select=1:ncpus=(\d+):mem=(\w+)\s*$", txt, re.M)
        w = re.search(r"^#PBS -l walltime=(\S+)\s*$", txt, re.M)
        if not m or not w or membytes(m.group(2)) is None or secs(w.group(1)) is None:
            die("%s/%s.pbs: its resource request cannot be read: tell Claude" % (r, j))
        nc += int(m.group(1)); mem += membytes(m.group(2)); req.append((secs(w.group(1)), int(m.group(1)), membytes(m.group(2))))
    return nc, mem, req

# ---- disk and quota where SD is (KiB)
def df():
    """(filesystem, mount point, KiB available to the user) from df -Pk, the figure the job scripts check"""
    rc, o, e = run(["df", "-Pk", SD])
    L = o.splitlines()
    if rc != 0 or len(L) < 2: die("df -Pk %s failed: %s" % (SD, (e + o).strip()[:200]))
    t = L[1].split()
    if len(t) < 6 or not t[3].isdigit(): die("df -Pk %s printed a line this script cannot read: %s" % (SD, L[1]))
    return t[0], t[-1], int(t[3])
def fstype():
    rc, o, e = run(["stat", "-f", "-c", "%T", SD])
    return o.strip() if rc == 0 and o.strip() else "type unknown (%s)" % (e.strip() or "stat failed")
def qrows(text):
    """the data lines of quota(1) or lfs quota output, as [filesystem, blocks, quota, limit, ...]: a line whose first
    word is a path (it has a '/'); a long name may stand on a line of its own, its numbers on the next"""
    out = []; L = text.splitlines(); i = 0
    while i < len(L):
        t = L[i].split()
        if len(t) == 1 and "/" in t[0] and i + 1 < len(L) and re.match(r"^\s+[0-9]", L[i + 1]):
            out.append([t[0]] + L[i + 1].split()); i += 2; continue
        if len(t) >= 4 and "/" in t[0]: out.append(t)
        i += 1
    return out
def quota(fs, mnt, typ):
    """(stop reason or None, KiB of quota left, lines to report, raw tool output)"""
    raw = []; rows = []; notes = []
    if shutil.which("quota"):
        for who in (["-u", USER], ["-g"]):
            cmd = ["quota", "-v", "-w"] + who
            rc, o, e = run(cmd)
            if rc not in (0, 1) and re.search(r"invalid option|unrecognized option|usage", e + o, re.I):
                raw.append("%s: exit %s\n%s%s" % (" ".join(cmd), rc, o, e))
                cmd = ["quota", "-v"] + who; rc, o, e = run(cmd)
            raw.append("%s: exit %s\n%s%s" % (" ".join(cmd), rc, o, e))
            rows += [(" ".join(cmd), t) for t in qrows(o)]
            if rc not in (0, 1) or e.strip(): notes.append("%s: exit %s%s" % (" ".join(cmd), rc, (", " + e.strip().splitlines()[0][:120]) if e.strip() else ""))
    else: raw.append("quota: not installed"); notes.append("quota(1) is not installed")
    if typ == "lustre":
        import grp
        for who in (["-u", USER], ["-g", grp.getgrgid(os.getgid()).gr_name]):
            cmd = ["lfs", "quota"] + who + [mnt]
            rc, o, e = run(cmd)
            raw.append("%s: exit %s\n%s%s" % (" ".join(cmd), rc, o, e))
            rows += [(" ".join(cmd), t) for t in qrows(o)]
            if rc != 0: notes.append("%s: exit %s" % (" ".join(cmd), rc))
    raw = "\n".join(raw)
    try: mounts = [l.split()[:2] for l in open("/proc/mounts") if len(l.split()) >= 2]
    except OSError: mounts = []
    elsewhere = set(x.rstrip("/") for src, mp in mounts if mp != mnt for x in (src, mp))   # other mounted filesystems
    def same(name):   # SD's filesystem: its df name or mount point, or the same NFS export named by another host alias
        n = name.rstrip("/") or "/"
        return n in (fs.rstrip("/"), mnt) or (":" in n and ":" in fs and n.split(":", 1)[1] == fs.rstrip("/").split(":", 1)[1])
    best = None; nolimit = []; others = []
    for cmd, t in rows:
        try:
            used, soft, hard = (int(x.rstrip("*")) for x in t[1:4])
        except ValueError:
            return "a quota line could not be read (%s: %s)" % (cmd, " ".join(t)), None, [], raw
        lims = [x for x in (soft, hard) if x]
        if not same(t[0]):
            if not lims: continue
            if t[0].rstrip("/") in elsewhere: others.append("%s on %s" % (gb(min(lims)), t[0])); continue
            return ("%s reports a limit on %s, which is neither SD's filesystem (%s) nor another mounted one"
                    % (cmd, t[0], fs)), None, [], raw
        if not lims: nolimit.append(cmd); continue
        left = max(min(lims) - used, 0)
        if best is None or left < best[0]:
            best = (left, "%s: %s used of a %s limit on %s, %s left" % (cmd, gb(used), gb(min(lims)), t[0], gb(left)))
    lines = []
    if best: lines.append("quota tool: " + best[1])
    elif nolimit: lines.append("quota tool: no limit set on %s (%s)" % (fs, ", ".join(nolimit)))
    else: lines.append("quota tool: nothing reported for %s%s" % (fs, (" (" + "; ".join(notes) + ")") if notes else ""))
    if others: lines.append("quota tool, other mounted filesystems (not SD's, not used): limits of " + ", ".join(others))
    # du: HOME + "/" follows a symlinked home; files that vanish during the walk (running jobs) are not an error
    rc, o, e = run(["du", "-skx", HOME + "/"], timeout=3600)
    m = re.match(r"^(\d+)\s", o)
    errs = [l for l in e.splitlines() if l.strip() and not re.match(r"^du: cannot access .*: No such file or directory$", l)]
    if not m or rc not in (0, 1) or errs or (rc == 1 and not e.strip()):
        return "the usage of %s could not be measured (du -skx: exit %s, %s)" % (
            HOME, rc, (errs or e.strip().splitlines() or ["no output"])[0][:160]), None, lines, raw
    used = int(m.group(1)); dleft = max(DOC_QUOTA - used, 0)
    lines.append("documented quota: %s, less the usage of %s (du -skx: %s; taken as all your usage on this filesystem) = %s left"
                 % (DOC_SRC, HOME, gb(used), gb(dleft)))
    left = dleft if best is None else min(dleft, best[0])
    return None, left, lines, raw

# ---- PBS limits and queues: all reported; per-user limits on queued jobs, cores and memory of the server and of its
# default queue are applied; the queue a job of the package's resource request would be routed to is found
LIMRE = re.compile(r"^(max_[\w.]+|queued_jobs_threshold[\w.]*|resources_(max|min|default)\.(walltime|mem|ncpus)|route_destinations|"
                   r"default_queue|queue_type|enabled|started|acl_\w+)$")
def user_limits(A, names):
    """{'jobs'|'ncpus'|'mem': the smallest per-user limit on queued work in the named server/queues} or a stop reason"""
    cap = {}
    fam = {"max_queued": "jobs", "queued_jobs_threshold": "jobs", "max_user_queuable": "jobs",
           "max_queued_res.ncpus": "ncpus", "queued_jobs_threshold_res.ncpus": "ncpus",
           "max_queued_res.mem": "mem", "queued_jobs_threshold_res.mem": "mem"}
    for n in names:
        for a, kind in fam.items():
            v = A.get(n, {}).get(a, "")
            ent = re.findall(r"\[([ugpo]):([^=\]]+)=([^\]]+)\]", v)
            if a == "max_user_queuable" and v.strip().isdigit(): ent = [("u", "PBS_GENERIC", v.strip())]
            for scope, who, num in ent:
                if scope != "u" or who.strip() not in ("PBS_GENERIC", USER): continue
                x = membytes(num) if kind == "mem" else (int(num) if num.strip().isdigit() else None)
                if x is None: return "%s: %s = %s cannot be read" % (n, a, v)
                cap[kind] = x if kind not in cap else min(cap[kind], x)
    return cap
def pbs_limits():
    """(stop reason or None, lines to print, parsed attributes)"""
    lines = []; A = {}
    for args in (["qstat", "-Bf"], ["qstat", "-Qf"]):
        rc, o, e = run(args)
        if rc != 0: return "%s failed (exit %s): %s" % (" ".join(args), rc, (e + o).strip()[:160]), [], {}
        name = None; k = None
        for l in o.splitlines():
            m = re.match(r"^(Server|Queue): (\S+)", l)
            if m: name = "%s %s" % (m.group(1).lower(), m.group(2)); A[name] = {}; k = None; continue
            if l.startswith("\t") and k and name: A[name][k] += l[1:]; continue
            m = re.match(r"\s+([\w.]+) = (.*)$", l)
            if m and name: k = m.group(1); A[name][k] = m.group(2).rstrip()
            else: k = None
    srv = [n for n in A if n.startswith("server ")]
    if len(srv) != 1: return "qstat -Bf did not describe one PBS server", [], {}
    for n in A:
        for a in sorted(A[n]):
            if LIMRE.match(a): lines.append("  %s: %s = %s" % (n, a, A[n][a]))
    return None, lines, A
def route(A, req):
    """(stop reason or None, text, [destination queues]): the execution queue PBS would put each distinct request
    (walltime s, ncpus, mem) in: from the default queue, following route queues' destinations in order, the first
    enabled, started queue that admits the request (resources_min/max, user and group ACLs)"""
    import grp
    srv = [n for n in A if n.startswith("server ")][0]
    dq = A[srv].get("default_queue", "").strip()
    try: groups = set(grp.getgrgid(g).gr_name for g in os.getgroups() + [os.getgid()])
    except KeyError: groups = set()
    def acl_ok(Q, en, lst, names):
        if Q.get(en, "False") != "True": return True
        E = [x.strip() for x in Q.get(lst, "").split(",") if x.strip()]
        name = lambda x: x.lstrip("+-").split("@")[0]
        if any(x.startswith("-") and name(x) in names for x in E): return False
        return any(not x.startswith("-") and (name(x) in names or name(x) == "*") for x in E)
    def admits(Q, w, nc, mem):
        if Q.get("enabled", "True") != "True" or Q.get("started", "True") != "True": return False
        if not acl_ok(Q, "acl_user_enable", "acl_users", {USER}) or not acl_ok(Q, "acl_group_enable", "acl_groups", groups): return False
        for r, val, conv in (("walltime", w, secs), ("ncpus", nc, lambda v: int(v) if v.strip().isdigit() else None), ("mem", mem, membytes)):
            lo, hi = Q.get("resources_min." + r), Q.get("resources_max." + r)
            if lo is not None and (conv(lo) is None or val < conv(lo)): return False
            if hi is not None and (conv(hi) is None or val > conv(hi)): return False
        return True
    def place(q, w, nc, mem, depth=0):
        Q = A.get("queue " + q)
        if Q is None or depth > 5 or not admits(Q, w, nc, mem): return None
        if Q.get("queue_type", "").lower() == "execution": return q
        for d in [x.split("@")[0].strip() for x in Q.get("route_destinations", "").split(",") if x.strip()]:
            got = place(d, w, nc, mem, depth + 1)
            if got: return got
        return None
    if "queue " + dq not in A: return "the default queue %r is not described by qstat -Qf" % dq, "", []
    out = []; dests = []
    for w, nc, mem in sorted(set(req)):
        to = place(dq, w, nc, mem)
        if not to: return "no queue reached from %s admits a job asking %d:%02d:00 walltime, %d cores, %d GB" % (
            dq, w // 3600, w % 3600 // 60, nc, mem // 1024 ** 3), "", []
        out.append("%d h, %d cores, %d GB -> %s" % (w // 3600, nc, mem // 1024 ** 3, to)); dests.append(to)
    return None, "; ".join(out), sorted(set(dests))
def my_jobs(pkg):
    """(jobs, cores, memory bytes of the user's jobs PBS still has; [the user's other jobs that run from SD]);
    pkg: the package's jobs PBS has, key -> attributes"""
    rc, o, e = run(["qselect", "-u", USER])
    if rc != 0: die("qselect -u %s failed (exit %s): %s" % (USER, rc, (e + o).strip()[:200]))
    n = 0; nc = 0; mem = 0; other = []
    for i in o.split():
        A = pkg.get(key(i)) or qstat_f(i)
        if A is None: continue
        n += 1
        c = A.get("Resource_List.ncpus", "0"); nc += int(c) if c.isdigit() else 0
        mem += membytes(A.get("Resource_List.mem", "0b")) or 0
        if key(i) not in pkg and (SDTAG in A.get("Output_Path", "") or SDTAG in A.get("Variable_List", "")):
            other.append("%s (%s, %s)" % (i, A.get("Job_Name", "?"), A["job_state"]))
    return n, nc, mem, other
def other_submit_runs():
    """other runs of this script in submit mode on this login node (pids)"""
    rc, o, e = run(["ps", "-u", str(os.getuid()), "-o", "pid=,args="])
    if rc != 0: return ["unknown (ps failed: %s)" % (e.strip() or "exit %s" % rc)[:80]]
    return [m.group(1) for m in (re.match(r"^\s*(\d+)\s+\S*python\S*\s.*x84_pkg_waves\.py submit", l) for l in o.splitlines())
            if m and m.group(1) != str(os.getpid())]

# ---- the run folders and the waves
def waves():
    W = []
    if os.path.isdir(WD):
        for n in sorted(os.listdir(WD)):
            m = re.match(r"^wave_(\d+)\.txt$", n)
            if m:
                L = open(os.path.join(WD, n)).read().splitlines()
                W.append((int(m.group(1)), [l.split()[1] for l in L if l.startswith("RUN ")], bool(L) and L[-1].startswith("END ")))
            else: die("package_waves/ holds an unexpected file %s: tell Claude" % n)
    W.sort()
    if [w[0] for w in W] != list(range(1, len(W) + 1)): die("package_waves/ does not hold wave_1 .. wave_N: tell Claude")
    return W
def run_state(r):
    d = os.path.join(SD, r)
    if not os.path.isdir(d): die("missing run folder " + r)
    if os.path.exists(os.path.join(d, "SUBMITTED.partial")): return "PARTIAL"
    if os.path.exists(os.path.join(d, "SUBMITTED")): return "submitted"
    if any(os.path.exists(os.path.join(d, j + ".pbs.out")) for j in JOBS): return "OUTPUTS"
    return "waiting" if os.path.exists(os.path.join(d, "DO_NOT_SUBMIT")) else "UNMARKED"
def verify(r, want):
    """the run folder is exactly as generated: its log is the committed one, every file and link the log records is as
    recorded, and nothing else is there but DO_NOT_SUBMIT"""
    d = os.path.join(SD, r); log = os.path.join(d, "GENERATOR_LOG.txt")
    if sha(log) != want: die("%s/GENERATOR_LOG.txt is not the committed one: tell Claude" % r)
    files = set(); links = set()
    for l in open(log):
        l = l.rstrip("\n")
        m = re.match(r"^  ([0-9a-f]{64})  (\S+)$", l)
        if m:
            files.add(m.group(2)); p = os.path.join(d, m.group(2))
            if os.path.islink(p) or not os.path.isfile(p) or sha(p) != m.group(1):
                die("%s/%s is not the file its GENERATOR_LOG records: tell Claude" % (r, m.group(2)))
        m = re.match(r"^  link (\S+) -> (\S+)$", l)
        if m:
            links.add(m.group(1)); p = os.path.join(d, m.group(1))
            if not os.path.islink(p) or os.readlink(p) != m.group(2) or not os.path.isfile(p):
                die("%s/%s is not the link its GENERATOR_LOG records: tell Claude" % (r, m.group(1)))
    if len(files) != 26 or len(links) != 9:
        die("%s/GENERATOR_LOG.txt records %d files and %d links, expected 26 and 9" % (r, len(files), len(links)))
    have = set()
    for dp, dn, fn in os.walk(d):
        for x in fn + [y for y in dn if os.path.islink(os.path.join(dp, y))]:
            have.add(os.path.relpath(os.path.join(dp, x), d))
    extra = sorted(have - files - links - {"GENERATOR_LOG.txt", "DO_NOT_SUBMIT"})
    if extra: die("%s holds files its generator did not write (%s): tell Claude" % (r, " ".join(extra[:5])))
    if "DO_NOT_SUBMIT" not in have: die("%s has no DO_NOT_SUBMIT: tell Claude" % r)

# ---- gather
MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE not in ("status", "submit"): die("usage: pkg_waves.py status | submit SCRIPT_SHA RUN=SHA ...")
if not os.path.isdir(SD): die("no folder " + SD)
want = {}
if MODE == "submit":
    if sys.argv[0] in ("", "-") or not os.path.isfile(sys.argv[0]): die("submit runs from a file, not from standard input")
    if len(sys.argv) < 3 or sha(sys.argv[0]) != sys.argv[2]: die("this script's sha256 is not the one x84 sent: tell Claude")
    for a in sys.argv[3:]:
        r, _, h = a.partition("=")
        if r not in RUNS or r in want or not re.match(r"^[0-9a-f]{64}$", h): die("bad argument " + a)
        want[r] = h
    if sorted(want) != sorted(RUNS): die("the committed GENERATOR_LOG sha256 of all %d run folders are needed" % len(RUNS))
fs, mnt, free = df(); typ = fstype()
print("measuring the usage of %s (du -skx; this can take several minutes) ..." % HOME); sys.stdout.flush()
qwhy, qleft, qlines, qraw = quota(fs, mnt, typ)          # slow (du): everything below is measured after it
fs, mnt, free = df()
W = waves()
ST = {r: run_state(r) for r in RUNS}
JID = {r: submitted(r) for r in RUNS if ST[r] == "submitted"}
JA = {r: {j: qstat_f(JID[r][j]) for j in JOBS} for r in JID}
JS = {r: {j: ("ended" if JA[r][j] is None else JA[r][j]["job_state"]) for j in JOBS} for r in JA}
LAB = {r: ended_labels(r) for r in JA}
for r in LAB:
    for j in LAB[r]: JS[r][j] = LAB[r][j][0]
PKG = dict((key(JID[r][j]), JA[r][j]) for r in JA for j in JOBS if JA[r][j] is not None)
njobs, ncores, nmem, other = my_jobs(PKG)
others_running = other_submit_runs()
pwhy, plines, PA = pbs_limits()
wave_of = {r: n for n, rs, e in W for r in rs}
left = [r for r in RUNS if ST[r] == "waiting"]
need_nc, need_mem, req = res_need(left[0]) if left else (None, None, [])
rwhy, rtext, dests = route(PA, req) if (PA and req) else (None, "", [])
pcap = {}
if PA and not pwhy:
    srvn = [n for n in PA if n.startswith("server ")][0]
    dq = PA[srvn].get("default_queue", "").strip()
    pcap = user_limits(PA, [srvn] + (["queue " + dq] if dq else []) + ["queue " + d for d in dests])
    if isinstance(pcap, str): pwhy, pcap = pcap, {}

stop = None; wait = None                     # stop: tell Claude (exit 1); wait: ask again later (exit 3)
bad = [r for r in RUNS if ST[r] in ("PARTIAL", "OUTPUTS", "UNMARKED")]
open_w = [n for n, rs, e in W if not e]
diskfail = ["%s/%s.pbs.out: %s" % (r, j, LAB[r][j][1][0]) for r in sorted(LAB) for j in JOBS if j in LAB[r] and LAB[r][j][0] == "DISK"]
noout = ["%s %s" % (r, j) for r in sorted(LAB) for j in JOBS if j in LAB[r] and LAB[r][j][0] == "NOOUT"]
if others_running: wait = "another x84 submit run is going on hpc1 now (pid %s): wait for it to finish" % " ".join(others_running)
elif open_w: wait = ("package_waves/wave_%d.txt has no END line: that wave's submission is still going or stopped part-way. "
                     "Ask again in a few minutes; if this stays, tell Claude and run nothing else" % open_w[0])
if not wait:
    if bad: stop = "%s: a partial submission, job outputs without SUBMITTED, or no DO_NOT_SUBMIT" % " ".join(bad)
    elif [r for r in RUNS if ST[r] == "submitted" and r not in wave_of]: stop = "a run folder is submitted outside the recorded waves"
    elif [r for n, rs, e in W for r in rs if ST.get(r) != "submitted"]: stop = "a run folder of a recorded wave is not submitted"
    elif diskfail: stop = "a job of an earlier wave stopped for lack of disk or quota (%s)" % diskfail[0]
    elif pwhy: stop = "PBS's limits could not be read (%s)" % pwhy
    elif rwhy: stop = "PBS's queues: " + rwhy
    elif qwhy: stop = "the quota could not be measured: " + qwhy
if not stop and not wait:
    for n, rs, e in W:
        busy = [(r, j) for r in rs for j in ALT if JA[r][j] is not None]
        if busy: wait = "wave %d's alternation jobs have not all ended (%s: %s; %d in all)" % (n, busy[0][0], busy[0][1], len(busy)); break
if not stop and not wait and noout:
    wait = ("%s ended but its output (.pbs.out) is not on hpc1; it may still be on its way. Ask again in a few minutes; if "
            "this stays, tell Claude (%d such job(s))" % (noout[0], len(noout)))
if not stop and not wait and other: wait = "another job of yours runs from SD (%s): wait for it to end, or tell Claude" % "; ".join(other)
if not stop and not wait and not left: wait = "every run folder has been submitted"
size = 0; sizeline = "n/a"
if not stop and not wait:
    lim = min(free, qleft)
    dcap = max(0, (lim - RESERVE) // PER_RUN)
    caps = [("disk and quota", dcap)]
    if "jobs" in pcap: caps.append(("PBS's queued-job limit", max(0, (pcap["jobs"] - njobs) // len(JOBS))))
    if "ncpus" in pcap: caps.append(("PBS's queued-core limit", max(0, (pcap["ncpus"] - ncores) // need_nc)))
    if "mem" in pcap: caps.append(("PBS's queued-memory limit", max(0, (pcap["mem"] - nmem) // need_mem)))
    size = min([c for _, c in caps] + [len(left)])
    sizeline = "floor((%s - 20 GB) / 11 GB) = %d by disk and quota%s; run folders left: %d" % (
        gb(lim), dcap, "".join(", %d by %s" % (c, w) for w, c in caps[1:]), len(left))
    if size < 1:
        wait = "no room: %s" % ("less than 31 GB free (or left in the quota) where SD is" if dcap < 1 else
                                "; ".join("%s leaves room for %d run folders" % (w, c) for w, c in caps[1:] if c < 1))
batch = [] if (stop or wait) else left[:size]

# ---- report
print("run folder          state      wave  each job: R running, Q queued, H held (waiting for the job it needs), E exiting;")
print("                                     ended; FAIL (an SP_..._FAIL line in its output); DISK (its output reports a full disk or")
print("                                     quota); killed (no end_job line: PBS ended it); skip (not run: a job it needs failed);")
print("                                     NOOUT (ended, output not on hpc1)")
print("                                     ts r_irc p_irc r0 (the alternation jobs) | ts_freq_irc r_irc_freq p_irc_freq r0_freq")
for r in RUNS:
    jt = "-"
    if r in JS: jt = " ".join(JS[r][j] for j in ALT) + " | " + " ".join(JS[r][j] for j in JOBS if j not in ALT)
    print("%-19s %-10s %-5s %s" % (r, ST[r], wave_of.get(r, "-"), jt))
print("run folders: %d waiting (DO_NOT_SUBMIT), %d submitted%s" % (len(left), len(JID), "; needing Claude: " + " ".join(bad) if bad else ""))
nst = {}
for r in JS:
    for j in JOBS: nst[JS[r][j]] = nst.get(JS[r][j], 0) + 1
if nst: print("package jobs: " + ", ".join("%d %s" % (nst[k], k) for k in sorted(nst)))
fl = [(r, j, LAB[r][j][1][0]) for r in sorted(LAB) for j in JOBS if j in LAB[r] and LAB[r][j][1]]
for r, j, l in fl[:10]: print("  %s %s: %s" % (r, j, l[:150]))
if len(fl) > 10: print("  ... %d more" % (len(fl) - 10))
qn = {}
for r in JA:
    for j in JOBS:
        if JA[r][j] is not None: qn[JA[r][j].get("queue", "?")] = qn.get(JA[r][j].get("queue", "?"), 0) + 1
if qn: print("package jobs in PBS by queue: " + ", ".join("%s %d" % (q, qn[q]) for q in sorted(qn)))
print("waves so far: %s" % ("; ".join("wave %d: %d run folder(s)%s" % (n, len(rs), "" if e else " (NO END LINE)") for n, rs, e in W) or "none"))
print("disk where SD is: %s on %s (%s), %s available (df -Pk; GB = 10^6 KiB, as the job scripts count)" % (fs, mnt, typ, gb(free)))
for l in qlines: print(l)
print("quota left: %s" % (gb(qleft) if qleft is not None else "not measured" + (" (%s)" % qwhy if qwhy else "")))
print("your jobs PBS still has: %d (%d cores)%s" % (njobs, ncores, "; from SD but not the package's: " + "; ".join(other) if other else ""))
print("PBS limits and queues:\n" + ("\n".join(plines) if plines else "  none reported") + ("\n  " + pwhy if pwhy else ""))
print("per-user limits on queued work (server, its default queue, the queues the jobs go to): %s" % (
    ", ".join("%s %s" % (k, gb(v // 1024) if k == "mem" else v) for k, v in sorted(pcap.items())) or "none set"))
if rtext or rwhy: print("where the package's jobs go: %s" % (rtext or rwhy))
print("wave size now: %s" % ("%s -> %d" % (sizeline, size) if sizeline != "n/a" else "n/a (no wave may go now)"))
print("NEXT_WAVE: %s" % ("STOP - %s: tell Claude" % stop if stop else "no - " + wait if wait else
                         "yes, wave %d of %d run folder(s): %s" % (len(W) + 1, len(batch), " ".join(batch))))
sys.stdout.flush()
if MODE == "status":
    print("\nquota tools, raw output:\n" + qraw.rstrip())
    sys.exit(0)

# ---- submit
if stop: sys.exit(STOP)
if wait: sys.exit(WAIT)
for r in batch: verify(r, want[r])
N = len(W) + 1
os.makedirs(WD, exist_ok=True)
wf = os.path.join(WD, "wave_%d.txt" % N)
hdr = ["wave %d of the SP package (SP_AMENDMENT2.txt A2.10), submitted %s by x84 (pkg_waves.py, sha256 %s)" % (
           N, time.strftime("%Y-%m-%d %H:%M:%S %Z"), sys.argv[2]),
       "disk where SD is: %s on %s (%s), %s available (df -Pk; GB = 10^6 KiB, as the job scripts count)" % (fs, mnt, typ, gb(free))]
hdr += qlines
hdr += ["quota left: %s" % gb(qleft),
        "per-user limits on queued work (server, its default queue, the queues the jobs go to): %s; your jobs PBS had: %d (%d cores)" % (
            ", ".join("%s %s" % (k, gb(v // 1024) if k == "mem" else v) for k, v in sorted(pcap.items())) or "none set", njobs, ncores),
        "where the package's jobs go: %s" % rtext,
        "size: %s; this wave: %d" % (sizeline, len(batch)),
        ("earlier waves: %s; all their alternation jobs had ended; no package job had reported a full disk or quota, or lacked its output" % ", ".join(str(n) for n, rs, e in W))
        if W else "earlier waves: none",
        "each run folder below: its inputs checked against its committed GENERATOR_LOG.txt (every recorded file and link, "
        "nothing else present), DO_NOT_SUBMIT removed, its submit.sh run; submit.sh's output follows"]
try:
    with open(wf, "x") as o: o.write("\n".join(hdr) + "\n")
except FileExistsError: die("%s exists already: another submit run made it. Run nothing else: tell Claude" % wf)
done = []
for r in batch:
    with open(wf, "a") as o: o.write("RUN %s\n" % r)
    os.remove(os.path.join(SD, r, "DO_NOT_SUBMIT"))
    p = subprocess.run(["bash", "submit.sh"], cwd=os.path.join(SD, r), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode(errors="replace")
    with open(wf, "a") as o:
        o.write("".join("  " + l + "\n" for l in out.rstrip("\n").splitlines()))
        if p.returncode != 0: o.write("  SUBMIT.SH STOPPED (exit %d)\n" % p.returncode)
    if p.returncode != 0:
        print(out.rstrip())
        die("%s: its submit.sh stopped (above) after %d run folder(s) of this wave were submitted (%s); %s records it. "
            "Run nothing else: tell Claude" % (r, len(done), " ".join(done) or "none", wf))
    done.append(r)
    print("submitted %s: %s" % (r, " ".join(l.split()[1] for l in open(os.path.join(SD, r, "SUBMITTED")) if len(l.split()) == 2)))
    sys.stdout.flush()
with open(wf, "a") as o: o.write("END %d run folder(s) submitted\n" % len(done))
print("WAVE %d SUBMITTED: %d run folder(s): %s" % (N, len(done), " ".join(done)))
