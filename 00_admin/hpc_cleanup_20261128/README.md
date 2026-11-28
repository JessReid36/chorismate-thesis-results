# The clean-up of hpc1, 28 November 2026

On 28 November, 42 297 bulky files were deleted from hpc1. Before any of them was deleted, an identical copy of each was
found on the external drive, in archives read that same day. This folder records that deletion.

Jessica's rule (26–27 November): a file on hpc1 or the PC is deleted only if it exists on the drive, and everything not
yet on the drive is copied first. That copy is recorded in `00_admin/hpc_full_copy_20261127` (hpc1). The copy of the
PC's Downloads was finished at 13:35 on 28 November; its records are kept off GitHub because they name personal files.

Her decision on what to delete from hpc1, 28 November (verbatim):

> both but we MUST confirm each file exists on the external before deleting..

That is, all six types below. It replaces the narrower scope (wavefunctions, scratch and hpc1's own archive copies)
named in the README of `00_admin/hpc_full_copy_20261127`. That README is not edited.

## What was deleted

| type | file names | deleted | kept |
|---|---|---:|---:|
| ORCA scratch | `*.tmp`, `*.tmp.N` | 23 123 | 0 |
| hpc1's own archive copies | `hpc_all_files_*.tar.xz` | 26 | 0 |
| wavefunctions | `*.gbw`, `*.gbwN` | 6 234 | 0 |
| densities | `*.densities`, `*.densitiesinfo` | 11 981 | 0 |
| MD trajectories | `*.nc` | 2 | 0 |
| MD restart files | `*.mdrestart` | 931 | 0 |
| **in all** | | **42 297** | **0** |

Jessica's home on hpc1 went from 170 144 167 KB to 52 146 512 KB, as measured by `du -sk` just before and just after
the deletion. That is 117 997 655 KiB, or 112.5 GiB, freed (derived).

Everything else on hpc1 was left as it was. That includes every input, every output (`.out`, `.xyz`, logs), every
script, and the software folders.

The numbers are from the printout, `CLEANHPC_printout_20261128.txt`, and from the records in this folder.

## How each file was confirmed on the drive

`CLEANHPC.sh` is the block as given; the same program is in `cleanhpc_as_run.py`. It ran on the PC from 13:46:42 to
about 14:48 on 28 November (1 h 2 min 7 s by the terminal).

- **Before starting.** It stops, with nothing deleted, unless all of these hold:
  - exactly one drive is mounted;
  - the copy of Downloads has finished (a first run at 13:13:53 stopped here, because that copy had not been run yet;
    nothing was deleted);
  - the results repository is clean, level with GitHub, and holds the records of the hpc1 copy (2d345c7f);
  - none of Jessica's jobs is in the queue on hpc1.
- **Candidates.** These are the files in the seven committed manifests of the copy
  (`00_admin/hpc_full_copy_20261127/<batch>/MANIFEST.sha256`) whose file name matches one of the six types: 42 297
  files. Each had to be listed either as copied (`COPIED.lst`) or as on the drive already
  (`ON_THE_DRIVE_ALREADY.tsv`). Of the 42 297, 13 655 had been copied on 27–28 November and 28 642 were already on the
  drive (derived from the committed records).
- **Confirmation on the drive, read today (13:46–14:13).** The drive archives holding them were read through on 28
  November, and every member was hashed:
  - all seven archives of `full_copy_20261127`;
  - 72 archives recorded earlier (`hpc_all_files_*.tar.xz`).

  Each archive's sha256, taken in the same pass, had to equal its record. A read error or a mismatch stops the
  program with nothing deleted. A candidate counts as confirmed only if its sha256 is among the members read. The
  printout says: "confirmed on the drive: 42297 of the 42297 files".
- **Unchanged on hpc1 (14:13–14:45).** Every candidate's sha256 was taken again on hpc1. A file was deleted only if
  that sha256 was unchanged since the copy and had been confirmed on the drive. Otherwise it would have been kept, with
  its reason, in `KEPT.tsv`. None was kept.
- **Deletion (14:45–14:48).** `xargs -0 rm -f --` was given the list of paths on its input; no patterns were used.
  Afterwards, `ls -d` on the same list found none of them left (`STILL_THERE.txt` is empty).

Confirmation is by content, not by name: an identical copy is on the drive.
- The column "where it is on the drive (read today)" in `DELETED.tsv` names the first archive member found with that
  content. For a file whose content occurs more than once, that member may have another path.
- The 42 297 files have 37 685 distinct contents. 109 of them are empty files (derived from the committed manifests).
- Each deleted file's own path and sha256 are in the committed manifests of the copy.

**To get a file back**, find its line in `DELETED.tsv`. The last column gives the archive (relative to
`chorismate-hpc-archive` on the drive) and the member to extract.

## Files

- `CLEANHPC.sh`, `cleanhpc_as_run.py`, `CLEANHPC_printout_20261128.txt`: the block, the program, and the printout as
  Jessica sent it.
- `TO_DELETE.tsv`: the files found confirmed and unchanged, with sha256, type and where on the drive.
- `DELETED.tsv`: the same files, after the deletion. It is identical to `TO_DELETE.tsv`, since none was left.
- `KEPT.tsv`: files not deleted, with the reason. Empty apart from its header.
- `STILL_THERE.txt`: files still on hpc1 after `rm`. Empty.
- `SUMMARY.txt`, `DONE`.
- `HPC_FILES_AFTER_20261128.lst.gz`: the files left on hpc1 in the copy's scope. That scope is every regular file under
  `/home/18660916` apart from `envs` and the files and folders at its top level whose names start with a dot. They were listed by the commit block, from hpc1,
  after the deletion. Before committing, that block checked two things: the list holds every file of the copy's
  manifests that was not deleted (92 658 expected), and it holds none of the deleted files. Its printout gives the
  counts.

## Not done here

- The clean-up of the PC's Downloads. It comes next and follows the same rule: a file is deleted only if an identical
  copy is confirmed on the drive at that moment. The items Jessica chose to leave out of the copy stay untouched.

Direction: none. Housekeeping; no result is read or changed.
