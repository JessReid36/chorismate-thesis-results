# Thesis submission bundle — manifest and build

## What this is

A single manifest (`SUBMISSION_MANIFEST.tsv`) that maps every thesis-facing artefact to
an exact file, at an exact commit, in one of the two source repos — plus a build script
that regenerates a renamed, verified bundle from it.

There is **no third repo of hand-copied files**. The bundle is a build artefact. If a
file needs to change, it changes in its source repo and the manifest is rehashed; the
bundle is thrown away and rebuilt. This is what keeps a number from existing in two
places and quietly diverging, which has already happened three times in this project
(`model_fidelity_validation_framework.md` stale in both repos, the `+15.771` / `+18.549`
confusion, and the Gen-2 geometries sitting inside the Gen-1 directory).

## Where it lives

Commit both files to `chorismate-thesis-results` at the repo root:

```
chorismate-thesis-results/
  SUBMISSION_MANIFEST.tsv
  build_submission.py
  SUBMISSION_README.md
```

The results repo is the right home — it is the one that already carries cross-cutting
records like `NAMING_CROSSWALK.md` and `OPTIMISER_FORK_AND_WRITEUP_SCOPE.md`.

Add `submission/` to `.gitignore`. The bundle is never committed; it is produced on
demand and, at final submission, tagged or zipped once.

## Daily use

Both repos cloned side by side under one parent directory:

```
~/thesis/
  chorismate-thesis-code/
  chorismate-thesis-results/
```

Then, from inside the results repo:

```bash
# before quoting any number in the thesis
python3 build_submission.py --check

# produce the renamed bundle
python3 build_submission.py --build submission/

# include development history for an appendix or a supervisor query
python3 build_submission.py --status final,superseded --build submission_full/

# after deliberately updating a source file
python3 build_submission.py --rehash        # then review the git diff
```

`--check` exits non-zero on any missing file, hash drift, or moved commit, so it can go
in a pre-commit hook or just be run habitually before a writing session.

## Naming convention

`<stage>_<content>_<discriminator>.<ext>`

- **stage** — `s0` geometry, `s1` single points and the Δv engine, `s2` grid
  construction, `s3` Δv on the grid, and onward as later stages settle.
  `x_` prefixes quarantined artefacts.
- **content** — what the file *is*, not which script made it: `grid`, `dvmap`,
  `singlepoint`, `refstate`.
- **discriminator** — the detail that disambiguates near-identical artefacts. This is
  the important part. `s2_grid_331pts.xyz` cannot be confused with the 326-point Gen-1
  grid or the 252-point Gen-2 grid, whereas three files all called `grid_final.xyz`
  can and did.

## Status column

| status | meaning |
|---|---|
| `final` | goes in the bundle; safe to cite |
| `superseded` | development history; kept for traceability, never cited as a result |
| `omit` | known-bad; listed so its absence is explicit and explained |

Listing the bad artefacts is the point. An examiner asking "what happened to the
252-point grid?" gets an answer from the manifest rather than silence.

## Current seed — Stage 0 to 3.1

40 rows, all verified against the repos: 31 `final`, 7 `superseded`, 2 `omit`.

Covered: substrate geometry provenance and the three 24-atom structures; the
vacuum-vs-CPCM reference-state decision; the three production single points
(reactant −836.367257939969, TS −836.339411092751 Eh → **+17.474 kcal/mol**); the
`orca_vpot` difference-potential engine and its sign check; the four grid-construction
scripts and the **331-point** grid (93/75/163 on the 2/3/4 Å shells, min spacing
1.5011 Å, Coulomb condition 8478); and the Δv map over that grid
(Δv ∈ [−0.008399, +0.009190] Eh, 212/331 sites stabilising).

Quarantined: the Gen-1 326-point grid and its Δv map (`superseded`), the Gen-2
252-point realgeom grid and Δv map (`omit`), and the stale
`phase2_charge_design/01_substrate/ts.xyz` carrying TS 2.173/2.547 (`omit`).

## Known gaps to close

1. **Gen-3 sign check has never been run.** The three-point validation exists only on
   Gen-1 (ether-O Δv = −0.012167 Eh) and Gen-2 (−0.012689 Eh) geometries. The manifest
   marks those rows `superseded` and there is currently no `final` replacement. Re-running
   `s1_dvpot_engine.sh` against the phase2b densities is a few minutes of `orca_vpot`
   and would let the thesis state the convention validation on the geometry actually used.
2. **`notes/phase2_stage2_grid_construction.md` is stale** — it describes the Gen-1
   326-point single-geometry grid, while the scripts it documents have since moved to
   the R+TS+P union envelope. Needs a rewrite against Gen 3, not a patch. Not yet in the
   manifest for that reason.
3. **`model_fidelity_validation_framework.md`** carries stale values in both repos and
   is deliberately absent from the manifest until fixed.

## Extending it

Add a row, then `--rehash` to fill in `commit` and `sha256` automatically. Keep the
load-bearing number in the `note` column — that way the manifest doubles as a one-line
index of what each artefact actually establishes, and a wrong number in the thesis can
be caught by reading the manifest rather than reopening every `.out` file.
