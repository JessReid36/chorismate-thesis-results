The PC archive of hpc1's outputs now lives on an external drive - the move of 20 November 2026, the
check of every archive against the committed records, and the clean-up of D44 that followed

21 November 2026. A dated note. It edits no committed record, and nothing is run because of it.


1. WHAT CHANGED

The rule (Jessica, 18 October 2026, as phase2.2/cs_stage6/d47/README.txt carries it): "every output
file of a finished job is downloaded and kept as a physical file, not only reported." The physical
files are one hpc_all_files_<name>.tar.xz per collection, kept in an archive folder outside this
repository and recorded here by size and sha256 in a PC_ARCHIVES.tsv beside the outputs.

Until 20 November 2026 that folder was /home/jess/Desktop/chorismate-hpc-archive on Jessica's PC.
From 20 November 2026 it is the folder chorismate-hpc-archive on Jessica's external drive, which
her PC mounts at /media/jess/KIOXIA (exfat), so: /media/jess/KIOXIA/chorismate-hpc-archive.

The decision is Jessica's, 20 November 2026. Of the drive: "wait no i dont want to move apps and
that.... this external is for my phd work." Asked what should move to it, she chose "HPC archive
lives on drive": the archive folder moves to the drive and later collections download straight to
it.

WHAT FOLLOWS FROM IT
   The drive must be plugged in for every collection. Nothing is left on the Desktop under the old
   name (the printout of section 2: "the old archive folder on the Desktop: gone, as it should
   be"), so that a collection which is not pointed at the drive stops instead of writing
   somewhere else.
   23 of the 25 PC_ARCHIVES.tsv files in this repository name the Desktop folder in their first
   line. They were true when written and are not edited. Read with this note, the path after
   "relative to the archive folder" now starts at the drive's folder. The two written since, d44's
   and d47's, name the drive's folder themselves.
   The archive exists in ONE place, as before: then the PC, now the drive. A second copy is
   Jessica's decision and has not been made.


2. THE CHECK OF 20 NOVEMBER 2026, 22:04 (block ARCHCHECK; it only read)

It read every PC_ARCHIVES.tsv in the working tree of this repository at 4bd02c33 (24 files, 61
records), took the sha256 of every .tar.xz under the drive's archive folder, and matched record to
file by size and sha256. As printed (PRINTOUT_ARCHCHECK_CLEANPC_CLEANHPC_20261120.txt):

   "3. On the drive: 61 archives (.tar.xz), 14887 MB; 5246 other files, 3835 MB"
   "the same file, at the recorded place: 57"
   "the same file, under another name: 4"
   "NOT matched: 0"
   "5. Archives on the drive that no record names: 0"
   "6. D44: its archive on the drive is the committed one, sha256 13d9a5ec1d5e5a43..."

So every archive this repository records is on the drive with the recorded size and sha256, and
the drive holds no archive that the repository does not record.

THE FOUR UNDER ANOTHER NAME. Four committed records print a path that holds the literal text $NAME,
a shell variable that was not filled in when the record was written. The files are the recorded
ones, by size and sha256; only the name in the record is wrong. The records are not edited. The
files are called:

   record (as committed)                                     the file in the archive folder
   phase2.2/cs_stage6/negatives/hpc_all_files_$NAME.tar.xz       .../negatives/hpc_all_files_negatives.tar.xz
      133381072 bytes   07d317ac52fa7f1992c2ccf09284fa533148cc9114ff1e1c858576fee9b89363
   phase2.2/cs_stage6/negatives_armA/hpc_all_files_$NAME.tar.xz  .../negatives_armA/hpc_all_files_negatives_armA.tar.xz
      67568284 bytes    658baa4813e2095a3644fac0aba7a7f6ddc524b6a56db6d0c09e68cd6a9e10dc
   phase2.2/cs_stage6/d16/hpc_all_files_$NAME.tar.xz             .../d16/hpc_all_files_d16.tar.xz
      384650988 bytes   a7454f9adf4f323198e82aca20c089f9385682355164e7e48b02d09750719850
   phase2.2/cs_stage6/d17/hpc_all_files_$NAME.tar.xz             .../d17/hpc_all_files_d17.tar.xz
      46814916 bytes    3f98590df339b36a2db6ba91bd3e505f01c8c6c50a735ed877e7fe678ec22ac8

WHAT THE CHECK DID NOT COVER
   The 5246 files in the archive folder that are not .tar.xz (3835 MB). ARCHCHECK counted them and
   compared them with nothing.
   The copying itself. The blocks that copied the folder to the drive and removed the original from
   the PC ran on 20 November 2026; their printouts are not in this folder. What stands here in
   their place is the comparison above, which was made on the drive after the move.
   D47's archive, which did not exist yet (section 4).

The printout also reports two things that are not part of this repository's record: a folder of
Jessica's own, attempt_3_final_analysis, is on the drive and no longer in Downloads; and a left-over
folder moved_from_pc_20261120 is on the drive and is not needed.


3. THE CLEAN-UP OF D44, 20 NOVEMBER 2026, 22:06 TO 22:25 (blocks CLEANPC and CLEANHPC)

The precedent is 00_admin/hpc_cleanup_20261007/README.txt: the sha256 of every file recorded before
any deletion, and deleted "only files in delete.tsv whose sha256 still matched the record". For D44
the record is the committed phase2.2/cs_stage6/d44/HPC_MANIFEST.sha256, and INVENTORY.tsv says
which files are kept only in the archive.

ON THE PC (CLEANPC). First the archive on the drive was read again and its sha256 compared with the
committed one, 13d9a5ec1d5e5a4380dff7286a3ebf5f1ca360eaaf5f4eff9acb6d28e9b17988. Then the unpacked
copy that the collection had used for its checks, /home/jess/Downloads/cs_d44_harvest_work/x, was
removed. As printed: "the unpacked check copy takes 20008M", "free on this PC now: 28176 MB".

ON hpc1 (CLEANHPC). The files to clear were the lines of the committed manifest that lie directly
inside a run folder and are not job.inp, job.out, job.property.txt, pc.pc or substrate.xyz: 9045
files, the ones d44/INVENTORY.tsv marks as kept only in the archive (ORCA's scratch and restart
files, wavefunctions and densities). Each was compared with the manifest by sha256 before any was
deleted. Then the copy of the archive on hpc1 was compared with the committed
sha256 and deleted. As printed:

   "deleted 9045 files, every one checked against the manifest first"
   "deleted the archive on hpc1; the same file is on your drive"
   "files left in d44 on hpc1: 968 (968 expected: the inputs and the text outputs, all in the repository)"
   "d44 on hpc1 now takes 23M"

SINCE THEN the wavefunctions, densities and scratch files of D44 exist only inside the archive on
the drive: ONE COPY. Its inputs and text outputs are on hpc1, on the PC and in this repository.


4. D47, 21 NOVEMBER 2026

D47's collection wrote its archive straight to the drive. phase2.2/cs_stage6/d47/PC_ARCHIVES.tsv:
phase2.2/cs_stage6/d47/hpc_all_files_d47.tar.xz, 681388672 bytes, sha256
1adfd88bcce4209670f111a1fb537102b9f4b3c8dcef6e15f28ce599746a14d8, 1378 members. The collection
checked it against hpc1's copy and every member against the manifest (d47/README.txt). ARCHCHECK ran
before it and does not cover it. At the time of this note nothing of D47 has been cleared from
hpc1: by d47/INVENTORY.tsv, 1082 files (1166.9 MB) that are kept only in the archive, and the copy
of the archive, are still there.


5. THE FILES IN THIS FOLDER

   PRINTOUT_ARCHCHECK_CLEANPC_CLEANHPC_20261120.txt
      Jessica's terminal, as she sent it on 21 November 2026: the three blocks and what they
      printed. Her shell folded each pasted command, so the capture shows only the first and last
      lines of each. Not edited.
   blocks/ARCHCHECK.sh, blocks/CLEANPC.sh, blocks/CLEANHPC.sh
      The three blocks as Claude gave them in the chat on 20 November 2026. Every line of a command
      that the capture shows is a line of these files; the folded lines cannot be compared. They
      were written for that evening and carry its literals (D44's sha256, the count 9045). They are
      here as a record of what ran, not to be run again.
