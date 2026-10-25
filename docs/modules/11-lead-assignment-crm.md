# Module: Lead Assignment & CRM

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Not Started
**Phase:** 2 (volume-triggered — do not build speculatively)
**Plan reference:** docs/execution-plan.md §8 "Phase 1 data refactor"
**Depends on:** 05, 07
**Blocks:** 12
**App:** `apps.core`

## Trigger
Start only when the same lead is routinely assigned to several partners, or handoff disputes become hard to
reconstruct from `founder_notes`.

## Purpose
Introduce `LeadAssignment` (lead × partner, per-assignment status/timestamps) and `LeadEvent` (append-only
history), clear billing-eligibility rules, and a partner response dashboard (in admin).

## Business rules
1. Migration moves `Lead.partner` and notes into `LeadAssignment`/`LeadEvent`, preserving consent and provenance.
2. Each assignment requires consent covering that share (fresh consent for broader sharing, plan §5/§13).
3. Events are append-only; no edits to history.

## Open questions / Decisions
- [OPEN] Adds models beyond the MVP four — stop and ask before starting (CLAUDE.md invariant 8).

## Changelog
- 2026-10-25  Created stub from the project setup.
