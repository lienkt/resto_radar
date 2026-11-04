---
name: review-branch
description: Run the agent review gate (code review, QA, security/compliance) on the current branch, a branch name, or a teammate's PR number before human review.
argument-hint: "[branch name or PR number — defaults to current branch]"
disable-model-invocation: true
---
Review **$ARGUMENTS** (if empty: the current branch; if a number: that PR — use `gh pr diff` and `gh pr view`).

1. Get the diff against `main` and the linked issue's acceptance criteria.
2. In parallel: **code-reviewer** (correctness, maintainability, conventions) and **compliance-reviewer** (security, GDPR, data-source terms) on the diff.
3. **qa-engineer** runs the affected suites and checks the acceptance criteria.
4. Run lint, typecheck, tests and `pre-commit run --all-files` locally.
5. Report one table: severity · file:line · finding · fix. Verdict: READY FOR HUMAN REVIEW / CHANGES REQUIRED.
6. When reviewing a teammate's PR, show the report to me; only post it with `gh pr comment` (asks permission) if I say so. Never approve or merge a PR — approvals are human.
