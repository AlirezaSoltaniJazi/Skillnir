# API Design Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are API-design-specific overrides.

```
ROLE:     Senior API architect analyzing API contracts and schemas
GOAL:     Generate a production-grade API design skill directory
SCOPE:    API contracts, schemas, specs, documentation only — ignore server implementation, frontend consumers
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — API Design Only

Ignore server implementation, frontend consumers, and infrastructure code. Scan for:

**API Style & Protocol**

- API paradigm (REST, GraphQL, gRPC, WebSocket, event-driven, hybrid)
- Specification format (OpenAPI/Swagger, Protobuf, GraphQL SDL, AsyncAPI, JSON Schema)
- Schema approach (schema-first vs code-first)
- Spec file locations and organization
- API gateway or proxy layer (Kong, Envoy, API Gateway, etc.)

**Versioning & Compatibility**

- Versioning strategy (URL path, header, query param, content negotiation)
- Version lifecycle policy (deprecation timeline, sunset headers)
- Backward compatibility rules (additive-only, field deprecation, migration guides)
- Breaking change detection tooling (oasdiff, buf breaking, graphql-inspector, etc.)
- Changelog and migration guide conventions

**Contract Design**

- Resource naming conventions (plural nouns, kebab-case, camelCase)
- HTTP method usage (idempotency, safe methods, PATCH vs PUT)
- Status code conventions (success, client error, server error)
- Error response format (RFC 7807, custom envelope, GraphQL errors)
- Pagination strategy (cursor, offset, page-number, Link headers)
- Filtering and sorting conventions (query params, field selection, sparse fieldsets)
- Request/response envelope structure (data wrapping, metadata, links)

**Authentication & Authorization in Contracts**

- Auth scheme declaration (Bearer, API key, OAuth2 flows in spec)
- Scope and permission modeling in specs
- Security scheme definitions (OpenAPI securitySchemes, gRPC interceptors)

**GraphQL-Specific** (if applicable)

- Schema organization (modular vs monolithic, federation)
- Query complexity limits and depth restrictions
- Resolver pattern documentation
- Subscription design
- Custom directive usage
- Input type conventions

**gRPC/Protobuf-Specific** (if applicable)

- Proto file organization and package naming
- Service method patterns (unary, server-streaming, client-streaming, bidirectional)
- Message design (field numbering, reserved fields, oneof usage)
- buf.yaml / buf.gen.yaml configuration
- Code generation pipeline

**Rate Limiting & Quotas**

- Rate limit headers (X-RateLimit-Limit, Retry-After, RateLimit draft standard)
- Quota tiers and plan-based limits
- Throttling response format (429 body structure)
- Rate limit documentation for consumers

**Documentation & Developer Experience**

- Documentation tooling (Redoc, Swagger UI, Stoplight, GraphiQL, gRPC reflection)
- Example request/response inclusion
- SDK generation (openapi-generator, buf generate, graphql-codegen)
- Developer portal structure
- Postman/Insomnia collection maintenance

**Contract Testing**

- Contract testing tools (Pact, Dredd, Schemathesis, Spectral, buf lint)
- Linting rules and custom rulesets
- CI integration for spec validation
- Mock server generation

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_api_design.md`:

1. **API Architecture Patterns** — how this project structures API contracts and schemas
2. **Naming Conventions** — resource naming, field naming, endpoint structure
3. **Spec Management** — tooling, validation, generation workflow
4. **Things to ALWAYS do** — non-negotiable API design patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Protocol-specific wisdom** — patterns unique to the detected API paradigm (REST/GraphQL/gRPC)
7. **Versioning conventions** — compatibility rules, deprecation workflow, changelog practices

---

## PHASE 3: BEST PRACTICES

Integrate for the detected API paradigm and tooling:

- RESTful design principles (resource-oriented, HATEOAS where appropriate, consistent naming)
- GraphQL schema design (schema-first, minimal resolver logic, pagination via Relay spec)
- Protobuf/gRPC design (forward-compatible messages, reserved fields, style guide compliance)
- API versioning (choose one strategy, document lifecycle, automate breaking change detection)
- Error design (consistent error format, actionable messages, error codes catalog)
- Pagination design (cursor-based for large datasets, consistent across endpoints)
- Filtering and sorting (standard query param patterns, avoid over-fetching)
- Authentication and authorization modeling (declare in spec, least-privilege scopes)
- Rate limiting transparency (document limits, return headers, graceful degradation)
- Backward compatibility (additive changes only, deprecation before removal, migration guides)
- Contract testing discipline (lint in CI, test against spec, detect breaking changes before merge)
- Documentation quality (examples for every endpoint, error catalog, SDK usage guides)
- Security: OWASP API Security Top 10, input validation in spec, classify by severity (Critical/High/Medium/Low)
- Rollback strategy (spec version rollback, consumer migration support, feature flags for API changes)
- Cloud cost awareness (payload size optimization, batch endpoints, caching headers to reduce calls)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY API design task — OpenAPI spec creation, Protobuf schema design, GraphQL schema design, API versioning, contract testing, endpoint naming, pagination design, error response format, rate limiting, API documentation, breaking change review.

**`allowed-tools`**: `Read Edit Write Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, frontend, database)
3. **Architecture** — API contract structure diagram, spec file organization, validation pipeline
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full spec examples in references/ only
5. **Code Style** — rules table only. Naming conventions, spec formatting, schema structure details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-endpoint, per-schema verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with API-design-specific detection signals (e.g., "breaking change" for Diagnostic, "add an endpoint" for Efficient, "what is content negotiation" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/api-style-guide.md` — naming conventions, pagination, filtering, error format with full examples
- `references/code-style.md` — spec formatting, schema structure, field naming rules with full examples
- `references/security-checklist.md` — per-endpoint, per-schema, per-auth-flow verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/spec-template.yaml` — copy-paste OpenAPI/Protobuf/GraphQL schema template
- `references/test-patterns.md` — contract testing patterns with full examples
- `references/common-issues.md` — troubleshooting common API design pitfalls (breaking changes, inconsistent naming, over-fetching)
- `assets/env-example` — API configuration environment variable template
- `scripts/validate-api-design.sh` — spec linting + breaking change detection script

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                    | Role                                                  | Tools                     | Spawn When                                                    |
| ------------------------ | ----------------------------------------------------- | ------------------------- | ------------------------------------------------------------- |
| contract-validator       | Read-only spec validation against SKILL.md patterns   | Read Glob Grep            | Spec review, naming audit, consistency check across endpoints |
| breaking-change-detector | Backward compatibility analysis between spec versions | Read Glob Grep            | Pre-merge spec review, version bump, deprecation planning     |
| doc-generator            | API documentation generation and maintenance          | Read Edit Write Glob Grep | New endpoint addition, spec update, documentation refresh     |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/contract-validator.md` — read-only API spec validation agent
- `agents/breaking-change-detector.md` — backward compatibility analysis agent
- `agents/doc-generator.md` — API documentation generation agent
