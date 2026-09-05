#!/usr/bin/env bash
# Read-only convention checker for the promptCompressor skill.
# Verifies the module contract (stdlib-only, entry point, fast) and runs its tests.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
mod="$root/src/skillnir/compressor.py"
fail=0

echo "== promptCompressor validate =="

# 1. Module exists
if [ ! -f "$mod" ]; then
  echo "FAIL: $mod is missing"
  fail=1
fi

# 2. Public entry point present
if ! grep -qE "^def compress_prompt\(" "$mod" 2>/dev/null; then
  echo "FAIL: compress_prompt() entry point not found in compressor.py"
  fail=1
fi

# 3. Stdlib-only — no third-party imports (only 're', typing, dataclasses, etc.)
if grep -qE "^(import|from) (nicegui|questionary|yaml|claude|requests|pydantic)" "$mod" 2>/dev/null; then
  echo "FAIL: compressor.py must stay dependency-free (no third-party imports)"
  fail=1
fi

# 4. Regex word matching uses word boundaries (\\b) — the core safety rule
if grep -qE "re\.(sub|compile|search|match)" "$mod" && ! grep -q '\\b' "$mod"; then
  echo "WARN: no \\b word-boundary found — verify word matching is boundary-safe"
fi

# 5. Tests pass
echo "-- running tests/test_compressor.py --"
if ! uv run pytest "$root/tests/test_compressor.py" -q; then
  echo "FAIL: compressor tests did not pass"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "OK: promptCompressor conventions verified"
fi
exit "$fail"
