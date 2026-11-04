---
name: plan-milestone
description: Plan a Resto Radar milestone as GitHub issues — stories with acceptance criteria, design/ADR needs and a work plan — then stop for the product owner's approval.
argument-hint: "<milestone, e.g. M2>"
disable-model-invocation: true
---
Plan milestone **$ARGUMENTS**. Read `CLAUDE.md`, `docs/TEAM.md`, `docs/SPEC.md` (this milestone), `docs/ARCHITECTURE.md`.

1. List what already exists: `gh issue list --milestone "$ARGUMENTS" --state all --limit 200` and open ADR issues (`gh issue list --label type:adr`).
2. Use the **product-manager** agent to draft the missing stories in `.plan/$ARGUMENTS.md` (gitignored scratch file) using the fields of `.github/ISSUE_TEMPLATE/story.yml`: user story, Given/When/Then acceptance criteria, area, mode (agent-heavy / human-led / human-only), size, dependencies, review needs.
3. Use the **architect** agent to add the design work needed (tables, OpenAPI operations, ADRs) as separate contract-first stories that block the feature stories.
4. Propose an order and which stories can run in parallel without touching the same files or migrations.
5. **Stop.** Show me the draft, cost drivers (paid APIs, LLM usage) and open questions (they become `needs-po-decision` issues).
6. Only after I reply "approved": create each issue with `gh issue create --title … --body-file … --label "type:story,area:…,mode:…" --milestone "$ARGUMENTS"` (each create asks for permission). Do **not** assign people — humans pick issues in planning.
