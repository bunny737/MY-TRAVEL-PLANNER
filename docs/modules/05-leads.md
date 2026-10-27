# Module: Leads

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — built without Module 02: the form is a reusable template tag plus a standalone `/enquiry/` page
**Phase:** 0
**Plan reference:** docs/execution-plan.md §5 (lead capture, consent, manual routing, statuses)
**Depends on:** 02, 03, 04
**Blocks:** 06, 09, 11
**App:** `apps.core`

## Purpose
Capture an enquiry from the short form (and let the founder record confirmed WhatsApp/call enquiries),
store the consent that allows sharing, and let the founder qualify and manually refer it to one partner.

## Data model (as-built)
```
Table: core_lead   (apps.core.models.Lead, migration core.0002)
  id
  name (120), phone (normalised +91…/+intl)          required
  service_type: tour | cab | stay                    required (stay added 2026-10-25, migration core.0006; stay pages preselect it)
  travel_date_or_month (60, free text), travellers (1–100)   required
  pickup_city (80), budget (60, free text), notes (≤1000 via form)   optional
  status: new | qualified | referred | partner_responded | won | lost | spam | invalid | withdrawn   (default new)
  partner FK → core_partner, null, on_delete=PROTECT, related_name=leads
  lead_channel: form | whatsapp | call | manual      (default manual; the form sets form)
  is_duplicate bool
  landing_path (200), utm_source/medium/campaign (100), gclid (255)     blank unless Module 06 supplies them
  consent_given bool (default False), consent_at, consent_notice_version (40), consent_source: form|whatsapp_reply|call|manual
  created_at, qualified_at, referred_at, partner_responded_at
  founder_notes
  indexes: status; (phone, service_type, created_at)
```
Money fields (e.g. booking value) are NOT in this module — they belong to module 12. `budget` is deliberately free text
(visitors write "around 20k"); nothing computes with it.

Supporting code: `forms.py` (EnquiryForm incl. honeypot field `website`), `throttle.py` (file-cache counters, per client IP),
`attribution.py` (`get_attribution(request)` reads `session['attribution']`, which Module 06 writes),
`notifications.py` (`notify_new_lead`), `templatetags/enquiry.py` (`{% load enquiry %}{% enquiry_form %}` — put the form on any page;
it posts to `/enquiry/`), `templates/partials/{enquiry_form,form_field}.html`, `templates/pages/{enquiry,thank_you}.html`.
Settings: `LEAD_FORM_THROTTLE` ("count/seconds"), `LEAD_DUPLICATE_WINDOW_HOURS` (24), `LEAD_NOTIFY_EMAIL`, `CLIENT_IP_HEADER`,
`CACHES` (file-based so all Gunicorn workers share counters, no Redis; on Cloud Run `CACHE_BACKEND=db` shares them across instances;
`CLIENT_IP_TRUSTED_HOPS` picks the right-most trusted entry of `X-Forwarded-For`; see Module 07).
Session flags (booleans only): `lead_conversion_pending` (Module 06 consumes it on `/thank-you/`) and `lead_consented`.

## Routes / endpoints
```
GET  /enquiry/       standalone form page, noindex                                  public
POST /enquiry/       validate → save Lead → redirect /thank-you/ (throttled 429)   public, CSRF, never returns lead data
GET  /thank-you/     confirmation (text depends on consent), noindex,nofollow, no-cache   public
```
Admin (`core_lead`): changelist filters (status, channel, service, consent, duplicate, campaign), search name/phone, date drill-down;
actions "mark qualified" (new only), "mark spam", "mark invalid" (new/qualified only); lead channel editable on add only;
consent time and notice version, attribution and timeline fields read-only. Partner changelist shows
"N of PILOT_REFERRALS_PER_PARTNER free" (+ "pilot used up"); spam/invalid leads are not counted.

## Business rules
1. Name, phone, service, travel date/month and travellers are required; phone and counts validated server-side.
2. Consent checkbox is unchecked by default; the form is rejected for tracking-as-consent shortcuts — a lead
   saved without consent has `consent_given=False` and cannot be assigned a partner.
3. On save: `consent_at` and `consent_notice_version` (from env) are stored with `consent_source`
   (`form` | `whatsapp_reply`). WhatsApp YES replies are entered manually by the founder.
4. Status transitions stamp `qualified_at`, `referred_at`, `partner_responded_at` exactly once.
5. Assigning a partner requires `consent_given`, an active partner, and moves status to `referred`.
6. Honeypot field + per-IP throttle (`LEAD_FORM_THROTTLE`); a throttled or honeypot hit saves nothing and
   shows a neutral message.
7. Duplicate submissions (same phone + service within a short window) are flagged, not double-counted
   (conversion event fires once per saved lead).
8. Optional founder notification email on new lead; it contains no more PII than needed (name + admin link).

## Permissions
Public: submit only. Owner: everything, in admin. No endpoint ever returns lead data to the public.

## Privacy & claims check
Phone/name never appear in URLs, query strings, analytics events or logs. Thank-you URL carries no lead id.
Lead rows are included in DB backups, which are therefore PII — treat accordingly (module 07).
First referral goes to ONE partner; broader sharing needs fresh consent recorded.

## Edge cases handled
-

## Tests
`apps/core/test_leads.py` (55 tests): required fields and server-side validation, CSRF, consent (unchecked by default, time/version/source
recorded, no partner without consent), status enum and once-only stamps, partner-assignment rules, throttle (per IP, proxy header,
spoofed X-Forwarded-For ignored), honeypot, duplicates, notification content, attribution copy/truncation, privacy (no public
data route, no identifiers in the thank-you URL, no PII in logs or session), admin filters/actions/manual WhatsApp lead.

## Open questions / Decisions
- [DECISION 2026-10-25] Duplicates are flagged with a boolean `is_duplicate`, not a status: the lead is kept for the founder to
  review, but triggers no conversion event and no email. Duplicate = same normalised phone + same service within
  `LEAD_DUPLICATE_WINDOW_HOURS`, ignoring spam/invalid originals.
- [DECISION 2026-10-25, revised same day by the owner] The consent box on the form is **required**: without the tick the form shows an
  error and nothing is saved, and the thank-you page no longer says we will ask permission later. It is still unchecked by default
  (the visitor ticks it), the wording and CONSENT_NOTICE_VERSION are unchanged, and consent_at / notice version / source are recorded
  as before. Visitors who only want to ask a question can use WhatsApp; for those manual leads the founder still records consent in
  admin, and the model still refuses a partner without it. The former `lead_consented` session flag was removed (no longer needed).
- [DECISION 2026-10-25] The form sets `consent_source='form'` itself (before model validation) so the model can require a source whenever
  consent is true. Found by a failing test: setting it in the view crashed with a 500.
- [DECISION 2026-10-25] The contact page now links to `/enquiry/`. `/enquiry/` is `noindex` until the Module 02 landing page carries the form.
- [DECISION 2026-10-25] Honeypot hits redirect to the normal thank-you page (a bot learns nothing) but save nothing and set no flags.
- [DECISION 2026-10-25] Partner validation runs only when a partner is newly assigned, so later edits (won/lost, notes) still work after a partner is deactivated.
- [DECISION 2026-10-25] Throttle counts every POST per client IP (valid or not). Behind a proxy set `CLIENT_IP_HEADER` to a header the proxy overwrites;
  otherwise everyone shares the proxy's address. X-Forwarded-For is never trusted.
- [OPEN] Retention period for all leads, especially `spam`/`invalid`/`withdrawn` (the privacy notice currently promises only "as long as needed").
- [OPEN] Withdrawal flow: manual by contact email at launch; delete vs anonymise.

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: Lead model + migration, form + template tag, throttle, honeypot, duplicates, notification, admin, thank-you page,
  ERD regenerated (docs/erd.png). Verified end to end against the running container.
