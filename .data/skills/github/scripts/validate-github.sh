#!/usr/bin/env bash
set -euo pipefail

# Read-only preflight for the github skill: confirms the GitHub CLI is installed
# and authenticated. Makes NO changes to any repo or PR.

if command -v gh >/dev/null 2>&1; then
    echo "✅ gh found: $(command -v gh) ($(gh --version | head -1))"
else
    echo "❌ gh not on PATH — install the GitHub CLI, then run 'gh auth login'"
    exit 1
fi

if gh auth status >/tmp/gh-auth.$$ 2>&1; then
    echo "✅ GitHub authenticated"
    grep -iE 'account|scopes' /tmp/gh-auth.$$ || true
    if grep -q "'project'" /tmp/gh-auth.$$; then
        echo "ℹ️  'project' scope present"
    else
        echo "⚠️  no 'project' scope — do not use 'gh pr create -p' (add PR to a Project)"
    fi
    rm -f /tmp/gh-auth.$$
else
    rm -f /tmp/gh-auth.$$
    echo "⚠️  Not authenticated — run 'gh auth login' before using the skill"
    exit 1
fi
echo "✅ github skill preflight passed"
