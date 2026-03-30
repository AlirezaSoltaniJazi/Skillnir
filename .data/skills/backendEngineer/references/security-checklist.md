# Security Checklist — Skillnir Backend

> Input validation, subprocess safety, secret management, and dependency auditing checklists.

---

## Path Validation

- [ ] Validate all user-provided paths with `Path.resolve()` before operations
- [ ] Check paths don't escape project root (path traversal prevention)
- [ ] Use `Path.exists()` and `Path.is_file()`/`Path.is_dir()` before operations
- [ ] Handle symlink targets — verify they point to expected locations
- [ ] Never use string concatenation for paths — always `Path /` operator

```python
# ✅ Safe path validation
def validate_project_path(path: Path, project_root: Path) -> bool:
    resolved = path.resolve()
    return resolved.is_relative_to(project_root.resolve())
```

---

## Subprocess Safety

- [ ] Never use `shell=True` with user-provided input
- [ ] Use list form for command arguments: `['cmd', 'arg1', 'arg2']`
- [ ] Use `shlex.quote()` if shell string construction is unavoidable
- [ ] Set `timeout` on `subprocess.run()` and `Popen.wait()`
- [ ] Validate CLI command exists with `shutil.which()` before execution
- [ ] Capture and log stderr for debugging
- [ ] Set `cwd` explicitly to control working directory

```python
# ✅ Safe subprocess call
import shutil
import subprocess

cmd = shutil.which('claude')
if cmd is None:
    return GenerationResult(success=False, error='claude CLI not found')

proc = subprocess.Popen(
    [cmd, '--print', prompt],  # list form, no shell=True
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=project_root,
    text=True,
    timeout=300,
)
```

---

## Secret Management

- [ ] Never embed API keys, tokens, or passwords in source code
- [ ] Use environment variables for all secrets
- [ ] Never log or print secret values
- [ ] Add `.env` to `.gitignore`
- [ ] Use `os.environ.get()` with fallback for optional secrets

---

## Dependency Auditing

- [ ] Run `safety` CVE scanner via pre-commit (documented exemptions only)
- [ ] Run `bandit` security scanner with `-lll -iii` threshold
- [ ] Review new dependencies before adding — check maintenance status
- [ ] Pin dependency versions in `uv.lock` for reproducibility
- [ ] Audit transitive dependencies periodically

---

## Input Validation

- [ ] Validate YAML frontmatter structure before processing
- [ ] Handle `json.JSONDecodeError` for config file parsing
- [ ] Validate enum values against known sets (backends, tools, scopes)
- [ ] Sanitize user input for display (prevent terminal escape sequences)
- [ ] Validate version strings match expected format

---

## File Operations Safety

- [ ] Use `encoding='utf-8'` explicitly on all `read_text()`/`write_text()` calls
- [ ] Check `source.resolve() != target.resolve()` before `shutil.rmtree()`
- [ ] Create parent directories with `mkdir(parents=True, exist_ok=True)`
- [ ] Handle `OSError` for all filesystem operations
- [ ] Use atomic writes (write to temp file, then rename) for critical data
