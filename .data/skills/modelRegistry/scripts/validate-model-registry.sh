#!/usr/bin/env bash
# Read-only validator for the AI model registry and CLI install hints.
# Checks the invariants the picker and model resolution depend on.
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"
fail=0

echo "== modelRegistry validate =="

# 1. Registry invariants: unique aliases, one default, resolvable default_model
uv run python - <<'PY' || fail=1
from skillnir.backends import BACKENDS, resolve_model_id

bad = 0
for backend, info in BACKENDS.items():
    name = backend.value
    aliases = [m.alias for m in info.models]

    dupes = {a for a in aliases if aliases.count(a) > 1}
    if dupes:
        print(f"FAIL [{name}] duplicate alias(es): {sorted(dupes)}")
        bad = 1

    defaults = [m for m in info.models if m.is_default]
    if len(defaults) != 1:
        print(f"FAIL [{name}] expected exactly 1 is_default, found {len(defaults)}")
        bad = 1

    resolved = resolve_model_id(backend, info.default_model)
    if resolved == info.default_model and info.default_model not in aliases:
        print(f"FAIL [{name}] default_model {info.default_model!r} does not resolve")
        bad = 1

    for m in info.models:
        if not m.id or not m.alias or not m.display_name:
            print(f"FAIL [{name}] incomplete ModelInfo: {m}")
            bad = 1
        if m.tier not in (1, 2, 3):
            print(f"FAIL [{name}] {m.alias}: tier {m.tier} not in 1..3")
            bad = 1

    print(f"ok   [{name}] {len(info.models)} models, default={info.default_model}"
          f" -> {resolve_model_id(backend, info.default_model)}")

raise SystemExit(bad)
PY

# 2. Install hints: every backend's cli_command has a setup entry with required fields
uv run python - <<'PY' || fail=1
from skillnir.ui.components.welcome_dialog import _CLI_SETUP_INFO

required = ("name", "icon", "install", "login", "verify", "notes")
bad = 0
for entry in _CLI_SETUP_INFO:
    missing = [k for k in required if not entry.get(k)]
    if missing:
        print(f"FAIL install hint {entry.get('name', '?')!r} missing: {missing}")
        bad = 1
    else:
        print(f"ok   install hint: {entry['name']}")
if "install_alt" in (k for e in _CLI_SETUP_INFO for k in e):
    pass
raise SystemExit(bad)
PY

# 3. Registry tests
echo "-- running tests/test_backends.py --"
uv run pytest tests/test_backends.py -q || fail=1

if [ "$fail" -eq 0 ]; then
  echo "OK: model registry and install hints valid"
fi
exit "$fail"
