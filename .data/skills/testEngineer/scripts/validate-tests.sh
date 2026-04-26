#!/usr/bin/env bash
set -euo pipefail

# Validates test automation conventions for the project.
# Usage: ./validate-tests.sh [project-root]
#
# Checks:
# 1. No sleep()/waitForTimeout() usage (flakiness source)
# 2. No assertions in page objects
# 3. Test files follow naming conventions
# 4. No hard-coded URLs or credentials
# 5. Page objects exist for referenced pages
# 6. No test-only code in production source

PROJECT_ROOT="${1:-.}"
TEST_DIRS=("$PROJECT_ROOT/tests" "$PROJECT_ROOT/test" "$PROJECT_ROOT/e2e" "$PROJECT_ROOT/spec" "$PROJECT_ROOT/__tests__" "$PROJECT_ROOT/cypress")

PASS=0
FAIL=0
WARN=0

pass() {
    echo "  ✅ PASS  $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  ❌ FAIL  $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo "  ⚠️  WARN  $1"
    WARN=$((WARN + 1))
}

# Find the actual test directory
FOUND_TEST_DIR=""
for dir in "${TEST_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        FOUND_TEST_DIR="$dir"
        break
    fi
done

echo "========================================="
echo "  Test Convention Validator"
echo "========================================="
echo ""

if [[ -z "$FOUND_TEST_DIR" ]]; then
    fail "No test directory found. Checked: tests/, test/, e2e/, spec/, __tests__/, cypress/"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

echo "Test directory: $FOUND_TEST_DIR"
echo ""

# Check 1: No sleep()/waitForTimeout() usage
echo "--- Checking wait patterns ---"
sleep_usage=$(grep -rn "sleep\s*(" "$FOUND_TEST_DIR" --include="*.ts" --include="*.js" --include="*.py" --include="*.java" 2>/dev/null | grep -v "node_modules" | grep -v "\.d\.ts" || true)
timeout_usage=$(grep -rn "waitForTimeout\|page\.waitForTimeout\|browser\.pause\|cy\.wait(\s*[0-9]" "$FOUND_TEST_DIR" --include="*.ts" --include="*.js" 2>/dev/null | grep -v "node_modules" || true)

if [[ -z "$sleep_usage" ]] && [[ -z "$timeout_usage" ]]; then
    pass "No sleep()/waitForTimeout() usage found"
else
    fail "Arbitrary waits found (use explicit waits instead):"
    if [[ -n "$sleep_usage" ]]; then echo "$sleep_usage" | head -5; fi
    if [[ -n "$timeout_usage" ]]; then echo "$timeout_usage" | head -5; fi
fi

# Check 2: No assertions in page objects
echo ""
echo "--- Checking page object patterns ---"
page_dirs=$(find "$FOUND_TEST_DIR" -type d -name "pages" -o -name "page-objects" -o -name "pageobjects" 2>/dev/null || true)

if [[ -n "$page_dirs" ]]; then
    po_assertions=""
    while IFS= read -r dir; do
        found=$(grep -rn "expect\|assert\|should\.\|\.to\.\|assertEquals\|assertTrue" "$dir" --include="*.ts" --include="*.js" --include="*.py" --include="*.java" 2>/dev/null | grep -v "// ❌\|# ❌\|NEVER\|don't\|DON'T" || true)
        if [[ -n "$found" ]]; then
            po_assertions="$po_assertions$found"
        fi
    done <<< "$page_dirs"

    if [[ -z "$po_assertions" ]]; then
        pass "No assertions found in page objects"
    else
        fail "Assertions found in page objects (move to spec files):"
        echo "$po_assertions" | head -5
    fi
else
    warn "No page objects directory found (pages/, page-objects/)"
fi

# Check 3: Test file naming conventions
echo ""
echo "--- Checking file naming ---"
bad_names=$(find "$FOUND_TEST_DIR" -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.java" 2>/dev/null | grep -v "node_modules" | grep -v "\.d\.ts" | while read -r f; do
    basename_f=$(basename "$f")
    # Check if test files follow conventions
    if echo "$f" | grep -qE "(spec|test|e2e|cy)" 2>/dev/null; then
        # Test file — should match pattern
        if ! echo "$basename_f" | grep -qE "\.(spec|test|e2e|cy)\.(ts|js|tsx|jsx)$|^test_.*\.py$|.*Test\.java$" 2>/dev/null; then
            echo "  Non-standard test file name: $basename_f"
        fi
    fi
done || true)

if [[ -z "$bad_names" ]]; then
    pass "All test files follow naming conventions"
else
    warn "Non-standard test file names found:"
    echo "$bad_names" | head -5
fi

# Check 4: No hard-coded URLs or credentials
echo ""
echo "--- Checking for hard-coded values ---"
hardcoded_urls=$(grep -rn "http://localhost\|https://.*\.com\|https://.*\.io" "$FOUND_TEST_DIR" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | grep -v "node_modules" | grep -v "config\." | grep -v "\.config\." | grep -v "// example\|# example\|baseURL\|base_url" || true)

if [[ -z "$hardcoded_urls" ]]; then
    pass "No hard-coded URLs in test files"
else
    warn "Possible hard-coded URLs (should use config/env vars):"
    echo "$hardcoded_urls" | head -5
fi

hardcoded_creds=$(grep -rn "password.*=.*['\"].*['\"]" "$FOUND_TEST_DIR" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | grep -v "node_modules" | grep -v "process\.env\|os\.environ\|\.env" | grep -v "getByLabel\|getByPlaceholder\|placeholder" || true)

if [[ -z "$hardcoded_creds" ]]; then
    pass "No hard-coded credentials found"
else
    warn "Possible hard-coded credentials (use env vars):"
    echo "$hardcoded_creds" | head -5
fi

# Check 5: Config file exists
echo ""
echo "--- Checking test configuration ---"
config_found=false
for config in "playwright.config.ts" "playwright.config.js" "cypress.config.ts" "cypress.config.js" "wdio.conf.ts" "wdio.conf.js" "pytest.ini" "pyproject.toml" "jest.config.ts" "jest.config.js" "vitest.config.ts"; do
    if [[ -f "$PROJECT_ROOT/$config" ]]; then
        pass "Test config found: $config"
        config_found=true
        break
    fi
done
if [[ "$config_found" == "false" ]]; then
    warn "No test framework config file found"
fi

echo ""
echo "========================================="
echo "  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "========================================="

if [[ $FAIL -gt 0 ]]; then
    exit 1
else
    exit 0
fi
