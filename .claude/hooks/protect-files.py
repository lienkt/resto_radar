#!/usr/bin/env python3
"""PreToolUse hook for Read/Edit/Write: protect secrets and the guardrails themselves.

- Secrets (.env, keys, certificates, secrets/ folders): always denied.
- Guardrail files (.claude/settings*.json, .claude/hooks/, CODEOWNERS): editing needs
  the human's approval, so an agent can never silently weaken its own safety rules.
- CI workflows: editing needs approval.
"""
import json
import re
import sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
path = (data.get("tool_input", {}) or {}).get("file_path", "") or ""
path = path.replace("\\", "/")
name = path.rsplit("/", 1)[-1]

SECRET_NAME = re.compile(r"^\.env(\..+)?$|\.(pem|key|p12|pfx|keystore|jks)$|^id_(rsa|ed25519|ecdsa)$|^credentials\.json$|^service-account.*\.json$")
SAFE_NAME = re.compile(r"^\.env\.(example|sample|template)$")


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


if not path:
    sys.exit(0)

if (SECRET_NAME.search(name) and not SAFE_NAME.match(name)) or "/secrets/" in path:
    # Exit code 2 = block; stderr is shown to Claude.
    print(f"Blocked: {path} may contain secrets. Agents never read or write secrets; "
          "ask the product owner to set the value. Use .env.example for documentation.",
          file=sys.stderr)
    sys.exit(2)

if tool in ("Edit", "Write", "MultiEdit"):
    if re.search(r"/\.claude/(settings(\.local)?\.json|hooks/)", path) or path.endswith("/.github/CODEOWNERS"):
        decide("ask", "This file is part of the project's safety guardrails. A human must approve changes.")
    if "/.github/workflows/" in path:
        decide("ask", "CI/CD workflow change: a human must approve changes to the pipeline.")

sys.exit(0)
