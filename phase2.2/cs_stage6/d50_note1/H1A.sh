bash -c '
set -u
stop() { echo; echo "H1A STOPPED: $*"; echo "Nothing is committed. Send Claude everything printed above."; exit 1; }
echo "H1A at $(date)"
D=""; n=0
for d in /media/jess/*/; do [ -d "$d" ] || continue; if [ "$(stat -c %d "$d")" != "$(stat -c %d /media/jess)" ] && [ "$(stat -c %d "$d")" != "$(stat -c %d /home/jess/Downloads)" ]; then D="${d%/}"; n=$((n+1)); fi; done
[ "$n" = 1 ] || stop "expected exactly one drive under /media/jess and found $n. Is the hard drive plugged in?"
A="$D/chorismate-hpc-archive"
[ -d "$A/phase2.2/cs_stage6" ] || stop "the HPC archive is not on the hard drive at $A."
[ ! -e /home/jess/Desktop/chorismate-hpc-archive ] || stop "an archive folder is on the Desktop again. The archive lives on the hard drive."
echo "   the archive folder for this collection: $A"
CS6_ARCHIVE="$A" bash /home/jess/Desktop/chorismate-thesis-code/phase2.2/cs6_d50_harvest.sh collect anyway \
  && echo "H1A DONE: the outputs are read as they stand and the archive is on the hard drive. Runs that did not finish are NOT MEASURED. The result is printed above. Nothing is committed yet. Next: send Claude this printout, then H2." \
  || echo "H1A STOPPED: nothing is committed. Send Claude everything printed above."
'
