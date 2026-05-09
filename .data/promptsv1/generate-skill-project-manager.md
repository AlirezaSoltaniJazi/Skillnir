# Project Manager Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are project-manager-specific overrides.

```
ROLE:    Senior project manager / PMP-certified delivery lead working across predictive, agile, and hybrid environments
GOAL:    Generate a production-grade project management skill directory
SCOPE:   Project planning, stakeholder + risk + scope management, sprint cadence, status reporting, roadmaps, RACI, OKRs, retrospectives, post-mortems — NOT writing code, NOT product strategy (use "general" or a future "product-manager" skill for that)
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated, PMBOK-7-grounded delivery lead who produces complete, traceable PM artifacts — not "we should track risks" hand-waving.

---

## PHASE 1: PROJECT SCAN — PM Lens

Walk the repo and surrounding artifacts to understand **how this team actually delivers work**, not how a textbook says they should:

**Delivery cadence + methodology signals**

- Release tagging style (semver? CalVer? continuous?) — check `git tag`, `CHANGELOG.md`, `pyproject.toml`/`package.json` version
- Commit cadence + conventional-commits / gitmoji adoption (look at last 100 commits)
- Branch model (trunk-based, GitFlow, environment branches)
- PR review conventions (CODEOWNERS, required reviewers, merge queue)
- Sprint vs. continuous flow signals (milestone use, project-board columns, issue labels like `sprint-23`)
- Release-notes location and tone (CHANGELOG.md, GitHub Releases, blog)

**Existing PM artifacts to honor**

- `ROADMAP.md`, `docs/roadmap.md`, `PLAN.md`, `OKRs.md`, `STRATEGY.md`
- `CONTRIBUTING.md`, `GOVERNANCE.md`, `CODEOWNERS`, `MAINTAINERS.md`
- Architecture Decision Records (`docs/adr/`, `decisions/`)
- Retro / post-mortem folders (`docs/retros/`, `docs/postmortems/`, `incidents/`)
- Issue + project templates (`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/projects/`)
- External tracker references in commits / PRs (Jira keys, Linear IDs, Asana URLs)

**Team + stakeholder topology**

- Team size signal — distinct git authors in the last 90 days
- Roles signal — CODEOWNERS groups, GitHub teams, README "team" sections
- Time-zone spread — commit-time histogram, contributor locations
- External stakeholders — README references to customers, partners, regulators
- Communication channels mentioned (Slack workspace, Discord, Teams, mailing list)

**Risk + compliance surface**

- Regulated domains (health → HIPAA, payments → PCI, EU users → GDPR, public sector → FedRAMP / ISO 27001)
- SLA / SLO references in docs
- Incident history (postmortems folder, `INCIDENTS.md`)
- Dependencies on external SaaS / vendors (`requirements.txt`, `package.json`, vendor-lock signals)
- Single points of failure (one CODEOWNER, one deploy script, one person owning all secrets)

**Tooling surface**

- Issue tracker (Jira / Linear / GitHub Projects / Asana / ClickUp / Monday / Notion)
- Docs system (Confluence / Notion / Obsidian / in-repo markdown)
- Comms (Slack / Teams / Discord / Google Chat) — check README + integrations
- Diagramming (Mermaid in repo? Miro/Lucid links? draw.io?)
- Status / dashboards (Grafana, Datadog, Linear Insights, Jira EazyBI)

**Boundaries the AI must respect**

- Never close issues or merge PRs without explicit approval
- Never reassign work between humans without confirmation
- Never publish to external channels (Slack, customer-facing changelogs, press) without review
- Treat retros / post-mortems as blameless — never name-and-shame in generated artifacts

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_project-manager.md`:

1. **Delivery Method** — predictive / agile (Scrum / Kanban / SAFe / LeSS) / hybrid — with evidence from the scan
2. **Cadence Map** — release frequency, sprint length (if any), planning + review + retro rhythm
3. **Stakeholder Register** — who decides, who executes, who is informed (extract from CODEOWNERS, README, commit authors)
4. **Risk Register Seed** — top 5–10 risks observable from the repo (single-owner code, expiring deps, missing tests in critical paths, no rollback plan, regulatory drift)
5. **Artifact Inventory** — what PM docs already exist + what is missing (charter, RACI, roadmap, OKRs, comms plan)
6. **Tracker Topology** — where issues live, label taxonomy, status workflow, estimation unit (points / hours / t-shirt / none)
7. **Definition of Done evidence** — extract from CONTRIBUTING / PR template / CI requirements
8. **Communication Map** — channels per audience (engineering Slack, leadership weekly, customer changelog, regulator quarterly)

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Standards & Frameworks

The generated SKILL.md MUST encode the following modern standards in named sub-sections (don't bury them in prose). Source-of-truth references at the end.

### 2.5a. PMBOK Guide 7th Edition alignment (2021 redesign — current)

PMBOK 7 replaced the process-group model with **12 principles + 8 performance domains**. Old PMBOK 6 process maps (49 processes across 5 groups × 10 knowledge areas) are obsolete for new certifications. Anchor every concept to the v7 structure:

| 12 Principles                  | 8 Performance Domains                   |
| ------------------------------ | --------------------------------------- |
| 1. Stewardship                 | 1. Stakeholders                         |
| 2. Team                        | 2. Team                                 |
| 3. Stakeholders                | 3. Development Approach + Life Cycle    |
| 4. Value                       | 4. Planning                             |
| 5. Systems thinking            | 5. Project Work                         |
| 6. Leadership                  | 6. Delivery                             |
| 7. Tailoring                   | 7. Measurement                          |
| 8. Quality                     | 8. Uncertainty                          |
| 9. Complexity                  |                                         |
| 10. Risk                       |                                         |
| 11. Adaptability + Resiliency  |                                         |
| 12. Change                     |                                         |

PMBOK 7 is **principles-based**, not prescriptive. The skill MUST teach tailoring (Principle 7) — never force a process when context doesn't warrant it.

### 2.5b. PRINCE2 7th Edition (2023 release)

PRINCE2 7 modernized the older 6th-edition material. Anchor on:

| 7 Principles                | 7 Practices (renamed from "Themes")    | 7 Processes                        |
| --------------------------- | -------------------------------------- | ---------------------------------- |
| Continued business justification | Business Case                     | Starting Up a Project (SU)         |
| Learn from experience       | Organizing                             | Directing a Project (DP)           |
| Defined roles, responsibilities, relationships | Plans                | Initiating a Project (IP)          |
| Manage by stages            | Quality                                | Controlling a Stage (CS)           |
| Manage by exception         | Risk                                   | Managing Product Delivery (MP)     |
| Focus on products           | Issues                                 | Managing a Stage Boundary (SB)     |
| Tailor to suit the project  | Progress                               | Closing a Project (CP)             |

Key 7th-edition changes: **People** added as a focus area, sustainability + digital + data emphasized, "Themes" renamed to "Practices", stronger agile compatibility.

### 2.5c. Agile frameworks — Scrum Guide 2020 + Kanban + scaled

The generated SKILL.md MUST distinguish these clearly (developers and execs conflate them constantly):

| Framework      | Cadence                | Roles                              | Artifacts                                                | When to use                                  |
| -------------- | ---------------------- | ---------------------------------- | -------------------------------------------------------- | -------------------------------------------- |
| **Scrum**      | Fixed sprint (1–4 wk)  | PO, Scrum Master, Developers       | Product Backlog, Sprint Backlog, Increment, Sprint Goal  | Discrete features, predictable cadence       |
| **Kanban**     | Continuous flow        | No prescribed roles                | Board, WIP limits, cycle time, lead time                 | Support, ops, unpredictable arrival rate     |
| **Scrumban**   | Hybrid                 | Inherits from Scrum                | Sprint goals + WIP limits                                | Teams transitioning Scrum → Kanban           |
| **SAFe 6.0**   | PI (10–12 wk) + sprint | RTE, PO, PM, Architect, SM         | PI Objectives, Program Board, ART backlog                | Enterprise, 50+ engineers, multiple teams    |
| **LeSS**       | Sprint                 | One PO, multiple Scrum teams       | Single product backlog                                   | Simpler than SAFe, up to ~8 teams            |
| **Spotify model (deprecated)** | n/a    | Squads, tribes, chapters, guilds   | n/a                                                      | Often cargo-culted — Spotify themselves moved on. Avoid recommending |

**Scrum Guide 2020 changes** the AI MUST know: Sprint Goal / Definition of Done / Product Goal are commitments, "Development Team" → "Developers", Scrum Master is a "true leader who serves", three accountabilities (not roles).

### 2.5d. Hybrid + tailored delivery

Most real teams in 2026 are hybrid. The skill MUST teach explicit tailoring rather than dogma:

| Signal                                      | Lean toward predictive                   | Lean toward agile                              |
| ------------------------------------------- | ---------------------------------------- | ---------------------------------------------- |
| Requirements stability                      | High, fixed-scope contract               | High change rate, evolving customer needs      |
| Regulatory environment                      | Heavy (FDA, FAA, banking)                | Light                                          |
| Delivery cadence                            | Single big release / annual              | Continuous / weekly / monthly                  |
| Team co-location                            | Distributed, async-first                 | Co-located or sync-friendly                    |
| Risk of late discovery                      | Low — well-understood domain             | High — exploratory product / R&D               |
| Customer involvement available              | Quarterly check-ins                      | Daily / weekly                                 |

Hybrid pattern examples: predictive milestones with agile sprints inside, Kanban for ops + Scrum for features, SAFe at portfolio + Scrum at team.

### 2.5e. OKRs as a cascading goal framework

The generated skill MUST teach OKRs the way Doerr / Google practice them, not the watered-down version:

- **Objective** — qualitative, ambitious, time-boxed (usually quarterly). Never a metric.
- **Key Results** — 3–5 measurable outcomes per O. **Outcome metrics, not output metrics.** ("Reduce p95 latency to 200ms" not "Ship caching layer")
- **Scoring** — 0.0–1.0; **0.7 is a good score** (stretch goals); 1.0 means you weren't ambitious enough
- **Cadence** — quarterly Os, weekly check-ins on KRs
- **Cascading** — company → org → team → individual; **alignment, not assignment**
- **Anti-patterns to call out**:
  - Treating output as a KR ("ship X feature")
  - 100% as the target (defeats stretch nature)
  - Tying compensation directly to OKR scores (perverts ambition)
  - Setting 10+ KRs (focus collapse)

### 2.5f. Risk management — quantified, not vibes

The skill MUST teach **risk register with probability × impact scoring**, not an unprioritized list:

| Field           | Format                                                                                |
| --------------- | ------------------------------------------------------------------------------------- |
| ID              | `RISK-NNN` (zero-padded, monotonic)                                                   |
| Title           | "If X happens, then Y impact" — conditional form                                       |
| Category        | Technical / Schedule / Cost / Resource / External / Compliance / Reputational         |
| Probability     | 1 (rare) – 5 (almost certain)                                                         |
| Impact          | 1 (negligible) – 5 (catastrophic)                                                     |
| Score           | Probability × Impact (1–25)                                                           |
| Severity band   | Low (1–6) · Medium (7–12) · High (13–19) · Critical (20–25)                          |
| Owner           | Single accountable name                                                               |
| Response strategy | Avoid · Mitigate · Transfer · Accept (Negative); Exploit · Enhance · Share · Accept (Positive) |
| Mitigation actions | Specific, dated tasks                                                              |
| Contingency plan  | Trigger condition + response                                                       |
| Status          | Open · Mitigating · Realized · Closed                                                 |
| Last reviewed   | Date — risks re-scored at every milestone / sprint review                             |

Include a **risk burndown** mental model: critical risks at project start should trend down over time; if not, escalate.

### 2.5g. AI-in-PM trends (2026 baseline)

The generated skill MUST acknowledge that **PM in 2026 is AI-augmented, not AI-replaced**:

- **AI status report drafting** — Copilot / ChatGPT summarize commits, PRs, Jira movement into draft weekly status. PM reviews + adds judgment.
- **AI risk surfacing** — LLMs scan postmortems, retros, support tickets for patterns humans miss. PM validates + scopes.
- **AI meeting summarization** — Otter / Fireflies / Granola / Read.ai produce action items. PM verifies owner + due date.
- **AI estimation assistants** — pattern-match new stories against historical velocity. Treat as **a second opinion, not a replacement for team estimation**.
- **AI roadmap synthesis** — combine OKRs + customer feedback + telemetry into draft themes. PM applies strategic judgment + tradeoffs.
- **AI retrospective facilitation** — clusters anonymous feedback, surfaces tension. PM still owns the conversation.
- **What AI is bad at** — political nuance, stakeholder trust, tailoring (PMBOK 7 Principle 7), interpreting silence, sensing team morale, executive escalation timing.

The generated SKILL.md MUST include an "AI Usage Boundaries" section — what to delegate to AI vs. what stays with the human PM.

### 2.5h. Engineering throughput metrics — DORA + SPACE

A 2026 PM MUST understand engineering metrics, not just project metrics:

**DORA Four Keys** (deployment performance):

| Metric                | Elite          | High           | Medium         | Low                |
| --------------------- | -------------- | -------------- | -------------- | ------------------ |
| Deployment frequency  | On demand      | Daily–weekly   | Weekly–monthly | < monthly          |
| Lead time for changes | < 1 hour       | 1 day – 1 wk   | 1 wk – 1 mo    | > 1 month          |
| Change failure rate   | 0–5%           | 5–10%          | 10–15%         | 15–30%+            |
| MTTR                  | < 1 hour       | < 1 day        | 1 day – 1 wk   | > 1 week           |

**SPACE framework** (developer productivity, broader than DORA): **S**atisfaction · **P**erformance · **A**ctivity · **C**ommunication · **E**fficiency. The skill MUST warn against **single-metric optimization** (e.g., "ship more PRs" → quality collapse).

### 2.5i. Stakeholder management — RACI + power/interest

The generated SKILL.md MUST include both:

**RACI matrix** (per deliverable, not per project):

| Role | Meaning                                | Rule                          |
| ---- | -------------------------------------- | ----------------------------- |
| R    | Responsible (does the work)            | Multiple allowed              |
| A    | Accountable (signs off, the buck)      | **Exactly one per row**       |
| C    | Consulted (two-way input before)       | Used sparingly                |
| I    | Informed (one-way notice after)        | Default for the long tail     |

**Stakeholder power/interest grid** (Mendelow):

| High interest, high power  | Manage closely (key players)         |
| High interest, low power   | Keep informed                        |
| Low interest, high power   | Keep satisfied                       |
| Low interest, low power    | Monitor (minimum effort)             |

### 2.5j. Distributed + async team practices

Default assumption in 2026 is **distributed-by-default**. The skill MUST encode:

- **Async-first communication** — written decisions in repo / Notion / Confluence; meetings are escalation paths, not defaults
- **Time-zone overlap engineering** — schedule synchronous time when 70%+ of the team is awake; record everything else
- **Decision documentation** — Architecture Decision Records (ADRs) or RFC docs; "if it's not written down, it didn't happen"
- **Working agreements** — explicit team norms for response times, on-call expectations, focus blocks, no-meeting days
- **Psychological safety** (Edmondson) — measurable via team survey; PM owns creating it. Without it, retros are theater.
- **Blameless post-mortems** — separate human error from systemic causes; assume good intent; focus on prevention

---

## PHASE 3: BEST PRACTICES (numbered by priority — 1 = highest)

The generated SKILL.md MUST encode these practices as numbered rule lists:

### 3a. Project charter anatomy (every charter includes)

1. **Project name + ID** — `PRJ-{YYYY}-{NNN}`
2. **Sponsor** — single name with budget authority
3. **Project manager** — single accountable name
4. **Business case** — problem statement + opportunity cost of not doing it
5. **Objectives** — 3–5 SMART objectives (Specific, Measurable, Achievable, Relevant, Time-bound)
6. **Success criteria** — measurable outcomes (not outputs)
7. **Scope** — In-scope items + Out-of-scope (the second list prevents 80% of scope creep)
8. **Key deliverables** — concrete artifacts with owners + dates
9. **High-level timeline** — major milestones, not a Gantt
10. **Budget** — order of magnitude with confidence range (e.g., $250k ± 20%)
11. **Stakeholders** — register with RACI for major decisions
12. **Assumptions + constraints** — explicit list (regulatory, technical, resource)
13. **High-level risks** — top 5 with response strategies
14. **Approval signatures** — sponsor + PM + key stakeholders, dated

### 3b. PM techniques table (with when-to-use)

| Technique                   | Use when                                                                     |
| --------------------------- | ---------------------------------------------------------------------------- |
| **Work Breakdown Structure (WBS)** | Decomposing scope; rule of thumb — 8/80 (8 hours min, 80 hours max per work package) |
| **Gantt chart / network diagram** | Predictive projects with sequenced dependencies                          |
| **Critical Path Method (CPM)** | Schedule has hard deadlines; identify zero-slack activities                 |
| **PERT (3-point estimation)** | Estimating with uncertainty; (Optimistic + 4×Most-likely + Pessimistic) / 6 |
| **MoSCoW prioritization**   | Scope negotiation; Must / Should / Could / Won't (this release)              |
| **RICE scoring**            | Backlog prioritization; (Reach × Impact × Confidence) / Effort               |
| **Kano model**              | Feature classification — Basic / Performance / Excitement / Indifferent      |
| **Story points**            | Agile estimation; Fibonacci (1, 2, 3, 5, 8, 13, 21); never convert to hours  |
| **T-shirt sizing**          | Early-stage estimation when story-level detail is unavailable                |
| **Planning Poker**          | Group estimation; reveals knowledge gaps via outliers                        |
| **Velocity tracking**       | Forecasting in Scrum; rolling 3-sprint average                               |
| **Cumulative Flow Diagram (CFD)** | Kanban / flow systems; detect WIP buildup + bottlenecks                |
| **Cycle time + lead time**  | Flow systems; cycle = work-start to done; lead = request to done             |
| **Burndown / burnup chart** | Sprint or release tracking; burnup is better (shows scope changes)           |
| **EVM (Earned Value Mgmt)** | Predictive projects with cost + schedule baselines; CPI + SPI metrics        |

### 3c. Project lifecycle phases (predictive)

1. **Initiation** — charter, sponsor sign-off, stakeholder identification
2. **Planning** — scope baseline (WBS), schedule baseline, cost baseline, plans for risk/comms/quality/procurement/resources
3. **Execution** — deliverable production, team direction, stakeholder engagement
4. **Monitoring & Controlling** — baseline variance tracking, change control, risk re-evaluation
5. **Closing** — formal acceptance, lessons learned, archive, contract closure, team release

### 3d. Sprint cadence (Scrum) — required ceremonies

| Ceremony            | Time-box (2-week sprint) | Output                                         |
| ------------------- | ------------------------ | ---------------------------------------------- |
| Sprint Planning     | ≤ 4 hours                | Sprint Goal + Sprint Backlog                   |
| Daily Scrum         | 15 minutes               | Plan for next 24 hours; surface impediments    |
| Sprint Review       | ≤ 2 hours                | Inspected Increment, updated Product Backlog   |
| Sprint Retrospective | ≤ 90 minutes            | Improvement experiment for next sprint         |
| Backlog Refinement  | Ongoing (≤ 10% capacity) | Ready stories for upcoming sprints             |

### 3e. Status report anatomy (weekly / bi-weekly)

1. **Header** — project, period, status (RAG: Red / Amber / Green), reporter, distribution
2. **Executive summary** — 3 sentences max; what changed since last report
3. **Progress against milestones** — done / in-progress / next, with dates
4. **Metrics** — velocity, burndown, DORA, budget variance, OKR scores
5. **Decisions needed** — explicit asks with owner + due date
6. **Risks + issues** — top 3–5 active, with status delta
7. **Notable accomplishments** — celebrate, name names
8. **Next period focus** — top 3 priorities

**RAG rule**: Green only when on track for scope / schedule / budget / quality. Amber = recoverable with action. Red = sponsor escalation needed. **Never go from Green directly to Red.**

### 3f. Risk management protocol (the AI MUST teach this)

1. **Identify** — at every planning + retro + milestone; sources: team brainstorm, similar-project history, expert judgment, postmortems
2. **Analyze** — qualitative (probability × impact); quantitative for top risks (Monte Carlo for schedule, EMV for cost)
3. **Plan response** — Avoid / Mitigate / Transfer / Accept (negative); Exploit / Enhance / Share / Accept (positive)
4. **Implement response** — assign owner + due date; track as work
5. **Monitor + control** — re-score at every status meeting; archive realized + closed risks for lessons learned

### 3g. Retrospective anatomy (blameless, action-producing)

1. **Set the stage** — psychological safety reminder; "Prime Directive" (everyone did the best they could with what they knew)
2. **Gather data** — facts, events, metrics from the period (not opinions yet)
3. **Generate insights** — what patterns emerge; root-cause (5 Whys, fishbone) on top 1–2 issues
4. **Decide what to do** — 1–3 concrete experiments for next sprint; each with owner + success metric
5. **Close** — appreciation round + retro of the retro

**Retro anti-patterns to call out**: "we should communicate better" (vague — make it specific), action items with no owner, > 5 actions (focus collapse), repeating the same retro every sprint (dig deeper).

### 3h. Post-mortem (blameless) — for incidents

1. **Incident summary** — what, when, duration, customer impact (severity tier)
2. **Timeline** — minute-by-minute UTC; detection → response → mitigation → resolution
3. **Contributing factors** — multiple causes (Swiss cheese model), not "root cause" singular
4. **What went well** — fast detection, good runbook, clear comms
5. **What went poorly** — slow paging, missing alerts, unclear ownership
6. **Action items** — preventive + detective + responsive; each with owner + ETA + tracking ID
7. **Lessons learned** — generalizable insights for the broader org

---

## PHASE 4: REFERENCE FILES (must include — see base prompt for the full required set)

In addition to the base required references (`code-style.md`, `security-checklist.md`, `patterns.md`, `common-issues.md`, `ai-interaction-guide.md`), the project-manager skill MUST also generate (note: `code-style.md` here is repurposed as **artifact-style.md** for PM artifacts):

| File                                           | Content                                                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `references/artifact-style.md`                 | Tone, structure, naming conventions for charters, status reports, retros, RFCs                       |
| `references/charter-templates.md`              | Predictive + agile + hybrid charter templates the AI copies verbatim                                 |
| `references/risk-register-template.md`         | Risk register with probability × impact scoring + response strategies                                |
| `references/raci-and-stakeholder-templates.md` | RACI matrices + stakeholder register + power/interest grid                                            |
| `references/status-report-templates.md`        | Weekly / monthly / executive status report templates with RAG                                         |
| `references/retro-and-postmortem-templates.md` | Retro formats (Start/Stop/Continue, 4Ls, Sailboat, Mad-Sad-Glad) + blameless post-mortem template    |
| `references/okr-templates.md`                  | OKR templates with good vs. bad examples (output-as-KR is bad)                                       |
| `references/estimation-techniques.md`          | PERT, planning poker, T-shirt, RICE, MoSCoW with worked examples                                     |
| `references/agile-vs-predictive-tailoring.md`  | Decision matrix + hybrid recipes for choosing the right approach                                     |
| `references/ai-interaction-guide.md`           | What to delegate to AI vs. keep human; review checklist for AI-drafted artifacts                     |

---

## PHASE 5: ASSETS

Generate at minimum:

- `assets/project-charter.md` — copy-paste charter template
- `assets/risk-register.csv` — spreadsheet-ready risk register with column headers
- `assets/raci-matrix.csv` — RACI template
- `assets/status-report.md` — weekly status report template
- `assets/sprint-planning.md` — sprint planning agenda + Sprint Goal template
- `assets/retrospective.md` — retro template (Start/Stop/Continue default)
- `assets/post-mortem.md` — blameless post-mortem template
- `assets/okr-template.md` — quarterly OKR template
- `assets/decision-record.md` — lightweight ADR / RFC template

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md includes the 14-field project charter anatomy
- [ ] SKILL.md includes the 15-technique PM techniques table with when-to-use
- [ ] SKILL.md includes the 12-field risk register schema with severity bands
- [ ] SKILL.md includes the RACI rule "exactly one A per row"
- [ ] SKILL.md includes the OKR scoring rule "0.7 is a good score"
- [ ] SKILL.md includes the RAG rule "never go from Green directly to Red"
- [ ] SKILL.md includes the DORA Four Keys table with Elite/High/Medium/Low bands
- [ ] At least 9 reference files generated (the 5 base + at least 4 PM-specific)
- [ ] At least 7 assets generated (charter, risk register, RACI, status, retro, post-mortem, OKR)
- [ ] Every artifact template uses real placeholders (`{sponsor-name}`, `{sprint-N}`) — never `xxx` or `foo`
- [ ] Includes guidance on **NOT** writing code — this skill is delivery-management-first
- [ ] PMBOK 7 referenced as current (not PMBOK 6)
- [ ] PRINCE2 7 referenced as current (not PRINCE2 2017)
- [ ] Scrum Guide 2020 terminology used ("Developers", three accountabilities, commitments)

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                                  | Why                                                                                |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Write "improve communication" as a retro action                        | Vague, no owner, no metric — guaranteed to recur next sprint                       |
| Set OKRs with output as the Key Result ("ship feature X")              | Outputs aren't outcomes; rewards motion over impact                                |
| Assign multiple Accountable on a RACI row                              | Diffuses ownership; "everyone is responsible" = nobody is                          |
| Convert story points to hours                                          | Defeats the purpose; story points are relative complexity, hours are absolute time |
| Skip the "Out of Scope" section in a charter                            | 80% of scope creep starts here                                                     |
| Go from RAG Green directly to Red                                      | Means you weren't tracking honestly; Amber is the warning                          |
| Run blameful post-mortems                                              | Kills psychological safety; future incidents get hidden                            |
| Use velocity to compare teams                                          | Velocity is calibrated per-team; cross-team comparison is meaningless              |
| Estimate in hours during Scrum planning                                | Forces false precision; Fibonacci story points are the convention                  |
| Treat AI-drafted status reports as final                                | AI misses political context, exec tone, real risk severity                         |
| Cargo-cult the Spotify model                                           | Spotify themselves moved on; copying it without context is anti-pattern            |
| Force Scrum on an ops / support team                                    | Kanban fits unpredictable arrival rates; Scrum forces artificial sprint boundaries |
| Run a daily standup that's just status updates to the PM               | Daily Scrum is for the team to coordinate, not for the PM to extract status        |
| Create a Gantt chart for an exploratory R&D project                    | False precision; use rolling-wave planning + adaptive forecasting                  |
| Skip the Definition of Done in agile                                    | Without it, "done" drifts; quality erodes invisibly                                |
| Plan capacity at 100% utilization                                      | Leaves zero room for incidents, sick days, focus work; 70–80% is realistic         |
| Track risks once at project kickoff and never re-score                  | Risks evolve; stale registers are decorative                                       |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

The generated skill MUST include the base "Communication Style" section. For project-manager specifically, when asked for an artifact (charter, status, retro, RACI, plan), the AI should ALWAYS:

1. Confirm scope (which project, what audience, what time period)
2. State the framework being applied (PMBOK 7 / Scrum / Kanban / hybrid) so the user sees the lens
3. Output as a complete structured artifact — table, list, or template — never prose narration
4. Cite the technique used (e.g., "RICE scoring", "PERT 3-point estimation")
5. Number every risk, every action item, every test of decision
6. Mark every action item with **owner + due date** — never an unowned item

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY project management task — project planning, charter writing, RACI, stakeholder management, sprint planning, retros, status reports, roadmaps, OKR drafting, risk management, post-mortems, milestone tracking, estimation, scope negotiation, agile/predictive method selection, hybrid tailoring.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep` (no language-specific subprocess scoping — PM is methodology-focused, not language-specific).

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (PM artifact requests, methodology questions, retros, status drafting)
2. **Do NOT Use** — cross-references to sibling skills (engineering skills for code, manual-tester for QA artifacts, future product-manager for strategy)
3. **Delivery Approach Detection** — predictive / agile / hybrid signals from the project scan
4. **Key Artifacts** — summary table only (artifact name, when, who owns). Full templates in references/
5. **Artifact Style** — naming, tone, structure rules. Full examples in references/artifact-style.md
6. **Common Recipes** — numbered step lists only ("Run a sprint planning", "Write a status report", "Facilitate a retro")
7. **Risk Management** — register schema + severity bands + protocol
8. **Stakeholder + Communication** — RACI rule + power/interest grid + comms cadence
9. **Metrics** — DORA + SPACE + OKRs; rules list, no code
10. **AI Usage Boundaries** — what to delegate to AI vs. keep human
11. **Anti-Patterns** — the "Never" table from Phase 7
12. **References** — key artifacts, frameworks, books
13. **Adaptive Interaction Protocols** — interaction modes with PM-specific detection signals (e.g., "draft a status report" for Efficient, "what's RACI" for Teaching, "the project is on fire" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/artifact-style.md` — naming, tone, structure for PM docs
- `references/charter-templates.md` — predictive + agile + hybrid charters
- `references/risk-register-template.md` — full risk register with scoring + response strategies
- `references/raci-and-stakeholder-templates.md` — RACI + stakeholder register + power/interest grid
- `references/status-report-templates.md` — weekly / monthly / executive with RAG
- `references/retro-and-postmortem-templates.md` — multiple retro formats + blameless post-mortem
- `references/okr-templates.md` — good vs. bad OKR examples
- `references/estimation-techniques.md` — PERT, planning poker, RICE, MoSCoW with worked examples
- `references/agile-vs-predictive-tailoring.md` — decision matrix + hybrid recipes
- `references/security-checklist.md` — PM artifact security (don't leak PII in status reports, vendor data classification, regulator escalation paths)
- `references/ai-interaction-guide.md` — AI delegation boundaries + review checklists
- `references/common-issues.md` — common PM pitfalls (scope creep, stale risks, vague retros, over-utilized teams)
- `assets/project-charter.md`, `assets/risk-register.csv`, `assets/raci-matrix.csv`, `assets/status-report.md`, `assets/sprint-planning.md`, `assets/retrospective.md`, `assets/post-mortem.md`, `assets/okr-template.md`, `assets/decision-record.md`
- `scripts/validate-pm-artifacts.sh` — checks naming, presence of required sections (e.g., charter has Out-of-Scope, risk register has owners, retros have action items with owners + dates)

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent              | Role                                                            | Tools                          | Spawn When                                                                       |
| ------------------ | --------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| status-synthesizer | Read-only — scan commits / PRs / issues to draft status reports | Read Glob Grep Bash            | Weekly / monthly status report request                                           |
| risk-scanner       | Read-only — surface risks from postmortems, code, dependencies  | Read Glob Grep                 | Risk-register refresh, milestone planning, audit prep                            |
| retro-facilitator  | Read-only — cluster feedback, surface patterns, propose actions | Read Glob Grep                 | Sprint retrospective prep, post-mortem analysis                                  |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/status-synthesizer.md` — read-only status drafting agent
- `agents/risk-scanner.md` — read-only risk identification agent
- `agents/retro-facilitator.md` — read-only retro pattern-clustering agent

Note: ALL recommended PM sub-agents are **read-only**. The PM skill itself should be cautious about modifying tracker state (issues, PRs) without explicit human approval — this is a key boundary.

---

## EXECUTION ORDER

```
[ ] 1. Scan project for delivery cadence, methodology signals, existing PM artifacts (Phase 1)
[ ] 2. Synthesize delivery method, stakeholder map, risk seed, artifact inventory to /tmp (Phase 2)
[ ] 3. Generate SKILL.md with all numbered rule lists (Phase 3) and modern-standards sections (Phase 2.5)
[ ] 4. Generate INJECT.md (50-150 token quick ref)
[ ] 5. Generate LEARNED.md (empty template with section headers)
[ ] 6. Generate the 9+ reference files (Phase 4)
[ ] 7. Generate the 7+ asset templates (Phase 5)
[ ] 8. Generate scripts/validate-pm-artifacts.sh (checks naming, required sections, owner+date on action items)
[ ] 9. Generate agents/ files (if skill warrants delegation — all read-only per PM safety boundary)
[ ] 10. Run quality gates (Phase 6)
[ ] 11. Verify all anti-patterns appear in SKILL.md "Never" table (Phase 7)
```

---

## SOURCES (for the AI to cite if asked)

- PMBOK Guide 7th Edition — released 2021 ([PMI](https://www.pmi.org/standards/pmbok))
- PRINCE2 7th Edition — released 2023 ([PeopleCert / Axelos](https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2))
- Scrum Guide 2020 — Schwaber + Sutherland ([scrumguides.org](https://scrumguides.org/scrum-guide.html))
- SAFe 6.0 — Scaled Agile Framework ([scaledagileframework.com](https://scaledagileframework.com/))
- LeSS — Larman + Vodde ([less.works](https://less.works/))
- DORA Four Keys — Accelerate / DORA State of DevOps ([dora.dev](https://dora.dev/))
- SPACE framework — Forsgren et al., ACM Queue 2021 ([queue.acm.org](https://queue.acm.org/detail.cfm?id=3454124))
- OKRs — Doerr, "Measure What Matters" ([whatmatters.com](https://www.whatmatters.com/))
- Mendelow's stakeholder matrix — power/interest grid (Mendelow, 1991)
- Edmondson — psychological safety ("The Fearless Organization", 2018)
- Blameless post-mortems — Google SRE Workbook ([sre.google](https://sre.google/workbook/postmortem-culture/))
- Architecture Decision Records — Nygard ([thoughtworks.com](https://www.thoughtworks.com/insights/blog/architecture/architecture-decision-records-help-teams))
