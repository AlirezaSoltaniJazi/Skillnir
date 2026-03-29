# Skill System Security Checklist

> Security verification for the skillnir skill file system. Covers content integrity, injection prevention, and access control.

---

## SKILL.md Security

- [ ] No secrets, API keys, or credentials in frontmatter or body
- [ ] `allowed-tools` is scoped minimally (no wildcard Bash unless needed)
- [ ] `Agent` is in `allowed-tools` if and only if `agents/` directory exists
- [ ] No executable code blocks that could be copy-pasted unsafely
- [ ] Links use relative paths only (no external URLs that could be hijacked)

## INJECT.md Security

- [ ] No secrets or credentials in quick reference
- [ ] No file paths containing sensitive directory names
- [ ] Token budget respected (50-150 tokens) — prevents context overflow

## LEARNED.md Security

- [ ] No secrets recorded as "preferences" or "corrections"
- [ ] No user-specific absolute paths (use relative or `~` notation)
- [ ] Entries are factual conventions, not executable instructions

## references/ Security

- [ ] Code examples use safe patterns (no `shell=True`, no `eval()`)
- [ ] Template files don't contain hardcoded credentials
- [ ] Security checklists are complete and up-to-date
- [ ] No references to internal/private URLs

## scripts/ Security

- [ ] All scripts use `set -euo pipefail`
- [ ] No `eval` or dynamic command construction
- [ ] File paths are quoted to prevent word splitting
- [ ] Scripts don't modify files — read-only validation only
- [ ] Exit codes properly indicate pass/fail

## Symlink Security

- [ ] Symlinks use relative paths (`../../.data/skills/`)
- [ ] `.resolve()` called before any delete/rmtree operations
- [ ] Symlink targets validated before creation
- [ ] No circular symlinks possible in the skill directory structure

## agents/ Security

- [ ] Analysis-only agents restricted to `Read Glob Grep` (no write access)
- [ ] Write agents explicitly listed with justification
- [ ] No agent can spawn sub-agents (max depth = 1 enforced in definitions)
- [ ] Context templates don't leak sensitive parent conversation data

## Cross-Tool Security

- [ ] `.claude/settings.json` permissions match skill requirements
- [ ] Tool-specific dotdirs (`.cursor/`, `.codex/`, etc.) only contain symlinks
- [ ] No tool-specific overrides that bypass skill conventions
