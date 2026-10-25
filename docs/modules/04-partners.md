# Module: Partners

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Done (2026-10-25) — pilot-referral counter in admin is added by Module 05 (needs Lead)
**Phase:** 0
**Plan reference:** docs/execution-plan.md §3 (Day-1 interview fields), §7 (partner pilot), §8 (Partner model)
**Depends on:** 01
**Blocks:** 05, 08
**App:** `apps.core`

## Purpose
Hold the independent tour/cab/homestay operators the founder refers leads to, with the facts needed to pick
the right one and to prove permission, in Django admin only. Partners never log in (MVP).

## Data model (as-built)
```
Table: core_partner   (apps.core.models.Partner, migration core.0001)
  id
  business_name (150), contact_name (120, blank)
  phone (required), whatsapp (blank)       validated + normalised on save to +91XXXXXXXXXX / +<intl digits>
  service_regions (255, blank)
  offers_tours, offers_cabs, offers_homestays   booleans; clean() requires at least one
  response_hours (120, blank)
  is_active (default True)
  referral_terms_agreed_on  DATE, null     the recorded acknowledgement; required before any lead is assigned
  referral_terms_notes      text           free pilot size, fee if agreed, invalid/duplicate rules
  notes                     text           interview notes, dated sample quote, licence supplied
  last_verified_at          datetime, null
  created_at, updated_at
property can_receive_referrals = is_active AND referral_terms_agreed_on is not null
```
Shared helper `apps/core/validators.py` (`normalize_phone`, `validate_phone`) is reused by Lead (Module 05).
Settings: `PILOT_REFERRALS_PER_PARTNER` (default 3, env) — the free-pilot size, never a literal (invariant 5).
Tests: `apps/core/test_partners.py`.
Day-1 interview extras (vehicle/tour offerings, dated sample quote, licence supplied, willingness to pay)
go in `notes` until volume justifies structure — do not add a quote table (invariant 8; module 09 decides).

## Routes / endpoints
None public. Django admin changelist with filters (active, service type, region) and search.

## Business rules
1. A partner can be assigned to a lead only if `is_active` and has a recorded referral-terms acknowledgement.
2. Partner contact data is never rendered on public pages; partner names appear publicly only with explicit consent.
3. Deactivating a partner does not delete leads referred to them (FK `PROTECT` or `SET_NULL` — decide, document).
4. Free pilot: 2–3 referrals per operator; the count is visible in admin (annotated from Lead) so the founder
   knows when the pilot ended **before** any chargeable referral (plan §7).

## Permissions
Owner only, via admin.

## Privacy & claims check
Partner phone numbers are business contacts but still private. No "verified" badge on the site unless the
partner supplied a registration/licence and agreed to publication.

## Edge cases handled
-

## Open questions / Decisions
- [DECISION 2026-10-25] `service_types` became three booleans (`offers_tours/cabs/homestays`): they filter in admin and in
  queries with no custom code. A new service type later means a new column, which is acceptable at this scale.
- [DECISION 2026-10-25] The spec's single `agreed_referral_terms` became a date (`referral_terms_agreed_on`, machine-checkable
  for rule 1) plus `referral_terms_notes` (what was agreed).
- [DECISION 2026-10-25] Lead → Partner uses `on_delete=PROTECT` (Module 05): a partner with referred leads can only be
  deactivated, not deleted, so handoff history is never lost.
- [OPEN] Pilot-referral counter (rule 4) is implemented in Module 05 as an annotated admin column.

## Changelog
- 2026-10-25  Created stub from the project setup.
- 2026-10-25  Built: Partner model + migration, phone validator, admin (filters/search), 14 tests.
