# Go Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Go-specific overrides.

```
ROLE:     Senior Go engineer analyzing a production Go codebase
GOAL:     Generate a production-grade Go skill directory
SCOPE:    Go source code only — ignore non-Go code, infrastructure, frontend
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Go Only

Ignore frontend, infrastructure, and non-Go code. Scan for:

**Module & Dependencies**

- Go version (go.mod `go` directive)
- Module path and namespace conventions
- Dependency management (go.mod, go.sum, vendoring via `vendor/`)
- Version selection strategy (minimum version selection, pinning, replace directives)
- Key dependencies and usage patterns (standard library preference vs third-party)

**Project Layout**

- Directory structure (`cmd/`, `internal/`, `pkg/`, `api/`, `web/`)
- Entry points (main packages under `cmd/`)
- Internal vs exported packages (`internal/` boundary enforcement)
- Build tags and platform-specific code
- Makefile / Taskfile / Mage build automation

**Language Idioms**

- Error handling patterns (`errors.Is`, `errors.As`, `fmt.Errorf` with `%w`, sentinel errors, custom error types)
- Interface design (small interfaces, accept interfaces return structs, embedding)
- Struct embedding patterns and composition over inheritance
- Generics usage (type constraints, type inference, when generics vs interfaces)
- Value vs pointer receiver conventions
- `context.Context` propagation patterns
- `init()` function usage (avoided or embraced)

**Concurrency**

- Goroutine patterns (fan-out/fan-in, worker pools, pipeline)
- Channel usage (buffered vs unbuffered, directional channels, `select` statements)
- Context propagation and cancellation (`context.WithCancel`, `context.WithTimeout`)
- `sync` primitives (`sync.Mutex`, `sync.RWMutex`, `sync.WaitGroup`, `sync.Once`, `sync.Pool`)
- `errgroup` and structured concurrency patterns
- Race condition prevention strategies

**Code Quality**

- Linting (`golangci-lint` config, enabled linters)
- Code formatting (`gofmt`, `goimports`, `gofumpt`)
- Documentation style (GoDoc conventions, package-level comments)
- Naming conventions (MixedCaps, acronyms, interface `-er` suffix)
- Constants and `iota` enum patterns
- Config management (env vars, Viper, `envconfig`, flags)

**Testing**

- Testing framework (`testing` stdlib, testify, gomock, mockgen)
- Table-driven test patterns
- Test structure (unit/integration split, `_test.go` conventions, `testdata/`)
- Test helpers and `testing.TB` patterns
- `httptest` usage for HTTP handler testing
- Race detector usage (`-race` flag)
- Benchmark tests (`Benchmark*` functions)
- Fuzz tests (`Fuzz*` functions)
- Coverage tooling and thresholds

**API & Networking**

- HTTP framework (net/http, Gin, Echo, Chi, Fiber, gRPC)
- Router/handler patterns (HandlerFunc, middleware chaining)
- Request/response encoding (JSON, protobuf, custom marshaling)
- Auth patterns (JWT, OAuth2, middleware-based)
- gRPC specifics if used (proto definitions, interceptors, streaming)

**Performance**

- `pprof` profiling integration
- Benchmark patterns and allocation tracking
- `sync.Pool` usage for object reuse
- Allocation-aware coding (stack vs heap, escape analysis)
- Connection pooling (database, HTTP clients)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_go.md`:

1. **Architecture Patterns** — how this project structures Go code
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Go-specific wisdom** — patterns unique to Go idioms in this codebase
7. **Concurrency conventions** — goroutine management, channel usage, synchronization rules

---

## PHASE 3: BEST PRACTICES

Integrate for the detected Go version and frameworks:

- Effective Go principles relevant to this project
- Error handling hierarchy (sentinel errors, custom types, wrapping with `%w`)
- Interface design (small interfaces, standard library interfaces, embedding)
- Goroutine lifecycle management (always know when a goroutine exits)
- Context propagation (first parameter, cancellation, timeouts, values)
- Resource cleanup (`defer`, `Close()`, leak prevention)
- Table-driven tests as default pattern
- Race detector in CI (`go test -race ./...`)
- Benchmark discipline (allocation counting, `b.ReportAllocs()`)
- Generics best practices (use when type-safe containers needed, avoid when interfaces suffice)
- Common anti-patterns (bare goroutines, ignoring errors, `interface{}` overuse, premature `sync.Pool`, `init()` side effects)
- Security: input validation, SQL injection prevention, TLS configuration, secrets management, classify by severity (Critical/High/Medium/Low)
- Dependency hygiene (minimize third-party, prefer stdlib, audit with `govulncheck`)
- Memory management (understanding escape analysis, reducing allocations, `sync.Pool` for hot paths)
- Observability (structured logging with `slog`, OpenTelemetry, metrics)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Go task — writing Go code, error handling, concurrency, testing, benchmarking, module management, code review, profiling, gRPC, HTTP handlers, interface design, generics.

**`allowed-tools`**: `Read Edit Write Bash(go:*) Bash(golangci-lint:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (frontend, infrastructure, database)
3. **Architecture** — project structure diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Naming, formatting, import grouping details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with Go-specific detection signals (e.g., "panic stack trace" for Diagnostic, "add an endpoint" for Efficient, "what does this interface do" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/api-patterns.md` — handler patterns, middleware examples, request/response encoding (ALL code examples go here)
- `references/code-style.md` — naming conventions, import grouping, formatting rules with full examples
- `references/security-checklist.md` — per-handler, per-middleware, per-package verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/concurrency-patterns.md` — goroutine lifecycle, channel patterns, sync primitives with full examples
- `references/test-patterns.md` — table-driven tests, benchmarks, fuzz tests with full examples
- `references/common-issues.md` — troubleshooting common Go pitfalls (nil pointer, goroutine leaks, race conditions)
- `assets/env-example` — environment variable template
- `scripts/validate-go.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent         | Role                                              | Tools                          | Spawn When                                                       |
| ------------- | ------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| code-reviewer | Read-only code analysis against SKILL.md patterns | Read Glob Grep                 | PR review, code audit, architecture compliance check             |
| test-writer   | Test generation following project conventions     | Read Edit Write Glob Grep Bash | "write tests for X", new handler/service creation, coverage gaps |
| race-detector | Concurrency safety analysis and race detection    | Read Glob Grep Bash            | Concurrency review, goroutine audit, pre-deploy race check       |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/code-reviewer.md` — read-only Go code analysis agent
- `agents/test-writer.md` — test generation agent
- `agents/race-detector.md` — concurrency safety and race detection agent
