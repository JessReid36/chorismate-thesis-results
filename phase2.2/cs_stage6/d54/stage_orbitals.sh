#!/bin/bash
# Stage 6 DIAGNOSTIC 54: puts the orbitals each run starts from into its folder as start.gbw.
# Run on hpc1 in the folder d54, which lies beside d53, before any job is submitted (block P4 runs it).
# Each file is a copy of an orbital file that a run of D53 left on hpc1, d53/<run>/job.gbw, and is
# checked against the sha256 that D53's committed HPC_MANIFEST.sha256 holds for that file, before it is
# copied and again after.
# It copies nothing over a file that is there already and changes nothing in d53.
cd "$(dirname "$0")" || exit 1
[ -f "../d53/DI6_CAM_F_d11_R/job.gbw" ] || { echo "STOP: d53/DI6_CAM_F_d11_R/job.gbw is not on hpc1. Nothing was copied."; exit 1; }
[ -f "../d53/DI6_WXV_F_d11_R/job.gbw" ] || { echo "STOP: d53/DI6_WXV_F_d11_R/job.gbw is not on hpc1. Nothing was copied."; exit 1; }
[ -f "../d53/DI6_WXV_F_d11_TS/job.gbw" ] || { echo "STOP: d53/DI6_WXV_F_d11_TS/job.gbw is not on hpc1. Nothing was copied."; exit 1; }
[ "$(sha256sum "../d53/DI6_CAM_F_d11_R/job.gbw" | cut -c1-64)" = 929c589d8d021d7c6569cee6e1b697e4101e151cb3d101f6f2a9a1a9afc75501 ] || { echo "STOP: d53/DI6_CAM_F_d11_R/job.gbw on hpc1 is not the file the committed manifest of D53 lists. Nothing was copied."; exit 1; }
[ "$(sha256sum "../d53/DI6_WXV_F_d11_R/job.gbw" | cut -c1-64)" = e151e94b4e3a67da5508bbaea9b4c31333432a004c7ab61909d182d80e3d0000 ] || { echo "STOP: d53/DI6_WXV_F_d11_R/job.gbw on hpc1 is not the file the committed manifest of D53 lists. Nothing was copied."; exit 1; }
[ "$(sha256sum "../d53/DI6_WXV_F_d11_TS/job.gbw" | cut -c1-64)" = ad828051c4a800a862c934a2d130de1b19eb7ad82f1096b940a1ba142f03dc86 ] || { echo "STOP: d53/DI6_WXV_F_d11_TS/job.gbw on hpc1 is not the file the committed manifest of D53 lists. Nothing was copied."; exit 1; }
[ -e "DI7_WXV_O_d11_R/start.gbw" ] || cp "../d53/DI6_WXV_F_d11_R/job.gbw" "DI7_WXV_O_d11_R/start.gbw" || { echo "STOP: the copy into DI7_WXV_O_d11_R failed."; exit 1; }
[ -e "DI7_WXV_O_d11_TS/start.gbw" ] || cp "../d53/DI6_WXV_F_d11_TS/job.gbw" "DI7_WXV_O_d11_TS/start.gbw" || { echo "STOP: the copy into DI7_WXV_O_d11_TS failed."; exit 1; }
[ -e "DI7_WXV_S_d11_R/start.gbw" ] || cp "../d53/DI6_CAM_F_d11_R/job.gbw" "DI7_WXV_S_d11_R/start.gbw" || { echo "STOP: the copy into DI7_WXV_S_d11_R failed."; exit 1; }
[ -e "DI7_CAM_S_d11_R/start.gbw" ] || cp "../d53/DI6_CAM_F_d11_R/job.gbw" "DI7_CAM_S_d11_R/start.gbw" || { echo "STOP: the copy into DI7_CAM_S_d11_R failed."; exit 1; }
[ -e "DI7_HF_S_d11_R/start.gbw" ] || cp "../d53/DI6_CAM_F_d11_R/job.gbw" "DI7_HF_S_d11_R/start.gbw" || { echo "STOP: the copy into DI7_HF_S_d11_R failed."; exit 1; }
sha256sum -c --quiet START_ORBITALS.sha256 || { echo "STOP: a start file is not the file the committed manifest of D53 lists. Submit nothing."; exit 1; }
echo "start orbitals: 5 files in place, each the file the committed manifest of D53 lists"
