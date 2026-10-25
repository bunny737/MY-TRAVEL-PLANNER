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
- [OPEN] Which pages first — decide from the first ad test's search-term report.
- [OPEN] Peak-season (Oct–Feb) field trip to collect original notes/photos before Oct 2027 content maturity.

## Changelog
- 2026-10-25  Created stub from the project setup.
