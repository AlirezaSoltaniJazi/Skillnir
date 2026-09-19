# Security Checklist — Per-Component Verification

## A01: Broken Access Control (OWASP 2021)

- [ ] All endpoints require authentication (or documented as public)
- [ ] Authorization checks on every state-changing operation
- [ ] No direct object references without ownership validation
- [ ] CORS configured with specific allowed origins (not `*`)
- [ ] Directory listing disabled on file-serving endpoints
- [ ] Rate limiting on authentication endpoints

**Skillnir status**: NiceGUI UI runs localhost-only. No auth required for local development tool. Document if deployment scope changes.

## A02: Cryptographic Failures

- [ ] No deprecated algorithms (MD5, SHA1 for security, DES, RC4)
- [ ] Passwords hashed with bcrypt/scrypt/Argon2 (not raw SHA-256)
- [ ] Encryption keys derived with PBKDF2 ≥100K iterations or Argon2
- [ ] Sensitive data encrypted at rest (config secrets, tokens)
- [ ] TLS 1.2+ enforced for all network communication
- [ ] No hardcoded keys, salts, or IVs in source code
- [ ] CSPRNG used for security-sensitive random values

**Skillnir status**: ✅ Fernet encryption with PBKDF2-HMAC-SHA256 (100K iterations). Machine-bound key derivation. 0o600 file permissions.

## A03: Injection

- [ ] All SQL queries parameterized (no string concatenation)
- [ ] YAML parsed with `safe_load()` only
- [ ] No `eval()`, `exec()`, `compile()` with user input
- [ ] Subprocess uses list arguments (no `shell=True` with user input)
- [ ] `shlex.quote()` for any shell argument construction
- [ ] Template engines use autoescaping
- [ ] `html.escape()` for user content in HTML output

**Skillnir status**: ✅ yaml.safe_load() only. List-based subprocess. html.escape() in UI. No eval/exec.

## A04: Insecure Design

- [ ] Threat model documented for security-critical features
- [ ] Input validation on all trust boundaries
- [ ] Rate limiting on resource-intensive operations
- [ ] Error handling fails closed (deny by default)

**Skillnir status**: Result dataclass pattern prevents exception leakage. Subprocess timeouts enforced.

## A05: Security Misconfiguration

- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Unnecessary features/endpoints disabled
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Error messages don't expose stack traces
- [ ] `.gitignore` covers sensitive files (.env, credentials, keys)

**Skillnir status**: ⚠️ Hardcoded NiceGUI `storage_secret`. ✅ .gitignore covers .env, .nicegui storage, config.

## A06: Vulnerable and Outdated Components

- [ ] No known CVEs in direct dependencies
- [ ] No known CVEs in transitive dependencies
- [ ] Lockfile present and pinned (uv.lock)
- [ ] Automated vulnerability scanning in CI (safety, bandit)
- [ ] Dependency update policy documented

**Skillnir status**: ✅ Safety + Bandit in pre-commit. Bandit also runs in CI (`.github/workflows/check-style.yml`); Safety is pre-commit-only (triggers on `pyproject.toml`/`uv.lock` changes, not run in CI). uv.lock pinned.

## A07: Identification and Authentication Failures

- [ ] Strong password policy (if applicable)
- [ ] MFA available for sensitive operations
- [ ] Session tokens invalidated on logout
- [ ] Brute force protection (rate limiting, lockout)

**Skillnir status**: N/A — local CLI tool. Auth delegated to AI backend CLIs.

## A08: Software and Data Integrity Failures

- [ ] Dependencies verified via checksums (lockfile)
- [ ] CI/CD pipeline uses pinned actions/versions
- [ ] No unsigned or unverified code execution
- [ ] Deserialization validated (yaml.safe_load only)

**Skillnir status**: ✅ uv.lock with checksums. yaml.safe_load() only. Pre-commit hooks.

## A09: Security Logging and Monitoring Failures

- [ ] Authentication events logged (success + failure)
- [ ] Authorization failures logged
- [ ] Input validation failures logged
- [ ] Log injection prevented (no CRLF in user data)
- [ ] Logs don't contain sensitive data (passwords, tokens)

**Skillnir status**: Minimal logging (print only). No sensitive data in output. Acceptable for local tool.

## A10: Server-Side Request Forgery (SSRF)

- [ ] Outbound HTTP requests use URL allowlists
- [ ] No user-controlled URLs in server-side requests
- [ ] Internal network access blocked for external-facing requests

**Skillnir status**: ✅ Notification webhook URLs (`src/skillnir/notifications/`) ARE user-controlled (entered in Settings), but every provider validator (`is_valid_gchat_webhook()`, `is_valid_slack_webhook()`, etc. in `providers.py`) enforces `https://` + a per-provider host allowlist before `senders.py` opens the connection (`# nosec B310`, justified since the allowlist check already ran).

---

## Infrastructure Checklist

### CI/CD (GitHub Actions)

- [ ] Secrets not exposed in logs
- [ ] Actions pinned to SHA (not tags)
- [ ] Branch protections on main
- [ ] Pre-commit hooks enforced

### Pre-commit Security Hooks

- [ ] Bandit: Static analysis (`-lll -iii`)
- [ ] Safety: Dependency CVE check
- [ ] Autoflake: Remove unused imports (reduces attack surface)
- [ ] YAML check: Prevent malformed YAML injection
- [ ] Merge conflict check: Prevent accidental code inclusion

---

## Skillnir Project-State Audit (as of last review)

Current posture per control. `✅` = verified compliant, `⚠️` = accepted risk / follow-up. Re-verify each on audit — do not trust the cached status.

| Category                     | Check                                                       | Status                                                    |
| ---------------------------- | ---------------------------------------------------------- | --------------------------------------------------------- |
| Deserialization              | `yaml.safe_load()` only, no `pickle`/`eval`/`exec`         | ✅ `src/skillnir/skills.py`                                |
| Subprocess                   | List args, no `shell=True`, `--` separator for user input  | ✅ `src/skillnir/backends.py`                              |
| Path handling                | `.resolve()` + `.is_dir()` on user paths, relative symlinks | ✅ `cli.py`, `injector.py`                                 |
| Secret storage               | Fernet + machine-bound PBKDF2 key, `0o600` perms           | ✅ `src/skillnir/crypto.py`                                |
| HTML output                  | `html.escape()` for user content in UI                     | ✅ `src/skillnir/ui/`                                      |
| SSRF (webhooks)              | `https://` + per-provider host allowlist before `urlopen`  | ✅ `src/skillnir/notifications/providers.py`               |
| Pre-commit security          | Bandit + Safety hooks active                                | ✅ `.pre-commit-config.yaml`                               |
| Dependency CVE scan          | Bandit runs in CI + pre-commit; Safety pre-commit only     | ⚠️ Safety not in CI (`check-style.yml`)                    |
| Web UI auth                  | Authentication on network-exposed endpoints                | ⚠️ Local-only (127.0.0.1) — no auth; document if exposed  |
| NiceGUI `storage_secret`     | Unique per-instance secret                                  | ⚠️ Hardcoded — `ui/__init__.py:211` (CWE-798, MEDIUM)     |
| Structured logging           | No sensitive data in logs                                   | ✅ `print()` only, no sensitive data                       |

Historical anti-patterns audited and **not present** in the codebase: `yaml.load()` without SafeLoader (CWE-502), `eval()`/`exec()` on user input (CWE-95), `subprocess(shell=True)` + user input (CWE-78), hardcoded API keys (CWE-798), `pickle.loads()` on untrusted data (CWE-502), MD5/SHA1 for security (CWE-327), stack traces in errors (CWE-209). Plaintext secret storage (CWE-312) was migrated to Fernet.
