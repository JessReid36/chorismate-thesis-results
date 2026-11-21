bash -c '
set -u
stop() { echo; echo "CLEANPC STOPPED: $*"; echo "Nothing was removed. Send Claude everything printed above."; exit 1; }
echo "CLEANPC at $(date)"
D=""; n=0
for d in /media/jess/*/; do [ -d "$d" ] || continue; if [ "$(stat -c %d "$d")" != "$(stat -c %d /media/jess)" ] && [ "$(stat -c %d "$d")" != "$(stat -c %d /home/jess/Downloads)" ]; then D="${d%/}"; n=$((n+1)); fi; done
[ "$n" = 1 ] || stop "expected exactly one drive under /media/jess and found $n. Is the hard drive plugged in?"
F="$D/chorismate-hpc-archive/phase2.2/cs_stage6/d44/hpc_all_files_d44.tar.xz"
R=/home/jess/Desktop/chorismate-thesis-results
X=/home/jess/Downloads/cs_d44_harvest_work/x
[ -f "$F" ] || stop "the D44 archive is not on the drive."
[ "$(stat -c %s "$F")" = 12431555204 ] || stop "the D44 archive on the drive has not the committed size."
git -C "$R" fetch -q origin || stop "GitHub could not be reached."
[ -z "$(git -C "$R" status --porcelain --untracked-files=all)" ] || stop "the results repository has uncommitted files."
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/main)" ] || stop "the results repository is not level with GitHub."
git -C "$R" merge-base --is-ancestor 3f6765ac307eba9348232518418a725f3aa7f8ea HEAD || stop "the D44 result is not in the results repository."
grep -q 13d9a5ec1d5e5a4380dff7286a3ebf5f1ca360eaaf5f4eff9acb6d28e9b17988 "$R/phase2.2/cs_stage6/d44/PC_ARCHIVES.tsv" || stop "the committed record of the D44 archive is not the expected one."
[ -d /home/jess/Downloads/cs_d44_harvest_work ] || stop "the work folder of the D44 collection is not in Downloads."
echo "   $(date +%H:%M) reading the D44 archive on the drive to take its sha256 (a few minutes, prints nothing) ..."
[ "$(sha256sum "$F" | cut -c1-64)" = 13d9a5ec1d5e5a4380dff7286a3ebf5f1ca360eaaf5f4eff9acb6d28e9b17988 ] || stop "the D44 archive on the drive is not the committed file."
echo "   $(date +%H:%M) the D44 archive on the drive is the committed file, and the D44 result is on GitHub"
touch /home/jess/Downloads/cs_d44_harvest_work/DRIVE_ARCHIVE_VERIFIED_20261120 || stop "could not write the marker for CLEANHPC."
if [ -d "$X" ] && [ ! -L "$X" ]; then
  echo "   the unpacked check copy takes $(du -s -BM "$X" | cut -f1)"
  chmod -R u+w -- /home/jess/Downloads/cs_d44_harvest_work/x 2>/dev/null
  rm -rf -- /home/jess/Downloads/cs_d44_harvest_work/x
  if [ -e "$X" ]; then echo; echo "CLEANPC STOPPED: the check copy could not be removed completely. Send Claude everything printed above."; exit 1; fi
  echo "   removed from this PC: $X"
else
  echo "   the unpacked check copy is already gone"
fi
echo "   free on this PC now: $(df --output=avail -BM /home/jess/Downloads | tail -n 1 | tr -dc 0-9) MB"
echo "CLEANPC DONE: the check copy is off this PC, and the archive on the drive was checked first. Next: CLEANHPC."
'
