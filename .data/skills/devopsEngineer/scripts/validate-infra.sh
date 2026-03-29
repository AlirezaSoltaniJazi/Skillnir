#!/usr/bin/env bash
set -euo pipefail

# Validate infrastructure conventions for the Skillnir project
# Usage: ./validate-infra.sh [project-root]

PROJECT_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
WORKFLOWS_DIR="$PROJECT_ROOT/.github/workflows"
ACTIONS_DIR="$PROJECT_ROOT/.github/actions"
PRECOMMIT="$PROJECT_ROOT/.pre-commit-config.yaml"

PASS=0
FAIL=0
WARN=0

check() {
    local description="$1"
    local result="$2"
    if [[ "$result" == "pass" ]]; then
        echo "  PASS  $description"
        ((PASS++))
    elif [[ "$result" == "warn" ]]; then
        echo "  WARN  $description"
        ((WARN++))
    else
        echo "  FAIL  $description"
        ((FAIL++))
    fi
}

echo "=== Skillnir Infrastructure Convention Validator ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# --- File Structure ---
echo "--- File Structure ---"

check ".github/workflows/ directory exists" \
    "$([[ -d "$WORKFLOWS_DIR" ]] && echo pass || echo fail)"

check ".github/actions/ directory exists" \
    "$([[ -d "$ACTIONS_DIR" ]] && echo pass || echo fail)"

check ".pre-commit-config.yaml exists" \
    "$([[ -f "$PRECOMMIT" ]] && echo pass || echo fail)"

check "pyproject.toml exists" \
    "$([[ -f "$PROJECT_ROOT/pyproject.toml" ]] && echo pass || echo fail)"

check ".gitignore exists" \
    "$([[ -f "$PROJECT_ROOT/.gitignore" ]] && echo pass || echo fail)"

check "PR template exists" \
    "$([[ -f "$PROJECT_ROOT/.github/pull_request_template.md" ]] && echo pass || echo fail)"

# --- Workflow Conventions ---
echo ""
echo "--- Workflow Conventions ---"

for workflow in "$WORKFLOWS_DIR"/*.yml; do
    if [[ -f "$workflow" ]]; then
        basename=$(basename "$workflow")

        # Check for timeout-minutes
        HAS_TIMEOUT=$(grep -c "timeout-minutes" "$workflow" || true)
        check "$basename has timeout-minutes" \
            "$([[ "$HAS_TIMEOUT" -gt 0 ]] && echo pass || echo fail)"

        # Check for pinned action versions (uses: with @)
        UNPINNED=$(grep "uses:" "$workflow" | grep -v "@" | grep -v "\./" || true)
        check "$basename has pinned action versions" \
            "$([[ -z "$UNPINNED" ]] && echo pass || echo fail)"

        # Check for checkout before local actions
        HAS_LOCAL=$(grep -c "uses: \./" "$workflow" || true)
        if [[ "$HAS_LOCAL" -gt 0 ]]; then
            HAS_CHECKOUT=$(grep -c "actions/checkout" "$workflow" || true)
            check "$basename has checkout before local actions" \
                "$([[ "$HAS_CHECKOUT" -gt 0 ]] && echo pass || echo fail)"
        fi
    fi
done

# --- Pre-commit Conventions ---
echo ""
echo "--- Pre-commit Conventions ---"

if [[ -f "$PRECOMMIT" ]]; then
    # Check that code quality hooks exclude .data/
    for hook in black pylint autoflake; do
        HOOK_SECTION=$(grep -A5 "id: $hook" "$PRECOMMIT" 2>/dev/null || true)
        if [[ -n "$HOOK_SECTION" ]]; then
            HAS_EXCLUDE=$(echo "$HOOK_SECTION" | grep -c "exclude.*data" || true)
            check "$hook hook excludes .data/" \
                "$([[ "$HAS_EXCLUDE" -gt 0 ]] && echo pass || echo warn)"
        fi
    done

    # Check that all repos have pinned rev
    UNPINNED_HOOKS=$(grep -B2 "hooks:" "$PRECOMMIT" | grep "repo:" | grep -v "local" || true)
    MISSING_REV=$(grep -c "rev:" "$PRECOMMIT" || true)
    REPO_COUNT=$(grep -c "repo:" "$PRECOMMIT" | grep -v "local" || true)
    check "All hook repos have pinned rev" \
        "$([[ "$MISSING_REV" -ge "$REPO_COUNT" ]] && echo pass || echo fail)"
fi

# --- Security Conventions ---
echo ""
echo "--- Security Conventions ---"

# Check .gitignore has critical exclusions
if [[ -f "$PROJECT_ROOT/.gitignore" ]]; then
    check ".gitignore excludes .env" \
        "$(grep -qc '\.env' "$PROJECT_ROOT/.gitignore" && echo pass || echo fail)"

    check ".gitignore excludes .pypirc" \
        "$(grep -qc '\.pypirc' "$PROJECT_ROOT/.gitignore" && echo pass || echo fail)"
fi

# Check for hardcoded secrets in workflows
SECRETS_IN_WORKFLOWS=$(grep -rn "password\|token\|secret\|api_key" "$WORKFLOWS_DIR" --include="*.yml" 2>/dev/null | grep -v "secrets\." | grep -v "GITHUB_TOKEN" | grep -v "storage_secret" || true)
check "No hardcoded secrets in workflows" \
    "$([[ -z "$SECRETS_IN_WORKFLOWS" ]] && echo pass || echo fail)"

# --- Build System ---
echo ""
echo "--- Build System ---"

if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    check "pyproject.toml has requires-python" \
        "$(grep -qc 'requires-python' "$PROJECT_ROOT/pyproject.toml" && echo pass || echo fail)"

    check "pyproject.toml has project.scripts entry" \
        "$(grep -qc '\[project.scripts\]' "$PROJECT_ROOT/pyproject.toml" && echo pass || echo fail)"

    check "pyproject.toml uses hatchling build" \
        "$(grep -qc 'hatchling' "$PROJECT_ROOT/pyproject.toml" && echo pass || echo fail)"
fi

# Check for pip/poetry usage (should be uv only)
PIP_USAGE=$(grep -rn "pip install" "$PROJECT_ROOT" --include="*.md" 2>/dev/null | grep -v "pip install -e" | grep -v node_modules || true)
check "No raw pip install in docs (use uv)" \
    "$([[ -z "$PIP_USAGE" ]] && echo pass || echo warn)"

echo ""
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
exit $FAIL
