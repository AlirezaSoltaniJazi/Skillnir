#!/usr/bin/env bash
set -euo pipefail

# Read-only preflight for the gitlab skill: confirms the GitLab CLI is installed
# and authenticated. Makes NO changes to any repo or MR.

if command -v glab >/dev/null 2>&1; then
    echo "✅ glab found: $(command -v glab) ($(glab --version 2>/dev/null | head -1))"
else
    echo "❌ glab not on PATH — install the GitLab CLI, then run 'glab auth login'"
    exit 1
fi

if glab auth status >/tmp/glab-auth.$$ 2>&1; then
    echo "✅ GitLab authenticated"
    grep -iE 'logged in|token|host' /tmp/glab-auth.$$ || true
    rm -f /tmp/glab-auth.$$
else
    rm -f /tmp/glab-auth.$$
    echo "⚠️  Not authenticated — run 'glab auth login' before using the skill"
    exit 1
fi
echo "✅ gitlab skill preflight passed"
