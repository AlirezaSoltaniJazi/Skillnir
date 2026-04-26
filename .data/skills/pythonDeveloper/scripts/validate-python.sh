#!/usr/bin/env bash
set -euo pipefail

# Validates Python coding conventions for a generic Python project.
# Usage: ./validate-python.sh [project-root] [src-package-name]
#
# Examples:
#   ./validate-python.sh .                          # Auto-detect src package
#   ./validate-python.sh /path/to/project mypackage # Explicit package name
#
# Checks:
# 1. No relative imports in source package
# 2. No os.path usage (should use pathlib)
# 3. No Optional[] from typing (should use X | None)
# 4. No Dict/List/Tuple from typing (should use lowercase builtins)
# 5. All .py files have module docstrings
# 6. No print() in source (should use logging)
# 7. No bare except clauses
# 8. No string-formatted SQL
# 9. pyproject.toml exists with required sections
# 10. No legacy config files (setup.py, requirements.txt)

PROJECT_ROOT="${1:-.}"

# Auto-detect source package
if [[ -n "${2:-}" ]]; then
    PACKAGE_NAME="$2"
elif [[ -d "$PROJECT_ROOT/src" ]]; then
    # Find first directory under src/ that contains __init__.py
    PACKAGE_NAME=$(find "$PROJECT_ROOT/src" -maxdepth 2 -name "__init__.py" -printf '%h\n' 2>/dev/null | head -1 | xargs -r basename)
else
    PACKAGE_NAME=""
fi

# Determine source directory
if [[ -n "$PACKAGE_NAME" ]] && [[ -d "$PROJECT_ROOT/src/$PACKAGE_NAME" ]]; then
    SRC_DIR="$PROJECT_ROOT/src/$PACKAGE_NAME"
elif [[ -n "$PACKAGE_NAME" ]] && [[ -d "$PROJECT_ROOT/$PACKAGE_NAME" ]]; then
    SRC_DIR="$PROJECT_ROOT/$PACKAGE_NAME"
else
    SRC_DIR="$PROJECT_ROOT/src"
fi

PASS=0
FAIL=0
WARN=0

pass_check() {
    echo "  ✅ PASS  $1"
    PASS=$((PASS + 1))
}

fail_check() {
    echo "  ❌ FAIL  $1"
    FAIL=$((FAIL + 1))
}

warn_check() {
    echo "  ⚠️  WARN  $1"
    WARN=$((WARN + 1))
}

echo "========================================="
echo "  Python Convention Validator"
echo "========================================="
echo "  Project: $PROJECT_ROOT"
echo "  Source:  $SRC_DIR"
echo ""

if [[ ! -d "$SRC_DIR" ]]; then
    fail_check "Source directory not found: $SRC_DIR"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# --- Import Conventions ---
echo "--- Checking import conventions ---"

# Check 1: No relative imports
relative_imports=$(grep -rn "^from \." "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$relative_imports" ]]; then
    pass_check "No relative imports found"
else
    fail_check "Relative imports found:"
    echo "$relative_imports" | head -5
fi

# Check 2: No os.path usage
ospath_usage=$(grep -rn "os\.path\." "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$ospath_usage" ]]; then
    pass_check "No os.path usage found (using pathlib)"
else
    fail_check "os.path usage found (should use pathlib):"
    echo "$ospath_usage" | head -5
fi

# Check 3: No Optional[] from typing
optional_usage=$(grep -rn "Optional\[" "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$optional_usage" ]]; then
    pass_check "No Optional[] usage (using X | None syntax)"
else
    warn_check "Optional[] found (should use X | None):"
    echo "$optional_usage" | head -5
fi

# Check 4: No Dict/List/Tuple from typing
typing_generics=$(grep -rn "from typing import.*\(Dict\|List\|Tuple\|Set\)" "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$typing_generics" ]]; then
    pass_check "No deprecated typing generics (Dict/List/Tuple/Set)"
else
    warn_check "Deprecated typing generics found:"
    echo "$typing_generics" | head -5
fi

# --- Code Quality ---
echo ""
echo "--- Checking code quality ---"

# Check 5: Module docstrings
missing_docstrings=0
while IFS= read -r pyfile; do
    if [[ -f "$pyfile" ]]; then
        first_content=$(grep -m1 -v "^#\|^$" "$pyfile" 2>/dev/null || true)
        if [[ "$first_content" != '"""'* ]] && [[ "$first_content" != "'''"* ]]; then
            basename_file=$(basename "$pyfile")
            if [[ "$basename_file" != "__init__.py" ]]; then
                warn_check "Missing module docstring: $pyfile"
                missing_docstrings=$((missing_docstrings + 1))
            fi
        fi
    fi
done < <(find "$SRC_DIR" -name "*.py" -not -path "*/__pycache__/*" 2>/dev/null)
if [[ $missing_docstrings -eq 0 ]]; then
    pass_check "All modules have docstrings"
fi

# Check 6: No print() in source (should use logging)
print_usage=$(grep -rn "^\s*print(" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v "# noqa" | grep -v "__main__" || true)
if [[ -z "$print_usage" ]]; then
    pass_check "No print() in source (using logging)"
else
    warn_check "print() found (should use logging module):"
    echo "$print_usage" | head -5
fi

# Check 7: No bare except clauses
bare_except=$(grep -rn "except:" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v "# noqa" || true)
if [[ -z "$bare_except" ]]; then
    pass_check "No bare except clauses"
else
    fail_check "Bare except clauses found (should catch specific exceptions):"
    echo "$bare_except" | head -5
fi

# Check 8: No string-formatted SQL (basic check)
sql_format=$(grep -rn "f['\"].*SELECT\|f['\"].*INSERT\|f['\"].*UPDATE\|f['\"].*DELETE\|\.format.*SELECT\|\.format.*INSERT" "$SRC_DIR" --include="*.py" 2>/dev/null || true)
if [[ -z "$sql_format" ]]; then
    pass_check "No string-formatted SQL detected"
else
    fail_check "Possible string-formatted SQL (use parameterized queries):"
    echo "$sql_format" | head -5
fi

# --- Project Structure ---
echo ""
echo "--- Checking project structure ---"

# Check 9: pyproject.toml exists
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    pass_check "pyproject.toml exists"

    if grep -q "\[build-system\]" "$PROJECT_ROOT/pyproject.toml"; then
        pass_check "pyproject.toml has [build-system]"
    else
        warn_check "pyproject.toml missing [build-system]"
    fi

    if grep -q "\[project\]" "$PROJECT_ROOT/pyproject.toml"; then
        pass_check "pyproject.toml has [project]"
    else
        fail_check "pyproject.toml missing [project]"
    fi

    if grep -q "requires-python" "$PROJECT_ROOT/pyproject.toml"; then
        pass_check "pyproject.toml specifies requires-python"
    else
        warn_check "pyproject.toml missing requires-python"
    fi
else
    fail_check "pyproject.toml not found"
fi

# Check 10: No legacy config files
if [[ -f "$PROJECT_ROOT/setup.py" ]]; then
    warn_check "setup.py found (prefer pyproject.toml only)"
else
    pass_check "No setup.py (using pyproject.toml)"
fi

if [[ -f "$PROJECT_ROOT/setup.cfg" ]]; then
    warn_check "setup.cfg found (prefer pyproject.toml for tool config)"
else
    pass_check "No setup.cfg"
fi

# --- Summary ---
echo ""
echo "========================================="
echo "  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "========================================="

if [[ $FAIL -gt 0 ]]; then
    exit 1
else
    exit 0
fi
