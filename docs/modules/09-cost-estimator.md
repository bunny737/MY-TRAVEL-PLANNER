# Module: Trip Cost Estimator

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Not Started
**Phase:** 1 (days 8–21; only with real quote data)
**Plan reference:** docs/execution-plan.md §4 "Simple trip cost estimator"
**Depends on:** 02, 05, 07
**Blocks:** none
**App:** `apps.core`

## Purpose
`/araku-trip-cost-calculator/`: group size, trip days, pickup city, vehicle category, optional hotel tier →
an *illustrative* range based on dated partner quotes, with a breakdown and a "Get a current quote" CTA.

## Business rules
1. Output is always labelled illustrative, shows the "last updated" date and the exclusions; never "live" or
   "guaranteed" (invariant 3).
2. Ranges come from dated partner quotes; with no quote data for an input combination show "request a quote".
3. All amounts are Decimal (INR); no float arithmetic (invariant 6).
4. Calculator → lead conversion is recorded (event only, no personal data).

## Data model
Open decision. The four-model limit (invariant 8) means storing quote ranges needs approval: options are
(a) a JSON config on a `ContentPage`, (b) a new `QuoteRange` model. Ask before choosing.

## Privacy & claims check
Inputs are not personal data and are not stored unless the visitor submits the enquiry form.

## Open questions / Decisions
- [OPEN] CONFLICT TO RESOLVE BEFORE BUILDING: on 2026-10-25 the owner decided package/cab pages show no prices. An estimator
  is, by definition, a price display. Confirm whether it is still wanted (it would be the one place indicative ranges appear).
- [OPEN] Quote-range storage (see Data model). 
- [OPEN] Server-rendered form post vs small client-side JS (default: server-rendered).

## Changelog
- 2026-10-25  Created stub from the project setup.
