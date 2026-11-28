python3 -c '
import hashlib, lzma, os, re, subprocess, sys, tarfile, time, zlib
HOST = "18660916@hpc"
R = "/home/jess/Desktop/chorismate-thesis-results"
M = "/media/jess"
W = "/home/jess/Downloads"
OUT = W + "/hpc_cleanup_20261128"
FC = "00_admin/hpc_full_copy_20261127"
BATCHES = ["01_home_other", "02_sysdev_other", "03_phase2.2", "04_qmmm_other", "05_qmmm_19_ensemble", "06_qmmm_24_sp_barriers", "07_amber_md"]
TYPES = [
    ("ORCA scratch", re.compile(r"\.tmp(\.[0-9]+)?$")),
    ("hpc1 archive copy", re.compile(r"^hpc_all_files_.*\.tar\.xz$")),
    ("wavefunction", re.compile(r"\.gbw[0-9]?$")),
    ("density", re.compile(r"\.densities(info)?$")),
    ("MD trajectory", re.compile(r"\.nc$")),
    ("MD restart", re.compile(r"\.mdrestart$")),
]
T0 = time.time()
def now():
    return time.strftime("%H:%M")
def stop(m):
    print("CLEANHPC STOPPED: " + m + " Send Claude everything printed above.")
    sys.exit(1)
def kind(p):
    b = p.rsplit("/", 1)[-1]
    for k, rx in TYPES:
        if rx.search(b):
            return k
    return None
def git(*a):
    return subprocess.run(["git", "-C", R] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
def rem(cmd, data=None):
    r = subprocess.run(["ssh", HOST, cmd], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        stop("hpc1 did not answer or the command failed (" + r.stderr.decode(errors="replace").strip()[-300:] + "). Nothing more was deleted.")
    return r.stdout
class HR:
    def __init__(s, f):
        s.f, s.h = f, hashlib.sha256()
    def read(s, n=-1):
        b = s.f.read(n)
        s.h.update(b)
        return b
def sha_fo(fo):
    h = hashlib.sha256()
    for b in iter(lambda: fo.read(1 << 22), b""):
        h.update(b)
    return h.hexdigest()
print("CLEANHPC at " + time.strftime("%a %d %b %Y %H:%M:%S"))
drives = [os.path.join(M, d) for d in sorted(os.listdir(M)) if os.path.isdir(os.path.join(M, d)) and os.stat(os.path.join(M, d)).st_dev != os.stat(M).st_dev] if os.path.isdir(M) else []
if len(drives) != 1:
    stop("expected exactly one drive under /media/jess and found %d. Nothing was deleted." % len(drives))
D = drives[0]
A = os.path.join(D, "chorismate-hpc-archive")
if not os.path.isfile(os.path.join(W, "pc_downloads_copy_20261128", "DONE")):
    stop("the copy of Downloads (COPYPC) has not finished. Everything is copied before anything is deleted. Nothing was deleted.")
if git("fetch", "-q", "origin").returncode != 0:
    stop("GitHub could not be reached. Nothing was deleted.")
if git("rev-parse", "HEAD").stdout != git("rev-parse", "origin/main").stdout or git("status", "--porcelain", "--untracked-files=all").stdout.strip():
    stop("the results repository is not clean and level with GitHub. Nothing was deleted.")
if git("merge-base", "--is-ancestor", "2d345c7f7a928612ffee2c6816396a0108d641fc", "HEAD").returncode != 0:
    stop("the results repository does not hold the records of the hpc1 copy (2d345c7f). Nothing was deleted.")
if os.path.exists(os.path.join(OUT, "DONE")):
    print("CLEANHPC DONE before (see %s). Nothing more to do." % OUT)
    sys.exit(0)
q = rem("qstat -u 18660916 2>/dev/null | grep -c 18660916; true").decode().strip()
if q not in ("", "0"):
    stop("a job of yours is in the queue on hpc1. Nothing was deleted.")
os.makedirs(OUT, exist_ok=True)
print("1. the files to delete, from the committed records of the copy")
cand, where = {}, {}
for b in BATCHES:
    bd = os.path.join(R, FC, b)
    copied = set(l.rstrip("\n") for l in open(os.path.join(bd, "COPIED.lst"), encoding="utf-8", errors="surrogateescape"))
    already = {}
    for l in list(open(os.path.join(bd, "ON_THE_DRIVE_ALREADY.tsv"), encoding="utf-8", errors="surrogateescape"))[1:]:
        f = l.rstrip("\n").split("\t")
        already[f[0]] = f[2]
    for l in open(os.path.join(bd, "MANIFEST.sha256"), encoding="utf-8", errors="surrogateescape"):
        l = l.rstrip("\n")
        p, h = l[66:], l[:64]
        if kind(p) is None:
            continue
        if p in copied:
            where[p] = ("batch", b)
        elif p in already:
            where[p] = ("already", already[p])
        else:
            stop("%s is in the manifest of %s but neither copied nor listed as on the drive already. Nothing was deleted." % (p, b))
        cand[p] = h
n_k = {}
for p in cand:
    n_k[kind(p)] = n_k.get(kind(p), 0) + 1
print("   %d files: %s" % (len(cand), "; ".join("%s %d" % (k, n_k.get(k, 0)) for k, rx in TYPES)))
print("2. %s confirming on the drive that each of them is there, by reading the archives that hold them ..." % now())
need_sha = set(cand.values())
ondrive = {}
def scan_archive(path, mode, want_sha, label):
    try:
        scan1(path, mode, want_sha, label)
    except (tarfile.TarError, OSError, EOFError, zlib.error, lzma.LZMAError) as e:
        stop("the archive %s on the drive could not be read to its end (%s). Nothing was deleted." % (os.path.relpath(path, D), e))
def scan1(path, mode, want_sha, label):
    with open(path, "rb") as raw:
        hr = HR(raw)
        with tarfile.open(fileobj=hr, mode=mode) as tf:
            for mi in tf:
                if mi.isfile():
                    h = sha_fo(tf.extractfile(mi))
                    if h in need_sha:
                        ondrive.setdefault(h, label + ": " + mi.name)
        while hr.read(1 << 22):
            pass
    if hr.h.hexdigest() != want_sha:
        stop("the archive %s on the drive is not the recorded file. Nothing was deleted." % os.path.relpath(path, D))
def rec_lines(d):
    out = []
    for l in open(os.path.join(R, d, "PC_ARCHIVES.tsv")):
        f = l.rstrip("\n").split("\t")
        if l.startswith(chr(35)) or len(f) < 3:
            continue
        k = [i for i, x in enumerate(f) if re.fullmatch("[0-9a-f]{64}", x)]
        out.append((f[k[0] - 2], int(f[k[0] - 1]), f[k[0]]))
    return out
xz = None
def find_xz(rel, nbytes, d):
    global xz
    for r in (rel, rel.replace("$NAME", os.path.basename(d))):
        p = os.path.join(A, r)
        if os.path.isfile(p) and os.path.getsize(p) == nbytes:
            return p
    if xz is None:
        xz = [os.path.join(r, f) for r, ds, fs in os.walk(A) for f in fs if f.endswith(".tar.xz")]
    c = [x for x in xz if os.path.getsize(x) == nbytes]
    if len(c) != 1:
        stop("the archive %s is not on the drive (or not only once by its size). Nothing was deleted." % rel)
    return c[0]
for b in BATCHES:
    if not any(w == ("batch", b) for w in where.values()):
        continue
    rel, nb, h = rec_lines(os.path.join(FC, b))[0]
    p = os.path.join(A, rel)
    if not os.path.isfile(p) or os.path.getsize(p) != nb:
        stop("the archive %s is not on the drive as recorded. Nothing was deleted." % rel)
    print("   %s reading %s (%d MB) ..." % (now(), rel, nb // 1048576))
    scan_archive(p, "r|gz" if rel.endswith(".gz") else "r|", h, rel)
recdirs, files_same = set(), set()
for p, w in where.items():
    if w[0] == "already":
        if w[1].startswith("the archive recorded in "):
            recdirs.add(w[1][len("the archive recorded in "):])
        elif w[1].startswith("the same file as "):
            files_same.add(w[1][len("the same file as "):])
        else:
            stop("cannot read where %s is on the drive (%s). Nothing was deleted." % (p, w[1]))
for d in sorted(recdirs):
    for rel, nb, h in rec_lines(d):
        p = find_xz(rel, nb, d)
        print("   %s reading %s (%d MB) ..." % (now(), os.path.relpath(p, A), nb // 1048576))
        scan_archive(p, "r|xz", h, os.path.relpath(p, A))
for rp in sorted(files_same):
    p = os.path.join(D, rp)
    if not os.path.isfile(p):
        stop("%s is not on the drive. Nothing was deleted." % rp)
    with open(p, "rb") as f:
        h = sha_fo(f)
    if h in need_sha:
        ondrive.setdefault(h, rp)
conf = [p for p in cand if cand[p] in ondrive]
print("   %s confirmed on the drive: %d of the %d files" % (now(), len(conf), len(cand)))
print("3. %s taking the sha256 of each of them on hpc1 again (a long step, prints nothing) ..." % now())
lst = b"".join(("./" + p).encode("utf-8", "surrogateescape") + b"\0" for p in sorted(cand))
cur = {}
for l in rem("cd /home/18660916 && xargs -0 -r nice -n 19 sha256sum 2>/dev/null; true", lst).decode("utf-8", "surrogateescape").splitlines():
    if len(l) > 66 and not l.startswith("\\"):
        cur[l[66:][2:] if l[66:].startswith("./") else l[66:]] = l[:64]
dele, kept = [], []
for p in sorted(cand):
    if p not in cur:
        kept.append((p, "not on hpc1 any more"))
    elif cur[p] != cand[p]:
        kept.append((p, "changed on hpc1 since the copy"))
    elif cand[p] not in ondrive:
        kept.append((p, "NOT confirmed on the drive"))
    else:
        dele.append(p)
with open(os.path.join(OUT, "KEPT.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write("path\treason\n" + "".join("%s\t%s\n" % x for x in kept))
with open(os.path.join(OUT, "TO_DELETE.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write("path\tsha256\ttype\twhere it is on the drive (read today)\n" + "".join("%s\t%s\t%s\t%s\n" % (p, cand[p], kind(p), ondrive[cand[p]]) for p in dele))
bad = [x for x in kept if x[1] == "NOT confirmed on the drive"]
print("   to delete: %d files; kept: %d (%d not on hpc1 any more, %d changed since the copy, %d NOT confirmed on the drive)" % (len(dele), len(kept), sum(1 for x in kept if x[1].startswith("not on")), sum(1 for x in kept if x[1].startswith("changed")), len(bad)))
if bad:
    print("   the files not confirmed on the drive are listed in %s/KEPT.tsv and are NOT deleted" % OUT)
if not dele:
    open(os.path.join(OUT, "DONE"), "w").write("nothing deleted\n")
    print("CLEANHPC DONE: nothing to delete.")
    sys.exit(0)
before = rem("du -sk /home/18660916 2>/dev/null | cut -f1; true").decode().strip()
print("4. %s deleting the %d files on hpc1, each confirmed on the drive and unchanged ..." % (now(), len(dele)))
rem("cd /home/18660916 && xargs -0 -r rm -f --", b"".join(("./" + p).encode("utf-8", "surrogateescape") + b"\0" for p in dele))
left = rem("cd /home/18660916 && xargs -0 -r ls -d -- 2>/dev/null; true", b"".join(("./" + p).encode("utf-8", "surrogateescape") + b"\0" for p in dele)).decode("utf-8", "surrogateescape").splitlines()
after = rem("du -sk /home/18660916 2>/dev/null | cut -f1; true").decode().strip()
with open(os.path.join(OUT, "DELETED.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write("path\tsha256\ttype\twhere it is on the drive (read today)\n" + "".join("%s\t%s\t%s\t%s\n" % (p, cand[p], kind(p), ondrive[cand[p]]) for p in dele if "./" + p not in left))
open(os.path.join(OUT, "SUMMARY.txt"), "w").write("CLEANHPC %s\ncandidates %d\ndeleted %d\nkept %d\nstill there after rm %d\nhome on hpc1 before %s KB, after %s KB\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), len(cand), len(dele) - len(left), len(kept), len(left), before, after))
with open(os.path.join(OUT, "STILL_THERE.txt"), "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write("".join(x + "\n" for x in left))
if left:
    stop("%d of the files are still on hpc1 after the deletion (listed in the output folder). The rest were deleted." % len(left))
open(os.path.join(OUT, "DONE"), "w").write("%d deleted\n" % len(dele))
try:
    freed = (int(before) - int(after)) / 1048576.0
except ValueError:
    freed = float("nan")
print("   %s deleted %d files; your home on hpc1 went from %s KB to %s KB (%.1f GB freed)" % (now(), len(dele), before, after, freed))
print("CLEANHPC DONE: every deleted file was confirmed on the drive today and unchanged on hpc1 just before deletion; %d min. Records: %s. Next: send Claude this printout." % ((time.time() - T0) // 60, OUT))
'
