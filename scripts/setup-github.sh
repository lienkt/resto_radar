#!/usr/bin/env bash
# One-time GitHub setup for Resto Radar. Run by a HUMAN (PO or tech lead) with admin
# rights:  gh auth login  &&  ./scripts/setup-github.sh OWNER/REPO
# Safe to re-run. Agents must not run this script (it changes repository settings).
set -euo pipefail
REPO="${1:?usage: setup-github.sh OWNER/REPO}"

echo "→ Labels"
label() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force >/dev/null; }
label "type:story"  1d76db "User-facing or technical story"
label "type:bug"    d73a4a "Something is broken"
label "type:adr"    5319e7 "Architecture decision"
label "type:chore"  c5def5 "Maintenance"
for a in api workers radar web mobile infra harness; do label "area:$a" fbca04 "Area: $a"; done
label "mode:agent-heavy" 0e8a16 "Agents do most of the work; human reviews"
label "mode:human-led"   fef2c0 "Human designs/decides; agents assist"
label "mode:human-only"  b60205 "No agent work"
label "needs-security-review" b60205 "2 approvals incl. tech lead"
label "needs-po-decision"     d93f0b "Product owner must decide"
label "blocked"               000000 "Blocked by another issue or decision"
label "agent-built"           bfdadc "Most of the code was produced by agents"

echo "→ Milestones"
for m in "M0 Foundations" "M1 Places & search" "M2 Watch & notify" "M3 Radar collect" "M4 Radar score" "M5 Launch readiness"; do
  gh api "repos/$REPO/milestones" -f title="$m" >/dev/null 2>&1 || true
done

echo "→ Repository settings (squash merge only, delete merged branches)"
gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true >/dev/null

echo "→ Secret scanning + push protection (needs a public repo or GitHub Advanced Security)"
gh api -X PATCH "repos/$REPO" --input - >/dev/null <<'JSON' || echo "  (skipped — not available on this plan)"
{"security_and_analysis": {"secret_scanning": {"status": "enabled"},
 "secret_scanning_push_protection": {"status": "enabled"}}}
JSON

echo "→ Branch protection on main"
gh api -X PUT "repos/$REPO/branches/main/protection" --input - >/dev/null <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": [
    "Python (api)", "Python (workers)", "Web, mobile & packages",
    "Secret scan (gitleaks)", "Semgrep (OWASP rules)"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true,
    "dismiss_stale_reviews": true,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON

cat <<'TXT'
Done. Manual steps left:
  1. Create GitHub teams (team-backend, team-web, team-mobile, team-radar) or use
     individual @handles, then replace @PO / @TECH-LEAD / @team-* in .github/CODEOWNERS.
  2. Create a Project board with columns Backlog → Ready → In progress → In review → Done.
  3. Enable Dependabot alerts + security updates in Settings → Code security.
  4. For the 2-approval rule on critical areas, add a ruleset targeting those paths
     (Settings → Rules) or enforce it in review — see docs/TEAM.md §4.
TXT
