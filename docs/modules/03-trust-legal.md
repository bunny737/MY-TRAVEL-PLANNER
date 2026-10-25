# Module: Trust & Legal

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — wording is a DRAFT pending legal review (see Decisions)
**Phase:** 0
**Plan reference:** docs/execution-plan.md §2 (positioning), §5 (consent), §13 (compliance)
**Depends on:** 01
**Blocks:** 05, 07
**App:** `apps.core`

## Purpose
Genuine contact details, privacy notice, terms and the referral disclosure used identically everywhere,
so a visitor knows we are a referral platform and exactly what happens to their details.

## Scope
- Pages: `/contact/`, `/privacy/`, `/terms/` (P0).
- A reusable template partial `referral_disclosure.html` with the plan's wording:
  "We are a travel enquiry and referral platform. With your permission, we will share your trip requirements
  and contact details with selected independent travel partners so they can contact you with quotes.
  Bookings and tour delivery are handled by those partners."
- Consent notice text bound to `CONSENT_NOTICE_VERSION` (stored on each Lead by module 05); changing the
  text requires bumping the version.
- Published response hours from `RESPONSE_HOURS_TEXT`; withdrawal/deletion contact in the privacy notice.

## As-built
```
templates/pages/{contact,privacy,terms}.html     plain Django templates, served by TemplateView (apps/core/urls.py)
templates/partials/referral_disclosure.html      plan §2 wording, verbatim
templates/partials/consent_notice.html           checkbox label (used by Module 05's form); bound to CONSENT_NOTICE_VERSION
templates/base.html footer                       Contact / Privacy / Terms links + one-line referral statement on every page
```
Tests: `apps/core/test_trust_legal.py` (pages, unique title/meta, disclosure wording, footer links, forbidden-claims scan,
privacy/terms key statements, contact config on/off, pinned consent wording + version).

## Data model (as-built)
None. Static templates (not `ContentPage` rows): the wording is legal text that should change in code review, not in admin.

## Routes / endpoints
```
GET  /contact/ (core:contact)   GET /privacy/ (core:privacy)   GET /terms/ (core:terms)    public, indexable
```

## Business rules
1. The disclosure partial is included next to every enquiry CTA (landing page, homepage, form, WhatsApp block).
2. Privacy notice states: what is collected, purpose (quotes only), sharing with ONE selected partner first,
   fresh consent before broader sharing, retention, how to withdraw/delete, no secondary marketing without
   separate permission.
3. Terms state the referral-only role: partners deliver and are responsible for services; we take no trip payment.
4. No claim of official tourism affiliation, guaranteed cheapest price, or verified reviews anywhere.
5. Contact page shows the real owner contact (email/phone/WhatsApp from env) and response hours.

## Permissions
Public read.

## Privacy & claims check
This module defines the wording others depend on. Any change to consent wording is a stop-and-ask
(CLAUDE.md) and must bump `CONSENT_NOTICE_VERSION`.

## Edge cases handled
-

## Open questions / Decisions
- [DECISION 2026-10-25] Privacy and Terms text was drafted from the plan's §2/§5/§13 in plain, generic language.
  It has NOT been reviewed by a lawyer. Do not run ads until it is. Assumptions a lawyer should confirm: no fixed
  retention period is stated, "governing law" is intentionally omitted, the liability-limit wording, and the
  "last updated" date (25 October 2026), which must change whenever the text changes.
- [DECISION 2026-10-25] The consent checkbox says "one selected independent travel partner" (plan §5: first share with one
  operator only) while the plan's §2 disclosure says "selected independent travel partners". Both are kept as the plan
  words them; harmonise if the lawyer asks.
- [DECISION 2026-10-25] Consent wording is pinned by a test; changing the partial fails it until `CONSENT_NOTICE_VERSION` is bumped.
- [DECISION 2026-10-25] The contact page's "send an enquiry online" link is added by Module 05 (the form route does not exist yet).
- [OPEN] DPDP Rules 2025 provisions in force at launch — get local legal advice before finalising the notice.
- [OPEN] Cookie/analytics consent banner: requirement depends on the tag setup (plan §13); decide in module 06.
- [OPEN] Business registration / GST / entity details to show on Terms and Contact.
- [OPEN] Google Business Profile: do NOT create one for a lead-gen-only business (plan §13).

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: contact/privacy/terms pages, disclosure + consent partials, footer links, 12 tests.
