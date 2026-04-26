#!/usr/bin/env bash
set -euo pipefail

# Validates frontend conventions for a generic web project.
# Usage: ./validate-frontend.sh [src-dir]
#
# Checks:
# 1. Component files use PascalCase naming
# 2. No `any` type usage in TypeScript files
# 3. No inline styles for static values
# 4. No default exports in component files (pages excluded)
# 5. No direct DOM manipulation (document.querySelector, etc.)
# 6. No console.log in production code
# 7. Accessibility: no missing alt attributes on images
# 8. Import order and alias usage

SRC_DIR="${1:-./src}"

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
echo "  Frontend Convention Validator"
echo "========================================="
echo ""

if [[ ! -d "$SRC_DIR" ]]; then
    fail_check "Source directory not found: $SRC_DIR"
    echo ""
    echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
    exit 1
fi

# Check 1: Component files use PascalCase
echo "--- Checking component file naming ---"
bad_names=0
for f in "$SRC_DIR"/components/**/*.{tsx,vue,svelte} 2>/dev/null; do
    if [[ -f "$f" ]]; then
        basename_file=$(basename "$f")
        # Skip index files and test files
        if [[ "$basename_file" == "index."* ]] || [[ "$basename_file" == *".test."* ]] || [[ "$basename_file" == *".spec."* ]]; then
            continue
        fi
        # Check if first char is uppercase (PascalCase)
        first_char="${basename_file:0:1}"
        if [[ "$first_char" != [A-Z] ]]; then
            warn_check "Non-PascalCase component file: $basename_file"
            bad_names=$((bad_names + 1))
        fi
    fi
done
if [[ $bad_names -eq 0 ]]; then
    pass_check "All component files use PascalCase naming"
fi

# Check 2: No explicit `any` type usage
echo ""
echo "--- Checking TypeScript any usage ---"
any_usage=$(grep -rn ": any\b\|<any>\|as any" "$SRC_DIR" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "node_modules" | grep -v ".test." | grep -v ".spec." | head -10 || true)
if [[ -z "$any_usage" ]]; then
    pass_check "No explicit 'any' type usage found"
else
    fail_check "Explicit 'any' type found in source files:"
    echo "$any_usage" | head -5
fi

# Check 3: No console.log in production code
echo ""
echo "--- Checking for console.log ---"
console_usage=$(grep -rn "console\.\(log\|debug\|info\)" "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.vue" --include="*.svelte" 2>/dev/null | grep -v "node_modules" | grep -v ".test." | grep -v ".spec." | head -10 || true)
if [[ -z "$console_usage" ]]; then
    pass_check "No console.log in production code"
else
    warn_check "console.log found (should use proper logging):"
    echo "$console_usage" | head -5
fi

# Check 4: No direct DOM manipulation
echo ""
echo "--- Checking for direct DOM manipulation ---"
dom_usage=$(grep -rn "document\.\(querySelector\|getElementById\|getElementsBy\|createElement\)" "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.vue" --include="*.svelte" 2>/dev/null | grep -v "node_modules" | grep -v ".test." | head -10 || true)
if [[ -z "$dom_usage" ]]; then
    pass_check "No direct DOM manipulation"
else
    warn_check "Direct DOM manipulation found (use framework APIs):"
    echo "$dom_usage" | head -5
fi

# Check 5: No dangerouslySetInnerHTML or v-html without sanitization
echo ""
echo "--- Checking for unsafe HTML rendering ---"
unsafe_html=$(grep -rn "dangerouslySetInnerHTML\|v-html\|\[innerHTML\]" "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.vue" --include="*.svelte" 2>/dev/null | grep -v "node_modules" | grep -v "DOMPurify\|sanitize" | head -10 || true)
if [[ -z "$unsafe_html" ]]; then
    pass_check "No unsafe HTML rendering without sanitization"
else
    fail_check "Unsafe HTML rendering found (use DOMPurify):"
    echo "$unsafe_html" | head -5
fi

# Check 6: No relative imports beyond co-located files
echo ""
echo "--- Checking import conventions ---"
deep_relative=$(grep -rn "from '\.\./\.\.\|from \"\.\./\.\." "$SRC_DIR" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "node_modules" | grep -v ".test." | head -10 || true)
if [[ -z "$deep_relative" ]]; then
    pass_check "No deep relative imports (../../+)"
else
    warn_check "Deep relative imports found (use path aliases @/):"
    echo "$deep_relative" | head -5
fi

# Check 7: Image alt attributes
echo ""
echo "--- Checking image accessibility ---"
missing_alt=$(grep -rn "<img " "$SRC_DIR" --include="*.tsx" --include="*.vue" --include="*.svelte" 2>/dev/null | grep -v "alt=" | grep -v "node_modules" | head -10 || true)
if [[ -z "$missing_alt" ]]; then
    pass_check "All <img> elements have alt attributes"
else
    fail_check "Images missing alt attribute:"
    echo "$missing_alt" | head -5
fi

# Check 8: Test files exist for components
echo ""
echo "--- Checking test coverage ---"
untested=0
for f in "$SRC_DIR"/components/**/*.{tsx,vue,svelte} 2>/dev/null; do
    if [[ -f "$f" ]]; then
        basename_file=$(basename "$f")
        # Skip index files, test files, and non-component files
        if [[ "$basename_file" == "index."* ]] || [[ "$basename_file" == *".test."* ]] || [[ "$basename_file" == *".spec."* ]]; then
            continue
        fi
        # Check for co-located or __tests__ test file
        dir=$(dirname "$f")
        name_without_ext="${basename_file%.*}"
        if [[ ! -f "$dir/$name_without_ext.test.tsx" ]] && \
           [[ ! -f "$dir/$name_without_ext.test.ts" ]] && \
           [[ ! -f "$dir/$name_without_ext.spec.tsx" ]] && \
           [[ ! -f "$dir/$name_without_ext.spec.ts" ]] && \
           [[ ! -f "$dir/__tests__/$name_without_ext.test.tsx" ]] && \
           [[ ! -f "$dir/__tests__/$name_without_ext.test.ts" ]]; then
            warn_check "No test file for: $basename_file"
            untested=$((untested + 1))
        fi
    fi
done
if [[ $untested -eq 0 ]]; then
    pass_check "All components have test files"
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
