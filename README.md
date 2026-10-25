# My Travel Planner

A travel enquiry and referral website for **Araku Valley, Lambasingi, Vanjangi, Maredumilli and Vizag**.

Travellers browse trips, cabs and stays and send a free enquiry. The founder qualifies it and, **only with the traveller's consent**,
refers it to **one** independent local partner who quotes and delivers the trip.

We are **not** a tour operator, a payment aggregator or an online travel agency. Nothing is booked or paid on the site.

> Concierge MVP: lead handoff is manual, Django admin is the back office, and there is no partner login, billing or checkout.
> Scope, rules and decisions live in [CLAUDE.md](CLAUDE.md) and [docs/execution-plan.md](docs/execution-plan.md).

## What is on the site
- **Packages, cabs and stays**: one page per search intent, each with an enquiry form and a WhatsApp link.
- **Dated partner prices**: a "from" amount copied from a partner quote, shown with its quote date, never naming the partner,
  and hidden automatically after `PRICE_MAX_AGE_DAYS` (default 90). Only a page's price fields can hold an amount.
- **Guides and a blog**: destination and attraction guides, articles with headings, in-text photos and a destination filter.
- **Listings and menus**: `/tour-packages/`, `/blog/`, `/destinations/`, related pages, menus built from the published pages.
- **Enquiry form**: unchecked consent box, honeypot, throttle, de-duplication, private leads (visible only in Django admin).
- **Photos**: free-licence images only (CC0, CC BY, CC BY-SA), with alt text and credit on `/photo-credits/`.

## Tech stack
Python 3.12, Django 5.2 LTS with server-rendered templates, PostgreSQL 16, plain CSS, no frontend build step.
Gunicorn + WhiteNoise on Google Cloud Run with Cloud SQL in production. Admin protected by `django-otp` (TOTP).
No DRF, SPA, Redis, Celery or WhatsApp API.

## Quick start (Docker)
```bash
cp .env.example .env                       # set SECRET_KEY (any long random string)
docker compose up -d db
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose up -d web                   # http://localhost:8100   (admin: /admin/ unless ADMIN_URL_PATH is changed)
```
Local ports are non-default on purpose: web **8100**, Postgres **5440**.

### Load the launch content
Every page is created as a **draft**; nothing is public until you publish it in admin (Content pages, "Publish selected").
```bash
docker compose run --rm web python manage.py seed_launch_content     # Araku, Lambasingi, Vizag + first drafts
docker compose run --rm web python manage.py seed_site_content       # 32 more draft pages (packages, cabs, stays, guides, blog)
# after creating the Partner row in admin:
docker compose run --rm web python manage.py set_partner_prices --partner "Partner business name"
```
The seed commands never publish, never overwrite a page you edited and are safe to run twice.
`set_partner_prices` never overwrites a price you entered (use `--refresh` to rewrite prices from the same partner).

### Tests
```bash
docker compose run --rm web python manage.py test
```

## Project layout
| Path | What |
|---|---|
| `backend/apps/core/` | models (`Destination`, `ContentPage`, `Lead`, `Partner`), views, forms, admin, tests |
| `backend/apps/core/seed/` | draft page content and the partner price list |
| `backend/templates/`, `backend/static/` | templates, CSS, licensed photos |
| `docs/` | execution plan, module specs, decisions, deployment, ERD, partner fact sheet |
| `deploy/` | Cloud Run deploy script and backup scripts |

## Rules that never bend
The ten invariants are in [CLAUDE.md](CLAUDE.md). The ones that matter most when editing content:
1. **Consent before sharing** a lead with a partner, and only ever to one partner.
2. **A click is not a lead**; only a saved enquiry counts.
3. **Honest claims**: no ratings, reviews, "cheapest", "official" or "guaranteed"; every price dated and sourced.
4. **Lead data is private**: never in URLs, analytics, logs or public endpoints.
5. **Business settings live in env** (see `.env.example`), not in templates.

## Docs
- [Local setup](docs/dev-setup.md) · [Deployment](docs/deployment.md) · [Execution plan](docs/execution-plan.md)
- [Module status board](docs/modules/README.md) · [Open decisions](docs/open-decisions.md) · [Data model (ERD)](docs/erd.png)
