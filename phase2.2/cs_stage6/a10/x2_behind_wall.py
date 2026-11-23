"""One electron at the positive charges of B_n11_q0.25, bare and behind a wall, IN THE FUNCTIONS A DIANION RUN CARRIES:
set X2 or X3 (the def2-TZVPD functions of hydrogen plus s and p functions of exponents 0.035, 0.012 and, in X3, 0.004)
at ghost centres 0.01 A beyond each charge, read from a committed input of D50. Against the large-basis level of
cluster_levels.py. For one electron Hartree-Fock is the lowest eigenvalue in the basis, so nothing is iterated.
"own": functions at the charged sites only. "six": functions at all six positive sites of the design.
COMPUTED BY CLAUDE on 23 November 2026 in PySCF 2.15.1; not ORCA, and not a result of any diagnostic.
Run from the top of the results repository:   python3 -B phase2.2/cs_stage6/a10/x2_behind_wall.py"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cluster_levels as c
from pyscf import gto
INP = os.path.join(HERE, "..", "d50", "CAMTZX_B_n11_q0.25_X2A_di_R", "job.inp")
gh = [tuple(map(float, l.split()[1:4])) for l in open(INP).read().split("\n") if l.startswith("H:")]
order = [1124, 1073, 1107, 1359, 1005, 1052]; GH = dict(zip(order, gh))
for s in order: assert abs(np.linalg.norm(np.array(GH[s]) - np.array(c.SITE[s])) - 0.01) < 2e-4, s
ADD = {"X2": (0.035, 0.012), "X3": (0.035, 0.012, 0.004)}
def fb(name): return gto.basis.load("def2-tzvpd", "H") + [[0, [e, 1.0]] for e in ADD[name]] + [[1, [e, 1.0]] for e in ADD[name]]
def level(charged, ghosts, fset, wall=None, q=0.25):
    atoms = [["GHOST-H", GH[s]] for s in ghosts]; basis = {"GHOST-H": fb(fset)}
    if wall:  # the wall centre needs a function in PySCF; one so tight that the lowest level cannot use it
        atoms += [[wall, c.SITE[s]] for s in charged]; basis[wall] = [[0, [1.0e7, 1.0]]]
    mol = gto.Mole(); mol.atom = atoms; mol.basis = basis; mol.unit = "Angstrom"
    if wall: mol.ecp = {wall: gto.basis.parse_ecp(c.ECP[wall])}
    mol.charge = -1; mol.spin = 1; mol.verbose = 0; mol.build()
    S = mol.intor("int1e_ovlp"); H = mol.intor("int1e_kin")
    for s in charged:
        with mol.with_rinv_origin(np.array(c.SITE[s]) / c.ANG): H = H - q * mol.intor("int1e_rinv")
    if wall: H = H + mol.intor("ECPscalar")
    w, U = np.linalg.eigh(S); keep = w > 1e-7; X = U[:, keep] / np.sqrt(w[keep])
    return -np.linalg.eigvalsh(X.T @ H @ X)[0] * c.EV
if __name__ == "__main__":
    arr = [("1124", [1124]), ("1124+1073", [1124, 1073]), ("the four", [1124, 1073, 1107, 1052]), ("all six", order)]
    print("B in eV, charges of +0.25 e. limit: the large basis of cluster_levels.py (all six: its smaller basis). In brackets: minus the limit.")
    for wall in (None, "He", "Ne"):
        for name, ch in arr:
            lim = c.level(ch, 0.25, wall, big=(len(ch) < 6))
            r = [level(ch, g, f, wall) for f in ("X2", "X3") for g in (ch, order)]
            print("%-5s %-10s limit %.4f | X2 own %.4f (%+.4f) six %.4f (%+.4f) | X3 own %.4f (%+.4f) six %.4f (%+.4f)" % (
                wall or "bare", name, lim, r[0], r[0] - lim, r[1], r[1] - lim, r[2], r[2] - lim, r[3], r[3] - lim), flush=True)
