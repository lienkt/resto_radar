#!/usr/bin/env python3
"""PreToolUse hook for Bash: block destructive, exfiltrating or deploying commands.

Permission rules in settings.json are the first layer; this hook catches variations
(pipes, chained commands, flags in other positions) that simple patterns miss.
"""
import json
import re
import sys

data = json.load(sys.stdin)
cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
c = " ".join(cmd.split())  # normalise whitespace

DENY = [
    (r"\brm\s+-[a-z]*r[a-z]*f?[a-z]*\s+(/|~|\$HOME|\.\.|\*)(\s|$)", "recursive delete of a root, home, parent or wildcard path"),
    (r"\bgit\s+push\b.*(\s--force(-with-lease)?\b|\s-f\b)", "force push"),
    (r"\bgit\s+push\b.*\b(main|master|production)\b", "pushing directly to a protected branch — open a PR instead"),
    (r"\bgit\s+commit\b.*--no-verify|\bgit\s+push\b.*--no-verify", "skipping pre-commit/pre-push checks"),
    (r"\bgit\s+reset\s+--hard\s+(origin/)?(main|master)\b", "hard reset of the main branch"),
    (r"\bgit\s+clean\s+-[a-z]*f[a-z]*d", "git clean of untracked files"),
    (r"(curl|wget)[^|;&]*\|\s*(ba|z)?sh\b", "piping a download into a shell"),
    (r"\b(cat|less|more|head|tail|bat|grep|sed|awk|cp|mv|base64|xxd)\b[^|;&]*\.env(\s|$|\")(?!\.example)", "reading or copying a secrets file"),
    (r"(^|[;&|]\s*)(printenv|env)(\s*$|\s*[|>])", "dumping environment variables (may contain secrets)"),
    (r"\bchmod\s+(-R\s+)?777\b", "world-writable permissions"),
    (r"\bdocker\s+(system|volume)\s+prune\b|\bdocker\s+compose\s+down\b.*\s-v\b", "deleting docker volumes/data"),
    (r"\b(drop\s+(database|schema)|truncate\s+table)\b", "destructive SQL"),
    (r"\balembic\s+downgrade\s+base\b", "downgrading all migrations"),
    (r"\b(eas\s+submit|eas\s+update\b.*--branch\s+production|vercel\s+(--prod|deploy)|fly\s+deploy|terraform\s+(apply|destroy)|kubectl\s+(apply|delete))\b", "deploying or changing infrastructure — deployments are done by a human"),
    (r"\bnpm\s+publish\b|\bpnpm\s+publish\b|\btwine\s+upload\b", "publishing a package"),
    (r"\bssh\b|\bscp\b", "remote shell access"),
    (r"\bgh\s+pr\s+(merge|review)\b", "merging or approving PRs — approvals and merges are human"),
    (r"\bgh\s+(secret|variable|auth|release|ruleset)\b|\bgh\s+repo\s+(delete|edit|archive|rename)\b|\bgh\s+workflow\s+(run|enable|disable)\b|\bgh\s+issue\s+(delete|transfer)\b", "changing GitHub secrets, settings, releases or workflows"),
    (r"\bgh\s+api\b.*(-X|--method)\s*(PUT|PATCH|DELETE)|\bgh\s+api\b.*/(protection|merges|merge|collaborators|hooks|keys|rulesets)\b", "write calls to the GitHub API (repo settings, branch protection, merges)"),
    (r"setup-github\.sh", "repository setup script — run by a human admin only"),
]

for pattern, reason in DENY:
    if re.search(pattern, c, flags=re.IGNORECASE):
        print(f"Blocked by project guardrail ({reason}). If this is really needed, explain why "
              "and ask the product owner to run it.", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
