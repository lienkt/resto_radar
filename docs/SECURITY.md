# Security & privacy baseline

Target: **OWASP ASVS 5.0 Level 2** for web/API and **OWASP MASVS (L1 + resilience basics)** for mobile, GDPR for personal data.
This is an engineering baseline, not legal advice — a lawyer should confirm the privacy policy, data-processing agreements and data-source licensing before launch.

## 1. Threat model (STRIDE summary — update when components change)

| Component | Main threats | Controls |
|---|---|---|
| Public API | broken access control (IDOR), credential stuffing, injection, abuse/scraping of our own API | authz check on every query by `user_id`; rate limiting per IP + user; ORM/bound params only; schema validation; WAF/CDN in front |
| Auth | account takeover, session theft | managed auth provider, MFA for admins (optional for owners), short-lived access tokens + rotating refresh tokens, secure storage on mobile |
| Crawlers / collectors | SSRF into internal network, malicious/huge pages, being blocked or sued for ToS violation | block private/link-local/metadata IPs after DNS resolution, size/time limits, no JS execution outside sandboxed Playwright, robots.txt + rate limits, source allow-list approved by admin |
| LLM pipeline | prompt injection from crawled text, data leakage, runaway cost | crawled text only as delimited data; LLM has no tools/actions; output schema validation; no personal data in prompts; daily budget cap + alerts |
| Admin console | privilege escalation, insider misuse | role-based access, MFA, audit log of every admin action, separate admin route group |
| Object storage | public exposure of snapshots | private buckets, signed URLs with short expiry |
| Workers / queue | poisoned tasks, replay | queue not exposed publicly, task payloads validated, idempotency keys |
| CI/CD & supply chain | malicious dependency, leaked secrets, compromised action | lockfiles, Dependabot, pip-audit/pnpm audit, Trivy, gitleaks, actions pinned to SHA, least-privilege tokens, protected `main`, CODEOWNERS on guardrail files |
| AI coding agents | agent leaks secrets, runs destructive commands, weakens its own guardrails | `.claude/settings.json` deny rules + hooks, secrets never on disk in the repo, human approval for push/merge/deploy/workflow edits, all work via reviewed PRs |

## 2. Checklist (ticked per release in `/ship-check`)

### Authentication & sessions
- [ ] Managed provider (ADR-001); passwords never handled by our code
- [ ] MFA enforced for admin role
- [ ] Access token ≤ 15 min, refresh token rotation + revocation on logout/password change
- [ ] Mobile tokens in `expo-secure-store`, never AsyncStorage
- [ ] Web: HttpOnly, Secure, SameSite cookies; CSRF protection for cookie-based flows

### Access control
- [ ] Every endpoint has an explicit auth dependency; default deny
- [ ] Every DB query for user-owned data filtered by owner; tests for cross-user access (IDOR)
- [ ] Admin endpoints separately routed and role-checked; admin actions written to `audit_log`

### Input, output, API
- [ ] Pydantic validation on all input; max lengths; pagination limits
- [ ] Rate limiting (e.g. slowapi/Redis) on auth, search and expensive endpoints
- [ ] Security headers on web: CSP (no `unsafe-inline` scripts), HSTS, X-Content-Type-Options, Referrer-Policy, frame-ancestors
- [ ] CORS restricted to our origins
- [ ] Error responses never leak stack traces or internals

### Crawling & external data
- [ ] SSRF guard (post-DNS IP check, redirect re-check, no `file://`/`gopher://`)
- [ ] Response size + time limits; content-type allow-list; PDF parsing in a resource-limited worker
- [ ] robots.txt respected; per-host rate limit; identifiable User-Agent with contact page
- [ ] Each data provider's terms, attribution and caching limits implemented as in ADR-002

### Data protection (GDPR)
- [ ] Data inventory + processors list (hosting, auth, email, push, Anthropic, places providers) in the privacy policy
- [ ] EU hosting region for database and backups
- [ ] Encryption in transit (TLS 1.2+) and at rest (managed DB/storage encryption)
- [ ] Export (`GET /me/export`) and deletion (`DELETE /me`) implemented and tested; deletion propagates to backups within the retention window
- [ ] Retention: snapshots 12 months, logs 30 days, LLM usage logs without content
- [ ] No personal data of third parties (competitor staff/customers) stored from crawled pages

### Secrets & infrastructure
- [ ] Secrets only in the platform secret manager / local `.env` (gitignored); `.env.example` documents names only
- [ ] gitleaks in pre-commit and CI; secret scanning + push protection enabled on GitHub
- [ ] Least-privilege DB roles: app role without DDL; migration role used only by the migration job
- [ ] Containers run as non-root; images scanned (Trivy); base images updated monthly
- [ ] Backups automated, encrypted, restore tested every 30 days

### Mobile (MASVS)
- [ ] No secrets in the app bundle (only public config)
- [ ] TLS only; consider certificate pinning after launch
- [ ] Deep links validated; push payloads contain IDs, not sensitive content
- [ ] Release builds: no debug logging, minification enabled

### LLM features
- [ ] Prompt templates versioned; injection test cases in the eval set (pages containing "ignore previous instructions…")
- [ ] Output validated against JSON schema; failures retried then dropped, never shown raw
- [ ] AI-generated content labelled in UI with source link
- [ ] Daily cost cap enforced in the gateway; alert at 80%

## 3. Before public launch
- External penetration test (web + API + mobile) by a qualified firm.
- Senior human code review of auth, crawling and data-deletion code.
- Lawyer review of privacy policy, terms of service, DPAs and data-source licences.
- `security.txt` and a contact address for vulnerability reports.
