# Resto Radar — Product Spec (v1, Brussels pilot)

## Users
- **Owner** (primary): runs 1–3 restaurants/cafés. Wants to see what competitors and
  inspiring venues are doing, and to not miss opportunities or obligations.
- **Admin** (internal): manages sources, moderates data, watches crawl health.

## Owner profile (drives all personalisation)
Created at onboarding (the owner can also claim their own venue from the places database):
- Venue type (restaurant, café, bar, bakery, food truck…), cuisine(s), price level
- Location (address → geo point), seats, staff size band, opening hours
- Service model: dine-in / takeaway / delivery / catering
- Goals (multi-select): more covers, higher ticket, sustainability, digitalisation,
  staff retention, compliance, new concept…
- Budget band for investments and time available per month
- Languages (FR/NL/EN)
The profile is stored as structured fields + a text embedding used for ranking.

---

## Module 1 — Competitor Watch

### 1.1 Search & discover
- Search by free-text address, city, country; map view + list view.
- Filters: cuisine, price level, distance radius, rating band (only where the source licenses it), open now.
- Data comes from the **places layer** (Google Places API / Foursquare / OSM), normalised
  into our `venue` table with source IDs and attribution.
- "Suggested to watch": venues similar to the owner (same cuisine/price within N km) and
  "inspiration" venues (same concept, any city).

### 1.2 Follow a venue
Following creates a **watch** on the venue's channels:
- Website (homepage + discovered menu/news/events pages)
- Menu (HTML page or PDF; parsed into dishes + prices)
- Images (website gallery; licensed place photos referenced via API only)
- Campaigns/promotions (detected on website: offers, events, new hours, set menus)
- Official social accounts only where an official API permits it (phase 2).

### 1.3 Change detection & notifications
- Crawl schedule per channel (default: daily for menu/website, weekly for images).
- Pipeline: fetch → normalise → snapshot → diff vs previous → LLM classifies the change
  (new dish, price change, removed dish, new campaign, new photos, redesign, hours change)
  → significance score → notification if above the owner's threshold.
- Channels: in-app feed, mobile push (Expo), weekly email digest.
- Each change card shows what changed (before/after), when, and a short
  **"What you could learn"** insight generated against the owner's profile.

### 1.4 Insights
- Price benchmarking: median price per dish category in the area vs the owner's menu.
- Trend tiles: dishes/ingredients/campaign types appearing more often among watched venues.

---

## Module 2 — Innovation Radar

### 2.1 Collection
- Curated sources per region in `config/sources.<region>.yaml`: laws & regulations,
  food-safety notices, grants/subsidies, trade fairs & events, courses/training, sector news.
- Collectors: RSS/Atom, official APIs, sitemaps, and HTML crawling where permitted.
- **Source discovery** (weekly): proposes new sources from outbound links in collected
  items and web search. New sources go to an admin review queue; never auto-enabled.

### 2.2 Processing
Each item → language detection → dedup (URL + near-duplicate embedding) → summary in the
owner's language → type:
`law | regulation_change | grant | event | course | news | technology | supplier_offer`
→ extracted fields: published / effective / deadline / event dates, cost, location,
who it applies to.

### 2.3 Relevance + value scoring
For each (item, owner) pair:
- **Relevance (0–100)**: embedding similarity between item and profile, plus rule boosts
  (same city/region, venue type, cuisine keywords, goal match).
- **Value score (0–100)** from:
  - expected impact (revenue gain / cost saving / risk avoided — LLM estimate as a band),
  - cost (money) and effort (hours) vs the owner's budget band,
  - time sensitivity (deadline proximity),
  - confidence (source authority × extraction certainty).
- **Mandatory flag**: laws/regulations that apply to the owner appear in a separate
  "Compliance" lane and are never ranked below optional opportunities.
- Every score shows a 1–3 line **rationale** and links to the original source.
- Weights live in config (`config/scoring.yaml`) so they can be tuned without deploys;
  owner feedback (save/dismiss) is logged to calibrate them later.

### 2.4 Compare & decide
- Radar view (rings: Act now / Plan / Watch; sectors: item type) + sortable list.
- Select 2–4 items → side-by-side comparison (cost, effort, impact, deadline, ROI band).
- Owner actions: save, dismiss (feeds ranking), add to plan, set reminder.

---

## Platforms
- Web (Next.js): full experience incl. admin console.
- Mobile (Expo iOS/Android): feed, notifications, search/map, radar, comparison, profile.
  Admin is web-only.

## Non-functional
- UI languages: FR, NL, EN from day one.
- p95 API read latency < 300 ms; notification within 24 h of a detected change.
- GDPR: data export/delete, privacy policy, cookie consent on web.
- Observability: structured logs, crawl success-rate dashboard, LLM/API cost tracking
  with per-day budget caps.

## Out of scope for v1
Payments/subscriptions, social media monitoring, review scraping, multi-user teams per
venue, regions other than Brussels (but config-ready).

## Milestones
1. **M0 Foundations** — monorepo, docker compose, auth, profile onboarding, CI with
   coverage + security scans, pre-commit, branch protection, Sentry, staging environment,
   feature flags, audit log, GDPR export/delete skeleton.
2. **M1 Places & search** — Brussels venues imported, search + map on web & mobile.
3. **M2 Watch & notify** — follow venues, website/menu crawl, diffs, change feed, push.
4. **M3 Radar collect** — sources config, collectors, item processing, admin queue.
5. **M4 Radar score** — relevance/value scoring, radar view, comparison, feedback loop.
6. **M5 Launch readiness** — full `docs/SECURITY.md` checklist, threat model review,
   load test, backup-restore drill, alerts from `docs/OPERATIONS.md`, i18n polish,
   privacy policy + terms (lawyer-reviewed), external penetration test, store builds.

## Acceptance examples
- Owner of a Vietnamese restaurant in Ixelles follows 5 nearby Asian restaurants; one
  adds a lunch formula at €16.50 → within 24 h a push arrives: "Pho Saigon added a €16.50
  lunch formula (3 courses)" with before/after and an insight.
- A new Brussels-Capital grant for energy-efficient kitchen equipment is published →
  appears in "Act now" for owners with goal "sustainability", with deadline, max amount,
  effort estimate and rationale.
- A new federal food-safety labelling rule for allergens → shown in the Compliance lane
  for every owner, regardless of goals.
