#!/usr/bin/env bash
# validate-security.sh — Security convention checker for Skillnir
# Checks for hardcoded secrets, insecure patterns, missing headers, deprecated crypto
# Usage: bash scripts/validate-security.sh [path-to-src]

set -euo pipefail

SRC="${1:-src/skillnir}"
ERRORS=0

echo "=== Security Convention Checker ==="
echo "Scanning: $SRC"
echo ""

# 1. Check for unsafe YAML loading
echo "--- Checking for unsafe YAML loading (CWE-502) ---"
if grep -rn 'yaml\.load(' "$SRC" --include="*.py" | grep -v 'safe_load' | grep -v '# nosec'; then
    echo "FAIL: Found yaml.load() without safe_load"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: All YAML loading uses safe_load"
fi
echo ""

# 2. Check for shell=True in subprocess
echo "--- Checking for shell=True (CWE-78) ---"
if grep -rn 'shell\s*=\s*True' "$SRC" --include="*.py" | grep -v '# nosec'; then
    echo "FAIL: Found shell=True in subprocess calls"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No shell=True found"
fi
echo ""

# 3. Check for eval/exec
echo "--- Checking for eval/exec (CWE-95) ---"
if grep -rn '\beval(' "$SRC" --include="*.py" | grep -v '# nosec' | grep -v '#.*eval'; then
    echo "FAIL: Found eval() calls"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No eval() calls found"
fi
if grep -rn '\bexec(' "$SRC" --include="*.py" | grep -v '# nosec' | grep -v '#.*exec'; then
    echo "FAIL: Found exec() calls"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No exec() calls found"
fi
echo ""

# 4. Check for pickle
echo "--- Checking for pickle usage (CWE-502) ---"
if grep -rn 'pickle\.\(loads\|load\)(' "$SRC" --include="*.py" | grep -v '# nosec'; then
    echo "FAIL: Found pickle deserialization"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No pickle deserialization found"
fi
echo ""

# 5. Check for hardcoded secrets patterns
echo "--- Checking for hardcoded secrets (CWE-798) ---"
if grep -rn -E '(api_key|api_secret|password|passwd)\s*=\s*["\x27][^"\x27]{8,}' "$SRC" --include="*.py" | grep -v '# nosec' | grep -v 'help=' | grep -v 'description='; then
    echo "WARN: Possible hardcoded secrets found (review manually)"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No obvious hardcoded secrets"
fi
echo ""

# 6. Check for deprecated crypto
echo "--- Checking for deprecated crypto (CWE-327) ---"
if grep -rn 'hashlib\.\(md5\|sha1\)(' "$SRC" --include="*.py" | grep -v '# nosec' | grep -v 'checksum' | grep -v 'fingerprint'; then
    echo "WARN: Found MD5/SHA1 usage (verify not for security)"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No deprecated crypto for security purposes"
fi
echo ""

# 7. Check for os.path usage (project convention: use pathlib)
echo "--- Checking for os.path usage (project convention) ---"
if grep -rn 'import os\.path\|from os\.path\|os\.path\.' "$SRC" --include="*.py" | grep -v '# nosec'; then
    echo "WARN: Found os.path usage (project uses pathlib)"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: No os.path usage found"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ "$ERRORS" -eq 0 ]; then
    echo "All security checks PASSED"
    exit 0
else
    echo "$ERRORS issue(s) found — review above"
    exit 1
fi
