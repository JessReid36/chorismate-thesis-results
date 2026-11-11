#!/usr/bin/env python3
"""Completeness pass 2 (by name) for WRITEUP_CONSOLIDATED_20261110.md.

    python3 sweep_pass2.py --res <results repo> --code <code repo> --out <this directory>

Searches ALL committed text in both repositories - loose files, single .xz files and every member of every
committed tar archive (extracted to a temporary directory) - for each name on a deliberately broad list of
functionals, wavefunction and semi-empirical methods, basis sets, corrections, charge schemes, force fields and
programs, and records in which KIND of file each occurs:

    n_input_files    ORCA inputs (anywhere in the file)
    n_output_files   output files (anywhere: banner, citations, tables, the input echo)
    n_script_files   .py .sh .pbs
    n_doc_files      every other text file

and joins that to T1b_keyword_tokens.tsv, pass 1's count of files carrying the name ON A KEYWORD LINE.
A name with keyword counts of zero was never asked for by an ORCA keyword line.  A name that occurs only in
output files is the ORCA-banner trap.  A name in scripts or documents with no keyword line needs a human
reading of the example path: it may be a list of names inside a parser, a literature discussion, a default
that a keyword implies (TPSS/def2-TZVP under !FOD), an ECP named in an input block (SDD), or work done in
another program (pyscf, sqm, sander).  Needs grep with -P (PCRE); about four minutes; 6 GB of scratch.
"""
import argparse, collections, lzma, os, re, shutil, subprocess, sys, tarfile, tempfile

CI = """
B3LYP CAM-B3LYP wB97X-D3 wB97X-D3BJ wB97X-D wB97X-D4 wB97X-V wB97M-V wB97M-D3BJ wB97X wB97X-3c
M06-2X M06-L M06 M05-2X M08-HX MN15 PBE0 BP86 BLYP TPSSh TPSS revPBE B97-D3 B97-D B97-3c B97M-V
r2SCAN-3c r2SCAN PBEh-3c HF-3c B2PLYP B2GP-PLYP DSD-BLYP DSD-PBEP86 LC-wPBE LC-BLYP LC-PBE BHandHLYP BHLYP
X3LYP O3LYP PW6B95 HSE06 B3PW91 B3P86 mPW1PW91 MPW1K MPWB1K PWPB95 revDSD-PBEP86 wB2PLYP
RI-MP2 SCS-MP2 SOS-MP2 DLPNO-MP2 MP2 MP3 MP4 CCSD(T) CCSD DLPNO-CCSD(T) DLPNO-CCSD CASSCF CASPT2 NEVPT2
QCISD(T) CBS-QB3 G3B3 G4 W1 CBS
PM3 PM6 PM7 RM1 AM1-BCC AM1 MNDO OM2 OM3 DFTB3 DFTB SCC-DFTB GFN2-xTB GFN1-xTB GFN-FF GFN2 GFN1 XTB2 XTB1 xtb EVB
def2-SVP def2-SVPD def2-SV(P) def2-TZVP def2-TZVPP def2-TZVPD def2-TZVPPD def2-QZVP def2-QZVPP def2-QZVPD def2-QZVPPD
ma-def2-SVP ma-def2-TZVP ma-def2-TZVPP ma-def2-QZVPP def2-mSVP def2-mTZVP def2/J def2/JK def2-SVP/C def2-TZVP/C def2-TZVPP/C AutoAux
6-31G(d) 6-31G* 6-31G** 6-31G(d,p) 6-31+G(d) 6-31+G* 6-31+G** 6-31+G(d,p) 6-31++G(d,p) 6-31++G** 6-311G(d,p) 6-311G**
6-311+G(d,p) 6-311+G** 6-311++G(d,p) 6-311++G** 6-311+G(2d,p) 6-311+G(2df,2p) 6-311+G(3df,2p) 6-31G 6-311G 3-21G STO-3G MINIX vDZP
cc-pVDZ cc-pVTZ cc-pVQZ cc-pV5Z aug-cc-pVDZ aug-cc-pVTZ aug-cc-pVQZ aug-cc-pV5Z jun-cc-pVDZ jun-cc-pVTZ jul-cc-pVDZ
pcseg-1 pcseg-2 aug-pcseg-1 def2-SD def2-ECP SDD LANL2DZ HayWadt CRENBL Stuttgart
D3BJ D3ZERO D3(BJ) D3(0) gCP VV10 RIJCOSX RIJK RIJONX COSX
CPCM C-PCM SMD COSMO-RS COSMO ALPB GBSA IEFPCM IEF-PCM PCM ddCOSMO Poisson-Boltzmann
NEB-TS NEB-CI CI-NEB OptTS NumFreq StabPerform LevelShift SlowConv VerySlowConv TRAH KDIIS SOSCF TightSCF VeryTightSCF
CHELPG RESP Hirshfeld Loewdin Löwdin Lowdin Mulliken NBO MBIS Merz-Kollman
ORCA AmberTools Amber sander pmemd cpptraj tleap antechamber parmchk2 Psi4 Gaussian16 Gaussian09 Q-Chem Multiwfn OpenMM GROMACS CHARMM NAMD
Knarr geomeTRIC Gurobi HiGHS PuLP SCIP CPLEX OR-Tools CP-SAT scipy numpy RDKit propka PDB2PQR GOCAT DTSS GdMC Rosetta AlphaFold RFdiffusion
PyMOL orca_vpot orca_2mkl orca_plot Molpro Turbomole NWChem CP2K ChemShell DL_POLY Tinker MOPAC DFTB+ PySCF
ff14SB ff19SB ff99SB GAFF2 GAFF TIP3P TIP4P SPC/E UFF Lennard-Jones
pseudopotential NewECP Gaussian-smeared smeared erf-damped Thole GEEP blurred ghost
QM/MM ONIOM electrostatic-embedding mechanical-embedding polarizable-embedding
"""
# short or ambiguous names: matched case-sensitively
CS = """
HF UHF RHF ROHF RI NL D3 D4 ASH OPC MK ESP SCAN PBE CBC PCM NEB IRC FOD ECP sqm MD MM LJ MP2 DFT
"""


SKIP = (".gbw", ".densities", ".npz", ".png", ".svg", ".docx", ".rst7", ".prmtop", ".inpcrd", ".pdf", ".hess", ".densitiesinfo",
        ".cpcm", ".cpcm_corr", ".xyz", ".pc", ".pdb", ".mol2", ".interp", ".xz", ".gz", ".tar", ".engrad", ".opt", ".nc", ".dcd")


OWN = re.compile(r"^phase2\.2/(cs_stage6/(WRITEUP_CONSOLIDATED_\d{8}\.md|figures/.*)|cs_writeup_check\.py)$")


def cls(p):
    l = p.lower()
    if l.endswith(".out"):
        return "output"
    if l.endswith(".inp"):
        return "input"
    if l.endswith((".py", ".sh", ".pbs", ".rejected")):
        return "script"
    return "doc"


def extract(repo, dest):
    files = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
    for f in sorted(x for x in files if x):
        full = os.path.join(repo, f)
        if f.endswith((".tar.xz", ".tar.gz", ".tgz", ".tar")):
            with tarfile.open(full, "r:*") as tf:
                for m in tf:
                    if not m.isfile():
                        continue
                    data = tf.extractfile(m).read()
                    name = m.name.lstrip("./")
                    if name.endswith(".xz"):
                        try:
                            data = lzma.decompress(data)
                            name = name[:-3]
                        except Exception:
                            continue
                    if b"\0" in data[:4096]:
                        continue
                    p = os.path.join(dest, f + "__members", name)
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    with open(p, "wb") as fh:
                        fh.write(data)
        elif f.endswith(".xz"):
            try:
                with open(full, "rb") as fh:
                    data = lzma.decompress(fh.read())
            except Exception:
                continue
            if b"\0" in data[:4096]:
                continue
            p = os.path.join(dest, f[:-3])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    self_dir = os.path.abspath(a.out)
    ci = sorted(set(CI.split()), key=lambda s: (-len(s), s))
    cs = sorted(set(CS.split()), key=lambda s: (-len(s), s))
    pat = r"(?<![A-Za-z0-9])(?:(?i:" + "|".join(re.escape(n) for n in ci) + ")|" + "|".join(re.escape(n) for n in cs) + r")(?![A-Za-z0-9])"
    canon = {n.lower(): n for n in ci}
    tmp = tempfile.mkdtemp(prefix="cswu_p2_")
    try:
        extract(a.res, tmp)
        lists = []
        for repo, tag in ((a.res, "results"), (a.code, "code")):
            fs = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
            for f in fs:
                if not f or f.lower().endswith(SKIP):
                    continue
                full = os.path.abspath(os.path.join(repo, f))
                if full.startswith(self_dir + os.sep) or OWN.match(f):
                    continue                      # this write-up's own files are not evidence about the record
                lists.append((full, tag + ":" + f))
        for dp, dn, fn in os.walk(tmp):
            for f in fn:
                full = os.path.join(dp, f)
                if not f.lower().endswith(SKIP):
                    lists.append((full, "results(archived):" + os.path.relpath(full, tmp)))
        label = dict(lists)
        flist = os.path.join(tmp, "__files.txt")
        with open(flist, "w") as fh:
            fh.write("\0".join(p for p, _ in lists))
        counts = collections.defaultdict(collections.Counter)
        ex = collections.defaultdict(lambda: collections.defaultdict(list))
        proc = subprocess.Popen(["xargs", "-0", "-a", flist, "-n", "400", "grep", "-P", "-o", "-H", "-I", "--no-messages", "-e", pat],
                                stdout=subprocess.PIPE, text=True, errors="replace")
        seen = set()
        for line in proc.stdout:
            line = line.rstrip("\n")
            k = line.rfind(":")
            path, m = line[:k], line[k + 1:]
            name = canon.get(m.lower(), m)
            if (path, name) in seen:
                continue
            seen.add((path, name))
            c = cls(path)
            counts[name][c] += 1
            ex[name][c].append(label.get(path, path))
        proc.wait()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tok = {}
    with open(os.path.join(a.out, "T1b_keyword_tokens.tsv")) as fh:
        for l in fh:
            if l.startswith("#") or l.startswith("token"):
                continue
            t, i, o = l.rstrip("\n").split("\t")
            tok[t] = (int(i), int(o))
    classes = ["input", "output", "script", "doc"]
    with open(os.path.join(a.out, "T2_names.tsv"), "w", newline="\n") as f:
        f.write("# Pass 2. Every name on sweep_pass2.py's list, with the number of committed files of each kind in which it occurs,\n")
        f.write("# and (kw_*) the number of ORCA keyword lines carrying it, from pass 1. %d files searched for %d names.\n"
                % (len(lists), len(set(ci) | set(cs))))
        f.write("# example: the first path, in sorted order, of each kind in which the name occurs.\n")
        f.write("name\tkw_input_files\tkw_output_echoes\tn_input_files\tn_output_files\tn_script_files\tn_doc_files\texample\n")
        for n in sorted(set(ci) | set(cs), key=lambda s: (s.lower(), s)):
            kw = tok.get(n.upper(), (0, 0))
            e = "; ".join("%s: %s" % (c, sorted(ex[n][c])[0]) for c in classes if ex[n][c])
            f.write("%s\t%d\t%d\t%s\t%s\n" % (n, kw[0], kw[1], "\t".join(str(counts[n][c]) for c in classes), e))
    print("files searched: %d; names on the list: %d; found somewhere: %d" % (len(lists), len(set(ci) | set(cs)),
          sum(1 for n in counts if sum(counts[n].values()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
