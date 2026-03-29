# Performance Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are performance-specific overrides.

```
ROLE:     Senior performance engineer analyzing a codebase for optimization opportunities
GOAL:     Generate a production-grade performance skill directory
SCOPE:    Cross-cutting performance analysis — examine all code layers for bottlenecks and optimization opportunities
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Performance Focus

Examine all code layers for performance-relevant patterns. Scan for:

**Language & Runtime**

- Primary language(s) and runtime(s) (Node.js, Python, Go, Java, Rust, etc.)
- Runtime configuration (heap size, GC tuning, thread pools, worker counts)
- Language-specific profiling tools available (pprof, cProfile, perf, async-profiler, Chrome DevTools)
- Hot path identification (high-frequency code paths, request handlers, event loops)
- Compilation/build optimization settings (release mode, LTO, PGO)

**Profiling Infrastructure**

- CPU profiling integration (pprof, perf, async-profiler, py-spy, dotTrace)
- Memory profiling tools (heap snapshots, allocation tracking, valgrind, memray)
- I/O profiling (disk I/O, network I/O, syscall tracing, strace/dtrace)
- Continuous profiling setup (Pyroscope, Parca, Datadog Continuous Profiler)
- APM integration (New Relic, Datadog, Elastic APM, Jaeger, OpenTelemetry)

**Database Performance**

- Query patterns (ORM-generated vs raw, prepared statements, batch operations)
- Slow query logging configuration
- Index usage (existing indexes, missing indexes, unused indexes)
- Connection pooling (pool size, idle connections, timeout settings)
- N+1 query patterns and mitigation (eager loading, dataloaders, joins)
- Migration performance impact assessment
- Read replica / write splitting patterns

**Caching**

- Cache layers (HTTP cache headers, CDN configuration, reverse proxy cache)
- Application cache (Redis, Memcached, in-memory LRU, local cache)
- Database query cache (query result caching, materialized views)
- Cache invalidation strategy (TTL, event-driven, manual)
- Cache hit ratio monitoring
- Serialization format for cached data (JSON, MessagePack, protobuf)

**Network & Transport**

- HTTP version (HTTP/1.1, HTTP/2, HTTP/3)
- Compression (gzip, Brotli, zstd — response compression, asset compression)
- Connection pooling (HTTP keep-alive, database connections, gRPC channels)
- DNS resolution and optimization
- TLS configuration (session resumption, OCSP stapling)
- API payload optimization (field selection, pagination, sparse fieldsets)

**Frontend Performance**

- Bundle size and splitting strategy (webpack, Vite, esbuild, Rollup)
- Code splitting and lazy loading patterns
- Asset optimization (image formats, compression, responsive images)
- Web Vitals baseline (LCP, FID/INP, CLS measurements)
- Critical rendering path optimization (above-the-fold, preload, prefetch)
- Service worker and offline caching strategies
- Third-party script impact assessment

**Load Testing**

- Existing load test setup (k6, Locust, Artillery, JMeter, Gatling)
- Test scenarios and traffic patterns
- Performance baselines and SLOs
- Staging/performance environment configuration
- Synthetic monitoring setup

**Memory Management**

- Allocation patterns (object pooling, arena allocation, stack vs heap)
- Garbage collection tuning and monitoring
- Memory leak detection tooling
- Large object handling (streaming, chunking, memory-mapped files)
- Buffer management and reuse patterns

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_performance.md`:

1. **Architecture Patterns** — how this project's architecture affects performance characteristics
2. **Coding Conventions** — performance-relevant style and optimization conventions
3. **Package Patterns** — key performance-related packages and their usage
4. **Things to ALWAYS do** — non-negotiable performance practices observed
5. **Things to NEVER do** — performance anti-patterns explicitly avoided
6. **Bottleneck profile** — identified or likely bottlenecks by layer (CPU, memory, I/O, network)
7. **Monitoring conventions** — metrics, alerting, and observability patterns for performance

---

## PHASE 3: BEST PRACTICES

Integrate for the detected language(s) and framework(s):

- Profiling before optimizing (measure first, optimize second — no premature optimization)
- Database query optimization (EXPLAIN plans, index design, N+1 elimination, batch operations)
- Connection pooling configuration (database, HTTP, gRPC — sizing, timeouts, health checks)
- Caching strategy hierarchy (L1 in-memory, L2 distributed, L3 CDN — when to use each)
- Cache invalidation correctness (eventual consistency, stampede prevention, warm-up)
- Memory allocation reduction (object reuse, pooling, streaming, arena patterns)
- Garbage collection awareness (GC pause reduction, allocation rate, generational GC tuning)
- Bundle optimization (tree shaking, code splitting, dynamic imports, compression)
- Web Vitals optimization (LCP: resource priority, FID/INP: main thread work, CLS: layout stability)
- Load testing discipline (realistic scenarios, ramp-up, soak tests, chaos engineering)
- Benchmarking rigor (statistical significance, warm-up, environment isolation, regression detection)
- Network optimization (compression, HTTP/2 multiplexing, connection reuse, payload minimization)
- Async and concurrent patterns (non-blocking I/O, parallelism, backpressure)
- Security vs performance tradeoffs (rate limiting overhead, encryption cost, audit logging impact)
- Cost-performance tradeoffs (right-sizing, autoscaling, spot instances, reserved capacity)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY performance task — profiling, benchmarking, load testing, query optimization, caching, bundle analysis, memory leaks, slow endpoints, Web Vitals, latency reduction, throughput improvement, resource utilization.

**`allowed-tools`**: `Read Glob Grep Bash`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend for logic changes, frontend for UI changes, infrastructure for provisioning)
3. **Architecture** — performance-relevant architecture diagram, bottleneck zones, data flow with latency annotations
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — performance-oriented rules table only. Profiling setup, benchmark templates in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list for performance tests + link to references/test-patterns.md
8. **Performance Rules** — bullet list with priority tiers (Critical/High/Medium/Low impact)
9. **Security** — summary of security-performance tradeoffs + link to references/security-checklist.md
10. **Anti-Patterns** — what NOT to do (premature optimization, micro-benchmarking without context, caching without invalidation, etc.)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with performance-specific detection signals (e.g., "endpoint is slow" for Diagnostic, "optimize this query" for Efficient, "why is this allocation expensive" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/profiling-guide.md` — language-specific profiling tool setup and interpretation (ALL code examples go here)
- `references/code-style.md` — performance-oriented coding patterns, benchmark templates with full examples
- `references/security-checklist.md` — security-performance tradeoff verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/caching-patterns.md` — cache layer design, invalidation strategies, stampede prevention with full examples
- `references/test-patterns.md` — load test scenarios, benchmark patterns, regression detection with full examples
- `references/common-issues.md` — troubleshooting common performance pitfalls (memory leaks, N+1 queries, GC pressure)
- `assets/k6-template.js` — load test scenario template
- `scripts/validate-performance.sh` — performance baseline and regression checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent               | Role                                             | Tools                     | Spawn When                                                          |
| ------------------- | ------------------------------------------------ | ------------------------- | ------------------------------------------------------------------- |
| profiler            | Run profiling tools and collect performance data | Read Glob Grep Bash       | Performance investigation, CPU/memory analysis, hot path detection  |
| bottleneck-analyzer | Identify performance anti-patterns in code       | Read Glob Grep            | Code review for performance, N+1 detection, allocation analysis     |
| load-test-designer  | Create and configure load test scenarios         | Read Edit Write Glob Grep | "create load test for X", new endpoint load testing, SLO validation |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/profiler.md` — profiling tool execution and data collection agent
- `agents/bottleneck-analyzer.md` — performance anti-pattern detection agent
- `agents/load-test-designer.md` — load test scenario creation agent
