# Remediation Templates — Copy-Paste Secure Code

## 1. Fix Hardcoded NiceGUI Storage Secret

```python
# BEFORE (vulnerable)
ui.run(storage_secret="skillnir-local")

# AFTER (secure)
import secrets
from pathlib import Path

def _get_storage_secret() -> str:
    """Return a persistent per-install storage secret."""
    secret_file = Path.home() / ".skillnir" / "ui_secret"
    try:
        if secret_file.exists():
            return secret_file.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    secret = secrets.token_hex(32)
    try:
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        secret_file.write_text(secret + "\n", encoding="utf-8")
        secret_file.chmod(0o600)
    except OSError:
        pass
    return secret

ui.run(storage_secret=_get_storage_secret())
```

## 2. Parameterized Subprocess with Input Validation

```python
import shlex
import subprocess
from pathlib import Path

def safe_subprocess(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run subprocess with validated arguments."""
    # Ensure no shell=True
    # Ensure cwd is resolved and exists
    if cwd:
        cwd = cwd.resolve()
        if not cwd.is_dir():
            raise ValueError(f"Working directory does not exist: {cwd}")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
```

## 3. Safe YAML Loading

```python
import yaml

def safe_load_yaml(text: str) -> dict:
    """Load YAML safely — never use yaml.load()."""
    return yaml.safe_load(text) or {}
```

## 4. HTML Escaping for Web UI

```python
import html

def safe_html(user_input: str) -> str:
    """Escape user input for safe HTML rendering."""
    return html.escape(user_input, quote=True)

# Usage in NiceGUI
ui.html(f"<div>{safe_html(user_text)}</div>")
```

## 5. Path Validation

```python
from pathlib import Path

def validate_path(user_path: str, allowed_base: Path) -> Path:
    """Validate user-provided path is within allowed directory."""
    resolved = Path(user_path).resolve()
    allowed = allowed_base.resolve()
    if not resolved.is_relative_to(allowed):
        raise ValueError(f"Path {resolved} is outside allowed base {allowed}")
    return resolved
```

## 6. Secure File Permissions

```python
from pathlib import Path

def write_sensitive_file(path: Path, content: str) -> None:
    """Write file with restrictive permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    try:
        path.chmod(0o600)  # Owner read/write only
    except OSError:
        pass  # Best-effort on non-POSIX
```

## 7. Secret Scanning Regex Patterns

```python
import re

SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[\w-]{20,}'),
    re.compile(r'(?i)(secret|password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}'),
    re.compile(r'(?i)(token|bearer)\s*[=:]\s*["\']?[\w.-]{20,}'),
    re.compile(r'(?i)(aws_access_key_id)\s*[=:]\s*["\']?AKIA[\w]{16}'),
    re.compile(r'(?i)(private[_-]?key)\s*[=:]\s*["\']?-----BEGIN'),
    re.compile(r'hooks\.googleapis\.com/spaces/[\w/]+'),  # Google Chat webhook
]
```
