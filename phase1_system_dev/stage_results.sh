#!/usr/bin/env bash
# Generic results-staging: mirror the system_development tree into a staging dir,
# copying every useful output <= 90 MB, sha256-checksumming anything larger (too big
# for GitHub -> Zenodo), and skipping antechamber scratch / .bak / empty / junk.
# Reusable for every step. Only writes into $stage.
set -euo pipefail
src="${1:-$HOME/system_development}"
stage="${2:-$HOME/system_development/00_admin/results_staging}"
capB=$((90*1024*1024))
rm -rf "$stage"; mkdir -p "$stage"
big="$stage/CHECKSUMS_large_files.txt"; : > "$big"
man=0; bg=0; sk=0
while IFS= read -r -d '' f; do
  rel="${f#$src/}"; base="$(basename "$f")"
  case "$base" in
    *.bak|core|core.*|*.tmp|*.swp|.DS_Store|ANTECHAMBER_*|ATOMTYPE.INF) sk=$((sk+1)); continue;;
  esac
  [[ -s "$f" ]] || { sk=$((sk+1)); continue; }
  sz=$(stat -c%s "$f")
  if (( sz > capB )); then
    ( cd "$src" && sha256sum "$rel" ) >> "$big"; bg=$((bg+1))
  else
    mkdir -p "$stage/$(dirname "$rel")"; cp -f "$f" "$stage/$rel"; man=$((man+1))
  fi
done < <(find "$src" -type d -name "$(basename "$stage")" -prune -o -type f -print0)
echo "staged (<=90MB): $man   checksummed (>90MB): $bg   skipped junk: $sk"
echo "--- large-file checksums (for Zenodo) ---"; cat "$big"
echo "staging dir: $stage"
