---
name: standup
description: Draft the user's daily async stand-up (merged, in progress incl. agent work, blocked, needs review) from GitHub activity.
disable-model-invocation: true
---
Draft my daily stand-up. Use only read-only `gh` commands:
- `gh api user --jq .login`
- my PRs merged since the last working day: `gh pr list --author @me --state merged --search "merged:>=<date>"`
- my open PRs and their review status: `gh pr list --author @me --json number,title,isDraft,reviewDecision,statusCheckRollup`
- issues assigned to me: `gh issue list --assignee @me --state open --json number,title,labels`
- PRs waiting for my review: `gh pr list --search "review-requested:@me"`

Write 3–5 lines max:
**Done:** … · **Doing:** … (say which parts agents are running) · **Blocked:** … (and who can unblock) · **Reviews I owe:** …
Show it to me to copy; don't post it anywhere.
