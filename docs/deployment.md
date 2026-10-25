# Deployment

Status: **decided 2026-10-25 — Google Cloud Run + the existing Cloud SQL instance** (owner decision, Module 07).
The files below are written and tested locally (production image, settings, backup scripts); the cloud steps in §3
have **not been run yet**. The deploy script's gcloud flags were checked against the official CLI's help, not against a live project.
Target: public HTTPS site live by 2026-10-31 (execution plan §3 Days 6–7).

## 1. Architecture
```
mytravelplanner.in ──► Cloud Run service "travel-web"  (Gunicorn + WhiteNoise, image from backend/Dockerfile.prod)
 www → 301 to apex          │  unix socket via the Cloud SQL connector
                            ▼
                  Cloud SQL for PostgreSQL (existing instance)  —  database travel_platform, its own user travel_app
Secrets: Secret Manager (SECRET_KEY, DB_PASSWORD, EMAIL_HOST_PASSWORD)     Config: deploy/cloudrun/env.prod.yaml
Cloud Run jobs (same image): migrate, createcachetable, clearsessions (daily), manage (createsuperuser, reset_admin_mfa…)
Backups: Cloud SQL automated backups  +  an encrypted dump you download weekly (deploy/backup/)
```
Files: `backend/Dockerfile.prod`, `deploy/cloudrun/{deploy.sh, cloudbuild.yaml, env.prod.yaml.example}`, `deploy/backup/{download_backup.sh, restore_check.sh}`.

Cloud Run differences from a single server, and what the code does about them:
| Cloud Run fact | What we did |
|---|---|
| Many instances, no shared disk | Lead-form throttle counters live in the database cache (`CACHE_BACKEND=db`, table made by `createcachetable`) |
| Client IP arrives in `X-Forwarded-For` | `CLIENT_IP_HEADER=X-Forwarded-For`, `CLIENT_IP_TRUSTED_HOPS=1`: only the entry Google appended is used, so a visitor cannot forge their way out of the throttle (tested) |
| `*.run.app` URL exists alongside the domain | Listed in `ALLOWED_HOSTS` for smoke tests; only `www` is redirected (`REDIRECT_TO_CANONICAL_HOSTS`) |
| TLS ends at Google; app sees `X-Forwarded-Proto` | `SECURE_PROXY_SSL_HEADER` + `SECURE_SSL_REDIRECT` (already in prod settings); `/health/` is exempt |
| Scales to zero by default | `MIN_INSTANCES=1` is worth it once ads run (§5) |
| No cron | Cloud Scheduler runs the `clearsessions` job daily (`deploy.sh schedule`) |

## 2. Production configuration
- `config.settings.prod` refuses to start with: DEBUG on, a weak/short `SECRET_KEY`, empty `ALLOWED_HOSTS`, a non-https `SITE_BASE_URL`,
  the default `admin/` path, an unknown `CACHE_BACKEND`, or `ADMIN_REQUIRE_MFA=False`. CI runs `check --deploy` with these settings.
- **Admin MFA** is always on in production (§4). `ADMIN_URL_PATH` must be a long random path ending in `/`.
- HSTS: leave `SECURE_HSTS_SECONDS=0` until HTTPS works on the apex and `www`, then raise it (one year = 31536000).
- Sessions live in the database: the `clearsessions` job (daily) removes expired rows.
- Error reports: set `SENTRY_DSN` only if wanted; `send_default_pii` is off. Cloud Run request logs include URLs — the site never puts
  personal data in a URL (invariant 4), and Gunicorn's own access log is off.

## 3. First-time cloud setup (once)
Replace `PROJECT`, `REGION` (e.g. `asia-south1`), `INSTANCE`, `RUNTIME_SA`. All values below are placeholders.
```bash
gcloud config set project PROJECT
gcloud services enable run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com cloudscheduler.googleapis.com

# 1. Image repository
gcloud artifacts repositories create travel --repository-format=docker --location=REGION

# 2. A separate database and user on the EXISTING Cloud SQL instance (do not reuse another app's user)
gcloud sql databases create travel_platform --instance=INSTANCE
gcloud sql users create travel_app --instance=INSTANCE --password="$(openssl rand -base64 24)"   # copy it into the secret below
gcloud sql instances patch INSTANCE --backup-start-time=21:00 --enable-point-in-time-recovery      # 21:00 UTC = 02:30 IST

# 3. Secrets (read from files/stdin so they never appear in shell history)
printf '%s' "<50+ random characters>" | gcloud secrets create travel-secret-key --data-file=-
printf '%s' "<the travel_app password>" | gcloud secrets create travel-db-password --data-file=-
printf '%s' "<smtp password>"           | gcloud secrets create travel-email-password --data-file=-
printf '%s' "<a strong admin password>" | gcloud secrets create travel-admin-password --data-file=-

# 4. A runtime service account with only what it needs
gcloud iam service-accounts create travel-runtime
for role in roles/cloudsql.client roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding PROJECT --member=serviceAccount:travel-runtime@PROJECT.iam.gserviceaccount.com --role=$role
done
```
Reminder: `gcloud sql users create` is run against the existing instance; because the database is new and `travel_app` owns only it,
this site cannot read the other applications' data.

## 4. Release and first admin sign-in
```bash
cp deploy/cloudrun/env.prod.yaml.example deploy/cloudrun/env.prod.yaml     # fill every <value>; the script refuses placeholders
export PROJECT_ID=PROJECT REGION=REGION SQL_CONNECTION=PROJECT:REGION:INSTANCE
export RUNTIME_SA=travel-runtime@PROJECT.iam.gserviceaccount.com
deploy/cloudrun/deploy.sh release          # build image -> migrate + createcachetable (jobs) -> deploy service; prints the URL
```
1. Put the printed `*.run.app` host into `ALLOWED_HOSTS` in `env.prod.yaml` if you have not, run `deploy.sh deploy`, open the URL.
2. Create the owner login (password comes from Secret Manager, never the command line):
   `deploy/cloudrun/deploy.sh manage createsuperuser --noinput --username owner --email you@example.com`
3. Open `https://<service-url>/<ADMIN_URL_PATH>`, sign in with the password. A QR code appears **once**: scan it with an authenticator app
   (Google Authenticator, Microsoft Authenticator, 1Password…), type the 6-digit code. From then on every sign-in needs password + code.
4. Lost phone: `deploy/cloudrun/deploy.sh manage reset_admin_mfa owner`, then sign in again to enrol the new phone straight away.
   A stolen password alone can never add a new authenticator (enrolment is only offered while none exists).
5. Daily clean-up: `SCHEDULER_SA=<service account that may run jobs> deploy/cloudrun/deploy.sh schedule`
6. Seed the starting content, then review and publish the Araku draft in the admin:
   `deploy/cloudrun/deploy.sh manage seed_launch_content`

## 5. Domain: mytravelplanner.in
- **Canonical host:** `https://mytravelplanner.in` (no www). `SITE_BASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `REDIRECT_TO_CANONICAL_HOSTS`
  are in `env.prod.yaml`; `http://` is redirected to `https://` by the app, `www` is 301-redirected to the apex (query string kept, so click IDs survive).
- **Connecting the domain** (choose after checking your region): Cloud Run *domain mappings*
  (`gcloud beta run domain-mappings create --service travel-web --domain mytravelplanner.in --region REGION`, then add the DNS records it prints,
  repeat for `www.mytravelplanner.in`) are simplest but are only available in some regions; otherwise put a global external Application Load Balancer
  with a Google-managed certificate in front. **With a load balancer set `CLIENT_IP_TRUSTED_HOPS: "2"`** (it appends its own address).
  After DNS works, send a request with a forged header and confirm in the lead-form throttle test that the real IP is used (see the checklist).
- **Search Console:** add `https://mytravelplanner.in`, verify with `GOOGLE_SITE_VERIFICATION`, submit `/sitemap.xml`. Ads final URLs use the apex.
- **Staging:** the `*.run.app` URL is the staging site until DNS is ready. Never put it in ads or Search Console (plan §14).
- **Cold starts:** with `MIN_INSTANCES=0` the first visitor after a quiet period waits a few seconds. Before ads start run
  `MIN_INSTANCES=1 deploy/cloudrun/deploy.sh deploy` (costs a small always-on instance).

## 6. Backups (the database holds lead PII)
Owner decision 2026-10-25: keep it simple, no extra bucket. On Cloud SQL that means two layers:
1. **Cloud SQL automated backups** (daily, 7 kept by default) + point-in-time recovery, enabled in §3 step 2. Restore from the console if the database is damaged.
2. **Your own encrypted copy, weekly:** `deploy/backup/download_backup.sh` (needs the Cloud SQL Auth Proxy, Docker and gpg). The dump is piped straight into
   `gpg` (AES-256, passphrase you choose), so a plain copy never touches disk; the 8 newest copies are kept in `backups/` (gitignored).
   Store the passphrase in a password manager. Delete old copies as the privacy notice promises (do not keep leads indefinitely).
3. **Restore test (required before ads):** `deploy/backup/restore_check.sh backups/<file>.dump.gpg` restores into a throwaway local database, prints row
   counts only (no names or phone numbers), checks the schema matches the code, and drops the database. Tested on the local database on 2026-10-25;
   repeat it once on a real production download.

## 7. Go-live
Follow the checklist in [modules/07-launch-deployment.md](modules/07-launch-deployment.md) (plan §15). Ads are enabled only after every box is ticked.

## 8. Deploy automation
`deploy.sh release` is the one command. A GitHub workflow that runs it after CI passes can be added once the first manual release works (CI today only tests).
