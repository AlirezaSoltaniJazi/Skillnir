# Secure Coding Conventions — Skillnir

## Naming Conventions for Security Utilities

| Context                  | Convention                   | Example                                   |
| ------------------------ | ---------------------------- | ----------------------------------------- |
| Encryption functions     | `encrypt_`/`decrypt_` prefix | `encrypt_string()`, `decrypt_string()`    |
| Validation functions     | `validate_`/`is_` prefix     | `validate_path()`, `is_safe_url()`        |
| Sanitization functions   | `sanitize_`/`escape_` prefix | `sanitize_input()`, `escape_html()`       |
| Security constants       | `SCREAMING_SNAKE_CASE`       | `_SALT`, `_PBKDF2_ITERATIONS`             |
| Private security helpers | `_` prefix                   | `_derive_key()`, `_machine_fingerprint()` |

## Import Patterns for Security Modules

```python
# Standard library security imports
import hashlib
import hmac
import secrets
import html
import shlex
from pathlib import Path

# Third-party security imports
from cryptography.fernet import Fernet, InvalidToken

# Local security imports (absolute only)
from skillnir.crypto import encrypt_string, decrypt_string
```

## Secure Error Handling Pattern

```python
@dataclass
class SecurityCheckResult:
    check_name: str
    passed: bool
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    cwe_id: str | None = None
    description: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    remediation: str | None = None
    error: str | None = None
```

## File Permission Pattern

```python
# Set restrictive permissions on sensitive files
path.chmod(0o600)  # Owner read/write only

# Verify permissions before reading sensitive files
if path.stat().st_mode & 0o077:
    print("WARNING: Sensitive file has overly permissive access")
```
