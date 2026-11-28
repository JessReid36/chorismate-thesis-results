# The copy of hpc1's work onto the external drive, 27–28 November 2026

Jessica decided on 26 November that the external drive should be a complete copy of all the work on hpc1, so that
hpc1 and the PC's Downloads can be cleared. Her rule: a file on hpc1 or the PC is deleted only if it exists on the
drive. On 27 November she asked that everything not yet on the drive be copied before anything is deleted. This folder
records that copy for hpc1. **Nothing was deleted by it, on hpc1, the PC or the drive.**

## What was copied

Everything under `/home/18660916` on hpc1, except the software folders `.conda`, `envs`, `.cache` and `.local`, and
`.ssh` (keys). The drive is for PhD work only.

| batch | files on hpc1 | already on the drive | copied | archive on the drive |
|---|---:|---:|---:|---|
| 01_home_other (outside `system_development`) | 7 896 | 5 | 7 891 | `full_copy_20261127/01_home_other.tar.gz` |
| 02_sysdev_other (`system_development` apart from 04, 05, phase2.2) | 11 487 | 0 | 11 487 | `02_sysdev_other.tar.gz` |
| 03_phase2.2 | 57 756 | 44 345 | 13 411 | `03_phase2.2.tar.gz` |
| 04_qmmm_other (`05_qmmm` apart from 19 and 24) | 5 561 | 735 | 4 826 | `04_qmmm_other.tar.gz` |
| 05_qmmm_19_ensemble | 16 101 | 60 | 16 041 | `05_qmmm_19_ensemble.tar.gz` |
| 06_qmmm_24_sp_barriers | 36 092 | 1 807 | 34 285 | `06_qmmm_24_sp_barriers.tar.gz` |
| 07_amber_md | 62 | 0 | 62 | `07_amber_md.tar` |
| **in all** | **134 955 (159.8 GB)** | **46 952** | **88 003 (105.3 GB)** | |

The archive paths are relative to `chorismate-hpc-archive` on the drive. The numbers are from the printout,
`COPYHPC_printout_20261127.txt`.

## How

`COPYHPC.sh` (the block as given; the same program is in `copyhpc_as_run.py`) ran on the PC from 14:02:20 on
27 November to about 02:43 on 28 November (12 h 41 min 39 s by the terminal). Steps:

1. Every archive recorded in the repository was read on the drive. All 76 were the recorded files (sha256 and size).
2. On hpc1, the sha256 of every file in each batch was taken.
3. A file was counted as already on the drive only when its sha256 matched one of these:
   - its line in a committed manifest of a verified drive archive;
   - a loose file at the same place in the drive's archive folder;
   - a whole verified drive archive (hpc1's own archive copies).

   Each such file is listed, with where it is, in `<batch>/ON_THE_DRIVE_ALREADY.tsv`.
4. Every other file was streamed with tar (gzip -1, except 07) straight from hpc1 onto the drive.
5. The archive was then read back from the drive. Each member was hashed against the sha256 taken on hpc1, and the
   members had to be exactly the files listed for copying.
6. Only then was the archive renamed from `.part`.

Each batch's folder holds:
- `MANIFEST.sha256`: every file of the batch on hpc1, at the time of the copy
- `ON_THE_DRIVE_ALREADY.tsv`
- `COPIED.lst`: the members of the archive
- `LINKS.tsv`: symbolic links, which tar was not given
- `PC_ARCHIVES.tsv`: the archive's size, sha256 and member count
- `DONE`
- `tar_stderr.txt`

The same files are also on the drive, beside each archive.

The speed was about 0.8 to 1.2 MB/s for the compressed batches and 4.9 MB/s for 07, which was not compressed. That
compressing on hpc1's login node set the pace is likely, but it was not measured.

`INV_HPC_20261127.txt` and `INV_HPC_FILES_20261127.tsv.gz` are the read-only inventory of hpc1 taken at 13:18 on
27 November, from which the copy was planned. The inventory of the PC is not committed, because it lists personal
files in Downloads by name.

## Not done here

- The PC's Downloads: its work items not yet on the drive are copied in a later step.
- The clean-up of hpc1 (wavefunctions, scratch and hpc1's own archive copies only, as Jessica chose on 27 November),
  and of Downloads, come after that. Each deletes a file only after checking it against the drive at that moment.

Direction: none. Housekeeping; no result is read or changed.
