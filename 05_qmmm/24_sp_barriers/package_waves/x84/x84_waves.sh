#!/usr/bin/env bash
# x84_waves.sh - RUN ON THE PC (not on hpc1), from anywhere:
#   bash x84/x84_waves.sh status    read-only: where the package stands on hpc1 and what the next wave would be
#   bash x84/x84_waves.sh submit    submits the next wave if it may go now; otherwise says why not and submits nothing
# The SP package's submission in waves (05_qmmm/24_sp_barriers/SP_AMENDMENT2.txt A2.10): "Before submission the bundle
# measures the free space and the quota on hpc1 and submits at most (the smaller of the two, less 20 GB) / 11 GB run
# folders at a time, in frame-number order, the next wave when a wave's alternation jobs have ended; the waves are
# reported." pkg_waves.py does the work on hpc1; its header gives the rules. For submit, this script:
#  0. checks: the bundle; the results repo clean, up to date, on main, with x83's inputs commit 6cd2d20 unchanged since;
#     each committed run folder's inputs match its committed GENERATOR_LOG.txt; on hpc1, SD's five scripts are the ones
#     SP_AMENDMENT2.txt lists and the force-field copy is the recorded one; every wave record on hpc1 is either committed
#     and identical or complete (it ends with END);
#  1. copies pkg_waves.py to SD/staging/x84_pkg_waves.py (sha256 checked; replaced on each run);
#  2. runs it there under nohup, so that a dropped connection cannot stop a wave part-way: it measures and checks
#     everything, and if the next wave may go now it checks each of its run folders against the sha256 of its committed
#     GENERATOR_LOG.txt, removes its DO_NOT_SUBMIT and runs its submit.sh, recording the wave in
#     SD/package_waves/wave_N.txt; if the wave may not go yet (an earlier wave's alternation jobs still running, no
#     room), it changes nothing and this script says why; anything that needs Claude is a STOP;
#  3. results repo: any wave record not yet committed into 05_qmmm/24_sp_barriers/package_waves/ (with this bundle's
#     scripts in package_waves/x84/ the first time) - one commit, additions only [retained-final]; pushed and checked.
# Nothing is deleted on hpc1 (apart from each submitted run folder's DO_NOT_SUBMIT marker) or in the repos.
# Safe to re-run: a wave that may not go yet is reported, not submitted.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
HPC="18660916@hpc"
SSHO="-o ServerAliveInterval=30 -o ServerAliveCountMax=10"
RH=/home/18660916/system_development
SD=$RH/05_qmmm/24_sp_barriers
T=05_qmmm/24_sp_barriers
C4=05_qmmm/23_c4_reactant
A2=SP_AMENDMENT2.txt
X83=6cd2d20
REC=$T/package_waves
MD_FRAMES="20000 21634 23268 24883 26495 33320 34991 36665 38344 40485 41786 43087 43738 44388 45688 46990 47641 48292 49592 50892 52192 53493 54144 54795 55446 56098 57397 58698 59999"
CI_FRAMES="20000 44388 59999"
CODEF="spa_prepare.py spa_stage.py spa_report.py spa_package.py spa_package_stats.py"
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
stop() { echo "STOP: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }
RUNS=""
for f in $MD_FRAMES; do RUNS="$RUNS f${f}_r8_a1"; done
for f in $CI_FRAMES; do RUNS="$RUNS f${f}_r8_ci_a1"; done
MODE=${1:-}
[ "$MODE" = status ] || [ "$MODE" = submit ] || stop "usage: bash x84/x84_waves.sh status | submit"
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT

( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
for t in git ssh scp sha256sum; do command -v "$t" > /dev/null || stop "$t is needed on the PC"; done
[ -d "$RES/.git" ] || stop "$RES is not a git repo"
PW=$(sha "$B/pkg_waves.py")
ssh "$HPC" "test -d $SD" || stop "cannot reach hpc1, or $SD is missing"

# the wave records on hpc1 against the results repo: each "committed" (identical), "new" (complete) or a stop
waves_hpc() {
  ssh "$HPC" "if [ -d $SD/package_waves ]; then cd $SD/package_waves && ls; fi" > "$S/wl.txt" || stop "cannot list $SD/package_waves on hpc1"
  : > "$S/new.txt"; : > "$S/committed.txt"
  while read -r w; do
    case "$w" in wave_[0-9]*.txt) ;; *) stop "$SD/package_waves holds an unexpected file $w: tell Claude";; esac
    ssh "$HPC" "cat $SD/package_waves/$w" > "$S/$w" || stop "cannot read $w on hpc1"
    if git -C "$RES" cat-file -e "HEAD:$REC/$w" 2> /dev/null; then
      git -C "$RES" show "HEAD:$REC/$w" | cmp -s - "$S/$w" || stop "$w on hpc1 differs from the committed record: tell Claude"
      echo "$w" >> "$S/committed.txt"
    else
      tail -1 "$S/$w" | grep -q '^END ' || stop "$w on hpc1 has no END line: its submission stopped part-way, or is still going. Wait a few minutes and run status; if this stays, tell Claude and run nothing else"
      echo "$w" >> "$S/new.txt"
    fi
  done < "$S/wl.txt"
}

if [ "$MODE" = status ]; then
  echo "status: asking hpc1 (measuring your home folder's usage can take several minutes) ..."
  ssh $SSHO "$HPC" "python3 -I -u - status" < "$B/pkg_waves.py" || stop "pkg_waves.py status failed on hpc1 (above): tell Claude"
  waves_hpc
  echo "wave records on hpc1: $(wc -l < "$S/committed.txt") in your results repo, $(wc -l < "$S/new.txt") not yet$(if [ -s "$S/new.txt" ]; then echo " ($(tr '\n' ' ' < "$S/new.txt" | sed 's/ $//'))"; fi)"
  echo "status only: nothing was changed on hpc1 or in the repos"
  exit 0
fi

# ---- 0. checks (submit)
[ -z "$(git -C "$RES" status --porcelain)" ] || stop "$RES has uncommitted changes"
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
git -C "$RES" pull --ff-only -q || stop "git pull failed in $RES"
git -C "$RES" merge-base --is-ancestor "$X83" HEAD 2> /dev/null || stop "x83's commit $X83 is not in the results repo"
git -C "$RES" diff --quiet "$X83" HEAD -- $(for r in $RUNS; do echo "$T/$r"; done) "$T/package_inputs_x83" \
  || stop "the committed package inputs changed after $X83: tell Claude"
ARGS=""
for r in $RUNS; do
  L="$RES/$T/$r/GENERATOR_LOG.txt"; [ -f "$L" ] || stop "$T/$r/GENERATOR_LOG.txt is not committed"
  [ "$(grep -c '^  [0-9a-f]\{64\}  ' "$L")" -eq 26 ] || stop "$T/$r/GENERATOR_LOG.txt does not record 26 files"
  ( cd "$RES/$T/$r" && grep '^  [0-9a-f]\{64\}  ' GENERATOR_LOG.txt | grep -v -e ' ts/start.xyz$' -e ' r0/start.xyz$' | sed 's/^  //' | sha256sum -c --quiet ) \
    || stop "$T/$r: a committed input differs from its GENERATOR_LOG record: tell Claude"
  ARGS="$ARGS $r=$(sha "$L")"
done
for f in $CODEF; do
  w=$(awk -v f="$f" '$1 == "sha256" && $2 == f {print $3}' "$RES/$T/$A2"); [ ${#w} -eq 64 ] || stop "$A2 lists no sha256 for $f"
  [ "$(ssh "$HPC" "sha256sum < $SD/$f" | cut -c1-64)" = "$w" ] || stop "$SD/$f is not the version $A2 lists: tell Claude"
done
P41=$(awk '$2 == "05_qmmm/19_ensemble/frame_41786/complex_solvated.ORCAFF.prms" {print $1}' "$RES/$C4/c4_sources.sha256")
[ ${#P41} -eq 64 ] && [ "$(ssh "$HPC" "sha256sum < $SD/complex_solvated.ORCAFF.prms" | cut -c1-64)" = "$P41" ] \
  || stop "the force-field copy in $SD is not the recorded file: tell Claude"
if [ -e "$RES/$REC/x84" ]; then
  for f in x84_waves.sh pkg_waves.py MANIFEST.sha256; do cmp -s "$B/$f" "$RES/$REC/x84/$f" || stop "$REC/x84/$f differs from this bundle's: tell Claude"; done
fi
waves_hpc
echo "0. bundle intact; results repo clean and up to date; the 32 run folders' committed inputs match their logs; SD's scripts and force field are the recorded ones; wave records on hpc1: $(wc -l < "$S/committed.txt") committed, $(wc -l < "$S/new.txt") to commit"

# ---- commit the complete wave records not yet committed (and this bundle's scripts the first time); push; check
commit_waves() {   # $1: when the records were committed, for the message
  cd "$RES"
  if [ -s "$S/new.txt" ]; then
    mkdir -p "$REC"
    while read -r w; do [ ! -e "$REC/$w" ] || stop "$REC/$w exists but is not committed: tell Claude"; cp "$S/$w" "$REC/$w"; git add "$REC/$w"; done < "$S/new.txt"
    if [ ! -e "$REC/x84" ]; then
      mkdir "$REC/x84"; cp "$B/x84_waves.sh" "$B/pkg_waves.py" "$B/MANIFEST.sha256" "$REC/x84/"; git add "$REC/x84"
    fi
    [ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify or delete a committed file: tell Claude"
    local nf ws summ
    nf=$(git diff --cached --name-only | wc -l)
    ws=$(sed 's/^wave_//; s/\.txt$//' "$S/new.txt" | tr '\n' ' ' | sed 's/ $//; s/ /, /g')
    summ=$(while read -r w; do echo "wave ${w//[!0-9]/}: $(grep -c '^RUN ' "$S/$w") run folder(s), $(sed -n 's/^size: //p' "$S/$w" | sed 's/; run folders left.*//')"; done < "$S/new.txt" | tr '\n' ';' | sed 's/;$//; s/;/; /g')
    git commit -q -m "SP package: record of wave(s) $ws as submitted on hpc1 (SP_AMENDMENT2.txt A2.10): $summ. Each record gives the free disk and the quota left as measured where SD is (quota tool, and the documented 1 TB quota less the home folder's usage), the wave's size, each run folder's inputs checked against its committed GENERATOR_LOG.txt, and the job ids from its submit.sh; $1 [retained-final]" -m "$TRAILER" \
      || stop "git commit failed (above); nothing was committed. To clear the copies:  git -C $RES reset -q && git -C $RES clean -fdq -- $REC"
    echo "3. committed: $(git log -1 --format=%h) ($nf files, additions only)"
  fi
  if git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ]; then return 0; fi
  git push -q || stop "push failed: run  git -C $RES push origin main"
  git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub: run  git -C $RES push origin main"
  echo "   pushed: results $(git log -1 --format=%h), in step with GitHub"
}

# ---- 1. the script onto hpc1
ssh "$HPC" "mkdir -p $SD/staging" || stop "cannot make $SD/staging"
scp -q "$B/pkg_waves.py" "$HPC:$SD/staging/x84_pkg_waves.py.part" || stop "copying pkg_waves.py to hpc1 failed (run this again)"
[ "$(ssh "$HPC" "sha256sum < $SD/staging/x84_pkg_waves.py.part" | cut -c1-64)" = "$PW" ] || stop "pkg_waves.py arrived on hpc1 damaged (run this again)"
ssh "$HPC" "mv $SD/staging/x84_pkg_waves.py.part $SD/staging/x84_pkg_waves.py" || stop "could not put pkg_waves.py in place on hpc1"
LOG=$SD/staging/x84_submit_$(date +%Y%m%d_%H%M%S).log
echo "1. pkg_waves.py is on hpc1; its run is logged in $LOG"

# ---- 2. measure, decide and (if it may) submit, on hpc1 under nohup
echo "2. measuring on hpc1 and submitting the next wave if it may go now (measuring your home folder's usage can take several minutes) ..."
set +e
ssh $SSHO "$HPC" "cd $SD && nohup python3 -I -u staging/x84_pkg_waves.py submit $PW $ARGS > $LOG 2>&1 < /dev/null; echo \"PKG_EXIT=\$?\" >> $LOG"
rc_ssh=$?
set -e
if ! ssh "$HPC" "cat $LOG" > "$S/submit.log"; then
  stop "could not read $LOG on hpc1 (ssh exit $rc_ssh, then the read failed). If the connection dropped during the submission, it carries on there. When hpc1 can be reached, run  bash x84/x84_waves.sh status  and send it to Claude"
fi
grep -v -e '^PKG_EXIT=' -e '^measuring the usage' "$S/submit.log" || true
ex=$(sed -n 's/^PKG_EXIT=//p' "$S/submit.log")
[ -n "$ex" ] || stop "the run on hpc1 has not reported its end (ssh exit $rc_ssh): if the connection dropped, it carries on there. In a few minutes run  bash x84/x84_waves.sh status  and send it to Claude"
if [ "$ex" = 3 ]; then
  echo "2. the next wave may not go yet: $(sed -n 's/^NEXT_WAVE: no - //p' "$S/submit.log"). Nothing was submitted"
  commit_waves "recorded by a later x84 run"
  exit 0
fi
if [ "$ex" != 0 ]; then
  saved="on hpc1 ($LOG)"
  if mkdir -p "$HOME/Downloads" 2> /dev/null && cp "$S/submit.log" "$HOME/Downloads/x84_submit.log" 2> /dev/null; then saved="$saved and in ~/Downloads/x84_submit.log"; fi
  stop "pkg_waves.py stopped on hpc1 (exit $ex; the reason is above, and the log is $saved). Nothing was committed: tell Claude"
fi
grep -q '^WAVE [0-9]* SUBMITTED: ' "$S/submit.log" || stop "pkg_waves.py ended without reporting a submitted wave: tell Claude"

# ---- 3. commit the wave record
waves_hpc
[ -s "$S/new.txt" ] || stop "no new wave record on hpc1 after the submission: tell Claude"
commit_waves "committed right after the submission by x84"
echo "   $(sed -n 's/^WAVE \([0-9]*\) SUBMITTED: \([0-9]*\) .*/wave \1 (\2 run folders)/p' "$S/submit.log") is in PBS's queue on hpc1. Check on it with  bash x84/x84_waves.sh status ; a next wave, if any run folders are left, goes once this wave's alternation jobs have ended"
