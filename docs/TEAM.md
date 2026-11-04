# Working as a team of humans + agents

**Core rule: humans are accountable, agents are tools.** Every agent session belongs to
one person, and that person owns everything it produces as if they had written it.

## 1. Roles
| Role | Who | Responsibilities |
|---|---|---|
| Product owner (PO) | Nhan | priorities, scope, acceptance, releases, data-provider and budget decisions |
| Tech lead (TL) | one experienced engineer | architecture, approves ADRs, owns `.claude/` and CI, second approver on critical areas, production secrets |
| Engineers | 2–5 people | own assigned issues end to end, drive their own agents, review each other's PRs |
| Agents | `.claude/agents/` | do work delegated by a human; never own an issue; never merge or deploy |

Each engineer runs Claude Code on their own machine with their own Anthropic account and
their own GitHub identity. The repo's shared agents, rules, hooks and slash commands make
everyone's agents behave the same way.

## 2. Work tracking: GitHub Issues + Project board
- Every story, bug and ADR is a GitHub issue created from the templates in `.github/ISSUE_TEMPLATE/`.
- Board columns: **Backlog → Ready → In progress → In review → Done**.
- An issue is **Ready** only when it has acceptance criteria, an `area:*` label, a `mode:*` label and an estimate.
- **One issue = one assignee (a human) = one branch = one PR.** Agents work only on issues assigned to the person running them; `/build-story` refuses otherwise. This is how double work is prevented.
- Milestones in GitHub = product milestones M0–M5.

### Labels (created by `scripts/setup-github.sh`)
- `type:story`, `type:bug`, `type:adr`, `type:chore`
- `area:api`, `area:workers`, `area:radar`, `area:web`, `area:mobile`, `area:infra`, `area:harness`
- `mode:agent-heavy` (agents do most of the work, human reviews), `mode:human-led` (human designs/decides, agents assist), `mode:human-only`
- `needs-security-review`, `needs-po-decision`, `blocked`, `agent-built`

### What goes in which mode
- **agent-heavy:** CRUD endpoints, UI screens from an agreed design, tests, new radar collectors, refactors, docs.
- **human-led:** architecture/ADRs, auth, crawling policy, data deletion, scoring weights, LLM prompts shown to owners.
- **human-only:** choosing providers and reading their terms, conversations with restaurant owners, legal, production access, releases.

## 3. Branches, collisions, contracts
- Branch name: `feat/<issue>-<slug>` / `fix/<issue>-<slug>`; PR body contains `Closes #<issue>`.
- Keep PRs small and branches short-lived (merge within 1–3 days). Rebase on `main` daily.
- **Contract first:** API changes are merged as their own small PR (OpenAPI + generated client) before backend, web and mobile work starts in parallel.
- Migrations: only one open PR with a migration per service at a time — announce it in the issue to avoid Alembic head conflicts.
- Areas have code owners (`.github/CODEOWNERS`), so the right human is requested automatically.

## 4. Review rules
1. **Agent gate first** (`/review-branch`): code-reviewer, qa-engineer, compliance-reviewer if in scope. Fix blockers before asking a human.
2. **Human approval required to merge:** at least **1 approval from someone other than the person who drove the agents**.
3. **2 approvals (incl. TL)** for: `area:harness`, `area:infra`, auth, crawling/robots logic, personal-data handling, data deletion, LLM prompts, and anything labelled `needs-security-review`.
4. The PR's **"Agent involvement"** section says what agents produced, what the human verified by hand, and anything the human is unsure about.
5. Reviewers review design and risk; style is the formatter's and code-reviewer's job.
6. The author merges (squash) after approvals and green CI. Nobody merges their own PR without a review.

## 5. Shared vs personal configuration
| Shared — changed only by PR, TL review | Personal — never committed |
|---|---|
| `CLAUDE.md`, `docs/*` | `.claude/settings.local.json` (personal permissions, model choice) |
| `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` | your own Anthropic account / API key |
| `.claude/settings.json`, `.mcp.json` | your `.env` with **dev** keys |
| `.github/`, `.pre-commit-config.yaml` | |

- **Improve agents through PRs.** If an agent keeps making the same mistake, fix its instructions in a PR (`area:harness`) so everyone's agents improve.
- **Secrets:** everyone has personal dev keys. Staging/production secrets live only in the hosting platform's secret manager; access = PO + TL.

## 6. Rhythm
| When | What | Tool |
|---|---|---|
| Daily (async, by 10:00) | 3–5 lines: merged, in progress (incl. what your agents are running), blocked | `/standup` drafts it from GitHub |
| Weekly – Monday | Planning: PO presents priorities; humans pull Ready issues | board |
| Weekly – Friday | Demo of merged work (web + mobile) + 15-min **agent retro**: which agent outputs needed heavy fixing → harness PRs | |
| Per milestone | `/plan-milestone` before, `/ship-check` + retrospective after | |
| Monthly | Cost review: Claude usage per person, LLM cost inside the app per active owner | |

## 7. Communication
- Decisions → ADR (`docs/adr/`) linked from the issue. Discussion → issue comments, not private chats.
- Agent handoff notes go into the **PR description** (section "Agent handoff"), so they live next to the code and are searchable.
- Ask the PO in the issue with label `needs-po-decision` instead of letting an agent guess.

## 8. Onboarding a new person (½ day)
1. Read `README.md`, `docs/SPEC.md`, this file, `docs/HARNESS.md`, `docs/CONVENTIONS.md`.
2. Do the local setup in `docs/HARNESS.md` and `gh auth login`.
3. Pair with someone on one `mode:agent-heavy` issue: watch `/build-story`, then do one yourself.
4. First PRs are small; TL reviews the first three.

## 9. Scaling
Start with **PO + TL + 1–2 engineers**. Add people when review turnaround stays under one
working day. With agents, human review becomes the bottleneck long before coding does —
watch the "In review" column, not the "In progress" one.
