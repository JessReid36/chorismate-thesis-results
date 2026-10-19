#!/usr/bin/env bash
# x83_package_inputs.sh - RUN ON THE PC (not on hpc1), from anywhere:  bash x83/x83_package_inputs.sh
# The SP package's inputs (05_qmmm/24_sp_barriers/SP_AMENDMENT2.txt A2.10), generated and committed before any package
# job is submitted. In this order, each step only after the last:
#  0. checks: the bundle; both repos clean, up to date and on their branches; SP_AMENDMENT2.txt and its five code files
#     committed with the sha256 the amendment lists; C4 closed (C4_FINAL.txt);
#  1. hpc1, 05_qmmm/24_sp_barriers (SD): no job of yours running from SD; SD's Amendment 1 scripts (spa_prepare.py,
#     spa_stage.py, spa_report.py) moved into SD/superseded_a1/ (kept, not deleted) and replaced by Amendment 2's, and
#     spa_package.py and spa_package_stats.py added - each checked against the sha256 SP_AMENDMENT2.txt lists;
#  2. hpc1: every source's sha256, taken from the repos' records, written to SD/staging/expected_package.sha256; the
#     generator writes the 32 run folders (the 29 frames other than 42436 with S = md, f<FRAME>_r8_a1; frames 20000,
#     44388 and 59999 with S = ci, f<FRAME>_r8_ci_a1); a second generation into a scratch folder must reproduce every
#     file and link byte for byte; each run folder then gets DO_NOT_SUBMIT (its submit.sh refuses to run), because
#     A2.10 submits in waves sized to the disk, which the next bundle does;
#  3. results repo: the inputs of the 32 run folders (every generated file but the 64 full-system start files, whose
#     sha256 are in each GENERATOR_LOG.txt and checked on hpc1), the expected sha256 list and this bundle's scripts in
#     package_inputs_x83/ - one commit, additions only [retained-final]; pushed and checked.
# Nothing is submitted, nothing of the smoke tests or of C4 is touched, and nothing is deleted on hpc1 (apart from this
# bundle's own scratch copy of the second generation) or in the repos.
# Safe to re-run: a finished step is checked and skipped; anything unexpected stops it.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
CODE="$HOME/Desktop/chorismate-thesis-code"
HPC="18660916@hpc"
RH=/home/18660916/system_development
SD=$RH/05_qmmm/24_sp_barriers
T=05_qmmm/24_sp_barriers
C4=05_qmmm/23_c4_reactant
A2=SP_AMENDMENT2.txt
REC=package_inputs_x83
CHANGED="spa_prepare.py spa_stage.py spa_report.py"
NEW="spa_package.py spa_package_stats.py"
MD_FRAMES="20000 21634 23268 24883 26495 33320 34991 36665 38344 40485 41786 43087 43738 44388 45688 46990 47641 48292 49592 50892 52192 53493 54144 54795 55446 56098 57397 58698 59999"
CI_FRAMES="20000 44388 59999"
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
stop() { echo "STOP: $*" >&2; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }
listed() { grep -q "^  sha256 $1 *$2\$" "$RES/$T/$A2"; }       # name as SP_AMENDMENT2.txt writes it, sha256
S=$(mktemp -d); RG=""
trap 'rm -rf "$S"; if [ -n "$RG" ]; then ssh "$HPC" "rm -rf $RG" || echo "NOTE: remove the scratch copy $RG on hpc1 by hand" >&2; fi' EXIT
SPECS=""; RUNS=""
for f in $MD_FRAMES; do SPECS="$SPECS $f:8:md"; RUNS="$RUNS f${f}_r8_a1"; done
for f in $CI_FRAMES; do SPECS="$SPECS $f:8:ci"; RUNS="$RUNS f${f}_r8_ci_a1"; done
NR=$(echo $RUNS | wc -w)

# ---- 0. the bundle, the repos, the amendment and its code
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
for t in python3 git ssh scp tar; do command -v "$t" > /dev/null || stop "$t is needed on the PC"; done
for r in "$RES" "$CODE"; do
  [ -d "$r/.git" ] || stop "$r is not a git repo"
  [ -z "$(git -C "$r" status --porcelain)" ] || stop "$r has uncommitted changes"
done
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ "$(git -C "$CODE" rev-parse --abbrev-ref HEAD)" = tier1-realism ] || stop "the code repo is not on tier1-realism"
for r in "$RES" "$CODE"; do git -C "$r" pull --ff-only -q || stop "git pull failed in $r"; done
[ "$(sha "$RES/$T/$A2")" = 180a280a9f9193a7322e233941661bde79277e5008ffcb1e2fdf8dba948f459f ] || stop "$T/$A2 is not the committed amendment: tell Claude"
for f in $CHANGED $NEW; do listed "$f" "$(sha "$CODE/phase1_system_dev/$f")" || stop "phase1_system_dev/$f is not the version $A2 lists: tell Claude"; done
listed "23_c4_reactant/c4_bands.tsv" "$(sha "$RES/$C4/c4_bands.tsv")" || stop "$C4/c4_bands.tsv is not the file $A2 names"
[ -e "$RES/$C4/C4_FINAL.txt" ] || stop "C4 is not closed yet ($C4/C4_FINAL.txt missing): run x82 first"
frames=$(awk -F'\t' '!/^#/ && $1 ~ /^[0-9]+$/ {print $1}' "$RES/$C4/c4_bands.tsv" | grep -v -x 42436 | sort | tr '\n' ' ' | sed 's/ $//')
[ "$frames" = "$MD_FRAMES" ] || stop "the frames of c4_bands.tsv other than 42436 are not the 29 this bundle generates: tell Claude"
( cd "$CODE/phase1_system_dev" && python3 -I -B spa_package.py selftest > /dev/null ) || stop "spa_package.py's statistics self-test failed on this PC: tell Claude"
echo "0. bundle intact; both repos clean and up to date; $A2 and its five code files are the committed ones; C4 closed; $NR run folders to generate"

# ---- 1. hpc1: nothing running from SD; the code
ssh "$HPC" "test -d $SD/staging && test -e $SD/complex_solvated.ORCAFF.prms" || stop "cannot reach hpc1, or $SD is not as the smoke tests left it"
# each of your jobs in the queue: its job_state and whether its output path or working directory is in SD (PBS wraps long
# values onto lines that start with a tab; they are joined first). A qselect or qstat failure stops: a job is never
# taken as ended because PBS could not be asked.
jobs=$(ssh "$HPC" 'bash -s' << 'EOS'
ids=$(qselect -u 18660916) || { echo "QSELECT_FAILED"; exit 0; }
for id in $ids; do
  o=$(qstat -f "$id" 2>&1) || { echo "$o" | grep -qE "Unknown Job Id|Job has finished" && continue; echo "QSTAT_FAILED $id"; continue; }
  j=$(printf '%s\n' "$o" | awk '/^\t/ {sub(/^\t/, ""); printf "%s", $0; next} NR > 1 {print ""} {printf "%s", $0} END {print ""}')
  st=$(printf '%s\n' "$j" | sed -n 's/^ *job_state = //p')
  [ -n "$st" ] || { echo "QSTAT_FAILED $id (no job_state)"; continue; }
  [ "$st" = F ] && continue
  printf '%s\n' "$j" | grep -E '^ *(Output_Path|Variable_List) = ' | grep -q '05_qmmm/24_sp_barriers' && echo "IN_SD $id $st"
done
echo "CHECKED"
EOS
) || stop "cannot ask PBS on hpc1 which jobs are queued"
echo "$jobs" | grep -q '^CHECKED$' || stop "the job check on hpc1 did not finish: $jobs"
echo "$jobs" | grep -q -E '^(QSELECT_FAILED|QSTAT_FAILED)' && stop "PBS could not be asked about your jobs ($(echo "$jobs" | grep -E '^Q' | head -2 | tr '\n' ' ')): try again later"
echo "$jobs" | grep -q '^IN_SD ' && stop "a job of yours is queued or running from $SD ($(echo "$jobs" | grep '^IN_SD ' | cut -d' ' -f2- | tr '\n' ' ')): wait for it to end"
P41=$(awk '$2 == "05_qmmm/19_ensemble/frame_41786/complex_solvated.ORCAFF.prms" {print $1}' "$RES/$C4/c4_sources.sha256")
[ ${#P41} -eq 64 ] || stop "no recorded sha256 for the force field in c4_sources.sha256"
[ "$(ssh "$HPC" "sha256sum < $SD/complex_solvated.ORCAFF.prms" | cut -c1-64)" = "$P41" ] || stop "the force-field copy in $SD is not the recorded file"
a1() { git -C "$CODE" show "1bca074:phase1_system_dev/$1" 2> /dev/null | sha256sum | cut -c1-64; }   # Amendment 1's version (A1.8)
nmoved=0; nadded=0
for f in $CHANGED $NEW; do
  want=$(sha "$CODE/phase1_system_dev/$f")
  have=$(ssh "$HPC" "if [ -e $SD/$f ]; then sha256sum < $SD/$f; fi" | cut -c1-64)
  if [ "$have" = "$want" ]; then continue; fi
  if [ -n "$have" ]; then
    case " $CHANGED " in *" $f "*) ;; *) stop "$SD/$f exists and is not the version $A2 lists: tell Claude";; esac
    [ "$have" = "$(a1 "$f")" ] || stop "$SD/$f is neither Amendment 1's nor Amendment 2's version: tell Claude"
    ssh "$HPC" "mkdir -p $SD/superseded_a1 && test ! -e $SD/superseded_a1/$f && mv $SD/$f $SD/superseded_a1/$f" \
      || stop "could not move $SD/$f into superseded_a1/ (is a copy there already?): tell Claude"
    nmoved=$((nmoved + 1))
  fi
  scp -q "$CODE/phase1_system_dev/$f" "$HPC:$SD/$f.part" || stop "copying $f to hpc1 failed (run this again)"
  [ "$(ssh "$HPC" "sha256sum < $SD/$f.part" | cut -c1-64)" = "$want" ] || stop "$f arrived on hpc1 damaged (run this again)"
  ssh "$HPC" "mv $SD/$f.part $SD/$f" || stop "could not put $f in place on hpc1"
  nadded=$((nadded + 1))
done
for f in $CHANGED $NEW; do
  listed "$f" "$(ssh "$HPC" "sha256sum < $SD/$f" | cut -c1-64)" || stop "$SD/$f is not the version $A2 lists"
done
ssh "$HPC" "cd $SD && python3 -B spa_package.py selftest > /dev/null" || stop "spa_package.py's self-test failed on hpc1: tell Claude"
echo "1. hpc1: no job running from $SD; the five scripts in $SD are $A2's ($nadded copied, $nmoved Amendment 1 version(s) kept in superseded_a1/); the statistics self-test passes there"

# ---- 2. hpc1: the sources' sha256 from the repos' records; two generations
crec() { awk -v p="$1" '$2 == p {print $1}' "$RES/$C4/c4_sources.sha256"; }
band() { awk -F'\t' -v f="$1" '/^frame\t/ {for (i = 1; i <= NF; i++) if ($i == "band") c = i; next} !/^#/ && c && $1 == f {print $c}' \
           "$RES/$C4/c4_bands.tsv"; }
{ grep " $RH/03_amber/tleap_build/complex_solvated.prmtop\$" "$RES/00_admin/sha256_step09_tleap_build.txt" || stop "no recorded sha256 for the prmtop in 00_admin/sha256_step09_tleap_build.txt"
  echo "$P41  $RH/05_qmmm/19_ensemble/frame_41786/complex_solvated.ORCAFF.prms"
  for f in c4_bands.tsv active_atoms.txt; do echo "$(sha "$RES/$C4/$f")  $RH/$C4/$f"; done
  for f in $MD_FRAMES; do
    b=$(band "$f"); [ -n "$b" ] || stop "no band for frame $f in c4_bands.tsv"
    p="05_qmmm/19_ensemble/frame_$f/frame_${f}_CHA2.pdb"; echo "$(crec "$p")  $RH/$p"
    p="05_qmmm/$b/frame_$f/neb_MEP.allxyz"; echo "$(crec "$p")  $RH/$p"
    for x in neb.inp neb_MEP.QMRegion_trj.xyz; do
      p="05_qmmm/$b/frame_$f/$x"; h=$(sha "$RES/$p")
      [ "$h" = "$(crec "REPO/$p")" ] || stop "$p in the results repo is not the file c4_sources.sha256 records"
      echo "$h  $RH/$p"
    done
  done; } > "$S/expected.sha256"
NE=$((4 + 4 * $(echo $MD_FRAMES | wc -w)))
[ "$(wc -l < "$S/expected.sha256")" -eq "$NE" ] && [ "$(grep -c '^[0-9a-f]\{64\}  /' "$S/expected.sha256")" -eq "$NE" ] \
  || { grep -v '^[0-9a-f]\{64\}  /' "$S/expected.sha256" | head; stop "could not build the $NE expected checksums from the repos"; }
if ssh "$HPC" "test -e $SD/staging/expected_package.sha256"; then
  ssh "$HPC" "cat $SD/staging/expected_package.sha256" | cmp -s - "$S/expected.sha256" || stop "staging/expected_package.sha256 on hpc1 differs from the repos' records: tell Claude"
else
  scp -q "$S/expected.sha256" "$HPC:$SD/staging/expected_package.sha256.part" || stop "copying the expected checksums to hpc1 failed (run this again)"
  ssh "$HPC" "cat $SD/staging/expected_package.sha256.part" | cmp -s - "$S/expected.sha256" || stop "the expected checksums arrived on hpc1 damaged (run this again)"
  ssh "$HPC" "mv $SD/staging/expected_package.sha256.part $SD/staging/expected_package.sha256" || stop "could not put the expected checksums in place on hpc1"
fi
manifest() {   # folder on hpc1; the paths to list come on stdin (one per line): "<sha256> path", "link <target> path" or "missing path"
  ssh "$HPC" "cd $1 && while read -r p; do if [ -L \"\$p\" ]; then echo \"link \$(readlink \"\$p\") \$p\"; elif [ -f \"\$p\" ]; then echo \"\$(sha256sum < \"\$p\" | cut -c1-64) \$p\"; else echo \"missing \$p\"; fi; done"
}
free=$(ssh "$HPC" "df -Pk $SD | awk 'NR == 2 {print \$4}'")
[ -n "$free" ] && [ "$free" -ge 2000000 ] || stop "hpc1 has $((${free:-0} / 1000000)) GB free where $SD is; the two generations need up to about 1 GB: free some space there first"
mark() {   # DO_NOT_SUBMIT in every run folder not yet submitted (submit.sh refuses while it exists); prints how many were marked
  ssh "$HPC" "n=0; for r in $RUNS; do cd $SD/\$r || exit 1; if [ ! -e DO_NOT_SUBMIT ] && [ ! -e SUBMITTED ] && [ ! -e SUBMITTED.partial ]; then \
    echo 'x83: the package is submitted in waves sized to the disk (SP_AMENDMENT2.txt A2.10) by the next bundle, which removes this file for each wave' > DO_NOT_SUBMIT || exit 1; fi; \
    [ -e DO_NOT_SUBMIT ] && n=\$((n + 1)); done; echo \$n"
}
existing=$(ssh "$HPC" "cd $SD && ls -d $RUNS 2> /dev/null || true" | LC_ALL=C sort)
if [ -n "$existing" ]; then
  [ "$existing" = "$(printf '%s\n' $RUNS | LC_ALL=C sort)" ] || stop "only some of the $NR run folders exist on hpc1: tell Claude"
  G=""; for r in $RUNS; do G="$G $r/*.pbs.out $r/SUBMITTED $r/SUBMITTED.partial"; done
  if ssh "$HPC" "cd $SD && ls $G 2> /dev/null || true" | grep -q .; then
    [ -e "$RES/$T/$REC/expected_package.sha256" ] || stop "some run folders have been submitted although their inputs are not committed: tell Claude"
    echo "   (some run folders have been submitted already, after their inputs were committed)"
  fi
  nm=$(mark) || stop "could not mark the run folders DO_NOT_SUBMIT"
  echo "2. the $NR run folders exist on hpc1 already ($nm marked DO_NOT_SUBMIT): generating once more into a scratch folder to compare"
else
  ssh "$HPC" "cd $SD && python3 spa_prepare.py staging/expected_package.sha256 $SD $SPECS" > "$S/gen1.txt" \
    || { tail -5 "$S/gen1.txt"; stop "the generator stopped on hpc1 (above): tell Claude before running this again"; }
  nm=$(mark) || stop "could not mark the run folders DO_NOT_SUBMIT: do not submit anything; tell Claude"
  echo "2. generated on hpc1: $(grep -c '^== ' "$S/gen1.txt") run folders, $nm marked DO_NOT_SUBMIT"
  grep -E '^== |^region \(|^alternation' "$S/gen1.txt" | sed -E 's/^region \(whole residues[^)]*\): /     region: /; s/^alternation.*environment = the region without them, /     environment: /' | cut -c1-120
fi
RG=$(ssh "$HPC" "mktemp -d $SD/staging/regen.XXXXXX") || stop "could not make a scratch folder on hpc1"
ssh "$HPC" "cd $SD && python3 spa_prepare.py staging/expected_package.sha256 $RG $SPECS" > "$S/gen2.txt" || stop "the second generation failed"
ssh "$HPC" "cd $RG && find $RUNS \\( -type f -o -type l \\) | LC_ALL=C sort" > "$S/paths.txt" || stop "listing the second generation failed"
manifest "$RG" < "$S/paths.txt" > "$S/m2.txt" || stop "reading the second generation failed"
manifest "$SD" < "$S/paths.txt" > "$S/m1.txt" || stop "reading the run folders failed"
ssh "$HPC" "rm -rf $RG" && RG=""
[ "$(wc -l < "$S/paths.txt")" -eq $((NR * 36)) ] || stop "the second generation wrote $(wc -l < "$S/paths.txt") files and links, expected $((NR * 36)) ($NR x (27 files + 9 links))"
cmp -s "$S/m1.txt" "$S/m2.txt" || { diff "$S/m1.txt" "$S/m2.txt" | head || true; stop "the run folders on hpc1 differ from a fresh generation: tell Claude"; }
grep -q '^missing ' "$S/m1.txt" && stop "a generated file is missing on hpc1: tell Claude"
echo "   a second generation reproduces every generated file and link on hpc1 byte for byte ($(wc -l < "$S/paths.txt"))"

# ---- 3. commit the inputs (every generated file but the full-system start files), the expected list and the scripts
cd "$RES"
L=""
for r in $RUNS; do
  L="$L $r/GENERATOR_LOG.txt $r/region.txt $r/starts.sha256 $r/submit.sh $r/irc/irc.inp"
  for j in job_ts job_ts_freq_irc job_r_irc job_r_irc_freq job_p_irc job_p_irc_freq job_r0 job_r0_freq; do L="$L $r/$j.pbs"; done
  for st in ts r_irc p_irc r0; do L="$L $r/$st/env.inp $r/$st/core.inp"; done
  for st in ts_freq r_irc_freq p_irc_freq r0_freq; do L="$L $r/$st/freq.inp"; done
done
mkdir "$S/D"; ssh "$HPC" "cd $SD && tar -cf - $L" | tar -xf - -C "$S/D" || stop "fetching the inputs from hpc1 failed"
for r in $RUNS; do
  ( cd "$S/D/$r" && grep '^  [0-9a-f]\{64\}  ' GENERATOR_LOG.txt | grep -v -e ' ts/start.xyz$' -e ' r0/start.xyz$' | sed 's/^  //' | sha256sum -c --quiet ) \
    || stop "$r: a fetched input differs from its GENERATOR_LOG record"
  [ "$(grep -c '^  [0-9a-f]\{64\}  ' "$S/D/$r/GENERATOR_LOG.txt")" -eq 26 ] || stop "$r: GENERATOR_LOG.txt does not record the 26 files it wrote besides itself"
  for st in ts r0; do
    h=$(grep " $r/$st/start.xyz\$" "$S/m1.txt" | cut -c1-64)
    grep -q "^  $h  $st/start.xyz\$" "$S/D/$r/GENERATOR_LOG.txt" || stop "$r/$st/start.xyz on hpc1 is not the one its log records"
  done
done
NF0=$(echo $L | wc -w)
# every fetched file, the logs included, against the sha256 taken on hpc1 in step 2
printf '%s\n' $L | awk 'NR == FNR {w[$1]; next} ($2 in w) {print $1 "  " $2}' - "$S/m1.txt" > "$S/L.sha256"
[ "$(wc -l < "$S/L.sha256")" -eq "$NF0" ] || stop "the hpc1 manifest lacks some of the $NF0 inputs: tell Claude"
( cd "$S/D" && sha256sum -c --quiet "$S/L.sha256" ) || stop "a fetched input differs from the file on hpc1: tell Claude"
if [ -e "$T/$REC/expected_package.sha256" ]; then
  for p in $L; do cmp -s "$S/D/$p" "$T/$p" || stop "$p on hpc1 differs from the committed input: tell Claude"; done
  cmp -s "$S/expected.sha256" "$T/$REC/expected_package.sha256" || stop "$T/$REC/expected_package.sha256 differs from the repos' records: tell Claude"
  echo "3. inputs already committed and identical to hpc1's ($NF0 files)"
else
  for r in $RUNS; do [ ! -e "$T/$r" ] || stop "$T/$r exists without $T/$REC: tell Claude"; done
  for p in $L; do mkdir -p "$T/$(dirname "$p")"; cp "$S/D/$p" "$T/$p"; done
  mkdir -p "$T/$REC"
  cp "$S/expected.sha256" "$T/$REC/expected_package.sha256"
  cp "$B/x83_package_inputs.sh" "$B/MANIFEST.sha256" "$T/$REC/"
  git add "$T"
  [ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the inputs commit would modify or delete a committed file: tell Claude"
  NF=$(git diff --cached --name-only | wc -l); [ "$NF" -eq $((NF0 + 3)) ] || stop "expected $((NF0 + 3)) files, staged $NF: tell Claude"
  ENV=$(for r in $RUNS; do grep -m1 '^alternation' "$T/$r/GENERATOR_LOG.txt" | sed 's/.*them, //; s/ atoms.*//'; done | sort -n | sed -n '1p;$p' | tr '\n' ' ')
  git commit -q -m "SP package inputs (SP_AMENDMENT2.txt A2.10), committed before any package job is submitted: $NR run folders at 8 A under Amendment 1's alternating scheme with A2.6's 20-cycle limit - the 29 frames of c4_bands.tsv other than 42436 with S = md (f<FRAME>_r8_a1) and frames 20000, 44388 and 59999 with S = ci (f<FRAME>_r8_ci_a1); environments of $(echo $ENV | sed 's/ / to /') atoms plus the 24 substrate atoms; generated on hpc1 by spa_prepare.py (code $(git -C "$CODE" log -1 --format=%h -- phase1_system_dev/spa_prepare.py)) from sources checked against the repos' sha256 records ($REC/expected_package.sha256), and reproduced byte for byte by a second generation; per run folder its GENERATOR_LOG.txt, region.txt, starts.sha256, inputs, the eight job scripts and submit.sh (the two full-system start files stay on hpc1, their sha256 in the log). On hpc1 the scripts are Amendment 2's (Amendment 1's kept in superseded_a1/) and every run folder is marked DO_NOT_SUBMIT until its wave (A2.10). Nothing submitted [retained-final]" -m "$TRAILER" \
    || stop "git commit failed (above); nothing was committed. To clear the copies:  git -C $RES reset -q && git -C $RES clean -fdq -- $T"
  echo "3. inputs committed: $(git log -1 --format=%h) ($NF files, additions only)"
fi
git push -q || stop "push failed: run  git -C $RES push origin main"
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub: run  git -C $RES push origin main"
echo "   pushed: results $(git log -1 --format=%h), in step with GitHub. Nothing was submitted."
