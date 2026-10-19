#!/bin/bash
# submit.sh - the eight jobs of f52192_r8_a1 (SP Amendment 1), with dependencies (PBS afterok: a job starts only if the one it
# needs ended with exit 0, i.e. every check passed). Run once, on hpc1: bash /home/18660916/system_development/05_qmmm/24_sp_barriers/f52192_r8_a1/submit.sh
set -euo pipefail
cd /home/18660916/system_development/05_qmmm/24_sp_barriers/f52192_r8_a1
[[ -e SUBMITTED ]] && { echo "STOP: already submitted (SUBMITTED lists the job ids)"; exit 1; }
[[ -e SUBMITTED.partial ]] && { echo "STOP: an earlier submission stopped part-way; these jobs are queued (tell Claude, do not re-run):"; cat SUBMITTED.partial; exit 1; }
[[ -e DO_NOT_SUBMIT ]] && { echo "STOP: DO_NOT_SUBMIT: $(cat DO_NOT_SUBMIT)"; exit 1; }
for j in job_ts job_ts_freq_irc job_r_irc job_r_irc_freq job_p_irc job_p_irc_freq job_r0 job_r0_freq; do
  [[ -s $j.pbs ]] || { echo "STOP: missing $j.pbs"; exit 1; }
  [[ -e $j.pbs.out ]] && { echo "STOP: $j.pbs.out exists"; exit 1; }
done
sub() { local id; id=$(qsub "$@") || { echo "STOP: qsub $* failed; submitted so far (also in SUBMITTED.partial):" >&2; cat SUBMITTED.partial >&2; exit 1; }; echo "$id"; }
: > SUBMITTED.partial
A1=$(sub job_ts.pbs);                                  echo "job_ts $A1" >> SUBMITTED.partial
A2=$(sub -W depend=afterok:$A1 job_ts_freq_irc.pbs);  echo "job_ts_freq_irc $A2" >> SUBMITTED.partial
B1=$(sub -W depend=afterok:$A2 job_r_irc.pbs);        echo "job_r_irc $B1" >> SUBMITTED.partial
B2=$(sub -W depend=afterok:$B1 job_r_irc_freq.pbs);   echo "job_r_irc_freq $B2" >> SUBMITTED.partial
C1=$(sub -W depend=afterok:$A2 job_p_irc.pbs);        echo "job_p_irc $C1" >> SUBMITTED.partial
C2=$(sub -W depend=afterok:$C1 job_p_irc_freq.pbs);   echo "job_p_irc_freq $C2" >> SUBMITTED.partial
D1=$(sub job_r0.pbs);                                  echo "job_r0 $D1" >> SUBMITTED.partial
D2=$(sub -W depend=afterok:$D1 job_r0_freq.pbs);      echo "job_r0_freq $D2" >> SUBMITTED.partial
mv SUBMITTED.partial SUBMITTED
echo "f52192_r8_a1: submitted"; cat SUBMITTED
