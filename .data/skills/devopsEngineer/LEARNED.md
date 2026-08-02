# devopsEngineer — Learned Knowledge

> Auto-updated by AI. Entries accumulate across sessions. Format: `- YYYY-MM-DD: rule description`

## Corrections

## Preferences

## Discovered Conventions

- 2026-08-02: `.pre-commit-config.yaml` has 12 hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-ast, check-merge-conflict, uv-safety, bandit, autoflake, pylint, black, prettier), not 11 as SKILL.md's Architecture tree comment says.
- 2026-08-02: `pyproject.toml`'s dev-group floor is `pre-commit>=4.6.0`, not `4.5+` as SKILL.md's `compatibility` frontmatter says.
- 2026-08-02: `.github/workflows/` has two more workflows than SKILL.md's Architecture tree shows: `pr-version-check.yml` (fails a PR if `pyproject.toml`'s version goes backwards) and `bump-version.yml` (bumps version + promotes CHANGELOG + tags + releases, on PR-merge or manual dispatch).
