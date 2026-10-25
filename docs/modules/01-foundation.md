# Module: Foundation

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — admin MFA deferred to Module 07, see Decisions
**Phase:** 0
**Plan reference:** docs/execution-plan.md §8 (technical choices), §3 Day 2
**Depends on:** none
**Blocks:** 02, 03, 04, 05, 06, 07
**App:** project `config` + `apps.core`

## Purpose
A running Django site in Docker with settings split, a base layout, hardened admin and a health check,
so every later module only adds models, views and templates.

## Scope
- `backend/manage.py`, `config/{settings/{base,dev,prod}.py,urls.py,wsgi.py}`, `apps/core` app skeleton
  (run `django-admin startproject` / `startapp` inside the container; do not hand-write boilerplate).
- Settings read `.env` through `django-environ` (same pattern as the PG project). `prod.py` refuses to start
  without `SECRET_KEY`, `ALLOWED_HOSTS`, `SITE_BASE_URL` and sets HTTPS/HSTS/secure-cookie flags.
- Postgres via `DB_*` env; WhiteNoise for static files; Gunicorn entry for prod.
- `base.html` (mobile-first, `<title>`/meta/canonical blocks, header/footer, skip-link), plain CSS, no JS framework.
- A context processor exposing site config to templates: `SITE_NAME`, `WHATSAPP_NUMBER`, `CONTACT_EMAIL`,
  `CONTACT_PHONE`, `RESPONSE_HOURS_TEXT`, `CONSENT_NOTICE_VERSION`, tracking IDs (invariant 9).
- Admin at `ADMIN_URL_PATH`; owner-only; note MFA approach in Decisions (see below).
- `GET /health/` returns 200 `ok` (no DB detail, no PII).
- `django-extensions` + graphviz so `graph_models` works (dev only).

## As-built layout
```
backend/manage.py                      defaults to config.settings.dev
backend/config/settings/base.py        env via django-environ; Postgres; WhiteNoise; site + tracking config; console logging
backend/config/settings/dev.py         DEBUG default True; adds django_extensions; no WhiteNoise middleware
backend/config/settings/prod.py        fail-fast checks; HTTPS/secure-cookie/HSTS flags; optional Sentry (send_default_pii=False)
backend/config/{urls,wsgi,asgi}.py     wsgi/asgi default to config.settings.prod
backend/apps/core/                     views.py (health), urls.py (namespace "core"), context_processors.py, test_foundation.py
backend/templates/{base,404,500}.html  base blocks: title, meta_description, robots, canonical, extra_head, nav, content, footer, extra_body
backend/static/css/site.css            plain mobile-first CSS, 16px gutter
```
`prod.py` raises `ImproperlyConfigured` for: `DEBUG` true, `SECRET_KEY` default/`change-me*`/under 50 chars,
empty `ALLOWED_HOSTS`, non-https `SITE_BASE_URL`. `/health/` is exempt from the HTTPS redirect.
Base template emits a self-canonical (`SITE_BASE_URL` + path) unless the `canonical` block is overridden, and
`robots` defaults to `index,follow` (utility pages override it).

## Data model (as-built)
None in this module (Django auth/session tables only).

## Routes / endpoints
```
GET  /health/        liveness probe, plain text         public
GET  /<ADMIN_URL_PATH>   Django admin                    owner login
```

## Business rules
1. `prod` settings fail fast when required env vars are missing or `DEBUG` is true.
2. Site config values reach templates only via the context processor (no literals in templates).
3. `python manage.py check --deploy --fail-level ERROR` passes with prod settings and dummy env.
4. `makemigrations --check` is clean.

## Permissions
Admin: superuser only. No public registration, no public login page.

## Privacy & claims check
No personal data. Logging config must not log request bodies. Error pages show no stack traces in prod.

## Edge cases handled
- Compose `web` waits for the `db` healthcheck.
- CRLF/LF: shell/SQL/YAML/Dockerfile files stay LF (`.gitattributes`).

## Open questions / Decisions
- [DECISION 2026-10-25, built in Module 07] Admin MFA: `django-otp` (authenticator app) approved by the owner and built; `INSTALLED_APPS` now
  uses `config.apps.MfaAdminConfig` instead of `django.contrib.admin`, and production refuses to start with MFA off or the default admin path.
  Module 01 itself still ships the non-default `ADMIN_URL_PATH`, 12-char minimum password validator and no public login page.
- [DECISION 2026-10-25] Plain CSS, no build step (Tailwind only if the founder asks).
- [DECISION 2026-10-25] English only at launch (`LANGUAGE_CODE=en-in`, `TIME_ZONE=Asia/Kolkata`); templates do not
  use `{% trans %}`. Revisit if Telugu/Hindi is added.
- [DECISION 2026-10-25] `startproject`/`startapp` were run in the container, then the generated `settings.py` was split
  into the settings package and the unused generated `models.py`/`views.py`/`tests.py` stubs replaced.
- [DECISION 2026-10-25] Footer shows only the copyright line for now; Module 03 adds privacy/terms/contact links.
- [DECISION 2026-10-25] `django-debug-toolbar` dropped from dev requirements (unused).
- [DECISION 2026-10-25] Django 5.2 LTS (same as PG project); plan allows 5.x/6.x — re-check supported versions at build time.
- [DECISION 2026-10-25] Local ports: web 8100, Postgres 5440 (3000/5433/6379/8000 are used by pg-management-web).

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: settings split, site-config context processor, base/404/500 templates, `/health/`, 13 tests
  (health, context processor, admin path/login, prod fail-fast). `check --deploy --fail-level ERROR` passes with prod
  settings (only the HSTS warning remains until HTTPS is verified).
