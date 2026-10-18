#!/usr/bin/env python3
"""
verify_stage.py - PC side of x77 (the SP runs' outputs kept as physical files). Python 3, standard library plus the tar
and xz commands. Writes nothing in the repo.

  verify_stage.py stage W REPO PC     W = a fetched hpc1 stage folder (batch_N); PC = the folder with the fetched PC
                                      archives (RUN.tar.xz). Before anything is committed: every PC archive is read
                                      member by member and each member's sha256 compared with the inventory, and its
                                      members are exactly the batch's regular files of that run; every git archive is
                                      extracted and each member compared with its manifest; every file compressed one by
                                      one is decompressed and compared with its original's sha256; every list agrees with
                                      the inventory, file by file; nothing to be committed is over 95 MB or exists in the
                                      repo already, and all of it together stays under GitHub's 2 GB push limit (1.5 GB);
                                      every file on the deletion list is scratch or a working file, lies in a step folder
                                      of the four runs, and is no step's final wavefunction (deletion checks these again)
  verify_stage.py pcarchive A M       A = a PC archive, M = its manifest (sha256  path): every member present once, with
                                      its sha256, and nothing else (used again before any deletion)
  verify_stage.py precheck B          B = a committed batch folder: every file to be deleted or compressed in place is in
                                      that batch's committed PC-archive manifest with the same sha256, and each manifest
                                      used belongs to a PC archive listed in PC_ARCHIVES.tsv (before deletion)
  verify_stage.py postcheck W         after the deletion: every listed file deleted (or compressed in place, or kept as it
                                      is), and every file that was to stay still there with its recorded size; prints the
                                      summary for POSTCHECK.txt
  verify_stage.py extras ADMIN        the files x76's batches kept on hpc1 (keep.tsv rows other than links) that no x77
                                      batch has taken yet, as +PATH=SHA256 items for the stage; stops if a row has no sha256
  verify_stage.py track ADMIN FILES   FILES = sp_cleanup.py files output: every file now in a step that a batch has taken
                                      (STEPS.txt) was archived or committed by a batch with this size and modification
                                      time (to the minute), or is the .xz a deletion left in its place (by size); every
                                      folder of the four runs is a step or cycle
                                      folder; no folder named after one of the four runs exists (e.g. an A1.5 RUN_stop1)
"""
import hashlib, os, re, subprocess, sys, tarfile, tempfile

REL0 = "05_qmmm/24_sp_barriers/"
RUNS = ("f42436_r8", "f42436_r6", "f42436_r8_a1", "f42436_r6_a1")
CATS = ("git_text", "git_xz", "git_asis", "pc_keep", "pc_delete", "link")
GIT_MAX = 95 * 1000000
PUSH_MAX = 1500 * 1000000          # all git files of one batch together (GitHub refuses a push over 2 GB)
A1_RUNS = ("f42436_r8_a1", "f42436_r6_a1")
ALT = ("ts", "r_irc", "p_irc", "r0")
JOBS = (("job_ts", ("ts",)), ("job_ts_freq_irc", ("ts_freq", "irc")), ("job_r_irc", ("r_irc",)),
        ("job_r_irc_freq", ("r_irc_freq",)), ("job_p_irc", ("p_irc",)), ("job_p_irc_freq", ("p_irc_freq",)),
        ("job_r0", ("r0",)), ("job_r0_freq", ("r0_freq",)))
STEPS = [x for j, ss in JOBS for x in ss]
FIRST_STEP_OF_JOB = dict((j, ss[0]) for j, ss in JOBS)
CYC_RE = re.compile(r"^c\d\d_(env|core)$")
WFN_RE = re.compile(r"(\.gbw\d*|\.densities)$")
BAD = []

def bad(m): BAD.append(m)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def xz_sha(p):
    h = hashlib.sha256()
    x = subprocess.Popen(["xz", "-dc", p], stdout=subprocess.PIPE)
    for b in iter(lambda: x.stdout.read(1 << 20), b""): h.update(b)
    return h.hexdigest() if x.wait() == 0 else None
def sums(p):
    D = {}
    for l in open(p):
        l = l.rstrip("\n")
        if l:
            if l[64:66] != "  " or not re.match(r"^[0-9a-f]{64}$", l[:64]): bad("%s: malformed line %r" % (os.path.basename(p), l[:80])); continue
            if l[66:] in D: bad("%s lists %s twice" % (os.path.basename(p), l[66:]))
            D[l[66:]] = l[:64]
    return D
def tsv(p): return [l.rstrip("\n").split("\t") for l in open(p) if l.strip() and not l.startswith("#")]
def inventory(w):
    I = {}
    for r in tsv(w + "/inventory.tsv"):
        if len(r) != 5: bad("inventory.tsv: malformed row %r" % r[:3]); continue
        size, mtime, path, cat, h = r
        if cat != "-" and cat not in CATS: bad("inventory.tsv: unknown category %s for %s" % (cat, path))
        if path in I: bad("inventory.tsv lists %s twice" % path)
        I[path] = (cat, int(size), h)
    return I
def in_runs(p):
    q = p.split("/")
    return p.startswith(REL0) and len(q) >= 4 and q[2] in RUNS and ".." not in q
def deletable(p):
    """scratch and working files only (as sp_cleanup.py)"""
    return bool(re.search(r"(\.tmp|\.tmp\.[^/]*|\.appr\.hess|\.carthess|\.gbw\d*|\.densities)$", os.path.basename(p)))
def rel_ok(p):
    """(run, step, cycle folder or None) if p is a file in a step folder (or a cycle folder of an alternation) of the
    four runs; None otherwise (as sp_cleanup.py)"""
    q = p.split("/")
    if not p.startswith(REL0) or len(q) not in (5, 6) or q[2] not in RUNS or q[3] not in STEPS: return None
    if any(x in ("", ".", "..") for x in q): return None
    if len(q) == 6:
        if not (q[2] in A1_RUNS and q[3] in ALT and CYC_RE.match(q[4])): return None
        return q[2], q[3], q[4]
    return q[2], q[3], None
def replaceable(p):
    """a git_xz file that the deletion replaces by its .xz (as sp_cleanup.py)"""
    n = os.path.basename(p)
    return bool(rel_ok(p)) and not WFN_RE.search(n) and not n.endswith(".hess")
def pc_members(a):
    """{member: sha256} of a tar.xz, read as a stream; None if it cannot be read"""
    got = {}
    try:
        with tarfile.open(a, "r|xz") as t:
            for m in t:
                if not m.isfile(): bad("%s: member %s is not a regular file" % (os.path.basename(a), m.name)); continue
                if m.name in got: bad("%s holds %s twice" % (os.path.basename(a), m.name))
                f = t.extractfile(m); h = hashlib.sha256()
                for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
                got[m.name] = h.hexdigest()
    except (tarfile.TarError, EOFError, OSError) as e:
        bad("%s cannot be read: %s" % (a, e)); return None
    return got
def pcarchive(a, m):
    M = sums(m); got = pc_members(a)
    if got is None: return
    if sorted(got) != sorted(M): bad("%s: members differ from %s (%d against %d)" % (a, m, len(got), len(M)))
    for p, h in got.items():
        if M.get(p) != h: bad("%s: member %s does not match its sha256" % (a, p))
    if not BAD: print("PC archive verified: %s (%d members, each with its recorded sha256)" % (a, len(got)))

def stage(w, repo, pc):
    for f in ("DONE", "STEPS.txt", "EXTRAS.txt", "SUMMARY.txt", "inventory.tsv", "archives.tsv", "ARCHIVES_BUILT.tsv",
              "individual.tsv", "INDIV.sha256", "INDIV_XZ.sha256", "as_is.tsv", "AS_IS.sha256", "delete.tsv",
              "DELETE_CHECKSUMS.sha256", "pc_keep.tsv", "links.tsv", "SP_REPORT.txt", "SPA_REPORT.txt"):
        if not os.path.isfile(os.path.join(w, f)): bad("missing " + f)
    if BAD: return
    I = inventory(w)
    batch = dict((p, v) for p, v in I.items() if v[0] != "-")
    cat = lambda c: dict((p, v) for p, v in batch.items() if v[0] == c)
    for p in batch:
        if not in_runs(p): bad("a batch file outside the four run folders: " + p)
    # the PC archives: every regular batch file of each run, with its sha256, and nothing else
    regular = dict((p, v) for p, v in batch.items() if v[0] != "link")
    for run_ in RUNS:
        lst = os.path.join(w, "PCLIST_%s.txt" % run_)
        mine = sorted(p for p in regular if p.split("/")[2] == run_)
        if not mine:
            if os.path.exists(lst) or os.path.exists(os.path.join(pc, run_ + ".tar.xz")): bad("a PC list or archive for %s, which has no batch file" % run_)
            continue
        if not os.path.isfile(lst): bad("missing PCLIST_%s.txt" % run_); continue
        L = [l.rstrip("\n") for l in open(lst) if l.strip()]
        if sorted(L) != mine: bad("PCLIST_%s.txt is not the batch's regular files of that run" % run_)
        a = os.path.join(pc, run_ + ".tar.xz")
        if not os.path.isfile(a): bad("missing PC archive " + a); continue
        got = pc_members(a)
        if got is None: continue
        if sorted(got) != mine: bad("%s: members are not the batch's regular files of %s" % (a, run_))
        for p, h in got.items():
            if regular.get(p, ("", 0, ""))[2] != h: bad("%s: member %s does not match the inventory's sha256" % (a, p))
    # git archives: lists, manifests, members
    A = tsv(w + "/archives.tsv"); arch = {}
    for name, size, path in A: arch.setdefault(name, []).append(path)
    if sorted(p for n, s, p in A) != sorted(cat("git_text")): bad("archives.tsv and the inventory's git_text files differ")
    for name, size, path in A:
        if path not in batch: bad("archives.tsv lists %s, which the inventory does not have in this batch" % path); continue
        if int(size) != batch[path][1]: bad("archives.tsv size of %s differs from the inventory" % path)
    built = tsv(w + "/ARCHIVES_BUILT.tsv")
    if sorted(b[0] for b in built) != sorted(arch): bad("ARCHIVES_BUILT.tsv and archives.tsv name different archives")
    for name, nmem, size in built:
        a = os.path.join(w, "arch", name); m = a[:-len(".tar.xz")] + ".MANIFEST.sha256"
        if not (os.path.isfile(a) and os.path.isfile(m)): bad("missing archive or manifest " + name); continue
        if os.path.getsize(a) != int(size) or os.path.getsize(a) > GIT_MAX: bad("%s: size %d (recorded %s)" % (name, os.path.getsize(a), size))
        M = sums(m)
        if sorted(M) != sorted(arch[name]) or len(M) != int(nmem): bad("%s: manifest and archives.tsv list different members" % name)
        for p, h in M.items():
            if h != batch.get(p, ("", 0, ""))[2]: bad("%s: manifest sha256 of %s differs from the inventory" % (name, p))
        with tempfile.TemporaryDirectory() as d:
            x = subprocess.Popen(["xz", "-dc", a], stdout=subprocess.PIPE)
            t = subprocess.run(["tar", "-xf", "-", "-C", d], stdin=x.stdout); x.stdout.close()
            if x.wait() != 0 or t.returncode != 0: bad("%s: extraction failed" % name); continue
            got = {}
            for dp, dn, fn in os.walk(d):
                for f in fn: got[os.path.relpath(os.path.join(dp, f), d)] = sha(os.path.join(dp, f))
            if sorted(got) != sorted(M): bad("%s: members differ from the manifest" % name)
            for p, h in got.items():
                if M.get(p) != h: bad("%s: member %s does not match its manifest sha256" % (name, p))
    # compressed one by one
    ind = dict((r[1], int(r[0])) for r in tsv(w + "/individual.tsv"))
    IS, IX = sums(w + "/INDIV.sha256"), sums(w + "/INDIV_XZ.sha256")
    if sorted(ind) != sorted(cat("git_xz")) or sorted(IS) != sorted(ind) or sorted(IX) != sorted(p + ".xz" for p in ind):
        bad("individual.tsv, INDIV.sha256, INDIV_XZ.sha256 and the inventory list different files")
    for p in ind:
        if p not in batch: bad("individual.tsv lists %s, which the inventory does not have in this batch" % p); continue
        q = os.path.join(w, "indiv", p + ".xz")
        if not os.path.isfile(q): bad("missing compressed " + p); continue
        if os.path.getsize(q) > GIT_MAX: bad(p + ".xz is over 95 MB")
        if sha(q) != IX.get(p + ".xz"): bad(p + ".xz does not match INDIV_XZ.sha256")
        if xz_sha(q) != IS.get(p) or IS.get(p) != batch[p][2]: bad(p + ".xz does not decompress to the original")
    # as they are
    asis = dict((r[1], int(r[0])) for r in tsv(w + "/as_is.tsv")); AS = sums(w + "/AS_IS.sha256")
    if sorted(asis) != sorted(cat("git_asis")) or sorted(AS) != sorted(asis): bad("as_is lists differ from the inventory")
    for p in asis:
        if p not in batch: bad("as_is.tsv lists %s, which the inventory does not have in this batch" % p); continue
        q = os.path.join(w, "asis", p)
        if not os.path.isfile(q) or sha(q) != AS.get(p) or AS.get(p) != batch[p][2] or os.path.getsize(q) > GIT_MAX:
            bad("the copy of %s is missing, changed or over 95 MB" % p)
        elif subprocess.run(["xz", "-t", q]).returncode != 0: bad("the job's compressed file %s fails xz -t" % p)
    # deletion, PC-only and link lists
    dl = dict((r[2], (r[0], int(r[1]))) for r in tsv(w + "/delete.tsv")); DS = sums(w + "/DELETE_CHECKSUMS.sha256")
    if sorted(dl) != sorted(cat("pc_delete")) or sorted(DS) != sorted(dl): bad("delete lists differ from the inventory")
    for p in dl:
        if p not in batch: bad("delete.tsv lists %s, which the inventory does not have in this batch" % p); continue
        if DS.get(p) != batch[p][2]: bad("DELETE_CHECKSUMS.sha256 of %s differs from the inventory" % p)
        if not deletable(p): bad("a file of a kind that is never deleted is on the deletion list: " + p)
        t = rel_ok(p)
        if not t: bad("a file outside a step folder of the four runs is on the deletion list: " + p)
        elif t[2] is None and re.search(r"\.(gbw|densities)$", p): bad("a step's final wavefunction is on the deletion list: " + p)
    fins = {}                                     # an alternation's final wavefunction: from one core folder only
    for p in cat("git_xz"):
        t = rel_ok(p)
        if t and t[2] and WFN_RE.search(p): fins.setdefault(t[:2], set()).add(t[2])
    for k, v in fins.items():
        if len(v) != 1 or not list(v)[0].endswith("_core"): bad("%s/%s: final wavefunction from %s" % (k[0], k[1], sorted(v)))
    for p in dl:
        t = rel_ok(p)
        if t and t[2] and (t[0], t[1]) not in fins and re.search(r"\.gbw$", p) and t[2].endswith("_core"):
            bad("%s/%s: no core step's wavefunction is kept, but %s is to be deleted" % (t[0], t[1], p))
    pk = [r[2] for r in tsv(w + "/pc_keep.tsv")]
    if sorted(pk) != sorted(cat("pc_keep")): bad("pc_keep.tsv differs from the inventory")
    lk = [r[0] for r in tsv(w + "/links.tsv")]
    if sorted(lk) != sorted(cat("link")): bad("links.tsv differs from the inventory")
    for p in lk:
        if not re.match(r"^link:[^:]+:[0-9a-f]{64}$", batch[p][2]): bad("the link %s has no recorded target sha256" % p)
    for p in cat("git_xz"):
        if p.endswith((".gbw", ".densities")) and not batch[p][2]: bad("no sha256 for " + p)
    # nothing to be committed exists in the repo already, or twice
    targets = [n for n in arch] + [n[:-len(".tar.xz")] + ".MANIFEST.sha256" for n in arch] + [p + ".xz" for p in ind] + list(asis)
    if len(set(targets)) != len(targets): bad("two files would be committed to the same path")
    for t in targets:
        if os.path.lexists(os.path.join(repo, t)): bad("would overwrite %s in the repo" % t)
    gitb = (sum(os.path.getsize(os.path.join(w, "arch", n)) for n in arch) + sum(
            os.path.getsize(os.path.join(w, "indiv", p + ".xz")) for p in ind if os.path.isfile(os.path.join(w, "indiv", p + ".xz")))
            + sum(os.path.getsize(os.path.join(w, "asis", p)) for p in asis if os.path.isfile(os.path.join(w, "asis", p))))
    if gitb > PUSH_MAX: bad("the batch would commit %.2f GB to git (limit 1.5 GB per batch, GitHub refuses a push over 2 GB): tell Claude" % (gitb / 1e9))
    nrep = sum(1 for p in ind if replaceable(p))
    S = dict((c, (len(cat(c)), sum(v[1] for v in cat(c).values()))) for c in CATS)
    print("verified: PC archives with all %d regular files (%.2f GB) of the batch, each with its sha256; git (%.2f GB): %d "
          "archives (%d text files) extracted and matched, %d files compressed one by one and matched (%d to be replaced "
          "by that .xz on hpc1, the rest stay as they are), %d as compressed by the jobs; PC only: %d kept on hpc1, %d "
          "(%.2f GB; scratch and working files) to be deleted from hpc1; %d links" % (
          len(regular), sum(v[1] for v in regular.values()) / 1e9, gitb / 1e9, len(arch), S["git_text"][0], S["git_xz"][0],
          nrep, S["git_asis"][0], S["pc_keep"][0], S["pc_delete"][0], S["pc_delete"][1] / 1e9, S["link"][0]))

def postcheck(w):
    I = inventory(w)
    batch = dict((p, v) for p, v in I.items() if v[0] != "-")
    log = {}
    for l in open(w + "/DELETED.log"):
        f = l.split()
        if not f: continue
        log[f[-1]] = f[0]
    rem = {}
    for l in open(w + "/REMAINING.tsv"):
        s, p = l.rstrip("\n").split("\t")
        rem[p] = s
    DS = sums(w + "/DELETE_CHECKSUMS.sha256"); IS = sums(w + "/INDIV.sha256")
    n = {"DELETED": 0, "COMPRESSED": 0, "KEPT": 0}; other = []
    for p in list(DS) + list(IS):
        st = log.get(p)
        if st is None: bad("not in DELETED.log: " + p); continue
        if st == "KEPT" and (p in DS or replaceable(p)): bad("KEPT, but it was to be deleted or compressed: " + p)
        if st == "COMPRESSED" and (p in DS or not replaceable(p)): bad("COMPRESSED, but it was to stay as it is: " + p)
        if st == "DELETED" and p not in DS: bad("DELETED, but it is not on the deletion list: " + p)
        if st in n: n[st] += 1
        else: other.append("%s %s" % (st, p))
        if st in ("DELETED", "COMPRESSED") and p in rem: bad("still present after %s: %s" % (st, p))
        if st == "COMPRESSED" and p + ".xz" not in rem: bad("compressed copy missing: %s.xz" % p)
        if st == "KEPT" and (p not in rem or rem[p] == "link" or int(rem[p]) != batch.get(p, ("", -1))[1]):
            bad("committed as .xz and to stay as it is, but gone or changed in size: " + p)
    for p, (c, size, h) in batch.items():
        if c in ("git_text", "git_asis", "pc_keep", "link"):
            if p not in rem: bad("a file that was to stay is gone: " + p)
            elif c == "link":
                if rem[p] != "link": bad("a link that was to stay is no longer a link: " + p)
            elif rem[p] == "link" or int(rem[p]) != size: bad("a file that was to stay changed size: " + p)
    gone = [p for p in batch if p not in rem and p not in DS and p not in IS]
    for p in gone: bad("gone although not listed: " + p)
    freed = sum(batch[p][1] for p in DS if log.get(p) == "DELETED")
    print("post-check: %d deleted (%.2f GB), %d compressed in place, %d committed as .xz and kept as they are, %d not "
          "acted on%s; every file that was to stay is present with its recorded size; no other file of this batch is gone" % (
          n["DELETED"], freed / 1e9, n["COMPRESSED"], n["KEPT"], len(other),
          (" (" + "; ".join(other[:10]) + ("; ..." if len(other) > 10 else "") + ")") if other else ""))

def precheck(b):
    """every file the deletion acts on is in the batch's committed PC-archive manifest, with the same sha256"""
    M = {}
    listed = set(r[0] for r in tsv(b + "/PC_ARCHIVES.tsv"))
    for f in sorted(os.listdir(b)):
        m = re.match(r"^PCMANIFEST_(.+)\.sha256$", f)
        if m and m.group(1) in listed: M[m.group(1)] = sums(os.path.join(b, f))
    D = sums(b + "/DELETE_CHECKSUMS.sha256"); I = sums(b + "/INDIV.sha256")
    n = 0
    for p, h in list(D.items()) + [(p, h) for p, h in I.items() if replaceable(p)]:
        q = p.split("/")
        if len(q) < 4 or M.get(q[2], {}).get(p) != h: bad("not in the committed PC-archive manifest with this sha256: " + p)
        n += 1
    if not BAD: print("every one of the %d files to be deleted or compressed in place is in the committed PC-archive manifests" % n)

def batch_dirs(admin):
    B = [d for d in os.listdir(admin) if re.match(r"^batch_\d+$", d) and os.path.isdir(os.path.join(admin, d))]
    return [os.path.join(admin, d) for d in sorted(B, key=lambda d: int(d[6:]))]
def extras(admin):
    """x76's kept files (keep.tsv: reason, path, sha256 or link:TARGET) that no x77 batch has taken (EXTRAS.txt)"""
    taken = set()
    for b in batch_dirs(admin):
        if os.path.isfile(b + "/EXTRAS.txt"): taken |= set(r[0] for r in tsv(b + "/EXTRAS.txt"))
    out = []
    for b in batch_dirs(admin):
        if not os.path.isfile(b + "/keep.tsv"): continue
        for r in tsv(b + "/keep.tsv"):
            if len(r) != 3: bad("%s/keep.tsv: malformed row %r" % (os.path.basename(b), r[:2])); continue
            reason, p, h = r
            if reason == "link" and h.startswith("link:"): continue
            if not re.match(r"^[0-9a-f]{64}$", h): bad("%s/keep.tsv: no sha256 for %s" % (os.path.basename(b), p)); continue
            if not rel_ok(p): bad("%s/keep.tsv: %s is not in a step folder of the four runs" % (os.path.basename(b), p)); continue
            if p not in taken: out.append("+%s=%s" % (p, h))
    if not BAD and out: print("\n".join(out))
def step_of(p):
    """the step a file of the four runs belongs to, as the batches record it (RUN/STEP), or None"""
    q = p.split("/")
    if len(q) == 4:
        m = re.match(r"^(job_\w+)\.pbs\.out$", q[3])
        if m: return "%s/%s" % (q[2], FIRST_STEP_OF_JOB[m.group(1)]) if m.group(1) in FIRST_STEP_OF_JOB else None
        return "%s/_run" % q[2]
    if len(q) == 5 and q[3] in STEPS: return "%s/%s" % (q[2], q[3])
    if rel_ok(p): return "%s/%s" % (q[2], q[3])
    return None
def track(admin, files):
    done, known, known_xz = set(), set(), set()
    for b in batch_dirs(admin):
        for r in tsv(b + "/STEPS.txt"): done.add(r[0])
        for r in tsv(b + "/inventory.tsv"):          # size, mtime, path, category, sha256 (or link:...)
            if len(r) == 5 and r[3] != "-":
                known.add((r[2], "link", "-") if r[3] == "link" or r[4].startswith("link:") else (r[2], r[0], r[1]))
        if os.path.isfile(b + "/DELETED.log") and os.path.isfile(b + "/REMAINING.tsv"):
            comp = set(l.split()[-1] for l in open(b + "/DELETED.log") if l.startswith("COMPRESSED "))
            for r in tsv(b + "/REMAINING.tsv"):
                if r[1].endswith(".xz") and r[1][:-3] in comp: known_xz.add((r[1], r[0]))
        repo = os.path.dirname(os.path.dirname(os.path.abspath(admin)))      # admin = REPO/00_admin/hpc_cleanup_smoke1
        if os.path.isfile(b + "/INDIV_XZ.sha256"):     # a file's .xz as committed (a deletion may have put it in place)
            for x in sums(b + "/INDIV_XZ.sha256"):
                if os.path.isfile(os.path.join(repo, x)): known_xz.add((x, str(os.path.getsize(os.path.join(repo, x)))))
    n = 0
    for r in tsv(files):
        if r[0] == "D": bad("%s is named after one of the four runs but is not one (e.g. SP_AMENDMENT1 A1.5's RUN_stop1): tell Claude" % r[1]); continue
        if r[0] != "F" or len(r) != 4: bad("malformed line of the file listing: %r" % r); continue
        p, size, mtime = r[1], r[2], r[3]
        st = step_of(p)
        if st is None: bad("a file in no step folder of the four runs: %s: tell Claude" % p); continue
        if st not in done: continue
        n += 1
        if (p, size, mtime) not in known and (p, size) not in known_xz:
            bad("%s is in %s, which a batch has taken, but no batch archived or committed it with this size and time "
                "(%s, %s): tell Claude" % (p, st, size, mtime))
    if not BAD: print("file check: each of the %d files now in the %d steps that batches have taken was archived or committed by "
                      "one, with the same size and modification time" % (n, len(done)))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "stage": stage(a[1], a[2], a[3])
    elif len(a) == 3 and a[0] == "pcarchive": pcarchive(a[1], a[2])
    elif len(a) == 2 and a[0] == "precheck": precheck(a[1])
    elif len(a) == 2 and a[0] == "extras": extras(a[1])
    elif len(a) == 3 and a[0] == "track": track(a[1], a[2])
    elif len(a) == 2 and a[0] == "postcheck": postcheck(a[1])
    else: sys.exit(__doc__)
    if BAD:
        print("FAILED:\n  " + "\n  ".join(BAD[:40]))
        sys.exit(1)
