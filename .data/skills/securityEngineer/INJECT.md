# securityEngineer — Quick Reference

<!-- Always-loaded firewall: bullets only, <150 tokens. -->

- **FIRST**: read [LEARNED.md](LEARNED.md) for corrections
- **READ-ONLY**: suggest fixes, never apply
- **Every finding**: CVSS + CWE + `file:line`
- **Stack safe**: `yaml.safe_load`, list subprocess, `Path.resolve`, `html.escape`, Fernet+PBKDF2 (`crypto.py`)
- **Known issues**: hardcoded NiceGUI `storage_secret` (CWE-798); UI localhost-only, no auth
- **Sub-agents** (read-only): vulnerability-scanner, dependency-auditor, config-auditor, pentest-reviewer
- **Full**: [SKILL.md](SKILL.md)
