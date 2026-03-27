# Infrastructure Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are infrastructure-specific overrides.

```
ROLE:     Senior DevOps/platform engineer analyzing production infrastructure
GOAL:     Generate a production-grade infrastructure skill directory
SCOPE:    Infrastructure, deployment, DevOps files only — ignore application source code (business logic, UI, models)
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Infrastructure Only

**Containerization**

- Dockerfile(s) — base images, multi-stage builds, layer optimization
- docker-compose.yml — services, networks, volumes, env config
- Container registry (ECR, GCR, Docker Hub, GHCR)
- Image tagging strategy (latest, semver, git-sha)
- .dockerignore patterns

**CI/CD Pipelines**

- Platform (GitHub Actions, GitLab CI, Jenkins, CircleCI)
- Pipeline files (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Stages (lint, test, build, deploy, release)
- Branch strategy + release/deployment triggers
- Artifact management + secret management in CI (vault, env vars, OIDC)

**Infrastructure as Code**

- IaC tool (Terraform, Pulumi, CloudFormation, CDK, Ansible)
- Cloud provider (AWS, GCP, Azure, multi-cloud)
- Resource organization (modules, stacks, workspaces)
- State management (remote backend, locking)
- Environment separation (dev/staging/prod)
- Naming conventions for resources

**Orchestration & Compute**

- Orchestrator (Kubernetes, ECS, Nomad, Lambda, App Runner)
- If K8s: manifests, Helm charts, Kustomize, operators
- Namespace strategy + resource limits + scaling policy (HPA, KEDA)
- Service mesh (Istio, Linkerd, none)

**Networking & Security**

- Load balancer (ALB, NLB, Nginx, Traefik)
- DNS management (Route53, Cloud DNS, Cloudflare)
- TLS/SSL (ACM, Let's Encrypt, cert-manager)
- Network policies/security groups + IAM roles
- Secret management (AWS Secrets Manager, Vault, K8s secrets, SOPS)

**Monitoring & Observability**

- Logging (CloudWatch, ELK, Loki, Datadog)
- Metrics (Prometheus, CloudWatch Metrics, Datadog)
- Tracing (Jaeger, X-Ray, Tempo)
- Alerting (PagerDuty, Opsgenie, Slack webhooks)
- Dashboards + health checks/readiness probes

**Database & Storage**

- DB provisioning (RDS, Cloud SQL, managed, self-hosted)
- Backup strategy + migration tooling at infra level
- Object storage (S3, GCS, MinIO) + CDN (CloudFront, Fastly)

**Developer Experience**

- Local dev setup (docker-compose, Tilt, Skaffold, devcontainers)
- Makefiles/Justfiles/task runners
- Environment variable management (.env, .env.example)
- Scripts directory (deploy, migration, seed scripts)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_infra.md`:

1. **Deployment Patterns** — how this project is built and deployed
2. **Infrastructure Conventions** — naming, tagging, organization
3. **Pipeline Patterns** — CI/CD stages, triggers, artifact flow
4. **Security Posture** — secrets, IAM, network policies
5. **Things to ALWAYS do** — non-negotiable infra patterns
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Operational wisdom** — monitoring, alerting, incident response patterns

---

## PHASE 3: BEST PRACTICES

Integrate for the detected stack:

- 12-factor app methodology (config, backing services, disposability)
- Docker best practices (minimal images, non-root, layer caching, .dockerignore)
- CI/CD best practices (fast feedback, idempotent deploys, rollback strategy)
- IaC principles (immutable infra, drift detection, state management)
- Kubernetes best practices (resource limits, health probes, security contexts, PDB)
- Secret management (never in code, rotation, least privilege)
- Network security (zero trust, mTLS, network policies)
- Observability (RED/USE methods, SLOs/SLIs, structured logging)
- Cost optimization (right-sizing, reserved instances, spot/preemptible)
- Disaster recovery (backup verification, RTO/RPO, multi-region)
- GitOps principles (declarative, versioned, automated)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY infrastructure task — Docker/container config, CI/CD pipelines, Terraform/IaC, Kubernetes manifests, deployment scripts, monitoring setup, secret management, cloud provisioning, networking, DevOps automation.

**`allowed-tools`**: `Read Edit Write Bash(terraform:*) Bash(docker:*) Bash(kubectl:*) Bash(helm:*) Glob Grep` (adjust for detected IaC/orchestration tools)

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (backend, frontend, mobile)
3. **Architecture** — infrastructure diagram, environment topology, deploy flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Conventions** — rules table only. Naming, tagging, env separation details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Monitoring & Alerting** — bullet list, no code examples
8. **Security** — summary + link to references/security-checklist.md for secrets, IAM, network verification
9. **Disaster Recovery** — backup, restore, rollback procedures
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — config files, runbooks, cloud docs
12. **Adaptive Interaction Protocols** — interaction modes with infra-specific detection signals (e.g., "what is this Terraform resource" for Teaching, "same module as X" for Efficient, "terraform plan failed" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, memory bridge

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/deployment-guide.md` — deployment flow, environment topology
- `references/code-style.md` — naming, tagging, env separation conventions with examples
- `references/security-checklist.md` — secrets, IAM, network, compliance checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/pipeline-patterns.md` — CI/CD stage patterns with full examples (ALL code examples)
- `references/common-issues.md` — troubleshooting common infra pitfalls
- `assets/docker-example` — Dockerfile + docker-compose templates
- `assets/terraform-example` — Terraform module/resource templates
- `scripts/validate-infra.sh` — naming + config convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                    | Tools               | Spawn When                                                         |
| ---------------- | ------------------------------------------------------- | ------------------- | ------------------------------------------------------------------ |
| security-scanner | IaC security audit and secret detection                 | Read Glob Grep      | Terraform plan review, secret detection, network policy audit      |
| drift-detector   | Configuration drift analysis between environments       | Read Glob Grep Bash | Environment comparison, state review, config validation            |
| cost-reviewer    | Resource cost analysis and right-sizing recommendations | Read Glob Grep      | Resource right-sizing, cost optimization review, capacity planning |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/security-scanner.md` — IaC security audit agent
- `agents/drift-detector.md` — configuration drift analysis agent
- `agents/cost-reviewer.md` — resource cost analysis agent
