python3 -c '
import hashlib, os, re, subprocess, sys, tarfile, time
HOST = "18660916@hpc"
R = "/home/jess/Desktop/chorismate-thesis-results"
M = "/media/jess"
STAGE = "/home/jess/Downloads/hpc_full_copy_20261127"
SUB = "full_copy_20261127"
X = "-not -path \"./.*\" -not -path \"./envs/*\" -not -path \"./system_development/*\""
BATCHES = [
    ("01_home_other", "find . -type f " + X, "gz"),
    ("02_sysdev_other", "find system_development -type f -not -path \"system_development/04_amber_md/*\" -not -path \"system_development/05_qmmm/*\" -not -path \"system_development/phase2.2/*\"", "gz"),
    ("03_phase2.2", "find system_development/phase2.2 -type f", "gz"),
    ("04_qmmm_other", "find system_development/05_qmmm -type f -not -path \"system_development/05_qmmm/19_ensemble/*\" -not -path \"system_development/05_qmmm/24_sp_barriers/*\"", "gz"),
    ("05_qmmm_19_ensemble", "find system_development/05_qmmm/19_ensemble -type f", "gz"),
    ("06_qmmm_24_sp_barriers", "find system_development/05_qmmm/24_sp_barriers -type f", "gz"),
    ("07_amber_md", "find system_development/04_amber_md -type f", "none"),
]
T0 = time.time()
def now():
    return time.strftime("%H:%M")
def stop(m):
    print("COPYHPC STOPPED: " + m + " Nothing was deleted anywhere. Send Claude everything printed above.")
    sys.exit(1)
def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()
def rem(cmd):
    r = subprocess.run(["ssh", HOST, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        stop("hpc1 did not answer (" + r.stderr.decode(errors="replace").strip()[-300:] + ").")
    return r.stdout
def norm(p):
    return p[2:] if p.startswith("./") else p
print("COPYHPC at " + time.strftime("%a %d %b %Y %H:%M:%S"))
drives = [os.path.join(M, d) for d in sorted(os.listdir(M)) if os.path.isdir(os.path.join(M, d)) and os.stat(os.path.join(M, d)).st_dev != os.stat(M).st_dev] if os.path.isdir(M) else []
if len(drives) != 1:
    stop("expected exactly one drive under /media/jess and found %d. Is the hard drive plugged in?" % len(drives))
D = drives[0]
A = os.path.join(D, "chorismate-hpc-archive")
DEST = os.path.join(A, SUB)
if not os.path.isdir(A):
    stop("there is no chorismate-hpc-archive on the drive.")
if subprocess.run(["git", "-C", R, "merge-base", "--is-ancestor", "86a0734e92f0da2597e8fbc1bc576299a2c3333b", "HEAD"]).returncode != 0:
    stop("the results repository does not hold the commit of the meeting documents (86a0734e).")
os.makedirs(DEST, exist_ok=True)
os.makedirs(STAGE, exist_ok=True)
print("1. what is on the drive already, from the committed records")
recs = []
for r, ds, fs in os.walk(R):
    if ".git" in ds:
        ds.remove(".git")
    if "PC_ARCHIVES.tsv" in fs:
        for l in open(os.path.join(r, "PC_ARCHIVES.tsv")):
            f = l.rstrip("\n").split("\t")
            if l.startswith(chr(35)) or len(f) < 3:
                continue
            k = [i for i, x in enumerate(f) if re.fullmatch("[0-9a-f]{64}", x)]
            if len(k) != 1 or k[0] < 2:
                stop("a line of " + os.path.join(r, "PC_ARCHIVES.tsv") + " could not be read.")
            recs.append((os.path.relpath(r, R), f[k[0] - 2], int(f[k[0] - 1]), f[k[0]]))
arcs = []
for r, ds, fs in os.walk(A):
    if os.path.abspath(r) == os.path.abspath(DEST):
        ds[:] = []
        continue
    for f in fs:
        if f.endswith(".tar.xz"):
            arcs.append(os.path.join(r, f))
print("   reading the %d archives on the drive to take their sha256 (a minute or two) ..." % len(arcs))
asha = {}
for p in arcs:
    asha.setdefault(sha_file(p), p)
okdirs, verified = set(), {}
for src, rel, nbytes, h in recs:
    if rel.startswith(SUB + "/"):
        continue
    if h in asha and os.path.getsize(asha[h]) == nbytes:
        okdirs.add(src)
        verified[h] = os.path.relpath(asha[h], D)
    else:
        stop("the archive recorded in %s/PC_ARCHIVES.tsv (%s) is not on the drive as recorded." % (src, rel))
print("   %d recorded archives, every one on the drive and the recorded file" % len(recs))
cov = {}
def addman(path, prefix, where):
    for l in open(path, errors="replace"):
        l = l.rstrip("\n")
        if len(l) > 66 and re.match("[0-9a-f]{64}  ", l):
            cov[prefix + norm(l[66:])] = (l[:64], where)
C6 = os.path.join(R, "phase2.2/cs_stage6")
for r, ds, fs in os.walk(C6):
    if "HPC_MANIFEST.sha256" in fs and "PC_ARCHIVES.tsv" in fs:
        rel = os.path.relpath(r, R)
        if rel in okdirs:
            addman(os.path.join(r, "HPC_MANIFEST.sha256"), "system_development/phase2.2/cs_stage6/" + os.path.relpath(r, C6) + "/", "the archive recorded in " + rel)
for sub in ("00_admin/hpc_cleanup_smoke1/batch_2", "00_admin/hpc_outputs_c4/batch_1"):
    if sub in okdirs:
        for f in sorted(os.listdir(os.path.join(R, sub))):
            if f.startswith("PCMANIFEST_") and f.endswith(".sha256"):
                addman(os.path.join(R, sub, f), "system_development/", "the archive recorded in " + sub)
for sub, man, prefix in (("05_qmmm/19_ensemble/active_regions_x89", "hpc_neb_active_regions_band30.MANIFEST.sha256", "system_development/"), ("phase2.2/cs_stage5/exploratory/dev_A", "hpc_all_files_dev_A.MANIFEST.sha256", "system_development/phase2.2/")):
    if sub in okdirs:
        addman(os.path.join(R, sub, man), prefix, "the archive recorded in " + sub)
loose = {}
for r, ds, fs in os.walk(A):
    if os.path.abspath(r) == os.path.abspath(DEST):
        ds[:] = []
        continue
    for f in fs:
        p = os.path.join(r, f)
        if f.endswith((".tar.xz", ".MANIFEST.sha256")) or not os.path.isfile(p) or os.path.islink(p):
            continue
        rel = os.path.relpath(p, A)
        for c in ("system_development/phase2.2/cs_stage6/" + rel, "system_development/" + rel):
            loose[c] = p
print("   files named in the committed manifests: %d; loose files in the archive folder: %d" % (len(cov), len(set(loose.values()))))
lsha = {}
tot_files = tot_bytes = tot_cov = tot_cp = tot_cpb = 0
for name, find, comp in BATCHES:
    t1 = time.time()
    SD = os.path.join(STAGE, name)
    fin = os.path.join(DEST, name + (".tar.gz" if comp == "gz" else ".tar"))
    if os.path.exists(os.path.join(SD, "DONE")):
        d = open(os.path.join(SD, "DONE")).read().split()
        if d and d[0] == "empty":
            print("2. %s: done before, nothing to copy" % name)
            continue
        if len(d) >= 2 and os.path.exists(fin) and os.path.getsize(fin) == int(d[1]):
            print("2. %s: done before, the archive is on the drive (%d MB)" % (name, int(d[1]) // 1048576))
            continue
        stop("%s is marked done but its archive on the drive is missing or of another size." % name)
    os.makedirs(SD, exist_ok=True)
    print("2. %s, %s: listing it on hpc1 and taking the sha256 of every file (minutes) ..." % (name, now()))
    sizes = {}
    for x in rem("cd /home/18660916 && " + find + " -printf \"%s\\t%p\\0\"").split(b"\0"):
        if x:
            s, p = x.decode("utf-8", "surrogateescape").split("\t", 1)
            sizes[norm(p)] = int(s)
    if not sizes:
        open(os.path.join(SD, "DONE"), "w").write("empty\n")
        print("   no files")
        continue
    man = {}
    for l in rem("cd /home/18660916 && " + find + " -print0 | xargs -0 -r nice -n 19 sha256sum").decode("utf-8", "surrogateescape").splitlines():
        if l.startswith("\\"):
            stop("a file name in %s holds a backslash or a line break: %s" % (name, l[:200]))
        if len(l) > 66:
            man[norm(l[66:])] = l[:64]
    if set(man) != set(sizes):
        stop("the list of files and the list of checksums of %s do not agree (%d against %d)." % (name, len(sizes), len(man)))
    links = rem("cd /home/18660916 && " + find.replace("-type f", "-type l", 1) + " -printf \"%p\\t%l\\n\"").decode("utf-8", "surrogateescape")
    covd, tocopy = {}, []
    for p in sorted(man):
        h = man[p]
        if p in cov and cov[p][0] == h:
            covd[p] = cov[p][1]
        elif h in verified:
            covd[p] = "the same file as " + verified[h]
        elif p in loose and os.path.getsize(loose[p]) == sizes[p]:
            if loose[p] not in lsha:
                lsha[loose[p]] = sha_file(loose[p])
            if lsha[loose[p]] == h:
                covd[p] = "the same file as " + os.path.relpath(loose[p], D)
            else:
                tocopy.append(p)
        else:
            tocopy.append(p)
    with open(os.path.join(SD, "MANIFEST.sha256"), "w", encoding="utf-8", errors="surrogateescape") as f:
        for p in sorted(man):
            f.write("%s  %s\n" % (man[p], p))
    with open(os.path.join(SD, "ON_THE_DRIVE_ALREADY.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("path\tsha256\twhere it is on the drive\n")
        for p in sorted(covd):
            f.write("%s\t%s\t%s\n" % (p, man[p], covd[p]))
    with open(os.path.join(SD, "LINKS.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("link\ttarget\n" + links)
    nb = sum(sizes.values())
    cb = sum(sizes[p] for p in tocopy)
    print("   %d files, %.2f GB; on the drive already %d files, %.2f GB; to copy %d files, %.2f GB" % (len(man), nb / 2**30, len(covd), (nb - cb) / 2**30, len(tocopy), cb / 2**30))
    tot_files += len(man); tot_bytes += nb; tot_cov += len(covd)
    if not tocopy:
        open(os.path.join(SD, "DONE"), "w").write("empty\n")
        continue
    part = fin + ".part"
    cmd = "set -o pipefail; cd /home/18660916 && nice -n 19 tar --null --no-recursion -T - -cf -" + (" | nice -n 19 gzip -1" if comp == "gz" else "")
    errf = os.path.join(SD, "tar_stderr.txt")
    print("   %s copying to the drive: %s (progress every 10 min) ..." % (now(), os.path.relpath(fin, D)))
    with open(part, "wb") as out, open(errf, "wb") as err:
        pr = subprocess.Popen(["ssh", HOST, cmd], stdin=subprocess.PIPE, stdout=out, stderr=err)
        pr.stdin.write(b"".join(("./" + p).encode("utf-8", "surrogateescape") + b"\0" for p in tocopy))
        pr.stdin.close()
        t2, nxt = time.time(), time.time() + 600
        while pr.poll() is None:
            time.sleep(5)
            if time.time() >= nxt:
                w = os.path.getsize(part)
                print("      ... %d MB on the drive after %d min (%.1f MB/s)" % (w // 1048576, (time.time() - t2) // 60, w / 1048576 / max(1, time.time() - t2)))
                nxt += 600
    if pr.returncode != 0:
        stop("the copy of %s ended with an error (see %s). The unfinished file %s is left on the drive and will be written again on the next run." % (name, errf, part))
    w = os.path.getsize(part)
    print("   %s copied %d MB in %d min (%.1f MB/s); now reading it back from the drive, file by file ..." % (now(), w // 1048576, (time.time() - t2) // 60, w / 1048576 / max(1, time.time() - t2)))
    class HR:
        def __init__(s, f):
            s.f, s.h = f, hashlib.sha256()
        def read(s, n=-1):
            b = s.f.read(n)
            s.h.update(b)
            return b
    seen = set()
    with open(part, "rb") as raw:
        hr = HR(raw)
        with tarfile.open(fileobj=hr, mode="r|gz" if comp == "gz" else "r|") as tf:
            for mi in tf:
                if not mi.isfile():
                    stop("the archive of %s holds something that is not a file: %s" % (name, mi.name))
                p = norm(mi.name)
                if p not in man or p in seen:
                    stop("the archive of %s holds %s, which it should not." % (name, p))
                h = hashlib.sha256()
                fo = tf.extractfile(mi)
                for b in iter(lambda: fo.read(1 << 22), b""):
                    h.update(b)
                if h.hexdigest() != man[p]:
                    stop("in the archive of %s, %s is not the file on hpc1." % (name, p))
                seen.add(p)
        while hr.read(1 << 22):
            pass
        ash = hr.h.hexdigest()
    if seen != set(tocopy):
        stop("the archive of %s holds %d of the %d files it should." % (name, len(seen), len(tocopy)))
    os.replace(part, fin)
    with open(os.path.join(SD, "PC_ARCHIVES.tsv"), "w") as f:
        f.write(chr(35) + " PC archive (relative to the archive folder on the drive, chorismate-hpc-archive)\tbytes\tsha256\tmembers\n")
        f.write("%s/%s\t%d\t%s\t%d\n" % (SUB, os.path.basename(fin), w, ash, len(seen)))
    with open(os.path.join(SD, "COPIED.lst"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("".join(p + "\n" for p in sorted(seen)))
    for f in ("MANIFEST.sha256", "ON_THE_DRIVE_ALREADY.tsv", "LINKS.tsv", "PC_ARCHIVES.tsv", "COPIED.lst"):
        with open(os.path.join(SD, f), "rb") as a, open(os.path.join(DEST, name + "." + f), "wb") as b:
            b.write(a.read())
    open(os.path.join(SD, "DONE"), "w").write("%s %d %d\n" % (ash, w, len(seen)))
    tot_cp += len(seen); tot_cpb += cb
    print("   %s %s: every one of the %d files read back from the drive is the file on hpc1; archive sha256 %s" % (now(), name, len(seen), ash[:16]))
print("3. this run: %d files listed, %.1f GB; on the drive already %d files; copied %d files, %.1f GB; %d min" % (tot_files, tot_bytes / 2**30, tot_cov, tot_cp, tot_cpb / 2**30, (time.time() - T0) // 60))
print("COPYHPC DONE: everything on hpc1 except the software folders (.conda, envs, .cache, .local) and .ssh is on the drive, read back and checked. Nothing was deleted. Next: send Claude this printout.")
'
