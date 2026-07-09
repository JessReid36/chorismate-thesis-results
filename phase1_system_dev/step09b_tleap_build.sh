#!/usr/bin/env bash
# Step 09b - tleap build (ff14SB + GAFF + TIP3P, 10 A box, Na+ neutralise) plus a
# deep prmtop/inpcrd audit, in one pass.
#
# Folds attempt_3 steps 17 (build) + 18 (topology identity) + 18b (log/warning
# classification) + 18c (close-contact) into one. Key correctness point: the
# SOLVATED PDB saturates at 9999 residues, so water/ion counts are read from the
# prmtop/inpcrd (source of truth), never the PDB. Expectations are derived from
# the dry system (Na+ = |dry charge|), not hard-coded.
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

root="$HOME/system_development"
builddir="$root/03_amber/tleap_build"
ligdir="$root/03_amber/ligand_gaff"
admin="$root/00_admin"

pretleap="$builddir/complex_for_tleap.pdb"      # 09a
cha_mol2="$ligdir/cha_gaff.mol2"                 # 08b
cha_frcmod="$ligdir/cha.frcmod"                  # 08b
mkdir -p "$builddir" "$admin"

echo "=== step 09b: input presence ==="
for f in "$pretleap" "$cha_mol2" "$cha_frcmod"; do
  [[ -s "$f" ]] || { echo "FAIL missing/empty: $f"; exit 1; }
  echo "PASS $f"
done

echo
echo "=== step 09b: write tleap input ==="
cat > "$builddir/tleap_complex.in" <<EOF
logFile tleap_complex.log
# Paper-aligned build: protein ff14SB, chorismate GAFF, TIP3P water, 10 A box, Na+.
source leaprc.protein.ff14SB
source leaprc.gaff
source leaprc.water.tip3p

CHA = loadmol2 $cha_mol2
loadamberparams $cha_frcmod

complex = loadpdb $pretleap
check complex
charge complex

saveamberparm complex complex_dry.prmtop complex_dry.inpcrd
savepdb complex complex_dry.pdb

solvatebox complex TIP3PBOX 10.0
addions complex Na+ 0
check complex
charge complex

saveamberparm complex complex_solvated.prmtop complex_solvated.inpcrd
savepdb complex complex_solvated.pdb
quit
EOF
cat "$builddir/tleap_complex.in"

echo
echo "=== step 09b: load AMBER22 tools ==="
set +u                                      # amber.sh references unset vars
export PERL5LIB="${PERL5LIB:-}" PYTHONPATH="${PYTHONPATH:-}"
module load app/amber22/22
set -u
echo "AMBERHOME=${AMBERHOME:-UNSET}"
command -v tleap >/dev/null || { echo "FAIL tleap not found"; exit 1; }

echo
echo "=== step 09b: run tleap ==="
cd "$builddir"
if ! tleap -f tleap_complex.in > tleap_complex.stdout 2> tleap_complex.stderr; then
  echo "FAIL tleap returned nonzero"; echo "--- stdout tail ---"; tail -40 tleap_complex.stdout
  echo "--- log tail ---"; tail -60 tleap_complex.log 2>/dev/null || true; exit 1
fi
echo "PASS tleap completed"

echo
echo "=== step 09b: required outputs present ==="
for f in complex_dry.prmtop complex_dry.inpcrd complex_solvated.prmtop complex_solvated.inpcrd tleap_complex.log; do
  [[ -s "$f" ]] || { echo "FAIL missing/empty: $f"; exit 1; }
  echo "PASS $f ($(stat -c%s "$f") bytes)"
done

echo
echo "=== step 09b: deep prmtop/inpcrd + log audit (source of truth) ==="
python3 - "$builddir" "$admin" <<'PY'
import sys, re
from collections import Counter
from pathlib import Path

builddir, admin = Path(sys.argv[1]), Path(sys.argv[2])
audit_txt = admin / "step09b_topology_audit.txt"
res_tsv   = admin / "step09b_prmtop_residue_counts.tsv"

CHARGE_SCALE = 18.2223            # AMBER internal charge units -> e
SOLVENT = {"WAT", "HOH"}

def die(m): sys.exit("FAIL " + m)

def read_flags(path):
    flags, fmts, cur = {}, {}, None
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("%FLAG"):
            cur = line.split()[1]; flags[cur] = []
        elif line.startswith("%FORMAT"):
            fmts[cur] = line[line.find("(")+1:line.rfind(")")]
        elif line.startswith("%"):
            continue
        elif cur is not None:
            flags[cur].append(line)
    return flags, fmts

def width_of(fmt):
    m = re.match(r"\s*\d*[aAiIeEfFgG](\d+)", fmt)
    return int(m.group(1)) if m else None

def tokens(flags, fmts, name, cast):
    if name not in flags: die("prmtop missing %FLAG " + name)
    w = width_of(fmts.get(name, ""))
    out = []
    for line in flags[name]:
        if w:
            out += [line[i:i+w].strip() for i in range(0, len(line.rstrip("\n")), w) if line[i:i+w].strip()]
        else:
            out += line.split()
    return [cast(x) for x in out]

def parse_prmtop(path):
    flags, fmts = read_flags(path)
    pointers = tokens(flags, fmts, "POINTERS", int)
    natom, nres = pointers[0], pointers[11]
    names   = tokens(flags, fmts, "ATOM_NAME", str)
    charges = tokens(flags, fmts, "CHARGE", float)
    labels  = tokens(flags, fmts, "RESIDUE_LABEL", str)
    if len(names) != natom:   die("%s: ATOM_NAME %d != NATOM %d" % (path.name, len(names), natom))
    if len(charges) != natom: die("%s: CHARGE %d != NATOM %d" % (path.name, len(charges), natom))
    if len(labels) != nres:   die("%s: RESIDUE_LABEL %d != NRES %d" % (path.name, len(labels), nres))
    return {"natom": natom, "nres": nres, "total_charge": sum(charges)/CHARGE_SCALE,
            "label_counts": Counter(labels)}

def parse_inpcrd(path):
    lines = path.read_text(errors="replace").splitlines()
    natom = int(lines[1].split()[0])
    floats = []
    for line in lines[2:]:
        for tok in line.split():
            try: floats.append(float(tok.replace("D", "E")))
            except ValueError: pass
    ncoord = len(floats)
    has_box = ncoord == 3*natom + 6
    return {"natom": natom, "ncoord": ncoord, "has_box": has_box, "ok": has_box or ncoord == 3*natom}

dry_top = parse_prmtop(builddir/"complex_dry.prmtop")
dry_crd = parse_inpcrd(builddir/"complex_dry.inpcrd")
sol_top = parse_prmtop(builddir/"complex_solvated.prmtop")
sol_crd = parse_inpcrd(builddir/"complex_solvated.inpcrd")

def counts(top):
    solv = sum(v for k, v in top["label_counts"].items() if k in SOLVENT)
    na   = sum(v for k, v in top["label_counts"].items() if k in {"Na+", "NA", "Na"})
    cl   = sum(v for k, v in top["label_counts"].items() if k in {"Cl-", "CL", "Cl"})
    cha  = top["label_counts"].get("CHA", 0)
    return solv, na, cl, cha

dry_solv, dry_na, dry_cl, dry_cha = counts(dry_top)
sol_solv, sol_na, sol_cl, sol_cha = counts(sol_top)
dry_charge_int = round(dry_top["total_charge"])
sol_charge_int = round(sol_top["total_charge"])
expected_na = -dry_charge_int if dry_charge_int < 0 else 0

if not dry_crd["ok"]: die("dry inpcrd coord count %d != 3*%d" % (dry_crd["ncoord"], dry_crd["natom"]))
if not sol_crd["ok"]: die("solvated inpcrd coord count %d unexpected" % sol_crd["ncoord"])
if dry_top["natom"] != dry_crd["natom"]: die("dry prmtop/inpcrd NATOM mismatch")
if sol_top["natom"] != sol_crd["natom"]: die("solvated prmtop/inpcrd NATOM mismatch")
if dry_crd["has_box"]:     die("dry inpcrd unexpectedly has box")
if not sol_crd["has_box"]: die("solvated inpcrd missing box (6 box floats)")
if abs(dry_top["total_charge"] - dry_charge_int) > 0.01: die("dry total charge %.4f not near integer" % dry_top["total_charge"])
if abs(sol_top["total_charge"] - sol_charge_int) > 0.01: die("solvated total charge %.4f not near integer" % sol_top["total_charge"])
if sol_charge_int != 0: die("solvated system not neutral: total charge %d" % sol_charge_int)
if sol_na != expected_na: die("Na+ added %d, expected %d (=|dry charge|)" % (sol_na, expected_na))
if sol_cha != dry_cha:    die("CHA residues changed on solvation: dry %d vs solvated %d" % (dry_cha, sol_cha))
if sol_top["natom"] != dry_top["natom"] + 3*sol_solv + sol_na + sol_cl:
    die("solvated NATOM %d != dry %d + 3*%d + %dNa + %dCl" % (sol_top["natom"], dry_top["natom"], sol_solv, sol_na, sol_cl))

# ---- tleap log/stdout classification ---------------------------------------
# AMBER22 teLeap prints a bare "teLeap: Warning!" banner, then the message on the
# next line; older/other builds use inline "WARNING: <msg>". Handle both, per file
# (banner->message pairing is within a single file's line sequence).
def warn_messages(lines):
    msgs = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if re.search(r"teLeap:\s*Warning!?$", s, re.I):
            for nxt in lines[i+1:i+3]:              # message is the next non-empty, non "--" line
                t = nxt.strip()
                if t and t != "--":
                    msgs.append(t); break
        else:
            m = re.match(r"(?:WARNING|Warning)\s*[:!]\s*(.+)$", s)
            if m and len(m.group(1)) > 3:
                msgs.append(m.group(1).strip())
    return msgs

sources = []
for fn in ("tleap_complex.stdout", "tleap_complex.log", "tleap_complex.stderr"):
    p = builddir / fn
    if p.is_file():
        sources.append((fn, p.read_text(errors="replace")))
# de-dup identical files so warnings aren't counted twice (stdout==log is common)
uniq, seen = [], set()
for fn, txt in sources:
    h = hash(txt)
    if h not in seen:
        seen.add(h); uniq.append((fn, txt))

all_msgs = []
for _, txt in uniq:
    all_msgs += warn_messages(txt.splitlines())

def classify(msg):
    m = msg.lower()
    if "close contact" in m: return "close_contact"
    if "terminal residue name" in m or re.search(r"->\s*(MET|LEU|ALA|GLY|SER|THR|VAL|LYS|ARG|ASP|GLU|HI[DEP])", msg): return "terminal_rename"
    if "not zero" in m and "charge" in m: return "nonzero_charge_dry"
    if "could not find" in m or "no parameter" in m or "missing" in m: return "missing_param"
    if "unknown" in m and ("atom type" in m or "residue" in m): return "unknown_type"
    return "other"

by_cat = Counter(classify(x) for x in all_msgs)

# close-contact detail: distances + whether solute-internal (present before solvation)
combined = "\n".join(txt for _, txt in uniq).splitlines()
solv_start = next((i for i, ln in enumerate(combined)
                   if re.search(r"solvatebox|solute vdw bounding box|solvent unit box|total vdw box size|added\s+\d+\s+residues", ln, re.I)), len(combined))
box_m = re.search(r"total vdw box size:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "\n".join(combined), re.I)
box_size = "%s x %s x %s A" % box_m.groups() if box_m else "not reported"
cc_re = re.compile(r"close contact of\s+([\d.]+)\s*angstrom", re.I)
cc_atoms_re = re.compile(r"nonbonded atoms\s+(\S+)\s+and\s+(\S+)", re.I)
# A contact seen in the pre-solvation (dry) segment is solute-internal, since no
# solvent exists yet. One seen ONLY after solvation is solute-solvent. Classify
# per atom-pair so a solute-internal contact re-reported by the solvated check
# is not miscounted as solvent.
cc_reports = 0
cc_dists = []
pairs_before, pairs_after = set(), set()
for i, ln in enumerate(combined):
    m = cc_re.search(ln)
    if not m: continue
    cc_reports += 1
    cc_dists.append(float(m.group(1)))
    ap = cc_atoms_re.search(ln)
    pair = tuple(sorted((ap.group(1), ap.group(2)))) if ap else ("line", i)
    (pairs_before if i < solv_start else pairs_after).add(pair)
internal_pairs = pairs_before
solvent_pairs  = pairs_after - pairs_before
cc_unique = len(pairs_before | pairs_after)
cc_solute_internal = not solvent_pairs

# hard gate: only genuinely dangerous categories fail the build
errors = re.findall(r"\bERROR\b|Errors\s*=\s*[1-9]", "\n".join(txt for _, txt in uniq))
fatal  = [l for l in combined if "fatal" in l.lower()]
if errors or fatal or by_cat.get("missing_param") or by_cat.get("unknown_type"):
    for m in all_msgs:
        if classify(m) in ("missing_param", "unknown_type"): print("  ", m)
    die("tleap: errors/fatal/missing-parameter/unknown-type present")

cc_note = "none"
if cc_unique:
    where = "all solute-internal (present in the solvent-free dry check)" if cc_solute_internal else \
            "%d solute-internal, %d solute-solvent" % (len(internal_pairs), len(solvent_pairs))
    cc_note = "%d distinct atom pairs (%d reports), %s; min %.3f A; relaxed during restrained minimisation" % (
        cc_unique, cc_reports, where, min(cc_dists) if cc_dists else 0.0)

with res_tsv.open("w") as f:
    f.write("system\tlabel\tcount\n")
    for sysname, top in (("dry", dry_top), ("solvated", sol_top)):
        for lab, n in sorted(top["label_counts"].items()):
            f.write("%s\t%s\t%d\n" % (sysname, lab, n))

lines = [
    ("dry_prmtop_natom", dry_top["natom"]), ("dry_prmtop_nres", dry_top["nres"]),
    ("dry_inpcrd_natom", dry_crd["natom"]), ("dry_has_box", dry_crd["has_box"]),
    ("dry_total_charge", "%.4f" % dry_top["total_charge"]), ("dry_charge_int", dry_charge_int),
    ("dry_CHA_residues", dry_cha),
    ("solvated_prmtop_natom", sol_top["natom"]), ("solvated_prmtop_nres", sol_top["nres"]),
    ("solvated_inpcrd_natom", sol_crd["natom"]), ("solvated_has_box", sol_crd["has_box"]),
    ("solvated_total_charge", "%.4f" % sol_top["total_charge"]), ("solvated_charge_int", sol_charge_int),
    ("water_residues", sol_solv), ("Na_ions", sol_na), ("Cl_ions", sol_cl),
    ("solvated_CHA_residues", sol_cha), ("expected_Na_from_dry_charge", expected_na),
    ("prmtop_inpcrd_natom_match_dry", dry_top["natom"] == dry_crd["natom"]),
    ("prmtop_inpcrd_natom_match_solvated", sol_top["natom"] == sol_crd["natom"]),
    ("tleap_warnings_total", len(all_msgs)),
    ("warn_terminal_rename", by_cat.get("terminal_rename", 0)),
    ("warn_nonzero_charge_dry", "%d (expected: dry unit is %+d before addions)" % (by_cat.get("nonzero_charge_dry", 0), dry_charge_int)),
    ("warn_close_contact", cc_note),
    ("warn_other", by_cat.get("other", 0)),
    ("solvated_box_size", box_size),
    ("tleap_errors", len(errors)), ("tleap_fatal", len(fatal)),
]
audit_txt.write_text("\n".join("%s\t%s" % kv for kv in lines) + "\n")

print("  dry:       NATOM %d  NRES %d  charge %+.4f  box %s  CHA %d" % (dry_top["natom"], dry_top["nres"], dry_top["total_charge"], dry_crd["has_box"], dry_cha))
print("  solvated:  NATOM %d  NRES %d  charge %+.4f  box %s" % (sol_top["natom"], sol_top["nres"], sol_top["total_charge"], sol_crd["has_box"]))
print("  water residues (from prmtop): %d   Na+: %d (expected %d)   Cl-: %d   CHA: %d" % (sol_solv, sol_na, expected_na, sol_cl, sol_cha))
print("  prmtop<->inpcrd NATOM match: dry %s, solvated %s" % (dry_top["natom"] == dry_crd["natom"], sol_top["natom"] == sol_crd["natom"]))
print("  tleap warnings: %d total  ->  terminal-rename %d, nonzero-charge(dry) %d, close-contact %d (%d distinct pairs), other %d" % (
    len(all_msgs), by_cat.get("terminal_rename", 0), by_cat.get("nonzero_charge_dry", 0), by_cat.get("close_contact", 0), cc_unique, by_cat.get("other", 0)))
print("    close contacts: %s" % cc_note)
print("  tleap errors %d, fatal %d" % (len(errors), len(fatal)))
print("  solvated box size: %s" % box_size)
print("\n  WROTE %s" % audit_txt)
print("  WROTE %s" % res_tsv)
print("\n  RESULT: PASS - solvated topology neutral, box present, counts consistent, no tleap errors")
PY

echo
echo "=== step 09b: method note + checksums ==="
cat > "$admin/step09_method_note.txt" <<'EOF'
Step 09 method note (system build):

09a - combine: H++ protonated protein (07b) + 3 placed chorismates (step 06) into
      one pre-tleap PDB (complex_for_tleap.pdb). Counts derived, charge computed.

09b - tleap build (paper-aligned): protein ff14SB, chorismate GAFF (cha_gaff.mol2 +
      cha.frcmod, AM1-BCC charges from step 08), TIP3P water, 10 A box, neutralised
      with Na+ (addions Na+ 0). A dry topology is written first, then solvated.
      AMBER18 unavailable -> AMBER22 tools. Audit reads the prmtop/inpcrd directly
      (the solvated PDB saturates at 9999 residues); Na+ count is derived from the
      dry-system charge, not assumed. tleap warnings are classified: terminal-name
      conversions (cosmetic), the pre-neutralisation dry-charge notice (expected),
      and solute-internal close contacts from H++ hydrogen placement (relaxed by
      the first restrained minimisation). No missing-parameter or unknown-type
      warnings; no errors.
EOF
sha256sum "$builddir/complex_dry.prmtop" "$builddir/complex_dry.inpcrd" \
          "$builddir/complex_solvated.prmtop" "$builddir/complex_solvated.inpcrd" \
          "$builddir/complex_for_tleap.pdb" > "$admin/sha256_step09_tleap_build.txt"
cat "$admin/sha256_step09_tleap_build.txt"

echo
echo "STEP 09b DONE - complex_solvated.prmtop/.inpcrd ready for minimisation (step 10)"
