#!/usr/bin/env bash
set -euo pipefail

# Validate Python backend conventions for the Skillnir project
# Usage: ./validate-backend.sh [project-root]

PROJECT_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
SRC_DIR="$PROJECT_ROOT/src/skillnir"
TESTS_DIR="$PROJECT_ROOT/tests"

PASS=0
FAIL=0

check() {
    local description="$1"
    local result="$2"
    if [[ "$result" == "pass" ]]; then
        echo "  PASS  $description"
        ((PASS++))
    else
        echo "  FAIL  $description"
        ((FAIL++))
    fi
}

echo "=== Skillnir Backend Convention Validator ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# --- File Structure ---
echo "--- File Structure ---"

check "src/skillnir/ directory exists" \
    "$([[ -d "$SRC_DIR" ]] && echo pass || echo fail)"

check "tests/ directory exists" \
    "$([[ -d "$TESTS_DIR" ]] && echo pass || echo fail)"

check "pyproject.toml exists" \
    "$([[ -f "$PROJECT_ROOT/pyproject.toml" ]] && echo pass || echo fail)"

check "conftest.py exists in tests/" \
    "$([[ -f "$TESTS_DIR/conftest.py" ]] && echo pass || echo fail)"

# --- Naming Conventions ---
echo ""
echo "--- Naming Conventions ---"

# Check for snake_case Python files (no camelCase or PascalCase)
BAD_NAMES=$(find "$SRC_DIR" -name "*.py" | grep -E '[A-Z]' | grep -v __pycache__ || true)
check "All Python files use snake_case naming" \
    "$([[ -z "$BAD_NAMES" ]] && echo pass || echo fail)"

# Check that test files match test_*.py pattern
BAD_TESTS=$(find "$TESTS_DIR" -name "*.py" -not -name "test_*" -not -name "conftest.py" -not -name "__*" | head -5 || true)
check "All test files use test_*.py naming" \
    "$([[ -z "$BAD_TESTS" ]] && echo pass || echo fail)"

# --- Code Conventions ---
echo ""
echo "--- Code Conventions ---"

# Check for os.path usage (should use pathlib)
OS_PATH=$(grep -rn "import os\.path\|from os\.path\|os\.path\." "$SRC_DIR" --include="*.py" 2>/dev/null || true)
check "No os.path usage (use pathlib.Path)" \
    "$([[ -z "$OS_PATH" ]] && echo pass || echo fail)"

# Check for double quotes in Python files (Black -S enforces single quotes)
# Only check string literals, not docstrings
DOUBLE_QUOTES=$(grep -rn "= \"" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v '"""' | grep -v "encoding=" | head -5 || true)
check "Single quotes preferred (Black -S)" \
    "$([[ -z "$DOUBLE_QUOTES" ]] && echo pass || echo fail)"

# Check for type hints on function definitions
NO_HINTS=$(grep -rn "def [a-z_]*(.*)[^>]:$" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v "-> " | grep -v "__init__" | head -5 || true)
check "Functions have return type hints" \
    "$([[ -z "$NO_HINTS" ]] && echo pass || echo fail)"

# Check for module docstrings
for pyfile in "$SRC_DIR"/*.py; do
    if [[ -f "$pyfile" ]]; then
        FIRST_LINE=$(head -1 "$pyfile")
        if [[ "$FIRST_LINE" != '"""'* ]]; then
            MISSING_DOCSTRING="$pyfile"
            break
        fi
    fi
done
check "All modules have docstrings" \
    "$([[ -z "${MISSING_DOCSTRING:-}" ]] && echo pass || echo fail)"

# Check for yaml.load (should use yaml.safe_load)
UNSAFE_YAML=$(grep -rn "yaml\.load(" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v "safe_load" || true)
check "No yaml.load() usage (use yaml.safe_load)" \
    "$([[ -z "$UNSAFE_YAML" ]] && echo pass || echo fail)"

# Check for encoding parameter in read_text/write_text
MISSING_ENCODING=$(grep -rn "\.read_text()\|\.write_text(" "$SRC_DIR" --include="*.py" 2>/dev/null | grep -v "encoding=" | head -5 || true)
check "Path.read_text/write_text include encoding='utf-8'" \
    "$([[ -z "$MISSING_ENCODING" ]] && echo pass || echo fail)"

# --- Testing Conventions ---
echo ""
echo "--- Testing Conventions ---"

# Check that each source module has a test file
for pyfile in "$SRC_DIR"/*.py; do
    if [[ -f "$pyfile" ]]; then
        basename=$(basename "$pyfile" .py)
        if [[ "$basename" != "__init__" && "$basename" != "__main__" ]]; then
            test_file="$TESTS_DIR/test_${basename}.py"
            check "Test file exists for $basename.py" \
                "$([[ -f "$test_file" ]] && echo pass || echo fail)"
        fi
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
exit $FAIL
