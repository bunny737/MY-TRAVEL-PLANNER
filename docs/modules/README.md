# Module Index & Status Board

Build strictly top to bottom. Do not start a module until all dependencies are ✅.
Scope, copy and economics come from [../execution-plan.md](../execution-plan.md); this board tracks build status.

## Status
⬜ Not Started · 🟨 In Progress · ✅ Done

Phase 0 = week-one launch sprint (target 2026-10-31). Phase 1 = after launch, days 8–45 of the plan.
Phase 2 = triggered by volume or the first collected fee — never built speculatively.

| # | Module | Spec file | Phase | Depends on | Plan § | Status |
|---|--------|-----------|-------|------------|--------|--------|
| 01 | Foundation (Django skeleton, settings, layout, admin hardening) | 01-foundation.md | 0 | none | 8 | ✅ |
| 02 | Content Pages (Destination, ContentPage, home, Araku package page, SEO) | 02-content-pages.md | 0 | 01 | 4, 9 | ✅ (photos + destinations hub; Araku, Lambasingi and Vizag pages are drafts to review and publish) |
| 03 | Trust & Legal (contact, privacy, terms, referral disclosure, consent notice) | 03-trust-legal.md | 0 | 01 | 2, 13 | ✅ |
| 04 | Partners (Partner model + admin) | 04-partners.md | 0 | 01 | 3, 7, 8 | ✅ |
| 05 | Leads (form, consent, statuses, admin routing, throttle) | 05-leads.md | 0 | 02, 03, 04 | 5 | ✅ (built before 02; see spec) |
| 06 | Tracking & Attribution (UTM/gclid, GA4, Ads conversions, WhatsApp CTA) | 06-tracking-attribution.md | 0 | 05 | 5, 6 | ✅ (needs real IDs + consent decision before ads) |
| 07 | Launch & Deployment (HTTPS, backups, QA, go-live checklist) | 07-launch-deployment.md | 0 | 01–06 | 1, 15 | 🟨 (deployed 2026-10-27 at https://mytravelplanner.in on PGLive's shared instance/edge; owner MFA enrolment and go-live checklist items open) |
| 08 | Cab Page (`/vizag-to-araku-cab/`, gates cab ads) | 08-cab-page.md | 1 | 02, 04, 07 | 4, 6 | ✅ (built early at the owner's request; page is a draft to review and publish; no cab ads until a cab partner has agreed) |
| 09 | Trip Cost Estimator | 09-cost-estimator.md | 1 | 02, 05, 07 | 4 | ⬜ |
| 10 | Content Cluster (2D/1N, itinerary, Lambasingi, guides) | 10-content-cluster.md | 1 | 02, 07 | 4, 9 | 🟨 (pulled forward at the owner's request: site code built; content drafts and partner fact sheet in progress) |
| 11 | Lead Assignment & CRM (LeadAssignment, LeadEvent, response dashboard) | 11-lead-assignment-crm.md | 2 | 05, 07 | 8 | ⬜ |
| 12 | Referral Fees (booking-fee tracking, disputes, invoicing support) | 12-referral-fees.md | 2 | 11 | 7, 8 | ⬜ |

## Phase 2 triggers (from the plan)
- **11** starts only when one lead is routinely assigned to several partners or handoff disputes appear.
- **12** starts only after the first referral fee has actually been collected manually.

## Cross-cutting (enforced in every module — not built once)
- Consent recorded before any lead data is shared (CLAUDE.md invariant 1)
- Click ≠ lead; tracking never carries personal data (invariants 2, 4)
- Honest claims: no unsourced prices, ratings or "official" wording (invariant 3)
- Decimal money, no floats (invariant 6)
- Business config in settings/env, not templates (invariant 9)
- Original content, unique title/meta/canonical per page (invariant 10)

## Week-one definition of done
Live HTTPS site with homepage + one Araku package page + trust/legal pages; a test enquiry is saved in admin,
attributed and manually routable; WhatsApp CTA + form conversion events verified; ≥2 responsive partners
confirmed; Ads drafted and submitted for review (they may not serve on day 7). Full list:
[../execution-plan.md](../execution-plan.md) §1 and §15.
