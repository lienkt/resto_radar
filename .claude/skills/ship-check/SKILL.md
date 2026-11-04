---
name: ship-check
description: Release-readiness check before a staging or production release of Resto Radar — security checklist, migrations, observability, rollback, store/legal items.
argument-hint: "<staging|production> <version>"
disable-model-invocation: true
---
Run the release-readiness check (gh read-only: release PRs, milestone issues, CI runs) for **$ARGUMENTS**. You do not deploy; you produce a go/no-go report for the product owner.

Check and report each item as ✅ / ⚠️ / ❌ with evidence (file, command output, link):
1. CI on the release commit is green: lint, types, tests, coverage thresholds, OpenAPI client check, security scans (CodeQL, Semgrep, Bandit, gitleaks, pip-audit/pnpm audit, Trivy) with no open high/critical findings.
2. `docs/SECURITY.md` checklist (ASVS/MASVS items) fully ticked for features in this release; threat model updated for new components.
3. Database migrations: reviewed, expand/contract safe, tested up+down on a copy of staging data, backup taken and restore tested in the last 30 days.
4. Observability: Sentry release created, alerts configured (API errors, crawl failure rate, LLM daily budget), dashboards exist.
5. Rollback plan written in the release notes (previous image tag, feature flags to disable, migration compatibility).
6. All issues in the milestone closed or moved; `CHANGELOG.md` updated; version bumped (SemVer); mobile build numbers incremented.
7. Legal/compliance: privacy policy and data-processor list current, new data providers' terms approved, AI-generated content labelled.
8. Production only: staging has run this exact version ≥ 48 h without new error classes.

Finish with GO / NO-GO and the exact commands or console steps the product owner must perform to deploy.
