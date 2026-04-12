---
name: securityEngineer
description: >-
  Comprehensive security audit skill for the Skillnir project. Covers vulnerability
  assessment, dependency auditing, secret scanning, access control review, cryptographic
  review, secure code review, OWASP compliance, security configuration, threat modeling,
  CVE triage, security headers review, penetration test review, incident response,
  and compliance checks across all platforms — backend, frontend, infrastructure, and CI/CD.
compatibility: "Python 3.14+, bandit, safety, yaml.safe_load, Fernet, NiceGUI, subprocess"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: security
allowed-tools: Read Glob Grep Bash(pip-audit:*) Bash(npm:audit) Bash(trivy:*) Bash(semgrep:*) Agent
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: securityEngineer skill" at the very start of your response before doing any work.

**This skill is READ-ONLY.** Security analysis never modifies code. Remediation is suggested with code examples — never silently applied.

## When to Use

1. Security audit or vulnerability assessment of any project component
2. Pre-deploy security review or compliance check (OWASP, NIST, CIS)
3. Dependency audit, CVE triage, or supply chain risk assessment
4. Secret scanning, credential review, or cryptographic implementation review
5. Incident investigation or penetration test report review
6. Code review with security focus (injection, auth, access control)

## Do NOT Use

- **Python backend development** (API design, CLI logic, async patterns) — use [backendEngineer](../backendEngineer/SKILL.md)
- **NiceGUI UI components/pages** (Tailwind, Quasar, HTML) — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **CI/CD, Docker, pre-commit hooks, workflows** — use [devopsEngineer](../devopsEngineer/SKILL.md)
- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)

## Vulnerability Classification

| Severity     | CVSS Score | Response                      | Format                            |
| ------------ | ---------- | ----------------------------- | --------------------------------- |
| **Critical** | ≥ 9.0      | Immediate — block release     | `CRITICAL: CWE-XXX — description` |
| **High**     | 7.0–8.9    | Fix before next deploy        | `HIGH: CWE-XXX — description`     |
| **Medium**   | 4.0–6.9    | Fix within sprint             | `MEDIUM: CWE-XXX — description`   |
| **Low**      | 0.1–3.9    | Track and fix when convenient | `LOW: CWE-XXX — description`      |
| **Info**     | 0.0        | Document for awareness        | `INFO: description`               |

## Key Patterns

| Vulnerability Class     | Detection Signal                                     | Remediation Approach                      | CWE     |
| ----------------------- | ---------------------------------------------------- | ----------------------------------------- | ------- |
| Command injection       | `subprocess` + `shell=True`, user input in commands  | List-based args, `shlex.quote()`          | CWE-78  |
| Unsafe deserialization  | `yaml.load()`, `pickle.loads()`, `eval()`            | `yaml.safe_load()`, validated schemas     | CWE-502 |
| Path traversal          | User input in `Path()` / `open()` without validation | `.resolve()`, allowlist, chroot           | CWE-22  |
| Hardcoded secrets       | Strings matching key/token/password patterns         | Environment vars, vault, encrypted config | CWE-798 |
| SQL injection           | String concatenation in queries                      | Parameterized queries, ORM                | CWE-89  |
| XSS                     | User input rendered without escaping                 | `html.escape()`, CSP headers              | CWE-79  |
| Broken access control   | Missing auth checks on endpoints/operations          | Middleware auth, RBAC enforcement         | CWE-862 |
| Insecure crypto         | MD5/SHA1 for security, weak key sizes                | Argon2/bcrypt for passwords, AES-256      | CWE-327 |
| SSRF                    | User-controlled URLs in outbound requests            | URL allowlist, no internal network access | CWE-918 |
| Sensitive data exposure | PII/secrets in logs, errors, client-side storage     | Redaction, structured logging, encryption | CWE-200 |

See [references/vulnerability-patterns.md](references/vulnerability-patterns.md) for detection patterns and remediation code.

## Security Checklist

| Category                       | Check                                                | Status in Skillnir |
| ------------------------------ | ---------------------------------------------------- | ------------------ |
| **Deserialization**            | `yaml.safe_load()` only, no pickle/eval              | ✅ Compliant       |
| **Subprocess**                 | List args, no `shell=True`, `--` separator for input | ✅ Compliant       |
| **Path handling**              | `.resolve()` on user paths, relative symlinks        | ✅ Compliant       |
| **Secret storage**             | Fernet encryption, machine-bound keys, 0o600 perms   | ✅ Compliant       |
| **HTML output**                | `html.escape()` for user content in UI               | ✅ Compliant       |
| **Pre-commit security**        | Bandit + Safety hooks active                         | ✅ Compliant       |
| **Web UI auth**                | Authentication on network-exposed endpoints          | ⚠️ Local-only      |
| **Storage secret**             | Unique per-instance NiceGUI `storage_secret`         | ⚠️ Hardcoded       |
| **Structured logging**         | No sensitive data in logs                            | ✅ No logging      |
| **Dependency vulnerabilities** | No known CVEs (safety check)                         | ✅ CI enforced     |

See [references/security-checklist.md](references/security-checklist.md) for per-component verification details.

## Common Recipes

1. **Audit auth flow**: Read auth-related modules → trace token/session lifecycle → check storage, expiry, invalidation → verify access control on all endpoints → report gaps
2. **Check for injection**: Grep for `subprocess`, `eval`, `exec`, `yaml.load`, `pickle`, `shell=True` → trace user input flow → verify sanitization at each boundary → report vectors
3. **Review dependencies**: Read `pyproject.toml` + `uv.lock` → run `pip-audit` / `safety check` → cross-reference CVE databases → assess transitive risk → prioritize by CVSS
4. **Scan for secrets**: Grep for patterns matching API keys, tokens, passwords, webhook URLs → check `.gitignore` coverage → verify encrypted storage → check git history for leaks
5. **Assess crypto implementation**: Read `crypto.py` → verify algorithm choices (Fernet/PBKDF2) → check key derivation parameters → validate key storage permissions → review rotation policy
6. **Review web UI security**: Check NiceGUI config → verify storage secret uniqueness → check HTML escaping → assess network binding → review static file serving paths

## Vulnerability Report Format

```
## [SEVERITY]: Short Title — CWE-XXX

**CVSS Score**: X.X | **File**: `path/to/file.py:LINE`

**Description**: What the vulnerability is and why it matters.

**Evidence**: Code snippet or grep output showing the issue.

**Remediation**: Specific fix with code example.

**References**: OWASP category, NIST control, CIS benchmark.
```

See [references/report-template.md](references/report-template.md) for full template with CVSS scoring guide.

## Compliance Mapping

- **OWASP Top 10 (2021)**: A01-Broken Access Control, A02-Crypto Failures, A03-Injection, A05-Security Misconfiguration, A06-Vulnerable Components, A08-Software/Data Integrity
- **OWASP API Security Top 10 (2023)**: API1-BOLA, API2-Broken Auth, API5-BFLA, API8-Security Misconfiguration
- **NIST CSF**: ID.AM (asset management), PR.AC (access control), PR.DS (data security), PR.IP (protective processes), DE.CM (continuous monitoring)
- **CIS Controls**: CIS 2 (software inventory), CIS 4 (secure configuration), CIS 6 (access control), CIS 16 (application software security)
- **SANS/CWE Top 25**: CWE-78, CWE-79, CWE-89, CWE-200, CWE-502, CWE-798, CWE-862

See [references/owasp-mapping.md](references/owasp-mapping.md) for project-specific mapping with file locations.

## Anti-Patterns

| Anti-Pattern                                | CWE     | Severity     | Skillnir Status |
| ------------------------------------------- | ------- | ------------ | --------------- |
| `yaml.load()` without SafeLoader            | CWE-502 | **CRITICAL** | Not present ✅  |
| `eval()`/`exec()` with user input           | CWE-95  | **CRITICAL** | Not present ✅  |
| `subprocess` with `shell=True` + user input | CWE-78  | **CRITICAL** | Not present ✅  |
| Hardcoded API keys / passwords              | CWE-798 | **HIGH**     | Not present ✅  |
| `pickle.loads()` on untrusted data          | CWE-502 | **HIGH**     | Not present ✅  |
| Plaintext secret storage                    | CWE-312 | **HIGH**     | Migrated ✅     |
| MD5/SHA1 for security hashing               | CWE-327 | **MEDIUM**   | Not present ✅  |
| Stack traces in production errors           | CWE-209 | **MEDIUM**   | Not present ✅  |
| Missing `html.escape()` in web output       | CWE-79  | **MEDIUM**   | Escaped ✅      |
| Hardcoded NiceGUI `storage_secret`          | CWE-798 | **MEDIUM**   | ⚠️ Present      |

## Code Generation Rules

1. **Never modify code** — security analysis is read-only; suggest fixes with code examples in reports
2. **Always cite evidence** — include file path, line number, and code snippet for every finding
3. **Use CVSS scoring** — classify every finding by severity with CWE ID
4. **Check LEARNED.md first** — apply all accumulated rules before starting analysis
5. **Map to standards** — reference OWASP, NIST, CIS, or CWE for every finding
6. **On correction** — acknowledge, restate as rule, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then SKILL.md, ask ONE question

## Adaptive Interaction Protocols

| Mode       | Detection Signal                                                    | Behavior                                                               |
| ---------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Diagnostic | "CVE alert", "endpoint breached", "security incident", stack trace  | Triage severity, trace attack path, assess blast radius, recommend fix |
| Efficient  | "check this endpoint like the last one", "same audit as before"     | Apply previous checklist, minimal explanation, report findings only    |
| Teaching   | "what is BOLA", "explain CSRF", "how does Fernet work"              | Explain with project examples, link to OWASP references                |
| Review     | "audit this module", "security review", "check for vulnerabilities" | Full checklist scan, structured report, prioritized findings           |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent                 | Role                                         | Spawn When                                             | Tools               |
| --------------------- | -------------------------------------------- | ------------------------------------------------------ | ------------------- |
| vulnerability-scanner | Static code analysis for security patterns   | Security audit, code review, OWASP compliance scan     | Read Glob Grep      |
| dependency-auditor    | Supply chain and dependency vulnerability    | CVE alert, lockfile review, new dependency addition    | Read Glob Grep Bash |
| config-auditor        | Security misconfiguration detection          | Docker/K8s check, CI/CD audit, CORS/headers review     | Read Glob Grep      |
| pentest-reviewer      | Penetration testing review and exploit chain | Pentest report review, threat modeling, attack surface | Read Glob Grep      |

**Delegation rules**: All sub-agents are read-only. Spawn when task is self-contained. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                   | Examples                                      |
| ----------------- | ----------------------------------------------------------------------- | --------------------------------------------- |
| **MUST** follow   | Read-only analysis, CVSS classification, CWE references, evidence-based | "MUST include file:line for every finding"    |
| **SHOULD** follow | OWASP mapping, structured report format, compliance references          | "SHOULD map findings to OWASP Top 10"         |
| **CAN** customize | Checklist ordering, report verbosity, remediation detail level          | "CAN prioritize by business impact over CVSS" |

## References

| File                                                                         | Description                                                  |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [LEARNED.md](LEARNED.md)                                                     | **Auto-updated.** Corrections, preferences, conventions      |
| [INJECT.md](INJECT.md)                                                       | Always-loaded quick reference (hallucination firewall)       |
| [references/vulnerability-patterns.md](references/vulnerability-patterns.md) | Detection patterns and remediation code for all vuln classes |
| [references/code-style.md](references/code-style.md)                         | Secure coding conventions and naming for security utilities  |
| [references/security-checklist.md](references/security-checklist.md)         | Per-component, per-platform verification checklists          |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md)     | Anti-dependency strategies, correction protocols             |
| [references/owasp-mapping.md](references/owasp-mapping.md)                   | Full OWASP Top 10 mapping with project file locations        |
| [references/remediation-templates.md](references/remediation-templates.md)   | Copy-paste secure code templates for common fixes            |
| [references/common-issues.md](references/common-issues.md)                   | Troubleshooting false positives and common misconfigurations |
| [references/report-template.md](references/report-template.md)               | Vulnerability report template with CVSS scoring guide        |
| [assets/security-headers-example.conf](assets/security-headers-example.conf) | Security headers configuration template                      |
| [assets/csp-policy-example.json](assets/csp-policy-example.json)             | Content Security Policy template                             |
| [scripts/validate-security.sh](scripts/validate-security.sh)                 | Security convention checker script                           |
| [agents/vulnerability-scanner.md](agents/vulnerability-scanner.md)           | Static security analysis agent                               |
| [agents/dependency-auditor.md](agents/dependency-auditor.md)                 | Supply chain vulnerability analysis agent                    |
| [agents/config-auditor.md](agents/config-auditor.md)                         | Security misconfiguration detection agent                    |
| [agents/pentest-reviewer.md](agents/pentest-reviewer.md)                     | Penetration testing review agent                             |
