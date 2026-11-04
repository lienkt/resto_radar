# How the agents work (inside the team process)

People, ownership, reviews and rituals are in **`docs/TEAM.md`**. This file covers the
agents each human drives.

## Agents
| Agent (`.claude/agents/`) | Owns | Model |
|---|---|---|
| **Orchestrator** (your main session) | your assigned issues: delegation, agent review gate, draft PR | your default |
| `product-manager` | drafts stories + acceptance criteria (humans create the issues) | sonnet |
| `architect` | ADRs, data model, API contract, repo structure | opus |
| `backend-engineer` | `services/api`, migrations, auth, endpoints | sonnet |
| `data-ingestion-engineer` | places sync, website crawling, menu parsing, diffing | sonnet |
| `radar-engineer` | radar collectors, processing, scoring, source discovery, LLM gateway | opus |
| `web-engineer` | `apps/web` incl. admin console | sonnet |
| `mobile-engineer` | `apps/mobile`, push notifications, EAS config | sonnet |
| `devops-engineer` | CI/CD, containers, environments, observability, backups | sonnet |
| `code-reviewer` | correctness, maintainability, conventions (read-only) | opus |
| `qa-engineer` | tests against acceptance criteria, bug reports (read/write tests only) | sonnet |
| `compliance-reviewer` | security, GDPR, data-source terms (read-only) | opus |

Engineering agents run in isolated git worktrees (`isolation: worktree`), so your parallel
agents never collide with each other. Subagents cannot call each other — the orchestrator
passes work and context between them.

## Flow of one issue
```
Planning (humans)          You                           Agents (yours)                   Team
─────────────────          ───                           ──────────────                   ────
/plan-milestone  ──►  pick a Ready issue,  ──►  /build-story <#>:                  ──►  human review
issues created        assign it to you          engineer agent(s) in a worktree          (≠ you; 2 incl. TL
                                                → code-reviewer → qa-engineer             for critical areas)
                                                → compliance-reviewer (if in scope)      → you squash-merge
                      verify by hand  ◄──       draft PR with handoff
```

## Rules for delegation prompts
Every task given to a subagent includes: the issue number, acceptance criteria, files/areas
it may touch, the contract it must follow, and the definition of done from
`docs/CONVENTIONS.md`. Keep tasks to roughly one PR each.

## Slash commands
| Command | Who uses it | What it does |
|---|---|---|
| `/plan-milestone M2` | PO + TL | drafts stories, design work and order; creates issues after approval |
| `/build-story 42` | assignee of #42 | builds the issue end to end, opens a draft PR |
| `/review-branch [branch\|PR#]` | anyone | agent review gate on your branch or a teammate's PR (report only) |
| `/standup` | everyone, daily | drafts your async stand-up from GitHub |
| `/ship-check staging 0.3.0` | TL / PO | release go/no-go report |

## Human checkpoints
- PO approves each milestone's stories before issues are created.
- PO approves any new radar source, data provider or paid API.
- Humans approve and merge every PR; TL approves changes to `.claude/`, CI and critical areas.
- Humans deploy, after `/ship-check` says GO.
- Humans add all keys and secrets.
