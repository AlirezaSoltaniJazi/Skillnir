# Common Skill System Issues

> Troubleshooting guide for common problems when working with the skillnir skill system.

---

## LEARNED.md Issues

### Problem: Duplicate or Conflicting Entries

**Symptom**: Two entries in LEARNED.md contradict each other.
**Fix**: Keep the more recent entry. Add a new entry that explicitly supersedes the old one:

```
- 2026-03-21: [SUPERSEDES 2026-03-15] Use pathlib.Path, not os.path (original entry was too vague)
```

### Problem: Entries Too Vague to Apply

**Symptom**: Entry like `- 2026-03-21: Use good patterns`.
**Fix**: Replace with specific, actionable rule:

```
- 2026-03-21: Use @dataclass(frozen=True) for all value objects (AITool, BackendInfo, ModelInfo)
```

### Problem: Multi-Rule Entries

**Symptom**: One entry contains multiple unrelated rules combined with "and".
**Fix**: Split into separate entries, one rule per line.

### Problem: Wrong Date Format

**Symptom**: Entry uses `Mar 21` or `03/21/2026` instead of `YYYY-MM-DD`.
**Fix**: Always use ISO 8601 format: `2026-03-21`.

---

## SKILL.md Issues

### Problem: SKILL.md Too Long (>300 Lines)

**Symptom**: Skill generator output exceeds budget.
**Fix**: Move code examples (>5 lines) to `references/`. Replace with one-liner summaries and links.

### Problem: Manual Edits Overwritten

**Symptom**: Hand-edited SKILL.md content lost after regeneration.
**Fix**: Manual learnings go in LEARNED.md, not SKILL.md. SKILL.md is generated content.

### Problem: Missing "Before You Start" Section

**Symptom**: AI doesn't read LEARNED.md or announce skill.
**Fix**: Every SKILL.md must start with the "Before You Start" section containing both instructions.

---

## INJECT.md Issues

### Problem: INJECT.md Too Large

**Symptom**: INJECT.md exceeds 150 tokens, consuming context budget.
**Fix**: Keep only the most critical facts. Move details to SKILL.md or references/.

### Problem: Stale Quick Reference

**Symptom**: INJECT.md references files or patterns that no longer exist.
**Fix**: Update INJECT.md when major project restructuring occurs. Verify all referenced paths exist.

---

## Symlink Issues

### Problem: Broken Symlinks After Skill Rename

**Symptom**: `.claude/skills/{{name}}` points to non-existent directory.
**Fix**: Re-run `skillnir install` to recreate symlinks. Or manually update:

```bash
cd .claude/skills/
rm broken-link
ln -s ../../.data/skills/{{new-name}} {{new-name}}
```

### Problem: Symlinks Not Created for New Tool

**Symptom**: New AI tool's dotdir doesn't have skill symlinks.
**Fix**: Run `skillnir install` which creates symlinks for all registered tools.

---

## Cross-Skill Issues

### Problem: Wrong Skill Activated

**Symptom**: backendEngineer patterns applied to UI code, or vice versa.
**Fix**: Use file-based routing from [cross-skill-rules.md](cross-skill-rules.md). Announce the correct skill.

### Problem: Conflicting Conventions Between Skills

**Symptom**: Two skills give different guidance for the same pattern.
**Fix**: Check LEARNED.md in both skills for overrides. The more domain-specific skill wins. Record resolution in the skillnir skill's LEARNED.md.

### Problem: LEARNED.md Entry in Wrong Skill

**Symptom**: Frontend convention written to backendEngineer's LEARNED.md.
**Fix**: Move the entry to the correct skill's LEARNED.md. Each skill owns its domain's learnings.

---

## Validation Script Issues

### Problem: Script Fails on macOS vs Linux

**Symptom**: `sed`, `grep`, or `find` behaves differently across platforms.
**Fix**: Use POSIX-compatible flags. Prefer `grep -E` over `grep -P`. Test on both platforms.

### Problem: Script Reports False Positives in .data/

**Symptom**: Linting/validation scripts flag generated content in `.data/` directory.
**Fix**: Add `--exclude-dir=.data` or equivalent to skip generated skill content.
