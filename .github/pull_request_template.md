Closes #___

## What & why
<!-- 2–5 lines. Link ADRs if a decision was made. -->

## How to test
<!-- Commands / steps; screenshots for UI changes (web + mobile). -->

## Agent involvement
- Driven by: @___ · Agents used: ___
- What agents produced: ___
- What I verified by hand: ___
- Where I'm unsure / want reviewer focus: ___

<details><summary>Agent handoff (what changed · how to test · open questions)</summary>

</details>

## Checklist (definition of done — docs/CONVENTIONS.md)
- [ ] Acceptance criteria covered by automated tests; CI green incl. coverage and security scans
- [ ] API change → OpenAPI + `packages/api-client` updated; backward compatible or versioned
- [ ] DB change → reversible migration, expand/contract for destructive changes
- [ ] No secrets, no personal data in logs; new env vars added to `.env.example`
- [ ] i18n (FR/NL/EN) and accessibility for user-facing changes
- [ ] New dependency justified (purpose, maintenance, licence)
- [ ] Human approval from someone other than the agent driver (2 incl. tech lead for critical areas — docs/TEAM.md §4)
- [ ] code-reviewer: APPROVE · qa-engineer: PASS · compliance-reviewer (if in scope): no open blocker/major
- [ ] Docs updated (ARCHITECTURE / OPERATIONS / SECURITY / README) if behaviour or operations changed
