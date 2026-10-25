# Travel Lead Generation Platform — Execution Plan (Version 3.0)

**Updated:** 25 October 2026  
**Owner:** Solo founder; assumes ~10–15 hours/week outside a day job (increase time or reduce scope if the first week is tighter)  
**Immediate target:** Launch a working website **by 31 October 2026**, then turn on Google Search Ads once tracking, partner readiness and ad review are complete.  
**Launch region:** Araku Valley, Vizag, Lambasingi/Vanjangi (focus first paid campaign on Araku packages; defer cab advertising until its dedicated page exists).  
**Model:** Independent tourism planning and referral platform, *not* a tour operator, payment aggregator or online travel agency. Travellers submit enquiries free; independent partners quote and deliver tours.  
**Status:** Planning assumptions; actual operator participation, search volumes, CPCs, price quotes and conversion rates remain to be validated.

## 0. Decisions and changes from previous versions

1. **Paid validation comes before organic-traffic validation.** Launch the site in one week, run a capped ₹5,000 first Google Search test (up to ₹10,000 only after reviewing results), and use partner feedback as the primary commercial signal. SEO is a 6–12+ month growth channel, not a day-90 revenue gate.
2. **Concierge MVP instead of a marketplace.** Only four primary data models at launch: `Destination`, `ContentPage` (can represent a package), `Lead`, and `Partner`. Lead handoff is manual. No partner login, billing software, complex workflows, hotel inventory, or customer checkout.
3. **WhatsApp and a short form are equally prominent CTAs.** Track WhatsApp clicks as *intent*, not confirmed leads; when a user messages, qualify and record the enquiry with appropriate notice/consent before forwarding.
4. **Partners are small local operators with limited web presence.** Prioritize independent cab owners, local guides, small tour agencies and homestay operators. Do not assume competitors operating their own SEO sites will buy referrals.
5. **Commercial-first content.** Launch with **one commercial Araku landing page** plus a homepage and trust/legal pages. Cab pages and the cost estimator come after the site is live, using real quote ranges.
6. **Charge only for confirmed bookings.** Offer 2–3 free pilot referrals per operator, then negotiate a **fixed ₹1,000–₹2,000 referral fee per verified converted booking** with each partner. Unconverted enquiries are free. Do not build billing before collecting the first fee.
7. **Honest brand and scope.** Choose a destination-neutral brand/domain by Day 1 if possible; launch a regional content cluster. Do not claim to operate tours or have certified inventory.
8. **Field evidence gathered during October–February peak season.** Record current quotes, partner availability, package inclusions, permitted original photographs and changes in timings; use the material to mature SEO before the following tourist season.

### Version 3 decisions (locked)
- **Launch by 31 October:** the *smallest* site, not the full catalogue.
- **Ads:** ₹5,000 initial Search campaign, scheduled only when the founder can respond.
- **Monetization:** **₹1,000–₹2,000 per verified converted booking**, not ₹1,000–₹2,000 per enquiry; no fee on unsuccessful referrals.
- **Tools:** dedicated **WhatsApp Business app** with quick replies and labels, plus Django admin. No WhatsApp API at launch.
- **Consent:** the same referral wording everywhere; first share with **one** selected operator only.
- **Review:** first ad test is primarily a demand and response-speed test, not a profitability test.

## 1. First-week success definition

**Launch success ≠ rankings, traffic or revenue.** At the end of the first seven days we want:
- Live HTTPS website with a working mobile homepage, **one Araku package landing page**, and basic trust/legal pages.
- Two **confirmed responsive** tour/cab partners; ideally three to five vetted prospects. Get their permission to refer enquiries and document their coverage and response hours.
- A test enquiry can be submitted, saved in Django admin, attributed to source/campaign, and manually routed without exposing customer details publicly.
- Working outbound WhatsApp CTA (into the platform's number), form conversion event, basic analytics and Google Ads tagging verified with test events.
- Ads drafted, billing configured and submitted for review. Ads may not start serving on Day 7 because review is not guaranteed on schedule.

**Do not buy ads until:** landing pages load, contact/consent flows work, messages reach you, at least two operators can respond, and the ad claims match the page.

## 2. Business positioning and customer promise

**Suggested copy:** “Plan your Araku trip. Compare suitable tour and cab options from independent local travel providers. Request quotes free.”

Explain near every enquiry CTA: “We are a travel enquiry and referral platform. With your permission, we will share your trip requirements and contact details with selected independent travel partners so they can contact you with quotes. Bookings and tour delivery are handled by those partners.”

Do not advertise “guaranteed cheapest”, “official tourism office”, “verified 5-star reviews”, “instant confirmation” or precise package prices without evidence. The platform does not take the traveller’s trip payment in MVP.

**Travellers:** families, couples, small groups and visitors arriving in Vizag or travelling from Hyderabad.  
**Lead buyers:** small local cab owners/tour organisers/homestays without strong SEO, not necessarily the existing five ranking websites.

## 3. Focused seven-day work plan

| Date | Hard priority | Deliverable | Founder effort target |
|---|---|---|---|
| **Sun 25 Oct — Day 1** | Brand/domain decision; call 6–10 operators; collect at least 2 usable sample quotes and their service area; write copy and consent language | Name selected, domain plan, partner shortlist, offer sheets | 2–3 h |
| **Mon 26 Oct — Day 2** | Django skeleton, PostgreSQL or SQLite for MVP if managed carefully, HTML templates, mobile styles, homepage, header/footer | Site runs end-to-end locally | 2–3 h |
| **Tue 27 Oct — Day 3** | Araku package landing page (defer the cab page); original inclusions; truthful prices or “request quote” | One campaign-relevant landing page | 2–3 h |
| **Wed 28 Oct — Day 4** | Lead form, model/admin, inbound email notifications or admin check, WhatsApp CTA, attribution fields | Form submission and chat flow work | 2–3 h |
| **Thu 29 Oct — Day 5** | Privacy/terms/contact/referral disclosure; title/meta/canonical/sitemap; GA4, Google Ads and Search Console; validation + bot guard | Minimum compliant, measurable launch candidate | 2–3 h |
| **Fri 30 Oct — Day 6** | Deploy HTTPS, backups, domain/DNS, mobile performance checks; test real lead and end-to-end handoff; create Search campaign | Public staging/live site, QA checklist green | 2–3 h |
| **Sat 31 Oct — Day 7** | Production release, submit/enable ads after prerequisites; monitor click/search terms/conversion events; partner availability check | Launch and test campaign initiated | 1–2 h |

**Committed week-one scope: 10–15 hours.** Build **homepage + one Araku landing page + short form + WhatsApp Business app + privacy/contact/referral disclosure + basic conversion tagging + deployment**. **Defer** separate cab page, cost estimator, extra packages, advanced partner management and automated notifications. The schedule below is a priority order, not a requirement to spend 2–3 hours every day. Reuse Django admin, a simple template/theme and ordinary server-rendered HTML. No elaborate custom design system.

### Day 1 operator interview script and data fields

“I'm building a website that helps travellers compare Araku tour options. I want to send you genuine interested enquiries, initially free. Do you handle [Araku day/2-day tours/cabs]? Which trips and group sizes can you serve? What is included, what changes the price, and how quickly could you respond to a customer?”

Record: operator name; phone/WhatsApp; area; vehicle and tour offerings; sample quote with date, inclusions/exclusions and group size; availability/response hours; permission to refer; lead acceptance criteria; willingness to pay later; any verified registration or licence supplied by operator. Do not publish partner claims without consent.

## 4. Launch page architecture and priority

| Launch priority | URL pattern | Content and conversion goal |
|---|---|---|
| P0 | `/` | Strong promise, top trip choices, trust/referral disclosure, CTAs |
| P0 | `/araku-tour-packages/` | Package durations, example itineraries, actual inclusions/ranges, FAQ, short form + WhatsApp |
| P1 (after launch; required before cab ads) | `/vizag-to-araku-cab/` | Vehicle/group choices, pickup points, cab inclusions, restrictions, quote CTA |
| P0 | `/contact/`, `/privacy/`, `/terms/` | Genuine contact, data sharing explanation, booking responsibility |
| P1 days 8–21 | `/araku-trip-cost-calculator/` | Group size, departure city, number of nights, cab category, indicative costs from partner quotes, updated date + uncertainty |
| P1 days 8–30 | `/araku-2-days-tour-package/` | Detailed, original 2D/1N itinerary with quote CTA |
| P1 | `/vizag-araku-itinerary/`, `/lambasingi-tour-packages/` | Useful next commercial cluster |
| P2 | Destination guides, original hotels/cabs comparisons, seasonal tips | Long-run search coverage and internal links |

**Rule:** Do not ship generic filler pages. A smaller website with correct quotes and clear intent is better than ten repetitive SEO pages.

### Landing-page content checklist
- Headline closely matches ad/search query.
- Clearly describe independent partner quote/referral model.
- Show an honest starting price or mark “Price varies by dates, vehicle, inclusions; request a current quote.”
- Provide trip duration, examples of attractions, pickup and drop, exclusions, available vehicle types and who actually delivers.
- Place short form + WhatsApp near top and again after itinerary; support mobile sticky CTA if unobtrusive.
- FAQ with real answers, contact details, policy links and no invented ratings.
- Fast images: licensed/original, optimized, meaningful alt text, no misleading stock presentation as operator-owned.

### Simple trip cost estimator (P1, ideally first 2–3 weeks)
Inputs: group size, trip days, pickup city, vehicle size/category, hotel tier (optional). Output: *illustrative* range based on dated partner quotes, breakdown (transport, accommodation, tickets, meals where known), exclusions, and “Get a current quote”. Never label it a live or guaranteed price. Record calculator-to-lead conversion.

## 5. Lead capture, consent and manual routing

### Website short-form fields
- Name and phone (required).
- Service: tour package / cab (required).
- Travel date or approximate month (required).
- Number of travellers (required).
- Pickup/departure location (optional initially, useful for qualification).
- Budget and notes (optional).
- **Unbundled consent:** an unchecked, readable checkbox explaining that enquiry details and phone can be shared with selected independent providers for quotes; link privacy notice. Do not pre-check it.
- Hidden anti-spam field or rate limit; attribution fields in server session/hidden signed input as appropriate.

Submission: server validation → save lead with consent timestamp and displayed notice version → thank-you page/event → notify founder → founder manually checks and refers to one appropriate operator at first; optionally more, if disclosed and consented. Do not auto-forward to an unrestricted broadcast list.

### WhatsApp first flow
Primary button opens chat to **your dedicated WhatsApp Business app number** (not the API), not multiple partners. Use built-in quick replies and labels for follow-up. Pre-fill only non-sensitive travel context, e.g. “Hi, I want an Araku tour quote for 4 people.” The **click** event is a micro-conversion, not a confirmed lead. Your first response should give a brief privacy/referral notice and request explicit agreement **before** collecting/forwarding details for referral; record agreement in `Lead` once received. No assumptions that clicking a link constitutes consent.

Example response:
> “Thanks for your enquiry. We connect travellers with independent tour operators. With your permission, may we share your name, number and trip requirements with one suitable local operator so they can send you quotes? Reply YES to agree. Privacy policy: [link].”

Track the confirmed WhatsApp enquiries **manually** in Django admin, matched to click source where feasible without overstating attribution.

### Lead statuses (single enum at MVP)
`new` → `qualified` → `referred` → `partner_responded` → `won/lost`, with `spam`, `invalid`, `withdrawn` alternatives. Store partner ID on Lead for first assignment and simple founder notes. If multiple partner assignments become routine, introduce `LeadAssignment` in Phase 1.

**Lead response policy (chosen for a solo founder with a day job):** run Search Ads only during founder-covered windows: **7:00–9:00 AM and 7:00–10:00 PM IST on weekdays; 8:00 AM–10:00 PM on weekends**. These are starting windows, adjustable based on actual availability and campaign results. During those windows, aim for a first acknowledgement within 30–60 minutes; send handoffs promptly and follow up after 24 hours. Publish honest availability, e.g. “We respond during 7–9 AM and 7–10 PM on weekdays; 8 AM–10 PM on weekends.” Outside these windows the website remains live; configure the **WhatsApp Business app away message** with response hours and a brief acknowledgement, and use quick replies for the same referral-consent script. Do not promise 24/7 service. If a partner eventually covers daytime enquiries, expand ad hours only after testing that handoff.

## 6. Google Ads — initial paid validation experiment

### Campaign setup
- **Campaign:** `Araku | Search | Lead Validation | Oct-Nov 2026`.
- **Network:** Search only; disable Display expansion. Decide Search Partners separately; leave off for initial clarity.
- **Geographic targeting:** start with **Visakhapatnam, Hyderabad, Bengaluru, Chennai, Kolkata and Bhubaneswar** using presence-based targeting where supported. Ask operators specifically about visitors already in Vizag booking next-day Araku trips. Do not use unrestricted India-wide interest targeting in the first ₹5k test. Review city-level spend and lead quality at ~₹2,000, then narrow or broaden deliberately.
- **Ad groups at launch:** Araku packages only. Do not advertise cab queries until the separate `/vizag-to-araku-cab/` page is live and cab partner supply is confirmed.
- **Keyword launch (Araku package landing page only):** phrase/exact match candidates: `araku tour packages`, `araku tour package 2 days`, `vizag araku tour package`, `araku family tour package`. These are **hypotheses**; confirm Keyword Planner volumes and CPC estimates.
- **Negative keyword seed:** jobs, recruitment, wallpaper, pictures, free, map, route map, wikipedia; check actual search-term reports and avoid excluding valid searches accidentally.
- **Ad copy:** match the page and disclose quote comparison, not guaranteed low price or direct ownership of travel inventory.
- **Bidding:** start with Maximize Clicks with suitable CPC control where the interface permits, then reconsider based on *qualified* conversions; avoid overfitting to a handful of events.
- **Ad schedule:** **weekdays 7–9 AM and 7–10 PM IST; weekends 8 AM–10 PM IST**, matching the published response policy. Disable ads outside these hours until proven daytime coverage exists.
- **Primary conversion:** successful form submission (deduplicated). Secondary: click-to-WhatsApp and click-to-call, separated in reporting; count confirmed WhatsApp leads offline.
- **Tracking:** Google Ads conversion tag through Google tag/GTM, GA4, UTM/gclid retention where lawful and possible, server-side lead-source fields. Test real and duplicate submissions before ads.

### Budget control
**First test:** ₹5,000 over approximately 10–14 days (nominal ₹500/day where appropriate for the scheduled run time). **Important:** Google may charge up to **2× average daily budget on a day** for many campaigns; a nominal ₹500 daily budget is not a hard ₹500/day cap. Apply an end date, check spending daily, and use a campaign total budget feature *if eligible and available* or manual pause/automated rule where supported. Do not assume an exact ₹5,000 hard cap merely from daily budget × 10.

**Extension:** additional ₹5,000 only if measured enquiries are genuinely qualified, partners are responding and the next batch can answer an unresolved question. No open-ended automatic scaling.

### Evaluation: paid traffic ≠ profitable acquisition
Capture daily: impressions, clicks, spend, search terms, form submissions, WhatsApp clicks, confirmed WhatsApp enquiries, invalid/duplicate leads, qualified leads, partner-accepted leads, partner responses, reported bookings, partner payments.

Formulas:
- `CPC = ad spend / paid clicks`.
- `Enquiry conversion = confirmed enquiries / ad clicks` (keep form and WhatsApp sources separate where attribution is uncertain).
- `Cost per qualified lead (CPQL) = ad spend / qualified paid leads`.
- `Cost per accepted lead = spend / partner-accepted paid leads`.
- `Realized revenue per paid lead = actual money collected from partners / paid leads`.
- `Contribution = collected referral revenue − ad spend − incremental servicing costs`.

**Example:** ₹5,000 spend / ₹20 CPC = 250 clicks; 5% *confirmed* enquiry rate = ~12–13 enquiries; if 70% qualified, ~9 qualified enquiries, **CPQL ≈ ₹556**. The first ad test measures **search interest, clicks, enquiry conversion, qualification and partner response**—**not profitability**. Revenue depends on **actual bookings**, not just enquiries. At an agreed **₹1,000–₹2,000 per verified booking**, recovering ₹5,000 of ad spend requires **5 bookings at ₹1,000 or 3 bookings at ₹2,000** (rounding up), *before* servicing costs and possible refunds. This is an arithmetic scenario, not a forecast or guarantee of that booking conversion rate.

### Kill, fix and extend rules
- **Pause immediately:** tracking broken, invalid claims, lead spam, no operators available, consent/privacy failure, or out-of-control spend.
- **At ~₹2,000 spent:** inspect real search terms, location and device performance, landing-page drop-offs and response speed. If high-intent clicks are scarce, tighten targeting and message; do not draw strong conclusions from tiny sample sizes.
- **At ₹5,000 spent:** classify as (a) no demand detected, (b) demand but poor conversion, (c) qualified leads but slow partner response, (d) qualified demand with bookings not yet known, or (e) early confirmed bookings. Then run *one focused follow-up test* if warranted.
- **Do not require profitability in first 10 days**, but do require evidence to justify additional spending.

## 7. Partner sales and monetization experiment

### Whom to recruit
Prioritize small tour organisers, reliable local cab providers, homestays and destination experience operators who depend on referrals and are unlikely to compete for the same high-volume SERP keywords. Existing ranking sites are competitors and optional partners—not the default acquisition target.

### Partner pilot terms (simple one-page agreement)
- You send up to 2–3 pilot enquiries per operator for free, contingent on permission and supply fit.
- Partner responds within a mutually agreed period, provides genuine quotes, and tells you whether referral converted.
- Partner uses contact details *only* to quote/serve the requested trip; no unrelated marketing or resale.
- Agree what counts as an invalid/duplicate lead, what happens on customer withdrawal, and how disputes are handled.
- You and partner confirm when free pilot ends **before** any payable leads are sent.

### Primary monetization: pay only for converted bookings
**Default commercial offer:** a partner pays **₹1,000–₹2,000 for each verified booking originating from your referral**. Charge **₹0 for clicks, raw enquiries, unqualified leads and referrals that do not convert**. Negotiate the exact fixed fee based on genuine package value, operator margin and type of booking. A ₹1,000 fee on a ₹5,000 booking is 20% of sales value; this may be unattractive to an operator, so do **not** assume every booking supports the target fee. Confirm package prices and margins on operator calls.

**Definition of a converted booking:** a distinct traveller referred by the platform books an eligible tour/cab service with the assigned partner and the partner receives a confirmed deposit or payment; evidence should be mutually agreed (e.g. booking ID, dated confirmation, masked receipt), without collecting unnecessary sensitive information. Record referral date, partner, package, booking date, booking value where disclosed, fixed fee, payment due, and cancellation/refund status. Set an explicit attribution window (pilot proposal: **30 days**) and agree how pre-existing customers and duplicate enquiries are handled. A cancellation or refunded booking does not trigger a fee (or triggers a credit/refund if already paid), according to agreed written terms.

**Commercial pilot:** start with 2–3 free referrals per operator, then obtain their explicit agreement to the per-booking fee **before referring chargeable prospects**. Follow up with the traveller and partner after referral to confirm whether a booking happened, without assuming partner-reported bookings are complete. Keep a manual spreadsheet/admin note for fees, disputes and cash received. Invoices and tax handling follow the applicable advice of an accountant. Avoid fully automated billing in MVP.

**Secondary experiment, not a launch requirement:** prepaid credits or lower-priced per-lead fees can be explored later **only** for organic leads or if paid-acquisition unit economics support them. They are not the default pricing model.

**Primary commercial KPI:** verified bookings / qualified referred enquiries (booking conversion rate), with partner response time and cash collected alongside it. Using the sample ~9 qualified enquiries and ₹5,000 spend, break-even on ads alone requires about 56% booking conversion at ₹1,000 per booking or about 33% at ₹2,000; these are demanding thresholds, not targets to assume.

**Commercial validation event:** at least one actual, attributable booking and **₹1,000–₹2,000 fee collected**, not merely a promise to pay. Measure partner satisfaction and repeat willingness to participate.

## 8. Minimal Django implementation

### Technical choices
- Django 5.x/6.x compatible supported release; check current supported versions when implementing.
- PostgreSQL preferred for production; SQLite acceptable for the smallest single-instance launch if backed up and migrated early. No Redis/Celery initially.
- Django templates + Tailwind CSS or straightforward compiled CSS; minimize frontend JS.
- Django admin for manual content and leads; one app (e.g. `core`) is sufficient initially.
- Hosted Linux server with HTTPS, Gunicorn, reverse proxy, automatic OS/application updates and daily database backups. Use your existing GCP credit only if it simplifies launch; avoid overbuilding infrastructure.
- Email notifications optional; admin/WhatsApp checks can suffice while volume is tiny. Avoid relying on unapproved WhatsApp automation APIs.

### The four core models

**`Destination`**: `name`, `slug`, `summary`, `is_active`, `sort_order`.

**`ContentPage`**: `destination` FK (nullable), `page_type` (`home`, `package`, `cab`, `guide`), `title`, `slug`, `body`/structured itinerary, `meta_title`, `meta_description`, `canonical_override` (rare), `published_at`, `status`, `updated_at`. Structured package fields may be minimal nullable attributes rather than a new model initially.

**`Partner`**: `business_name`, `contact_name`, `phone`, `whatsapp`, `service_regions`, `service_types`, `response_hours`, `is_active`, `agreed_referral_terms`, `notes`, `last_verified_at`.

**`Lead`**: `name`, `phone`, `service_type`, `travel_date_or_month`, `travellers`, `pickup_city`, `budget`, `notes`, `status`, `partner` (nullable FK), `lead_channel` (`form`, `whatsapp`, `call`, `manual`), `landing_path`, `utm_source`, `utm_medium`, `utm_campaign`, `gclid` (if captured), `consent_given`, `consent_at`, `consent_notice_version`, `consent_source`, `created_at`, `qualified_at`, `referred_at`, `partner_responded_at`, `founder_notes`. Avoid unnecessary duplication of sensitive data in logs.

**Practical minimum security:** HTTPS, CSRF, server-side validation, basic request throttling/bot guard, strong admin authentication + MFA if supported, access limited to owner, backups and restore test, secrets via environment, no public lead endpoint, consent recorded before sharing. Encryption at rest through hosting/database facilities is desirable; do not implement a custom field-level crypto system in the week-one sprint.

### Phase 1 data refactor (triggered by volume)
When assigning the same lead to multiple partners or disputing handoffs becomes difficult, introduce `LeadAssignment` and `LeadEvent`, clear billing eligibility rules and a partner response dashboard. Migrate old notes/partner FK, preserve consent and provenance.

### Phase 2 (triggered by first collected payment)
Booking-fee tracking, payment/invoicing, cancellation and booking-attribution disputes, partner portal, automated lead distribution, richer CRM metrics. Build only features proven necessary by operations.

## 9. SEO: launch foundations vs. long-term moat

### Week-one technical essentials
- Unique, natural title/meta description; correct H1; semantic links; clean slug structure.
- Canonical URL, robots.txt, XML sitemap; noindex for thank-you, admin and utility pages.
- Search Console verification and sitemap submission; GA4 event checks.
- Mobile-first performance, compressed hero images, no intrusive overlays.
- Accurate LocalBusiness/Organization only if eligible; BreadcrumbList where applicable; no fabricated Product/Review ratings.
- Legal, contact and editorial transparency; no copied competitor text or unsupported prices.

### Months 2–12 content and research
- Prefer **booking-intent pages first**: Araku tours, 2D/1N, family/group itineraries, cabs, hotel+cab bundle planning, trip cost calculator.
- Keep destination guides as supporting, useful content, not the entire strategy; informational clicks may be limited by AI answer surfaces.
- Original field notes: verify drive times, access/timings, cab and lodging costs, tickets and holiday surge. Timestamp and refresh content.
- Use seasonal October–February evidence in site improvements during early 2027. Aim content maturity ahead of **October 2027**; SEO outcomes are not guaranteed.
- Internal link from guides to commercial pages; avoid doorway duplicates for every city-duration permutation.

### Competitive reference sites (research only)
- https://sribhulokhatravels.in/
- https://www.vizagarakutourpackages.com/
- https://vizagarakuholidaytrips.com/
- https://arakutourism.com/
- https://araku-valley.com/

Audit actual live SERPs before expanding; do not presume past page observations or ranking stability.

## 10. 90-day roadmap with independent validation gates

| Window | Business focus | Product/content focus | Evidence / decision |
|---|---|---|---|
| **Days 1–7 (25–31 Oct)** | Interview operators, confirm 2+ responders | Launch tiny website, form + WhatsApp, tagging | Site and tracking work; operator readiness |
| **Days 8–21 (1–14 Nov)** | Run ₹5k Search experiment, handle leads personally, measure quality | Fix funnel, add useful FAQ/cost estimator if time | What are CPC, CPQL, lead quality and response? |
| **Days 22–45 (15 Nov–8 Dec)** | Free pilot referrals, then collect booking-based referral fees | Add 2–4 pages from real intent; revise pricing/copy | Is anyone willing to **pay** for a valid referral? |
| **Days 46–60 (9–23 Dec)** | Collect first payment and document terms, or pivot economics | Admin and routing refinements only if painful | First cash collected; economics reviewed |
| **Days 61–90 (24 Dec–22 Jan)** | Repeat with 2nd partner; decide which destinations/traffic channels to expand | Publish original peak-season research, SEO content, Phase 1 CRM only if required | Repeatability, partner retention, measurable funnel |

**Day-90 outcomes:**
- **Proceed** if at least one partner has paid, another is plausibly ready, qualified enquiries can be sourced and handled, and there is a credible path to profitable organic/paid acquisition.
- **Iterate** if demand exists but response, conversion, pricing or routing is weak; select one constraint to fix and retest.
- **Pause/pivot** if genuine enquiries are expensive, partners will not pay, or referrals cannot be handled ethically/reliably.

Do not use “organic leads by Day 90” as a mandatory gate. Track indexed pages, impressions, click-through and technical health separately as *leading SEO indicators*.

## 11. Founder time and operating rhythm

**Day job constraint:** after the launch sprint, budget **10–15 hours/week**:
- 3 h partner calls, follow-ups and quote maintenance.
- 2–3 h lead qualification/handoffs and payment follow-ups.
- 2–3 h campaign/report review and landing-page tests.
- 3–4 h original commercial content, SEO maintenance, site fixes.
- 1 h weekly retrospective and decisions.

If lead handling requires daytime response and you're unavailable, recruit a reliable partner/assistant or run ads only during response coverage. Slow replies can waste paid demand.

**Simple weekly dashboard:** ad spend, clicks, confirmed enquiries, qualified enquiries, CPQL, handoffs, accepted leads, partner response within SLA, reported bookings, **cash collected**, refund/invalid rate, Search Console impressions/indexed pages, content changes. Keep form conversions distinct from WhatsApp clicks and reported bookings.

## 12. Budget and break-even guardrails

| Item | First-month working estimate |
|---|---:|
| Domain (if not owned) | ₹700–₹1,500/year (planning allowance) |
| Hosting | ₹500–₹1,500/month, depending on provider and existing credits |
| Google Ads first experiment | **₹5,000** |
| Ads extension (optional, gated) | **₹5,000** |
| Travel/field research | ₹0–₹8,000 depending on trip and original-content needs |
| Misc. tools/messaging | ₹0–₹1,000 |

**Minimum cash plan:** roughly ₹6,200–₹9,000 for launch + first ₹5k ad test (excluding travel, taxes and your labour; depends on domain/hosting). Avoid a paid CRM, pricey page builder, automated WhatsApp service or paid SEO suite until justified.

**Economic constraint:** The agreed model is **₹1,000–₹2,000 per verified converted booking, not per enquiry**. A ₹5,000 ad test requires **5 converted bookings at ₹1,000** or **3 at ₹2,000** merely to recover ad spend, before servicing costs, cancellations, taxes or refunds. If ~9 qualified enquiries are acquired in the sample scenario, this corresponds to ~56% or ~33% booking conversion respectively—**difficult assumptions that must be tested rather than promised**. This first campaign is a demand/conversion experiment; do not judge it by immediate break-even.

## 13. Compliance, advertising and customer trust

- India's **DPDP Rules, 2025** were notified on 14 November 2025 with phased commencement. Check which provisions apply as of launch and seek local legal advice for final notices. Regardless of phase-in, collect minimal data, explain referral purpose, record consent, restrict access, offer withdrawal/deletion contact and avoid secondary marketing without separate permission.
- A lead-gen-only business should **not** create an ineligible Google Business Profile. Google's guidelines list lead-generation agents and online-only businesses as ineligible.
- Use actual owner contact information and a working support channel; list business details truthfully, and check Google Ads destination and misrepresentation policies before launch.
- Do not imply official Andhra Pradesh tourism affiliation unless true; no fake scarcity, fake testimonials, unverified discounts or fabricated price guarantees.
- Partners are responsible for delivering their services. Document cancellations, dispute handling, and referral-only role honestly. Consider liability, taxes/invoicing and applicable tourism/local business registrations with an accountant/lawyer.
- Separate essential referral consent from optional marketing consent. Share only the minimum data with one selected partner, as described in the consent notice; seek fresh consent before any broader sharing.
- Ad/analytics cookies and user consent obligations should be checked for the specific setup and jurisdictions rather than assumed to be automatically solved by a checkbox.

## 14. Brand/domain decision — do not block the build

Choose a trustworthy, memorable name that can cover all travel destinations. Avoid a name suggesting you are an official tourism authority or restricting future expansion to Araku. Check `.com`/`.in` availability, trademark conflicts and handle availability; do not assume example candidates are available. If naming takes longer than Day 1, work on a temporary staging subdomain and decide before public ads. Use only the final domain in ads and Search Console.

**Open decisions, with owners and deadlines:**

| Decision | Default | Owner / deadline |
|---|---|---|
| Brand/domain | Broad travel brand, Araku content first | Founder, **25 Oct** |
| Business WhatsApp/contact | Dedicated reachable number with published response hours | Founder, **27 Oct** |
| Partner supply | Minimum 2 reliable local operators | Founder, **29 Oct** |
| First paid product | Araku package enquiries | Founder, **29 Oct** |
| Ads budget | ₹5k first test; ₹5k extension only after review | Founder, **30 Oct** |
| Tech | Django templates + admin; one deploy | Founder, **26 Oct** |
| Operator terms | Free initial pilot then ₹1,000–₹2,000 per verified booking | Founder, **1–14 Nov** |

## 15. Production / Ads go-live checklist

### Product and operations
- [ ] Final brand/domain and SSL work on mobile.
- [ ] The launch Araku package page has truthful, useful content and visible enquiry CTAs; cab page and cab ads remain P1.
- [ ] Privacy policy, terms, contact and independent-referral notice are live.
- [ ] Form stores a valid lead with notice version, source and consent; rejects invalid submission.
- [ ] WhatsApp opens your business account, and response/consent process is ready.
- [ ] At least two operators consent to receive suitable referred leads.
- [ ] Lead can be viewed privately, qualified and manually forwarded.
- [ ] Test notifications, backup and restore, error handling, admin login and spam guard.

### Measurement and paid acquisition
- [ ] GA4 and Google Ads tags implemented; duplicate form submissions do not double-count.
- [ ] Form conversion tested; WhatsApp click measured separately.
- [ ] Thank-you page not indexable; no personal data in event URLs or ad analytics.
- [ ] UTMs and click IDs stored appropriately; test campaign attribution.
- [ ] Search campaign uses page-matched ad copy and relevant location/keywords.
- [ ] Negative keywords and search-term monitoring process created.
- [ ] Budget/end date set; daily spend and lead quality review scheduled.
- [ ] Ad account billing and policy review complete; ads serving verified before reporting a launch.

## 16. References and verification links

**Primary references (accessed/verified 25 Oct 2026):**
- Google Ads spending limits: https://support.google.com/google-ads/answer/10486637
- Google Ads campaign total budget overview (availability is feature- and campaign-dependent): https://developers.google.com/google-ads/api/docs/campaigns/budgets/overview
- DPDP Rules notification / phased implementation, Government of India: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190014
- Google Business Profile eligibility: https://support.google.com/business/answer/13762416
- Google Search SEO starter guide: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- Google Search spam policies: https://developers.google.com/search/docs/essentials/spam-policies

**Research note:** Price estimates, lead prices, timelines, cost-per-click and KPI thresholds in this document are *planning hypotheses*, not independently validated market quotes. Where a provider-specific term changes, verify current policy before making spending or compliance decisions.

---

### Immediate next action
**Today:** decide a usable brand/domain, start contacting operators, and collect at least two dated, real Araku package/cab quotations. **Build only what is required to convert and route the first enquiry.**
