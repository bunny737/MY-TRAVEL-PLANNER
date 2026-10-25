# CLAUDE.md — Agent Rules

Read this file at the start of every session before writing any code.

## What we are building
A travel enquiry and referral website (launch region: Araku Valley, Vizag, Lambasingi).
Travellers submit a free enquiry (short form or WhatsApp); the founder qualifies it and, with the
traveller's consent, refers it to one independent local tour/cab partner who quotes and delivers the trip.
We are **not** a tour operator, payment aggregator or online travel agency. Source of truth for scope,
copy, ads and economics: [docs/execution-plan.md](docs/execution-plan.md) (v3.0, 2026-10-25).

Concierge MVP: lead handoff is manual, Django admin is the back office, no partner login, no billing
software, no customer checkout. First public launch target: **2026-10-31**.

**Website only (owner decision 2026-10-25).** No mobile app (Flutter/native), no PWA/service worker, no push
notifications, no public REST API. Mobile visitors are served by the responsive website.

## Locked tech stack — do not deviate
- Backend: Python 3.12, Django 5.2 LTS, server-rendered Django templates. No DRF, no SPA, no Next.js.
- DB: PostgreSQL 16 (Docker for dev). No Row-Level Security — single-tenant, owner-only admin.
- Frontend: plain CSS (Tailwind only if the founder asks), minimal JS. No frontend build step at launch.
- No Redis, no Celery, no WhatsApp API at launch. WhatsApp = dedicated **WhatsApp Business app**
  (quick replies + labels) reached through a `wa.me` link.
- Serving: **Google Cloud Run + the existing Cloud SQL (PostgreSQL) instance** (owner decision 2026-10-25): Gunicorn + WhiteNoise in the image from
  `backend/Dockerfile.prod`, HTTPS terminated by Google. Release with `deploy/cloudrun/deploy.sh`; steps in docs/deployment.md.
- Admin second factor: **django-otp** (TOTP authenticator app), mandatory in production (owner decision 2026-10-25).
- Analytics/ads: GA4 + Google Ads tag (via Google tag/GTM) + Search Console.
- Local Docker uses **non-default ports** (web 8100, Postgres 5440) so it runs beside other projects.

## 10 Non-negotiable invariants

1. CONSENT BEFORE SHARING: A lead's details are shared with a partner only after consent is recorded
   on the Lead (`consent_given`, `consent_at`, `consent_notice_version`, `consent_source`). The form
   checkbox is unchecked by default and separate from any marketing consent. A WhatsApp click is
   not consent. First referral goes to ONE selected partner; never broadcast.

2. CLICK ≠ LEAD: A WhatsApp click or call click is a micro-conversion, not a lead. Only a saved
   Lead (form) or a manually recorded confirmed WhatsApp enquiry counts as an enquiry. Keep form,
   WhatsApp-click and confirmed-enquiry numbers separate; the form conversion is de-duplicated.

3. HONEST CLAIMS: We are a referral platform. Never write "cheapest", "official", "guaranteed",
   "instant confirmation", invented ratings/reviews, fake scarcity, or an unsourced price. Every
   price shown is a dated, sourced range or "request a current quote". Package and cab pages show NO
   prices at all (owner decision 2026-10-25); they invite a free quote. Never imply Andhra Pradesh
   tourism affiliation. Partner claims are published only with the partner's consent.

4. LEAD DATA IS PRIVATE: No lead endpoint that returns data publicly. No personal data in URLs,
   GA4/Ads events, logs or error reports. Thank-you and utility pages are `noindex`. Lead data is
   visible only in Django admin (owner login, MFA when available). Collect the minimum fields.

5. CHARGE ONLY FOR CONFIRMED BOOKINGS: ₹1,000–₹2,000 per verified converted booking, ₹0 for raw
   enquiries. Do not build invoicing/billing before the first fee is actually collected (Module 12 is
   gated on that). Fee range, attribution window (30 days) and pilot size (2–3) are config/docs,
   never scattered literals.

6. MONEY = Decimal always. Never float. `DecimalField(max_digits=12, decimal_places=2)` (INR).

7. LEAD STATUS LIFECYCLE is exact and a single enum:
   `new → qualified → referred → partner_responded → won | lost`, plus `spam`, `invalid`, `withdrawn`.
   Timestamps (`qualified_at`, `referred_at`, `partner_responded_at`) are set on the transition.

8. SMALLEST SCOPE: MVP has exactly four core models — `Destination`, `ContentPage`, `Lead`, `Partner`.
   Anything beyond (LeadAssignment, LeadEvent, quote tables, partner portal, automation) is a stop-and-ask
   and is triggered by volume, not by guesswork (execution plan §8 "Phase 1/2 triggers").

9. NO HARDCODED BUSINESS CONFIG: WhatsApp number, contact email/phone, published response hours,
   consent-notice version, GA4 / Ads IDs and conversion labels, lead-notification email live in
   settings/env (see `.env.example`), not in templates or views. Response hours shown on the site
   must match the Ads schedule (execution plan §5, §6).

10. SECURITY & CONTENT BASELINE: HTTPS only, CSRF on, server-side validation on every field,
    throttle + honeypot on the lead form, secrets from env, DEBUG off in prod, daily DB backup with a
    tested restore. Content is original: no copied competitor text, licensed/owned photos only,
    every page has a unique title/meta description/canonical.

## Build order — strict dependency sequence
Week-one launch scope (Phase 0), then post-launch phases:

01 foundation → 02 content-pages → 03 trust-legal → 04 partners → 05 leads → 06 tracking-attribution
→ 07 launch-deployment
→ (Phase 1, after launch) 08 cab-page → 09 cost-estimator → 10 content-cluster
→ (Phase 2, volume/cash triggered) 11 lead-assignment-crm → 12 referral-fees

Do not build 08+ before module 07 is ✅ and the first ad test has produced evidence.

## Per-task workflow
1. Read this file + the relevant docs/modules/<nn>-*.md spec + the matching section of docs/execution-plan.md
2. Check all dependencies are ✅ in docs/modules/README.md
3. Implement: model → migration → form/view → template → admin → test
4. Write tests for every business rule (each rule in the spec maps to a test); consent and
   "no personal data leaks" rules always get a test
5. Any model or DB schema change (new/changed model, field, constraint):
   a. `docker compose run --rm web python manage.py makemigrations`
   b. `docker compose run --rm web python manage.py migrate` — confirm it applies cleanly
   c. Regenerate the ERD and commit it in the same commit (see docs/dev-setup.md):
      `docker compose exec web python manage.py graph_models -a -o erd.png`
      then move the file to `docs/erd.png`
6. Update the module spec to match what was actually built (same commit)
7. Update docs/modules/README.md status
8. Record every judgement call in the module spec under "Decisions"

## When to stop and ask (do not guess)
- The task needs a fifth model, a new dependency, or a cross-module schema change
- Anything touching consent wording, data sharing, or what is sent to Google/analytics
- Any user-facing price, claim, partner name, rating or "verified" badge without a sourced input
- Anything that sends messages automatically (WhatsApp API, SMS, bulk email) or auto-forwards leads
- Anything that moves money or adds billing, partner login, or checkout before Module 12's trigger
- Ads work: budgets, schedules, keywords, geo targeting — the plan's numbers are hypotheses; confirm first
- Brand is "My Travel Planner" at mytravelplanner.in (canonical, no www; owner decision 2026-10-25). Still read the name from `SITE_NAME` in env, never hardcode it
- New photos: only CC0 / CC BY / CC BY-SA or the owner's own, added through `apps/core/images.py` (alt text and credit are mandatory), never hot-linked
