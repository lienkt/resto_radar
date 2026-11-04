---
name: build-story
description: Build one GitHub issue assigned to the current user end to end — isolated branch, implementation by the right agent, agent review gate, draft PR with an agent-involvement section.
argument-hint: "<issue number, e.g. 42>"
disable-model-invocation: true
---
Build issue **#$ARGUMENTS**. You are the orchestrator for the human running this session; delegate, don't implement large changes yourself.

1. `gh issue view $ARGUMENTS --json number,title,body,labels,assignees,milestone,state` and `gh api user --jq .login`.
   - Stop if the issue is not open, not assigned to this user, labelled `mode:human-only`, `blocked` or `needs-po-decision`, or lacks acceptance criteria.
   - Stop if a contract/ADR it depends on is not merged yet; say which.
   - `mode:human-led`: agree the approach with the human before delegating any code.
2. Check for collisions: `gh pr list --search "#$ARGUMENTS"` and open PRs touching the same migration folder. Report conflicts before starting.
3. Delegate to the right engineering agent(s) by `area:*` label. Each prompt includes: issue number, acceptance criteria, files/areas allowed, contract to follow, definition of done (`docs/CONVENTIONS.md`). Branch: `feat/$ARGUMENTS-<slug>` (or `fix/…` for bugs), in a worktree.
4. Agent gate: **code-reviewer** → fix blocker/major via the owner agent; **qa-engineer** → PASS required; **compliance-reviewer** if labels/areas include auth, crawling, personal data, LLM, infra, harness or `needs-security-review`.
5. Ask the human to verify the result by hand (run it, read the risky parts). Help them fill in "What I verified by hand".
6. Push the branch and open a **draft** PR with `gh pr create --draft` using `.github/pull_request_template.md`: `Closes #$ARGUMENTS`, the agent handoff in the details block, label `agent-built` when most code came from agents. The human marks it ready and requests reviewers; never merge.
7. Comment on the issue with a 2-line status and the PR link.
