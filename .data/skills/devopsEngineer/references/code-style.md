# Code Style — Infrastructure Files

## GitHub Actions Workflow Conventions

### Naming
- Workflow files: `kebab-case.yml` (e.g., `run-tests.yml`, `check-style.yml`)
- Workflow names: `PR - {Description}` for PR-triggered workflows
- Job names: descriptive, title case (e.g., `Run Tests`, `Lint & Format Check`)
- Step names: imperative, title case (e.g., `Checkout repository`, `Setup Python`)

### Structure
```yaml
name: PR - {Description}

on: [pull_request]  # or expanded form for specific types

jobs:
    job-name:
        name: Descriptive Job Name
        runs-on: ubuntu-latest
        timeout-minutes: 10  # ALWAYS set

        steps:
            - name: Checkout repository
              uses: actions/checkout@v4

            - name: Setup Python
              uses: ./.github/actions/setup-python

            - name: {Action description}
              run: {command}
```

### Action Pinning
- Always pin to major version: `actions/checkout@v4`, `actions/setup-python@v5`
- Never use `@main`, `@latest`, or `@master`
- Composite actions use relative paths: `uses: ./.github/actions/setup-python`

### Permissions
- Scope to minimum required per job
- Default: no explicit permissions (read-only)
- Document why permissions are needed

## Pre-commit Configuration

### Hook Entry Structure
```yaml
- repo: https://github.com/{org}/{repo}
    rev: vX.Y.Z  # Always pinned
    hooks:
      - id: {hook-id}
        args: ["{flag1}", "{flag2}"]
        exclude: ^\.data/  # Exclude generated/data dirs
```

### Exemption Documentation
```yaml
args:
  # Ignore {CVE-ID} ({reason}, {current version} is latest)
  - --ignore={CVE-number}
```

## Bash Script Conventions

### Validation Scripts
```bash
#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PASS=0; FAIL=0; WARN=0

# --- Helper Functions ---
pass_check() { ((PASS++)); echo "  ✅ $1"; }
fail_check() { ((FAIL++)); echo "  ❌ $1"; }
warn_check() { ((WARN++)); echo "  ⚠️  $1"; }

# --- Checks ---
echo "🔍 Checking {category}..."
# ... checks ...

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

### Key Rules
- Always use `set -euo pipefail`
- Use `PROJECT_ROOT` calculated from script location
- Use emoji prefixes for output: ✅ pass, ❌ fail, ⚠️ warning
- Exit 0 on all pass, exit 1 on any failure
- Group related checks under section headers

## Environment Separation

| Environment | Purpose                  | Configuration Source    |
| ----------- | ------------------------ | ---------------------- |
| Local       | Developer machine        | `.pre-commit-config.yaml`, `.pylintrc` |
| CI          | PR validation            | `.github/workflows/*.yml` |
| Production  | Not applicable (CLI tool)| N/A                    |

## File Organization

```
.github/
├── actions/
│   └── setup-python/
│       └── action.yml          # Composite action
├── workflows/
│   ├── run-tests.yml           # Test runner
│   ├── check-style.yml         # Linting + formatting
│   └── auto-assign-author.yml  # PR automation
└── pull_request_template.md    # PR template
```
