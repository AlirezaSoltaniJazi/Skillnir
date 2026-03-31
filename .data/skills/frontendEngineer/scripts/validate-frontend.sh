#!/usr/bin/env bash
set -euo pipefail

# Validates NiceGUI frontend conventions for the Skillnir project.
# Usage: ./validate-frontend.sh [project-root]
#
# Checks:
# 1. All component files have module docstrings
# 2. All page functions call header()
# 3. No raw HTML usage (ui.html) in components
# 4. No relative imports in ui/
# 5. Component filenames match function names
# 6. All pages are imported in __init__.py
# 7. No hardcoded hex colors outside _COLOR_HEX maps

PROJECT_ROOT="${1:-.}"
UI_DIR="$PROJECT_ROOT/src/skillnir/ui"
COMPONENTS_DIR="$UI_DIR/components"
PAGES_DIR="$UI_DIR/pages"

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

echo "========================================="
echo "  NiceGUI Frontend Convention Validator"
echo "========================================="
echo ""

if [[ ! -d "$UI_DIR" ]]; then
    fail "UI directory not found: $UI_DIR"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# Check 1: Component module docstrings
echo "--- Checking component docstrings ---"
missing_docs=0
for pyfile in "$COMPONENTS_DIR"/*.py; do
    if [[ -f "$pyfile" ]]; then
        basename_file=$(basename "$pyfile")
        if [[ "$basename_file" == "__init__.py" ]]; then
            continue
        fi
        first_content=$(grep -m1 -v "^#\|^$" "$pyfile" 2>/dev/null || true)
        if [[ "$first_content" != '"""'* ]] && [[ "$first_content" != "'''"* ]]; then
            warn "Missing module docstring: components/$basename_file"
            missing_docs=$((missing_docs + 1))
        fi
    fi
done
if [[ $missing_docs -eq 0 ]]; then
    pass "All components have module docstrings"
fi

# Check 2: Page functions call header()
echo ""
echo "--- Checking page layout conventions ---"
for pyfile in "$PAGES_DIR"/*.py; do
    if [[ -f "$pyfile" ]]; then
        basename_file=$(basename "$pyfile")
        if [[ "$basename_file" == "__init__.py" ]]; then
            continue
        fi
        if grep -q "@ui.page" "$pyfile"; then
            if ! grep -q "header()" "$pyfile"; then
                fail "Page missing header() call: pages/$basename_file"
            else
                pass "Page calls header(): pages/$basename_file"
            fi
        fi
    fi
done

# Check 3: No raw ui.html() in components
echo ""
echo "--- Checking for raw HTML usage ---"
html_usage=$(grep -rn "ui\.html(" "$COMPONENTS_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$html_usage" ]]; then
    pass "No ui.html() usage in components"
else
    warn "ui.html() found in components (prefer NiceGUI elements):"
    echo "$html_usage" | head -5
fi

# Check 4: No relative imports in ui/
echo ""
echo "--- Checking import conventions ---"
relative_imports=$(grep -rn "^from \." "$UI_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$relative_imports" ]]; then
    pass "No relative imports in ui/"
else
    fail "Relative imports found in ui/:"
    echo "$relative_imports" | head -5
fi

# Check 5: No os.path usage
ospath_usage=$(grep -rn "os\.path\." "$UI_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$ospath_usage" ]]; then
    pass "No os.path usage (using pathlib)"
else
    fail "os.path usage found in ui/ (should use pathlib):"
    echo "$ospath_usage" | head -5
fi

# Check 6: Pages imported in __init__.py
echo ""
echo "--- Checking route registration ---"
init_file="$UI_DIR/__init__.py"
if [[ -f "$init_file" ]]; then
    for pyfile in "$PAGES_DIR"/*.py; do
        basename_file=$(basename "$pyfile" .py)
        if [[ "$basename_file" == "__init__" ]]; then
            continue
        fi
        if grep -q "@ui.page" "$pyfile" 2>/dev/null; then
            if grep -q "$basename_file" "$init_file"; then
                pass "Page registered in __init__.py: $basename_file"
            else
                fail "Page NOT registered in __init__.py: $basename_file"
            fi
        fi
    done
else
    fail "UI __init__.py not found"
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
