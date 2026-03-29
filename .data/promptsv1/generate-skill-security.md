# Security Engineer Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are security-specific overrides.

```
ROLE:     Senior security engineer performing a comprehensive security audit across all platforms
GOAL:     Generate a production-grade security audit skill directory
SCOPE:    Security posture across ALL code — backend, frontend, mobile, infrastructure, dependencies, secrets, configurations
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Security Audit (All Platforms)

Unlike other scopes, security is **cross-cutting**. Scan ALL code across every platform present. Organize findings by security domain.

**Authentication & Authorization**

- Auth mechanism (JWT, session, OAuth2, SAML, API keys, mTLS)
- Password policy (hashing algorithm, salting, complexity requirements, rotation)
- Session management (expiry, invalidation, fixation prevention, cookie flags)
- Access control model (RBAC, ABAC, ACL — check for broken access control patterns)
- Multi-factor authentication presence and enforcement
- OAuth2/OIDC implementation (redirect URI validation, state parameter, PKCE)
- Mobile auth (biometric, Keychain/KeyStore usage, token storage location)
- API authentication (key rotation, scope enforcement, rate limiting per key)
- Default credentials, hardcoded passwords, shared secrets

**Injection & Input Validation**

- SQL injection vectors (raw queries, ORM misuse, missing parameterization)
- XSS vectors (reflected, stored, DOM-based — output encoding, CSP presence)
- Command injection (subprocess calls, eval, exec, template injection, shell=True)
- Path traversal (file operations with user input, directory escape)
- SSRF (outbound HTTP with user-controlled URLs, internal network access)
- Deserialization (unsafe deserialization — pickle, yaml.load, JSON, XML)
- GraphQL-specific (query depth limiting, introspection in prod, batching abuse)
- LDAP/XPath/header injection if applicable
- Mobile: WebView JavaScript injection, intent/deep link parameter injection, IPC abuse

**Cryptography & Data Protection**

- Encryption at rest (database, file storage, mobile local storage, backups)
- Encryption in transit (TLS version, cipher suites, HSTS, certificate pinning)
- Key management (hardcoded keys, rotation policy, KMS/vault usage)
- Hashing (deprecated algorithms: MD5, SHA1 for security; proper bcrypt/scrypt/Argon2 for passwords)
- Sensitive data exposure (PII in logs, error messages, URLs, client-side storage, localStorage)
- Mobile data protection (Keychain access groups, EncryptedSharedPreferences, data protection classes)
- Random number generation (CSPRNG usage vs Math.random/random module for security)

**Dependency & Supply Chain**

- Known vulnerabilities in dependencies (CVE presence, outdated packages)
- Lockfile integrity (presence, pinning strategy, checksum verification)
- Private package registry security (scoped packages, dependency confusion risk)
- Build pipeline integrity (signed commits, protected branches, artifact verification)
- Container base image vulnerabilities and update policy
- Mobile: third-party SDK permissions, SDK update cadence, transitive dependency risk
- License compliance for security-relevant libraries

**Infrastructure & Configuration Security**

- Docker (non-root USER, minimal base image, no secrets in layers, read-only fs, cap-drop)
- Kubernetes (SecurityContext, NetworkPolicies, PodSecurityStandards, RBAC, Secrets encryption)
- CI/CD (secret exposure in logs, pipeline injection, OIDC vs static credentials, branch protections)
- Cloud IAM (least privilege, no wildcard permissions, service account hygiene, MFA on root)
- Secret management (hardcoded secrets, .env in VCS, vault integration, rotation)
- CORS configuration (overly permissive origins, credentials mode)
- HTTP security headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, HSTS)
- Rate limiting and DoS protection (throttling, resource quotas, connection limits)
- TLS termination (where, certificate management, auto-renewal)

**Mobile-Specific Security**

- OWASP Mobile Top 10 (2024) coverage
- Insecure data storage (SharedPreferences, NSUserDefaults, SQLite without encryption, cache/clipboard)
- Certificate pinning implementation and bypass resistance
- Binary protections (obfuscation, anti-tampering, anti-debugging, root/jailbreak detection)
- Inter-process communication (exported components, URL schemes, deep links, broadcast receivers)
- WebView security (JavaScript bridges, file access, mixed content, loadUrl with user input)
- App Transport Security (iOS) / Network Security Configuration (Android)
- Backup configuration (android:allowBackup, iOS encryption class)

**Logging, Monitoring & Incident Response**

- Security event logging (auth failures, privilege escalation, data access, admin actions)
- Log injection prevention (sanitization of CR/LF/delimiters in user input within logs)
- Audit trail completeness (who, what, when, where for sensitive operations)
- Error handling (stack trace exposure, verbose errors in production, information leakage)
- Alerting on suspicious activity patterns (brute force, unusual data access)
- Log storage security (tamper protection, retention policy, access control)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_security.md`:

1. **Vulnerability Landscape** — categorized findings by CVSS severity (Critical/High/Medium/Low/Info)
2. **Attack Surface Map** — entry points, trust boundaries, data flows across platforms
3. **Security Architecture** — existing security controls, gaps, defense-in-depth assessment
4. **Things to ALWAYS do** — non-negotiable security patterns observed or required
5. **Things to NEVER do** — dangerous anti-patterns found or to be avoided (with CWE reference)
6. **Platform-specific findings** — issues unique to each detected platform (backend/frontend/mobile/infra)
7. **Remediation Priority** — ordered by risk (CVSS score × exploitability × business impact)

---

## PHASE 3: BEST PRACTICES

Integrate for the detected platforms and stack:

- OWASP Top 10 (2021) — mapped to project-specific code patterns
- OWASP API Security Top 10 (2023) — if REST/GraphQL/gRPC endpoints detected
- OWASP Mobile Top 10 (2024) — if Android/iOS code detected
- OWASP LLM Top 10 — if AI/ML components or LLM integrations detected
- NIST Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover)
- CIS Benchmarks for detected infrastructure (Docker, Kubernetes, cloud provider)
- SANS/CWE Top 25 Most Dangerous Software Weaknesses
- Secure SDLC practices (threat modeling, security requirements, secure code review)
- Zero trust architecture principles (verify explicitly, least privilege, assume breach)
- Defense in depth (layered security controls, no single point of failure)
- Principle of least privilege across all layers (code, infra, CI/CD, cloud)
- Secure defaults (deny by default, fail closed, minimum permissions)
- Supply chain security (SLSA levels, SBOM generation, signed artifacts)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY security task — vulnerability assessment, security audit, penetration test review, OWASP compliance, dependency audit, secret scanning, access control review, cryptographic review, secure code review, security configuration, compliance check, threat modeling, incident response, CVE triage, security headers review.

**`allowed-tools`**: `Read Glob Grep Bash(pip-audit:*) Bash(npm:audit) Bash(trivy:*) Bash(semgrep:*) Agent`

Note: Security analysis is primarily **read-only**. No `Edit` or `Write` — remediation is suggested with code examples, never silently applied. Bash is scoped to security scanning CLIs. When security CLIs are unavailable, fall back to pattern-based analysis using Read/Glob/Grep.

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (security audit, pre-deploy review, dependency check, compliance assessment, incident investigation, code review with security focus)
2. **Do NOT Use** — cross-references to sibling skills for non-security tasks (use backend for API design, frontend for UI patterns, infra for deployment pipelines, testing for test automation)
3. **Vulnerability Classification** — CVSS-based severity table (Critical ≥9.0, High 7.0–8.9, Medium 4.0–6.9, Low 0.1–3.9, Info 0.0) with CWE/CVE reference format
4. **Key Patterns** — summary table only (vulnerability class, detection signal, remediation approach, CWE ID). Full code examples in references/ only
5. **Security Checklist** — rules table organized by OWASP category. Per-component verification details in references/security-checklist.md
6. **Common Recipes** — numbered step lists only (how to audit auth flow, how to check for injection, how to review dependencies, how to assess mobile security)
7. **Vulnerability Report Format** — structured format: severity (CVSS score), CWE ID, description, evidence (file:line), remediation with code example, standards references (OWASP/NIST/CIS)
8. **Compliance Mapping** — bullet list mapping findings to standards (OWASP, NIST, CIS, SOC 2, PCI-DSS, HIPAA where applicable)
9. **Anti-Patterns** — dangerous security anti-patterns with CWE reference and severity (e.g., "Hardcoded secrets — CWE-798 — CRITICAL")
10. **References** — OWASP cheat sheets, CWE database, framework-specific security guides, tool documentation
11. **Adaptive Interaction Protocols** — interaction modes with security-specific detection signals (e.g., "what is BOLA" for Teaching, "check this endpoint like the last one" for Efficient, "we got a CVE alert" / "this endpoint was breached" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/vulnerability-patterns.md` — detailed vulnerability patterns with detection and remediation code examples (ALL code examples go here)
- `references/code-style.md` — secure coding conventions, naming for security utilities, import patterns
- `references/security-checklist.md` — per-component, per-platform verification checklists mapped to OWASP categories
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/owasp-mapping.md` — full OWASP Top 10 mapping with project-specific code locations and remediation
- `references/remediation-templates.md` — copy-paste secure code templates for common fixes (parameterized queries, CSP headers, auth middleware, cert pinning, input validation)
- `references/common-issues.md` — troubleshooting common security misconfigurations and false positives
- `references/report-template.md` — vulnerability report template with CVSS scoring guide and CWE/CVE reference format
- `assets/security-headers-example.conf` — security headers configuration template (nginx/Apache/Express)
- `assets/csp-policy-example.json` — Content Security Policy template with common directives
- `scripts/validate-security.sh` — security convention checker (hardcoded secrets, insecure patterns, missing headers, deprecated crypto)

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                 | Role                                                                 | Tools               | Spawn When                                                                  |
| --------------------- | -------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------- |
| vulnerability-scanner | Static code analysis for security patterns across all platforms      | Read Glob Grep      | Security audit, code review, pre-deploy check, OWASP compliance scan        |
| dependency-auditor    | Supply chain and dependency vulnerability analysis                   | Read Glob Grep Bash | CVE alert triage, lockfile review, new dependency addition, update review   |
| config-auditor        | Security misconfiguration detection for infrastructure, cloud, CI/CD | Read Glob Grep      | Docker/K8s security check, CI/CD pipeline audit, cloud config review, CORS  |
| pentest-reviewer      | Penetration testing review and exploit chain analysis                | Read Glob Grep      | Pentest report review, threat modeling, attack surface assessment, red team |

All sub-agents are **read-only** — security analysis should never modify code. The `dependency-auditor` has Bash access scoped to running audit commands (`pip-audit`, `npm audit`, `trivy`).

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/vulnerability-scanner.md` — static security analysis agent (code patterns, injection, auth, crypto)
- `agents/dependency-auditor.md` — supply chain vulnerability analysis agent (CVEs, lockfiles, SBOMs)
- `agents/config-auditor.md` — security misconfiguration detection agent (infra, cloud, headers, CORS)
- `agents/pentest-reviewer.md` — penetration testing review agent (exploit chains, threat models, attack narratives)
