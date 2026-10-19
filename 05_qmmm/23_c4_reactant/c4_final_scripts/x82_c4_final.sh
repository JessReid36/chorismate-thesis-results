#!/usr/bin/env bash
# x82_c4_final.sh - RUN ON THE PC (not on hpc1), from anywhere:  bash x82/x82_c4_final.sh
# C4's steps 0-2 on all 35 runs, as C4_CLOSURE.txt sets out (item 3), from the files x81 committed (results d3f72f4):
#  0. checks: the bundle; both repos clean, up to date and on their branches; d3f72f4 in the results repo;
#     C4_CRITERIA.txt, C4_AMENDMENT1.txt, C4_CLOSURE.txt and the two analysis scripts are the files C4_FINAL.txt names;
#  1. in a scratch folder: each run's committed text archive extracted and checked against its manifest; the
#     pre-registered c4_analyse.py and the amended c4_analyse_a1.py run on all 35 runs; x_check.py repeats check X;
#  2. the six outputs must be byte-identical to Claude's run of the same scripts on the same files (sha256 in
#     C4_FINAL.txt), and x_check.py's line the same; if anything differs, nothing is committed and the outputs are left
#     in ~/Downloads/x82_outputs for Claude;
#  3. results repo: the six outputs and C4_FINAL.txt into 05_qmmm/23_c4_reactant/, this bundle's scripts into
#     05_qmmm/23_c4_reactant/c4_final_scripts/ - one commit, additions only [retained-final]; pushed and checked.
# M1: all 35 runs are finished, so there are no continuations to make. Touches nothing on hpc1 and nothing already
# committed. Safe to re-run: once committed, it checks the commit and stops.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
RES="$HOME/Desktop/chorismate-thesis-results"
CODE="$HOME/Desktop/chorismate-thesis-code"
C=05_qmmm/23_c4_reactant
P=phase1_system_dev
X81=d3f72f4
OUTS="C4_REPORT.txt c4_results.tsv c4_step0.tsv C4_A1_REPORT.txt c4_a1_results.tsv c4_a1_step0.tsv"
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017YuATYmxt3jH4FZabHPPtD"
stop() { echo "STOP: $*"; exit 1; }
sha() { sha256sum < "$1" | cut -c1-64; }
expect() { awk -v f="$1" '$1 == "sha256" && $2 == f {print $3}' "$B/C4_FINAL.txt"; }
XLINE=$(sed -n 's/^  x_check.py: //p' "$B/C4_FINAL.txt")

# ---- 0. the bundle, the repos and the inputs
( cd "$B" && sha256sum -c --quiet MANIFEST.sha256 ) || stop "a bundle file differs from MANIFEST.sha256: download the bundle again"
for t in python3 xz tar git; do command -v "$t" > /dev/null || stop "$t is needed on the PC"; done
for r in "$RES" "$CODE"; do
  [ -d "$r/.git" ] || stop "$r is not a git repo"
  [ -z "$(git -C "$r" status --porcelain)" ] || stop "$r has uncommitted changes"
done
[ "$(git -C "$RES" rev-parse --abbrev-ref HEAD)" = main ] || stop "the results repo is not on main"
[ "$(git -C "$CODE" rev-parse --abbrev-ref HEAD)" = tier1-realism ] || stop "the code repo is not on tier1-realism"
for r in "$RES" "$CODE"; do git -C "$r" pull --ff-only -q || stop "git pull failed in $r"; done
git -C "$RES" merge-base --is-ancestor "$X81" HEAD 2> /dev/null || stop "x81's commit $X81 is not in the results repo: run x81 first"
for f in C4_CRITERIA.txt C4_AMENDMENT1.txt C4_CLOSURE.txt; do
  [ "$(sha "$RES/$C/$f")" = "$(expect "$f")" ] || stop "$C/$f is not the file C4_FINAL.txt names: tell Claude"
done
for f in c4_analyse.py c4_analyse_a1.py; do
  [ "$(sha "$CODE/$P/$f")" = "$(expect "$f")" ] || stop "$P/$f in the code repo is not the committed analysis C4_FINAL.txt names: tell Claude"
done
[ -n "$XLINE" ] || stop "C4_FINAL.txt has no x_check.py line: download the bundle again"
if [ -e "$RES/$C/C4_FINAL.txt" ]; then
  cmp -s "$RES/$C/C4_FINAL.txt" "$B/C4_FINAL.txt" || stop "$C/C4_FINAL.txt is committed and differs from the bundle's: tell Claude"
  for f in $OUTS; do [ "$(sha "$RES/$C/$f")" = "$(expect "$f")" ] || stop "$C/$f differs from C4_FINAL.txt: tell Claude"; done
  for f in x82_c4_final.sh x_check.py; do cmp -s "$RES/$C/c4_final_scripts/$f" "$B/$f" || stop "$C/c4_final_scripts/$f differs from the bundle's: tell Claude"; done
  git -C "$RES" fetch -q && [ "$(git -C "$RES" rev-parse HEAD)" = "$(git -C "$RES" rev-parse '@{u}')" ] \
    || stop "committed but not in step with GitHub: run  git -C $RES push origin main"
  echo "already committed and pushed: C4_FINAL.txt, the six outputs and the scripts are in the results repo as C4_FINAL.txt names them; nothing to do"
  exit 0
fi
for f in $OUTS c4_final_scripts; do [ ! -e "$RES/$C/$f" ] || stop "$C/$f exists already: tell Claude"; done
echo "0. bundle intact; both repos clean and up to date; x81's $X81 present; criteria, amendment, closure and both analyses are the named files"

# ---- 1. the analyses, from the committed files, in a scratch folder
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
WC="$W/$C"; mkdir -p "$WC"
cp -r "$RES/$C/runs.tsv" "$RES/$C/c4_bands.tsv" "$RES/$C/active_atoms.txt" "$RES/$C/frames" "$WC/"
n=0
for a in "$RES/$C"/S*/hpc_text_outputs_1.tar.xz; do
  tar -xJf "$a" -C "$W" || stop "extracting $a failed"
  ( cd "$W" && sha256sum -c --quiet "${a%.tar.xz}.MANIFEST.sha256" ) || stop "$a does not match its manifest: tell Claude"
  n=$((n + 1))
done
[ "$n" -eq 35 ] && [ "$(find "$WC" -mindepth 1 -maxdepth 1 -type d -name 'S*' | wc -l)" -eq 35 ] \
  || stop "expected 35 run archives and 35 run folders, found $n archives: tell Claude"
echo "1. 35 run archives extracted and every file checked against its manifest ($(find "$WC" -mindepth 2 -type f -path '*/S*/*' | wc -l) files)"
cp "$CODE/$P/c4_analyse.py" "$CODE/$P/c4_analyse_a1.py" "$W/"
( cd "$W" && python3 -I c4_analyse.py "$WC" > "$W/c4_analyse.log" 2>&1 ) || { tail -5 "$W/c4_analyse.log"; stop "c4_analyse.py failed (above): tell Claude"; }
( cd "$W" && python3 -I c4_analyse_a1.py "$WC" > "$W/c4_analyse_a1.log" 2>&1 ) || { tail -5 "$W/c4_analyse_a1.log"; stop "c4_analyse_a1.py failed (above): tell Claude"; }
xgot=$(python3 -I "$B/x_check.py" "$WC") || { echo "$xgot"; stop "x_check.py failed (above): tell Claude"; }
echo "   both analyses ran (Python $(python3 -c 'import platform; print(platform.python_version())')); X: $xgot"

# ---- 2. the same as Claude's run, byte for byte
diff=""
for f in $OUTS; do [ "$(sha "$WC/$f")" = "$(expect "$f")" ] || diff="$diff $f"; done
[ "$xgot" = "$XLINE" ] || diff="$diff x_check.py's line"
if [ -n "$diff" ]; then
  O="$HOME/Downloads/x82_outputs"; rm -rf "$O"; mkdir -p "$O"
  for f in $OUTS; do cp "$WC/$f" "$O/"; done; cp "$W"/c4_analyse*.log "$O/"; echo "$xgot" > "$O/x_check.txt"
  stop "these differ from Claude's run:$diff. Nothing was committed; the outputs are in $O - send them to Claude"
fi
echo "2. all six outputs byte-identical to Claude's run (sha256 in C4_FINAL.txt); X line identical"

# ---- 3. commit (additions only), push, check
cd "$RES"
for f in $OUTS; do cp "$WC/$f" "$C/$f"; done
cp "$B/C4_FINAL.txt" "$C/C4_FINAL.txt"
mkdir -p "$C/c4_final_scripts"
cp "$B/x82_c4_final.sh" "$B/x_check.py" "$C/c4_final_scripts/"
( cd "$C/c4_final_scripts" && sha256sum x82_c4_final.sh x_check.py ../C4_FINAL.txt > MANIFEST.sha256 )
git add "$C/C4_FINAL.txt" "$C/c4_final_scripts" $(for f in $OUTS; do echo "$C/$f"; done)
[ "$(git diff --cached --name-status | grep -vc '^A')" -eq 0 ] || stop "the commit would modify or delete a committed file: tell Claude"
nf=$(git diff --cached --name-only | wc -l)
PYV=$(python3 -c 'import platform; print(platform.python_version())')
git commit -q -m "C4's steps 0-2 on all 35 runs, reported as C4_CLOSURE.txt sets out (C4_FINAL.txt): M1 met by all 35 runs, so no continuations; G, X and M0 pass; the pre-registered M2 fails for S2_24883 and S2_42436 (labels one NEB iteration old) and the amended M2 passes for all 35; step 0 finds incomplete optimisation in all five image-0 frames; step 2 accepts 0 of 30 frames - A1 fails in every frame (re-optimised reactant 1.7 to 11.6 kcal/mol below k_low), A2 passes in all, A3 fails in 23268 only; steps 3-6 not run. C4_REPORT.txt and C4_A1_REPORT.txt with their tables, from c4_analyse.py and c4_analyse_a1.py (code 471da61) on the files committed in $X81, byte-identical on Claude's run and on this PC (Python $PYV); x_check.py repeats X from the committed geometries [retained-final]" -m "$TRAILER" \
  || stop "git commit failed (above); nothing was committed. To clear the staged copies:  git -C $RES reset -q && git -C $RES clean -fdq -- $C"
echo "3. committed: $(git log -1 --format=%h) ($nf files, additions only)"
git push -q || stop "push failed: run  git -C $RES push origin main"
git fetch -q && [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] || stop "the results repo is not in step with GitHub after the push: run  git -C $RES push origin main"
echo "   pushed: results $(git log -1 --format=%h), in step with GitHub. C4 is closed; nothing was changed on hpc1."
