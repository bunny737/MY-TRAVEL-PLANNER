#!/usr/bin/env bash
# Download an ENCRYPTED copy of the production database to this computer (Module 07, owner decision 2026-10-25:
# Cloud SQL automated backups + a copy you download yourself; no extra bucket).
#
# The dump contains travellers' names and phone numbers. It is piped straight into gpg, so no unencrypted copy is
# ever written to disk. Keep the passphrase in your password manager: without it the backup cannot be restored.
#
# Before running:
#   1. Install the Cloud SQL Auth Proxy and sign in:  gcloud auth application-default login
#   2. In another terminal:  cloud-sql-proxy --port 6543 <project-id>:<region>:<instance-name>
#   3. Docker Desktop running (pg_dump runs in the postgres image; no local PostgreSQL install needed)
#
# Usage (from the repository root):  deploy/backup/download_backup.sh
# Then test it:                      deploy/backup/restore_check.sh backups/<file>.dump.gpg
set -euo pipefail

DB_NAME="${DB_NAME:-travel_platform}"
DB_USER="${DB_USER:-travel_app}"
PROXY_PORT="${PROXY_PORT:-6543}"
PG_IMAGE="${PG_IMAGE:-postgres:16-alpine}"   # client must be >= the Cloud SQL server version
OUT_DIR="${OUT_DIR:-backups}"
KEEP="${KEEP:-8}"                            # newest local copies to keep (about two months of weekly downloads)

command -v gpg >/dev/null || { echo "gpg is required (it ships with Git for Windows)." >&2; exit 1; }
mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR" 2>/dev/null || true
out="$OUT_DIR/${DB_NAME}-$(date +%Y%m%d-%H%M).dump.gpg"

read -r -s -p "Password for database user ${DB_USER}: " PGPASSWORD; echo
export PGPASSWORD

echo "Dumping ${DB_NAME} through the proxy on port ${PROXY_PORT}; gpg will ask for a passphrase to encrypt it."
docker run --rm -i -e PGPASSWORD "$PG_IMAGE" \
  pg_dump --host host.docker.internal --port "$PROXY_PORT" --username "$DB_USER" --dbname "$DB_NAME" \
          --format custom --no-owner --no-privileges \
  | gpg --symmetric --cipher-algo AES256 --output "$out"
unset PGPASSWORD

[[ -s "$out" ]] || { echo "Backup failed: $out is empty." >&2; rm -f "$out"; exit 1; }
echo "Saved $out ($(wc -c < "$out") bytes, encrypted)."

# Local retention: delete the oldest encrypted copies beyond KEEP (matches the privacy notice: no indefinite copies).
ls -1t "$OUT_DIR"/"${DB_NAME}"-*.dump.gpg 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do
  rm -f -- "$old" && echo "Removed old copy $old"
done
