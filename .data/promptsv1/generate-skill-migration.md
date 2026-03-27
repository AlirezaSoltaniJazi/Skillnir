# Migration Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are migration-specific overrides.

```
ROLE:     Senior migration engineer planning and executing codebase transformations
GOAL:     Generate a production-grade migration skill directory
SCOPE:    Migration plans, compatibility analysis, incremental transformation strategies — NOT day-to-day feature development
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Migration Only

Ignore unrelated feature code and static assets. Scan for:

**Source & Target Versions**

- Current language version (Python 3.10, Java 11, Node 18, etc.)
- Target language version (Python 3.13, Java 21, Node 22, etc.)
- Current framework version (Django 4, React 17, Angular 15, Spring 5, etc.)
- Target framework version (Django 5, React 18, Angular 17, Spring 6, etc.)
- Runtime and toolchain versions (JVM, V8, CPython, GraalVM)

**Dependency Landscape**

- Package manager + lock file (requirements.txt, pyproject.toml, package-lock.json, go.sum, pom.xml, Cargo.lock)
- Major dependency versions and known breaking changes
- Transitive dependency depth and pinning strategy
- Deprecated API usage across dependencies
- Version constraint ranges vs exact pins

**Architecture**

- Project structure (monolith vs modular vs microservices)
- Inter-service communication patterns (REST, gRPC, message queues, shared DBs)
- Shared library / internal package dependencies
- Build system and CI/CD pipeline configuration
- Deployment topology (single deploy, rolling, blue-green, canary)
- Feature flag infrastructure (LaunchDarkly, Unleash, custom, none)

**Data Layer**

- Database type and version (PostgreSQL 14→16, MySQL 5.7→8, MongoDB 5→7)
- ORM / query builder version and migration tooling (Alembic, Flyway, Knex, ActiveRecord)
- Existing migration history (count, complexity, custom SQL)
- Schema change patterns (additive, destructive, rename-heavy)
- Data volume estimates (row counts, table sizes, blob storage)
- Seed data and fixture management

**Code Patterns**

- Deprecated language features in use (e.g., `typing.Optional` pre-3.10, `javax` pre-Jakarta)
- Framework-specific deprecated APIs (removed middleware, changed config keys)
- Type system usage (partial, full, none — affects migration tooling)
- Test coverage and test framework version
- Async/sync boundary patterns (relevant for sync→async migrations)

**Compatibility Constraints**

- API contracts (OpenAPI specs, protobuf definitions, GraphQL schemas)
- Client SDK compatibility requirements
- Third-party integration version constraints
- Compliance / regulatory freeze windows
- Multi-environment parity (dev, staging, prod version alignment)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_migration.md`:

1. **Migration Scope** — what is being migrated, from/to versions, estimated blast radius
2. **Breaking Change Inventory** — categorized list of known breaking changes affecting this codebase
3. **Dependency Graph** — critical path dependencies that must migrate in order
4. **Things to ALWAYS do** — non-negotiable migration patterns observed (e.g., backward-compatible schema changes first)
5. **Things to NEVER do** — dangerous patterns explicitly avoided (e.g., big-bang migrations, untested rollbacks)
6. **Incremental Strategy** — phased migration plan with rollback points
7. **Compatibility Matrix** — version compatibility table for key components

---

## PHASE 3: BEST PRACTICES

Integrate for the detected language/framework migration:

- Strangler fig pattern for incremental migration (Priority 1)
- Backward-compatible database migrations — expand/contract pattern (Priority 1)
- Feature flag gating for migration stages (Priority 1)
- Dual-write / dual-read patterns for data migration (Priority 2)
- Codemods and automated refactoring tools (jscodeshift, libcst, OpenRewrite, Rector) (Priority 2)
- Deprecation warning enforcement before removal (Priority 2)
- Compatibility shim layers for gradual API transition (Priority 3)
- Canary deployment for migrated components (Priority 3)
- Rollback strategy at every phase (database, code, config) (Priority 1)
- Integration test gates between migration phases (Priority 1)
- Performance benchmarking before/after migration (Priority 3)
- Security audit of new version dependencies (Priority 2)
- Documentation of migration decisions (ADRs) (Priority 3)
- Data backfill strategies (batch processing, background jobs, zero-downtime) (Priority 2)
- Monitoring and alerting during migration rollout (Priority 1)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY migration task — framework upgrades, language version bumps, architecture refactors, dependency upgrades, data migrations, schema changes, API versioning, monolith decomposition, sync-to-async conversion, feature flag rollout, compatibility analysis, rollback planning.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep`

**Body sections** (all required in SKILL.md):

| # | Section | Content |
| -- | ------- | ------- |
| 1 | **When to Use** | 4-6 trigger conditions (framework upgrade, language bump, architecture refactor, data migration, dependency major version, deprecation cleanup) |
| 2 | **Do NOT Use** | Cross-references to sibling skills (backend for new features, infra for provisioning, testing for test-only work) |
| 3 | **Migration Scope** | Source/target version matrix, affected components diagram, blast radius estimate |
| 4 | **Breaking Change Inventory** | Summary table only (component, breaking change, severity, mitigation). Full details in references/ only |
| 5 | **Incremental Strategy** | Phased migration plan with rollback checkpoints, no code blocks |
| 6 | **Compatibility Matrix** | Version compatibility table (component, min version, max version, notes) |
| 7 | **Data Migration Patterns** | Rules list + link to references/data-migration-patterns.md |
| 8 | **Rollback Procedures** | Numbered step lists per phase, no code examples |
| 9 | **Feature Flag Strategy** | Flag naming, lifecycle, cleanup rules + link to references/feature-flag-guide.md |
| 10 | **Anti-Patterns** | What NOT to do (with why) — big-bang migrations, skipping versions, untested rollbacks |
| 11 | **References** | Key files, docs, resources |
| 12 | **Adaptive Interaction Protocols** | Interaction modes with migration-specific detection signals (e.g., "upgrade failed" for Diagnostic, "migrate next component" for Efficient, "why did this API change" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md |

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/breaking-changes.md` — full breaking change catalog with code examples and migration paths
- `references/data-migration-patterns.md` — expand/contract, dual-write, backfill strategies with full examples
- `references/feature-flag-guide.md` — flag naming, lifecycle management, cleanup procedures
- `references/compatibility-matrix.md` — detailed version compatibility table with test results
- `references/rollback-playbook.md` — step-by-step rollback procedures per migration phase
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/codemod-recipes.md` — automated refactoring scripts and patterns
- `references/common-issues.md` — troubleshooting common migration pitfalls
- `assets/migration-checklist.md` — pre/post migration verification template
- `scripts/validate-migration.sh` — compatibility + migration completeness checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                  | Role                                                        | Tools                | Spawn When                                                         |
| ---------------------- | ----------------------------------------------------------- | -------------------- | ------------------------------------------------------------------ |
| compatibility-analyzer | Checks breaking changes against codebase usage              | Read Glob Grep Bash  | Version upgrade planned, dependency bump, framework migration      |
| risk-assessor          | Identifies high-risk areas and migration ordering            | Read Glob Grep       | Migration planning, blast radius analysis, rollback risk review    |
| migration-validator    | Verifies migration completeness and no leftover deprecated code | Read Glob Grep Bash  | Post-migration check, phase gate verification, cleanup audit       |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/compatibility-analyzer.md` — breaking change detection and compatibility verification agent
- `agents/risk-assessor.md` — migration risk analysis and ordering agent
- `agents/migration-validator.md` — migration completeness and cleanup verification agent
