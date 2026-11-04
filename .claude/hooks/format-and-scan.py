#!/usr/bin/env python3
"""PostToolUse hook for Edit/Write: auto-format the changed file and scan it for secrets.

Formatting is best-effort (skipped silently if the formatter is not installed yet).
A detected secret makes the hook exit 2 so Claude sees the warning and must remove it.
"""
import json
import os
import re
import shutil
import subprocess
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input", {}) or {}).get("file_path", "") or ""
if not path or not os.path.isfile(path):
    sys.exit(0)

project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
ext = os.path.splitext(path)[1].lower()


def run(cmd):
    try:
        subprocess.run(cmd, cwd=project, capture_output=True, timeout=45, check=False)
    except Exception:
        pass


if ext == ".py":
    if shutil.which("uv"):
        run(["uv", "run", "--quiet", "ruff", "format", path])
        run(["uv", "run", "--quiet", "ruff", "check", "--fix", "--quiet", path])
    elif shutil.which("ruff"):
        run(["ruff", "format", path])
        run(["ruff", "check", "--fix", "--quiet", path])
elif ext in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".css", ".md", ".yaml", ".yml"}:
    local = os.path.join(project, "node_modules", ".bin", "prettier")
    if os.path.exists(local):
        run([local, "--write", "--log-level", "silent", path])

SECRET_PATTERNS = [
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,}", "GitHub token"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack token"),
    (r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----", "private key"),
    (r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][A-Za-z0-9_\-/+]{16,}[\"']", "hard-coded credential"),
]

if os.path.basename(path).startswith(".env.") or "/tests/fixtures/" in path.replace("\\", "/"):
    sys.exit(0)

try:
    text = open(path, encoding="utf-8", errors="ignore").read()
except Exception:
    sys.exit(0)

hits = [label for pattern, label in SECRET_PATTERNS if re.search(pattern, text)]
if hits:
    print(f"Possible secret in {path}: {', '.join(sorted(set(hits)))}. Remove it now and read "
          "the value from an environment variable (document the name in .env.example).",
          file=sys.stderr)
    sys.exit(2)
sys.exit(0)
