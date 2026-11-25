R=~/Desktop/chorismate-thesis-results && git -C "$R" fetch -q origin && \
git -C "$R" log -1 --format=%s origin/main | grep -q "^\[retained-final\] AMENDMENT 12" && \
ssh 18660916@hpc "P=/home/18660916/system_development/phase2.2/cs_stage6/d56; [ -d \$P ] || { echo 'NOTE|LOOK STOPPED: d56 is not on hpc1.'; exit 1; }; echo \"NOTE|LOOK at \$(date)\"; for L in C0 N1 N2 N3 N4 N5 N6 N7 N8 N9; do if grep -q '^finished: ' \$P/run_\$L.pbs.out 2>/dev/null; then echo \"JOB|\$L|ended\"; else echo \"JOB|\$L|not ended\"; fi; done; for r in \$(grep -h '^run ' \$P/run_*.pbs | cut -d' ' -f2); do f=\$P/\$r/job.out; if [ -e \$f ]; then o=\$(grep -c 'ORCA TERMINATED NORMALLY' \$f); e=\$(awk '/FINAL SINGLE POINT ENERGY/{v=\$NF} END{print v}' \$f); s=\$(grep -i -o -E 'wave ?function is (stable|unstable)' \$f | awk '{print \$NF}' | tr '\n' ','); c=\$(grep -c 'SCF NOT CONVERGED' \$f); echo \"ROW|\$r|\$o|\$e|\$s|\$c\"; else echo \"ROW|\$r|none|||0\"; fi; done" | awk -F"|" '
$1=="NOTE" { print $2; next }
$1=="JOB" { if ($3=="ended") je = je " " $2; else jn = jn " " $2; next }
$1=="ROW" { n++; r=$2; if ($3=="1" && $4 != "") { E[r]=$4; ok++ } else if ($3=="none") { nout++ } else { nbad++; badl = badl " " r }
  if (index(tolower($5),"unstable")>0) U[r]=1; if ($6+0>0) NC[r]=1
  split(r,a,"_"); if (a[2]=="S") { d=a[3] "_" a[4]; if ((d in seen)==0) { seen[d]=1; ord[++nd]=d } } next }
END {
  if (n==0) { print "LOOK: no rows came back. hpc1 could not be reached, or d56 is not there. Nothing was changed."; exit }
  H=627.5094740631; V=27.211386245988
  print ""; print "UNOFFICIAL LOOK. These are not results. The result is only what H1 prints."
  print "jobs that ran to their end:" (je=="" ? " none" : je); print "jobs not ended yet:" (jn=="" ? " none" : jn)
  printf "runs: %d in all, %d ended normally, %d with no output yet, %d with an output that has not ended normally\n", n, ok+0, nout+0, nbad+0
  if (nbad>0) print "   not ended normally (running now, or failed):" badl
  print ""
  for (i=1;i<=2;i++) { L=(i==1)?"SV":"TZ"; if ((L "_C_ctl_R" in E) && (L "_C_ctl_TS" in E)) { bar[L]=(E[L "_C_ctl_TS"]-E[L "_C_ctl_R"])*H; printf "barrier with no charges, %s: %.3f kcal/mol\n", L, bar[L] } else printf "barrier with no charges, %s: controls not finished\n", L }
  print ""; print "change of the barrier in kcal/mol (negative = lower). SV = def2-SVPD, TZ = def2-TZVPD."
  print "bound = energy to remove one electron, in eV, at R and at TS (positive = the electron stays)."
  print ""
  printf "%-8s %9s %9s %8s   %-15s %-15s %s\n", "design", "SV", "TZ", "TZ vs SV", "bound SV (R,TS)", "bound TZ (R,TS)", "notes"
  for (j=1;j<=nd;j++) { d=ord[j]; line=sprintf("%-8s", d); note=""
    for (i=1;i<=2;i++) { L=(i==1)?"SV":"TZ"; k=L "_S_" d "_di_"; has[L]=0
      if ((k "R" in E) && (k "TS" in E) && (L in bar)) { dd[L]=(E[k "TS"]-E[k "R"])*H-bar[L]; has[L]=1; line=line sprintf(" %9.3f", dd[L]) } else line=line sprintf(" %9s", "--") }
    if (has["SV"] && has["TZ"] && dd["SV"] != 0) { p=100*(dd["TZ"]-dd["SV"])/(dd["SV"]<0?-dd["SV"]:dd["SV"]); line=line sprintf(" %7.1f%%", p) } else line=line sprintf(" %8s", "--")
    line=line "  "
    for (i=1;i<=2;i++) { L=(i==1)?"SV":"TZ"; b=""
      for (t=1;t<=2;t++) { st=(t==1)?"R":"TS"; kd=L "_S_" d "_di_" st; km=L "_S_" d "_mo_" st
        if ((kd in E) && (km in E)) b=b sprintf("%6.2f", (E[km]-E[kd])*V); else b=b sprintf("%6s", "--"); if (t==1) b=b "," }
      line=line sprintf(" %-15s", b) }
    for (i=1;i<=2;i++) { L=(i==1)?"SV":"TZ"; for (q=1;q<=2;q++) { c=(q==1)?"di":"mo"; for (t=1;t<=2;t++) { st=(t==1)?"R":"TS"; k=L "_S_" d "_" c "_" st
      if (k in U) note=note " " L "_" c "_" st ":UNSTABLE"; if (k in NC) note=note " " L "_" c "_" st ":SCF-not-converged" } } }
    print line " " note }
  print ""
  print "NOT read in this look: the four legs (where the electrons sit, dipole, gap, cycles). So no design"
  print "is called a survivor here. A TZ vs SV figure under 15 percent is what the committed rule asks for,"
  print "and a change smaller than 3.2 kcal/mol at SV cannot be assessed by that rule."
  print "LOOK DONE: nothing was changed on hpc1 or on this PC. Paste everything printed above to Claude."
}' || echo "LOOK STOPPED: AMENDMENT 12 is not on GitHub yet (run A1 and A2 first), or GitHub could not be reached. Nothing was changed."
