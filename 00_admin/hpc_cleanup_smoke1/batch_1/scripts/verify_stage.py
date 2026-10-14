#!/usr/bin/env python3
"""
verify_stage.py - PC side of x76 (the clean-up of SP smoke test 1). Python 3, standard library plus the tar and xz
commands. Writes nothing in the repo.

  verify_stage.py stage W REPO     W = a fetched hpc1 stage folder (batch_N). Before anything is committed: every
                                   archive is extracted and each member's sha256 compared with its manifest; every
                                   compressed output is decompressed and compared with its original's sha256; every
                                   list agrees with the inventory, file by file; nothing to be committed is over 95 MB or
                                   exists in the repo already; no frequency Hessian is on the deletion list
  verify_stage.py postcheck W      after the deletion: every listed file deleted (or compressed in place), and every file
                                   that was to stay still there with its recorded size; prints the summary for
                                   POSTCHECK.txt
"""
import hashlib, os, re, subprocess, sys, tempfile

REL0 = "05_qmmm/24_sp_barriers/"
RUNS = ("f42436_r8", "f42436_r6")
GIT_MAX = 95 * 1000000
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
            if l[64:66] != "  ": bad("%s: malformed line %r" % (os.path.basename(p), l[:80])); continue
            D[l[66:]] = l[:64]
    return D
def tsv(p): return [l.rstrip("\n").split("\t") for l in open(p) if l.strip() and not l.startswith("#")]
def inventory(w):
    I = {}
    for r in tsv(w + "/inventory.tsv"):
        if len(r) != 5: bad("inventory.tsv: malformed row %r" % r[:3]); continue
        size, mtime, path, cat, h = r
        I[path] = (cat, int(size), h)
    return I
def in_runs(p):
    q = p.split("/")
    return p.startswith(REL0) and len(q) >= 4 and q[2] in RUNS and ".." not in q

def stage(w, repo):
    for f in ("DONE", "STEPS.txt", "SUMMARY.txt", "inventory.tsv", "archives.tsv", "ARCHIVES_BUILT.tsv", "individual.tsv",
              "INDIV.sha256", "INDIV_XZ.sha256", "as_is.tsv", "AS_IS.sha256", "delete.tsv", "DELETE_CHECKSUMS.sha256",
              "keep.tsv"):
        if not os.path.isfile(os.path.join(w, f)): bad("missing " + f)
    if BAD: return
    I = inventory(w)
    batch = dict((p, v) for p, v in I.items() if v[0] != "-")
    cat = lambda c: dict((p, v) for p, v in batch.items() if v[0] == c)
    for p in batch:
        if not in_runs(p): bad("a batch file outside the two run folders: " + p)
    # archives: lists, manifests, members
    A = tsv(w + "/archives.tsv"); arch = {}
    for name, size, path in A: arch.setdefault(name, []).append(path)
    if sorted(p for n, s, p in A) != sorted(cat("archive")): bad("archives.tsv and the inventory's archive files differ")
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
    if sorted(ind) != sorted(cat("compress")) or sorted(IS) != sorted(ind) or sorted(IX) != sorted(p + ".xz" for p in ind):
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
    if sorted(asis) != sorted(cat("as_is")) or sorted(AS) != sorted(asis): bad("as_is lists differ from the inventory")
    for p in asis:
        if p not in batch: bad("as_is.tsv lists %s, which the inventory does not have in this batch" % p); continue
        q = os.path.join(w, "asis", p)
        if not os.path.isfile(q) or sha(q) != AS.get(p) or AS.get(p) != batch[p][2] or os.path.getsize(q) > GIT_MAX:
            bad("the copy of %s is missing, changed or over 95 MB" % p)
        elif subprocess.run(["xz", "-t", q]).returncode != 0: bad("the job's compressed file %s fails xz -t" % p)
    # deletion and keep lists
    dl = dict((r[2], (r[0], int(r[1]))) for r in tsv(w + "/delete.tsv")); DS = sums(w + "/DELETE_CHECKSUMS.sha256")
    if sorted(dl) != sorted(cat("delete")) or sorted(DS) != sorted(dl): bad("delete lists differ from the inventory")
    for p in dl:
        if p not in batch: bad("delete.tsv lists %s, which the inventory does not have in this batch" % p); continue
        if DS.get(p) != batch[p][2]: bad("DELETE_CHECKSUMS.sha256 of %s differs from the inventory" % p)
        q = p.split("/")
        if len(q) != 5: bad("a file to delete outside a step folder: " + p); continue
        if p.endswith(".hess") and (q[3].endswith("_freq") or q[3] == "irc"): bad("a frequency Hessian is on the deletion list: " + p)
        if dl[p][0].startswith("full-system trajectory"):        # its frames must be reproducible from committed files
            d = os.path.dirname(p); act = os.path.join(d, os.path.basename(p)[:-len("_trj.xyz")] + ".activeRegion_trj.xyz")
            if batch.get(act, ("",))[0] not in ("archive", "compress") or batch.get(os.path.join(d, "start.xyz"), ("",))[0] != "archive":
                bad("%s is to be deleted but its activeRegion trajectory or start.xyz is not committed" % p)
    kp = [r[1] for r in tsv(w + "/keep.tsv")]
    if sorted(kp) != sorted(cat("keep")): bad("keep.tsv differs from the inventory")
    # nothing to be committed exists in the repo already
    targets = [n for n in arch] + [n[:-len(".tar.xz")] + ".MANIFEST.sha256" for n in arch] + [p + ".xz" for p in ind] + list(asis)
    if len(set(targets)) != len(targets): bad("two files would be committed to the same path")
    for t in targets:
        if os.path.lexists(os.path.join(repo, t)): bad("would overwrite %s in the repo" % t)
    S = dict((c, (len(cat(c)), sum(v[1] for v in cat(c).values()))) for c in ("archive", "compress", "as_is", "delete", "keep"))
    print("verified: %d archives (%d members) extracted and matched; %d outputs compressed and matched; %d files as they"
          " are; %d files listed for deletion (%.2f GB); %d kept on hpc1" % (len(arch), S["archive"][0], S["compress"][0],
          S["as_is"][0], S["delete"][0], S["delete"][1] / 1e9, S["keep"][0]))

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
    n = {"DELETED": 0, "COMPRESSED": 0}; other = []
    for p in list(DS) + list(IS):
        st = log.get(p)
        if st is None: bad("not in DELETED.log: " + p); continue
        if st in n: n[st] += 1
        else: other.append("%s %s" % (st, p))
        if st in ("DELETED", "COMPRESSED") and p in rem: bad("still present after %s: %s" % (st, p))
        if st == "COMPRESSED" and p + ".xz" not in rem: bad("compressed copy missing: %s.xz" % p)
    for p, (c, size, h) in batch.items():
        if c in ("archive", "as_is", "keep"):
            if p not in rem: bad("a file that was to stay is gone: " + p)
            elif c != "keep" or rem[p] != "link":
                if rem[p] != "link" and int(rem[p]) != size: bad("a file that was to stay changed size: " + p)
    gone = [p for p in batch if p not in rem and p not in DS and p not in IS]      # steps of running jobs may change
    for p in gone: bad("gone although not listed: " + p)
    freed = sum(batch[p][1] for p in DS if log.get(p) == "DELETED")
    print("post-check: %d deleted (%.2f GB), %d compressed in place, %d not acted on%s; every file that was to stay is"
          " present with its recorded size; no other file of this batch is gone" % (
          n["DELETED"], freed / 1e9, n["COMPRESSED"], len(other), (" (" + "; ".join(other) + ")") if other else ""))

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "stage": stage(a[1], a[2])
    elif len(a) == 2 and a[0] == "postcheck": postcheck(a[1])
    else: sys.exit(__doc__)
    if BAD:
        print("FAILED:\n  " + "\n  ".join(BAD[:40]))
        sys.exit(1)
