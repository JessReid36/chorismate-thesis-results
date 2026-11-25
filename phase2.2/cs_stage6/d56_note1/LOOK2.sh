bash -c '
set -u -o pipefail
stop() { echo "LOOK2 STOPPED: $1 Send Claude everything printed above."; exit 1; }
R="/home/jess/Desktop/chorismate-thesis-results"
C="/home/jess/Desktop/chorismate-thesis-code"
H=947942df6d2762a4efb0c40e173436def5ed0c7860ce6396b04dad08d93e9327
echo "LOOK2 at $(date)"
F=""
while IFS= read -r c; do [ "$(sha256sum "$c" | cut -d" " -f1)" = "$H" ] && F="$c"; done <<< "$(find /home/jess/Downloads -maxdepth 1 -type f -name "d56_look2*.py")"
[ -n "$F" ] || stop "the file d56_look2.py that Claude sent is not in Downloads. Nothing was changed."
git -C "$R" fetch -q origin || stop "GitHub could not be reached. Nothing was changed."
git -C "$R" log -1 --format=%s origin/main | grep -q "^\[retained-final\] AMENDMENT 12" || stop "the last commit on GitHub is not AMENDMENT 12. This look is for the time between A2 and H1 only. Nothing was changed."
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/main)" ] || stop "the results repository on this PC is not level with GitHub. Nothing was changed."
[ -z "$(git -C "$R" status --porcelain --untracked-files=all)" ] || stop "the results repository has files that are changed or not committed. Has H1 been run? Nothing was changed."
[ "$(git -C "$C" rev-parse HEAD)" = 3de5c4cda3ed201c21c43dbf1ea9bc39afe6bf79 ] || stop "the code repository is not at the commit that holds the reader. Nothing was changed."
[ -z "$(git -C "$C" status --porcelain --untracked-files=all)" ] || stop "the code repository has files that are changed or not committed. Nothing was changed."
T="/home/jess/Downloads/d56_look_$(date +%H%M%S)"
[ ! -e "$T" ] || stop "the folder $T exists already. Run LOOK2 again. Nothing was changed."
mkdir -p "$T" && cp -r "$R/phase2.2/cs_stage6/d56" "$T/d56" || stop "the committed inputs could not be copied into $T."
ssh 18660916@hpc "cd /home/18660916/system_development/phase2.2/cs_stage6/d56 && find . -maxdepth 2 -name job.out | tar -czf - -T -" | tar -xzf - -C "$T/d56" || stop "the outputs could not be fetched from hpc1. The folder $T can be deleted."
echo "   outputs fetched: $(find "$T/d56" -name job.out | wc -l) of 224, into $T ($(du -sh "$T" | cut -f1))"
echo
python3 "$F" --res "$R" --code "$C" --look "$T" || stop "the look script failed; the lines above say where. Nothing in either repository was changed."
[ -z "$(git -C "$R" status --porcelain --untracked-files=all)" ] || stop "the results repository changed during the look. Do not go on."
echo "LOOK2 DONE: nothing was changed on hpc1 or in either repository. The folder $T can be deleted. Paste everything printed above to Claude."
'
