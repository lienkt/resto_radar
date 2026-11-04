# Engineering conventions

These apply to every human and agent working on Resto Radar. The code-reviewer enforces them.

## Repository & git
- Trunk-based: `main` is always releasable and protected (PR + green CI + 1 approval; no direct pushes, no force pushes).
- Branches: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, `chore/<slug>`; PR body has `Closes #<issue>`. One story ≈ one PR, ideally < 400 changed lines.
- Commits: [Conventional Commits](https://www.conventionalcommits.org) — `feat(api): add venue search endpoint (#12)`.
- Versions: SemVer; `CHANGELOG.md` generated from commits at release.
- Every PR uses the PR template, links its issue and fills in "Agent involvement". Squash merge only.

## Definition of done (every story)
1. Acceptance criteria met and covered by automated tests.
2. Lint, format, typecheck, tests and security scans green locally and in CI.
3. Coverage does not drop; new code ≥ 80% lines (services), ≥ 70% (apps).
4. API changes: OpenAPI updated, `packages/api-client` regenerated, backward compatible or versioned.
5. DB changes: Alembic migration, reversible, expand → migrate → contract for anything destructive.
6. Docs updated (ARCHITECTURE/ADR/OPERATIONS/README) when behaviour or operations change.
7. PR description complete, including "Agent involvement" and the agent handoff.
8. code-reviewer: APPROVE; qa-engineer: PASS; compliance-reviewer: no open blocker/major when in scope.
9. Human approval(s) per `docs/TEAM.md` §4 — never only the person who drove the agents.

## Python (services/api, services/workers)
- Python 3.12, `uv`, `ruff` (lint + format), `mypy --strict` on new modules, `pytest` + `pytest-asyncio`.
- Layers: `routers/` (HTTP only) → `services/` (business logic) → `repositories/` (DB access) → `models/`. Routers never touch the session directly.
- Pydantic v2 schemas for every request/response; no raw dicts across layers.
- Errors: domain exceptions → one exception handler → standard error body `{code, message, details}`.
- Config: `pydantic-settings`, read once; no `os.environ` scattered in code.
- Time: store UTC (`timestamptz`), convert to Europe/Brussels only for display. Money: integer cents + ISO currency.
- Logging: `structlog` JSON, include `request_id`/`task_id`; never log tokens, emails or crawled page bodies.
- Workers: tasks idempotent, retries with backoff + jitter, timeouts on every network call, per-host rate limits.

## TypeScript (apps/web, apps/mobile, packages)
- `strict: true`, no `any` (use `unknown` + narrowing), ESLint + Prettier, Vitest/Jest.
- API access only through `packages/api-client` + TanStack Query hooks in a `features/<domain>/api.ts` file.
- Folder by feature: `features/<domain>/{components,hooks,api,types}`; shared UI in `components/ui`.
- All user-visible text through i18n keys (FR/NL/EN); no hard-coded strings.
- Accessibility: labels on interactive elements, WCAG AA contrast, keyboard (web) and screen reader (mobile) checks.

## Dependencies
- Adding a dependency needs a one-line justification in the PR (why, maintenance status, licence). Prefer well-maintained, permissively licensed packages (MIT/BSD/Apache-2.0).
- Lockfiles committed; Dependabot PRs reviewed weekly.

## LLM usage in the product
- All calls via the LLM gateway; prompts in versioned files; outputs validated against JSON schemas.
- Crawled/collected text is placed in clearly delimited data sections and never treated as instructions.
- Every AI-generated text shown to owners is labelled and links to its source.
