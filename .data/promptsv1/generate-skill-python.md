# Python Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Python-specific overrides.

```
ROLE:     Senior Python engineer analyzing a production Python codebase
GOAL:     Generate a production-grade Python development skill directory
SCOPE:    Python code only — ignore frontend (JS/TS), mobile (Swift/Kotlin), infra (Docker/Terraform)
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Python Only

**Language & Tooling**

- Python version (3.10/3.11/3.12/3.13/3.14)
- Package manager (uv/pip/poetry/pdm/pipenv/conda)
- Build system (hatchling/setuptools/poetry-core/flit/maturin)
- Dependency file (pyproject.toml/requirements.txt/setup.cfg/Pipfile)
- Virtual environment strategy (.venv, conda env, system)
- Key dependencies and their roles

**Framework & Architecture**

- Web framework (FastAPI/Flask/Django/Starlette/Litestar/aiohttp — or none for CLIs/libraries/scripts)
- Architecture pattern (monolith, modular, layered, microservices, serverless, CLI)
- API patterns (REST/GraphQL/gRPC — routing, validation, serialization)
- Project type (web API, CLI tool, data pipeline, library, script collection, ML/AI)
- Entry points (main.py, manage.py, cli.py, **main**.py)
- Configuration pattern (pydantic-settings, python-dotenv, dynaconf, environ)

**Code Quality**

- Type hints usage (partial, full, strict mypy, pyright)
- Formatter/linter (ruff/black/isort/flake8/pylint)
- Docstring format (Google, NumPy, Sphinx, none)
- Error handling (custom exceptions, result types, error middleware)
- Naming conventions (modules, classes, functions, constants)
- Import style (absolute vs relative, grouping)

**Data Layer**

- ORM/database (SQLAlchemy/Django ORM/Tortoise/Peewee/raw SQL/MongoDB)
- Database type (PostgreSQL/MySQL/SQLite/MongoDB/Redis)
- Migration tool (Alembic/Django migrations/manual)
- Data validation (Pydantic/marshmallow/attrs/dataclasses)
- Caching (Redis/memcached/in-memory)

**Async & Concurrency**

- Async framework (asyncio/trio/anyio — or sync only)
- Task queue (Celery/Dramatiq/Huey/ARQ/RQ)
- Background tasks pattern
- Thread/process pool usage

**Testing**

- Framework (pytest/unittest)
- Structure (unit/integration split, conftest.py, fixtures)
- Test data (factories/fixtures/faker/model_bakery)
- Mocking (unittest.mock/pytest-mock/responses/httpx-mock)
- Coverage tooling (coverage.py, pytest-cov)
- Async testing (pytest-asyncio/anyio)

**CLI & Scripting** (if applicable)

- CLI framework (click/typer/argparse/rich)
- Script organization (single file, package, entry points)
- Input/output patterns (stdin/stdout, file I/O, rich output)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_python.md`:

1. **Architecture Patterns** — how this project structures Python code
2. **Data Flow** — input to processing to output path
3. **Coding Conventions** — style, naming, structure conventions
4. **Package Patterns** — key packages and idiomatic usage
5. **Things to ALWAYS do** — non-negotiable patterns observed
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Framework-specific wisdom** — patterns unique to the detected framework/project type

---

## PHASE 3: BEST PRACTICES

Integrate for the detected stack:

- Python 3.13+ features (type unions, match statements, exception groups, TaskGroups)
- Type annotation best practices (generics, protocols, TypeVar, overload)
- Error handling hierarchy (custom exceptions, result patterns, logging)
- Testing discipline (unit vs integration, what to mock, fixture patterns)
- Async best practices (structured concurrency, cancellation, TaskGroups)
- Performance (profiling, generators, **slots**, caching, bulk operations)
- Security (input validation, SQL injection prevention, secret management, dependency auditing)
- Packaging (pyproject.toml, entry points, extras, version management)
- Documentation (docstrings, type stubs, README patterns)
- 12-factor app principles (config from env, stateless processes, disposability)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Python task — web APIs, CLI tools, data processing, scripts, libraries, testing, database operations, async code, package management, deployment, type annotations.

**`allowed-tools`**: `Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (frontend JS/TS, mobile, infra)
3. **Architecture** — project structure, module organization, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Import order, type hints, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with Python-specific detection signals (e.g., "what is this decorator" for Teaching, "another endpoint like X" for Efficient, "ImportError" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/patterns.md` — API/CLI/data patterns with full code examples (ALL code examples go here)
- `references/code-style.md` — import order, type hints, formatting with full examples
- `references/security-checklist.md` — input validation, SQL injection, secret management checklists
- `references/template.py` — copy-paste module/class boilerplate
- `references/test-patterns.md` — testing patterns with full examples
- `references/common-issues.md` — troubleshooting common Python pitfalls
- `assets/pyproject-example.toml` — pyproject.toml template
- `scripts/validate-python.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent              | Role                                                           | Tools                          | Spawn When                                                     |
| ------------------ | -------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------- |
| code-reviewer      | Read-only Python code analysis and type checking audit         | Read Glob Grep                 | PR review, refactoring assessment, type annotation audit       |
| test-writer        | Pytest test generation following project fixtures and patterns | Read Edit Write Glob Grep Bash | "write tests for X", new module creation, coverage gaps        |
| dependency-auditor | Dependency analysis and security audit                         | Read Glob Grep Bash            | Dependency update, security audit, version compatibility check |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Python code analysis agent
- `agents/test-writer.md` — pytest test generation agent
- `agents/dependency-auditor.md` — dependency analysis and security agent
