#!/usr/bin/env bash
set -euo pipefail

# Read-only preflight for the jira skill: confirms the Atlassian CLI is installed
# and authenticated to a Jira site. Makes NO changes to Jira.

fail=0

if command -v acli >/dev/null 2>&1; then
    echo "✅ acli found: $(command -v acli)"
else
    echo "❌ acli not on PATH — install the Atlassian CLI, then run 'acli jira auth login'"
    exit 1
fi

if acli jira auth status >/tmp/jira-auth.$$ 2>&1; then
    echo "✅ Jira authenticated"
    grep -i 'Site:' /tmp/jira-auth.$$ || true
else
    echo "⚠️  Not authenticated — run 'acli jira auth login' before using the skill"
    fail=1
fi
rm -f /tmp/jira-auth.$$

if [ "$fail" -ne 0 ]; then
    exit 1
fi
echo "✅ jira skill preflight passed"
