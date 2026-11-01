# Deployment

Status: **decided 2026-10-25 — Google Cloud Run + an existing Cloud SQL instance** (owner decision, Module 07).
**Revised 2026-10-27 (owner decision):** the instance is PGLive's (`pglive-pg-prod`, PG-MANAGEMENT-WEB), which is live.
Our service, image, secrets and jobs live in **our own GCP project**. The domain goes through **PGLive's nginx edge VM**
(`pglive-worker`) as an extra server block. Rule one: **PGLive must not notice.** See §2a for what we may and may not touch.
The edge config was tested next to PGLive's real nginx config (`deploy/edge/test-travel-edge.sh`).
**Live since 2026-10-27:** project `mytravelplanner-prod`, service `travel-web` (asia-south1), https://mytravelplanner.in through the edge with the
lock on. §3 and §4 steps 1–5, 8 and 9 are done; the owner's MFA enrolment (§4 step 6) is still open.
PGLive was checked before and after every step and did not change: same responses, same instance settings version, nginx files byte-identical,
and one added IAM member.

## 1. Architecture
```
GoDaddy DNS: A @, www (mytravelplanner.in) → 34.14.158.50  (pglive-edge-ip, the pglive-worker VM in project pglive-prod)
nginx on pglive-worker — PGLive's conf.d/pglive.conf untouched, ours is conf.d/travel.conf (own Let's Encrypt cert)
  http://*            → https://mytravelplanner.in        www → 301 apex (query kept, click IDs survive)
  mytravelplanner.in  → https://travel-web-….run.app     Host = run.app name, X-Forwarded-Host = mytravelplanner.in,
                                                          X-Forwarded-For overwritten with the visitor, X-Travel-Edge-Key
Cloud Run service "travel-web" (our project, asia-south1; Gunicorn + WhiteNoise, image from backend/Dockerfile.prod)
        │  unix socket via the Cloud SQL connector (cross-project; roles/cloudsql.client in pglive-prod)
        ▼
Cloud SQL pglive-pg-prod (PGLive's) — our database travel_platform, our role travel_app (CONNECTION LIMIT 12)
Secrets: Secret Manager in our project (SECRET_KEY, DB_PASSWORD, EMAIL_HOST_PASSWORD, EDGE_SHARED_SECRET)
Config: deploy/cloudrun/env.prod.yaml
Cloud Run jobs (same image): migrate, createcachetable, clearsessions (daily), manage (createsuperuser, reset_admin_mfa…)
Backups: PGLive's instance backups cover our database too  +  an encrypted dump you download weekly (deploy/backup/)
```
Files: `backend/Dockerfile.prod`, `deploy/cloudrun/{deploy.sh, cloudbuild.yaml, env.prod.yaml.example}`,
`deploy/cloudsql/create-travel-db.sql`, `deploy/edge/{travel.conf.template, setup-travel-edge.sh, test-travel-edge.sh}`,
`deploy/backup/{download_backup.sh, restore_check.sh}`.

How Cloud Run differs from a single server, and what the code does about it:
| Cloud Run fact | What we did |
|---|---|
| Many instances, no shared disk | Lead-form throttle counters live in the database cache (`CACHE_BACKEND=db`, table made by `createcachetable`) |
| Client IP arrives in `X-Forwarded-For` | nginx overwrites it with the visitor, Google appends the VM: `CLIENT_IP_TRUSTED_HOPS=2` (tested) |
| Cloud Run routes on `Host`, so nginx must send the run.app name | `USE_X_FORWARDED_HOST=True`: Django reads the public host from `X-Forwarded-Host` (nginx overwrites it; ALLOWED_HOSTS still checks it) |
| The `*.run.app` URL is public (another project's VM can't use `internal` ingress) | `EDGE_SHARED_SECRET`: any request without nginx's `X-Travel-Edge-Key` gets a 403 (`/health/` exempt), so the edge can't be bypassed to forge the IP |
| TLS ends at nginx; app sees `X-Forwarded-Proto` | `SECURE_PROXY_SSL_HEADER` + `SECURE_SSL_REDIRECT` (prod settings); `/health/` is exempt |
| Scales to zero by default | `MIN_INSTANCES=1` is worth it once ads run (§5) |
| No cron | Cloud Scheduler runs the `clearsessions` job daily (`deploy.sh schedule`) |

## 2. Production configuration
- `config.settings.prod` refuses to start with: DEBUG on, a weak/short `SECRET_KEY`, empty `ALLOWED_HOSTS`, a non-https `SITE_BASE_URL`,
  the default `admin/` path, an unknown `CACHE_BACKEND`, or `ADMIN_REQUIRE_MFA=False`. CI runs `check --deploy` with these settings.
- **Admin MFA** is always on in production (§4). `ADMIN_URL_PATH` must be a long random path ending in `/`.
- HSTS: leave `SECURE_HSTS_SECONDS=0` until HTTPS works on the apex and `www`, then raise it (one year = 31536000). Django sets it, not nginx.
- Sessions live in the database: the `clearsessions` job (daily) removes expired rows.
- Error reports: set `SENTRY_DSN` only if wanted; `send_default_pii` is off. Cloud Run request logs include URLs — the site never puts
  personal data in a URL (invariant 4), and Gunicorn's own access log is off.

## 2a. Sharing PGLive's instance and edge VM (read before any change)
What we added to PGLive's side. This is the complete list, and each item can be undone on its own:
| Where | What | Undo |
|---|---|---|
| `pglive-prod` IAM | `roles/cloudsql.client` for `travel-runtime@<our project>` | remove the binding |
| `pglive-pg-prod` | role `travel_app` (plain role, not cloudsqlsuperuser, CONNECTION LIMIT 12) and database `travel_platform` | `DROP DATABASE` / `DROP ROLE` |
| `pglive-worker` | `/etc/nginx/conf.d/travel.conf`, `/etc/nginx/travel-edge-key.conf`, LE cert `mytravelplanner.in` | `rm` both files, `nginx -t && systemctl reload nginx` |

Rules:
- **Never** change the instance from this repo: no `gcloud sql instances patch` (tier, flags, backup window, maintenance, SSL), no restarts,
  no `gcloud sql users create` (it adds `cloudsqlsuperuser`). Instance settings belong to PGLive (its `infra/20-data.sh`).
- **Connection budget:** the instance is a db-g1-small (~50 connections) and PGLive needs most of them. `travel_app` is hard-capped at
  12 and `deploy.sh` defaults to `MAX_INSTANCES=2` (8 threads each, connections closed after each request). Raise either only after checking
  PGLive's headroom with its owner.
- **Never** edit PGLive's nginx files (`pglive.conf`, `00-pglive-limits.conf`, `snippets/pglive-*`). `travel.conf` never declares a
  `default_server` or reuses PGLive's zone, variable or snippet names. `setup-travel-edge.sh` reloads nginx only after `nginx -t` passes,
  and restores the previous file if the test fails. Run `deploy/edge/test-travel-edge.sh` before changing `travel.conf.template`.
  PGLive's `setup-edge.sh` rewrites only its own files, so each survives the other's re-runs. PGLive's certbot deploy hook reloads nginx for our renewals too.
- **Downtime we inherit:** Cloud SQL maintenance (Sunday 20:00 UTC = Monday 01:30 IST) and any pglive-worker outage take this site down too.
- **PGLive's disaster recovery** (PITR clone to a *new* instance, the old one stopped for 14 days) takes this site down too. If it
  happens, switch `SQL_CONNECTION` and `DB_HOST` to the new instance, re-run `create-travel-db.sql` if the role is missing, then run `deploy.sh deploy`.
- PGLive's instance logs connections (`log_connections=on`), so ours show up in its Cloud SQL logs, under `travel_app`.

## 3. First-time cloud setup (once)
`TRAVEL` = our project (e.g. `mytravelplanner-prod`), `REGION=asia-south1`. Run in Git Bash.
```bash
# 0. Owner: create the project and link billing (console). Everything below runs in it unless it says pglive-prod.
gcloud services enable run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com cloudscheduler.googleapis.com --project TRAVEL
# (sqladmin must be enabled in OUR project for the Cloud Run connector.)

# 1. Image repository
gcloud artifacts repositories create travel --repository-format=docker --location=asia-south1 --project TRAVEL

# 2. Runtime service account: our secrets in our project; connect-only on PGLive's instance (the one IAM change there)
gcloud iam service-accounts create travel-runtime --project TRAVEL
gcloud projects add-iam-policy-binding TRAVEL --member=serviceAccount:travel-runtime@TRAVEL.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
gcloud projects add-iam-policy-binding pglive-prod --member=serviceAccount:travel-runtime@TRAVEL.iam.gserviceaccount.com \
  --role=roles/cloudsql.client --condition=None

# 3. Secrets (piped from stdin so they never appear in shell history). Strip \r as well as \n: Git Bash's openssl
#    prints CRLF, and a password ending in an invisible \r breaks typing it later.
openssl rand -base64 48 | tr -d '\r\n' | gcloud secrets create travel-secret-key --data-file=- --project TRAVEL
openssl rand -hex 24    | tr -d '\r\n' | gcloud secrets create travel-db-password --data-file=- --project TRAVEL
printf '%s' "<smtp password>"        | gcloud secrets create travel-email-password --data-file=- --project TRAVEL
printf '%s' "<a strong admin password>" | gcloud secrets create travel-admin-password --data-file=- --project TRAVEL
# travel-edge-secret is created in §4 step 4, after the edge works.

# 4. Our database and role on PGLive's instance, as postgres through the Auth Proxy. The postgres password is in
#    pglive-prod's secret POSTGRES_ADMIN_PASSWORD (set 2026-10-27; PGLive's services never use it).
cloud-sql-proxy pglive-prod:asia-south1:pglive-pg-prod --port 6543 &
export PGPASSWORD="$(gcloud secrets versions access latest --secret POSTGRES_ADMIN_PASSWORD --project pglive-prod)"
TRAVEL_DB_PASSWORD="$(gcloud secrets versions access latest --secret travel-db-password --project TRAVEL)" \
  psql "host=127.0.0.1 port=6543 user=postgres dbname=postgres sslmode=disable" \
  -v travel_password="$TRAVEL_DB_PASSWORD" -f deploy/cloudsql/create-travel-db.sql
unset PGPASSWORD
```
No local proxy or psql? Run both in Docker: start
`docker run -d --name travel-sql-proxy gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.14.1 --address 0.0.0.0 --port 6543 --token "$(gcloud auth print-access-token)" pglive-prod:asia-south1:pglive-pg-prod`.
Then run `psql` with `docker run --rm -i -e PGPASSWORD --network container:travel-sql-proxy postgres:16-alpine psql … -f - < deploy/cloudsql/create-travel-db.sql`.
In Git Bash, gcloud needs `CLOUDSDK_PYTHON` set to the SDK's `platform/bundledpython/python.exe`.
Prefix only the docker commands with `MSYS2_ARG_CONV_EXCL='*'`, because that setting breaks gcloud.
Backups need no setup: PGLive's instance already makes daily backups (20:30 UTC, 14 kept) with 7-day point-in-time recovery,
and they include `travel_platform`. Because `travel_app` owns only its own database and `pg_platform` admits nobody by default
(`REVOKE ALL … FROM PUBLIC`), this site cannot read PGLive's data.

## 4. Release, domain and first admin sign-in
```bash
export PROJECT_ID=TRAVEL REGION=asia-south1 SQL_CONNECTION=pglive-prod:asia-south1:pglive-pg-prod
export RUNTIME_SA=travel-runtime@TRAVEL.iam.gserviceaccount.com
deploy/cloudrun/deploy.sh release          # build image -> migrate + createcachetable (jobs) -> deploy service; prints the URL
```
`deploy.sh` refuses a `pglive-*` PROJECT_ID and an `env.prod.yaml` that still has `<placeholders>`.
1. Put the printed `*.run.app` host into `ALLOWED_HOSTS` in `env.prod.yaml`, run `deploy.sh deploy`, then open `https://<run.app>/health/`
   and `/`. The edge lock is still off at this point, so this is the smoke test.
2. GoDaddy (owner): A records `@` and `www` for mytravelplanner.in → `34.14.158.50`. Wait until `nslookup mytravelplanner.in` returns it.
3. Edge (§5): copy `deploy/edge/` to the VM and run `setup-travel-edge.sh`.
4. Turn the edge lock on: `printf '%s' "$EDGE_KEY" | gcloud secrets create travel-edge-secret --data-file=- --project TRAVEL`, then
   `deploy.sh deploy`. From now on `https://<run.app>/` answers 403 and the site is only reachable through https://mytravelplanner.in.
5. Create the owner login (the password comes from Secret Manager, never the command line):
   `deploy/cloudrun/deploy.sh manage createsuperuser --noinput --username owner --email you@example.com`
6. Open `https://mytravelplanner.in/<ADMIN_URL_PATH>` and sign in with the password. A QR code appears **once**: scan it with an authenticator app
   (Google Authenticator, Microsoft Authenticator, 1Password…), type the 6-digit code. From then on every sign-in needs password + code.
7. Lost phone: `deploy/cloudrun/deploy.sh manage reset_admin_mfa owner`, then sign in again to enrol the new phone straight away.
   A stolen password alone can never add a new authenticator (enrolment is only offered while none exists).
8. Daily clean-up: `SCHEDULER_SA=<service account in TRAVEL that may run jobs> deploy/cloudrun/deploy.sh schedule`
9. Seed the starting content, then review and publish the Araku draft in the admin:
   `deploy/cloudrun/deploy.sh manage seed_launch_content`

## 5. Domain: mytravelplanner.in through the pglive-worker nginx
- **Canonical host:** `https://mytravelplanner.in` (no www). nginx sends `http://` and `www` to it with a 301 (query string kept).
  `REDIRECT_TO_CANONICAL_HOSTS` stays set as a backstop.
- **Why this edge:** Cloud Run domain mappings aren't offered in asia-south1, and a load balancer costs about $18/month. The VM already
  terminates TLS for pglive.in (owner decision 2026-10-27).
- **Set up (once, and to change the run.app host):**
  ```bash
  EDGE_KEY="$(openssl rand -hex 32)"     # keep it for §4 step 4 (it becomes travel-edge-secret)
  gcloud compute scp --recurse deploy/edge pglive-worker:/tmp/travel-edge --zone asia-south1-a --tunnel-through-iap --project pglive-prod
  gcloud compute ssh pglive-worker --zone asia-south1-a --tunnel-through-iap --project pglive-prod -- \
    "sudo mkdir -p /opt/travel-edge && sudo cp /tmp/travel-edge/* /opt/travel-edge/ && \
     sudo TRAVEL_HOST=<run.app host> LE_EMAIL=<you> EDGE_KEY=$EDGE_KEY /opt/travel-edge/setup-travel-edge.sh"
  ```
  The script writes only our two files, gets the certificate with HTTP-01 (DNS must already point at the VM), and reloads only after `nginx -t` passes.
- **Rotating the edge key:** add a new `travel-edge-secret` version, re-run the script with the new key, then `deploy.sh deploy`. Requests get a 403
  for a few seconds in between, so do it at a quiet hour.
- **Client IP check after go-live:** submit the form 6 times from one network: the 6th must be throttled, while another network (mobile data)
  still gets through. That proves `CLIENT_IP_TRUSTED_HOPS=2` picks the visitor, not the VM.
- **Search Console:** add `https://mytravelplanner.in`, verify with `GOOGLE_SITE_VERIFICATION`, submit `/sitemap.xml`. Ads final URLs use the apex.
- **Staging:** the `*.run.app` URL is the staging site only until the edge lock is on. Never put it in ads or Search Console (plan §14).
- **Cold starts:** with `MIN_INSTANCES=0` the first visitor after a quiet period waits a few seconds. Before ads start, run
  `MIN_INSTANCES=1 deploy/cloudrun/deploy.sh deploy` (costs a small always-on instance).

## 6. Backups (the database holds lead PII)
Owner decision 2026-10-25: keep it simple, no extra bucket. Two layers:
1. **PGLive's instance backups** (daily 20:30 UTC, 14 kept, 7-day point-in-time recovery) include our database. Restoring one rolls back the
   **whole instance**, PGLive included, so for a problem only we have, restore our own copy (layer 2) instead, and agree any instance restore with PGLive.
2. **Your own encrypted copy, weekly:** `deploy/backup/download_backup.sh` (needs the Cloud SQL Auth Proxy, Docker and gpg). It dumps only
   `travel_platform` as `travel_app`. The dump is piped straight into `gpg` (AES-256, passphrase you choose), so a plain copy never touches disk.
   The 8 newest copies are kept in `backups/` (gitignored).
   Store the passphrase in a password manager. Delete old copies as the privacy notice promises (do not keep leads indefinitely).
3. **Restore test (required before ads):** `deploy/backup/restore_check.sh backups/<file>.dump.gpg` restores into a throwaway local database, prints row
   counts only (no names or phone numbers), checks the schema matches the code, and drops the database. Tested on the local database on 2026-10-25;
   repeat it once on a real production download.

## 7. Go-live
Follow the checklist in [modules/07-launch-deployment.md](modules/07-launch-deployment.md) (plan §15). Ads are enabled only after every box is ticked.

## 8. Deploy automation
`deploy.sh release` is the one command. A GitHub workflow that runs it after CI passes can be added once the first manual release works (CI today only tests).
