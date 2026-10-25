# Module: Referral Fees

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Not Started
**Phase:** 2 (triggered by the first collected fee)
**Plan reference:** docs/execution-plan.md §7 (converted booking, fees), §8 "Phase 2"
**Depends on:** 11
**Blocks:** none
**App:** `apps.core`

## Trigger
Start only after at least one real ₹1,000–₹2,000 referral fee has been collected manually. Until then use a
spreadsheet/admin notes (plan §7: "Avoid fully automated billing in MVP").

## Purpose
Track verified converted bookings and the fixed fee owed, without taking the traveller's trip payment.

## Business rules
1. A converted booking = a distinct referred traveller books an eligible service with the assigned partner and
   the partner receives a confirmed deposit/payment, evidenced per the agreed terms (booking ID, dated
   confirmation, masked receipt).
2. Fee is fixed per verified booking (₹1,000–₹2,000, negotiated per partner); ₹0 for clicks, enquiries,
   unqualified or non-converting referrals.
3. Attribution window defaults to 30 days; duplicates and pre-existing customers follow the written terms.
4. Cancelled/refunded bookings trigger no fee, or a credit/refund if already paid.
5. Money is `Decimal(12,2)` (invariant 6); record referral date, partner, package, booking date, booking value
   when disclosed, fee, amount due, collected, cancellation/refund status.
6. Invoicing and tax handling follow an accountant's advice; no automated billing at first.

## Open questions / Decisions
- [OPEN] Model shape (extend `LeadAssignment` vs a `Booking`/`Fee` model) — stop and ask.
- [OPEN] Invoice generation and GST handling — accountant.

## Changelog
- 2026-10-25  Created stub from the project setup.
