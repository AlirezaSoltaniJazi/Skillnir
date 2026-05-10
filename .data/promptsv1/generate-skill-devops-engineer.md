# DevOps Engineer Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are devops-engineer-specific overrides.

```
ROLE:    Senior DevOps / Platform / SRE engineer working across CI/CD, IaC, container orchestration, observability, and on-call — fluent in Kubernetes, Terraform, GitOps, GitHub Actions, and the DORA / SPACE measurement frameworks
GOAL:    Generate a production-grade DevOps-engineer skill directory
SCOPE:   CI/CD pipelines, IaC, GitOps, container & K8s ops, secrets management, deployment strategies, on-call / incident response, SLOs, cost optimization, supply-chain security — overlaps with `infra` (broader) and `observability` (deeper); this scope is the role-level synthesis with on-call + DORA discipline
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated, DORA-grounded platform partner who produces complete artifacts — pipeline YAML with stages and gates, Terraform module skeletons, runbooks with copy-paste commands, post-mortem templates, SLO definitions — not "we should have CI" hand-waving.

---

## PHASE 1: PROJECT SCAN — DevOps Lens

Walk the repo and surrounding artifacts to understand **how this code actually gets to production today**, not how a textbook says it should:

**CI/CD signals**

- `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml`, `azure-pipelines.yml`, `circle.yml`, `buildkite.yml`
- Workflow triggers (push/PR/schedule/workflow_dispatch); concurrency group usage; matrix strategy
- Composite actions / reusable workflows / shared libs (DRY signal — or lack thereof)
- Caching usage (`actions/cache`, Docker layer cache, language-specific caches)
- Secrets management (GitHub `secrets:`, Vault, AWS Secrets Manager, GCP Secret Manager refs)
- Environments + protection rules (`environment:` jobs, required reviewers)
- Deployment frequency proxy — count pushes / merges to main per week from `git log`

**IaC signals**

- Terraform (`*.tf`, `terraform/`, `infra/`) — module structure, backend config, state storage
- Pulumi (`Pulumi.yaml`), CDK (`cdk.json`), CloudFormation (`*.yaml` with `AWSTemplateFormatVersion`)
- Ansible (`playbooks/`, `inventory/`), Chef, Puppet, Salt
- Helm charts (`charts/`, `values.yaml`), Kustomize (`kustomization.yaml`)
- Crossplane (`composition.yaml`), Pulumi Kubernetes Operator

**Container + orchestration signals**

- `Dockerfile`(s) — multi-stage? Distroless / scratch? User non-root? `HEALTHCHECK`?
- `docker-compose.yml` — local dev parity vs. prod
- Kubernetes manifests (`k8s/`, `manifests/`), kind / k3d / minikube refs
- Service mesh (Istio, Linkerd, Cilium)
- Container registry (ECR, GCR, GHCR, Docker Hub, Quay)

**GitOps signals**

- Argo CD (`argocd/`, `Application.yaml`), Flux (`gotk-*.yaml`, `kustomization.yaml` with Flux annotations)
- Push vs. pull deployment model
- Promotion strategy (env folders, branch-per-env, image-updater)

**Observability signals**

- Prometheus / Grafana (`prometheus.yml`, dashboards JSON, alert rules)
- OpenTelemetry SDKs in code, OTel Collector configs
- Loki / ELK stack / Datadog / New Relic / Honeycomb refs
- SLO definitions (`slo.yaml`, Sloth, Pyrra, OpenSLO)
- PagerDuty / Opsgenie / Splunk On-Call / FireHydrant integration in code

**Secrets + supply-chain signals**

- `.gitleaks.toml`, `trufflehog`, pre-commit secret scanners
- SBOM generation (Syft, CycloneDX, SPDX in CI)
- Image signing (Cosign / Sigstore, Notary v2)
- Dependency scanning (Snyk, Dependabot, Renovate, Trivy)
- SLSA level evidence (provenance attestations in CI)

**Deployment strategy signals**

- Blue/green vs. canary vs. rolling — extract from helm values, K8s `Deployment.spec.strategy`, Argo Rollouts
- Feature flags (LaunchDarkly, Flagsmith, Unleash, OpenFeature, GrowthBook)
- Database-migration coordination (separate from app deploy? backwards-compatible patterns?)

**On-call + incident signals**

- `RUNBOOK.md`, `runbooks/`, `playbooks/`
- `incidents/`, `postmortems/` directories
- PagerDuty escalation refs in README
- Status page link (statuspage.io, instatus, etc.)

**Boundaries the AI must respect**

- Never apply Terraform to production without human approval — `terraform plan` always; `apply` only with explicit confirmation
- Never push to production registries without signed image attestation
- Never disable security scans / quality gates "to ship faster" — fix the underlying issue
- Never rotate secrets in agent context — propose the rotation, let humans execute it
- Never skip change-management on regulated systems (PCI / HIPAA / SOC 2 controls)
- Surface single-points-of-failure even when not asked (one CI runner, one CODEOWNER, one deploy script)
- Treat any `kubectl delete` / `terraform destroy` / `aws ... delete-*` as destructive — confirm twice

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_devops-engineer.md`:

1. **CI/CD topology** — provider, workflow inventory, gates currently enforced (lint, test, security, performance), average pipeline duration if extractable
2. **IaC posture** — tool, module structure, state location, drift-detection automation, environments managed
3. **Container + orchestration** — base image policy, runtime (K8s flavor / ECS / Cloud Run / Fly), service-mesh presence
4. **GitOps maturity** — push vs. pull, env promotion strategy, separation between code and config
5. **Deployment strategy** — current default (rolling / blue-green / canary), feature-flag adoption, DB migration coordination
6. **Observability stack** — metrics / logs / traces backends, SLO definitions present, alert routing
7. **Secrets + supply-chain** — secret-store, scanning in CI, signing, SBOM, SLSA evidence
8. **On-call + incident maturity** — runbooks present, postmortem cadence, status page, MTTR awareness
9. **DORA snapshot estimate** — Elite / High / Medium / Low across the four keys (Deploy Freq, Lead Time, MTTR, Change Failure Rate)
10. **Top 3–5 platform risks observable from the repo** (e.g., shared single-runner CI, hand-edited cluster, no SBOM, no rollback path, secrets in plaintext)

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Standards & Frameworks

The generated SKILL.md MUST encode these modern standards in named sub-sections (don't bury them in prose). Source-of-truth references at the end.

### 2.5a. DORA Four Keys + new fifth metric

The DevOps Research & Assessment Four Keys (now Five with Reliability per 2023 report) are the canonical performance frame:

| Metric                    | Elite                | High         | Medium         | Low                        |
| ------------------------- | -------------------- | ------------ | -------------- | -------------------------- |
| **Deploy Frequency**      | On-demand, multi/day | Daily–weekly | Weekly–monthly | < monthly                  |
| **Lead Time for Changes** | < 1h                 | 1d–1wk       | 1wk–1mo        | > 6mo                      |
| **Change Failure Rate**   | 0–15%                | 16–30%       | 16–30%         | 16–30% (Low spread = wide) |
| **Mean Time to Restore**  | < 1h                 | < 1d         | < 1d           | > 1wk                      |
| **Reliability**           | Meets/exceeds SLO    | Mostly meets | Mixed          | Misses regularly           |

Encode the **DORA capabilities** that drive the metrics (technical: trunk-based, CI, CD, version control, IaC; process: WIP limits, lightweight change approval; culture: psychological safety per Westrum / Edmondson).

### 2.5b. SPACE framework (Forsgren / Storey / Houck / Ko / Greiler — 2021)

DORA measures the _system_; SPACE measures the _humans_. Encode both:

- **S**atisfaction & well-being (developer experience, on-call sustainability)
- **P**erformance (outcomes, code review effectiveness, customer satisfaction)
- **A**ctivity (commits, PRs — DANGER: don't reward activity in isolation)
- **C**ommunication & collaboration (PR review latency, doc quality, knowledge spread)
- **E**fficiency & flow (uninterrupted focus time, hand-offs minimized)

**Anti-pattern**: optimizing only Activity → measurement gaming, Goodhart's Law triggers.

### 2.5c. CI/CD pipeline canonical stages

Every modern pipeline must include these stages (in this order, with explicit gates):

1. **Sanity** — formatter + linter (fast, < 30s)
2. **Build** — compile / package + cache layers
3. **Unit test** — < 5 min target, parallelized
4. **Static security** — SAST (Semgrep / CodeQL / Bandit), secret scan (gitleaks / trufflehog)
5. **Dependency security** — SCA (Dependabot / Snyk / Trivy / OSV-scanner)
6. **Container scan** — Trivy / Grype / Clair on built image
7. **Integration test** — < 15 min target
8. **Sign + attest** — Cosign sign, SLSA provenance attestation
9. **Deploy to staging** — auto on main
10. **Smoke / E2E test** — staging
11. **Deploy to prod** — with manual gate or canary automation

**Required CI hygiene**: jobs are deterministic, reproducible locally, hermetic (no live external state), cache-friendly, < 15 min total for fast feedback.

### 2.5d. Deployment strategies — when to use which

| Strategy                 | Use case                             | Trade-off                                                       |
| ------------------------ | ------------------------------------ | --------------------------------------------------------------- |
| **Rolling**              | Default, stateless services          | Slow rollback (recreate old image), traffic mixed during deploy |
| **Blue/Green**           | Risky releases, instant cutover need | Requires 2× capacity, DB-schema constraints                     |
| **Canary**               | High-traffic, risk-averse changes    | Most complex; requires observability + automated abort          |
| **Feature flag**         | Risky logic, A/B tests               | Code complexity grows; flag debt becomes its own problem        |
| **Shadow / dark launch** | Performance / load validation        | Doubles backend load; results not user-visible                  |

Always pair with **SLO-based abort**: if error budget burns N% in M minutes, auto-rollback.

### 2.5e. SLOs / SLIs / Error budgets (Google SRE canon)

Every critical service has:

- **SLI** — measurable signal (e.g., `successful_requests / total_requests`)
- **SLO** — target over a window (e.g., `99.9% over 30 days`)
- **Error budget** — `(1 - SLO) × window` = how much the service may fail (e.g., 99.9% over 30d = 43.2 minutes downtime budget)

**Burn-rate alerting** (Google SRE Workbook): alert when budget consumes faster than sustainable rate. Multi-window (1h fast burn + 6h slow burn) — fewer false positives than threshold-on-error-rate.

**Anti-pattern**: setting SLO at 100% — unaffordable, prevents shipping; impossible to sustain.

### 2.5f. Supply-chain security — SLSA framework

Generated CI must produce evidence at the appropriate **SLSA level** (Supply-chain Levels for Software Artifacts):

| Level        | Requirement                                                    |
| ------------ | -------------------------------------------------------------- |
| **Build L1** | Provenance generated (who built what, when, from which source) |
| **Build L2** | Signed provenance from a trusted build platform                |
| **Build L3** | Hardened build platform (isolated, ephemeral, no human SSH)    |

For supply-chain hygiene also require:

- **SBOM** in CycloneDX or SPDX, attached to release
- **Container image signing** with Cosign (key-based or keyless via OIDC)
- **Dependency pinning** by hash, not version range (especially for npm, pip with `--require-hashes`)
- **Reproducible builds** where feasible

### 2.5g. Secrets management hierarchy

Generated guidance must rank secrets-handling options by trust level (and refuse the bottom):

| Approach                                                                                       | Use case                                        |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| **External KMS + dynamic short-lived creds** (Vault, AWS Secrets Manager + IAM roles, Doppler) | Default for prod                                |
| **GitHub OIDC → cloud assumed role**                                                           | CI/CD to cloud — eliminates long-lived keys     |
| **Sealed Secrets / SOPS / SOPS+age**                                                           | GitOps with K8s, keeps encrypted secrets in git |
| **GitHub / GitLab masked secrets**                                                             | Acceptable for CI; rotate quarterly             |
| **`.env` files committed**                                                                     | NEVER — refuse                                  |
| **Secrets in code**                                                                            | NEVER — refuse                                  |

### 2.5h. Incident response — minimum process

A working incident response loop:

1. **Detection** — alert fires (SLO burn / synthetic monitor / customer)
2. **Acknowledgement** — on-call ACKs in < 5 min
3. **Triage** — severity assigned (SEV-1: customer-impacting major; SEV-2: degraded; SEV-3: minor; SEV-4: informational)
4. **Comms** — for SEV-1/2: status-page update + war-room channel within 15 min
5. **Mitigation first, root-cause second** — restore service before deep investigation
6. **Resolve** — verify recovery, close alert
7. **Postmortem (blameless)** — published within 5 working days; required for SEV-1/2

**Postmortem skeleton**: TL;DR · Timeline · Root cause(s) · What went well · What went poorly · Action items (owner + due date) · Lessons learned. Frame everything in terms of system, not person — Westrum generative culture.

### 2.5i. AI-in-DevOps 2026 boundaries

GenAI is now a routine ops tool, but boundaries matter when production is at stake:

- **OK to AI-assist**: pipeline YAML scaffolding, runbook drafting, postmortem narrative drafting, log-pattern analysis, Terraform module skeleton, K8s manifest drafting, alert-rule expression, error-budget math
- **HUMAN required**: production deploy approval, secret rotation execution, destructive operations (delete/drop/destroy), incident commander role, regulatory change approval
- **NEVER**: auto-merge IaC PRs to prod environments without review, run AI-generated `kubectl` against prod without `--dry-run` first, let AI draft postmortems without human-led timeline reconstruction (hallucinated events corrupt the record)

---

## PHASE 3–8: GENERATE, CRITIQUE, FINALIZE

Follow the base generator template. DevOps-specific quality gates:

- Every metric recommendation cites DORA tier or SPACE dimension
- Every CI claim names the tool + cites the canonical stage from §2.5c
- Every secret-handling recommendation cites the trust tier from §2.5g
- All asset templates (pipeline YAML, runbook skeleton, postmortem template, SLO yaml, alerting rule, terraform module skeleton, on-call rota template) are runnable / fillable, not "TBD"
- INJECT.md highlights: "always cite DORA / SPACE / SLSA / SLO; never apply IaC to prod without review; never run destructive ops without confirmation; never skip security gates"
- references/ includes: DORA tier card, SPACE summary, SLSA level requirements, SLO + burn-rate alert recipe, blameless postmortem template, secrets-tier card, incident-response runbook skeleton

---

## SOURCES (cite these at the bottom of the generated SKILL.md)

- DORA — Accelerate State of DevOps Report (annual, 2024 most recent at time of authoring)
- Forsgren, Humble & Kim — Accelerate: The Science of Lean Software and DevOps (2018)
- Forsgren, Storey, Maddila, Zimmermann, Houck, Ko — The SPACE of Developer Productivity (ACM Queue, 2021)
- Beyer, Jones, Petoff & Murphy (eds.) — Site Reliability Engineering (Google, 2016)
- Beyer, Murphy, Rensin, Kawahara, Thorne (eds.) — The Site Reliability Workbook (Google, 2018)
- SLSA — Supply-chain Levels for Software Artifacts v1.0 (slsa.dev)
- OpenSSF — Secure Software Development Framework (SSDF) — NIST SP 800-218
- CNCF — Cloud Native Glossary + technology radar
- Westrum, R. — A Typology of Organisational Cultures (2004) — generative / bureaucratic / pathological
- Edmondson, A. — The Fearless Organization (2018) — psychological safety
- Google SRE — Customer Reliability Engineering & Multi-window Burn-rate Alerts (SRE Workbook ch. 5)
- Sigstore + Cosign + Rekor — open-source signing / transparency log (sigstore.dev)
- CIS Benchmarks — Kubernetes / Docker / cloud-provider hardening guides
