# Security Checklist — Generic Python Reference

> Input validation, SQL injection, subprocess safety, secret management, and dependency auditing checklists.

---

## Input Validation

- [ ] Validate all user input at API/CLI boundaries before processing
- [ ] Use Pydantic models or dataclasses with validators for structured input
- [ ] Validate enum values against known sets
- [ ] Validate string lengths, numeric ranges, and format patterns
- [ ] Sanitize user input for display (prevent XSS in web apps, terminal escapes in CLIs)
- [ ] Reject unexpected fields in API requests (use strict Pydantic models)

```python
# Correct — validate at boundary
from pydantic import BaseModel, Field

class CreateItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=0, le=10000)
```

---

## SQL Injection Prevention

- [ ] Use parameterized queries for ALL database operations — never string-format SQL
- [ ] Use ORM query builders when available (SQLAlchemy, Django ORM)
- [ ] Validate and whitelist column names for dynamic ORDER BY / WHERE clauses
- [ ] Never interpolate user input directly into SQL strings

```python
# Correct — parameterized query
cursor.execute(
    'SELECT * FROM users WHERE email = %s AND active = %s',
    (email, True),
)

# Correct — SQLAlchemy
stmt = select(User).where(User.email == email)

# Wrong — SQL injection vulnerability
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

---

## Path Validation

- [ ] Validate all user-provided paths with `Path.resolve()` before operations
- [ ] Check paths don't escape project root (path traversal prevention)
- [ ] Use `Path.exists()` and `Path.is_file()`/`Path.is_dir()` before operations
- [ ] Handle symlink targets — verify they point to expected locations
- [ ] Never use string concatenation for paths — always `Path /` operator

```python
from pathlib import Path

def validate_path(path: Path, root: Path) -> bool:
    """Ensure path is within the allowed root directory."""
    resolved = path.resolve()
    return resolved.is_relative_to(root.resolve())
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
import shutil
import subprocess

cmd = shutil.which('tool_name')
if cmd is None:
    return OperationResult(success=False, error='tool_name not found')

result = subprocess.run(
    [cmd, '--flag', argument],   # list form, no shell=True
    capture_output=True,
    text=True,
    timeout=60,
    cwd=working_dir,
)
```

---

## Secret Management

- [ ] Never embed API keys, tokens, or passwords in source code
- [ ] Use environment variables for all secrets
- [ ] Never log or print secret values
- [ ] Add `.env` to `.gitignore`
- [ ] Use `os.environ.get()` with fallback for optional settings
- [ ] Use a secrets manager (AWS Secrets Manager, Vault, etc.) for production
- [ ] Rotate secrets periodically
- [ ] Use separate secrets for each environment (dev, staging, production)

---

## Dependency Auditing

- [ ] Run `pip-audit` or `safety` regularly for known CVEs
- [ ] Run `bandit` for static security analysis of Python code
- [ ] Review new dependencies before adding — check maintenance status and license
- [ ] Pin dependency versions in lock files for reproducibility
- [ ] Audit transitive dependencies periodically
- [ ] Use minimal dependency sets — prefer stdlib when possible

---

## Authentication & Authorization

- [ ] Hash passwords with bcrypt/argon2 — never store plaintext
- [ ] Use constant-time comparison for tokens (`hmac.compare_digest`)
- [ ] Validate JWT tokens properly (expiry, issuer, audience)
- [ ] Implement rate limiting on authentication endpoints
- [ ] Log authentication failures for monitoring

---

## File Operations Safety

- [ ] Use `encoding='utf-8'` explicitly on all `read_text()`/`write_text()` calls
- [ ] Check `source.resolve() != target.resolve()` before destructive operations
- [ ] Create parent directories with `mkdir(parents=True, exist_ok=True)`
- [ ] Handle `OSError` for all filesystem operations
- [ ] Use atomic writes (write to temp file, then rename) for critical data
- [ ] Set appropriate file permissions on sensitive files
