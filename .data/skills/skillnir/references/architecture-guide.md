# Skill System Architecture

## Directory Structure

`.data/skills/` is the central skill storage and single source of truth. Each
skill is a `camelCase` directory. The injector symlinks these into every tool
dotdir — the dotdirs never hold real content, only relative symlinks pointing
back to `.data/skills/<skillName>`.

```
.data/skills/                    # Central skill storage (SOURCE OF TRUTH)
├── backendEngineer/             # Python backend, CLI, async, dataclasses, testing
├── devopsEngineer/              # CI/CD, pre-commit, quality gates, packaging
├── frontendEngineer/            # NiceGUI UI, Tailwind/Quasar, theming, i18n
├── github/                      # GitHub workflow conventions
├── gitlab/                      # GitLab workflow conventions
├── jira/                        # Jira workflow conventions
├── promptCompressor/            # Rule-based prompt token compression
├── securityEngineer/            # Security audit, vuln assessment, crypto review
└── skillnir/                    # THIS SKILL — meta-rules for the skill system
    ├── SKILL.md                 # Generated decision guide
    ├── INJECT.md                # Always-loaded quick reference (firewall)
    ├── LEARNED.md               # Session-accumulated learnings
    ├── references/              # Detailed skill-system documentation
    └── scripts/validate-skill-system.sh
```

There are currently **9 skills**: backendEngineer, devopsEngineer,
frontendEngineer, github, gitlab, jira, promptCompressor, securityEngineer,
skillnir. `github`, `gitlab`, and `jira` were added in commit `4c980f2`
(2026-08-01). Verify the live roster with `ls .data/skills/`.

## Data Flow

1. Skills live in `.data/skills/` (source of truth).
2. `skillnir install` runs the injector, which creates relative symlinks in each
   tool dotdir — `.claude/skills/`, `.cursor/skills/`, `.codex/skills/`,
   `.agents/skills/`, `.gemini/skills/`, `.github/skills/`, etc.
3. On activation, AI tools read `SKILL.md`.
4. `LEARNED.md` is read first — its session corrections override SKILL.md defaults.
5. `INJECT.md` is always loaded as a hallucination firewall.

## Tooling

| Command                     | Purpose                                             |
| --------------------------- | --------------------------------------------------- |
| `skillnir generate-skill`   | Generate a skill from prompts in `.data/promptsv1/` |
| `skillnir install`          | Symlink skills into tool dotdirs                    |
| `skillnir update` / `sync`  | Version-aware sync of skill changes                 |

File-ownership rules (who edits SKILL.md vs LEARNED.md vs references/) live in
SKILL.md's File Ownership table. See [skill-file-guide.md](skill-file-guide.md)
for token budgets and full per-file documentation.
