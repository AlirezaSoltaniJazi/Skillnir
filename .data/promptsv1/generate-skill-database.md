# Database Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are database-specific overrides.

```
ROLE:     Senior database engineer analyzing a production data layer
GOAL:     Generate a production-grade database skill directory
SCOPE:    Database schema, queries, migrations, ORM code only — ignore application logic, API layer, frontend
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Database Only

Ignore application logic, API controllers, and frontend code. Scan for:

**Database Engine & Connectivity**

- Database type (PostgreSQL, MySQL, MariaDB, MongoDB, SQLite, etc.)
- Database driver / connector library
- Connection pooling setup (PgBouncer, HikariCP, SQLAlchemy pool, Prisma pool, etc.)
- Connection string management (env vars, secrets manager, vault)
- Read replicas / write-primary topology

**Schema & Data Modeling**

- Schema definition approach (ORM models, raw DDL files, migration-generated)
- Normalization level observed (1NF–BCNF, deliberate denormalization)
- Naming conventions (snake_case, camelCase, plural vs singular tables)
- Primary key strategy (serial, UUID, ULID, composite)
- Foreign key and relationship patterns (one-to-many, many-to-many, polymorphic)
- Soft delete vs hard delete patterns
- Audit columns (created_at, updated_at, deleted_at, created_by)
- Enum handling (DB-level enum, check constraint, application-level)

**Migrations**

- Migration tool (Alembic, Django migrations, Flyway, Liquibase, Knex, Prisma Migrate, goose, etc.)
- Migration naming convention
- Zero-downtime migration patterns (column add before use, backfill strategy)
- Rollback support (reversible migrations, manual rollback scripts)
- Data migrations vs schema migrations separation
- Migration testing approach
- Seed data / fixture management

**Query Patterns**

- ORM usage (SQLAlchemy, Django ORM, Hibernate, ActiveRecord, Prisma, GORM, etc.)
- Raw SQL usage (when and where)
- Query builder patterns
- N+1 prevention (select_related, joinedload, eager loading, dataloaders)
- Pagination approach (OFFSET/LIMIT, cursor-based, keyset)
- Full-text search (tsvector, Elasticsearch integration, LIKE patterns)
- Aggregation and reporting queries
- Stored procedures / functions / triggers

**Indexing & Performance**

- Index strategy (B-tree, GIN, GiST, partial, covering)
- EXPLAIN plan usage in reviews or CI
- Slow query logging / monitoring
- Query caching (materialized views, application cache, Redis)
- Partitioning strategy (range, hash, list)
- Vacuum / maintenance schedules (PostgreSQL)

**Data Integrity**

- Constraint usage (NOT NULL, UNIQUE, CHECK, EXCLUDE)
- Transaction patterns (explicit transactions, savepoints, nested)
- Isolation level configuration (READ COMMITTED, SERIALIZABLE, etc.)
- Optimistic vs pessimistic locking
- Idempotency patterns for data operations

**Multi-Tenancy**

- Tenancy model (shared schema, schema-per-tenant, database-per-tenant, row-level)
- Tenant isolation enforcement (RLS, middleware, query filters)
- Cross-tenant query prevention

**Backup & Recovery**

- Backup strategy (pg_dump, mysqldump, mongodump, WAL archiving, snapshots)
- Point-in-time recovery setup
- Backup verification / restore testing
- Data retention policies

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_database.md`:

1. **Schema Patterns** — how this project structures tables, relationships, and naming
2. **Migration Conventions** — migration workflow, naming, safety practices
3. **Query Patterns** — ORM usage, raw SQL, optimization techniques observed
4. **Things to ALWAYS do** — non-negotiable data integrity patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Engine-specific wisdom** — patterns unique to the detected database engine
7. **Performance conventions** — indexing strategy, caching, query optimization rules

---

## PHASE 3: BEST PRACTICES

Integrate for the detected database engine and ORM:

- Schema design principles (normalization, deliberate denormalization with justification)
- Migration safety (zero-downtime migrations, backward-compatible changes, rollback plans)
- Query optimization (EXPLAIN plan analysis, index selection, N+1 prevention)
- Transaction management (appropriate isolation levels, transaction scope minimization)
- Data integrity (constraint enforcement at DB level, not just application level)
- Connection pooling (pool sizing, connection lifecycle, leak prevention)
- Indexing discipline (index what you query, composite index column order, covering indexes)
- Multi-tenancy isolation (row-level security, query scoping, data leak prevention)
- Backup and recovery (automated backups, restore testing, point-in-time recovery)
- Security: SQL injection prevention, least-privilege DB roles, encrypt sensitive columns, classify by severity (Critical/High/Medium/Low)
- Monitoring and observability (slow query logs, connection pool metrics, replication lag)
- Data lifecycle management (archival, purging, GDPR/data retention compliance)
- Rollback strategy and data recovery (migration rollback, data backfill verification, backup restore drills)
- Cloud cost awareness (right-sizing instances, read replica usage, storage optimization, reserved capacity)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY database task — schema design, migration creation, query optimization, data modeling, indexing, backup strategy, ORM configuration, raw SQL review, transaction management, multi-tenancy, connection pooling, data integrity.

**`allowed-tools`**: `Read Edit Write Bash(psql:*) Bash(mysql:*) Bash(mongosh:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, infra, security)
3. **Architecture** — database topology diagram, schema overview, migration flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Naming conventions, SQL formatting, ORM usage details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-table, per-query verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with database-specific detection signals (e.g., "slow query" for Diagnostic, "add a column" for Efficient, "what is this index" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/schema-patterns.md` — table design, relationship patterns, naming conventions with full examples
- `references/code-style.md` — SQL formatting, ORM usage, naming rules with full examples
- `references/security-checklist.md` — per-table, per-query, per-migration verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/migration-template.sql` — copy-paste migration template with rollback section
- `references/test-patterns.md` — database testing patterns with full examples
- `references/common-issues.md` — troubleshooting common database pitfalls (deadlocks, N+1, connection exhaustion)
- `assets/env-example` — database connection environment variable template
- `scripts/validate-database.sh` — naming + schema convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent             | Role                                                  | Tools              | Spawn When                                                          |
| ----------------- | ----------------------------------------------------- | ------------------ | ------------------------------------------------------------------- |
| schema-reviewer   | Read-only schema analysis against SKILL.md patterns   | Read Glob Grep     | Schema review, data model audit, normalization compliance check     |
| migration-auditor | Migration safety and rollback verification            | Read Glob Grep     | New migration review, pre-deploy migration check, rollback planning |
| query-optimizer   | Query performance analysis and optimization           | Read Glob Grep Bash | Slow query investigation, EXPLAIN plan review, index recommendations |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/schema-reviewer.md` — read-only schema and data model analysis agent
- `agents/migration-auditor.md` — migration safety and rollback audit agent
- `agents/query-optimizer.md` — query performance analysis agent
