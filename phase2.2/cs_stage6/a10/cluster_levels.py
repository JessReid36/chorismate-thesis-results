"""One electron in the field of the positive charges of B_n11_q0.25 alone, bare and behind a wall: the lowest
level, by diagonalising the one-electron Hamiltonian (no functional, no grid) in a large even-tempered basis of
s, p and d functions at every centre. No substrate and no negative charge is in it. A wall is a coreless core
potential at the charge: the helium and neon sets of Marefat Khah et al., written as phase2.2/cs6_exp0.py of
the code repository writes them (power 2, that is r^0; exponent; coefficient).
COMPUTED BY CLAUDE on 23 November 2026 in PySCF 2.15.1 (numpy 2.5.3, scipy 1.18.1); not ORCA, and not a result
of any diagnostic. Run:   python3 cluster_levels.py   (about a minute; it reads no file and writes none).
With the word check after it, it instead repeats one centre and one pair in a still larger basis."""
import itertools, sys, numpy as np
from pyscf import gto
EV = 27.211386245988; ANG = 0.52917721090380
SITE = {1124: (44.3597190000, 18.4491730000, 38.6355190000), 1073: (44.4024000000, 19.9187640000, 41.6024090000),
        1107: (47.2269430000, 19.6684800000, 39.7073420000), 1052: (45.9684180000, 22.3670030000, 43.1156540000),
        1359: (38.1098680000, 26.0569890000, 36.6862940000), 1005: (44.9458060000, 28.6808720000, 39.3340930000)}
ECP = {"He": "He nelec 2\nHe ul\n2 1.00000 0.00000\nHe S\n2 0.50980 2.42000\nHe P\n2 0.49165 -0.43590\n",
       "Ne": "Ne nelec 10\nNe ul\n2 1.0000 0.0000\nNe S\n2 2.0475 54.5100\nNe P\n2 0.44815 1.46500\nNe D\n2 0.49205 -0.83800\n"}
def et(hi, lo, ratio):
    out = []; e = hi
    while e > lo: out.append(e); e /= ratio
    return out
def basis(big=True):
    s = et(60.0, 0.0015, 2.0) if big else et(20.0, 0.004, 2.4)
    p = et(6.0, 0.004, 2.0) if big else et(2.0, 0.008, 2.4)
    d = et(1.5, 0.01, 2.2) if big else et(0.5, 0.02, 2.6)
    return [[0, [e, 1.0]] for e in s] + [[1, [e, 1.0]] for e in p] + [[2, [e, 1.0]] for e in d]
def larger(big=True):
    return ([[0, [e, 1.0]] for e in et(200.0, 0.0008, 1.6)] + [[1, [e, 1.0]] for e in et(20.0, 0.002, 1.7)]
            + [[2, [e, 1.0]] for e in et(5.0, 0.005, 1.8)])
def level(sites, q=0.25, wall=None, big=True, coords=None):
    """B = minus the lowest one-electron level, eV"""
    xyz = [coords[i] if coords else SITE[s] for i, s in enumerate(sites)]
    sym = wall if wall else "GHOST-H"
    mol = gto.Mole(); mol.atom = [[sym, x] for x in xyz]; mol.basis = {sym: basis(big)}; mol.unit = "Angstrom"
    if wall: mol.ecp = {wall: gto.basis.parse_ecp(ECP[wall])}
    mol.charge = -1; mol.spin = 1; mol.verbose = 0; mol.build()
    S = mol.intor("int1e_ovlp"); H = mol.intor("int1e_kin")
    for x in xyz:
        with mol.with_rinv_origin(np.array(x) / ANG):
            H = H - q * mol.intor("int1e_rinv")
    if wall:
        assert abs(mol.atom_charges()).max() == 0
        H = H + mol.intor("ECPscalar")
    w, U = np.linalg.eigh(S); keep = w > 1e-7; X = U[:, keep] / np.sqrt(w[keep])
    e = np.linalg.eigvalsh(X.T @ H @ X)
    return -e[0] * EV
if __name__ == "__main__" and sys.argv[1:] == ["check"]:
    for name, b in (("the large basis ", basis), ("a larger basis  ", larger)):
        basis = b
        print("%s one centre: bare %.4f | He wall %.4f | Ne wall %.4f" % (name, level([1124]), level([1124], 0.25, "He"), level([1124], 0.25, "Ne")))
        print("%s 1124+1073:  bare %.4f | He wall %.4f | Ne wall %.4f" % (name, level([1124, 1073]), level([1124, 1073], 0.25, "He"), level([1124, 1073], 0.25, "Ne")), flush=True)
elif __name__ == "__main__":
    print("one centre, bare, against exact 13.605693 q^2 (a check of the basis):")
    for q in (0.25, 0.50, 1.00):
        print("   q %.2f  B %.4f  exact %.4f | He wall %.4f | Ne wall %.4f" % (q, level([1124], q), 13.605693122994 * q * q, level([1124], q, "He"), level([1124], q, "Ne")))
    four = (1124, 1073, 1107, 1052)
    print("the four clustered sites, +0.25 e each: B in eV, bare | He wall | Ne wall")
    for n in (1, 2, 3, 4):
        for sub in itertools.combinations(four, n):
            b = level(list(sub)); print("   %-24s %.4f | %.4f | %.4f" % ("+".join(str(s) for s in sub), b, level(list(sub), 0.25, "He"), level(list(sub), 0.25, "Ne")), flush=True)
    six = four + (1359, 1005)
    print("   all six, smaller basis   %.4f | %.4f | %.4f" % (level(list(six), big=False), level(list(six), 0.25, "He", big=False), level(list(six), 0.25, "Ne", big=False)))
    print("   the four, smaller basis    %.4f (a check of the basis against the line of the four above)" % level(list(four), big=False))
    print("   the four, smaller basis, He wall | Ne wall   %.4f | %.4f" % (level(list(four), 0.25, "He", big=False), level(list(four), 0.25, "Ne", big=False)))
    print("   one centre, smaller basis, bare | He wall | Ne wall   %.4f | %.4f | %.4f" % (level([1124], big=False), level([1124], 0.25, "He", big=False), level([1124], 0.25, "Ne", big=False)))
