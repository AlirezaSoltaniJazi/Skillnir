# Backend Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are backend-specific overrides.

```
ROLE:     Senior backend engineer analyzing a production server-side codebase
GOAL:     Generate a production-grade backend skill directory
SCOPE:    Server-side code only — ignore frontend/, client/, mobile/, static assets
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Backend Only

Ignore frontend, mobile, and infrastructure code. Scan for:

**Language & Framework**

- Primary language (Python/Go/Java/Rust/Node.js/etc.)
- Web framework (Django/Flask/FastAPI/Spring/Express/Gin/Actix/etc.)
- Package manager + dependency file (requirements.txt, pyproject.toml, go.mod, pom.xml, package.json, Cargo.toml)
- Key dependencies and usage patterns
- Version pinning strategy

**Architecture**

- Project structure (monolith vs modular vs microservices)
- Data models (ORM, schemas, structs — base classes, mixins, managers)
- API layer (ViewSets, handlers, controllers, routers)
- Serialization/validation (request/response shaping)
- URL routing conventions + versioning
- Middleware/interceptors (custom?)
- Configuration/settings structure (single file, split by env, env vars)
- Signal/event/hook patterns

**Code Quality**

- Type hints/annotations (partial, full, none)
- Docstring format (Google, NumPy, JSDoc, Rustdoc, none)
- Error handling (custom exceptions, error middleware, result types)
- Logging (stdlib, structlog, slog, log4j, custom)
- Constants/enums management
- Config management (env vars, files, vault)

**Testing**

- Framework (pytest, unittest, go test, JUnit, jest)
- Structure (unit/integration split, factories, fixtures)
- Naming conventions + coverage tooling

**API Patterns**

- REST/GraphQL/gRPC conventions
- GraphQL specifics if used (resolvers, dataloaders, schema-first vs code-first)
- Auth (JWT, session, token, OAuth2 — which library)
- Permission/authorization structure
- Pagination approach + response format

**Async & Performance**

- Background tasks (Celery, Bull, goroutines, async tasks)
- Caching (Redis, memcached, in-memory)
- Query optimization patterns
- WebSocket/real-time patterns (channels, socket.io, SSE)
- Async/concurrent patterns

**Database**

- Type (PostgreSQL, MySQL, MongoDB, etc.)
- Migration approach
- Seed data/fixtures
- Multi-tenancy patterns

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_backend.md`:

1. **Architecture Patterns** — how this project structures backend code
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected framework
7. **API conventions** — endpoint structure, auth flow, error responses

---

## PHASE 3: BEST PRACTICES

Integrate for the detected language/framework:

- Clean architecture principles relevant to this project
- REST API design (resource naming, HTTP methods, status codes)
- GraphQL best practices (N+1 via dataloaders, schema design, pagination)
- Database query optimization (N+1 prevention, indexing, explain plans)
- Transaction and data integrity patterns
- Auth/authorization best practices
- Error handling hierarchy
- Testing discipline (unit vs integration, what to mock)
- Security: OWASP top 10 for the detected framework
- Logging and observability patterns
- 12-factor app principles where applicable
- WebSocket/real-time best practices (connection lifecycle, reconnection)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY backend task — API development, model design, serializer/schema questions, database queries, authentication, background tasks, testing, migrations, code review, performance, deployment, WebSocket/real-time.

**`allowed-tools`**: `Read Edit Write Bash(python:*) Bash(pip:*) Glob Grep` (adjust `python/pip` for detected language: `go`, `cargo`, `npm`, `mvn`, etc.)

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (frontend, mobile, infra)
3. **Architecture** — project structure diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Import order, transaction patterns, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with backend-specific detection signals (e.g., "traceback" for Diagnostic, "another endpoint" for Efficient, "what is this mixin" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, memory bridge

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/api-patterns.md` — endpoint patterns, request/response examples (ALL code examples go here)
- `references/code-style.md` — import order, transaction patterns, formatting with full examples
- `references/security-checklist.md` — per-ViewSet, per-Serializer, per-Model verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/model-template.{{ext}}` — copy-paste model/schema template (use detected language extension)
- `references/test-patterns.md` — testing patterns with full examples
- `references/common-issues.md` — troubleshooting common backend pitfalls
- `assets/env-example` — environment variable template
- `scripts/validate-backend.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                              | Tools                          | Spawn When                                                      |
| ---------------- | ------------------------------------------------- | ------------------------------ | --------------------------------------------------------------- |
| code-reviewer    | Read-only code analysis against SKILL.md patterns | Read Glob Grep                 | PR review, code audit, architecture compliance check            |
| test-writer      | Test generation following project conventions     | Read Edit Write Glob Grep Bash | "write tests for X", new endpoint/model creation, coverage gaps |
| security-scanner | OWASP security audit for backend code             | Read Glob Grep                 | Security review, pre-deploy check, dependency audit             |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only backend code analysis agent
- `agents/test-writer.md` — test generation agent
- `agents/security-scanner.md` — OWASP security audit agent
