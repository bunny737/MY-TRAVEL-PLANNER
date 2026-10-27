# Module: Launch & Deployment

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** In Progress — code, image, backup scripts and docs are built and tested locally (2026-10-25); the cloud deployment,
real-world checks and the owner-only go-live items below are still open
**Phase:** 0
**Plan reference:** docs/execution-plan.md §1 (week-one success), §3 Days 6–7, §6 (go-live gates), §15 (checklist)
**Depends on:** 01, 02, 03, 04, 05, 06
**Blocks:** 08, 09, 10, 11
**App:** infra (`deploy/`, `backend/Dockerfile.prod`, `docs/deployment.md`) + `config/admin_site.py` (admin MFA)

## Purpose
Put the site on a public HTTPS host with backups, run the go-live checklist, and only then enable Google Ads.
Mostly operations; the code part is admin MFA, Cloud Run compatibility and the production image.

## Scope (as built)
- **Production image:** `backend/Dockerfile.prod` — `python:3.12-slim`, production requirements only (no Pillow, no dev tools), non-root user,
  `collectstatic` at build time, Gunicorn on `$PORT` (2 workers × 4 threads). `.gcloudignore` reuses `.dockerignore` so `.env` never reaches the build.
- **Cloud Run + Cloud SQL (owner decision):** `deploy/cloudrun/deploy.sh` (`release` = build → migrate + `createcachetable` jobs → deploy service;
  `manage <command>` runs any management command as a job; `schedule` sets the daily `clearsessions`), `cloudbuild.yaml`,
  `env.prod.yaml.example` (no secrets; secrets come from Secret Manager). It refuses to run with unfilled `<placeholders>`.
- **Admin MFA (owner decision, `django-otp` + `qrcode` added to `requirements/base.txt`):** `config/admin_site.py` + `templates/admin/mfa.html`.
  Password → 6-digit authenticator code → admin. First sign-in shows a QR code (rendered on the server, never cached) and confirms one code; a new
  authenticator can only be added after `manage.py reset_admin_mfa <user>` (run through `deploy.sh manage`), so a stolen password cannot enrol an
  attacker's phone. Wrong codes are throttled by django-otp. Production forces `ADMIN_REQUIRE_MFA=True`; locally it is off by default.
- **Settings for Cloud Run:** `CACHE_BACKEND=db` (throttle counters shared by all instances), `CLIENT_IP_HEADER=X-Forwarded-For` +
  `CLIENT_IP_TRUSTED_HOPS` (only the right-most entries our proxies appended are trusted), `REDIRECT_TO_CANONICAL_HOSTS` (`www` → apex 301,
  query string kept; `/health/` exempt). Production additionally refuses the default `admin/` path, an unknown cache backend, and MFA off.
- **Backups:** `deploy/backup/download_backup.sh` (pg_dump through the Cloud SQL Auth Proxy, piped straight into `gpg` AES-256, 8 newest copies kept)
  and `deploy/backup/restore_check.sh` (restore into a throwaway local database, row counts only, migration check, drop). Cloud SQL automated
  backups + point-in-time recovery are the second layer (setup in docs/deployment.md §3).
- **CI:** `check --deploy` now also sets `ADMIN_URL_PATH` and `CACHE_BACKEND`.

## Business rules (tests in `apps/core/test_launch.py`, 35 tests)
1. A staff password alone never opens the admin: every admin URL (including lead and partner lists) redirects to the code step.
2. First sign-in enrols an authenticator; a wrong or non-numeric code is refused; repeated wrong codes are throttled; the secret/QR is shown only
   while no confirmed authenticator exists, is served `no-store`, and non-staff users cannot enrol.
3. `next` cannot redirect off-site. Sign-out is available on the code page. With the switch off (local dev) the admin works with a password only.
4. `reset_admin_mfa` removes only the named user's authenticators.
5. Throttle IP: Cloud Run uses the entry Google appended (a forged `X-Forwarded-For` prefix cannot change the bucket); behind a load balancer
   `CLIENT_IP_TRUSTED_HOPS=2` skips the balancer's entry; with no header configured, forwarded headers are ignored.
6. `www` redirects permanently to the same path on the canonical host keeping the query string; the canonical and `*.run.app` hosts are served;
   `/health/` is never redirected; nothing redirects when the setting is empty.
7. Production settings refuse: MFA off, default admin path, unknown cache backend (plus the Module 01 refusals). OTP middleware runs after authentication.
8. The production image installs production requirements only, runs as non-root, binds `$PORT`, and keeps secrets out of the image; the env template
   holds no secrets, is set up for Cloud Run, and every key in it is a real setting. Backups are encrypted on the fly (never a plain dump file) and the
   restore script's queries select no personal columns.

Also verified by running them (2026-10-25): the production image builds and serves `/`, `/health/` (HTTP), static files, `/<admin>/` → login redirect and
`/admin/` → 404, http → https and `www` → apex redirects; the database-cache throttle blocked the 6th request from one real IP and not another;
`restore_check.sh` restored an encrypted dump of the local database and passed its checks.

## Go-live checklist (plan §15)
Legend: ✅ done and verified locally · 🔧 built, must be done/verified on the real deployment · 👤 only the owner can do it · ⬜ not started.

### Product and operations
- [ ] 🔧 Final brand/domain and SSL work on mobile (DNS + certificate; check on a real phone)
- [ ] 👤 Araku package page truthful and useful; enquiry CTAs visible; cab page/ads remain P1 (review the seeded draft, then publish)
- [x] ✅ Privacy, terms, contact and referral notice live (built; 👤 legal review of the wording is still open, see open-decisions)
- [x] ✅ Form stores a valid lead with notice version, source and consent; rejects invalid input (Module 05 tests) — repeat once on production
- [ ] 👤 WhatsApp opens the business account; response + consent process ready (set `WHATSAPP_NUMBER`, test on a phone)
- [ ] 👤 ≥2 operators consent to receive referred leads (create them as Partners with `referral_terms_agreed_on`)
- [ ] 🔧 Lead viewable privately, qualified and manually forwarded (do it with a real test lead on production, behind MFA)
- [ ] 🔧 Notifications (`EMAIL_*`, `LEAD_NOTIFY_EMAIL`), backup + restore (✅ locally; repeat on a production download), error handling, admin login with MFA, spam guard on production

### Measurement and paid acquisition
- [ ] 👤 GA4 + Google Ads tags in (needs your IDs; decide on the cookie/consent banner first)
- [ ] 🔧 Form conversion tested; WhatsApp click measured separately; duplicates do not double-count (Module 06 tests ✅; verify in GA4 DebugView)
- [x] ✅ Thank-you page not indexable; no personal data in event URLs or analytics (tests)
- [ ] 🔧 UTMs and click IDs stored; test campaign attribution (open `/?utm_source=test&gclid=abc` on production, submit a lead, check it in admin)
- [ ] 👤 Search campaign uses page-matched copy and relevant locations/keywords
- [ ] 👤 Negative keywords and search-term monitoring process created
- [ ] 👤 Budget/end date set (₹5,000 test; daily cap is not a hard cap); spend + lead-quality reviews scheduled
- [ ] 👤 Ad billing and policy review complete; ads serving verified before reporting a launch

### Added by this module
- [ ] 🔧 Production `check --deploy` clean on the deployed settings; HSTS raised after HTTPS is verified on apex and `www`
- [ ] 🔧 Throttle uses the real client IP on production (submit 6 enquiries from one phone; the 6th must be refused)
- [ ] 🔧 `clearsessions` scheduled; Cloud SQL automated backups + PITR on; one encrypted weekly download made and restore-tested
- [ ] 👤 Search Console property verified, sitemap submitted; staging/`run.app` host not in ads or Search Console
- [ ] 👤 `MIN_INSTANCES=1` before ads start (avoids a slow first page)

## Permissions
Owner only (cloud project, DNS, ad account, admin). The runtime service account has only Cloud SQL Client and Secret Accessor.

## Privacy & claims check
Backups are encrypted before they touch disk and are never committed (`*.dump`, `*.dump.gpg`, `backups/` are gitignored). `restore_check.sh` prints counts
only. The MFA page never logs or caches the secret. Server logs: Gunicorn access logging is off; Cloud Run request logs contain paths and query strings, and
the site never places personal data in URLs.

## Edge cases handled
- Password-authenticated user without a code is sent straight to the code step (not shown the password form again).
- `Host` not in `ALLOWED_HOSTS` still gets a 400 (the canonical-host middleware reads the raw header only to decide on the `www` redirect).
- A second browser tab can never add a second authenticator while one is confirmed; an abandoned half-enrolment is reused, not duplicated.

## Open questions / Decisions
- [DECISION 2026-10-25] Hosting: **Google Cloud Run + the existing Cloud SQL instance** (owner). The site gets its own database and user on that instance.
- [DECISION 2026-10-25] Admin MFA: **django-otp (TOTP authenticator app)**. New dependencies `django-otp` and `qrcode` approved by the owner.
- [DECISION 2026-10-25] Backups: owner chose "server + manual download". On Cloud SQL there is no server of our own, so the equivalent is
  Cloud SQL automated backups plus a weekly encrypted download by the owner; no extra bucket or credentials.
- [DECISION 2026-10-25] The throttle cache moved from files to the database on Cloud Run (`CACHE_BACKEND=db`); the file cache remains the default
  for local development and for a single-host setup.
- [DECISION 2026-10-25] No custom `Dockerfile` healthcheck: Cloud Run probes the port; `/health/` stays available for uptime checks.
- [DECISION 2026-10-27] The "existing instance" is PGLive's `pglive-pg-prod` (live). PGLive must not be disturbed. Owner chose **our own GCP
  project** for the service, image, secrets and jobs; the only change in `pglive-prod` is a `roles/cloudsql.client` binding for our runtime SA.
- [DECISION 2026-10-27] Region asia-south1 (same as the instance). Domain through **PGLive's nginx edge VM** (owner; domain mappings aren't
  offered in asia-south1, and a load balancer costs about $18/month): our own `conf.d/travel.conf` and our own LE cert, with PGLive's files untouched.
- [DECISION 2026-10-27] Judgement calls that follow from sharing the instance and VM:
  `travel_app` is created in SQL (`deploy/cloudsql/create-travel-db.sql`), not with `gcloud sql users create`, which would add cloudsqlsuperuser.
  It has CONNECTION LIMIT 12 and `MAX_INSTANCES` defaults to 2, because the db-g1-small has ~50 connections.
  The old "patch the backup window" step was removed (the window is PGLive's).
  `deploy.sh` refuses `pglive-*` projects.
  `USE_X_FORWARDED_HOST` + `CLIENT_IP_TRUSTED_HOPS=2` for the nginx hop.
  `EdgeSecretMiddleware` + `EDGE_SHARED_SECRET` locks out direct `*.run.app` access, because `internal` ingress can't admit another project's VM.
  The lock turns on when the `travel-edge-secret` secret exists.
- [OPEN] Cookie/analytics consent banner and legal review (open-decisions) — needed before real GA4/Ads IDs go in.
- [OPEN] Ads are submitted for review by Day 7 but may not serve; do not count that as a failed launch (plan §6).
- [OPEN] Deploy automation (GitHub Actions → `deploy.sh release`): add after the first manual release works.

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: admin MFA, Cloud Run settings (db cache, trusted client IP, www redirect), production image, deploy and backup scripts,
  deployment guide, 35 tests (274 in total).
- 2026-10-27  Deployment adapted to PGLive's shared instance and nginx edge: edge-lock middleware, forwarded-host setting, SQL role script,
  nginx server block + setup script + coexistence test (`deploy/edge/test-travel-edge.sh`, passes against PGLive's real config), 11 new tests
  (466 in total, all passing).
- 2026-10-27  Deployed: project `mytravelplanner-prod`, database `travel_platform` on `pglive-pg-prod`, edge on `pglive-worker` with a Let's
  Encrypt cert (expires 2027-01-25, auto-renews), edge lock on, owner superuser created, daily clearsessions scheduled, launch content seeded.
  `postgres` password reset (owner-approved) and stored as `POSTGRES_ADMIN_PASSWORD` in pglive-prod. No SMTP yet (LEAD_NOTIFY_EMAIL blank).
