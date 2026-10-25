# My Travel Planner

A travel enquiry and referral website for **Araku Valley, Lambasingi, Vanjangi, Maredumilli and Vizag**.

Travellers browse trips, cabs and stays and send a free enquiry. The founder qualifies it and, **only with the traveller's consent**,
refers it to **one** independent local partner who quotes and delivers the trip.

We are **not** a tour operator, a payment aggregator or an online travel agency. Nothing is booked or paid on the site.

> Concierge MVP: lead handoff is manual, Django admin is the back office, and there is no partner login, billing or checkout.
> Scope, rules and decisions live in [CLAUDE.md](CLAUDE.md) and [docs/execution-plan.md](docs/execution-plan.md).

## What is on the site

### Site map
| URL | What |
|---|---|
| `/` | Homepage: hero, destinations, the first six trips with their prices, explore tiles, how it works, enquiry form |
| `/tour-packages/` | Every published package grouped by destination, then **cabs** (`#cabs`) and **stays** (`#stays`), each card with its "from" price |
| `/<slug>/` | Any published package, cab, stay, guide or blog article (one page type per row in the admin) |
| `/blog/` | Articles, newest first, with destination filter chips (`?destination=araku-valley`) |
| `/destinations/` | Araku Valley, Lambasingi, Vizag, Vanjangi and Maredumilli as cards |
| `/enquiry/`, `/thank-you/` | The enquiry form page and the confirmation page (`noindex`) |
| `/contact/`, `/privacy/`, `/terms/`, `/photo-credits/` | Trust and legal pages |
| `/sitemap.xml`, `/robots.txt`, `/health/` | SEO and health check |

The header has **Tour packages**, **Destinations**, **Cabs & stays** and **Blog** menus, built from the published pages (a menu with nothing
published is hidden, and drafts are never linked). Every content page also shows **related pages** for its destination.

### Page types (all editable in Django admin, no code per page)
| Type | Has a form | Notes |
|---|---|---|
| **Package** | yes | Itinerary examples, inclusions and exclusions, FAQ, dated "from" price and an options list |
| **Cab** | yes | Cabs, tempo travellers and buses: vehicle cards and "questions to ask" instead of a day plan |
| **Stay** | yes | One page per destination (Araku, Lambasingi, Vizag, Maredumilli) listing the partner's properties with a "from" rate **per room per night**; no ratings |
| **Guide** | no | Destination and attraction guides (Borra Caves, Katiki, Chaparai, coffee museum, viewpoints, Kailasagiri, RK Beach...) |
| **Article** | no | Blog posts with a byline of the site team, publish date and read time |

### Stays
Stay pages are quote-based like everything else: the traveller picks "Hotel / stay" in the form (the stay page preselects it) and one partner
replies. Each stay page shows a **Stays and rates** list, for example the Araku page lists six properties from ₹1,800 to ₹3,600 per room per night.
Rates are indicative "from" amounts with their quote date, and availability and room type depend on the traveller's dates.

### Blog
- Posts and guides are plain text with **`## Heading`** lines (anchored, with a contents box from three headings) and **`[photo: key]`**
  lines that insert a licensed library photo with its credit. Everything is escaped, so nothing an editor types can inject markup.
- `/blog/` lists published articles newest first and filters by destination. The filtered address points its canonical back to `/blog/`
  and is not in the sitemap.
- Each article has a breadcrumb (Home > Blog > post), publish date, read time, related pages and a **Share on WhatsApp** link
  (title and address only, no tracking). Five launch articles are seeded: what changes a quote, a 2 day plan, best season,
  a trip from Hyderabad and train or cab.

### Prices
- A "from" amount is copied from a **dated partner quote** into the page's price fields (amount, unit, what it assumes, quote date,
  internal partner). It shows as "From ₹X per couple, based on a local partner's quote dated D Mon YYYY", never names the partner,
  and **hides itself after `PRICE_MAX_AGE_DAYS`** (default 90), so the page falls back to "request a quote".
- A page can also carry a **price options** list (`2 days / 1 night | 15000`) for several durations or several properties.
- Only package, cab and stay pages can hold a price; guides, articles and free text never do. No ratings, reviews or "was" prices.
- 16 pages are priced from the partner's published list: the packages (day trips to 5 day trips, Vanjangi, honeymoon, group) and the four stay pages.
  Cab and tempo/bus pages show no price (the partner shows no per-route fares).

### Launch content (all seeded as drafts)
| Group | Pages |
|---|---|
| Packages (12) | Araku, Lambasingi and Vizag overviews, Vizag to Araku day trip, Araku 2D/1N, Vizag + Araku 3D/2N, Araku + Lambasingi, Vanjangi sunrise, Maredumilli, Vizag/Araku/Lambasingi 4 to 5 days, honeymoon, group |
| Cabs (3) | Vizag to Araku cab, cab service in Vizag, tempo traveller and bus hire |
| Stays (4) | Araku, Lambasingi, Vizag, Maredumilli |
| Guides (14) | Araku Valley, Lambasingi, Vanjangi, Maredumilli, Vizag things to do, plus 9 attraction guides |
| Blog (5) | See above |

The content was written in our own words from the partner's published facts (see [docs/research/partner-facts-2026-10.md](docs/research/partner-facts-2026-10.md)),
with the partner's written OK. Items marked VERIFY there (hours, fees, some prices and the hotel names) must be checked before publishing.

### Enquiries and trust
- **Enquiry form**: consent box unchecked by default and required, honeypot, throttle, de-duplication, service type tour, cab or stay.
  Leads are private and visible only in Django admin; a WhatsApp click is not a lead.
- **Photos**: free-licence images only (CC0, CC BY, CC BY-SA), with alt text and credit on `/photo-credits/`; photos with identifiable people are cropped out.

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
docker compose run --rm web python manage.py seed_site_content       # 34 more draft pages (packages, cabs, stays, guides, blog)
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
| `backend/apps/core/` | models (`Destination`, `ContentPage`, `Lead`, `Partner`), views, forms, admin, tests (419) |
| `backend/apps/core/seed/` | draft page content (`packages`, `transport`, `guides`, `articles`) and the partner price list (`prices`) |
| `backend/apps/core/management/commands/` | `seed_launch_content`, `seed_site_content`, `set_partner_prices` |
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
