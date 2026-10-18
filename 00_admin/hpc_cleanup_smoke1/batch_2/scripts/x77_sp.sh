#!/usr/bin/env bash
# x77_sp.sh - RUN ON THE PC (not on hpc1):  bash x77/x77_sp.sh status | commit | delete
# The outputs of the SP runs (05_qmmm/24_sp_barriers: smoke test 1 f42436_r8 and f42436_r6, smoke test 2 f42436_r8_a1
# and f42436_r6_a1) kept as physical files before anything is removed from hpc1 (Jessica's rule of 18 October 2026:
# every output downloaded and committed, not only reported). Replaces x76 for every step x76 has not committed; x76's
# batch 1 stays as it is. Batches continue in the results repo's 00_admin/hpc_cleanup_smoke1 (batch_2, ...).
#   status  read-only: every job of the four runs (SUBMITTED, qstat now), each step's record and what would happen to
#           its files, and whether every file now in a step a batch has taken was archived or committed by a batch.
#           Changes nothing anywhere.
#   commit  first checks that every file now in a step a batch has taken was archived or committed by a batch, with the
#           same size and modification time (so that nothing written later, e.g. by a rerun, is missed), and that no
#           folder is named after one of the four runs without being one; then for the steps whose jobs have ended and that no batch
#           holds yet, and for the files x76's batches left on hpc1 (their keep lists: frequency Hessian and basis-set
#           files, sha256 checked): stages them on hpc1 (copies only,
#           in ~/x77_stage); downloads EVERY regular file of the batch into a PC archive per run (default
#           ~/Desktop/chorismate-hpc-archive, or $X77_ARCHIVE) and checks every file's sha256; fetches the stage and checks
#           every git archive and compressed file; then commits to the results repo the readable outputs, geometries,
#           Hessians and final wavefunctions, the sha256 of every archived file and where each PC archive is, and pushes.
#           Deletes nothing.
#   delete  for the oldest x77 batch not yet deleted: repeats commit's file check, checks every PC archive of that batch
#           against its committed sha256 (each member too), asks you to type DELETE, then on hpc1 (using the batch's stage
#           in ~/x77_stage, which must be kept until then) deletes the listed scratch and working files and
#           replaces text files over 50 MB (committed one by one) by their .xz - only if every one of them is in the
#           committed PC-archive manifests, the lists on hpc1 are the committed ones, each file's step still has the job
#           the batch recorded and that job has ended, and each file's sha256 still matches. Commits the deletion log, the files left and the
#           post-deletion check, pushes, and then removes the batch's stage (copies) from hpc1.
# Safe to re-run: a finished step is checked and skipped; anything unexpected stops it with a message.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
ARCH="${X77_ARCHIVE:-$HOME/Desktop/chorismate-hpc-archive}"
HPC="18660916@hpc"
ROOT=/home/18660916/system_development
SD=$ROOT/05_qmmm/24_sp_barriers
STG=/home/18660916/x77_stage
T=05_qmmm/24_sp_barriers
A=00_admin/hpc_cleanup_smoke1
RUNS="f42436_r8 f42436_r6 f42436_r8_a1 f42436_r6_a1"
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
    echo "are in place but recorded in no commit yet: the next commit checks them, keeps them if identical to its own"
    echo "download, and otherwise moves them aside). To clear the uncommitted copies before running commit again:"
    echo "  git -C $RES reset -q --hard HEAD && git -C $RES clean -fdq -- 00_admin 05_qmmm"
  fi
}
trap on_exit EXIT
MODE=${1:-}
case "$MODE" in status|commit|delete) ;; *) stop "usage: bash x77/x77_sp.sh status | commit | delete";; esac
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
sshc() { ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=10 "$@"; }
remote() { sshc "$HPC" "python3 - $*" < "$B/sp_cleanup.py"; }      # the hpc1 script, read from the bundle each time
track() {     # every file now in a step a batch has taken: archived or committed by a batch (verify_stage.py track)
  remote files "$SD" > "$S/files.txt" || { tail -3 "$S/files.txt"; return 1; }
  python3 "$B/verify_stage.py" track "$RES/$A" "$S/files.txt"
}
batches() { local d; for d in "$RES/$A"/batch_*; do if [ -d "$d" ]; then basename "$d"; fi; done | sort -V; }
if [ "$MODE" = status ]; then
  remote status "$SD" | grep -v '^STEPSTATE ' || stop "status failed on hpc1 (above)"
  echo "== files of the steps the batches have taken (results repo as it is on this PC)"
  track || echo "   (commit stops on this; nothing was changed)"
  exit 0
fi
command -v python3 >/dev/null || stop "python3 is needed on the PC"
command -v xz >/dev/null || stop "xz is needed on the PC"
git -C "$RES" pull --ff-only -q || stop "git pull failed in $RES"
[ -z "$(git -C "$RES" status --porcelain)" ] || stop "$RES has uncommitted changes"
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ -e "$RES/$T/SP_ERRATUM1.txt" ] || stop "$T/SP_ERRATUM1.txt is not in the results repo (x75 first)"
[ -e "$RES/$T/f42436_r8_a1/GENERATOR_LOG.txt" ] || stop "smoke test 2's inputs are not in the results repo (x74 first)"
[ -e "$RES/$A/batch_1/DELETED.log" ] || stop "x76's batch 1 is not complete in the results repo"
cd "$RES"

if [ "$MODE" = commit ]; then
  # ---- 1. what this batch takes: steps whose jobs have ended and that no batch holds; files x76 left on hpc1
  track || stop "the file check found something no batch holds (above): nothing was staged or committed"
  remote status "$SD" > "$S/status.txt" || { tail -5 "$S/status.txt"; stop "status failed on hpc1"; }
  awk '$1 == "STEPSTATE" && $3 == "ended" {print $2}' "$S/status.txt" | LC_ALL=C sort > "$S/ended"
  [ -s "$S/ended" ] || stop "hpc1 reported no step states"
  : > "$S/done"; for d in $(batches); do cut -f1 "$A/$d/STEPS.txt" >> "$S/done"; done
  LC_ALL=C sort -u -o "$S/done" "$S/done"
  LC_ALL=C comm -23 "$S/ended" "$S/done" > "$S/todo"
  python3 "$B/verify_stage.py" extras "$RES/$A" > "$S/extras" || { cat "$S/extras"; stop "reading x76's keep lists failed (above)"; }
  if [ ! -s "$S/todo" ] && [ ! -s "$S/extras" ]; then
    echo "nothing new to commit: every step whose job has ended is in a batch ($(batches | wc -l) batch(es)), and nothing x76 left on hpc1 is outstanding"
    exit 0
  fi
  nb=$(batches | wc -l); N=$((nb + 1))
  echo "batch $N: $(wc -l < "$S/todo") step(s) whose jobs have ended, and $(wc -l < "$S/extras") file(s) that x76 left on hpc1"
  # ---- 2. stage on hpc1 (copies only)
  OUT=$STG/batch_$N
  if sshc -n "$HPC" "test -e $OUT"; then
    sshc -n "$HPC" "test -e $OUT/DONE" || stop "$OUT exists on hpc1 from an unfinished stage. It holds copies only; remove it with  ssh $HPC \"rm -rf $OUT\"  and run commit again"
    sshc -n "$HPC" "cut -f1 $OUT/STEPS.txt" | LC_ALL=C sort > "$S/st_steps"
    sshc -n "$HPC" "cut -f1 $OUT/EXTRAS.txt" | LC_ALL=C sort > "$S/st_extras"
    sed 's/^+//; s/=[0-9a-f]*$//' "$S/extras" | LC_ALL=C sort > "$S/my_extras"
    if cmp -s "$S/st_steps" "$S/todo" && cmp -s "$S/st_extras" "$S/my_extras"; then
      echo "   batch $N was staged already on hpc1 with these steps and files: using that stage"
    else
      stop "$OUT exists on hpc1 from a different stage. It holds copies only; remove it with  ssh $HPC \"rm -rf $OUT\"  and run commit again"
    fi
  else
    sshc -n "$HPC" "mkdir -p $STG"
    remote stage "$SD" "$OUT" "$N" $(cat "$S/todo" "$S/extras") || stop "staging stopped on hpc1 (above); nothing was committed"
  fi
  # ---- 3. download every file of the batch into the PC archives, then fetch the stage, and check everything
  IN="$ARCH/.incoming_batch_$N"; rm -rf "$IN"; mkdir -p "$IN"
  sshc -n "$HPC" "cd $STG && tar -cf - batch_$N" | tar -xf - -C "$S" || stop "fetching the stage from hpc1 failed"
  W=$S/batch_$N
  for r in $RUNS; do
    [ -f "$W/PCLIST_$r.txt" ] || continue
    echo "   downloading every file of $r in this batch ($(wc -l < "$W/PCLIST_$r.txt") files) ..."
    sshc -n "$HPC" "bash -c 'set -o pipefail; cd $ROOT && tar -cf - --no-recursion -T $OUT/PCLIST_$r.txt | xz -1 -T1 -c'" > "$IN/$r.tar.xz" \
      || stop "downloading the files of $r failed; nothing was committed (run commit again)"
  done
  python3 "$B/verify_stage.py" stage "$W" "$RES" "$IN" || stop "the download or the stage did not verify (above); nothing was committed"
  # ---- 4. the PC archives into place, with their manifests; then verified again where they lie
  printf "# run\tPC archive (relative to the archive folder %s)\tbytes\tsha256\tmembers\n" "$ARCH" > "$S/PC_ARCHIVES.tsv"
  for r in $RUNS; do
    [ -f "$W/PCLIST_$r.txt" ] || continue
    D="$ARCH/$T/$r"; F="$D/hpc_all_files_batch_$N.tar.xz"; M="${F%.tar.xz}.MANIFEST.sha256"
    mkdir -p "$D"
    awk -F'\t' -v r="$r" 'NR > 1 && $4 != "-" && $4 != "link" { split($3, q, "/"); if (q[3] == r) print $5 "  " $3 }' "$W/inventory.tsv" | LC_ALL=C sort -k2 > "$S/manifest_$r"
    if [ -e "$F" ] && cmp -s "$F" "$IN/$r.tar.xz" && cmp -s "$M" "$S/manifest_$r"; then
      rm "$IN/$r.tar.xz"; echo "   $F: already in place from an earlier run of this commit, identical"
    else
      if [ -e "$F" ] || [ -e "$M" ]; then  # left by an earlier commit of this batch that stopped before its git commit
        X="$D/unrecorded_$(date +%Y%m%dT%H%M%S)"; mkdir -p "$X"
        for f in "$F" "$M"; do if [ -e "$f" ]; then mv "$f" "$X/"; fi; done
        echo "   an earlier, uncommitted download of this batch differs from this one (other steps): moved aside to $X"
      fi
      cp "$S/manifest_$r" "$M"; mv "$IN/$r.tar.xz" "$F"
    fi
    python3 "$B/verify_stage.py" pcarchive "$F" "$M" || stop "the PC archive $F did not verify where it lies: tell Claude"
    printf "%s\t%s\t%s\t%s\t%s\n" "$r" "${F#$ARCH/}" "$(stat -c %s "$F")" "$(sha256sum < "$F" | cut -c1-64)" "$(grep -c . "$M")" >> "$S/PC_ARCHIVES.tsv"
    cp "$M" "$S/PCMANIFEST_$r.sha256"
  done
  rmdir "$IN" 2>/dev/null || true
  # ---- 5. commit (additions only) and push
  COPYING=1
  mkdir -p "$A/batch_$N"
  for f in STEPS.txt EXTRAS.txt SUMMARY.txt inventory.tsv archives.tsv ARCHIVES_BUILT.tsv individual.tsv INDIV.sha256 \
           INDIV_XZ.sha256 as_is.tsv AS_IS.sha256 delete.tsv DELETE_CHECKSUMS.sha256 pc_keep.tsv links.tsv SP_REPORT.txt \
           SPA_REPORT.txt; do
    cp "$W/$f" "$A/batch_$N/$f"
  done
  cp "$S/PC_ARCHIVES.tsv" "$A/batch_$N/"
  for r in $RUNS; do if [ -f "$S/PCMANIFEST_$r.sha256" ]; then cp "$S/PCMANIFEST_$r.sha256" "$A/batch_$N/"; fi; done
  for sub in arch indiv asis; do      # git archives with manifests; files compressed one by one; files the jobs compressed
    if [ -d "$W/$sub" ]; then
      ( cd "$W/$sub" && find . -type f | sed 's|^\./||' ) > "$S/list_$sub"
      while read -r p; do mkdir -p "$(dirname "$p")"; cp "$W/$sub/$p" "$p"; done < "$S/list_$sub"
    fi
  done
  mkdir -p "$A/batch_$N/scripts"      # the scripts as run for this batch
  cp "$B/sp_cleanup.py" "$B/verify_stage.py" "$B/x77_sp.sh" "$B/MANIFEST.sha256" "$A/batch_$N/scripts/"
  cnt() { awk -F'\t' -v c="$1" 'NR > 1 && $4 == c' "$W/inventory.tsv" | grep -c . || true; }
  gbs() { awk -F'\t' -v c="$1" 'NR > 1 && $4 == c {s += $1} END {printf "%.2f", s/1e9}' "$W/inventory.tsv"; }
  nt=$(cnt git_text); nx=$(cnt git_xz); na=$(cnt git_asis); nk=$(cnt pc_keep); nd=$(cnt pc_delete); nl=$(cnt link)
  ntot=$((nt + nx + na + nk + nd)); gtot=$(awk -F'\t' 'NR > 1 && $4 != "-" && $4 != "link" {s += $1} END {printf "%.2f", s/1e9}' "$W/inventory.tsv")
  nar=$(grep -c . "$W/ARCHIVES_BUILT.tsv" || true); nw=$(grep -cE '\.(gbw|densities)$' "$W/INDIV.sha256" || true)
  ne=$(grep -c . "$W/EXTRAS.txt" || true); npa=$(($(grep -c . "$S/PC_ARCHIVES.tsv") - 1))
  nrep=$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import verify_stage as v
print(sum(1 for r in v.tsv(sys.argv[2]) if v.replaceable(r[1])))' "$B" "$W/individual.tsv")
  region=$(grep -E '^  -> ' "$W/SPA_REPORT.txt" | tail -1 | sed 's/^  -> //' || true)
  steps=$(cut -f1 "$W/STEPS.txt" | tr '\n' ' ' | sed 's/ $//')
  { echo "SP runs' outputs kept as physical files, batch $N (x77): what was archived, what was committed, what is to be deleted"
    echo
    echo "Rule (Jessica, 18 October 2026): every output file of a finished step is downloaded and kept as a physical file,"
    echo "not only reported. Steps (jobs ended; STEPS.txt): $steps"
    echo "Also $ne file(s) that x76's batches had left on hpc1 uncommitted (EXTRAS.txt: frequency Hessian, basis-set files)."
    echo "Smoke test 1's steps are exploratory (SP Amendment 1); smoke test 2's are SP Amendment 1's. Region rule at staging"
    echo "time (SPA_REPORT.txt, spa_report.py smoke): ${region:-no verdict line found}."
    echo
    echo "1. PC archives (PC_ARCHIVES.tsv; one per run, in the archive folder on Jessica's PC): all $ntot regular files of"
    echo "   the batch ($gtot GB uncompressed), every member's sha256 checked against inventory.tsv after the download and"
    echo "   again where it lies; PCMANIFEST_RUN.sha256 lists each member. Nothing of the batch exists only on hpc1."
    echo "2. In this repo: $nt text files in $nar tar.xz archives with manifests (hpc_text_outputs_${N}_STEP.tar.xz in the run"
    echo "   folders; ORCA inputs and outputs, geometries, QM-region trajectories, Hessians, gradients, records, job outputs);"
    echo "   $nx file(s) compressed one by one as .xz ($nw wavefunction/densities files of the steps' final states, the rest"
    echo "   text over 50 MB; individual.tsv); $na file(s) as the jobs compressed them (as_is.tsv). On hpc1, $nrep text"
    echo "   file(s) over 50 MB in step folders will be replaced by that same .xz; every other file committed here stays."
    echo "3. On the PC only (pc_keep.tsv, $nk file(s); stay on hpc1): active-region trajectories (also as the jobs"
    echo "   compressed them), full-system trajectories over 20 MB, MD-format files, binary files of no other kind, jobs'"
    echo "   .xz over 95 MB. To be deleted from hpc1 after this commit (delete.tsv, $nd file(s), $(gbs pc_delete) GB, all in the"
    echo "   PC archives): scratch and working files only - ORCA scratch, the optimiser's working Hessians, and the"
    echo "   wavefunctions and densities of intermediate states."
    echo "4. Links (links.tsv, $nl): the force field, with the target's sha256 in inventory.tsv."
    echo "Already gone before this batch, as the job scripts did after each passing step (SP_PLAN, SP Amendment 1;"
    echo "FILES_BEFORE_CLEANUP.txt in each step or cycle folder lists them): full-system trajectories, scratch, the IRC"
    echo "step's copy of the TS frequency Hessian (the original is in ts_freq), and in cycle folders the DCD trajectory,"
    echo "full-system PDB, densities and start.xyz. x76's batch 1, before the rule, deleted without a PC copy its steps'"
    echo "scratch, wavefunctions and densities, approximate and TS-search Hessians and two full-system trajectories"
    echo "(its delete.tsv lists each); those cannot be recovered, only recomputed from the committed geometries and inputs."
    echo "Checks (scripts/verify_stage.py, on the PC, before this commit): every file of the steps earlier batches took is"
    echo "in one of them with the same size and modification time; every PC archive read member by member; every git archive extracted and matched to its manifest;"
    echo "every .xz decompressed and matched to its original's sha256; every file to be deleted is scratch or a working"
    echo "file in a step folder."
    echo "Deletion (x77_sp.sh delete): only after every PC archive of the batch verifies again against PC_ARCHIVES.tsv and"
    echo "its manifest, and every file to be deleted is in those manifests; only listed files whose sha256 still matches;"
    echo "the log and post-deletion check are added here."
  } > "$A/batch_$N/README.txt"
  git add -A "$A" "$T"
  [ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify or delete a committed file: tell Claude"
  nf=$(git diff --cached --name-only | wc -l)
  git commit -q -m "SP runs' outputs kept as physical files, step 1 of 2 (batch $N, x77): every file of the ended steps ($steps) and $ne file(s) x76 left on hpc1 downloaded into $npa PC archive(s) ($ntot files, $gtot GB, each sha256 checked; PC_ARCHIVES.tsv, PCMANIFEST_*.sha256); committed here: $nt text files in $nar archives with manifests, $nx file(s) as .xz ($nw final-state wavefunction/densities), $na as compressed by the jobs; sp_report.py's and spa_report.py's reports at staging time; the scripts as run; PC only: $nk; to be deleted from hpc1 after this commit: $nd file(s), $(gbs pc_delete) GB (scratch, working Hessians, intermediate wavefunctions) [retained-final]" -m "$TRAILER"
  COPYING=0
  echo "committed: $(git log -1 --format=%h) ($nf files)"
  git push -q || stop "push failed: run  git -C $RES push origin main  and then  bash x77/x77_sp.sh delete"
  git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub after the push: run  git -C $RES push origin main"
  echo "pushed: results $(git log -1 --format=%h)"
  echo "PC archives: $ARCH/$T/<run>/hpc_all_files_batch_$N.tar.xz (back this folder up)"
  echo
  echo "NEXT - delete what is listed (checks the PC archives first, then asks you to type DELETE):  bash $B/x77_sp.sh delete"
  echo "(keep $OUT on hpc1 until then: the deletion uses its lists and .xz copies, and removes it afterwards)"
  exit 0
fi

# ---- delete: the oldest x77 batch (one with PC_ARCHIVES.tsv) without a deletion log in the repo
N=""
for d in $(batches); do
  [ -e "$A/$d/DELETED.log" ] && continue
  [ -e "$A/$d/PC_ARCHIVES.tsv" ] || stop "$d has no deletion log and was not made by x77: tell Claude"
  N=$d; break
done
[ -n "$N" ] || { echo "nothing to delete: every committed batch has its deletion log"; exit 0; }
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "push the results repo first:  git -C $RES push origin main"
track || stop "the file check found something no batch holds (above): nothing was deleted; tell Claude"
echo "$N: checking every PC archive of this batch (each member's sha256) before anything is deleted ..."
python3 "$B/verify_stage.py" precheck "$A/$N" || stop "a file to be deleted is not in this batch's committed PC-archive manifests: nothing was deleted; tell Claude"
while IFS=$'\t' read -r r f size h nm <&3; do
  case "$r" in \#*|"") continue;; esac
  P="$ARCH/$f"
  [ -f "$P" ] || stop "the PC archive $P is missing: nothing was deleted"
  [ "$(stat -c %s "$P")" = "$size" ] && [ "$(sha256sum < "$P" | cut -c1-64)" = "$h" ] || stop "the PC archive $P is not the committed one: nothing was deleted"
  python3 "$B/verify_stage.py" pcarchive "$P" "$A/$N/PCMANIFEST_$r.sha256" || stop "the PC archive $P did not verify: nothing was deleted"
done 3< "$A/$N/PC_ARCHIVES.tsv"
ED=$(sha256sum < "$A/$N/DELETE_CHECKSUMS.sha256" | cut -c1-64)
EI=$(sha256sum < "$A/$N/INDIV.sha256" | cut -c1-64)
EX=$(sha256sum < "$A/$N/INDIV_XZ.sha256" | cut -c1-64)
ES=$(sha256sum < "$A/$N/STEPS.txt" | cut -c1-64)
nd=$(grep -c . "$A/$N/DELETE_CHECKSUMS.sha256" || true)
gd=$(awk -F'\t' '{s+=$2} END {printf "%.2f", s/1e9}' "$A/$N/delete.tsv")
if sshc -n "$HPC" "test -e $STG/$N/DELETE.done"; then
  echo "$N: the deletion has run on hpc1 already; its log is fetched, checked and committed"
elif ! sshc -n "$HPC" "test -e $STG/$N/DONE"; then
  stop "the stage $STG/$N is missing on hpc1, and the deletion needs its lists and .xz copies: nothing was deleted; tell Claude"
elif sshc -n "$HPC" "test -e $STG/$N/DELETE.lock"; then
  stop "$STG/$N/DELETE.lock exists on hpc1: a deletion is running, or an earlier one was interrupted (its actions so far are in $STG/$N/DELETED.log). Tell Claude before going on"
else
  echo "$N (steps: $(cut -f1 "$A/$N/STEPS.txt" | tr '\n' ' ')): on hpc1, delete $nd scratch and working file(s) ($gd GB;"
  echo "every one is in the verified PC archives) and replace the text files over 50 MB committed one by one by their"
  echo "committed .xz. Nothing else is touched."
  read -r -p "Type DELETE to go ahead: " ans || ans=""
  [ "$ans" = DELETE ] || stop "not confirmed: nothing was deleted"
  remote delete "$SD" "$STG/$N" "$ED" "$EI" "$EX" "$ES" || stop "the deletion stopped on hpc1 (above); see $STG/$N on hpc1"
fi
mkdir -p "$S/$N"      # the committed lists, with the log and the listing of what is left fetched from hpc1
cp "$A/$N/inventory.tsv" "$A/$N/DELETE_CHECKSUMS.sha256" "$A/$N/INDIV.sha256" "$S/$N/"
sshc -n "$HPC" "cd $STG/$N && tar -cf - DELETED.log REMAINING.tsv" | tar -xf - -C "$S/$N" || stop "fetching the deletion log from hpc1 failed: run delete again"
python3 "$B/verify_stage.py" postcheck "$S/$N" > "$S/post.txt" || { cat "$S/post.txt"; stop "the post-deletion check found a problem (above): tell Claude"; }
cat "$S/post.txt"
cp "$S/$N/DELETED.log" "$S/$N/REMAINING.tsv" "$A/$N/"
{ echo "# verify_stage.py postcheck, $(date '+%Y-%m-%dT%H:%M:%S%z'), on the fetched DELETED.log and REMAINING.tsv"; cat "$S/post.txt"; } > "$A/$N/POSTCHECK.txt"
git add "$A/$N"
[ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify a committed file: tell Claude"
git commit -q -m "SP runs' outputs kept as physical files, step 2 of 2 ($N, x77): deletion log, the files left in the four run folders and the post-deletion check - $(sed 's/^post-check: //' "$S/post.txt"); every deleted file is in the batch's PC archives, verified before the deletion [retained-final]" -m "$TRAILER"
git push -q || stop "push failed: run  git -C $RES push origin main ; then remove the stage (copies only) with  ssh $HPC \"rm -rf $STG/$N\""
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub after the push: run  git -C $RES push origin main"
echo "committed and pushed: results $(git log -1 --format=%h)"
case "$N" in
  batch_[0-9]*)
    if sshc -n "$HPC" "rm -rf $STG/$N"; then echo "removed the stage $STG/$N on hpc1 (copies only; its lists and logs are committed)"
    else echo "NOTE: removing the stage failed; it holds copies only, remove it by hand:  ssh $HPC \"rm -rf $STG/$N\""; fi ;;
esac
