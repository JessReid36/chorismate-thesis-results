#!/usr/bin/env bash
# Re-derives the Phase-1 enzyme barrier from raw ORCA outputs. Run from the results repo root.
# Expected: barrier +15.9995 kcal/mol, reaction energy -13.1520 kcal/mol, TS one imaginary mode.
set -u
Q=05_qmmm
get() { grep "FINAL SINGLE POINT ENERGY (QM/MM)" "$1" | tail -1 | awk "{print \$NF}"; }
R=$(get $Q/18e_reactant_reduced/reactant_reduced.out)
TS=$(get $Q/18c_reduced_region/ts_reduced.out)
P=$(get $Q/18f_product_reduced/product_reduced.out)
echo "reactant $R"; echo "TS       $TS"; echo "product  $P"
python3 -c "
H=627.5094740631
R,TS,P=float(\"$R\"),float(\"$TS\"),float(\"$P\")
print(\"barrier        %+.4f kcal/mol\" % ((TS-R)*H))
print(\"reaction energy %+.4f kcal/mol\" % ((P-R)*H))
"
echo "--- active region atom count (expect 102) ---"
tr -s " " "\\n" < $Q/18c_reduced_region/active_reduced.txt | grep -c "[0-9]"
echo "--- converged imaginary modes (expect exactly one, -313.07) ---"
ln=$(grep -n "OPTIMIZATION RUN DONE" $Q/18c_reduced_region/ts_reduced.out | head -1 | cut -d: -f1)
tail -n +"$ln" $Q/18c_reduced_region/ts_reduced.out | grep "\*\*\*imaginary mode\*\*\*"
