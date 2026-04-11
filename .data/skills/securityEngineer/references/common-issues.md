# Common Issues — False Positives & Troubleshooting

## Bandit False Positives

### B101: assert_used
- **Trigger**: `assert` statements in production code
- **Skillnir context**: Acceptable in tests. Suppress with `# nosec B101` in test files only

### B603: subprocess_without_shell_equals_true
- **Trigger**: `subprocess.Popen()` without explicit `shell=False`
- **Skillnir context**: List-based commands are safe. Suppress with `# nosec B603` if verified

### B607: start_process_with_partial_path
- **Trigger**: Commands like `["claude", "--model", ...]` without full path
- **Skillnir context**: AI CLI tools resolved via PATH. Acceptable — suppress with `# nosec B607`

## Safety False Positives

### CVE-2025-6176 (brotli)
- **Status**: Documented exception in `.pre-commit-config.yaml`
- **Reason**: No fix available; low impact for local CLI tool
- **Action**: Monitor for upstream fix

## Common Misconfigurations

### NiceGUI storage_secret
- **Issue**: Hardcoded string shared across all instances
- **Impact**: Medium — cookie signing uses shared key
- **False positive?**: No — genuine issue, but low risk for localhost
- **Fix**: See [remediation-templates.md](remediation-templates.md#1-fix-hardcoded-nicegui-storage-secret)

### subprocess CWD with user input
- **Issue**: `cwd=str(target_project)` where path is user-provided
- **Impact**: Low — command itself is hardcoded
- **False positive?**: Partial — the CWD doesn't enable code execution
- **Mitigation**: Path.resolve() validates directory exists

## Grep Patterns That Generate Noise

| Pattern | Why it triggers | How to filter |
|---------|----------------|---------------|
| `password` | Variable names in forms | Check if it's assignment vs comparison |
| `secret` | NiceGUI `storage_secret` | Known issue — track separately |
| `token` | Generic "token" in comments | Filter to assignment patterns only |
| `key` | Dict key operations | Filter to string literal assignments |
| `eval` | Comments mentioning eval | Filter to actual function calls: `eval(` |
