#!/usr/bin/env python3
"""
verify_c4.py - PC side of x80 (C4's re-optimisation runs kept as physical files). Python 3, standard library plus the tar
and xz commands. Writes nothing in the repo.

  verify_c4.py stage W REPO PC     W = a fetched hpc1 stage folder (batch_N); PC = the folder with the fetched PC
                                   archives (RUN.tar.xz). Before anything is committed: every PC archive is read member
                                   by member, each member's sha256 compared with the inventory, and its members are
                                   exactly the batch's regular files of that run; every git archive is extracted and each
                                   member compared with its manifest; every file compressed one by one is decompressed
                                   and compared with its original's sha256; every list agrees with the inventory; nothing
                                   to be committed is over 95 MB or exists in the repo already, and all of it together
                                   stays under 1.5 GB (GitHub refuses a push over 2 GB)
  verify_c4.py pcarchive A M       A = a PC archive, M = its manifest (sha256  path): every member present once, with its
                                   sha256, and nothing else
  verify_c4.py track ADMIN FILES   FILES = c4_collect.py files output: every file now in a run that a batch has taken
                                   (RUNS.txt) was archived or committed by a batch with this size and modification time
                                   (to the minute); no run folder holds a folder; no folder is named like a run without
                                   being one
"""
import hashlib, os, re, subprocess, sys, tarfile, tempfile

REL0 = "05_qmmm/23_c4_reactant/"
CATS = ("git_text", "git_xz", "git_asis", "pc_keep", "scratch", "link")
GIT_MAX = 95 * 1000000
PUSH_MAX = 1500 * 1000000
RUN_RE = re.compile(r"^S[02]_\d+(_c)?$")
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
def run_of(p):
    """the run a path belongs to (a file directly in a run folder), or None"""
    q = p.split("/")
    if not p.startswith(REL0) or len(q) != 4 or not RUN_RE.match(q[2]) or any(x in ("", ".", "..") for x in q): return None
    return q[2]
def pc_members(a):
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
    for f in ("DONE", "RUNS.txt", "SUMMARY.txt", "inventory.tsv", "archives.tsv", "ARCHIVES_BUILT.tsv", "individual.tsv",
              "INDIV.sha256", "INDIV_XZ.sha256", "as_is.tsv", "AS_IS.sha256", "pc_keep.tsv", "links.tsv"):
        if not os.path.isfile(os.path.join(w, f)): bad("missing " + f)
    if BAD: return
    I = inventory(w)
    batch = dict((p, v) for p, v in I.items() if v[0] != "-")
    cat = lambda c: dict((p, v) for p, v in batch.items() if v[0] == c)
    runs = [r[0] for r in tsv(w + "/RUNS.txt")]
    if len(set(runs)) != len(runs) or not all(RUN_RE.match(r) for r in runs): bad("RUNS.txt is malformed")
    for p in batch:
        if run_of(p) not in runs: bad("a batch file outside the batch's run folders: " + p)
    for r in runs:
        if not any(run_of(p) == r for p in batch): bad("run %s has no file in this batch" % r)
    regular = dict((p, v) for p, v in batch.items() if v[0] != "link")
    for r in runs:                                    # PC archives
        lst = os.path.join(w, "PCLIST_%s.txt" % r)
        mine = sorted(p for p in regular if run_of(p) == r)
        if not os.path.isfile(lst): bad("missing PCLIST_%s.txt" % r); continue
        L = [l.rstrip("\n") for l in open(lst) if l.strip()]
        if sorted(L) != mine: bad("PCLIST_%s.txt is not the batch's regular files of that run" % r)
        a = os.path.join(pc, r + ".tar.xz")
        if not os.path.isfile(a): bad("missing PC archive " + a); continue
        got = pc_members(a)
        if got is None: continue
        if sorted(got) != mine: bad("%s: members are not the batch's regular files of %s" % (a, r))
        for p, h in got.items():
            if regular.get(p, ("", 0, ""))[2] != h: bad("%s: member %s does not match the inventory's sha256" % (a, p))
    extra_pc = [f for f in os.listdir(pc) if f.endswith(".tar.xz") and f[:-7] not in runs]
    if extra_pc: bad("PC archives of runs not in this batch: %s" % extra_pc)
    A = tsv(w + "/archives.tsv"); arch = {}       # git archives
    for name, size, path in A: arch.setdefault(name, []).append(path)
    if sorted(p for n, s, p in A) != sorted(cat("git_text")): bad("archives.tsv and the inventory's git_text files differ")
    for name, size, path in A:
        if path not in batch: bad("archives.tsv lists %s, which the inventory does not have in this batch" % path); continue
        if int(size) != batch[path][1]: bad("archives.tsv size of %s differs from the inventory" % path)
        if name != "%s%s/%s" % (REL0, run_of(path), os.path.basename(name)): bad("%s is archived outside its run folder" % path)
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
    ind = dict((r[1], int(r[0])) for r in tsv(w + "/individual.tsv"))     # compressed one by one
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
    asis = dict((r[1], int(r[0])) for r in tsv(w + "/as_is.tsv")); AS = sums(w + "/AS_IS.sha256")
    if sorted(asis) != sorted(cat("git_asis")) or sorted(AS) != sorted(asis): bad("as_is lists differ from the inventory")
    for p in asis:
        if p not in batch: bad("as_is.tsv lists %s, which the inventory does not have in this batch" % p); continue
        q = os.path.join(w, "asis", p)
        if not os.path.isfile(q) or sha(q) != AS.get(p) or AS.get(p) != batch[p][2] or os.path.getsize(q) > GIT_MAX:
            bad("the copy of %s is missing, changed or over 95 MB" % p)
        elif subprocess.run(["xz", "-t", q]).returncode != 0: bad("the job's compressed file %s fails xz -t" % p)
    pk = [(r[2], r[3]) for r in tsv(w + "/pc_keep.tsv")]
    if sorted(p for p, c in pk) != sorted(list(cat("pc_keep")) + list(cat("scratch"))): bad("pc_keep.tsv differs from the inventory")
    for p, c in pk:
        if batch.get(p, ("",))[0] != c: bad("pc_keep.tsv: %s is %s in the inventory, %s in the list" % (p, batch.get(p, ("-",))[0], c))
    lk = [r[0] for r in tsv(w + "/links.tsv")]
    if sorted(lk) != sorted(cat("link")): bad("links.tsv differs from the inventory")
    for p in lk:
        if not re.match(r"^link:[^:]+:[0-9a-f]{64}$", batch[p][2]): bad("the link %s has no recorded target sha256" % p)
    for p in cat("git_xz"):
        if not re.match(r"^[0-9a-f]{64}$", batch[p][2]): bad("no sha256 for " + p)
    targets = [n for n in arch] + [n[:-len(".tar.xz")] + ".MANIFEST.sha256" for n in arch] + [p + ".xz" for p in ind] + list(asis)
    if len(set(targets)) != len(targets): bad("two files would be committed to the same path")
    for t in targets:
        if os.path.lexists(os.path.join(repo, t)): bad("would overwrite %s in the repo" % t)
    gitb = (sum(os.path.getsize(os.path.join(w, "arch", n)) for n in arch) + sum(
            os.path.getsize(os.path.join(w, "indiv", p + ".xz")) for p in ind if os.path.isfile(os.path.join(w, "indiv", p + ".xz")))
            + sum(os.path.getsize(os.path.join(w, "asis", p)) for p in asis if os.path.isfile(os.path.join(w, "asis", p))))
    if gitb > PUSH_MAX: bad("the batch would commit %.2f GB to git (limit 1.5 GB per batch): tell Claude" % (gitb / 1e9))
    S = dict((c, (len(cat(c)), sum(v[1] for v in cat(c).values()))) for c in CATS)
    print("verified: PC archives with all %d regular files (%.2f GB) of %d runs, each with its sha256; git (%.2f GB): %d "
          "archives (%d text files) extracted and matched, %d files compressed one by one and matched, %d as compressed by "
          "the jobs; PC only: %d (%.2f GB; trajectories and binaries) and %d scratch; %d links" % (
          len(regular), sum(v[1] for v in regular.values()) / 1e9, len(runs), gitb / 1e9, len(arch), S["git_text"][0],
          S["git_xz"][0], S["git_asis"][0], S["pc_keep"][0], S["pc_keep"][1] / 1e9, S["scratch"][0], S["link"][0]))

def batch_dirs(admin):
    if not os.path.isdir(admin): return []
    B = [d for d in os.listdir(admin) if re.match(r"^batch_\d+$", d) and os.path.isdir(os.path.join(admin, d))]
    return [os.path.join(admin, d) for d in sorted(B, key=lambda d: int(d[6:]))]
def track(admin, files):
    done, known = set(), set()
    for b in batch_dirs(admin):
        for r in tsv(b + "/RUNS.txt"): done.add(r[0])
        for r in tsv(b + "/inventory.tsv"):
            if len(r) == 5 and r[3] != "-":
                known.add((r[2], "link", "-") if r[3] == "link" or r[4].startswith("link:") else (r[2], r[0], r[1]))
    n = 0
    for r in tsv(files):
        if r[0] == "D": bad("%s is named like a C4 run but is not one of runs.tsv's or their continuations: tell Claude" % r[1]); continue
        if r[0] == "M": bad("%s is missing or a link: tell Claude" % r[1]); continue
        if r[0] == "S": bad("%s is a folder inside a run folder: tell Claude" % r[1]); continue
        if r[0] != "F" or len(r) != 4: bad("malformed line of the file listing: %r" % r); continue
        p, size, mtime = r[1], r[2], r[3]
        run_ = run_of(p)
        if run_ is None: bad("a file outside the run folders: %s: tell Claude" % p); continue
        if run_ not in done: continue
        n += 1
        if (p, size, mtime) not in known:
            bad("%s is in %s, which a batch has taken, but no batch archived or committed it with this size and time "
                "(%s, %s): tell Claude" % (p, run_, size, mtime))
    if not BAD: print("file check: each of the %d files now in the %d runs that batches have taken was archived or committed "
                      "by one, with the same size and modification time" % (n, len(done)))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "stage": stage(a[1], a[2], a[3])
    elif len(a) == 3 and a[0] == "pcarchive": pcarchive(a[1], a[2])
    elif len(a) == 3 and a[0] == "track": track(a[1], a[2])
    else: sys.exit(__doc__)
    if BAD:
        print("FAILED:\n  " + "\n  ".join(BAD[:40]))
        sys.exit(1)
