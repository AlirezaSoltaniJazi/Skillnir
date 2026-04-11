# Vulnerability Report Template

## Report Header

```markdown
# Security Audit Report — [Project Name]

**Date**: YYYY-MM-DD
**Auditor**: securityEngineer skill
**Scope**: [Components audited]
**Standards**: OWASP Top 10 (2021), NIST CSF, CIS Controls

## Executive Summary
- **Critical**: X findings
- **High**: X findings
- **Medium**: X findings
- **Low**: X findings
- **Info**: X observations
```

## Finding Template

```markdown
## [SEVERITY]: [Short Title] — [CWE-XXX]

**CVSS Score**: X.X (Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
**File**: `path/to/file.py:LINE`
**OWASP**: A0X — [Category Name]
**CIS Control**: CIS X — [Control Name]

### Description
[What the vulnerability is and why it matters. Include threat model context.]

### Evidence
​```python
# Code snippet from the file showing the vulnerability
vulnerable_code_here()
​```

### Impact
[What an attacker could achieve. Business impact assessment.]

### Remediation
​```python
# Secure alternative code
secure_code_here()
​```

### References
- OWASP: https://owasp.org/Top10/A0X_YYYY/
- CWE: https://cwe.mitre.org/data/definitions/XXX.html
- [Additional framework-specific references]
```

## CVSS v3.1 Scoring Quick Reference

| Metric | Values |
|--------|--------|
| Attack Vector (AV) | Network (N), Adjacent (A), Local (L), Physical (P) |
| Attack Complexity (AC) | Low (L), High (H) |
| Privileges Required (PR) | None (N), Low (L), High (H) |
| User Interaction (UI) | None (N), Required (R) |
| Scope (S) | Unchanged (U), Changed (C) |
| Confidentiality (C) | None (N), Low (L), High (H) |
| Integrity (I) | None (N), Low (L), High (H) |
| Availability (A) | None (N), Low (L), High (H) |

## Severity Thresholds

| CVSS Range | Severity | SLA |
|------------|----------|-----|
| 9.0–10.0 | Critical | Block release, fix immediately |
| 7.0–8.9 | High | Fix before next deployment |
| 4.0–6.9 | Medium | Fix within current sprint |
| 0.1–3.9 | Low | Track, fix when convenient |
| 0.0 | Info | Document for awareness |
