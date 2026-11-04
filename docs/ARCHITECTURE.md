# Resto Radar — Architecture

## System overview

```
 ┌──────────────┐   ┌──────────────┐
 │ apps/web     │   │ apps/mobile  │      (Next.js, Expo — both use packages/api-client)
 └──────┬───────┘   └──────┬───────┘
        └─────── HTTPS / JSON ───────┐
                                     ▼
                         ┌───────────────────────┐
                         │ services/api (FastAPI)│── auth, profiles, venues, watches,
                         └──────────┬────────────┘   feed, radar, comparison, admin
                                    │
          ┌─────────────────────────┼──────────────────────────┐
          ▼                         ▼                          ▼
  Postgres + PostGIS +        Redis (queue,               S3 / MinIO
  pgvector                    cache, rate limits)          (snapshots, thumbnails)
          ▲                         │
          └──────────┬──────────────┘
                     ▼
        services/workers (Celery beat + workers)
        ├─ places_sync      Google Places / Foursquare / OSM → venue
        ├─ site_discovery   find menu / news / gallery pages on a venue website
        ├─ watch_crawler    fetch → normalise → snapshot (robots.txt-aware, per-host rate limit)
        ├─ differ           structural + text diff, LLM change classification
        ├─ notifier         feed rows, Expo push, weekly email digest
        ├─ radar_collect    RSS / API / sitemap / HTML collectors per source config
        ├─ radar_process    lang detect, dedup, summary, typing, field extraction, embedding
        ├─ radar_score      relevance + value per (item, owner), mandatory lane
        └─ source_discovery propose new sources → admin review queue
```

## Core data model (initial)
| Table | Key columns |
|---|---|
| `user` | id, email, locale, created_at |
| `owner_profile` | user_id, venue_id (own), venue_type, cuisines[], price_level, location (geography), seats, staff_band, service_modes[], goals[], budget_band, hours_per_month, languages[], embedding vector |
| `venue` | id, name, address, city, country, location (geography), cuisines[], price_level, website_url, phone, source, source_place_id, attribution, last_synced_at |
| `watch` | id, user_id, venue_id, channels[], threshold, created_at |
| `watched_page` | id, venue_id, url, kind (home/menu/news/gallery/event), robots_allowed, crawl_interval, etag, last_hash |
| `snapshot` | id, watched_page_id, fetched_at, content_hash, text_extract, structured jsonb (menu items, prices, offers), s3_key |
| `change_event` | id, venue_id, watched_page_id, kind, before jsonb, after jsonb, significance, summary, detected_at |
| `feed_item` | id, user_id, change_event_id, insight, read_at, notified_at |
| `menu_item` | id, venue_id, name, category, price_cents, currency, first_seen, last_seen |
| `radar_source` | id, region, name, url, kind (rss/api/sitemap/html), category, authority (0–1), language, enabled, status (proposed/approved/rejected) |
| `radar_item` | id, source_id, url, title, published_at, language, type, summary_i18n jsonb, fields jsonb (dates, cost, applies_to), embedding vector, dedup_key |
| `radar_score` | item_id, user_id, relevance, value, mandatory, ring, rationale, computed_at |
| `radar_feedback` | item_id, user_id, action (save/dismiss/plan/remind), at |
| `llm_usage` | id, task, model, tokens_in, tokens_out, cost_eur, at |

## Key flows

### Competitor change detection
1. `watch_crawler` picks due `watched_page` rows (per-host token bucket in Redis; obey
   robots.txt and `Crawl-delay`; conditional GET with ETag/Last-Modified).
2. Normalise: strip boilerplate, extract text; menus (HTML tables / PDFs) → structured
   items via parser first, LLM extraction only as fallback.
3. If `content_hash` unchanged → stop. Else store snapshot, run `differ`:
   structured diff for menu items/prices, text diff for the rest, image set diff by
   perceptual hash.
4. LLM classifies + summarises the change into `change_event` with significance 0–1.
5. `notifier` fans out to watchers whose threshold ≤ significance; generates the
   "what you could learn" insight per owner profile (cached per profile cluster).

### Radar scoring
`relevance = 100 × clamp(0.6·cos_sim(item, profile) + 0.4·rule_boosts)`

`value = 100 × (w_i·impact + w_c·(1−cost_norm) + w_e·(1−effort_norm) + w_t·urgency) × confidence`

Weights in `config/scoring.yaml`. Ring: Act now if value ≥ 70 and deadline ≤ 60 days or
mandatory; Plan if value ≥ 45; else Watch. LLM provides impact/cost/effort bands +
rationale with a strict JSON schema; numbers are computed in code, not by the LLM.

## Cross-cutting
- **Region config**: `config/region.<code>.yaml` (languages, bbox, place sources,
  radar source file). Adding a city = new config + places import job.
- **LLM gateway** module: one place for prompts, JSON-schema validation, retries,
  caching by input hash, cost logging, daily budget cap. Use a smaller/cheaper Claude
  model for classification and a stronger one for insights/rationales.
- **API contract**: FastAPI generates OpenAPI → `packages/api-client` is regenerated in
  CI; a contract diff fails the build if clients are not updated.
- **Security**: JWT auth, row-level ownership checks, rate limiting, SSRF protection in
  crawlers (block private IP ranges), secrets via env only.
- **Testing**: pytest + recorded HTTP fixtures (respx/vcrpy) for crawlers; Playwright e2e
  for web; Jest + React Native Testing Library for mobile; Maestro for mobile e2e later.
- **CI**: GitHub Actions — lint, typecheck, tests, OpenAPI client check, docker build.
- **Deploy (suggested)**: API + workers on Fly.io / Render / a small VPS in the EU,
  managed Postgres in an EU region, Vercel for web, EAS Build for mobile.
