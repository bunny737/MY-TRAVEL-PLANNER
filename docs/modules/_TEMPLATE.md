# Module: <NAME>

> Keep this file in sync with the code AT ALL TIMES.
> If the code and this file disagree, this file is wrong — fix it in the same commit.

**Status:** Not Started | In Progress | Done
**Phase:** 0 | 1 | 2
**Plan reference:** docs/execution-plan.md §<n>
**Depends on:** <modules>
**Blocks:** <modules>
**App:** `apps.core` (or the app this lives in)

## Purpose
What does this module let a visitor, the founder or a partner do?

## Data model (as-built)
Document tables as actually implemented, not as originally planned.

```
Table: <name>
  id
  ...
  created_at
  updated_at
```

## Routes / endpoints
```
METHOD  /path/    purpose    who can call it
```

## Business rules
Each rule maps to a test.
1.
2.

## Permissions
Who can see/do what (public visitor, owner in admin).

## Privacy & claims check
What personal data does this touch, what leaves the server (analytics, email), and what user-facing
claims/prices does it show? (CLAUDE.md invariants 1–4.)

## Edge cases handled
-

## Open questions / Decisions
- [DECISION 2026-10-xx] what was decided and why
- [OPEN] unresolved — needs input

## Changelog
- 2026-10-xx  Created stub.
