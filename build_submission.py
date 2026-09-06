#!/usr/bin/env python3
"""
build_submission.py - regenerate the thesis submission bundle from SUBMISSION_MANIFEST.tsv

The bundle is a BUILD ARTEFACT. Never hand-edit it. If a file needs to change,
change it in its source repo, update the manifest hash, and rebuild.

Usage
-----
  python3 build_submission.py --check
      Verify every manifest row against the source repos. Exit 1 on any mismatch.
      Run this before quoting any number in the thesis.

  python3 build_submission.py --build submission/
      Verify, then write the renamed bundle plus a generated crosswalk.

  python3 build_submission.py --rehash
      Recompute sha256 + commit for every row from the CURRENT working tree and
      rewrite the manifest. Use ONLY after deliberately updating a source file;
      review the diff before committing.

  Options:
    --repo-root DIR   parent directory holding the cloned repos (default: ..)
    --status LIST     comma-separated statuses to include (default: final)
                      e.g. --status final,superseded

Manifest columns
----------------
  thesis_name  name the file carries in the bundle and in the thesis text
  repo         'code' or 'results' (see REPO below)
  path         path within that repo
  stage        S0/S1/S2/S3/... pipeline stage; XX = quarantined
  thesis_ref   where it is cited (section, table, figure)
  status       final | superseded | omit
  commit       10-char SHA of the last commit touching the file
  sha256       full hash of the file content at that commit
  note         short human note; keep the load-bearing numbers here

Status semantics
----------------
  final       goes in the bundle; safe to cite
  superseded  development history; kept for traceability, NOT cited as a result
  omit        known-bad; listed so its absence is explicit and explained
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

REPO = {"code": "chorismate-thesis-code", "results": "chorismate-thesis-results"}
COLUMNS = ["thesis_name", "repo", "path", "stage", "thesis_ref",
           "status", "commit", "sha256", "note"]


def read_manifest(path):
    lines = Path(path).read_text().splitlines()
    header = lines[0].split("\t")
    if header != COLUMNS:
        sys.exit(f"manifest header mismatch\n  expected {COLUMNS}\n  found    {header}")
    rows = []
    for n, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        parts = line.split("\t")
        # trailing empty note is allowed
        while len(parts) < len(COLUMNS):
            parts.append("")
        if len(parts) != len(COLUMNS):
            sys.exit(f"line {n}: expected {len(COLUMNS)} columns, found {len(parts)}")
        rows.append(dict(zip(COLUMNS, parts)))
    return rows


def write_manifest(path, rows):
    out = ["\t".join(COLUMNS)]
    out += ["\t".join(r[c] for c in COLUMNS) for r in rows]
    Path(path).write_text("\n".join(out) + "\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def last_commit(repo_dir, path):
    r = subprocess.run(["git", "-C", str(repo_dir), "log", "-1", "--format=%H", "--", path],
                       capture_output=True, text=True)
    return (r.stdout.strip() or "UNKNOWN")[:10]


def resolve(root, row):
    return Path(root) / REPO[row["repo"]] / row["path"]


def verify(root, rows, statuses):
    ok, bad = [], []
    for row in rows:
        if row["status"] not in statuses:
            continue
        src = resolve(root, row)
        if not src.exists():
            bad.append((row, "MISSING", str(src)))
            continue
        actual = sha256_file(src)
        if actual != row["sha256"]:
            bad.append((row, "HASH DRIFT",
                        f"manifest {row['sha256'][:12]}... != actual {actual[:12]}..."))
            continue
        live = last_commit(Path(root) / REPO[row["repo"]], row["path"])
        if live != row["commit"] and live != "UNKNOWN":
            bad.append((row, "COMMIT MOVED",
                        f"manifest {row['commit']} != HEAD-of-file {live}"))
            continue
        ok.append(row)
    return ok, bad


def report(ok, bad):
    print(f"verified: {len(ok)}   problems: {len(bad)}")
    for row, kind, detail in bad:
        print(f"  [{kind}] {row['thesis_name']}")
        print(f"      {row['repo']}:{row['path']}")
        print(f"      {detail}")
    return len(bad) == 0


def build(root, rows, dest, statuses):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for row in rows:
        if row["status"] not in statuses:
            continue
        src = resolve(root, row)
        stage_dir = dest / row["stage"]
        stage_dir.mkdir(exist_ok=True)
        shutil.copy2(src, stage_dir / row["thesis_name"])
        written.append(row)

    lines = [
        "# Submission bundle - generated naming crosswalk",
        "",
        "GENERATED FILE. Do not edit. Produced by build_submission.py from",
        "SUBMISSION_MANIFEST.tsv. Every bundle name below resolves to an exact",
        "file at an exact commit in the source repos.",
        "",
        "| bundle name | stage | cited at | source repo | source path | commit |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(written, key=lambda r: (r["stage"], r["thesis_name"])):
        lines.append(f"| `{r['thesis_name']}` | {r['stage']} | {r['thesis_ref']} | "
                     f"{r['repo']} | `{r['path']}` | `{r['commit']}` |")

    excluded = [r for r in rows if r["status"] not in statuses]
    if excluded:
        lines += ["", "## Deliberately excluded", "",
                  "Listed so their absence is explicit rather than accidental.", "",
                  "| would-be name | status | source path | reason |", "|---|---|---|---|"]
        for r in sorted(excluded, key=lambda r: r["thesis_name"]):
            lines.append(f"| `{r['thesis_name']}` | {r['status']} | "
                         f"`{r['path']}` | {r['note']} |")

    (dest / "NAMING_CROSSWALK_GENERATED.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {len(written)} files to {dest}/ plus NAMING_CROSSWALK_GENERATED.md")


def rehash(root, rows, manifest_path):
    changed = 0
    for row in rows:
        src = resolve(root, row)
        if not src.exists():
            print(f"  skip (missing): {row['thesis_name']}")
            continue
        new_hash = sha256_file(src)
        new_commit = last_commit(Path(root) / REPO[row["repo"]], row["path"])
        if new_hash != row["sha256"] or new_commit != row["commit"]:
            print(f"  updated: {row['thesis_name']}")
            row["sha256"] = new_hash
            row["commit"] = new_commit
            changed += 1
    write_manifest(manifest_path, rows)
    print(f"rehashed {changed} row(s); review the diff before committing")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="SUBMISSION_MANIFEST.tsv")
    ap.add_argument("--repo-root", default="..")
    ap.add_argument("--status", default="final")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--build", metavar="DIR")
    ap.add_argument("--rehash", action="store_true")
    args = ap.parse_args()

    rows = read_manifest(args.manifest)
    statuses = {s.strip() for s in args.status.split(",")}

    if args.rehash:
        rehash(args.repo_root, rows, args.manifest)
        return

    ok, bad = verify(args.repo_root, rows, statuses)
    clean = report(ok, bad)

    if args.build:
        if not clean:
            sys.exit("refusing to build with unverified rows; fix or --rehash first")
        build(args.repo_root, rows, args.build, statuses)

    sys.exit(0 if clean else 1)


if __name__ == "__main__":
    main()
