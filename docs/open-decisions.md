# Open Decisions

From execution plan §14 plus items found while setting up the project. Update the status here and record the
outcome as a `[DECISION]` line in the affected module spec.

| Decision | Default / current | Owner / deadline | Affects |
|---|---|---|---|
| Brand / domain | **DECIDED 2026-10-25:** "My Travel Planner", mytravelplanner.in, canonical without www (www redirects) | Founder | All pages, ads, Search Console |
| Business WhatsApp / contact number | Dedicated reachable number + published response hours | Founder, 27 Oct | 03, 06 |
| Partner supply | ≥2 reliable local operators confirmed | Founder, 29 Oct | 04, 05, 07 |
| First paid product | Araku package enquiries only | Founder, 29 Oct | 02, 06 |
| Ads budget | ₹5k first test; ₹5k extension only after review | Founder, 30 Oct | 07 |
| Tech | Django templates + admin; one deploy | Founder, 26 Oct | 01 (decided in CLAUDE.md) |
| Operator terms | Free pilot, then ₹1,000–₹2,000 per verified booking | Founder, 1–14 Nov | 04, 12 |
| Hosting provider | **DECIDED 2026-10-25:** Google Cloud Run + existing Cloud SQL instance (own database and user). Open: region, and domain mapping vs load balancer | Founder | 07, docs/deployment.md |
| Admin MFA | **DECIDED 2026-10-25:** `django-otp` authenticator app (built, mandatory in production) | Founder | 01, 07 |
| Backups | **DECIDED 2026-10-25:** Cloud SQL automated backups + a weekly encrypted download you make yourself; no extra bucket | Founder | 07 |
| Cookie / analytics consent banner | Undecided; needs legal check | Founder, before ads | 03, 06 |
| Legal review of privacy/consent wording (DPDP Rules 2025) | Not started | Founder, before ads | 03, 05 |
| CSS approach | Plain CSS (Tailwind only if requested) | Founder, Day 2 | 01 |
| Languages | English only at launch | Founder, Day 2 | 01 |
| Quote-range storage for the cost estimator | Undecided; needs approval (fifth model) | Founder, Phase 1 | 09 |
