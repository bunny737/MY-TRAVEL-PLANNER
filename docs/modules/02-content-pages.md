# Module: Content Pages

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — code complete; the Araku page exists only as a DRAFT seed that you must review, complete and publish (see Decisions)
**Phase:** 0
**Plan reference:** docs/execution-plan.md §4 (page architecture, landing checklist), §9 (SEO)
**Depends on:** 01 (built after 05 and 06 at the owner's request)
**Blocks:** 08, 09, 10
**App:** `apps.core`

## Purpose
Serve the homepage and the commercial landing page (`/araku-tour-packages/`) from content edited in Django admin, with correct
SEO basics. Later pages (cab, 2D/1N, itinerary, Lambasingi, guides) are just more `ContentPage` rows — no new code per page.
**Pages never state a price** (owner decision 2026-10-25): there are no price fields, and every page invites a free quote instead.

## Data model (as-built) — migrations core.0003, core.0004 (adds `hero_image`)
```
Table: core_destination
  id, name, slug (unique), summary, is_active, sort_order

Table: core_contentpage
  id
  destination FK → core_destination, null, SET_NULL
  page_type: home | package | cab | guide
  title (150)                    the H1
  slug (unique)                  home row is forced to "home"; reserved: admin path, static, media, health, contact, privacy,
                                 terms, enquiry, thank-you, sitemap, robots, home
  sort_order                     lower = listed first on the homepage
  intro, duration, body          plain text; body = paragraphs separated by a blank line
  itinerary, faq                 text blocks separated by a blank line: first line = heading/question, rest = text
  inclusions, exclusions         one item per line
  hero_image (40)                key of a photo in apps/core/images.py; blank = default photo for the page type
  meta_title (70), meta_description (170), canonical_override
  status: draft | published      published_at is stamped once when first published
  updated_at (auto)              shown as "Last updated" on the page
  internal_notes                 never rendered
  constraint only_one_homepage   at most one row with page_type=home
```
All content is plain text rendered escaped, so an editor cannot inject markup (parsers in `apps/core/content.py`).
Package fields are columns on `ContentPage` (no extra model, invariant 8).

## Routes / endpoints
```
GET  /                         homepage: the published `home` row, else a built-in default (never 404)        public
GET  /<slug>/                  any published package / cab / guide page; drafts and the home row 404; LAST url pattern
GET  /sitemap.xml              homepage + published pages (canonical URLs, lastmod) + contact/privacy/terms
GET  /robots.txt               Disallow: <admin path>, /thank-you/ ; Sitemap line
GET  /photo-credits/           author, licence and source of every photo; noindex; linked from every footer
GET  /destinations/            every active Destination as a card (photo, summary, live pages, quote button); indexable, in sitemap
```

## Destinations (added 2026-10-25, owner request: "tours are not only for Araku")
- **Data:** `Destination.hero_image` (migration core.0005, validated against the photo registry like `ContentPage.hero_image`) and
  `hero_key` (falls back to the default photo). `'destinations'` is a reserved slug.
- **Navbar:** a "Destinations" menu (`{% destination_menu %}` in `templatetags/destinations.py`, a no-JS `<details>` dropdown; inline
  in the mobile menu) lists active destinations in `sort_order`. Each links to its first *published* page (package, then cab, then
  guide), else to its card at `/destinations/#<slug>`. Drafts are never linked. The footer "Destinations" column uses the same tag.
- **Homepage:** region-wide default copy ("Plan your Araku, Lambasingi or Vizag trip"), a "Where would you like to go?" band of
  destination cards (`{% destination_cards %}`, shared with the hub), Explore tiles from all three places.
- **Content pages:** the hero pill shows the page's destination; the photo strip shows only photos of that destination
  (`Photo.place`), and is hidden when fewer than two are left.
- **Photos:** 4 more Commons photos (all CC BY-SA 4.0, licence checked on each file page, no identifiable people):
  `lambasingi-valley`, `lambasingi-clouds`, `kailasagiri-coast`, `rushikonda-beach`. The library is now about 2.9 MB; the test cap
  is 3.5 MB because a page loads only its own few photos.
- **Seed:** Araku Valley (10), Lambasingi (20), Vizag (30) with summaries and photos (an existing row only gets blank fields and a
  default sort order filled); DRAFT `lambasingi-tour-packages` and `vizag-tour-packages` pages alongside the Araku draft.
- **Copy:** default `WHATSAPP_PREFILL_TEXT` is now "Hi, I want a tour quote."; the enquiry notes placeholder asks which places.
- Tests: `test_destinations.py` (21).

## Photos (added 2026-10-25) — see also docs/dev-setup.md "Adding a photo"
- **Library:** 9 free-licence photos of Araku Valley from Wikimedia Commons (8 × CC BY-SA 4.0 / 2.0, 1 × CC0), each licence checked on its
  file page. Source files are cropped/resized by `scripts/optimize_photo.py` into `static/img/photos/<stem>-800|1600.webp` (about 1.9 MB
  in total, no EXIF/GPS). None shows an identifiable person; the three Unsplash candidates could not be downloaded automatically
  (Unsplash blocks scripts) and were not used.
- **`apps/core/images.py`** is the single source of truth: key, files, size, **alt text**, title, author, licence, source URL, "what we changed".
  Alt text therefore can never be missing, the credits page is generated from it, and the admin dropdown reads it.
- **`{% photo key %}`** (`templatetags/photos.py`) renders `<img>` with `srcset`, `sizes`, intrinsic `width/height` (no layout shift) and the registry alt;
  the one top-of-page image is eager with `fetchpriority="high"`, everything else is `loading="lazy"`. `{% photo_url %}` gives the absolute URL for link previews.
- **Where they appear:** homepage hero (photo + dark pine wash, white text, gold primary button), card header on every trip card
  (`page.hero_key`), banner on content pages, a gallery strip ("Scenes from Araku Valley" / "Along the route") whose caption says the photos
  show the region and are not our partners' vehicles or services, and Open Graph/Twitter preview tags (WhatsApp shows the page's photo).
- **Rules (tests in `test_photos.py`, 41):** every registered file exists and is within size limits; registered size matches the file; alt text present;
  licence is CC0/BY/BY-SA only (never NC/ND); no unlisted files; no hot-linking of other sites' images; one eager image per page; credits page lists
  every photo and is `noindex`; `hero_image` must be a registry key.
- **Layout (owner request):** `.container` is `width: 90%` (capped at 1800px on very large monitors); long prose keeps a 78ch line length; the form
  becomes 3 columns and FAQs 2 columns from 1200px.
- **Colours:** superseded by "Page layout v2" below.

## Page layout v2 (2026-10-25) — reference: araku-valley.com, layout and colours only
Owner asked for pages like araku-valley.com, "take reference and colors, do not copy". Nothing was copied (no text, images or code);
the structure was re-implemented in our own templates/CSS and its colour palette adopted:
- **Palette (tokens at the top of `site.css`):** forest green `#2d6a4f` (primary), deep green `#1f4a37`, mint `#52b788` (decorative), saffron `#e9a84c`
  (main button, always with dark text), terracotta `#c4622d` (decorative; `#a9501f` for small text), cream `#fffbf4` page, mint `#eff7f2` and sand
  `#f4e9d8` bands, charcoal `#1c1c1e` footer, warm-brown body text. Every text pair is AA (4.5:1) and tested (`test_layout.ColourContrastTests`).
  The reference puts white text on saffron (2.1:1); we do not.
- **Structure:** `<main>` is full width; pages put edge-to-edge bands in `{% block page_header %}` / `{% block after_content %}` and their body in
  `.container.page-body` (still 90% wide). The homepage overrides `{% block main %}`.
- **Homepage:** full-width photo hero (centred title, location pill, place keywords, saffron + WhatsApp pills, scroll cue) → white "promise" strip
  overlapping the hero (free to ask / local partners / one partner only with your OK / reply hours) with the referral disclosure → trip cards (cream)
  → "Explore Araku" photo tiles (mint; `images.HIGHLIGHTS`, six places with factual one-line blurbs) → how it works (cream) → enquiry form on the
  forest-green band → "Have a question first?" WhatsApp/call band (sand, only when a number is configured).
- **Package/cab/guide pages:** full-width photo hero with breadcrumb, title, intro and CTAs → overlapping fact strip (trip length, type, "free to
  request a quote", last updated) → content column + enquiry card beside it (package/cab) → closing forest-green CTA band.
- **Inner pages** (contact, enquiry, privacy, terms, credits, 404): mint header band (`partials/page_header.html`) with eyebrow, H1, lead; contact uses
  icon rows; enquiry has a "What happens next" side card; legal text sits in a white card.
- **Header/footer:** cream sticky header with phone (when set), WhatsApp and saffron "Get Free Quotes"; four-column charcoal footer (brand, explore,
  trust & legal, get in touch with tracked WhatsApp/call links and reply hours).
Page layout (`templates/pages/content_page.html`): breadcrumb, H1, last-updated, trip length, intro, CTA row (Get free quotes +
WhatsApp with a page-specific prefill), the enquiry form (package/cab pages; service pre-selected), example itinerary, "What a
quote usually includes / is usually not included" (only if filled), body, FAQ, and a second CTA row. Guides get CTA links instead of
a form. Homepage: hero (plan §2 copy by default), referral disclosure, "Trips you can ask about" cards, optional body, form.
Admin: ContentPage list with filters, "Publish selected" (runs full validation, reports what is missing), "Unpublish selected", live-page link.

## Business rules (each has a test in apps/core/test_content.py, 54 tests)
1. Only `published` pages render; drafts and the home row are not served at `/<slug>/`.
2. Every page has one H1, a unique `<title>` and meta description (duplicates are refused when saving, case-insensitively), and a
   self-canonical unless `canonical_override` (https URL or a `/path`) is set.
3. No prices anywhere: no price fields; a test scans rendered pages (and the seed) for ₹ / Rs / INR / "price".
4. The sitemap lists indexable pages only; form, thank-you, admin and health URLs are never listed. `/enquiry/` stays crawlable
   (it is linked and `noindex`; blocking it in robots.txt would hide the noindex).
5. Each page carries the referral disclosure next to its CTAs, one form (package/cab/home), and WhatsApp CTAs near the top and after the content.
6. Structured data is limited to `BreadcrumbList` (escaped so a title cannot close the script tag); no Review/Product/Offer/rating markup.
7. Slugs cannot collide with other routes or the configured admin path; only one homepage row can exist.
8. Publishing requires a meta description and an intro.

## Permissions
Public read. Editing only in admin by the owner.

## Privacy & claims check
No personal data. No ratings, reviews or prices; no "cheapest/guaranteed/verified/official" wording (scanned in tests). Do not name
partners on a page without their consent.

## Seed content (`python manage.py seed_launch_content`)
Creates the "Araku Valley" destination and a **draft** `araku-tour-packages` page (title, search title/description, intro, a
day-trip and a 2D/1N example itinerary, five FAQs that describe our referral role). It never publishes, never overwrites an
existing page, and leaves **inclusions/exclusions empty on purpose**. The text was written from general knowledge, not field
research: `internal_notes` on the page lists what to verify (stops, order, drive time, seasonal waterfalls) before publishing.
The same command also creates the Lambasingi and Vizag package drafts and, since Module 08, the `vizag-to-araku-cab` draft (see 08-cab-page.md).

## Edge cases handled
- No `home` row: a default homepage renders so the site works on day one.
- Empty itinerary/FAQ/inclusion sections are not rendered at all.
- Canonical override as a path or as an https URL; sitemap uses the override.
- Admin path renamed in `.env`: robots.txt and the reserved-slug check follow it.

## Open questions / Decisions
- [DECISION 2026-10-25] Owner: no package prices on the site. `price_updated_on` and price-source ideas from the original spec are dropped;
  pages say "Independent local partners prepare quotes for your dates and group size. Asking is free."
- [DECISION 2026-10-25] Content is plain text in structured admin fields (line/blank-line formats described in each field's help text),
  not Markdown or a rich editor: no new dependency, nothing to sanitise, and the founder edits it in admin.
- [DECISION 2026-10-25] Package fields are text columns, not a JSONField: editable by hand in admin without writing JSON.
- [DECISION 2026-10-25] Module 02 was built after 05 and 06; the form (`{% enquiry_form %}`) was already reusable, so the pages just embed it.
- [DECISION 2026-10-25] Photos are static files chosen from a code registry, not uploads: no media storage, no hosting dependency, and alt text and
  credits cannot be skipped. Pillow was added to `requirements/dev.txt` ONLY (the optimiser script); it is not installed in production.
- [DECISION 2026-10-25] Owner chose free stock photos. Only Wikimedia Commons photos with a verified CC0 / CC BY / CC BY-SA licence are used, with the
  credit and "cropped and resized" note on `/photo-credits/`. CC BY-SA applies to the photo only, not to the site. Alt text describes what is
  visible and names Araku only where Commons categorises the photo there.
- [DECISION 2026-10-25] Owner: brand "My Travel Planner", domain mytravelplanner.in, canonical host without www (www redirects at the proxy).
- [DECISION 2026-10-25] Header navigation added with primary links (Home, Araku Packages, Request Quote, Contact, WhatsApp CTA, and Get Free Quotes action button) using accessible pure CSS mobile toggle to adhere to CSP rules (no inline scripts).
- [DECISION 2026-10-25] Elevated page aesthetics in site.css with an Eastern Ghats travel design system (curated emerald & gold palette, Plus Jakarta Sans & Inter typography, timeline itinerary layout, comparison cards for inclusions/exclusions, FAQ cards, and responsive form grid).
- [DECISION 2026-10-25] Reference-site sections we deliberately left out: **testimonials** (we have no genuine reviews; invariant 3 — a test
  checks the homepage has no review/rating wording), **package prices and "offers"** (no prices, owner decision), **resorts, travels, blog and
  destination pages** (not in Phase 0; cab page = Module 08, guides/destinations = Module 10). Their "key facts" strip (altitude, temperatures,
  distances) was not reproduced with numbers, because we have no sourced figures; our fact strip shows only page data.
- [DECISION 2026-10-25] Fonts stay Plus Jakarta Sans + Inter (the reference uses Poppins + Inter); switching is a one-line change in `base.html` if wanted.
- [DECISION 2026-10-25] Fixed an existing bug while restyling: `a.button` forced white text, so outline link buttons were white on white.
- [OPEN] Review and publish the seeded Araku draft; add inclusions/exclusions only from operators' confirmed quotes.
- [OPEN] Replace stock photos with your own (or partners' with written consent) once you have field photos: add them to the registry, same process.
- [OPEN] Three Araku photos on Unsplash look suitable (tagged Araku, free licence) but must be downloaded by hand from the site; send the files if wanted.
- [DECISION 2026-10-25] Owner: trips cover Araku Valley, Lambasingi and Vizag, not Araku only. Menu, footer, homepage and the new
  `/destinations/` hub are built from `Destination` rows, so publishing a page in admin updates them; nothing is hard-coded. The
  Lambasingi and Vizag drafts are seeded ahead of Module 10 at the owner's request (drafts only; the owner verifies and publishes).
- [DECISION 2026-10-25] No destination field on the enquiry form (owner chose the hub page instead); travellers name places in the notes.
  Adding one is a Lead schema change; revisit if leads arrive without a destination.
- [DECISION 2026-10-25] Distances and temperatures were left out of the new drafts (no source); a test rejects "<n> km" and degrees on them.
- [OPEN] Review and publish the Lambasingi and Vizag drafts after checking the stops with operators.
- [OPEN] Guides are linked from their destination's card on `/destinations/` once published; add in-page links from related pages (Module 10).

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: Destination + ContentPage + migration core.0003, homepage and content-page views/templates, sitemap, robots,
  breadcrumb markup, admin with publish/unpublish actions, seed command, 54 tests; ERD regenerated; previewed against the running container.
- 2026-10-25  Photography: image registry, `{% photo %}` tag, `hero_image` field (core.0004), photo hero / cards / banners / gallery, `/photo-credits/`,
  Open Graph tags, favicon, 90% content width, WebP MIME type, 41 tests (224 in total); ERD regenerated.
- 2026-10-25  Page layout v2 modelled on araku-valley.com (layout and palette only): full-width bands on every page, new homepage sections
  (promise strip, explore tiles, green enquiry band), photo hero + fact strip + form aside on content pages, mint page headers, charcoal footer;
  `test_layout.py` (13 tests) incl. AA contrast checks; 239 tests pass.
- 2026-10-25  Visual design overhaul and header navbar implementation: full responsive navigation menu, brand emblem, modern typography, timeline itinerary styling, inclusions/exclusions comparison grid, FAQ cards, and refined form layout; all 183 tests pass.
- 2026-10-25  Destinations: Destination.hero_image (core.0005), Destinations menu + footer, `/destinations/` hub, homepage destination
  band, per-destination photo strips, 4 Lambasingi/Vizag photos, Lambasingi and Vizag draft pages in the seed; 295 tests pass; ERD regenerated.
