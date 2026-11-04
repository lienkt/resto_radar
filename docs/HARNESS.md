# The Claude Code harness — how the agent team is controlled

Defence in depth: instructions tell the agents what to do; permissions, hooks and CI
make sure that even a confused or manipulated agent cannot do serious damage.

| Layer | File | What it does |
|---|---|---|
| 1. Project memory | `CLAUDE.md`, `docs/CONVENTIONS.md` | Stack, rules, definition of done — loaded every session |
| 2. Specialised agents | `.claude/agents/*.md` | 11 roles with least-privilege tools; reviewers cannot edit files; engineers work in isolated git worktrees |
| 3. Permissions | `.claude/settings.json` → `permissions` | Safe commands auto-allowed; push/merge/new dependencies/web access ask you; secrets, force-push, deploys, `curl`, `sudo` denied |
| 4. Hooks (deterministic) | `.claude/hooks/*.py` | `protect-files`: blocks secrets, asks before guardrail/CI edits · `guard-bash`: blocks destructive, exfiltrating and deploy commands incl. chained variants, plus GitHub merges, approvals and settings changes · `format-and-scan`: auto-formats every edit and rejects hard-coded secrets · `session-start`: injects a briefing: branch, my assigned issues, PRs waiting for my review |
| 5. Workflows as commands | `.claude/skills/*/SKILL.md` | `/plan-milestone`, `/build-story`, `/review-branch`, `/standup`, `/ship-check` — the same process every time |
| 6. Tools | `.mcp.json` | Playwright MCP so web/QA agents can open and check the running app |
| 7. Git & CI gate | `.pre-commit-config.yaml`, `.github/` | pre-commit (format, lint, gitleaks), CI tests + coverage + security scans, protected `main`, CODEOWNERS |
| 8. Team gate | GitHub + `docs/TEAM.md` | issues assigned to one human, CODEOWNERS per area, approval by someone other than the agent driver, 2 approvals for critical areas |
| 9. Human gate | PO / TL | approve scope, merges, workflow/guardrail edits, keys, deployments |

## Your one-time setup
1. Install: Claude Code, Node LTS + pnpm, Python 3.12 + uv, Docker, `pre-commit` (`uv tool install pre-commit`), then `pre-commit install`.
2. GitHub (once, by an admin): `gh auth login`, then `./scripts/setup-github.sh OWNER/REPO` — creates labels and milestones, squash-only merging, secret scanning and branch protection on `main`. Then replace the placeholders in `.github/CODEOWNERS` and create the Project board (the script prints the remaining steps).
   Every team member: `gh auth login` with their own account.
3. Start `claude` in the repo root; approve the project hooks and the Playwright MCP server when asked; check `/agents`, `/hooks` and `/permissions`.
4. Personal overrides go in `.claude/settings.local.json` (gitignored), not in the shared file.
5. Optional, stronger isolation: run Claude Code with its sandbox enabled (`/sandbox`), or inside a dev container, so Bash cannot reach files or networks outside the project.

## Daily use
```
/standup                  → draft today's async update
/plan-milestone M1        → (PO/TL) draft stories, create issues after approval
/build-story 42           → your assigned issue end to end, ends with a draft PR
/review-branch 57         → agent review of a teammate's PR before you review it
/ship-check staging 0.3.0 → go/no-go report before a release
```

## Known limits (be honest about them)
- Pattern-based guards can be bypassed by unusual command forms; they reduce risk, they don't remove it. That is why secrets never live in the repo, `main` is protected on GitHub, and deployments are done by a human.
- Agents can be confidently wrong. CI + code review + QA catch most issues; a senior human review and an external penetration test are still required before launch (see `docs/SECURITY.md`).
- Check the Claude Code docs after major updates — hook events and settings evolve.
