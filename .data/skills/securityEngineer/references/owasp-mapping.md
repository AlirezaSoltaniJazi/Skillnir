# OWASP Top 10 (2021) — Skillnir Project Mapping

## A01: Broken Access Control
- **Risk**: NiceGUI UI has no authentication
- **Locations**: `src/skillnir/ui/__init__.py`, `src/skillnir/ui/pages/`
- **Mitigation**: Localhost-only binding. Document network exposure risk.
- **Remediation**: Add auth middleware if deploying beyond localhost

## A02: Cryptographic Failures
- **Risk**: Webhook URL exposure
- **Locations**: `src/skillnir/crypto.py` (encryption), `src/skillnir/backends.py` (storage)
- **Mitigation**: Fernet encryption with machine-bound PBKDF2 key derivation
- **Status**: ✅ Compliant

## A03: Injection
- **Risk**: Command injection via subprocess, YAML deserialization
- **Locations**: `src/skillnir/backends.py:557` (subprocess), `src/skillnir/skills.py:29` (YAML)
- **Mitigation**: List-based subprocess args with `--` separator; `yaml.safe_load()` only
- **Status**: ✅ Compliant

## A04: Insecure Design
- **Risk**: Missing input validation on trust boundaries
- **Locations**: `src/skillnir/cli.py` (path input), `src/skillnir/ui/pages/skill.py` (path input)
- **Mitigation**: `.resolve()` and `.is_dir()` checks on user paths
- **Status**: ✅ Compliant

## A05: Security Misconfiguration
- **Risk**: Hardcoded NiceGUI storage secret
- **Location**: `src/skillnir/ui/__init__.py:140`
- **Mitigation**: None currently
- **Remediation**: Derive from `_machine_fingerprint()` or use `secrets.token_hex()`

## A06: Vulnerable and Outdated Components
- **Risk**: Known CVEs in dependencies
- **Locations**: `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`
- **Mitigation**: Safety + Bandit in pre-commit; CI enforcement
- **Status**: ✅ Compliant (CVE-2025-6176 documented exception)

## A07: Identification and Authentication Failures
- **Risk**: N/A for local CLI tool
- **Note**: Auth delegated to AI backend CLIs (claude, cursor, gemini, copilot)

## A08: Software and Data Integrity Failures
- **Risk**: Dependency tampering, unsafe deserialization
- **Locations**: `uv.lock` (checksums), `src/skillnir/skills.py` (YAML)
- **Mitigation**: Lockfile with checksums; yaml.safe_load() only
- **Status**: ✅ Compliant

## A09: Security Logging and Monitoring
- **Risk**: No structured security logging
- **Note**: Local development tool uses print(). Acceptable for threat model.

## A10: Server-Side Request Forgery
- **Risk**: Minimal — no user-controlled outbound HTTP
- **Status**: ✅ Not applicable
