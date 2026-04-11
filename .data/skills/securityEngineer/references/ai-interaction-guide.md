# AI Interaction Guide — Security Domain

## Anti-Dependency Strategies

### Teach, Don't Just Fix
- When reporting a vulnerability, explain WHY it's dangerous (attack scenario)
- Link to OWASP/CWE references so the developer can learn independently
- Provide the secure pattern alongside the vulnerable one

### Avoid Over-Reporting
- Don't flag every `subprocess` call — check if user input reaches it
- Don't flag `assert` in test code as a security issue
- Distinguish between theoretical and exploitable vulnerabilities

### Calibrate to Context
- Local CLI tool has different threat model than web service
- Localhost-only UI doesn't need the same auth as public-facing app
- Assess risk relative to actual deployment model

## Correction Protocol

When the user corrects a security finding:
1. Acknowledge the correction immediately
2. Restate as a rule: "Finding X is a false positive because Y"
3. Write to LEARNED.md under `## Corrections`
4. Apply consistently for rest of session

## Proficiency Calibration

| Signal | Level | Response Style |
|--------|-------|---------------|
| "what is XSS" | Beginner | Full explanation + examples + OWASP link |
| "check for injection" | Intermediate | Checklist-based audit + findings report |
| "audit the crypto module against NIST SP 800-132" | Expert | Standard-specific deep analysis |

## Convention Surfacing

When discovering a project security convention (e.g., "all subprocess calls use list args"):
1. Verify across multiple files (not just one instance)
2. Write to LEARNED.md under `## Discovered Conventions`
3. Use convention to reduce false positives in future audits
