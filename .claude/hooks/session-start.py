#!/usr/bin/env python3
"""SessionStart hook: give Claude a short, current briefing (stdout is added to context)."""
import glob
import os
import re
import subprocess

project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def sh(*args):
    try:
        r = subprocess.run(args, cwd=project, capture_output=True, text=True, timeout=4)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


lines = ["## Session briefing (auto-generated)"]
branch = sh("git", "branch", "--show-current")
if branch:
    dirty = len([l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()])
    lines.append(f"- Branch: {branch} · uncommitted files: {dirty}")
    if branch in ("main", "master"):
        lines.append("- You are on main: create a feature branch or worktree before changing code.")

import shutil
if shutil.which("gh"):
    me = sh("gh", "api", "user", "--jq", ".login")
    if me and re.fullmatch(r"[A-Za-z0-9-]{1,39}", me):
        issues = sh("gh", "issue", "list", "--assignee", "@me", "--state", "open", "--limit", "5",
                    "--json", "number,title", "--jq", ".[] | \"#\\(.number) \\(.title)\"")
        reviews = sh("gh", "pr", "list", "--search", "review-requested:@me", "--json", "number", "--jq", "length")
        lines.append(f"- GitHub user: {me} (agents work only on issues assigned to this user)")
        lines.append("- My open issues: " + ("; ".join(issues.splitlines()) if issues else "none"))
        if reviews and reviews != "0":
            lines.append(f"- PRs waiting for my review: {reviews} — human review comes before new agent work")
    else:
        lines.append("- GitHub CLI not signed in: run `gh auth login` so /build-story can check issue assignment.")

handoffs = sorted(glob.glob(os.path.join(project, "docs", "handoffs", "*.md")))[-3:]
if handoffs:
    lines.append("- Latest handoffs: " + ", ".join(os.path.basename(h) for h in handoffs))

lines.append("- Rules: follow CLAUDE.md and docs/CONVENTIONS.md; never touch secrets; every change ends with tests + agent gate + human review (docs/TEAM.md).")
print("\n".join(lines))
