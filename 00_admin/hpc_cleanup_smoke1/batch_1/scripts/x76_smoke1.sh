#!/usr/bin/env bash
# x76_smoke1.sh - RUN ON THE PC (not on hpc1):  bash x76/x76_smoke1.sh status | commit | delete
# Clean-up of SP smoke test 1 (05_qmmm/24_sp_barriers/f42436_r8 and f42436_r6, exploratory since SP Amendment 1), done
# the way the 7 October clean-up was (results 00_admin/hpc_cleanup_20261007): the outputs are committed first, with the
# sha256 of every file to be deleted, and afterwards only the listed files whose sha256 still matches are deleted.
#   status  read-only: every job of smoke test 1 (its SUBMITTED, qstat now), each step's record, and what the clean-up
#           would do with the files of each step whose job has ended. Changes nothing anywhere.
#   commit  for the steps whose jobs have ended and that are not committed yet: stages them on hpc1 (copies only, in
#           ~/x76_stage), fetches the stage, extracts every archive and checks each file against its sha256, then
#           commits to the results repo (archives and compressed outputs in the run folders; records, the deletion list
#           and the scripts as run in 00_admin/hpc_cleanup_smoke1/batch_N) and pushes. Deletes nothing.
#   delete  for the oldest committed batch not yet deleted: asks you to type DELETE, then on hpc1 deletes the listed
#           files and replaces the large outputs by their committed .xz - only if the lists on hpc1 are the committed
#           ones, no listed file belongs to a job still in the queue and each file's sha256 still matches. Commits the
#           deletion log, the files left and the post-deletion check, and pushes.
# Smoke test 1's 8 A R0 (418083) is still running and its frequencies (418084) are held: their steps are left out now;
# run commit and delete again when both have ended. Safe to re-run: a finished step is checked and skipped.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
HPC="18660916@hpc"
SD=/home/18660916/system_development/05_qmmm/24_sp_barriers
STG=/home/18660916/x76_stage
T=05_qmmm/24_sp_barriers
A=00_admin/hpc_cleanup_smoke1
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
stop() { echo "STOP: $*"; exit 1; }
MODE=${1:-}
case "$MODE" in status|commit|delete) ;; *) stop "usage: bash x76/x76_smoke1.sh status | commit | delete";; esac
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
remote() { ssh "$HPC" "python3 - $*" < "$B/smoke1_cleanup.py"; }      # the hpc1 script, read from the bundle each time
batches() { local d; for d in "$RES/$A"/batch_*; do if [ -d "$d" ]; then basename "$d"; fi; done | sort -V; }   # committed batches

if [ "$MODE" = status ]; then
  remote status "$SD" | grep -v '^STEPSTATE ' || stop "status failed on hpc1 (above)"
  exit 0
fi

command -v python3 >/dev/null || stop "python3 is needed on the PC"
git -C "$RES" pull --ff-only -q || stop "git pull failed in $RES"
[ -z "$(git -C "$RES" status --porcelain)" ] || stop "$RES has uncommitted changes"
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ -e "$RES/$T/SP_ERRATUM1.txt" ] || stop "$T/SP_ERRATUM1.txt is not in the results repo (x75 first)"
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
cd "$RES"

if [ "$MODE" = commit ]; then
  # ---- 1. which steps have ended and are not committed yet
  remote status "$SD" > "$S/status.txt" || { tail -5 "$S/status.txt"; stop "status failed on hpc1"; }
  awk '$1 == "STEPSTATE" && $3 == "ended" {print $2}' "$S/status.txt" | LC_ALL=C sort > "$S/ended"
  [ -s "$S/ended" ] || stop "hpc1 reported no step states"
  : > "$S/done"; for d in $(batches); do cut -f1 "$A/$d/STEPS.txt" >> "$S/done"; done
  LC_ALL=C sort -u -o "$S/done" "$S/done"
  LC_ALL=C comm -23 "$S/ended" "$S/done" > "$S/todo"
  if [ ! -s "$S/todo" ]; then
    echo "nothing new to commit: every step whose job has ended is committed ($(batches | wc -l) batch(es))"
    grep -E '^  (f42436|UNKNOWN)' "$S/status.txt" | grep -v '_run ' || true
    exit 0
  fi
  nb=$(batches | wc -l); N=$((nb + 1))
  echo "batch $N: $(wc -l < "$S/todo") step(s) whose jobs have ended: $(tr '\n' ' ' < "$S/todo")"
  # ---- 2. stage on hpc1 (copies only)
  OUT=$STG/batch_$N
  if ssh "$HPC" "test -e $OUT"; then
    if ssh "$HPC" "test -e $OUT/DONE" && [ "$(ssh "$HPC" "cut -f1 $OUT/STEPS.txt" | LC_ALL=C sort)" = "$(cat "$S/todo")" ]; then
      echo "   batch $N was staged already on hpc1 with these steps: using that stage"
    else
      stop "$OUT exists on hpc1 from an unfinished or different stage. It holds copies only; remove it with  ssh $HPC \"rm -rf $OUT\"  and run commit again"
    fi
  else
    ssh "$HPC" "mkdir -p $STG"
    remote stage "$SD" "$OUT" "$N" $(cat "$S/todo") || stop "staging stopped on hpc1 (above); nothing was committed"
  fi
  # ---- 3. fetch and verify every file
  ssh "$HPC" "cd $STG && tar -cf - batch_$N" | tar -xf - -C "$S" || stop "fetching the stage from hpc1 failed"
  W=$S/batch_$N
  python3 "$B/verify_stage.py" stage "$W" "$RES" || stop "the fetched stage did not verify (above); nothing was committed"
  # ---- 4. commit (additions only) and push
  mkdir -p "$A/batch_$N"
  for f in STEPS.txt SUMMARY.txt inventory.tsv archives.tsv ARCHIVES_BUILT.tsv individual.tsv INDIV.sha256 \
           INDIV_XZ.sha256 as_is.tsv AS_IS.sha256 delete.tsv DELETE_CHECKSUMS.sha256 keep.tsv SP_REPORT.txt; do
    cp "$W/$f" "$A/batch_$N/$f"
  done
  for sub in arch indiv asis; do      # archives with manifests; outputs compressed one by one; files the jobs compressed
    if [ -d "$W/$sub" ]; then
      ( cd "$W/$sub" && find . -type f | sed 's|^\./||' ) > "$S/list_$sub"
      while read -r p; do mkdir -p "$(dirname "$p")"; cp "$W/$sub/$p" "$p"; done < "$S/list_$sub"
    fi
  done
  mkdir -p "$A/batch_$N/scripts"      # the scripts as run for this batch
  cp "$B/smoke1_cleanup.py" "$B/verify_stage.py" "$B/x76_smoke1.sh" "$B/MANIFEST.sha256" "$A/batch_$N/scripts/"
  read -r na nm < <(awk -F'\t' '{n++; m+=$2} END {print n+0, m+0}' "$W/ARCHIVES_BUILT.tsv")
  nc=$(grep -c . "$W/individual.tsv" || true); nx=$(grep -c . "$W/as_is.tsv" || true)
  nd=$(grep -c . "$W/delete.tsv" || true); nk=$(grep -c . "$W/keep.tsv" || true)
  nko=$(awk -F'\t' '$1 != "link" && $1 != "frequency Hessian"' "$W/keep.tsv" | grep -c . || true)
  ntr=$(grep -c "full-system trajectory" "$W/delete.tsv" || true); nth=$(grep -c "the TS search's own Hessian" "$W/delete.tsv" || true)
  gd=$(awk -F'\t' '{s+=$2} END {printf "%.2f", s/1e9}' "$W/delete.tsv")
  gc=$(awk -F'\t' '{s+=$1} END {printf "%.2f", s/1e9}' "$W/individual.tsv")
  steps=$(tr '\n' ' ' < "$S/todo" | sed 's/ $//')
  { echo "SP smoke test 1 clean-up, batch $N: what was committed, what is to be deleted, and why"
    echo
    echo "Steps (jobs ended; STEPS.txt): $steps"
    echo "Done as on 7 October (00_admin/hpc_cleanup_20261007): staged on hpc1 by scripts/smoke1_cleanup.py (non-destructive),"
    echo "fetched and checked on the PC by scripts/verify_stage.py (every archive extracted and each member compared with"
    echo "its manifest; every compressed output decompressed and compared with its original's sha256), committed here"
    echo "before anything is deleted. inventory.tsv lists every file of both run folders at staging time."
    echo
    echo "Committed: $na archive(s) of text files ($nm files; hpc_text_outputs_$N.tar.xz with .MANIFEST.sha256, in the run"
    echo "folders), kept on hpc1; $nc text output(s) over 50 MB as .xz ($gc GB uncompressed; individual.tsv), which replace"
    echo "the originals on hpc1 at deletion; $nx file(s) already compressed by the jobs, as they are (as_is.tsv);"
    echo "SP_REPORT.txt, sp_report.py's report of smoke test 1 at staging time."
    echo "To be deleted on hpc1 (delete.tsv, DELETE_CHECKSUMS.sha256): $nd file(s), $gd GB. As on 7 October: scratch"
    echo "(*.tmp), approximate Hessians (*.appr.hess), Cartesian Hessians (*.carthess), wavefunctions and densities (*.gbw,"
    echo "*.gbwN, *.densities), *.dcd, *.mdrestart. Departures from 7 October, all in runs that ended without converging:"
    echo "(1) $ntr full-system trajectory(ies) over 20 MB (7 October kept optimisation trajectories) - deleted only where the"
    echo "step's activeRegion trajectory, committed, holds at least as many complete frames and its start.xyz is committed;"
    echo "ORCA moves no atom outside ActiveAtoms, so every frame is start.xyz with that frame's active atoms; (2) $nth TS"
    echo "search Hessian(s) (ts/*.hess; 7 October kept every .hess except *.appr.hess; the job scripts delete them after a"
    echo "passing TS step, which these never reached); (3) *.tmp.N scratch files, which 7 October's pattern did not cover."
    echo "Kept on hpc1, not committed (keep.tsv, sha256 recorded): $nk file(s) - links, frequency Hessians (as on 7 October),"
    echo "and $nko other file(s) left in place for the reason given in keep.tsv (e.g. basis-set scratch, binary files of no"
    echo "known kind)."
    echo "Deletion (x76_smoke1.sh delete): only files on the committed list whose sha256 still matches, and only if no"
    echo "listed file belongs to a job still in the queue; the log and the post-deletion check are added to this folder."
  } > "$A/batch_$N/README.txt"
  git add -A "$A" "$T"
  [ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify or delete a committed file: tell Claude"
  nf=$(git diff --cached --name-only | wc -l)
  git commit -q -m "SP smoke test 1 clean-up, step 1 of 2 (batch $N): outputs of the ended steps ($steps) committed before anything is deleted - $na archive(s) with member manifests ($nm files), $nc output(s) over 50 MB as .xz, $nx file(s) compressed by the jobs, sp_report.py's report at staging time, the scripts as run - and the deletion list with the sha256 of every file on it ($nd files, $gd GB: scratch, wavefunctions, densities, approximate Hessians as on 7 October; departures stated in README.txt: $ntr full-system trajectory(ies), each with a committed activeRegion trajectory of at least as many frames and its start.xyz, and $nth TS-search Hessian(s)); frequency Hessians and $nko file(s) of other kinds kept on hpc1; every archive member and compressed file checked against its sha256 on the PC [exploratory]" -m "$TRAILER"
  echo "committed: $(git log -1 --format=%h) ($nf files)"
  git push -q || stop "push failed: run  git -C $RES push  and then  bash x76/x76_smoke1.sh delete"
  git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub after the push: run  git -C $RES push"
  echo "pushed: results $(git log -1 --format=%h)"
  echo
  echo "NEXT - delete what is listed (asks you to type DELETE):  bash $B/x76_smoke1.sh delete"
  exit 0
fi

# ---- delete: the oldest committed batch without a deletion log in the repo
N=""
for d in $(batches); do [ -e "$A/$d/DELETED.log" ] || { N=$d; break; }; done
[ -n "$N" ] || { echo "nothing to delete: every committed batch has its deletion log"; exit 0; }
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "push the results repo first:  git -C $RES push"
ED=$(sha256sum < "$A/$N/DELETE_CHECKSUMS.sha256" | cut -c1-64)
EI=$(sha256sum < "$A/$N/INDIV.sha256" | cut -c1-64)
EX=$(sha256sum < "$A/$N/INDIV_XZ.sha256" | cut -c1-64)
nd=$(grep -c . "$A/$N/DELETE_CHECKSUMS.sha256" || true); ni=$(grep -c . "$A/$N/INDIV.sha256" || true)
gd=$(awk -F'\t' '{s+=$2} END {printf "%.2f", s/1e9}' "$A/$N/delete.tsv")
if ssh "$HPC" "test -e $STG/$N/DELETE.done"; then
  echo "$N: the deletion has run on hpc1 already; its log is fetched, checked and committed"
elif ssh "$HPC" "test -e $STG/$N/DELETE.lock"; then
  stop "$STG/$N/DELETE.lock exists on hpc1: a deletion is running, or an earlier one was interrupted (its actions so far are in $STG/$N/DELETED.log). Tell Claude before going on"
else
  echo "$N (steps: $(cut -f1 "$A/$N/STEPS.txt" | tr '\n' ' ')): on hpc1, delete $nd files ($gd GB) and replace $ni large"
  echo "output(s) by their committed .xz. Nothing else is touched; the frequency Hessians stay."
  read -r -p "Type DELETE to go ahead: " ans || ans=""
  [ "$ans" = DELETE ] || stop "not confirmed: nothing was deleted"
  remote delete "$SD" "$STG/$N" "$ED" "$EI" "$EX" || stop "the deletion stopped on hpc1 (above); see $STG/$N on hpc1"
fi
mkdir -p "$S/$N"      # the committed lists, with the log and the listing of what is left fetched from hpc1
cp "$A/$N/inventory.tsv" "$A/$N/DELETE_CHECKSUMS.sha256" "$A/$N/INDIV.sha256" "$S/$N/"
ssh "$HPC" "cd $STG/$N && tar -cf - DELETED.log REMAINING.tsv" | tar -xf - -C "$S/$N" || stop "fetching the deletion log from hpc1 failed: run delete again"
python3 "$B/verify_stage.py" postcheck "$S/$N" > "$S/post.txt" || { cat "$S/post.txt"; stop "the post-deletion check found a problem (above): tell Claude"; }
cat "$S/post.txt"
cp "$S/$N/DELETED.log" "$S/$N/REMAINING.tsv" "$A/$N/"
{ echo "# verify_stage.py postcheck, $(date '+%Y-%m-%dT%H:%M:%S%z'), on the fetched DELETED.log and REMAINING.tsv"; cat "$S/post.txt"; } > "$A/$N/POSTCHECK.txt"
git add "$A/$N"
[ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify a committed file: tell Claude"
git commit -q -m "SP smoke test 1 clean-up, step 2 of 2 ($N): deletion log, the files left in both run folders and the post-deletion check - $(sed 's/^post-check: //' "$S/post.txt") [exploratory]" -m "$TRAILER"
git push -q || stop "push failed: run  git -C $RES push"
echo "committed and pushed: results $(git log -1 --format=%h)"
