#!/usr/bin/env bash
# x94_package_memory.sh - RUN ON THE PC (not on hpc1), from anywhere:   bash x94/x94_package_memory.sh
#
# SP Amendment 3: the package's job memory requests. Seven of the eight job types asked PBS for 180 or 250 GB and
# measured under 4.11 GiB in both smoke tests, which left the first wave waiting for nodes it did not need (0 of 256
# jobs finished in the first 44.7 h). This bundle lowers those seven to 64 GB and puts the affected jobs back in the
# queue. job_ts keeps 250 GB: it measured 197 GiB.
#
#  0. checks: the bundle; git, python3, ssh, scp, tar on the PC; both repos clean, on their branches, level with
#     origin; hpc1 reachable and 24_sp_barriers as the first wave left it; the amendment not committed yet;
#  1. commits SP_AMENDMENT3.txt (results) and the amended spa_prepare.py (code), BEFORE anything on hpc1 changes;
#  2. puts the amended generator on hpc1, keeping the superseded one beside it;
#  3. reads every package job's state from PBS and sorts the 32 run folders into untouched and deferred (A3.3);
#  4. generates the run folders again into a scratch folder on hpc1 and proves that only the eight job_*.pbs and
#     GENERATOR_LOG.txt differ, and that each job script differs in its "#PBS -l select=" line alone (A3.4);
#  5. replaces those nine files in the untouched folders only;
#  6. for each untouched folder: deletes its eight queued jobs, checks they are gone, resubmits the eight with the
#     same afterok structure, and records the new ids in SUBMITTED (the first wave's kept as SUBMITTED.wave1);
#  7. commits the record (results package_waves/x94/) and pushes both repos.
#
# NOTHING RUNNING IS TOUCHED. A folder with a job in state R, or with any job output already written, is left exactly
# as it is and listed as deferred for a later bundle. Nothing of the smoke tests or of C4 is touched. No run folder is
# renamed and nothing is deleted on hpc1 except this bundle's own scratch copy. No barrier is read.
# Safe to re-run: a finished step is checked and skipped. Anything unexpected stops it.
# If it stops, nothing after the stop has happened; send Claude the whole output.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
CODE="$HOME/Desktop/chorismate-thesis-code"
HPC="18660916@hpc"
RH=/home/18660916/system_development
SD=$RH/05_qmmm/24_sp_barriers
T=05_qmmm/24_sp_barriers
A2=SP_AMENDMENT2.txt
A3=SP_AMENDMENT3.txt
REC=package_waves/x94
MD_FRAMES="20000 21634 23268 24883 26495 33320 34991 36665 38344 40485 41786 43087 43738 44388 45688 46990 47641 48292 49592 50892 52192 53493 54144 54795 55446 56098 57397 58698 59999"
CI_FRAMES="20000 44388 59999"
JOBNAMES="job_ts job_ts_freq_irc job_r_irc job_r_irc_freq job_p_irc job_p_irc_freq job_r0 job_r0_freq"
TRAILER="Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
stop() { echo "STOP: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }
S=$(mktemp -d); RG=""
trap 'rm -rf "$S"; if [ -n "$RG" ]; then ssh "$HPC" "rm -rf $RG" || echo "NOTE: remove the scratch copy $RG on hpc1 by hand" >&2; fi' EXIT
SPECS=""; RUNS=""
for f in $MD_FRAMES; do SPECS="$SPECS $f:8:md"; RUNS="$RUNS f${f}_r8_a1"; done
for f in $CI_FRAMES; do SPECS="$SPECS $f:8:ci"; RUNS="$RUNS f${f}_r8_ci_a1"; done
NR=$(echo $RUNS | wc -w)

echo "== 0. checks"
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
for t in python3 git ssh scp tar awk; do command -v "$t" > /dev/null || stop "$t is needed on the PC"; done
for r in "$RES" "$CODE"; do
  [ -d "$r/.git" ] || stop "$r is not a git repo"
  [ -z "$(git -C "$r" status --porcelain)" ] || stop "$r has uncommitted changes: commit or stash them first"
done
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ "$(git -C "$CODE" rev-parse --abbrev-ref HEAD)" = tier1-realism ] || stop "the code repo is not on tier1-realism"
for r in "$RES" "$CODE"; do
  br=$(git -C "$r" rev-parse --abbrev-ref HEAD)
  git -C "$r" fetch -q origin "$br" || stop "cannot reach origin for $r"
  [ "$(git -C "$r" rev-parse HEAD)" = "$(git -C "$r" rev-parse "origin/$br")" ] || stop "$r is not level with origin/$br: pull or push first"
done
# the four files this amendment leaves alone must be exactly what it records
while read -r _ nm want; do
  [ -n "${want:-}" ] || continue
  got=$(sha "$RES/$T/$nm") || stop "$nm is missing from the results repo"
  [ "$got" = "$want" ] || stop "$nm in the repo is not the file $A3 records ($got, expected $want)"
done << 'EOS'
sha256 SP_PLAN.txt c8eadbd9a5546fe644fe85a2c7d3e7e47c7117bb61a449a51ce50fb6945df1a6
sha256 SP_AMENDMENT1.txt 8f6128713b07ffc8d257120567d0cd8436608dd8048fe9ffb2a29a35f561b5be
sha256 SP_ERRATUM1.txt 6e58146782f280de97d208be37e9f0af3b0f87c87a4cc6d8db0d301ff58bd199
sha256 SP_AMENDMENT2.txt 180a280a9f9193a7322e233941661bde79277e5008ffcb1e2fdf8dba948f459f
EOS
# the amended generator the bundle carries must be the one the amendment records
GEN_NEW=66c9f4a4e3544e58e866baeb33afa7e9717711f124a249a5ee3ef737a64cec8f
GEN_OLD=291de214c995c3a00f74488334544e7a3730f4976e0280d46cdaa22a07f0c296
[ "$(sha "$B/code/spa_prepare.py")" = "$GEN_NEW" ] || stop "the bundle's spa_prepare.py is not the one $A3 records"
[ "$(sha "$CODE/phase1_system_dev/spa_prepare.py")" = "$GEN_OLD" ] \
  || stop "the code repo's spa_prepare.py is not the committed one $A2 records; this bundle may have run already"
python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$B/code/spa_prepare.py" || stop "the bundle's spa_prepare.py does not parse"
# the amended generator must differ from the committed one in the memory column and nothing else
python3 - "$CODE/phase1_system_dev/spa_prepare.py" "$B/code/spa_prepare.py" << 'EOS' || stop "the amended generator changes more than the memory column: tell Claude"
import re, sys
a, b = (open(p).read() for p in sys.argv[1:3])
TABLE = r'\nJOBS = \[(.*?)\n(?=\S)'     # the assignment runs to the next line that starts at column 0
def strip(s):                      # drop the JOBS table and comments: the rest must be identical
    s = re.sub(TABLE, '\n', s, flags=re.S)
    return "\n".join(l for l in s.splitlines() if not l.lstrip().startswith("#"))
if strip(a) != strip(b): sys.exit("outside JOBS")
def mems(s):
    m = re.search(TABLE, s, re.S)
    if not m: sys.exit("could not find the JOBS table")
    return re.findall(r'\("(job_\w+)",\s*(\d+)', m.group(1))
ma, mb = mems(a), mems(b)
if [x[0] for x in ma] != [x[0] for x in mb]: sys.exit("the job list changed")
want = {"job_ts": ("250", "250"), "job_ts_freq_irc": ("250", "64"), "job_r_irc": ("180", "64"),
        "job_r_irc_freq": ("180", "64"), "job_p_irc": ("180", "64"), "job_p_irc_freq": ("180", "64"),
        "job_r0": ("180", "64"), "job_r0_freq": ("180", "64")}
for (j, x), (_, y) in zip(ma, mb):
    if want[j] != (x, y): sys.exit("%s: %s -> %s, expected %s -> %s" % (j, x, y, want[j][0], want[j][1]))
EOS
[ -e "$RES/$T/$A3" ] && stop "$A3 is committed already: this bundle has run; tell Claude"
[ -e "$RES/$T/$REC" ] && stop "$RES/$T/$REC exists already: this bundle has run; tell Claude"
ssh "$HPC" "test -d $SD && test -e $SD/spa_prepare.py" || stop "cannot reach hpc1, or $SD is not as the first wave left it"
[ "$(ssh "$HPC" "sha256sum < $SD/spa_prepare.py" | cut -c1-64)" = "$GEN_OLD" ] \
  || stop "the generator on hpc1 is not the committed one: tell Claude"
# every run folder exists, and holds its first-wave SUBMITTED
miss=$(ssh "$HPC" "cd $SD && for r in $RUNS; do [ -d \$r ] || echo \$r; [ -s \$r/SUBMITTED ] || echo \$r/SUBMITTED; done")
[ -z "$miss" ] || stop "missing on hpc1: $(echo $miss | tr '\n' ' ')"
echo "   bundle, tools, repos, hpc1 and the $NR run folders: ok"
echo "   generator: $GEN_OLD -> $GEN_NEW (the memory column of JOBS only)"

echo "== 1. committing the amendment and the amended generator (before anything on hpc1 changes)"
cp "$B/$A3" "$RES/$T/$A3"
cp "$B/code/spa_prepare.py" "$CODE/phase1_system_dev/spa_prepare.py"
( cd "$CODE" && git add phase1_system_dev/spa_prepare.py
  [ "$(git diff --cached --name-only | grep -c .)" = 1 ] || stop "internal: expected 1 file in the code commit"
  git commit -q -F - << EOF
spa_prepare.py: the package jobs' memory requests, SP Amendment 3 A3.2. Seven of the eight job types asked PBS for 180 or 250 GB and measured under 4.11 GiB in both smoke tests (job_ts_freq_irc 4.10, job_r_irc 2.25, job_r_irc_freq 3.97, job_p_irc 2.22, job_p_irc_freq 4.09, job_r0 2.36, job_r0_freq 4.09 at 8 A, and no higher at 6 A), so the first wave sat waiting for large-memory nodes it did not need: 0 of 256 jobs finished in 44.7 h, 3 running, 61 queued, 192 held, the first job starting 27.9 h after submission. Those seven now ask for 64 GB, 15.6x the largest memory any of them used and 3.05x the largest virtual memory; PBS enforces the first of these. job_ts is unchanged at 250 GB: it measured 197.28 GiB at 8 A and 174.74 at 6 A, as SP_AMENDMENT2.txt records, and its %maxcore 12000 on 16 cores allows about 188 GiB. %maxcore is NOT changed anywhere, so no calculation, input, threshold or check differs and the ORCA ceiling still sits above the new request; a frame that needed more would be killed by PBS and re-run under A2.2. The only difference in each generated job script is its "#PBS -l select=" line. Direction: none, on any reported quantity

$TRAILER
EOF
  git push -q origin tier1-realism ) || stop "the code commit or push failed (above)"
CODEC=$(git -C "$CODE" rev-parse --short HEAD)
( cd "$RES" && git add "$T/$A3"
  [ "$(git diff --cached --name-only | grep -c .)" = 1 ] || stop "internal: expected 1 file in the amendment commit"
  [ -z "$(git diff --cached --name-status | grep -v '^A')" ] || stop "internal: the commit would change or delete a file"
  git commit -q -F - << EOF
SP Amendment 3 ($T/$A3): the package jobs' memory requests, committed before any job is deleted, any input replaced or anything resubmitted, and before any package result exists. Seven of the eight job types asked PBS for 180 or 250 GB and measured under 4.11 GiB in both committed smoke tests, so the first wave waited for nodes it did not need: at 11:12 SAST on 21 October, 44.7 h after submission, 0 of 256 jobs had finished (3 running, 61 queued, 192 held on their dependencies, the longest-running job having waited 27.9 h to start). Those seven ask for 64 GB; job_ts keeps 250 GB, having measured 197.28 GiB. %maxcore is not touched, so no calculation, input, threshold or check changes and each generated job script differs in one line. Only run folders in which every job is still queued and nothing has been written are deleted and resubmitted; a folder with a job running, or with any output, is left alone and deferred (A3.3). The deletion is a disclosed correction, not a machinery stop, and consumes no frame's single re-run (A3.5). Code tier1-realism $CODEC [retained-final]

$TRAILER
EOF
  git push -q origin main ) || stop "the amendment commit or push failed (above)"
A3C=$(git -C "$RES" rev-parse --short HEAD)
echo "   committed and pushed: code $CODEC, results $A3C"

echo "== 2. the amended generator onto hpc1"
if [ "$(ssh "$HPC" "sha256sum < $SD/spa_prepare.py" | cut -c1-64)" = "$GEN_NEW" ]; then
  echo "   already in place"
else
  ssh "$HPC" "mkdir -p $SD/superseded_a2 && cp -n $SD/spa_prepare.py $SD/superseded_a2/spa_prepare.py" \
    || stop "could not keep the superseded generator on hpc1"
  [ "$(ssh "$HPC" "sha256sum < $SD/superseded_a2/spa_prepare.py" | cut -c1-64)" = "$GEN_OLD" ] \
    || stop "the superseded copy on hpc1 is not the committed generator"
  scp -q "$B/code/spa_prepare.py" "$HPC:$SD/spa_prepare.py.part" || stop "copying the generator to hpc1 failed (run this again)"
  [ "$(ssh "$HPC" "sha256sum < $SD/spa_prepare.py.part" | cut -c1-64)" = "$GEN_NEW" ] || stop "the generator arrived on hpc1 damaged (run this again)"
  ssh "$HPC" "mv $SD/spa_prepare.py.part $SD/spa_prepare.py" || stop "could not put the generator in place on hpc1"
  echo "   copied; the committed one kept as superseded_a2/spa_prepare.py"
fi

echo "== 3. what PBS says about every package job (A3.3)"
# For each run folder, each job's id from its first-wave SUBMITTED, then its state from PBS. A job PBS does not know
# is "gone". qselect/qstat failures stop: a job is never taken as ended because PBS could not be asked.
ssh "$HPC" 'bash -s' > "$S/state.txt" << EOS || stop "could not ask PBS about the package's jobs"
set -u
cd $SD || { echo "NOSD"; exit 0; }
for r in $RUNS; do
  out=""
  while read -r jn id; do
    [ -n "\$id" ] || continue
    o=\$(qstat -f "\$id" 2>&1) || { if printf '%s\n' "\$o" | grep -qE "Unknown Job Id|Job has finished"; then out="\$out \$jn:\$id:gone"; continue; else echo "QSTAT_FAILED \$id"; exit 0; fi; }
    st=\$(printf '%s\n' "\$o" | awk '/^\t/ {sub(/^\t/, ""); printf "%s", \$0; next} NR > 1 {print ""} {printf "%s", \$0} END {print ""}' | sed -n 's/^ *job_state = //p' | head -1)
    [ -n "\$st" ] || { echo "QSTAT_FAILED \$id (no job_state)"; exit 0; }
    out="\$out \$jn:\$id:\$st"
  done < \$r/SUBMITTED
  # any output or step record already written in this folder
  wrote=\$(ls \$r/*.pbs.out 2>/dev/null | wc -l)
  recs=\$(ls \$r/*/STAGE_RESULT.txt 2>/dev/null | wc -l)
  echo "FOLDER \$r wrote=\$wrote recs=\$recs\$out"
done
echo "CHECKED"
EOS
grep -q '^CHECKED$' "$S/state.txt" || stop "the job check on hpc1 did not finish: $(head -3 "$S/state.txt")"
grep -q '^QSTAT_FAILED' "$S/state.txt" && stop "PBS could not be asked about a job ($(grep '^QSTAT_FAILED' "$S/state.txt" | head -1)): try again later"
[ "$(grep -c '^FOLDER ' "$S/state.txt")" -eq "$NR" ] || stop "read $(grep -c '^FOLDER ' "$S/state.txt") folders, expected $NR"
# sort the folders: untouched (all eight queued, nothing written) or deferred
: > "$S/untouched.txt"; : > "$S/deferred.txt"
while read -r _ r wrote recs rest; do
  w=${wrote#wrote=}; c=${recs#recs=}
  n=0; nqh=0; bad=""
  for t in $rest; do
    n=$((n + 1)); st=${t##*:}
    case "$st" in Q|H) nqh=$((nqh + 1)) ;; R) bad="running" ;; gone) bad="a job has left the queue" ;;
                  *) bad="state $st" ;; esac
  done
  [ "$n" -eq 8 ] || { echo "$r SUBMITTED lists $n jobs, not 8" >> "$S/deferred.txt"; continue; }
  if [ "$w" != 0 ] || [ "$c" != 0 ]; then echo "$r has written output ($w job outputs, $c step records)" >> "$S/deferred.txt"; continue; fi
  if [ -n "$bad" ]; then echo "$r $bad" >> "$S/deferred.txt"; continue; fi
  [ "$nqh" -eq 8 ] && echo "$r $rest" >> "$S/untouched.txt" || echo "$r mixed states" >> "$S/deferred.txt"
done < <(grep '^FOLDER ' "$S/state.txt")
NU=$(grep -c . "$S/untouched.txt" || true); ND=$(grep -c . "$S/deferred.txt" || true)
echo "   $NU of $NR run folders untouched (every job still queued, nothing written); $ND deferred"
[ "$ND" -gt 0 ] && sed 's/^/     deferred: /' "$S/deferred.txt"
[ "$NU" -gt 0 ] || { echo; echo "DONE: nothing to resubmit. The amendment and the amended generator are committed (code $CODEC, results $A3C) and the generator is in place on hpc1; every run folder is deferred because something is running or written. Send Claude this output."; exit 0; }

echo "== 4. generating again on hpc1, and what differs (A3.4)"
RG=$(ssh "$HPC" "mktemp -d $SD/staging/regen94.XXXXXX") || stop "could not make a scratch folder on hpc1"
ssh "$HPC" "cd $SD && python3 spa_prepare.py staging/expected_package.sha256 $RG $SPECS" > "$S/gen.txt" \
  || { tail -5 "$S/gen.txt"; stop "the generator stopped on hpc1 (above): nothing has been replaced; tell Claude"; }
ssh "$HPC" "cd $RG && find $RUNS \\( -type f -o -type l \\) | LC_ALL=C sort" > "$S/paths.txt" || stop "listing the generation failed"
[ "$(wc -l < "$S/paths.txt")" -eq $((NR * 36)) ] \
  || stop "the generation wrote $(wc -l < "$S/paths.txt") files and links, expected $((NR * 36)) ($NR x (27 files + 9 links))"
man() { ssh "$HPC" "cd $1 && while read -r p; do if [ -L \"\$p\" ]; then echo \"link \$(readlink \"\$p\") \$p\"; elif [ -f \"\$p\" ]; then echo \"\$(sha256sum < \"\$p\" | cut -c1-64) \$p\"; else echo \"missing \$p\"; fi; done"; }
man "$RG" < "$S/paths.txt" > "$S/new.txt" || stop "reading the generation failed"
man "$SD" < "$S/paths.txt" > "$S/old.txt" || stop "reading the run folders failed"
grep -q '^missing ' "$S/new.txt" && stop "a generated file is missing on hpc1: tell Claude"
grep -q '^missing ' "$S/old.txt" && stop "a run folder is missing a file it should have: tell Claude"
# exactly the nine expected files per folder may differ, and nothing else
python3 - "$S/old.txt" "$S/new.txt" "$NR" << 'EOS' > "$S/differs.txt" || stop "something other than the nine expected files differs: tell Claude"
import sys
old = {l.split(" ", 1)[1].rstrip("\n"): l.split(" ", 1)[0] for l in open(sys.argv[1])}
new = {l.split(" ", 1)[1].rstrip("\n"): l.split(" ", 1)[0] for l in open(sys.argv[2])}
if set(old) != set(new): sys.exit("the two listings cover different paths")
JOBS = ["job_ts", "job_ts_freq_irc", "job_r_irc", "job_r_irc_freq", "job_p_irc", "job_p_irc_freq", "job_r0", "job_r0_freq"]
allowed, diff = set(), []
for p in old:
    r = p.split("/", 1)[0]
    base = p.split("/", 1)[1]
    if base == "GENERATOR_LOG.txt" or base in [j + ".pbs" for j in JOBS]: allowed.add(p)
    if old[p] != new[p]: diff.append(p)
bad = [p for p in diff if p not in allowed]
if bad: sys.exit("these differ but should not: " + " ".join(sorted(bad)[:6]))
exp = 9 * int(sys.argv[3])
print("\n".join(sorted(diff)))
sys.stderr.write("%d of %d paths differ, all of them among the %d allowed\n" % (len(diff), len(old), exp))
EOS
echo "   $(grep -c . "$S/differs.txt") files differ of $(wc -l < "$S/paths.txt"), all of them job scripts or their log"
# every job script's only difference is its memory line
ssh "$HPC" 'bash -s' > "$S/lines.txt" << EOS || stop "could not compare the job scripts on hpc1"
set -u
for r in $RUNS; do for j in $JOBNAMES; do
  d=\$(diff $SD/\$r/\$j.pbs $RG/\$r/\$j.pbs || true)
  n=\$(printf '%s\n' "\$d" | grep -c '^[<>]' || true)
  bad=\$(printf '%s\n' "\$d" | grep '^[<>]' | grep -cv '^[<>] #PBS -l select=1:ncpus=16:mem=[0-9]*gb\$' || true)
  echo "\$r \$j lines=\$n other=\$bad \$(printf '%s\n' "\$d" | grep '^>' | tr -d '\n')"
done; done
echo "COMPARED"
EOS
grep -q '^COMPARED$' "$S/lines.txt" || stop "the job-script comparison did not finish"
grep -v '^COMPARED$' "$S/lines.txt" > "$S/lines.tmp" && mv "$S/lines.tmp" "$S/lines.txt"   # drop the sentinel
[ "$(grep -c . "$S/lines.txt")" -eq $((NR * 8)) ] || stop "the comparison covered $(grep -c . "$S/lines.txt") job scripts, expected $((NR * 8))"
# job_ts keeps 250 GB, so its script must be unchanged (0 differing lines); each of the other seven must differ in
# exactly one line (diff shows 2: the old and the new), and in no line that is not a "#PBS -l select=" line.
awk '{ want = ($2 == "job_ts") ? "lines=0" : "lines=2";
       if ($3 != want || $4 != "other=0") { print $0 "   [expected " want ", other=0]"; bad = 1 } }
     END { exit bad + 0 }' "$S/lines.txt" > "$S/badlines.txt" \
  && echo "   job_ts unchanged in all $NR folders; each of the other seven differs in exactly one line, its memory request" \
  || { head -5 "$S/badlines.txt"; stop "a job script differs other than in its memory line, or job_ts changed: nothing has been replaced; tell Claude"; }
[ "$(awk '$2 == "job_ts" && $3 == "lines=0"' "$S/lines.txt" | wc -l)" -eq "$NR" ] || stop "internal: job_ts should be unchanged in every folder"
[ "$(awk '$2 != "job_ts" && $3 == "lines=2"' "$S/lines.txt" | wc -l)" -eq $((NR * 7)) ] || stop "internal: the seven amended scripts should each differ in one line"
awk '{for (i = 5; i <= NF; i++) if ($i ~ /mem=/) print $2, $i}' "$S/lines.txt" | sort -u | sed 's/^/     /'

echo "== 5. replacing the nine files in the $NU untouched folders"
UF=$(awk '{print $1}' "$S/untouched.txt" | tr '\n' ' ')
ssh "$HPC" 'bash -s' > "$S/replaced.txt" << EOS || stop "replacing the job scripts on hpc1 failed: send Claude the output"
set -eu
for r in $UF; do
  for j in $JOBNAMES; do cp $RG/\$r/\$j.pbs $SD/\$r/\$j.pbs.new && mv $SD/\$r/\$j.pbs.new $SD/\$r/\$j.pbs; done
  cp $RG/\$r/GENERATOR_LOG.txt $SD/\$r/GENERATOR_LOG.txt.new && mv $SD/\$r/GENERATOR_LOG.txt.new $SD/\$r/GENERATOR_LOG.txt
  echo "\$r replaced"
done
echo "REPLACED"
EOS
grep -q '^REPLACED$' "$S/replaced.txt" || stop "the replacement did not finish: send Claude the output"
# each replaced folder must now equal the fresh generation, and its log must record its own files
ssh "$HPC" 'bash -s' > "$S/verify.txt" << EOS || stop "could not verify the replaced folders"
set -u
for r in $UF; do
  n=0
  for j in $JOBNAMES; do
    [ "\$(sha256sum < $SD/\$r/\$j.pbs | cut -c1-64)" = "\$(sha256sum < $RG/\$r/\$j.pbs | cut -c1-64)" ] || { echo "MISMATCH \$r \$j"; exit 0; }
    n=\$((n + 1))
  done
  [ "\$(sha256sum < $SD/\$r/GENERATOR_LOG.txt | cut -c1-64)" = "\$(sha256sum < $RG/\$r/GENERATOR_LOG.txt | cut -c1-64)" ] || { echo "MISMATCH \$r log"; exit 0; }
  ( cd $SD/\$r && grep '^  [0-9a-f]\{64\}  ' GENERATOR_LOG.txt | grep -v -e ' ts/start.xyz\$' -e ' r0/start.xyz\$' | sed 's/^  //' | sha256sum -c --quiet ) \
    || { echo "LOGMISMATCH \$r"; exit 0; }
  echo "\$r ok \$n"
done
echo "VERIFIED"
EOS
grep -q '^VERIFIED$' "$S/verify.txt" || { head -3 "$S/verify.txt"; stop "a replaced folder does not match the fresh generation or its own log: NOTHING HAS BEEN RESUBMITTED; tell Claude"; }
echo "   every replaced job script matches the fresh generation, and each folder's files match its own GENERATOR_LOG"

echo "== 6. deleting the queued jobs and resubmitting, folder by folder (A3.3)"
: > "$S/submitted.txt"
nf=0
while read -r r rest; do
  nf=$((nf + 1))
  ids=$(for t in $rest; do echo "${t#*:}" | cut -d: -f1; done | tr '\n' ' ')
  out=$(ssh "$HPC" 'bash -s' << EOS
set -u
cd $SD/$r || { echo "NODIR"; exit 0; }
# every job of this folder must still be Q or H right now; anything else and this folder is left alone
for id in $ids; do
  o=\$(qstat -f "\$id" 2>&1) || { echo "VANISHED \$id"; exit 0; }
  st=\$(printf '%s\n' "\$o" | awk '/^\t/ {sub(/^\t/, ""); printf "%s", \$0; next} NR > 1 {print ""} {printf "%s", \$0} END {print ""}' | sed -n 's/^ *job_state = //p' | head -1)
  case "\$st" in Q|H) ;; *) echo "CHANGED \$id \$st"; exit 0 ;; esac
done
ls *.pbs.out > /dev/null 2>&1 && { echo "WROTE"; exit 0; }
for id in $ids; do qdel "\$id" 2>&1 | grep -v '^\$' || true; done
sleep 5
for id in $ids; do
  o=\$(qstat -f "\$id" 2>&1) || continue
  st=\$(printf '%s\n' "\$o" | awk '/^\t/ {sub(/^\t/, ""); printf "%s", \$0; next} NR > 1 {print ""} {printf "%s", \$0} END {print ""}' | sed -n 's/^ *job_state = //p' | head -1)
  case "\$st" in E|F|"") ;; *) echo "STILLTHERE \$id \$st"; exit 0 ;; esac
done
[ -e SUBMITTED.wave1 ] || mv SUBMITTED SUBMITTED.wave1 || { echo "NOMOVE"; exit 0; }
rm -f SUBMITTED SUBMITTED.partial
# Each qsub is guarded on the ASSIGNMENT, not inside the command substitution: an "exit" inside \$(...) would only
# leave the subshell, so a failed qsub would be stored as if it were a job id and the folder reported as done.
# SUBMITTED.partial is left in place on any failure and SUBMITTED is not written, so what was queued is recorded.
: > SUBMITTED.partial
A1=\$(qsub job_ts.pbs)                                 || { echo "QSUBFAIL job_ts"; exit 0; }
echo "job_ts \$A1" >> SUBMITTED.partial
A2=\$(qsub -W depend=afterok:\$A1 job_ts_freq_irc.pbs) || { echo "QSUBFAIL job_ts_freq_irc"; exit 0; }
echo "job_ts_freq_irc \$A2" >> SUBMITTED.partial
B1=\$(qsub -W depend=afterok:\$A2 job_r_irc.pbs)       || { echo "QSUBFAIL job_r_irc"; exit 0; }
echo "job_r_irc \$B1" >> SUBMITTED.partial
B2=\$(qsub -W depend=afterok:\$B1 job_r_irc_freq.pbs)  || { echo "QSUBFAIL job_r_irc_freq"; exit 0; }
echo "job_r_irc_freq \$B2" >> SUBMITTED.partial
C1=\$(qsub -W depend=afterok:\$A2 job_p_irc.pbs)       || { echo "QSUBFAIL job_p_irc"; exit 0; }
echo "job_p_irc \$C1" >> SUBMITTED.partial
C2=\$(qsub -W depend=afterok:\$C1 job_p_irc_freq.pbs)  || { echo "QSUBFAIL job_p_irc_freq"; exit 0; }
echo "job_p_irc_freq \$C2" >> SUBMITTED.partial
D1=\$(qsub job_r0.pbs)                                 || { echo "QSUBFAIL job_r0"; exit 0; }
echo "job_r0 \$D1" >> SUBMITTED.partial
D2=\$(qsub -W depend=afterok:\$D1 job_r0_freq.pbs)     || { echo "QSUBFAIL job_r0_freq"; exit 0; }
echo "job_r0_freq \$D2" >> SUBMITTED.partial
[ "\$(grep -c . SUBMITTED.partial)" = 8 ] || { echo "QSUBFAIL only \$(grep -c . SUBMITTED.partial) of 8 recorded"; exit 0; }
mv SUBMITTED.partial SUBMITTED
echo "OK"; cat SUBMITTED
EOS
) || stop "$r: the ssh call failed; check with qstat before running this again and send Claude the output"
  case "$out" in
    *OK*) echo "   $r: 8 deleted, 8 resubmitted"
          { echo "RUN $r"; echo "  deleted: $ids"; printf '%s\n' "$out" | grep '^job_' | sed 's/^/  /'; } >> "$S/submitted.txt" ;;
    *CHANGED*|*VANISHED*|*WROTE*)
          echo "   $r: LEFT ALONE, its state changed since step 3 ($(printf '%s' "$out" | head -1))"
          { echo "RUN $r"; echo "  left alone: $(printf '%s' "$out" | head -1)"; } >> "$S/submitted.txt" ;;
    *QSUBFAIL*|*) printf '%s\n' "$out" | head -5
       stop "$r: the delete or the resubmission did not finish. Run 'qstat -u 18660916' and send Claude that and this output BEFORE running anything again; $r/SUBMITTED.partial on hpc1 lists what was submitted" ;;
  esac
done < "$S/untouched.txt"

echo "== 7. the record"
mkdir -p "$RES/$T/$REC"
{ echo "x94_package_memory.sh, SP Amendment 3 applied $(date -u +%Y-%m-%dT%H:%MZ) from this PC"
  echo "amendment: $T/$A3 (results $A3C); generator: code tier1-realism $CODEC, spa_prepare.py sha256 $GEN_NEW"
  echo "            superseded generator kept on hpc1 as superseded_a2/spa_prepare.py (sha256 $GEN_OLD)"
  echo
  echo "memory requested, by job type (SP_AMENDMENT3.txt A3.2):"
  awk '{for (i = 5; i <= NF; i++) if ($i ~ /mem=/) print "   " $2, $i}' "$S/lines.txt" | sort -u
  echo
  echo "run folders: $NR; untouched and handled: $NU; deferred: $ND"
  [ "$ND" -gt 0 ] && { echo; echo "deferred, left exactly as they were (A3.3; a later bundle resubmits them):"; sed 's/^/   /' "$S/deferred.txt"; }
  echo
  echo "what PBS said in step 3, before anything was deleted:"
  grep '^FOLDER ' "$S/state.txt" | sed 's/^FOLDER /   /'
  echo
  echo "deleted and resubmitted:"
  sed 's/^/   /' "$S/submitted.txt"
  echo
  echo "Every file of every run folder other than the eight job_*.pbs and GENERATOR_LOG.txt is byte for byte what is"
  echo "committed; each job script differs from the committed one in its '#PBS -l select=' line alone, shown above."
  echo "Nothing running was interrupted, no run folder was renamed, and no package result was read."
} > "$RES/$T/$REC/X94_RECORD.txt"
cp "$S/lines.txt" "$RES/$T/$REC/JOB_SCRIPT_DIFFS.txt"
cp "$S/state.txt" "$RES/$T/$REC/QSTAT_BEFORE.txt"
cp "$B/x94_package_memory.sh" "$RES/$T/$REC/x94_package_memory.sh"
( cd "$RES" && git add "$T/$REC"
  [ -z "$(git diff --cached --name-status | grep -v '^A')" ] || stop "internal: the commit would change or delete a file"
  git commit -q -F - << EOF
SP Amendment 3 applied ($T/$REC/): the package's job memory requests lowered and the affected jobs resubmitted. $NU of the $NR run folders were untouched (every job still queued, nothing written) and were deleted and resubmitted with the corrected scripts; $ND were deferred and left exactly as they were, which is what A3.3 requires of a folder with a job still running or any output already written. Before anything was deleted, a fresh generation on hpc1 showed that of the $((NR * 36)) generated files and links only the eight job_*.pbs and GENERATOR_LOG.txt per folder differ, and that each job script differs from the committed one in its "#PBS -l select=" line alone (JOB_SCRIPT_DIFFS.txt); every replaced folder was then checked against that generation and against its own GENERATOR_LOG. QSTAT_BEFORE.txt holds what PBS said about all 256 first-wave jobs, X94_RECORD.txt what was done to each. The deletion is a disclosed correction, not a machinery stop, so no frame's single re-run is consumed (A3.5) and no folder was renamed. Nothing running was interrupted and no package result was read. Code tier1-realism $CODEC [retained-final]

$TRAILER
EOF
  git push -q origin main ) || stop "the record commit or push failed (above)"
RECC=$(git -C "$RES" rev-parse --short HEAD)

echo
echo "DONE: amendment results $A3C, code $CODEC, record results $RECC."
echo "      $NU of $NR run folders resubmitted with 64 GB where it was 180 or 250; $ND deferred."
echo "      Nothing running was interrupted. Send Claude this output and a fresh 'qstat -u 18660916'."
