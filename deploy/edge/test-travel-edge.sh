#!/usr/bin/env bash
# Proves travel.conf can sit beside PGLive's real edge config on the VM's nginx version (1.22) without changing it:
# both load together, pglive.in still answers as before, unknown hosts still get nothing, and mytravelplanner.in
# redirects and forwards the right headers (client-sent X-Forwarded-For / edge key are overwritten).
#   PG_EDGE_DIR=../PG-MANAGEMENT-WEB/infra/edge deploy/edge/test-travel-edge.sh   (needs docker; ~15 s)
set -euo pipefail
export MSYS2_ARG_CONV_EXCL='*'    # Git Bash on Windows: pass container:path arguments through untouched
hp() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else echo "$1"; fi; }
HERE="$(cd "$(dirname "$0")" && pwd)"
PG_EDGE_DIR="${PG_EDGE_DIR:-$HERE/../../../PG-MANAGEMENT-WEB/infra/edge}"
IMAGE="${NGINX_IMAGE:-nginx:1.22-alpine}"
NAME="travel-edge-test-$$"
HTTPS="${TEST_PORT:-18444}"; HTTP="${TEST_HTTP_PORT:-18081}"
KEY="$(printf 'ab%.0s' {1..32})"
WORK="$(mktemp -d)"
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; rm -rf "$WORK"; }
trap cleanup EXIT
[[ -f "$PG_EDGE_DIR/pglive.conf.template" ]] || { echo "PGLive edge files not found in $PG_EDGE_DIR" >&2; exit 1; }

# PGLive's files, rendered the way its setup-edge.sh does (upstreams are a closed port: its hosts answer 502).
mkdir -p "$WORK/snippets"
cat > "$WORK/snippets/pglive-tls.conf" <<'EOF'
ssl_certificate     /etc/letsencrypt/live/pglive.in/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/pglive.in/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_session_cache shared:pglive_tls:10m;
add_header Strict-Transport-Security "max-age=300" always;
EOF
cat > "$WORK/snippets/pglive-proxy.conf" <<'EOF'
proxy_pass https://$upstream_host;
proxy_ssl_server_name on;
proxy_set_header Host $upstream_host;
proxy_connect_timeout 2s;
EOF
printf '"testkey" 1;\n' > "$WORK/edge-key.map"
printf 'allow all;\n' > "$WORK/admin-allow.conf"
sed -e 's|\${API_HOST}|127.0.0.1:9|g' -e 's|\${WEB_HOST}|127.0.0.1:9|g' "$PG_EDGE_DIR/pglive.conf.template" > "$WORK/pglive.conf"

# Ours, with an echo server as the "Cloud Run" upstream so the forwarded headers can be read back.
sed -e 's|\${TRAVEL_HOST}|127.0.0.1:8443|g' "$HERE/travel.conf.template" > "$WORK/travel.conf"
printf 'proxy_set_header X-Travel-Edge-Key "%s";\n' "$KEY" > "$WORK/travel-edge-key.conf"
cat > "$WORK/zz-echo.conf" <<'EOF'
server {
    listen 127.0.0.1:8443 ssl;
    ssl_certificate     /etc/letsencrypt/live/pglive.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pglive.in/privkey.pem;
    return 200 "host=$http_host xfh=$http_x_forwarded_host xff=$http_x_forwarded_for proto=$http_x_forwarded_proto key=$http_x_travel_edge_key uri=$request_uri\n";
}
EOF

docker create --name "$NAME" -p "$HTTPS:443" -p "$HTTP:80" --entrypoint sh "$IMAGE" -c '
  apk add --no-cache openssl >/dev/null 2>&1 &&
  for d in pglive.in mytravelplanner.in; do mkdir -p /etc/letsencrypt/live/$d &&
    openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=$d" \
      -keyout /etc/letsencrypt/live/$d/privkey.pem -out /etc/letsencrypt/live/$d/fullchain.pem 2>/dev/null; done &&
  rm -f /etc/nginx/conf.d/default.conf && nginx -t && exec nginx -g "daemon off;"' >/dev/null
docker cp "$(hp "$WORK/pglive.conf")" "$NAME:/etc/nginx/conf.d/pglive.conf"
docker cp "$(hp "$PG_EDGE_DIR/limits.conf")" "$NAME:/etc/nginx/conf.d/00-pglive-limits.conf"
docker cp "$(hp "$WORK/snippets")" "$NAME:/etc/nginx/"
docker cp "$(hp "$WORK/edge-key.map")" "$NAME:/etc/nginx/pglive-edge-key.map"
docker cp "$(hp "$WORK/admin-allow.conf")" "$NAME:/etc/nginx/pglive-admin-allow.conf"
docker cp "$(hp "$WORK/travel.conf")" "$NAME:/etc/nginx/conf.d/travel.conf"
docker cp "$(hp "$WORK/travel-edge-key.conf")" "$NAME:/etc/nginx/travel-edge-key.conf"
docker cp "$(hp "$WORK/zz-echo.conf")" "$NAME:/etc/nginx/conf.d/zz-echo.conf"
docker start "$NAME" >/dev/null

get() { curl -sk --max-time 5 --resolve "$1:$HTTPS:127.0.0.1" "${@:3}" "https://$1:$HTTPS$2"; }
for _ in $(seq 1 60); do get www.pglive.in / >/dev/null && break; sleep 0.5; done
get www.pglive.in / >/dev/null || { echo "FAIL nginx did not come up:"; docker logs "$NAME" 2>&1 | tail -20; exit 1; }

failures=0
check() { if [[ "${2,,}" == *"${3,,}"* ]]; then echo "ok   $1"; else echo "FAIL $1 (got: $2)"; failures=$((failures + 1)); fi; }

check "pglive.in still answers through PGLive's server block (502 from the test upstream, HSTS kept)" \
  "$(get www.pglive.in / -I)" "strict-transport-security: max-age=300"
check "pglive.in apex still redirects to www" "$(get pglive.in /x -I)" "location: https://www.pglive.in/x"
check "unknown hosts still get no answer" "$(get unknown.example / -w '%{http_code}' 2>/dev/null || true)" "000"
check "http mytravelplanner.in -> https apex" \
  "$(curl -s --max-time 5 -I -H 'Host: mytravelplanner.in' "http://127.0.0.1:$HTTP/a?gclid=1")" \
  "Location: https://mytravelplanner.in/a?gclid=1"
check "ACME challenge path is served for our hosts" \
  "$(curl -s --max-time 5 -w '%{http_code}' -H 'Host: www.mytravelplanner.in' "http://127.0.0.1:$HTTP/.well-known/acme-challenge/x")" "404"
check "www -> apex, query kept" "$(get www.mytravelplanner.in '/tour-packages/?gclid=1' -I)" \
  "location: https://mytravelplanner.in/tour-packages/?gclid=1"
echoed="$(get mytravelplanner.in '/enquiry/?utm_source=g' -H 'X-Forwarded-For: 6.6.6.6' -H 'X-Travel-Edge-Key: forged' -H 'X-Forwarded-Host: evil.example')"
check "Host is the upstream (Cloud Run routes on it)" "$echoed" "host=127.0.0.1:8443"
check "X-Forwarded-Host is the public host, not the client's" "$echoed" "xfh=mytravelplanner.in "
if [[ "$echoed" =~ xff=[0-9.]+\  && "$echoed" != *6.6.6.6* ]]; then
  echo "ok   client-sent X-Forwarded-For is overwritten with the one peer address"
else
  echo "FAIL X-Forwarded-For (got: $echoed)"; failures=$((failures + 1))
fi
check "edge key is ours, a forged one is overwritten" "$echoed" "key=$KEY "
check "proto https and URI untouched" "$echoed" "proto=https key"
check "request URI passed through" "$echoed" "uri=/enquiry/?utm_source=g"

(( failures == 0 )) && echo "All edge checks passed." || { echo "$failures check(s) failed."; exit 1; }
