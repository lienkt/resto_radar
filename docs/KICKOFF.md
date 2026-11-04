# Kickoff — first sessions with the agent team

Do the one-time setup in `docs/HARNESS.md` first (tools, `./scripts/setup-github.sh`,
CODEOWNERS, `pre-commit install`). Every team member reads `docs/TEAM.md`. Then run
`claude` in the repo root.

## 1. Plan M0
```
/plan-milestone M0
```
(PO + TL.) Review the stories and open questions, answer them, then say "approved" — the
issues are created in GitHub. In the planning meeting, each person assigns themselves issues.

## 2. Foundations
```
Use the architect agent to write ADR-001 (auth), ADR-002 (places providers, with current
pricing, terms and caching/attribution limits) and ADR-003 (queue), then scaffold the
monorepo, docker-compose and .env.example exactly as in CLAUDE.md. Use the devops-engineer
agent in parallel to turn .github/workflows/ci.yml into a working pipeline for that
skeleton. Then run /review-branch and open one draft PR for me (link the M0 scaffold issue).
```

## 3. Build the M0 stories
```
/build-story 1
```
Each person runs this on their own assigned issues. Each ends with a draft PR; a teammate
reviews it (they can run `/review-branch <PR#>` first), then the author squash-merges.

## 4. Next milestones
`/plan-milestone M1` → approve → people pick issues → `/build-story <#>` → review → merge → … For the radar milestones start with:
```
Use the radar-engineer agent to verify every source in config/sources.brussels.yaml
(feeds, APIs, terms, robots.txt) and report which can be enabled.
```

## 5. Every day
```
/standup
```
Post the draft in the team channel.

## 6. Releases
```
/ship-check staging 0.1.0
```
You deploy when the report says GO.
