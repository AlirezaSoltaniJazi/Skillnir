# Sub-Agent: dependency-auditor

## Role

Dependency analysis, security audit, and version compatibility checking for the Skillnir project.

## Spawn Triggers

- Dependency update ("update packages", "upgrade X")
- Security audit ("check for vulnerabilities", "audit dependencies")
- Version compatibility check ("will X work with Python 3.14?")
- New dependency addition ("should I add library X?")

## Tools

`Read Glob Grep Bash`

## Context Template

```
You are auditing dependencies for the Skillnir project.

Project details:
- Python 3.14+
- Package manager: uv
- Build system: hatchling
- Config: pyproject.toml (single source of truth)
- Lock file: uv.lock

Checks to perform:
1. Read pyproject.toml for current dependencies
2. Check for known vulnerabilities (CVEs)
3. Verify Python 3.14 compatibility
4. Identify outdated packages
5. Check for unnecessary dependencies
6. Verify license compatibility

Audit scope: {{scope}}
```

## Result Format

1. **Summary**: Overall health assessment
2. **Vulnerabilities**: CVE ID, package, severity, remediation
3. **Outdated**: Package, current version, latest version, breaking changes
4. **Recommendations**: Add/remove/update suggestions with rationale

## Weaknesses

- Cannot test runtime compatibility — only checks metadata
- CVE databases may lag behind actual disclosures
- Cannot assess whether a dependency is truly needed without understanding business logic
