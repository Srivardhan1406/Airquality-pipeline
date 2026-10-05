#!/usr/bin/env bash
# Creates a secure data landing zone with restricted permissions.
set -euo pipefail
umask 027                                   # new files: owner rw, group r, others none

BASE="${1:-data_lake}"
mkdir -p "$BASE"/landing/raw "$BASE"/landing/archive "$BASE"/landing/quarantine logs

chmod 750 "$BASE" "$BASE/landing"           # owner rwx, group r-x, others none
chmod 770 "$BASE/landing/raw"               # ingestion writes here
chmod 750 "$BASE/landing/archive"           # read-only for group
chmod 700 "$BASE/landing/quarantine"        # owner only (suspicious/bad files)
chmod 750 logs

echo "Landing zone created:"
ls -ld "$BASE" "$BASE"/landing "$BASE"/landing/* logs
echo
echo "Permission check (expect no 'others' access):"
if find "$BASE" -type d -perm /007 | grep -q .; then echo "WARNING: world-accessible dirs"; else echo "OK - no world-accessible directories"; fi
