# Module: Content Cluster

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Not Started
**Phase:** 1 (days 8–45) and ongoing
**Plan reference:** docs/execution-plan.md §4 (P1/P2 rows), §9 (months 2–12 content and research)
**Depends on:** 02, 07
**Blocks:** none
**App:** `apps.core` (`ContentPage` rows)

## Purpose
Grow booking-intent coverage with a few original, useful pages, then supporting guides:
`/araku-2-days-tour-package/`, `/vizag-araku-itinerary/`, `/lambasingi-tour-packages/`, later guides/hotel/cab comparisons.

## Business rules
1. No filler or city×duration doorway permutations; each page needs original, dated content (invariant 10).
2. Field notes (drive times, timings, ticket and cab costs, holiday surge) carry a verified date and are refreshed.
3. Guides link internally to the commercial pages; commercial pages keep the form + WhatsApp CTA.
4. New pages are added only when real search-term or partner evidence supports them.
5. Competitor sites are research only; never copy text, prices or images.

## Privacy & claims check
Original or licensed photos only; meaningful alt text; no fabricated schema.

## Open questions / Decisions
- [DECISION 2026-10-25] Owner: the site covers Araku Valley, Lambasingi and Vizag from launch. `seed_launch_content` already creates
  DRAFT `/lambasingi-tour-packages/` and `/vizag-tour-packages/` pages (no prices, notes on what to verify) and the `/destinations/` hub
  exists (Module 02). This module starts from those drafts rather than writing them again.
- [DECISION 2026-10-25] Owner: build the full set of pages BEFORE launch (pulled forward ahead of Module 07 go-live, like Module 08), written from the
  partner's published facts in our own words, with the partner's written OK. One page per search intent, no city x duration copies. Code
  (stay/article types, blog, listings, dated prices) is in Module 02's "Full site build" section.
- [OPEN] Which pages first — decide from the first ad test's search-term report (after launch; the launch set was chosen by the owner).
- [OPEN] Peak-season (Oct–Feb) field trip to collect original notes/photos before Oct 2027 content maturity.

## Launch set (built 2026-10-25): `python manage.py seed_site_content`
32 DRAFT pages plus the Vanjangi and Maredumilli destinations, written in our own words from `docs/research/partner-facts-2026-10.md`
(source: the partner's public site, read 2026-10-25; every VERIFY item there is left out or phrased loosely). The data lives in
`apps/core/seed/` (`packages.py`, `transport.py`, `guides.py`, `articles.py`, helpers in `common.py`). The command never publishes, never sets a price,
never overwrites an existing page and is safe to run twice.
- **Packages (9):** Vizag to Araku day trip; Araku 2D/1N; Vizag + Araku 3D/2N; Araku + Lambasingi (2 or 3 days); Vanjangi sunrise; Maredumilli; Vizag, Araku
  and Lambasingi 4 to 5 days; Araku honeymoon/couple; Araku group. (Plus the 3 earlier drafts: Araku, Lambasingi, Vizag.)
- **Cabs (2):** cab service in Vizag; tempo traveller and bus hire. (Plus the earlier Vizag to Araku cab draft.) Kakinada cab was left out: the partner's
  coverage of Kakinada is unknown.
- **Stays (2):** Araku; Lambasingi. No property names, ratings or stock photos of named hotels.
- **Guides (15):** Araku Valley, Lambasingi, Vanjangi, Maredumilli, Vizag things to do; Borra Caves, Katiki, Chaparai, Padmapuram, coffee museum and plantations,
  Tribal Museum, viewpoints, Kailasagiri, RK Beach.
- **Blog (5):** what changes the quote; Araku in two days; best time; trip from Hyderabad; train or cab.
- Tests (`test_site_seed.py`, 17): all drafts, idempotent, no overwrite, no price set, unique titles/descriptions/slugs, every page passes the publish checks,
  one H1 and a self-canonical, no ₹/price words/forbidden claims/partner branding/ratings, notes never rendered, distances only on pages whose notes flag
  them for checking, listings, blog and sitemap pick the pages up. 394 tests pass in total.
- [OPEN] Owner steps before publishing: the partner's written OK; dated quotes entered in each page's Price fieldset (never copied from their site);
  the VERIFY items in the fact sheet; publish page by page (admin action "Publish selected").
- [DECISION 2026-10-25] Owner: put the partner's same prices on our pages. `python manage.py set_partner_prices --partner "<Partner business_name>"`
  (`apps/core/seed/prices.py`) fills the dated "from" price on 9 package pages (day trip 6,000; Araku 2D/1N 9,000; Vizag + Araku 3D/2N 18,000;
  Araku + Lambasingi 15,000; Vanjangi 11,999; Maredumilli 18,500; Vizag, Araku and Lambasingi 5D/4N 34,500; honeymoon 6,000; group 18,000 per vehicle
  trip; all INR, per couple unless stated). Quote date 24 Oct 2026: the partner's site prints that date on only three of these pages (day trip,
  Vizag + Araku 3D/2N, 5D/4N); for the other six the owner chose the same date, and each page's internal notes say so. Left out because the
  partner shows no date anywhere for them: cab fares, tempo/bus rates, hotel rates. Never overwrites an existing price; hides itself after 90 days.
  Tests: `PartnerPriceTests` in `test_site_seed.py` (402 tests pass in total).
- [DECISION 2026-10-25] Owner: show the packages AND hotels with the same prices as the partner site. Done: `set_partner_prices` now fills 16 pages with their
  option lists (`--refresh` rewrites pages priced by the same partner). Packages: every duration the partner lists (Araku, Vizag, Araku + Lambasingi,
  Vanjangi, honeymoon, group, Vizag/Araku/Lambasingi 4 to 5 days). Hotels: one stay page per destination (Araku, Lambasingi, Vizag, Maredumilli: the last two
  are new) listing the partner's six properties each with a "from" rate per room per night. No ratings are shown. The partner's hotel pages show no date,
  so the same 24 Oct 2026 date was used. 419 tests pass.
- [OPEN] The hotel names look like template placeholders (the partner advertises "12+ hotels" and lists six, with stock photos). VERIFY every property exists
  before publishing; delete any line you cannot confirm from the page's Price options field.
- [OPEN] Ask the partner to confirm the undated prices, and to give dated figures for cabs (per route) and tempo/bus hire if they want those shown.
- [DONE 2026-10-25] Photos for Vanjangi and Maredumilli added (Module 02, "Full site build").
- [OPEN] The "partner-owned photo" licence type is not built: it is only needed if the partner sends photos they own (with a written licence).
- [DECISION 2026-10-25] Owner: the partner has given their written OK to use their published facts and to show their dated quotes. (Photos:
  none were supplied, so none were used.)

## Changelog
- 2026-10-25  Full-site build pulled forward: dated prices, stay/article types, blog, listings, related pages, nav menus (Module 02 "Full site build"),
  partner fact sheet, `seed_site_content` with 32 draft pages (see "Launch set").
- 2026-10-25  Created stub from the project setup.
