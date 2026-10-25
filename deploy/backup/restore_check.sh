#!/usr/bin/env bash
# Prove a backup can be restored (Module 07 / CLAUDE.md invariant 10: "daily DB backup with a tested restore").
#
# Decrypts the file, restores it into a throwaway database "restore_check" in the LOCAL Docker Postgres (port 5440),
# runs the app's migration check against it, prints row COUNTS only (never names or phone numbers), then drops it.
#
# Usage (from the repository root, with `docker compose up -d db` running):
#   deploy/backup/restore_check.sh backups/travel_platform-YYYYMMDD-HHMM.dump.gpg
set -euo pipefail

file="${1:?usage: $0 <backup .dump.gpg file>}"
[[ -s "$file" ]] || { echo "No such backup: $file" >&2; exit 1; }
SCRATCH=restore_check
psql_db() { docker compose exec -T db psql -U postgres -v ON_ERROR_STOP=1 "$@"; }

cleanup() { psql_db -d postgres -qc "DROP DATABASE IF EXISTS $SCRATCH" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "==> Restoring $file into the local scratch database '$SCRATCH' (gpg will ask for the passphrase)"
cleanup
psql_db -d postgres -qc "CREATE DATABASE $SCRATCH"
gpg_opts=(--decrypt --quiet)
# Optional, for unattended checks: a file holding the passphrase (keep it outside the repo, readable only by you).
[[ -n "${GPG_PASSPHRASE_FILE:-}" ]] && gpg_opts+=(--batch --pinentry-mode loopback --passphrase-file "$GPG_PASSPHRASE_FILE")
gpg "${gpg_opts[@]}" "$file" | docker compose exec -T db pg_restore -U postgres --dbname "$SCRATCH" --no-owner --no-privileges --exit-on-error

echo "==> Row counts (no personal data is printed)"
psql_db -d "$SCRATCH" -At -F ' ' -c "
  SELECT 'leads', count(*) FROM core_lead
  UNION ALL SELECT 'partners', count(*) FROM core_partner
  UNION ALL SELECT 'content pages', count(*) FROM core_contentpage
  UNION ALL SELECT 'admin users', count(*) FROM auth_user
  UNION ALL SELECT 'authenticators', count(*) FROM otp_totp_totpdevice;"
psql_db -d "$SCRATCH" -At -c "SELECT 'newest lead: ' || coalesce(to_char(max(created_at), 'YYYY-MM-DD HH24:MI'), 'none') FROM core_lead"

echo "==> Checking the restored schema matches the code (no missing migrations)"
docker compose run --rm -T -e DB_NAME="$SCRATCH" -e DB_USER=postgres \
  -e DB_PASSWORD="${POSTGRES_ADMIN_PASSWORD:-postgres}" web python manage.py migrate --check --noinput

echo "Restore check passed. The scratch database is dropped now."
