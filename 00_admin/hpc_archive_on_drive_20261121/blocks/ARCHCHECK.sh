python3 -c '
import hashlib, os, re, subprocess, sys, time
R = "/home/jess/Desktop/chorismate-thesis-results"
M = "/media/jess"
print("ARCHCHECK at " + time.strftime("%a %d %b %Y %H:%M:%S"))
def stop(msg):
    print("ARCHCHECK STOPPED: " + msg + " Nothing was changed. Send Claude everything printed above.")
    sys.exit(1)
if not os.path.isdir(M):
    stop("there is no /media/jess, so the hard drive is not plugged in.")
drives = [os.path.join(M, d) for d in sorted(os.listdir(M)) if os.path.isdir(os.path.join(M, d)) and os.stat(os.path.join(M, d)).st_dev != os.stat(M).st_dev]
if len(drives) != 1:
    stop("expected exactly one drive under /media/jess and found %d." % len(drives))
D = drives[0]
A = os.path.join(D, "chorismate-hpc-archive")
if not os.path.isdir(A):
    stop("there is no chorismate-hpc-archive on " + D + ".")
fs = [l.split()[2] for l in open("/proc/mounts") if l.split()[1].replace("\\040", " ") == D]
st = os.statvfs(D)
print("1. The drive: %s (%s), %d MB free" % (D, fs[-1] if fs else "?", st.f_bavail * st.f_frsize // 1048576))
print("   the old archive folder on the Desktop: " + ("STILL THERE" if os.path.lexists("/home/jess/Desktop/chorismate-hpc-archive") else "gone, as it should be"))
print("   attempt_3_final_analysis: on the drive " + ("yes" if os.path.isdir(os.path.join(D, "attempt_3_final_analysis")) else "NO") + "; in Downloads " + ("STILL THERE" if os.path.lexists("/home/jess/Downloads/attempt_3_final_analysis") else "gone, as it should be"))
print("   left-over folder moved_from_pc_20261120 on the drive: " + ("yes (not needed; you can delete it in the file manager)" if os.path.exists(os.path.join(D, "moved_from_pc_20261120")) else "no"))
head = subprocess.run(["git", "-C", R, "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE).stdout.decode().strip()
dirty = subprocess.run(["git", "-C", R, "status", "--porcelain", "--untracked-files=all"], stdout=subprocess.PIPE).stdout.decode().strip()
print("2. The results repository: at %s, %s" % (head, "clean" if not dirty else "NOT CLEAN"))
recs = []
for r, ds, fs_ in os.walk(R):
    if ".git" in ds:
        ds.remove(".git")
    if "PC_ARCHIVES.tsv" in fs_:
        for l in open(os.path.join(r, "PC_ARCHIVES.tsv")):
            f = l.rstrip("\n").split("\t")
            if l.startswith(chr(35)) or len(f) < 3:
                continue
            k = [i for i, x in enumerate(f) if re.fullmatch("[0-9a-f]{64}", x)]
            if len(k) != 1 or k[0] < 2:
                stop("a line of " + os.path.join(r, "PC_ARCHIVES.tsv") + " could not be read.")
            recs.append((os.path.relpath(r, R), f[k[0] - 2], int(f[k[0] - 1]), f[k[0]]))
print("   records of archives in it: %d, in %d files named PC_ARCHIVES.tsv" % (len(recs), len(set(x[0] for x in recs))))
arcs, other_n, other_b = [], 0, 0
for r, ds, fs_ in os.walk(A):
    for f in fs_:
        p = os.path.join(r, f)
        if f.endswith(".tar.xz"):
            arcs.append(p)
        else:
            other_n += 1
            other_b += os.path.getsize(p)
tot = sum(os.path.getsize(p) for p in arcs)
print("3. On the drive: %d archives (.tar.xz), %d MB; %d other files, %d MB" % (len(arcs), tot // 1048576, other_n, other_b // 1048576))
print("   reading every archive to take its sha256 (this is the slow part) ...")
sha, done, t0, nxt = {}, 0, time.time(), 0.25
for p in sorted(arcs):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    sha[p] = h.hexdigest()
    done += os.path.getsize(p)
    while tot and nxt <= 1.0 and done >= nxt * tot:
        print("   ... %d %% read after %d min" % (int(nxt * 100), (time.time() - t0) // 60))
        nxt += 0.25
bysha = {}
for p, h in sha.items():
    bysha.setdefault(h, []).append(p)
ok, moved, bad, used = 0, [], [], set()
for src, rel, nbytes, h in recs:
    p = os.path.join(A, rel)
    if p in sha and sha[p] == h and os.path.getsize(p) == nbytes:
        ok += 1
        used.add(p)
    elif h in bysha and os.path.getsize(bysha[h][0]) == nbytes:
        moved.append((src, rel, os.path.relpath(bysha[h][0], A)))
        used.add(bysha[h][0])
    elif p in sha:
        bad.append("%s: %s is on the drive but is NOT the recorded file" % (src, rel))
    else:
        bad.append("%s: %s is NOT on the drive" % (src, rel))
print("4. The %d records against the drive:" % len(recs))
print("   the same file, at the recorded place: %d" % ok)
print("   the same file, under another name: %d" % len(moved))
for src, rel, where in moved:
    print("      %s records %s; it is %s" % (src, rel, where))
print("   NOT matched: %d" % len(bad))
for b in bad:
    print("      " + b)
extra = sorted(os.path.relpath(p, A) for p in arcs if p not in used)
print("5. Archives on the drive that no record names: %d" % len(extra))
for e in extra[:12]:
    print("      %s  %d MB" % (e, os.path.getsize(os.path.join(A, e)) // 1048576))
if len(extra) > 12:
    print("      ... and %d more" % (len(extra) - 12))
d44 = [x for x in recs if x[1].endswith("hpc_all_files_d44.tar.xz")]
print("6. D44: " + ("its archive on the drive is the committed one, sha256 %s..." % d44[0][3][:16] if d44 and os.path.join(A, d44[0][1]) in used else "ITS ARCHIVE IS NOT MATCHED"))
print("ARCHCHECK DONE: this only read and changed nothing. Next: CLEANPC, if line 6 says the D44 archive is the committed one. If it does not, stop and send this printout to Claude.")
'
