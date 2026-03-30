#!/usr/bin/env bash
set -euo pipefail

# Validates Python backend conventions for the Skillnir project.
# Usage: ./validate-backend.sh [project-root]
#
# Checks:
# 1. No relative imports in src/skillnir/
# 2. No os.path usage (should use pathlib)
# 3. No Optional[] from typing (should use X | None)
# 4. No Dict/List/Tuple from typing (should use lowercase builtins)
# 5. All .py files have module docstrings
# 6. No setup.py or requirements.txt
# 7. pyproject.toml exists with required sections

PROJECT_ROOT="${1:-.}"
SRC_DIR="$PROJECT_ROOT/src/skillnir"

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
echo "  Python Backend Convention Validator"
echo "========================================="
echo ""

if [[ ! -d "$SRC_DIR" ]]; then
    fail "Source directory not found: $SRC_DIR"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# Check 1: No relative imports
echo "--- Checking import conventions ---"
relative_imports=$(grep -rn "^from \." "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$relative_imports" ]]; then
    pass "No relative imports found"
else
    fail "Relative imports found:"
    echo "$relative_imports" | head -5
fi

# Check 2: No os.path usage
ospath_usage=$(grep -rn "os\.path\." "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$ospath_usage" ]]; then
    pass "No os.path usage found (using pathlib)"
else
    fail "os.path usage found (should use pathlib):"
    echo "$ospath_usage" | head -5
fi

# Check 3: No Optional[] from typing
optional_usage=$(grep -rn "Optional\[" "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$optional_usage" ]]; then
    pass "No Optional[] usage (using X | None syntax)"
else
    warn "Optional[] found (should use X | None):"
    echo "$optional_usage" | head -5
fi

# Check 4: No Dict/List/Tuple from typing
typing_generics=$(grep -rn "from typing import.*\(Dict\|List\|Tuple\)" "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$typing_generics" ]]; then
    pass "No deprecated typing generics (Dict/List/Tuple)"
else
    warn "Deprecated typing generics found:"
    echo "$typing_generics" | head -5
fi

# Check 5: Module docstrings
echo ""
echo "--- Checking documentation ---"
missing_docstrings=0
for pyfile in "$SRC_DIR"/*.py; do
    if [[ -f "$pyfile" ]]; then
        # Check if file starts with docstring (after optional encoding/shebang)
        first_content=$(grep -m1 -v "^#\|^$" "$pyfile" 2>/dev/null || true)
        if [[ "$first_content" != '"""'* ]] && [[ "$first_content" != "'''"* ]]; then
            basename_file=$(basename "$pyfile")
            if [[ "$basename_file" != "__init__.py" ]]; then
                warn "Missing module docstring: $basename_file"
                missing_docstrings=$((missing_docstrings + 1))
            fi
        fi
    fi
done
if [[ $missing_docstrings -eq 0 ]]; then
    pass "All modules have docstrings"
fi

# Check 6: No legacy config files
echo ""
echo "--- Checking project structure ---"
if [[ -f "$PROJECT_ROOT/setup.py" ]]; then
    fail "setup.py found (should use pyproject.toml only)"
else
    pass "No setup.py (using pyproject.toml)"
fi

if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
    warn "requirements.txt found (project uses uv + pyproject.toml)"
else
    pass "No requirements.txt (using uv + pyproject.toml)"
fi

# Check 7: pyproject.toml exists
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    pass "pyproject.toml exists"

    if grep -q "\[build-system\]" "$PROJECT_ROOT/pyproject.toml"; then
        pass "pyproject.toml has [build-system]"
    else
        fail "pyproject.toml missing [build-system]"
    fi

    if grep -q "\[project\]" "$PROJECT_ROOT/pyproject.toml"; then
        pass "pyproject.toml has [project]"
    else
        fail "pyproject.toml missing [project]"
    fi
else
    fail "pyproject.toml not found"
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
