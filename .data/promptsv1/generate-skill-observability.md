# Observability Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are observability-specific overrides.

```
ROLE:     Senior observability engineer analyzing application instrumentation
GOAL:     Generate a production-grade observability skill directory
SCOPE:    Application-level instrumentation, tracing, metrics, logging only — ignore infrastructure provisioning (covered by infra skill)
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Observability Only

Ignore infrastructure provisioning, frontend UI, and mobile code. Scan for:

**Instrumentation Framework**

- Tracing library (OpenTelemetry, Jaeger client, Zipkin, AWS X-Ray SDK, Datadog APM)
- Metrics library (OpenTelemetry Metrics, Prometheus client, Micrometer, StatsD)
- Logging library (structlog, slog, log4j2, Winston, Serilog, zerolog)
- SDK configuration (auto-instrumentation vs manual, exporter setup)
- Key dependencies and version pinning
- Language/runtime (Python, Go, Java, Node.js, .NET, Rust)

**Distributed Tracing**

- Context propagation (W3C TraceContext, B3, baggage)
- Span design (naming conventions, attribute standards, span kind usage)
- Sampling strategy (head-based, tail-based, rate-based, custom sampler)
- Trace exporters (OTLP, Jaeger, Zipkin, vendor-specific)
- Cross-service correlation (service mesh integration, message queue tracing)
- Span enrichment patterns (custom attributes, events, links)

**Metrics Design**

- Metric types in use (counters, gauges, histograms, summaries)
- Naming conventions (dot notation, underscore, namespace prefixes)
- RED method signals (Rate, Errors, Duration per service)
- USE method signals (Utilization, Saturation, Errors per resource)
- Custom business metrics (conversion, latency percentiles, queue depth)
- Cardinality management (label/attribute constraints, pre-aggregation)
- Metric exporters (Prometheus scrape, OTLP push, StatsD)

**Structured Logging**

- Log format (JSON, logfmt, key-value, plain text)
- Correlation ID propagation (trace ID injection, request ID threading)
- Log level strategy (when to use each level, dynamic level adjustment)
- Context enrichment (user ID, tenant ID, request metadata)
- Sensitive data handling (PII redaction, field masking)
- Log routing (stdout, file, sidecar, direct export)

**Alerting & SLOs**

- SLI definitions (availability, latency, throughput, correctness)
- SLO targets and error budgets (99.9%, burn rate, window)
- Alert rule format (PromQL, Datadog monitors, CloudWatch alarms)
- Alert routing (PagerDuty, OpsGenie, Slack, email)
- Runbook references in alerts
- Alert severity classification

**Dashboards & Visualization**

- Dashboard tool (Grafana, Datadog, New Relic, CloudWatch, Kibana)
- Dashboard-as-code (Grafonnet, Terraform, JSON provisioning)
- Standard dashboard patterns (service overview, latency breakdown, error drill-down)
- Variable/template usage

**Error Tracking**

- Error tracking service (Sentry, Bugsnag, Rollbar, Datadog Error Tracking)
- SDK integration and configuration
- Error grouping and fingerprinting rules
- Source map / debug symbol upload
- Release tracking and deployment markers

**Log Aggregation**

- Aggregation stack (ELK/OpenSearch, Loki, CloudWatch Logs, Splunk)
- Log pipeline (Fluentd, Fluent Bit, Vector, Logstash)
- Index/label strategy and retention policies
- Query patterns and saved searches

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_observability.md`:

1. **Architecture Patterns** — how this project structures observability instrumentation
2. **Coding Conventions** — naming, labeling, attribute conventions
3. **Package Patterns** — key observability packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable instrumentation patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected observability stack
7. **SLO & alerting conventions** — SLI definitions, error budget policies, alert structure

---

## PHASE 3: BEST PRACTICES

Integrate for the detected observability stack:

- OpenTelemetry instrumentation principles relevant to this project
- Distributed tracing design (span naming, attribute standards, context propagation)
- Metrics design (RED/USE methods, cardinality control, histogram bucket selection)
- Structured logging discipline (correlation IDs, context enrichment, PII redaction)
- SLO-based alerting (error budgets, burn rate alerts, multi-window alerting)
- Alert quality (actionable alerts, runbook linking, severity classification, alert fatigue prevention)
- Dashboard design principles (USE/RED layout, drill-down hierarchy, variable templating)
- Error tracking integration (grouping strategy, release correlation, breadcrumbs)
- Sampling strategy trade-offs (completeness vs cost, tail-based for errors)
- Testing observability (trace assertion, metric validation, alert rule testing)
- Security: sensitive data in telemetry (PII in spans, credentials in logs), classify by severity (Critical/High/Medium/Low)
- Cost management (cardinality explosion prevention, retention policies, sampling tuning)
- Correlation across signals (trace-to-log, trace-to-metric, exemplars)
- Graceful degradation (telemetry pipeline failures must not impact application)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY observability task — tracing instrumentation, metrics design, logging setup, alert creation, SLO definition, dashboard building, error tracking integration, log aggregation, correlation ID propagation, sampling configuration.

**`allowed-tools`**: `Read Edit Write Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, infra, frontend)
3. **Architecture** — instrumentation architecture diagram, telemetry pipeline flow, signal relationships
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Span naming, metric naming, log format details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/test-patterns.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for PII and sensitive data verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with observability-specific detection signals (e.g., "alert firing" for Diagnostic, "add metrics to this service" for Efficient, "what is an error budget" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/tracing-patterns.md` — span design, context propagation, sampling examples (ALL code examples go here)
- `references/code-style.md` — span naming, metric naming, log format with full examples
- `references/security-checklist.md` — per-span, per-log, per-metric PII and sensitive data verification checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/metrics-catalog.md` — standard metric definitions, labels, and thresholds
- `references/test-patterns.md` — testing patterns for instrumentation with full examples
- `references/common-issues.md` — troubleshooting common observability pitfalls
- `assets/env-example` — environment variable template for exporter configuration
- `scripts/validate-observability.sh` — naming + instrumentation convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                    | Role                                                        | Tools          | Spawn When                                                         |
| ------------------------ | ----------------------------------------------------------- | -------------- | ------------------------------------------------------------------ |
| instrumentation-auditor  | Audit instrumentation coverage and correctness              | Read Glob Grep | New service onboarding, coverage review, instrumentation PR review |
| alert-designer           | Review and design alerting rules and SLO monitors           | Read Glob Grep | Alert creation, SLO definition, alert fatigue investigation        |
| slo-reviewer             | Validate SLO/SLI definitions and error budget configuration | Read Glob Grep | SLO changes, error budget review, reliability planning             |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/instrumentation-auditor.md` — instrumentation coverage audit agent
- `agents/alert-designer.md` — alerting rule review and design agent
- `agents/slo-reviewer.md` — SLO/SLI validation agent
