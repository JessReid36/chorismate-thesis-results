#!/usr/bin/env bash
# y02_transfer.sh - RUN ON THE PC (not on hpc1), from anywhere:   bash y02/y02_transfer.sh
#
# Stage 6 DIAGNOSTIC 7 (STAGE6_DIAGNOSTIC7_20261026.txt): generates the 24 single points of the transfer test and
# puts them on hpc1. S6-10 scaled over six lambda, at def2-SVP and def2-SVPD, so that the lambda <= 0.50 domain
# measured on S6-20 can be tested on a second design at the SAME total field.
#
#  0. checks: the bundle against its own manifest; git, python3, ssh, scp, tar, awk on the PC; both repos clean, on
#     their branches, level with origin; the eight committed files this step reads are byte for byte what the
#     pre-registration records, STAGE6_CRITERIA.txt and STAGE6_DIAGNOSTIC7_20261026.txt among them; cs6_field.py
#     UNCHANGED (it is the generator of record for D4 and this step must not touch it); nothing of this step
#     already present in either repo or on hpc1; hpc1 reachable;
#  1. commits cs6_transfer.py to the code repo and pushes it, BEFORE it is run (and it must be run from there, so
#     that its "import cs6_audit" resolves against the committed D6 classifier);
#  2. runs cs6_transfer.py prepare into a scratch folder on the PC. It submits nothing;
#  3. proves the generated inputs are what D7.2 fixed: 24 runs over the six lambda with the sum |q|, sum q^2 and
#     largest |q| the pre-registration prints, every job.inp byte for byte the committed D4 header for its basis,
#     every substrate.xyz byte for byte the committed geometry, and the generated manifest self-consistent;
#  4. copies the scratch folder into the results repo, commits and pushes it;
#  5. uploads it to hpc1 and verifies every file there against the same manifest;
#  6. writes the record, commits and pushes it, and PRINTS THE qsub LINE. IT DOES NOT SUBMIT.
#
# NOTHING IS SUBMITTED AND NOTHING EXISTING IS CHANGED. Every file this step writes is new: the commits are checked
# to be additions only, and the bundle stops if any path it would write already exists. cs6_field.py, the Stage 6
# criteria, the diagnostics and their results are read and never written. No barrier and no result is read.
# Safe to re-run: it refuses once any part of the step exists, rather than writing over it.
# If it stops, nothing after the stop has happened; send Claude the whole output.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
CODE="$HOME/Desktop/chorismate-thesis-code"
HPC="18660916@hpc"
RH=/home/18660916/system_development
T=phase2.2/cs_stage6
OUT=transfer
PRE=STAGE6_DIAGNOSTIC7_20261026.txt
DESIGN=S6-10
NSPH=10
NRUNS=24
NFILES=75
TRAILER="Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SiJLyw8h7oJEbw5UekYZZP"
stop() { echo "STOP: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }
S=$(mktemp -d)
# Nothing after a stop may have happened, so anything copied into a repo but not committed is taken back out.
# Without this, a failed commit would leave the file behind and the NEXT run would refuse with "already exists:
# this bundle has run", which would be false and would leave no way forward.
undo() {
  local st=$?
  rm -rf "$S"
  # ls-tree asks the COMMIT, not the index: git add may already have staged the file, so ls-files would call an
  # uncommitted file tracked and leave it behind - which is the very thing this is here to prevent.
  if [ -e "$CODE/phase2.2/cs6_transfer.py" ] \
     && [ -z "$(git -C "$CODE" ls-tree HEAD -- phase2.2/cs6_transfer.py 2>/dev/null)" ]; then
    git -C "$CODE" reset -q -- phase2.2/cs6_transfer.py 2>/dev/null || true
    rm -f "$CODE/phase2.2/cs6_transfer.py"
    echo "NOTE: took phase2.2/cs6_transfer.py back out of the code repo - it was copied in but not committed" >&2
  fi
  if [ -e "$RES/$T/$OUT" ] \
     && [ -z "$(git -C "$RES" ls-tree -d HEAD -- "$T/$OUT" 2>/dev/null)" ]; then
    git -C "$RES" reset -q -- "$T/$OUT" 2>/dev/null || true
    rm -rf "$RES/$T/$OUT"
    echo "NOTE: took $T/$OUT back out of the results repo - it was copied in but not committed" >&2
  fi
  exit $st
}
trap undo EXIT

# commit_push REPO BRANCH MESSAGE_FILE LABEL PATH...
# Every command is in one && chain, so the subshell's status IS the first failure's. That matters: a subshell on
# the left of || has errexit suppressed, so a bare sequence of commands in one would let a FAILED git commit pass
# as success - the bundle would upload to hpc1 and report DONE with nothing committed. Then, because an exit
# status is not evidence, the commit is confirmed by HEAD having moved and the push by being level with origin.
commit_push() {
  local r=$1 br=$2 msg=$3 label=$4; shift 4
  local before
  before=$(git -C "$r" rev-parse HEAD) || stop "$label: cannot read HEAD of $r"
  ( cd "$r" \
    && git add -- "$@" \
    && [ -z "$(git diff --cached --name-status | grep -v '^A')" ] \
    && git commit -q -F "$msg" \
    && git push -q origin "$br" ) \
    || stop "$label: the commit or push failed (the git error is above). Nothing after this point has happened"
  [ "$(git -C "$r" rev-parse HEAD)" != "$before" ] \
    || stop "$label: the commit did not happen - HEAD is still $before"
  git -C "$r" fetch -q origin "$br" || stop "$label: cannot reach origin to confirm the push landed"
  [ "$(git -C "$r" rev-parse HEAD)" = "$(git -C "$r" rev-parse "origin/$br")" ] \
    || stop "$label: the push did not land; $r is not level with origin/$br"
  if [ -n "$(git -C "$r" status --porcelain)" ]; then stop "$label: $r is dirty after the commit"; fi
}

echo "== 0. checks"
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
for t in python3 git ssh scp tar awk sha256sum; do command -v "$t" > /dev/null || stop "$t is needed on the PC"; done
for r in "$RES" "$CODE"; do
  [ -d "$r/.git" ] || stop "$r is not a git repo"
  [ -z "$(git -C "$r" status --porcelain)" ] || stop "$r has uncommitted changes: commit or stash them first"
done
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ "$(git -C "$CODE" rev-parse --abbrev-ref HEAD)" = tier1-realism ] || stop "the code repo is not on tier1-realism"
for r in "$RES" "$CODE"; do
  br=$(git -C "$r" rev-parse --abbrev-ref HEAD)
  git -C "$r" fetch -q origin "$br" || stop "cannot reach origin for $r"
  [ "$(git -C "$r" rev-parse HEAD)" = "$(git -C "$r" rev-parse "origin/$br")" ] \
    || stop "$r is not level with origin/$br: pull or push first"
done
# every committed file this step reads must be byte for byte what the pre-registration records
while read -r nm want; do
  [ -n "${want:-}" ] || continue
  got=$(sha "$RES/$T/$nm") || stop "$nm is missing from the results repo"
  [ "$got" = "$want" ] || stop "$T/$nm is not the file $PRE records ($got, expected $want)"
done << 'EOS'
STAGE6_CRITERIA.txt                     010d1d83d33c3ff28fcb11a2e05e337fbaa7df0fa51fd38c56973b5b2c93155e
STAGE6_DIAGNOSTIC7_20261026.txt         26357d1e4382df2204c892f7b9f3ca9aab1927760c788facfb9fc49e9ab98951
relax/ARRANGEMENTS.txt                  651e7e228e1409f052bb024b42d125ab59bc86ebee789f3dd60ad1eb5f9c6038
frozen/frozen.tsv                       ab48d52267a5e8c8de813a79acec0f8dceee0fde2e0aa32acb45ccbc465b7b5a
sites_f42436.tsv                        d2a750077d79e34dfecf448c30c2899ae0cea98f1edc5de3d10361b7c357cfc7
L_f42436.tsv                            ee6d57622619f0c3dccb105a36004c733c781fd67b565660b8bec2663f16ec2a
A_f42436.tsv                            a7faa6c5cacc2f2ee0956f80a1a6645eed1e04cc126830d5f5803d9762eae553
frame_42436/reactant_qm.xyz             6e8f41c7da3bcf4ed9f5c650dc9fcf12c2a36e5af7a900e164892c276497aa88
frame_42436/transition_state_qm.xyz     2babeb9000ca5220a908a70eaec80ec4a64358c8f5677e9a16cb104e0dffc5bf
frame_42436/transform.txt               a57991bd6c5827cf7eab7c0b932b136d94a065953278b53d6b6cd0d63df2ea4c
EOS
echo "   the 10 committed files this step reads are what $PRE records"
PREC=$(git -C "$RES" log -1 --format=%h -- "$T/$PRE") || stop "cannot find the commit that added $PRE"
[ -n "$PREC" ] || stop "$T/$PRE is not committed; a pre-registration is committed before its bundle runs"
# cs6_audit.py is used unchanged; cs6_field.py must not have been touched
AUD=19f63857536fb66645d8f31d286c21404159d672a4fa73a94c7b2ac8e90cfa7b
FLD=7695ec2e17e23833975a54b51ddd8e013fcc443f22b277bfb2a8d49687e2ebeb
NEW=c4388c44b823095f52d7309cc02120cefa528264d9800f15162dc4a60fe14d18
[ "$(sha "$CODE/phase2.2/cs6_audit.py")" = "$AUD" ] \
  || stop "the code repo's cs6_audit.py is not the committed D6 classifier $PRE records; reading 4 would not be D6's rule"
[ "$(sha "$CODE/phase2.2/cs6_field.py")" = "$FLD" ] \
  || stop "the code repo's cs6_field.py has changed. It is the generator of record for Diagnostic 4 and this step must not touch it"
[ "$(sha "$B/code/cs6_transfer.py")" = "$NEW" ] || stop "internal: the bundle's cs6_transfer.py is not the recorded one"
python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$B/code/cs6_transfer.py" \
  || stop "the bundle's cs6_transfer.py does not parse"
echo "   cs6_audit.py is the committed classifier; cs6_field.py is untouched; the new generator parses"
# nothing of this step may exist yet
if [ -e "$CODE/phase2.2/cs6_transfer.py" ]; then stop "$CODE/phase2.2/cs6_transfer.py already exists: this bundle has run"; fi
if [ -e "$RES/$T/$OUT" ]; then stop "$RES/$T/$OUT already exists: this bundle has run"; fi
ssh "$HPC" "test -d $RH/$T" || stop "cannot reach hpc1, or $RH/$T is not there"
if ssh "$HPC" "test -e $RH/$T/$OUT"; then stop "$RH/$T/$OUT already exists on hpc1: this bundle has run, or something else is there"; fi
echo "   nothing of this step exists in either repo or on hpc1; hpc1 is reachable"

echo "== 1. commit the generator BEFORE it is run"
cp "$B/code/cs6_transfer.py" "$CODE/phase2.2/cs6_transfer.py"
cat > "$S/msg_code.txt" << EOF
phase2.2/cs6_transfer.py: the generator and reader for Stage 6 DIAGNOSTIC 7, the transfer test ($T/$PRE, results $PREC). It scales a SECOND committed design over six lambda - D4's four plus two defined by matching S6-20's committed total fields of 1.440 and 2.880 e, computed from the committed ARRANGEMENTS.txt and not typed - so that the lambda <= 0.50 domain E3.3 measured on S6-20 can be tested on another arrangement at the same total field rather than at the same fraction. cs6_field.py is NOT modified and NOT imported: it is the generator of record for Diagnostic 4 and its result bundle checks it byte for byte. Nothing design-specific is typed here either: the committed score, sum q^2, sum L and the sites come out of ARRANGEMENTS.txt, the consistency target out of frozen/frozen.tsv at full precision, b out of DIAGNOSTIC2_AMENDMENT1_RESULT.txt, S6-20's Delta out of DIAGNOSTIC4_RESULT.txt and D6's control medians out of DIAGNOSTIC6_RESULT.txt. The per-site check does NOT use the 0.80 e cap, which E3.1 withdrew; it is E3.1's 0.65 e CLEAN observation, and it refuses any of the four 1.0000 e designs, which is intended. Every run is classified by DIAGNOSTIC 6's rule, which D4 could not do: cs6_audit.read() and all five of its thresholds are imported, never retyped, and its verdict() is a closure that cannot be imported so its five comparisons are transcribed structurally against the control medians the committed DIAGNOSTIC6_RESULT.txt publishes. Rehearsed before this commit: a clean run whose generated job.inp and substrate.xyz are byte for byte the committed D4 ones, ten negative tests against a mirror clone with every stop fired, and a final clean run byte-identical to the first with the mirror verified untouched. Its one() and its four readings need real ORCA outputs and are not rehearsed [retained-final]

$TRAILER
EOF
commit_push "$CODE" tier1-realism "$S/msg_code.txt" "the generator" phase2.2/cs6_transfer.py
CODEC=$(git -C "$CODE" rev-parse --short HEAD)
echo "   code tier1-realism $CODEC"

echo "== 2. generate into a scratch folder (nothing is submitted)"
python3 "$CODE/phase2.2/cs6_transfer.py" prepare "$RES" "$DESIGN" "$NSPH" "$S/$OUT" "$RH/$T/$OUT" \
  || stop "cs6_transfer.py prepare stopped (above); nothing has been written to either repo or to hpc1"

echo "== 3. prove the inputs are what D7.2 fixed"
n=$(awk 'NR>5 && NF' "$S/$OUT/TRANSFER_PLAN.tsv" | wc -l | tr -d ' ')
[ "$n" = "$NRUNS" ] || stop "the plan lists $n runs, expected $NRUNS"
f=$(find "$S/$OUT" -type f | wc -l | tr -d ' ')
[ "$f" = "$NFILES" ] || stop "$f files were generated, expected $NFILES"
( cd "$S/$OUT" && sha256sum -c --quiet INPUT_CHECKSUMS.sha256 ) \
  || stop "the generated INPUT_CHECKSUMS.sha256 does not match the files beside it"
# the six lambda and their three quantities, as the pre-registration prints them
while read -r lam sq sq2 mq; do
  [ -n "${mq:-}" ] || continue
  got=$(awk -F'\t' -v L="$lam" '$3==L && $2=="def2-SVP" && $4=="R" {print $5"|"$6"|"$7}' "$S/$OUT/TRANSFER_PLAN.tsv")
  [ "$got" = "$sq|$sq2|$mq" ] || stop "lambda $lam: the plan gives $got, $PRE gives $sq|$sq2|$mq"
done << 'EOS'
0.250000 1.0950 0.12646 0.1375
0.328767 1.4400 0.21870 0.1808
0.500000 2.1900 0.50585 0.2750
0.657534 2.8800 0.87482 0.3616
0.750000 3.2850 1.13816 0.4125
1.000000 4.3800 2.02340 0.5500
EOS
echo "   24 runs over the six lambda, every sum |q|, sum q^2 and largest |q| as $PRE prints them"
# every job.inp is the committed D4 header for its basis; every substrate.xyz the committed geometry
for b in def2-SVP def2-SVPD; do
  for d in "$S/$OUT/$b"/*; do
    cmp -s "$d/job.inp" "$RES/$T/field/$b/lam050_R/job.inp" \
      || stop "$(basename "$d"): job.inp is not the committed D4 $b header byte for byte"
    case "$(basename "$d")" in
      *_R)  g=reactant_qm.xyz ;;
      *_TS) g=transition_state_qm.xyz ;;
      *)    stop "unexpected run folder $(basename "$d")" ;;
    esac
    cmp -s "$d/substrate.xyz" "$RES/$T/frame_42436/$g" \
      || stop "$(basename "$d"): substrate.xyz is not the committed $g byte for byte"
    [ "$(head -1 "$d/pc.pc")" = "$NSPH" ] || stop "$(basename "$d"): pc.pc does not declare $NSPH charges"
  done
done
echo "   every job.inp is the committed D4 header for its basis; every substrate.xyz the committed geometry"

echo "== 4. commit the inputs"
cp -R "$S/$OUT" "$RES/$T/$OUT"
cat > "$S/msg_inputs.txt" << EOF
$T/$OUT/: the $NRUNS inputs of Stage 6 DIAGNOSTIC 7, generated by cs6_transfer.py prepare (code tier1-realism $CODEC) and committed before any job is submitted, as $PRE and STAGE6_CRITERIA.txt require of a generator and its inputs. $DESIGN scaled over six lambda at def2-SVP and def2-SVPD, both states: D4's 0.25, 0.50, 0.75 and 1.00, plus lamM1 and lamM2 at 24/73 and 48/73, which put this design at sum |q| 1.4400 and 2.8800 e - S6-20's own committed total fields at its lambda 0.25 and 0.50, computed from ARRANGEMENTS.txt rather than typed. Checked before this commit: the generated manifest against the files beside it; all six lambda's sum |q|, sum q^2 and largest |q| against the figures $PRE prints; every job.inp byte for byte the committed D4 header for its basis; every substrate.xyz byte for byte the committed frame_42436 geometry; every pc.pc declaring $NSPH charges. The largest single charge is 0.5500 e at lambda 1, below the +0.65 e E3.1 records as the largest CLEAN single magnitude at def2-SVPD; the withdrawn 0.80 e cap is not used anywhere. Nothing is submitted by this bundle and no result is read [retained-final]

$TRAILER
EOF
commit_push "$RES" main "$S/msg_inputs.txt" "the inputs" "$T/$OUT"
INPC=$(git -C "$RES" rev-parse --short HEAD)
echo "   results main $INPC"

echo "== 5. upload to hpc1 and verify there"
scp -q -r "$S/$OUT" "$HPC:$RH/$T/" || stop "the upload failed; $RH/$T/$OUT on hpc1 may be incomplete - check it before re-running"
out=$(ssh "$HPC" "cd $RH/$T/$OUT && sha256sum -c --quiet INPUT_CHECKSUMS.sha256 && echo VERIFIED && find . -type f | wc -l") \
  || stop "the files on hpc1 do not match the manifest; send Claude this output"
case "$out" in *VERIFIED*) ;; *) stop "hpc1 did not verify the manifest: $out" ;; esac
nf=$(printf '%s\n' "$out" | tail -1 | tr -d ' ')
[ "$nf" = "$NFILES" ] || stop "hpc1 holds $nf files, expected $NFILES"
echo "   all $NFILES files on hpc1 match the manifest"

echo "== 6. the record"
{ echo "y02_transfer.sh, Stage 6 DIAGNOSTIC 7 inputs generated $(date -u +%Y-%m-%dT%H:%MZ) from this PC"
  echo "pre-registration: $T/$PRE (results $PREC)"
  echo "generator: code tier1-realism $CODEC, cs6_transfer.py sha256 $NEW"
  echo "classifier used unchanged for reading 4: cs6_audit.py sha256 $AUD"
  echo "cs6_field.py NOT used and NOT modified, verified at sha256 $FLD"
  echo
  echo "design $DESIGN from relax/ARRANGEMENTS.txt; the matched lambda target S6-20's committed total fields."
  echo
  sed -n '1,4p' "$RES/$T/$OUT/TRANSFER_PLAN.tsv"
  echo
  echo "the six lambda, as $PRE prints them and as the plan reproduces them:"
  awk -F'\t' '$2=="def2-SVP" && $4=="R" {printf "   lambda %-9s sum |q| %-7s sum q^2 %-8s largest |q| %s\n", $3, $5, $6, $7}' \
    "$RES/$T/$OUT/TRANSFER_PLAN.tsv"
  echo
  echo "$NRUNS runs, $NFILES files, one restartable PBS job. NOTHING WAS SUBMITTED BY THIS BUNDLE."
  echo "Every job.inp is byte for byte the committed D4 header for its basis and every substrate.xyz is byte for"
  echo "byte the committed frame_42436 geometry; the generated manifest was verified on the PC and again on hpc1."
  echo "No barrier and no result was read."
} > "$RES/$T/$OUT/Y02_RECORD.txt"
cp "$B/y02_transfer.sh" "$RES/$T/$OUT/y02_transfer.sh"
cat > "$S/msg_record.txt" << EOF
$T/$OUT/Y02_RECORD.txt: what y02_transfer.sh did, with the bundle itself beside it. The $NRUNS DIAGNOSTIC 7 inputs were generated on the PC from the committed repo, checked against the figures $PRE prints, committed (results $INPC), uploaded to hpc1 and verified there against the same manifest. The generator was committed first (code tier1-realism $CODEC), which is what STAGE6_CRITERIA.txt requires and also what makes its "import cs6_audit" resolve against the committed D6 classifier. NOTHING WAS SUBMITTED: $PRE D7.2 has prepare submit nothing, so the qsub line is printed for Jessica to run when she chooses. The job is 8 cores and 24 GB, which is what STAGE6_CRITERIA.txt's "WHEN IT RUNS" sizes Stage 6 work at so it does not compete with the SP package's 16-core, 64-250 GB jobs [retained-final]

$TRAILER
EOF
commit_push "$RES" main "$S/msg_record.txt" "the record" "$T/$OUT/Y02_RECORD.txt" "$T/$OUT/y02_transfer.sh"
RECC=$(git -C "$RES" rev-parse --short HEAD)

echo
echo "DONE: code $CODEC, inputs results $INPC, record results $RECC."
echo "      $NRUNS single points are on hpc1 at $RH/$T/$OUT and verified. NOTHING IS SUBMITTED."
echo
echo "To submit, on hpc1:"
echo "    ssh $HPC"
echo "    cd $RH/$T/$OUT && qsub transfer.pbs"
echo
echo "Then send Claude that job id and 'qstat -u 18660916'. The job is restartable: if it is killed, resubmitting"
echo "it skips every single point that already terminated normally."
