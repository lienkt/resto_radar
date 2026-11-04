# Operations runbook

## Environments
| Env | Purpose | Deploy | Data |
|---|---|---|---|
| dev | local `docker compose` | developer/agent | seed + fixtures |
| staging | mirrors production config, EU region | automatic on merge to `main` (after CI) | anonymised copy / synthetic |
| production | real owners | manual approval by product owner after `/ship-check` GO | real |

Feature flags (simple DB/config-driven) gate unfinished features so `main` stays releasable.

## Observability
- **Errors:** Sentry projects for api, workers, web, mobile; releases tagged with git SHA.
- **Logs:** JSON (structlog / pino), `request_id` propagated API → workers.
- **Traces/metrics:** OpenTelemetry → provider chosen in an ADR (e.g. Grafana Cloud EU).
- **Dashboards:** API latency/error rate, queue depth, crawl success rate per host, radar items/day per source, LLM tokens + € per day, push delivery rate.

## Alerts (initial thresholds)
| Alert | Condition | First action |
|---|---|---|
| API error rate | 5xx > 2% for 5 min | check Sentry for new error class; roll back if it started with a release |
| API latency | p95 > 800 ms for 10 min | check DB slow queries, Redis, recent deploy |
| Queue backlog | > 5,000 tasks or oldest > 1 h | scale workers; look for a failing task type |
| Crawl failure | success rate < 80% (24 h) | check robots/blocks per host; pause offending hosts |
| Source silent | radar source no items for 2× its normal interval | check source page/feed changed; mark source degraded |
| LLM budget | 80% of daily cap | check for loops/duplicates; lower batch sizes |
| Backups | last successful backup > 26 h | trigger manual backup, investigate job |

## Routine
- **Weekly:** review Dependabot PRs; check crawl health and proposed sources queue.
- **Monthly:** restore a backup into a scratch DB and run smoke tests; update base images; review LLM cost per active owner.
- **Quarterly:** review the threat model and access list (who has admin, who has cloud console access).

## Release & rollback
1. Merge → staging deploy → smoke tests → `/ship-check production <version>`.
2. Product owner deploys: run migration job, then roll out new API/worker images, then web; mobile via EAS (OTA for JS-only fixes, store build otherwise).
3. Rollback: redeploy previous image tag (migrations are backward compatible by convention); disable feature flag; for mobile, publish previous OTA update.

## Incident handling
1. Acknowledge, open an incident note in `docs/incidents/YYYY-MM-DD-<slug>.md`.
2. Mitigate first (rollback, flag off, pause crawler/source), then investigate.
3. Personal-data breach: assess within 24 h; if required, notify the Belgian Data Protection Authority within 72 h of becoming aware and inform affected users.
4. Blameless post-mortem with action items added to the backlog.
