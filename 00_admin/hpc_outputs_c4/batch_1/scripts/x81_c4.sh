#!/usr/bin/env bash
# x81_c4.sh - RUN ON THE PC (not on hpc1):  bash x81/x81_c4.sh status | commit
# x80_c4.sh with two additions after x80's first commit stopped when the PC's disk filled (18 October 2026): a PC archive
# that an earlier, uncommitted run of this commit already put in place is checked member by member against the batch's
# inventory and reused instead of downloaded again; and the free space on the PC is checked before anything is downloaded
# or copied. Same stage folder on hpc1 (~/x80_stage), same hpc1 and PC-side checks (c4_collect.py, verify_c4.py unchanged).
# C4's re-optimisation runs (05_qmmm/23_c4_reactant: the 35 runs of runs.tsv, later any M1 continuation <run>_c) kept as
# physical files before C4's analysis is run on them (Jessica's rule of 18 October 2026; C4_CLOSURE.txt). Deletes
# nothing on hpc1: a run killed by the walltime keeps its trajectory there for its M1 continuation.
#   status  read-only: every run's job (in the queue or ended, how its output ends) and what would happen to its files;
#           and whether every file now in a run a batch has taken was archived or committed by a batch. Changes nothing.
#   commit  for the runs whose jobs have ended and that no batch holds: stages them on hpc1 (copies only, in
#           ~/x80_stage); downloads EVERY regular file of each run into a PC archive (default
#           ~/Desktop/chorismate-hpc-archive, or $X80_ARCHIVE) and checks every file's sha256; fetches the stage and checks
#           every git archive and compressed file; then commits to the results repo the readable outputs, geometries and
#           final wavefunctions, the sha256 of every archived file and where each PC archive is, and pushes.
# Safe to re-run: a finished batch is checked and skipped; anything unexpected stops it with a message.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
ARCH="${X80_ARCHIVE:-$HOME/Desktop/chorismate-hpc-archive}"; case "$ARCH" in /*) ;; *) ARCH="$PWD/$ARCH";; esac
X=x81
HPC="18660916@hpc"
ROOT=/home/18660916/system_development
CD=$ROOT/05_qmmm/23_c4_reactant
STG=/home/18660916/x80_stage
T=05_qmmm/23_c4_reactant
A=00_admin/hpc_outputs_c4
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
COPYING=0
stop() { echo "STOP: $*"; exit 1; }
S=$(mktemp -d)
on_exit() {
  local rc=$?
  rm -rf "$S"
  if [ "$rc" -ne 0 ] && [ "$COPYING" = 1 ]; then
    echo "NOTE: this batch's copies are in the results repo but not committed (hpc1 is untouched; the batch's PC archives"
    echo "are in place but recorded in no commit yet: the next commit checks each one whole and member by member, reuses it"
    echo "if it matches the batch, and otherwise downloads the run again and moves the old one aside). To clear the"
    echo "uncommitted copies before running commit again (they are copies; everything is in the PC archives and on hpc1):"
    echo "  git -C $RES reset -q --hard HEAD && git -C $RES clean -fdq -- 00_admin 05_qmmm"
  fi
}
trap on_exit EXIT
MODE=${1:-}
case "$MODE" in status|commit) ;; *) stop "usage: bash x81/x81_c4.sh status | commit";; esac
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
sshc() { ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=10 "$@"; }
remote() { sshc "$HPC" "python3 - $*" < "$B/c4_collect.py"; }      # the hpc1 script, read from the bundle each time
track() {     # every file now in a run a batch has taken: archived or committed by a batch
  remote files "$CD" > "$S/files.txt" || { tail -3 "$S/files.txt"; return 1; }
  python3 "$B/verify_c4.py" track "$RES/$A" "$S/files.txt"
}
batches() { local d; for d in "$RES/$A"/batch_*; do if [ -d "$d" ]; then basename "$d"; fi; done | sort -V; }
if [ "$MODE" = status ]; then
  remote status "$CD" | grep -v '^RUNSTATE ' || stop "status failed on hpc1 (above)"
  echo "== files of the runs the batches have taken (results repo as it is on this PC)"
  track || echo "   (commit stops on this; nothing was changed)"
  exit 0
fi
command -v python3 >/dev/null || stop "python3 is needed on the PC"
command -v xz >/dev/null || stop "xz is needed on the PC"
git -C "$RES" pull --ff-only -q || stop "git pull failed in $RES"
[ -z "$(git -C "$RES" status --porcelain)" ] || stop "$RES has uncommitted changes"
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ -e "$RES/$T/C4_CLOSURE.txt" ] || stop "$T/C4_CLOSURE.txt is not in the results repo (x79 first)"
cd "$RES"
# ---- 1. what this batch takes: runs whose jobs have ended and that no batch holds
track || stop "the file check found something no batch holds (above): nothing was staged or committed"
remote status "$CD" > "$S/status.txt" || { tail -5 "$S/status.txt"; stop "status failed on hpc1"; }
awk '$1 == "RUNSTATE" && $3 == "ended" {print $2}' "$S/status.txt" | LC_ALL=C sort > "$S/ended"
awk '$1 == "RUNSTATE" && $3 != "ended" {print $2}' "$S/status.txt" > "$S/active"
[ -s "$S/ended" ] || [ -s "$S/active" ] || stop "hpc1 reported no run states"
: > "$S/done"; for d in $(batches); do cut -f1 "$A/$d/RUNS.txt" >> "$S/done"; done
LC_ALL=C sort -u -o "$S/done" "$S/done"
LC_ALL=C comm -23 "$S/ended" "$S/done" > "$S/todo"
if [ ! -s "$S/todo" ]; then
  echo "nothing new to commit: every run whose job has ended is in a batch ($(batches | wc -l) batch(es)); not ended yet (in the queue, or not started): $(tr '\n' ' ' < "$S/active")"
  exit 0
fi
nb=$(batches | wc -l); N=$((nb + 1))
echo "batch $N: $(wc -l < "$S/todo") run(s) whose jobs have ended; not ended yet (in the queue, or not started): $(wc -l < "$S/active")"
# ---- 2. stage on hpc1 (copies only)
OUT=$STG/batch_$N
if sshc -n "$HPC" "test -e $OUT"; then
  sshc -n "$HPC" "test -e $OUT/DONE" || stop "$OUT exists on hpc1 from an unfinished stage. It holds copies only; remove it with  ssh $HPC \"rm -rf $OUT\"  and run commit again"
  sshc -n "$HPC" "cut -f1 $OUT/RUNS.txt" | LC_ALL=C sort > "$S/st_runs"
  if cmp -s "$S/st_runs" "$S/todo"; then
    echo "   batch $N was staged already on hpc1 with these runs: using that stage"
  else
    stop "$OUT exists on hpc1 from a different stage. It holds copies only; remove it with  ssh $HPC \"rm -rf $OUT\"  and run commit again"
  fi
else
  sshc -n "$HPC" "mkdir -p $STG"
  remote stage "$CD" "$OUT" "$N" $(cat "$S/todo") || stop "staging stopped on hpc1 (above); nothing was committed"
fi
# ---- 3. download every file of the batch into the PC archives, then fetch the stage, and check everything
IN="$ARCH/.incoming_c4_batch_$N"; rm -rf "$IN"; mkdir -p "$IN"
sshc -n "$HPC" "cd $STG && tar -cf - batch_$N" | tar -xf - -C "$S" || stop "fetching the stage from hpc1 failed (if the message above says No space left on device, free some space: df -h ~ /tmp); nothing was downloaded or committed"
W=$S/batch_$N
# a PC archive already in place from an earlier, uncommitted run of this commit: reused if its manifest is this batch's and
# every member matches it (read member by member); otherwise it is downloaded again (and the old one moved aside below)
: > "$S/fetch"; nreuse=0
while read -r r; do
  [ -f "$W/PCLIST_$r.txt" ] || stop "the stage has no file list for $r"
  F="$ARCH/$T/$r/hpc_all_files_c4_batch_$N.tar.xz"; M="${F%.tar.xz}.MANIFEST.sha256"
  awk -F'\t' -v r="$r" 'NR > 1 && $4 != "-" && $4 != "link" { split($3, q, "/"); if (q[3] == r) print $5 "  " $3 }' "$W/inventory.tsv" | LC_ALL=C sort -k2 > "$S/manifest_$r"
  if [ -f "$F" ] && [ -f "$M" ] && cmp -s "$M" "$S/manifest_$r" && xz -tq "$F" 2> /dev/null && python3 "$B/verify_c4.py" pcarchive "$F" "$M" > /dev/null 2>&1; then
    ln -s "$F" "$IN/$r.tar.xz"; nreuse=$((nreuse + 1))
  else
    echo "$r" >> "$S/fetch"
    if [ -e "$F" ] || [ -e "$M" ]; then echo "   $r: the PC archive in place does not match this batch or is damaged; it is downloaded again (the old one moved aside)"; fi
  fi
done < "$S/todo"
[ "$nreuse" -gt 0 ] && echo "   $nreuse PC archive(s) already in place from an earlier run of this commit: each tested whole and every member checked against this batch's inventory; reused"
# free space on the PC: the files still to download (counted uncompressed, so a safe upper bound) where the PC archives
# go, and the git files where the results repo is; both together if they are on one filesystem
need_a=$(awk -F'\t' 'NR == FNR {f[$1] = 1; next} FNR > 1 && $4 != "-" && $4 != "link" { split($3, q, "/"); if (q[3] in f) s += $1 } END {printf "%.0f", s + 5e8}' "$S/fetch" "$W/inventory.tsv")
need_g=$(( 2 * $(du -sb "$W" | cut -f1) + 500000000 ))   # the files in the repo and git's own copy of them
fa=$(( $(df -Pk "$ARCH" | awk 'NR==2 {print $4}') * 1024 )); fg=$(( $(df -Pk "$RES" | awk 'NR==2 {print $4}') * 1024 ))
if [ "$(df -P "$ARCH" | awk 'NR==2 {print $1}')" = "$(df -P "$RES" | awk 'NR==2 {print $1}')" ]; then
  [ "$fa" -ge $((need_a + need_g)) ] || stop "the PC's disk has $(awk -v b=$fa 'BEGIN {printf "%.2f", b/1e9}') GB free where the archive and the repo are; this commit needs up to $(awk -v b=$((need_a + need_g)) 'BEGIN {printf "%.2f", b/1e9}') GB. Nothing was downloaded or committed: free some space and run commit again"
else
  [ "$fa" -ge "$need_a" ] || stop "$ARCH has $(awk -v b=$fa 'BEGIN {printf "%.2f", b/1e9}') GB free; the downloads need up to $(awk -v b=$need_a 'BEGIN {printf "%.2f", b/1e9}') GB. Nothing was downloaded or committed"
  [ "$fg" -ge "$need_g" ] || stop "$RES has $(awk -v b=$fg 'BEGIN {printf "%.2f", b/1e9}') GB free; the commit needs up to $(awk -v b=$need_g 'BEGIN {printf "%.2f", b/1e9}') GB. Nothing was downloaded or committed"
fi
echo "   free space on the PC checked: enough for $(wc -l < "$S/fetch") run(s) still to download and the git files"
while read -r r; do
  echo "   downloading every file of $r ($(wc -l < "$W/PCLIST_$r.txt") files) ..."
  sshc -n "$HPC" "bash -c 'set -o pipefail; cd $ROOT && tar -cf - --no-recursion -T $OUT/PCLIST_$r.txt | xz -1 -T1 -c'" > "$IN/$r.tar.xz" \
    || stop "downloading the files of $r failed; nothing was committed (run commit again)"
done < "$S/fetch"
python3 "$B/verify_c4.py" stage "$W" "$RES" "$IN" || stop "the download or the stage did not verify (above); nothing was committed"
# ---- 4. the PC archives into place, with their manifests; then verified again where they lie
printf "# run\tPC archive (relative to the archive folder %s)\tbytes\tsha256\tmembers\n" "$ARCH" > "$S/PC_ARCHIVES.tsv"
while read -r r; do
  D="$ARCH/$T/$r"; F="$D/hpc_all_files_c4_batch_$N.tar.xz"; M="${F%.tar.xz}.MANIFEST.sha256"
  mkdir -p "$D"
  if [ -L "$IN/$r.tar.xz" ] && [ "$(readlink "$IN/$r.tar.xz")" = "$F" ] && cmp -s "$M" "$S/manifest_$r"; then
    rm "$IN/$r.tar.xz"; echo "   $F: in place from the earlier run of this commit, every member checked; reused"
  elif [ -e "$F" ] && cmp -s "$F" "$IN/$r.tar.xz" && cmp -s "$M" "$S/manifest_$r"; then
    rm "$IN/$r.tar.xz"; echo "   $F: already in place from an earlier run of this commit, identical"
  else
    [ -L "$IN/$r.tar.xz" ] && stop "the reused archive of $r changed during this run; nothing was committed: tell Claude"
    if [ -e "$F" ] || [ -e "$M" ]; then  # left by an earlier commit of this batch that stopped before its git commit
      ASIDE="$D/unrecorded_$(date +%Y%m%dT%H%M%S)"; mkdir -p "$ASIDE"
      for f in "$F" "$M"; do if [ -e "$f" ]; then mv "$f" "$ASIDE/"; fi; done
      echo "   an earlier, uncommitted download of this batch differs from this one: moved aside to $ASIDE"
    fi
    cp "$S/manifest_$r" "$M"; mv "$IN/$r.tar.xz" "$F"
  fi
  python3 "$B/verify_c4.py" pcarchive "$F" "$M" > /dev/null || { python3 "$B/verify_c4.py" pcarchive "$F" "$M" | tail -3; stop "the PC archive $F did not verify where it lies: tell Claude"; }
  printf "%s\t%s\t%s\t%s\t%s\n" "$r" "${F#$ARCH/}" "$(stat -c %s "$F")" "$(sha256sum < "$F" | cut -c1-64)" "$(grep -c . "$M")" >> "$S/PC_ARCHIVES.tsv"
  cp "$M" "$S/PCMANIFEST_$r.sha256"
done < "$S/todo"
rmdir "$IN" 2>/dev/null || true
echo "   every PC archive verified where it lies"
# ---- 5. commit (additions only) and push
COPYING=1
mkdir -p "$A/batch_$N"
for f in RUNS.txt SUMMARY.txt inventory.tsv archives.tsv ARCHIVES_BUILT.tsv individual.tsv INDIV.sha256 INDIV_XZ.sha256 \
         as_is.tsv AS_IS.sha256 pc_keep.tsv links.tsv; do
  cp "$W/$f" "$A/batch_$N/$f"
done
cp "$S/PC_ARCHIVES.tsv" "$A/batch_$N/"
while read -r r; do cp "$S/PCMANIFEST_$r.sha256" "$A/batch_$N/"; done < "$S/todo"
for sub in arch indiv asis; do      # git archives with manifests; files compressed one by one; files the jobs compressed
  if [ -d "$W/$sub" ]; then
    ( cd "$W/$sub" && find . -type f | sed 's|^\./||' ) > "$S/list_$sub"
    while read -r p; do mkdir -p "$(dirname "$p")"; cp "$W/$sub/$p" "$p"; done < "$S/list_$sub"
  fi
done
mkdir -p "$A/batch_$N/scripts"      # the scripts as run for this batch
cp "$B/c4_collect.py" "$B/verify_c4.py" "$B/x81_c4.sh" "$B/MANIFEST.sha256" "$A/batch_$N/scripts/"
cnt() { awk -F'\t' -v c="$1" 'NR > 1 && $4 == c' "$W/inventory.tsv" | grep -c . || true; }
gbs() { awk -F'\t' -v c="$1" 'NR > 1 && $4 == c {s += $1} END {printf "%.2f", s/1e9}' "$W/inventory.tsv"; }
nt=$(cnt git_text); nx=$(cnt git_xz); na=$(cnt git_asis); nk=$(cnt pc_keep); nsc=$(cnt scratch); nl=$(cnt link)
ntot=$((nt + nx + na + nk + nsc)); gtot=$(awk -F'\t' 'NR > 1 && $4 != "-" && $4 != "link" {s += $1} END {printf "%.2f", s/1e9}' "$W/inventory.tsv")
nar=$(grep -c . "$W/ARCHIVES_BUILT.tsv" || true); nw=$(grep -cE '/reopt\.(gbw|densities)$' "$W/INDIV.sha256" || true)
nr=$(wc -l < "$S/todo"); npa=$(($(grep -c . "$S/PC_ARCHIVES.tsv") - 1))
nconv=$(grep -c "C4_REOPT_CONVERGED" "$W/RUNS.txt" || true); ninc=$(grep -c "C4_REOPT_INCOMPLETE" "$W/RUNS.txt" || true)
nkill=$(grep -cE "PBS: job killed|=>> PBS" "$W/RUNS.txt" || true)
runs=$(cut -f1 "$W/RUNS.txt" | tr '\n' ' ' | sed 's/ $//')
{ echo "C4's re-optimisation runs kept as physical files, batch $N ($X): what was archived and what was committed"
  echo
  echo "Rule (Jessica, 18 October 2026): every output file of a finished job is downloaded and kept as a physical file, not"
  echo "only reported; for C4 this comes before its analysis (C4_CLOSURE.txt). Runs (jobs ended; RUNS.txt, with how each"
  echo "job's output ends):"; echo "$runs" | fold -s -w 116 | sed 's/^/  /'
  echo "Job outputs at staging time: $nconv with C4_REOPT_CONVERGED, $ninc with C4_REOPT_INCOMPLETE, $nkill with a PBS"
  echo "message (e.g. the walltime). Whether a run is finished in C4's sense (M1) is for the analysis, not this batch."
  echo
  echo "1. PC archives (PC_ARCHIVES.tsv; one per run, in the archive folder on Jessica's PC): all $ntot regular files of"
  echo "   the batch ($gtot GB uncompressed), every member's sha256 checked against inventory.tsv after the download and"
  echo "   again where it lies; PCMANIFEST_RUN.sha256 lists each member. Nothing of the batch exists only on hpc1."
  if [ "$nreuse" -gt 0 ]; then
    echo "   $nreuse of these PC archives were already in place from an earlier run of this commit that stopped before its git"
    echo "   commit (for batch 1: x80's run, stopped when the PC's disk filled); each was tested whole (xz -t), checked member"
    echo "   by member against this batch's inventory again, and reused."
  fi
  echo "2. In this repo: $nt text files in $nar tar.xz archives with manifests (hpc_text_outputs_$N.tar.xz in each run"
  echo "   folder: ORCA input and output, job script and output, energy CSV, start and final geometries, gradients and other"
  echo "   text); $nx file(s) compressed one by one as .xz ($nw final wavefunction/densities files, the rest text over"
  echo "   50 MB; individual.tsv); $na file(s) as the jobs compressed them (as_is.tsv)."
  echo "3. On the PC only (pc_keep.tsv; they stay on hpc1): $nk trajectory and binary file(s) - a run killed by the walltime"
  echo "   keeps its trajectory for its M1 continuation - and $nsc scratch file(s)."
  echo "4. Links (links.tsv, $nl): the force field, with the target's sha256 in inventory.tsv."
  echo "$X deletes nothing on hpc1. Checks (scripts/verify_c4.py, on the PC, before this commit): every PC archive read"
  echo "member by member; every git archive extracted and matched to its manifest; every .xz decompressed and matched to"
  echo "its original's sha256; nothing committed overwrites a file."
} > "$A/batch_$N/README.txt"
git add -A "$A" "$T"
[ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify or delete a committed file: tell Claude"
nf=$(git diff --cached --name-only | wc -l)
git commit -q -m "C4's re-optimisation runs kept as physical files, batch $N ($X), before C4's analysis (C4_CLOSURE.txt): every file of $nr run(s) whose jobs have ended ($runs) downloaded into $npa PC archive(s) ($ntot files, $gtot GB, each sha256 checked; PC_ARCHIVES.tsv, PCMANIFEST_*.sha256); committed here: $nt text files in $nar archives with manifests, $nx file(s) as .xz ($nw final wavefunction/densities), $na as compressed by the jobs; job outputs at staging: $nconv converged, $ninc incomplete, $nkill with a PBS message; the scripts as run; PC only: $nk trajectory/binary, $nsc scratch; nothing deleted on hpc1 [retained-final]" -m "$TRAILER"
COPYING=0
echo "committed: $(git log -1 --format=%h) ($nf files)"
git push -q || stop "push failed: run  git -C $RES push origin main"
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub after the push: run  git -C $RES push origin main"
echo "pushed: results $(git log -1 --format=%h)"
echo "PC archives: $ARCH/$T/<run>/hpc_all_files_c4_batch_$N.tar.xz (back this folder up)"
if sshc -n "$HPC" "rm -rf $OUT"; then echo "removed the stage $OUT on hpc1 (copies only; its lists are committed)"
else echo "NOTE: removing the stage failed; it holds copies only, remove it by hand:  ssh $HPC \"rm -rf $OUT\""; fi
exit 0
