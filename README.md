# chorismate-thesis-results

Output/data archive for the pipeline in **JessReid36/chorismate-thesis-code**
(scripts + notes live there; this repo holds the outputs, mirroring the same
`00_admin / 01_inputs / 02_preparation / 03_amber / 04_amber_md` step layout).

Files exceeding GitHub's 100 MB limit are not stored here. They are pinned by
sha256 in `CHECKSUMS_large_files.txt` and held by the author on local storage
(with independent backup) and, currently, on Stellenbosch HPC1 (Rhasatsha).

Large binaries (checksum-pinned):
- `04_amber_md/10c_production/prod.nc` — 20 ns production trajectory, 20,000 frames, 13.4 GB

Any copy can be verified against `CHECKSUMS_large_files.txt` with `sha256sum`.
