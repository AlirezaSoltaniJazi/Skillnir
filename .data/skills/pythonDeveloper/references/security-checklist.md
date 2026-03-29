# Security Checklist

> Per-module security verification checklists for the Skillnir project, classified by severity and OWASP category.

---

## Severity Classification

| Severity | Description | Examples |
|----------|-------------|---------|
| **Critical** | Data loss, arbitrary code execution | Subprocess injection, path traversal deleting files |
| **High** | Information disclosure, auth bypass | Config secrets in logs, unvalidated user paths |
| **Medium** | Logic flaws, input validation gaps | Missing encoding, unhandled edge cases |
| **Low** | Code quality, minor information leak | Unused imports, verbose error messages |

---

## Subprocess Module (OWASP A03: Injection)

### Critical

- [ ] Never use `shell=True` with subprocess.Popen — always pass command as list
- [ ] Never interpolate user input directly into subprocess commands
- [ ] Validate all external CLI tool paths with `shutil.which()` before spawning
- [ ] Set timeout on `proc.wait()` to prevent hanging processes

### High

- [ ] Sanitize prompt content before passing to CLI tools (strip shell metacharacters)
- [ ] Drain stderr in a separate thread to prevent deadlock (already implemented)
- [ ] Check process return code and handle non-zero exits

### Medium

- [ ] Use `text=True` consistently (not `universal_newlines`)
- [ ] Capture and log stderr for debugging without exposing to end users

---

## File Operations (OWASP A01: Broken Access Control)

### Critical

- [ ] Validate paths don't escape project root (path traversal prevention)
- [ ] Use `Path.resolve()` to compare source/target before `shutil.rmtree` (already implemented in syncer.py)
- [ ] Never call `shutil.rmtree` on user-provided paths without validation

### High

- [ ] Always use `encoding='utf-8'` with `Path.read_text()` and `Path.write_text()`
- [ ] Check `.exists()` / `.is_dir()` before file operations
- [ ] Use `parents=True, exist_ok=True` for `mkdir` to handle race conditions

### Medium

- [ ] Use sorted directory iteration for deterministic behavior
- [ ] Handle symlink resolution carefully — `Path.resolve()` follows symlinks

---

## Configuration (OWASP A05: Security Misconfiguration)

### High

- [ ] Never store API keys or tokens in config.json — backends handle their own auth
- [ ] Validate JSON before parsing config files (handle JSONDecodeError gracefully)
- [ ] Set restrictive file permissions on `~/.skillnir/config.json`

### Medium

- [ ] Provide safe defaults in `AppConfig` for missing config values
- [ ] Migrate old config paths (`~/.agenrix/`, `~/.ai-injector/`) securely

---

## YAML Parsing (OWASP A08: Software and Data Integrity)

### Critical

- [ ] Always use `yaml.safe_load()`, never `yaml.load()` (prevents arbitrary code execution)

### Medium

- [ ] Validate frontmatter structure before accessing nested keys
- [ ] Handle malformed YAML gracefully (return empty dict)

---

## Symlink Operations (OWASP A01: Broken Access Control)

### High

- [ ] Validate symlink targets are within the project root
- [ ] Use relative symlinks (`../../.data/skills/X`) not absolute paths
- [ ] Handle existing symlinks gracefully (check before creating)

### Medium

- [ ] Verify symlink target exists after creation
- [ ] Clean up broken symlinks during injection

---

## Dependency Security

### High

- [ ] Run `safety check` via pre-commit for known CVEs
- [ ] Pin dependency versions in `pyproject.toml` with minimum bounds
- [ ] Review `uv.lock` for transitive dependency vulnerabilities

### Medium

- [ ] Keep Bandit in pre-commit pipeline (`-lll -iii` threshold)
- [ ] Monitor `python-safety-dependencies-check` exceptions (CVE-2025-6176 brotli)

---

## NiceGUI Web UI (OWASP A07: XSS)

### Medium

- [ ] NiceGUI handles XSS prevention internally — don't bypass with raw HTML
- [ ] Use `storage_secret` for session storage (already implemented)
- [ ] Bind to localhost only for local development

### Low

- [ ] Don't expose internal file paths in UI error messages
- [ ] Validate user inputs in UI forms before processing

---

## Pre-Deploy Checklist

1. [ ] All pre-commit hooks pass (`pre-commit run --all-files`)
2. [ ] No Bandit findings at `-lll -iii` threshold
3. [ ] No safety CVE alerts (except documented exceptions)
4. [ ] No unused imports (autoflake clean)
5. [ ] Pylint score ≥10 (fail-under)
6. [ ] All tests pass (`pytest`)
7. [ ] No hardcoded paths or secrets in source
