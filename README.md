# Resto Radar — Claude Code agent team kit (hardened, team mode)

Drop these files into an empty GitHub repo, do the one-time setup in `docs/HARNESS.md`,
have every team member read `docs/TEAM.md`, then run `claude` from the repo root and
follow `docs/KICKOFF.md`.

```
resto-radar/
├── CLAUDE.md                     # project memory: stack, rules, commands
├── .mcp.json                     # Playwright MCP (agents can open the running app)
├── .claude/
│   ├── settings.json             # permissions: allow / ask / deny + hook wiring
│   ├── hooks/                    # protect-files, guard-bash, format-and-scan, session-start
│   ├── skills/                   # /plan-milestone /build-story /review-branch /standup /ship-check
│   └── agents/                   # 11 agents
│       ├── product-manager.md · architect.md
│       ├── backend-engineer.md · data-ingestion-engineer.md · radar-engineer.md
│       ├── web-engineer.md · mobile-engineer.md · devops-engineer.md
│       └── code-reviewer.md · qa-engineer.md · compliance-reviewer.md
├── .github/                      # CI, security scans, Dependabot, per-area CODEOWNERS,
│                                 # issue templates (story/bug/ADR), PR template
├── scripts/setup-github.sh       # labels, milestones, branch protection (run by an admin)
├── .pre-commit-config.yaml       # format, lint, gitleaks, no commits to main, commit format
├── .env.example · .gitignore · .editorconfig
├── config/
│   ├── sources.brussels.yaml     # seed radar sources (to verify)
│   └── scoring.yaml              # relevance/value weights
└── docs/
    ├── SPEC.md                   # product spec, milestones, acceptance examples
    ├── ARCHITECTURE.md           # system design, data model, flows
    ├── TEAM.md                   # humans + agents: roles, issues, reviews, rituals
    ├── WORKFLOW.md               # how the agents work inside that process
    ├── CONVENTIONS.md            # coding standards + definition of done
    ├── SECURITY.md               # threat model, ASVS/MASVS checklist, launch requirements
    ├── OPERATIONS.md             # environments, alerts, backups, release/rollback, incidents
    ├── HARNESS.md                # the 9 control layers + setup
    ├── KICKOFF.md                # first sessions, step by step
    └── adr/
```

## You will need (added by you to `.env`, never by the agents)
- Anthropic API key (LLM features inside the app)
- Places provider key(s) chosen in ADR-002 (e.g. Google Places API and/or Foursquare)
- Expo account (push + builds), Sentry, an email provider for digests
