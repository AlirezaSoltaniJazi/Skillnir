#!/usr/bin/env bash
set -euo pipefail

# Validate Skillnir infrastructure conventions
# Usage: bash .data/skills/devopsEngineer/scripts/validate-infra.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
PASS=0; FAIL=0; WARN=0

pass_check() { ((PASS++)); echo "  ✅ $1"; }
fail_check() { ((FAIL++)); echo "  ❌ $1"; }
warn_check() { ((WARN++)); echo "  ⚠️  $1"; }

# --- GitHub Actions Workflows ---
echo "🔍 Checking GitHub Actions workflows..."

WORKFLOW_DIR="$PROJECT_ROOT/.github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
    for wf in "$WORKFLOW_DIR"/*.yml; do
        [ -f "$wf" ] || continue
        name=$(basename "$wf")

        # Check timeout-minutes is set
        if grep -q "timeout-minutes:" "$wf"; then
            pass_check "$name has timeout-minutes"
        else
            fail_check "$name missing timeout-minutes on jobs"
        fi

        # Check actions are pinned to versions (not @main/@latest/@master)
        if grep -E "uses:.*@(main|latest|master)" "$wf" > /dev/null 2>&1; then
            fail_check "$name has unpinned action versions (@main/@latest/@master)"
        else
            pass_check "$name actions are version-pinned"
        fi

        # Check for hardcoded secrets
        if grep -iE "(password|secret|token|api_key)\s*[:=]" "$wf" > /dev/null 2>&1; then
            fail_check "$name may contain hardcoded secrets"
        else
            pass_check "$name has no hardcoded secrets"
        fi
    done
else
    warn_check "No .github/workflows/ directory found"
fi

# --- Composite Actions ---
echo ""
echo "🔍 Checking composite actions..."

ACTION_DIR="$PROJECT_ROOT/.github/actions"
if [ -d "$ACTION_DIR" ]; then
    for action_dir in "$ACTION_DIR"/*/; do
        [ -d "$action_dir" ] || continue
        name=$(basename "$action_dir")

        if [ -f "$action_dir/action.yml" ]; then
            pass_check "Composite action '$name' has action.yml"
        else
            fail_check "Composite action '$name' missing action.yml"
        fi
    done
else
    warn_check "No .github/actions/ directory found"
fi

# --- Pre-commit Configuration ---
echo ""
echo "🔍 Checking pre-commit configuration..."

PRECOMMIT="$PROJECT_ROOT/.pre-commit-config.yaml"
if [ -f "$PRECOMMIT" ]; then
    pass_check ".pre-commit-config.yaml exists"

    # Check for pinned revisions
    if grep -E "rev:\s*(main|latest|master)" "$PRECOMMIT" > /dev/null 2>&1; then
        fail_check "Pre-commit hooks have unpinned revisions"
    else
        pass_check "Pre-commit hook revisions are pinned"
    fi

    # Check for bandit hook
    if grep -q "bandit" "$PRECOMMIT"; then
        pass_check "Bandit security hook is configured"
    else
        fail_check "Bandit security hook missing"
    fi

    # Check for safety hook
    if grep -q "safety" "$PRECOMMIT"; then
        pass_check "Safety CVE scanning hook is configured"
    else
        warn_check "Safety CVE scanning hook missing"
    fi
else
    fail_check ".pre-commit-config.yaml not found"
fi

# --- Pylint Configuration ---
echo ""
echo "🔍 Checking linter configuration..."

if [ -f "$PROJECT_ROOT/.pylintrc" ]; then
    pass_check ".pylintrc exists"
else
    fail_check ".pylintrc not found"
fi

# --- CI/Pre-commit Parity ---
echo ""
echo "🔍 Checking CI ↔ pre-commit parity..."

if [ -f "$WORKFLOW_DIR/check-style.yml" ] && [ -f "$PRECOMMIT" ]; then
    for tool in black autoflake pylint bandit; do
        ci_has=$(grep -c "$tool" "$WORKFLOW_DIR/check-style.yml" 2>/dev/null || echo 0)
        pc_has=$(grep -c "$tool" "$PRECOMMIT" 2>/dev/null || echo 0)

        if [ "$ci_has" -gt 0 ] && [ "$pc_has" -gt 0 ]; then
            pass_check "$tool present in both CI and pre-commit"
        elif [ "$ci_has" -gt 0 ] && [ "$pc_has" -eq 0 ]; then
            warn_check "$tool in CI but not in pre-commit"
        elif [ "$ci_has" -eq 0 ] && [ "$pc_has" -gt 0 ]; then
            warn_check "$tool in pre-commit but not in CI"
        fi
    done
fi

# --- Summary ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
