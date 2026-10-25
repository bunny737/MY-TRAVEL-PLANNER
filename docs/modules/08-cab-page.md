# Module: Cab Page

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — page is a DRAFT for the owner to review and publish; cab ads stay gated (rule 1)
**Phase:** 1 (after launch; required before any cab ads)
**Plan reference:** docs/execution-plan.md §4 (P1 `/vizag-to-araku-cab/`), §6 (cab ads gated)
**Depends on:** 02, 04, 07 (07 is still in progress; built early at the owner's request, see Decisions)
**Blocks:** none
**App:** `apps.core` (a `ContentPage` row with `page_type=cab`, the shared content-page template, one `Partner` helper) — no new model, no migration

## Purpose
A dedicated landing page for Vizag→Araku cab queries: vehicle/group choices, pickup points, what to ask, inclusions
and a quote CTA. Unlocks the cab ad group once cab supply is confirmed.

## What was built
- **Seed draft** (`python manage.py seed_launch_content`): `vizag-to-araku-cab`, "Vizag to Araku Cab", destination Araku Valley, photo `valley-road`,
  journey "One way, round trip or day trip". Never published by the seed, never overwritten on re-run. Inclusions and exclusions are left **empty on
  purpose** (only what operators confirm). `internal_notes` lists what to verify and states the ads rule.
- **Cab layout** in `templates/pages/content_page.html`, chosen by `page_type == 'cab'`, using the existing fields (so no schema change):
  - the **itinerary field holds cards** (a heading line plus lines per block): three vehicle groups, pickup points in Visakhapatnam and "questions to ask
    before you book". They render as a card grid titled "Vehicles, pickup points and what to ask" with "Examples only…", not as a numbered day-by-day timeline;
  - the fact strip says **Journey** (not "Trip length") and "Cab with driver"; the closing band says "Need a cab from Vizag?";
  - the form is the standard one with **service = cab pre-selected**, the referral disclosure is on the page, the WhatsApp link is prefilled with only the page title.
- **Supply rule in admin** (`Partner.cab_supply_confirmed()`; `admin.warn_if_cab_supply_missing`): publishing a cab page — by the bulk action or by saving
  the edit form — still works, but if no *active* partner who *offers cabs* has a *referral terms date*, admin shows a warning: do not start cab ads yet.
- **Pickup points in the cards, no cab-owner names, no prices, no distances, durations or seat counts.**
- Discovery is automatic once published: homepage "Trips you can ask about" card (labelled "Cab"), sitemap, destination menu/hub, breadcrumb markup, canonical.

## Business rules (tests in `apps/core/test_cab_page.py`, 16 tests)
1. Cab ads start only after the page is live **and** at least one active cab partner has agreed to receive referrals — the warning above makes the gap visible;
   the ads themselves are the owner's task (CLAUDE.md "Ads work: confirm first").
2. The page shows vehicle types, group guidance, pickup points and what to ask. **No prices** (owner decision 2026-10-25); it invites a free quote (invariant 3).
   A test scans the rendered page for price words, distances/durations/seat counts, and over-claims ("cheapest", "guaranteed", "verified", "best cab", "safest"…).
3. Same form (`service_type=cab`), same referral disclosure and consent flow; a lead submitted from it is saved as a cab enquiry. No new models (invariant 8).
4. Package pages are unchanged (itinerary timeline, "Trip length", "Ready to plan your trip?").
5. The seeded draft passes publishing validation (meta lengths, intro) and is not served until published.

## Permissions
Public read once published. Editing only in admin by the owner.

## Privacy & claims check
Same as Module 02. Vehicle examples are labelled "(example)"; the operator who quotes confirms the real vehicle, seats and pickup. Do not name cab owners
without their consent. No ratings, reviews or "verified" wording.

## Edge cases handled
- A package page that happens to have an itinerary still renders the timeline; only `cab` pages get the card layout.
- A cab page with an empty itinerary simply omits the cards section.
- The warning appears at most once per save/action and never blocks publishing.

## Open questions / Decisions
- [DECISION 2026-10-25] Built before Module 07 is ✅ and before the first ad test, at the owner's explicit request ("implement next module"). CLAUDE.md says
  not to build 08+ before then; the work is content and layout only (no new dependency, schema or tracking change), and ads stay gated by rule 1.
- [DECISION 2026-10-25] No schema change: the cab cards reuse the `itinerary` field, with the section title chosen by page type. The admin help text for
  that field still says "itinerary" (changing help text would add a migration for no behaviour); the seed's `internal_notes` explain the card format.
- [DECISION 2026-10-25] Seat counts and durations are not stated on the page (unsourced); the cards tell travellers what to ask the operator.
- [OPEN] Cab partner supply and dated sample quotes (Day-1 calls). Edit the vehicle cards to match the vehicles your partners actually run, and add the
  inclusions/exclusions they confirm.
- [OPEN] Review and publish the draft. Then, only after rule 1 is met, plan the cab ad group (budget, schedule, keywords: confirm with the plan's numbers first).

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: seed draft, cab-specific sections, supply warning in admin, `Partner.cab_supply_confirmed()`, 16 tests (313 in total, including two existing tests whose seeded-page count went from 3 to 4).
