# Architecture Guide — backendEngineer

Full module map for `src/skillnir/`. SKILL.md carries only the prose summary; this file holds the structure.

## Directory Tree

```
src/skillnir/
├── cli.py                  # Entry point — argparse + questionary (28 commands)
├── backends.py             # Multi-backend registry (Claude, Cursor, Gemini, Copilot)
├── skills.py               # Skill dataclass + discovery, parse_frontmatter()
├── tools.py                # AITool registry (37 tools), SOURCE_DOTDIR
├── injector.py             # Symlink injection logic — inject_skill()
├── syncer.py               # Version-aware skill syncing
├── remover.py              # Skill + docs removal
├── generator.py            # AI doc (agents.md) generation (async SDK + subprocess)
├── skill_generator.py      # Multi-backend SKILL.md generation
├── skill_validator.py      # Deterministic validation of generated skill dirs
├── rule_generator.py       # Cursor rule (.mdc) generation
├── scaffold.py             # Skill scaffolding + to_camel_case()
├── researcher.py           # AI-engineering research + summarization
├── events.py               # AI events/conferences search (12 countries)
├── benchmarks.py           # AI model benchmarks search
├── security.py             # Security vulnerability search pipeline
├── package_vulns.py        # Package-advisory vulnerability research
├── harness_researcher.py   # AI agent / harness-engineering research
├── software_researcher.py  # Software-engineering research pipeline
├── testing_researcher.py   # Testing & QA research pipeline
├── news.py                 # Short-form AI news headlines pipeline
├── article_cleanup.py      # AI-classifies outdated articles → outdated/
├── article_status.py       # Shared article-status helpers (stdlib-only)
├── compressor.py           # Rule-based prompt compression
├── docs_compressor.py      # Rule-based + AI compression of AI-context docs
├── docs_optimizer.py       # AI-driven audit/fix of AI-context docs
├── wiki_generator.py       # llms.txt + docs/ wiki generation
├── crypto.py               # Fernet encryption for credential storage
├── notifications/          # Multi-provider webhook package (providers, senders)
├── notifier.py             # Back-compat shim → notifications/
├── hooks.py                # Sound notification hooks (macOS/Linux)
├── i18n.py                 # Internationalization (9 languages, RTL)
├── usage.py                # Thread-safe usage statistics tracking
├── locales/                # Translation JSON files (9 languages)
├── ui/                     # NiceGUI web interface
│   ├── layout.py           # Navigation structure (get_nav_groups + i18n)
│   ├── components/         # 13 reusable UI components
│   └── pages/              # 23 route page modules
└── resources/              # HTML templates and static assets
```

Module count drifts as pipelines are added — verify with `ls src/skillnir/*.py | wc -l`. See [LEARNED.md](../LEARNED.md) for the running discovery log.

## Data Flow

```
CLI input
  → main()'s choices=[...]-dispatched handler (cli.py)
  → core module (business logic — never in cli.py)
  → filesystem / subprocess / SDK
  → result dataclass
  → CLI/UI report (questionary/callback)
```

- **Entry point**: `skillnir = "skillnir.cli:main"` in `pyproject.toml`.
- **Source of truth**: `.data/skills/` — tool dotdirs hold only relative symlinks back to it.
- **Dual execution paths** in `skill_generator.py`: async SDK (Claude) vs subprocess CLI (Cursor/Gemini/Copilot). Both must be maintained.
