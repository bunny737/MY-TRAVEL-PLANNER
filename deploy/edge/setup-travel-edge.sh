#!/usr/bin/env bash
# On the pglive-worker VM (docs/deployment.md §5):
#   sudo TRAVEL_HOST=travel-web-<hash>-el.a.run.app LE_EMAIL=you@example.com EDGE_KEY=<64 hex> \
#        /opt/travel-edge/setup-travel-edge.sh
# EDGE_KEY: the same value as the travel-edge-secret secret (openssl rand -hex 32).
#
# Adds mytravelplanner.in to the VM's existing nginx WITHOUT touching PGLive's files: it writes only
# /etc/nginx/conf.d/travel.conf and /etc/nginx/travel-edge-key.conf, gets its own Let's Encrypt certificate
# (--cert-name mytravelplanner.in; HTTP-01, so both A records must already point at this VM), and reloads nginx only
# after `nginx -t` passes. A failed test leaves the running nginx (and pglive.in) exactly as it was. Re-runnable.
# Undo: rm /etc/nginx/conf.d/travel.conf /etc/nginx/travel-edge-key.conf && nginx -t && systemctl reload nginx
set -euo pipefail
: "${TRAVEL_HOST:?}" "${LE_EMAIL:?}" "${EDGE_KEY:?}"
[[ "$TRAVEL_HOST" =~ ^[a-z0-9-]+\.[a-z0-9-]+\.run\.app$ ]] || { echo "TRAVEL_HOST must be the *.run.app host" >&2; exit 1; }
[[ "$EDGE_KEY" =~ ^[a-f0-9]{64}$ ]] || { echo "EDGE_KEY must be 64 lowercase hex characters (openssl rand -hex 32)" >&2; exit 1; }
command -v nginx >/dev/null && command -v certbot >/dev/null && command -v envsubst >/dev/null \
  || { echo "nginx, certbot and envsubst are expected from PGLive's setup-edge.sh; not installing anything here." >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
CONF=/etc/nginx/conf.d/travel.conf
KEYFILE=/etc/nginx/travel-edge-key.conf
CERT=/etc/letsencrypt/live/mytravelplanner.in/fullchain.pem

apply() {  # install $1 as $CONF; keep the previous file if nginx -t fails
  local backup=""
  [[ -f "$CONF" ]] && { backup="$(mktemp)"; cp "$CONF" "$backup"; }
  cp "$1" "$CONF"
  if nginx -t; then
    systemctl reload nginx
  else
    echo "nginx -t failed: restoring the previous $CONF, nothing was reloaded." >&2
    if [[ -n "$backup" ]]; then cp "$backup" "$CONF"; else rm -f "$CONF"; fi
    exit 1
  fi
}

umask 077
printf '# Written by setup-travel-edge.sh. Do not edit by hand.\nproxy_set_header X-Travel-Edge-Key "%s";\n' "$EDGE_KEY" > "$KEYFILE"
chmod 600 "$KEYFILE"
umask 022
mkdir -p /var/www/certbot

if [[ ! -f "$CERT" ]]; then
  # Port 80 only first: the full config refers to a certificate that doesn't exist yet.
  tmp="$(mktemp)"
  awk '/^server \{/{n++} n==1{print} n==1 && /^\}/{exit}' "$HERE/travel.conf.template" > "$tmp"
  apply "$tmp"
  certbot certonly --webroot -w /var/www/certbot -d mytravelplanner.in -d www.mytravelplanner.in \
    --cert-name mytravelplanner.in --email "$LE_EMAIL" --agree-tos --non-interactive
fi
# Renewals: PGLive's /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh already reloads nginx for every certificate.

tmp="$(mktemp)"
# shellcheck disable=SC2016  # envsubst takes the variable NAME literally; only this one is replaced
TRAVEL_HOST="$TRAVEL_HOST" envsubst '${TRAVEL_HOST}' < "$HERE/travel.conf.template" > "$tmp"
apply "$tmp"
echo "Edge ready. Check: curl -sI https://mytravelplanner.in ; curl -sI https://www.pglive.in (must be unchanged)"
