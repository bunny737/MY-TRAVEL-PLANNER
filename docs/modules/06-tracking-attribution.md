# Module: Tracking & Attribution

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — code complete; real GA4/Ads IDs, conversion labels and the cookie-consent decision are still needed before ads (see Decisions)
**Phase:** 0
**Plan reference:** docs/execution-plan.md §5 (WhatsApp first flow), §6 (Ads tracking), §9 (Search Console)
**Depends on:** 05
**Blocks:** 07
**App:** `apps.core`

## Purpose
Know which ad click produced which enquiry, count conversions without double-counting, and keep WhatsApp
clicks (intent) separate from confirmed leads — without putting personal data into analytics.

## Scope
- Capture `utm_source/medium/campaign` and `gclid` on first landing into the session (server-side), copy them
  onto the Lead at submit, plus `landing_path`.
- Google tag: GA4 + Google Ads loaded only when the env IDs are set. Events:
  `generate_lead` / Ads conversion on the thank-you page (once), `whatsapp_click` (secondary),
  `call_click` (secondary). Each uses its own conversion label from env.
- WhatsApp CTA: `https://wa.me/<WHATSAPP_NUMBER>?text=<non-sensitive prefill>` e.g.
  "Hi, I want an Araku tour quote for 4 people." — no name/phone in the prefill.
- Sticky mobile CTA (unobtrusive), consistent across pages.
- Search Console verification tag from `GOOGLE_SITE_VERIFICATION`.

## As-built
```
apps/core/middleware.py        AttributionMiddleware: a GET/HEAD carrying utm_source/utm_medium/utm_campaign/gclid writes
                               session['attribution'] = {landing_path (path only), + the non-blank params}. Latest click wins.
                               Skips /static/, /health/, the admin path and non-GET. No params => nothing written, no session row.
apps/core/attribution.py       get_attribution(request): session values, truncated to the Lead column sizes; landing_path falls back
                               to the same-site Referer's PATH (never its query) so organic leads still show the page they filled in
static/js/tracking.js          loads gtag.js and sends events; configured ONLY by data-* attributes (no inline script, reads no
                               form field, cookie or storage)
templates/base.html            <script src=tracking.js defer data-tracking data-ga4-id data-ads-id> only if an ID is set;
                               Search Console <meta> from GOOGLE_SITE_VERIFICATION; {% block sticky_cta %}
templatetags/cta.py            {% whatsapp_cta %} / {% call_cta %}: tracked links, render nothing when the number is blank
templates/partials/            whatsapp_cta.html, call_cta.html, sticky_cta.html (phones only, <=640px; not on enquiry/thank-you/404)
context_processors.py          tracking.ads_{form,whatsapp,call}_send_to = "AW-ID/LABEL", '' unless both ID and label are set
```
Events: `generate_lead` (+ Ads conversion with the form label) from the `data-lead-conversion` marker on `/thank-you/`;
`whatsapp_click` and `call_click` (+ their own Ads conversions) from `data-track` links. Events carry no parameters beyond
`transport_type: beacon` and the Ads `send_to`.
Settings: `WHATSAPP_PREFILL_TEXT` (generic text only), plus the IDs/labels from Module 01.
Tests: `apps/core/test_tracking.py` (35).

## Data model (as-built)
No new tables; attribution fields live on `lead` (module 05). No migration in this module.

## Routes / endpoints
```
GET /thank-you/    renders the conversion marker only on the first view after a NEW (non-duplicate) lead; the view pops the
                   session flag, so refresh/revisit never repeats it                                    public, noindex
```

## Business rules
1. The form conversion fires once per saved lead (session flag), never on reload of the thank-you page.
2. WhatsApp/call clicks are reported as secondary conversions, separate from the primary lead conversion.
3. No name, phone, notes or lead id in any event parameter, URL or tag payload.
4. Tags are absent when their env IDs are blank (local/dev/CI render clean pages).
5. Attribution is stored only when present; a missing `gclid` never blocks a lead.
6. Confirmed WhatsApp enquiries are recorded manually in admin (channel `whatsapp`), not inferred from clicks.

## Permissions
Public (client-side tags). Admin shows source/campaign fields read-only.

## Privacy & claims check
Highest-risk module for invariant 4. Cookie/analytics consent requirements must be settled before ads go live.

## Edge cases handled
-

## Open questions / Decisions
- [DECISION 2026-10-25] Direct gtag (not GTM), loaded from a static file driven by data attributes, so there is no inline script.
- [DECISION 2026-10-25] Only a request with campaign parameters writes a session. Organic visitors and crawlers create no session rows;
  the trade-off is that an organic lead's `landing_path` comes from the Referer header and is blank if the browser sends none.
- [DECISION 2026-10-25] Tags load as soon as an ID is set, with NO consent banner and no Google Consent Mode. That is only acceptable
  while the IDs are blank. Settle the banner question (below) BEFORE putting real IDs in the production env.
- [DECISION 2026-10-25] WhatsApp prefill is generic ("Hi, I want an Araku tour quote.") from `WHATSAPP_PREFILL_TEXT`; the plan's
  "for 4 people" variant would need page-specific text passed to `{% whatsapp_cta text="..." %}` (Module 02/08 pages can do that).
- [OPEN] Cookie consent banner / Google Consent Mode required for GA4/Ads in the target jurisdictions (plan §13) — legal check.
  Blocks real tag IDs in production.
- [OPEN] Real GA4 measurement ID, Ads ID and the three conversion labels (create the conversion actions in the Ads account first).
- [OPEN] Verifying events fire needs a real tag on a staging host with GA4 DebugView / Tag Assistant; tests only prove the markup
  and the once-only server flag, not Google's receipt of the events.
- [OPEN] Enhanced conversions / offline conversion import of `gclid` — deferred; not needed for the ₹5k test.

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: attribution middleware, tracking.js, WhatsApp/call CTAs, sticky mobile bar, once-only conversion marker,
  35 tests; verified a campaign click -> form -> attributed lead against the running container.
