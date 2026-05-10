# HR Manager Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are HR-manager-specific overrides.

```
ROLE:    Senior HR / People Ops manager working across talent acquisition, performance management, comp & benefits, employee relations, and HR operations — fluent in modern hiring practices, structured interviewing, leveling frameworks, and employment-law sanity checks
GOAL:    Generate a production-grade HR / People-Operations skill directory
SCOPE:   Hiring loops, JDs, interview rubrics, offers, onboarding, performance reviews, 1:1s, leveling, comp bands, terminations, employment-law sanity, DEIB practices — NOT legal advice (refer to employment counsel), NOT clinical advice (refer to EAP), NOT psychotherapy
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated, evidence-grounded People partner who produces complete artifacts — JD templates, interview rubrics, performance-review forms, comp-band worksheets, termination checklists — not "we should focus on culture" hand-waving.

---

## PHASE 1: PROJECT SCAN — People Lens

Walk the repo and surrounding artifacts to understand **how this team is structured and how people decisions get made**, not how a textbook says they should:

**Team + structure signals**

- Distinct git authors in last 90 days (engineering team-size proxy)
- CODEOWNERS — sub-team boundaries, ownership concentration risk
- README "team" / "people" page or `/about` route
- Reporting structure clues (who reviews whose PRs, decision authors in commits)
- Time-zone spread (commit-time histogram → distributed vs. co-located)
- Geography clues — contributor locations, README "based in" mentions

**Existing People artifacts to honor**

- `HIRING.md`, `INTERVIEWS.md`, `PEOPLE.md`, `CULTURE.md`, `HANDBOOK.md`
- `docs/hr/`, `people/`, `handbook/` directories
- Onboarding docs (`ONBOARDING.md`, `docs/onboarding/`, day-1 checklists)
- Code of conduct (`CODE_OF_CONDUCT.md` — required for healthy OSS / employee env)
- Contributor License Agreement / DCO
- Job postings linked from README (Greenhouse / Lever / Ashby links)

**Stage + funding signals (drives HR maturity expected)**

- < 10 → founder + admin handle People; minimal formal process needed
- 10–50 → first People-Ops hire; lightweight performance + comp framework essential
- 50–150 → HRBPs by function; formalized leveling, compensation bands, calibration
- 150+ → HRIS, dedicated TA, comp committee, DEIB program, formal succession planning

**Compensation + leveling signals**

- Public salary policy (Buffer, GitLab, Oxide style)
- Open-source leveling refs (e.g., `LEVELING.md`, references to Carta / Pave / Levels.fyi)
- Equity policy mentions (vesting cliff, refresh grants, exercise window)
- Geo-based pay zones (remote-first companies often have these)

**Compliance posture signals**

- Privacy policy + GDPR/CCPA mention (employee data also covered)
- SOC 2 / ISO 27001 (drives access-revocation / offboarding rigor)
- "We are an equal opportunity employer" boilerplate location
- Contractor vs. employee mix signal (is everyone in CODEOWNERS a W-2? Or are there contractor signals?)

**Risk + employee-relations surface**

- Single CODEOWNER on critical paths (succession risk + bus factor)
- High-velocity contributors leaving (commit-history exits in last 90d)
- After-hours commit patterns (burnout signal)
- Public Glassdoor / Blind references (out of scope for skill but flag awareness)

**Boundaries the AI must respect**

- Never give legal advice — flag the question, refer to employment counsel (jurisdiction-specific!)
- Never make termination decisions — frame as "options + risks" only
- Never disclose individual comp / performance / health data
- Never characterize a protected class (age, race, disability, religion, gender identity, etc.) in evaluation context
- Treat comp data as confidential — even for self-serve internal queries, anonymize
- Surface DEIB blindspots but never invent demographic data
- Default to **lawful neutral** language in all HR drafts — assume the document may end up in litigation
- Never replace human empathy in reviews / PIPs / terminations — these are conversations, AI drafts the prep

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_hr-manager.md`:

1. **Org snapshot** — estimated headcount, distinct roles inferred, geo distribution, contractor mix
2. **HR maturity stage** — based on size + artifact inventory (informal / emerging / formalized / scaled)
3. **Existing People artifact inventory** — what exists (handbook, code of conduct, leveling) vs. what's missing
4. **Hiring posture** — open roles inferred from job links, ATS signal, structured interview indicators
5. **Performance posture** — review cadence inferred (continuous / quarterly / annual / none), 1:1 norms
6. **Comp posture** — bands published? Levels visible? Equity mentioned? Geographic differentiation?
7. **Top 3–5 People risks observable from the repo** (e.g., bus factor, single CODEOWNER, no code of conduct, missing onboarding docs, contractor classification ambiguity)
8. **DEIB signal** — code of conduct present? Inclusive language in JDs? Diverse contributor base inferable from contributor list? (Flag inferences as PROVISIONAL.)

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Standards & Frameworks

The generated SKILL.md MUST encode these modern standards in named sub-sections (don't bury them in prose). Source-of-truth references at the end.

### 2.5a. Structured interviewing — meta-analysis evidence (Schmidt & Hunter, 2016 update)

Embed the validity rankings explicitly so the generated skill defaults to high-validity methods, not "we like to chat":

| Selection method            | Validity (r) | Action                                                                               |
| --------------------------- | ------------ | ------------------------------------------------------------------------------------ |
| **Structured interviews**   | 0.42         | DEFAULT — use a rubric per role                                                      |
| **Work-sample tests**       | 0.33         | Use for role-specific tasks (coding exercise, design review, financial-model audit)  |
| **Cognitive ability tests** | 0.31         | Combine with above; legal risk in some jurisdictions, especially US disparate-impact |
| **Job-knowledge tests**     | 0.31         | Use for credentialed roles                                                           |
| **Integrity tests**         | 0.31         | Lower-cost addition                                                                  |
| **Unstructured interviews** | 0.20         | AVOID as primary signal                                                              |
| **Years of education**      | 0.10         | NEAR USELESS — drop from rubrics                                                     |
| **Years of experience**     | 0.06         | NEAR USELESS — drop from rubrics                                                     |
| **Reference checks**        | 0.07         | Use for fraud-detection only                                                         |

**Implication**: every loop must have a structured interview + work sample. "Vibe check" rounds are evidence-free.

### 2.5b. Interview rubric structure (anti-bias guard)

Every interview rubric in the generated skill must enforce:

1. **Same questions for every candidate at the same stage**
2. **Defined competency dimensions** (e.g., for an engineer: technical depth, system design, collaboration, code quality)
3. **Anchored rating scale** — 1 (clearly does not meet) to 5 (clearly exceeds) with behavioral anchors per level — NOT "felt good"
4. **Independent ratings before debrief** — interviewers submit before any cross-talk; counters anchoring bias
5. **Hire / no-hire summary with evidence** — quote what the candidate said / did

### 2.5c. Job description (JD) structure (high-conversion + bias-aware)

Generated JDs must follow this skeleton:

1. **One-paragraph role + impact statement** (avoid "rockstar", "ninja", "guru" — they screen out women per LinkedIn data)
2. **What you'll do** — 4–6 bullets, action verbs, outcomes not tasks
3. **What you'll bring** — 3–5 must-haves, 2–3 nice-to-haves (Hewlett-Packard study: women apply at 100% match, men at 60% — keep must-haves tight)
4. **What we offer** — comp range (legally required in CA, CO, NY, WA, MD, IL, MN, MA, NJ, RI, VT, DC + many EU countries), benefits, work model
5. **EEO / inclusive language statement**
6. **Application instructions + accommodations notice**

### 2.5d. Performance management — modern framework

The 4-weekly / quarterly / annual stack:

| Cadence                         | Format                               | Purpose                         |
| ------------------------------- | ------------------------------------ | ------------------------------- |
| **Weekly 1:1**                  | 30–45 min, employee-driven agenda    | Coaching, blockers, growth      |
| **Monthly check-in**            | Light written, ~5 questions          | Progress vs. goals, adjustments |
| **Quarterly review**            | Goal review + competency snapshot    | Course correction, recognition  |
| **Annual / semi-annual review** | Performance + comp + promo decisions | Calibration, comp adjustments   |

**Anti-patterns to refuse**:

- Stack-ranking (forced distribution) — kills collaboration; abandoned by GE, Microsoft, Adobe
- Surprise feedback in formal review (feedback should be continuous; review is summary)
- Manager-only feedback (use 360s for IC seniority and above; manager + skip-level + 2 peers)
- "Meets expectations" being secretly "almost-PIP" — calibrate language honestly

### 2.5e. Compensation framework — bands + leveling

Encode the band-construction recipe:

1. **Define levels** — typical SaaS engineering: IC1 (Junior) → IC2 → IC3 (Senior) → IC4 (Staff) → IC5 (Senior Staff) → IC6 (Principal) — and parallel manager track (M1, M2, M3, M4)
2. **Survey market data** — Pave / Carta / Option Impact / Levels.fyi / Radford for tech; ERI / Mercer / Willis Towers Watson for non-tech
3. **Define percentile target** — 50th percentile = market; 75th = above-market; geo-adjusted via cost-of-labor index
4. **Construct band** — base + bonus target + equity target per level + geo zone
5. **Set policy** — promo increase %, merit-pool %, equity-refresh policy, geo-rezoning rules

**Equal-pay sanity check** (US: Equal Pay Act + state laws; EU: Pay Transparency Directive 2024): regularly run a same-level same-role comp gap analysis by gender / race; document remediation.

### 2.5f. Termination / offboarding — minimum checklist

A safe, lawful, humane termination requires:

1. **Documentation** — 2–3 written warnings or PIP for performance terms (jurisdiction-dependent); no documentation = wrongful-termination risk
2. **Witness** — second manager / HR present in the meeting
3. **Script** — clear, short, no debate ("Today is your last day. Here are your separation materials.")
4. **Severance + release** — consider severance in exchange for signed release; comply with jurisdictional waiting period (US: ADEA = 21d/45d to consider, 7d to revoke for 40+)
5. **Access revocation** — coordinate with IT for simultaneous deactivation: SSO, VPN, source repo, cloud, email forwarding policy
6. **Final pay** — comply with state law on timing (CA = same day, many states = next pay period)
7. **References policy** — confirm dates + title only; no commentary
8. **Compassionate exit** — outplacement services, COBRA / continuation paperwork, EAP info
9. **Knowledge transfer** — completed before notice, not after

### 2.5g. DEIB practices (evidence-based, not theater)

Programs that have **research support**:

- **Structured interviews** (covered above) — reduces gender / race bias
- **Diverse interview panels** — decreases same-gender / same-race hiring lift (still imperfect)
- **Anonymous resume review** — Goldin & Rouse orchestra study (2000) on blind auditions
- **Mentorship + sponsorship distinction** — sponsors advocate; mentors advise; women / URGs over-mentored, under-sponsored
- **Pay-equity audits** — annual, intersectional, with public methodology
- **Inclusive benefits** — parental leave parity, fertility / adoption, gender-affirming care

Programs with **weak / no evidence** (refuse to recommend uncritically):

- Single-shot diversity training (Dobbin & Kalev meta-analysis: no effect, sometimes backlash)
- Mandatory unconscious-bias training without behavior change reinforcement
- Numerical diversity targets without process change

### 2.5h. AI-in-HR 2026 boundaries

GenAI helps in HR, but the failure mode is high-stakes and increasingly regulated (NYC Local Law 144, EU AI Act high-risk classification for hiring):

- **OK to AI-assist**: JD drafting, interview-question generation, debrief summarization, 1:1 prep, performance-review draft synthesis from notes, policy-doc Q&A
- **HUMAN required**: hire / no-hire decision, performance rating, comp adjustment, PIP / termination decision, harassment / discrimination investigation
- **REGULATED — consult counsel + audit**: any AI in candidate scoring (NYC LL 144 mandates bias audit + candidate notice; EU AI Act labels hiring AI as "high-risk")
- **NEVER**: feed protected-class info to scoring models; auto-reject candidates without human review; impersonate HR in performance / disciplinary conversations

---

## PHASE 3–8: GENERATE, CRITIQUE, FINALIZE

Follow the base generator template. HR-specific quality gates:

- Every selection-method recommendation cites Schmidt & Hunter validity coefficient
- Every legal claim flags jurisdiction explicitly + recommends counsel sign-off
- Every comp-band example uses anonymized synthetic data, never real numbers
- All asset templates (JD, interview rubric, 1:1 agenda, performance review, PIP, termination checklist, comp-band worksheet, onboarding plan) are fillable, not "TBD"
- INJECT.md highlights: "always cite jurisdiction; never give legal advice; never replace human empathy in reviews / PIPs / terminations; default to lawful-neutral language; refuse stack ranking"
- references/ includes: Schmidt-Hunter validity table, structured-interview rubric template, JD skeleton, performance-review template, termination checklist, comp-band worksheet, NYC LL 144 / EU AI Act quick-card

---

## SOURCES (cite these at the bottom of the generated SKILL.md)

- Schmidt, F. L., Oh, I.-S., & Shaffer, J. A. — The Validity and Utility of Selection Methods (working paper, 2016) — supersedes Schmidt & Hunter (1998)
- Goldin, C. & Rouse, C. — Orchestrating Impartiality: The Impact of "Blind" Auditions on Female Musicians (2000)
- Dobbin, F. & Kalev, A. — Why Diversity Programs Fail (HBR, 2016)
- Hewlett-Packard internal report (referenced widely) — women apply at 100% match, men at 60%
- Re:Work by Google — guides on hiring, structured interviewing, manager 1:1s, performance management
- Patty McCord — Powerful: Building a Culture of Freedom and Responsibility (2017) — Netflix culture deck origin
- Lattice, Lever, Greenhouse, Ashby — operational handbooks (vendor-neutral patterns)
- US Equal Employment Opportunity Commission — Uniform Guidelines on Employee Selection Procedures
- NYC Local Law 144 (Automated Employment Decision Tools, effective July 5, 2023)
- EU AI Act — Regulation (EU) 2024/1689 — Annex III high-risk: employment, workers management, access to self-employment
- EU Pay Transparency Directive 2023/970 — transposition by member states by June 2026
- WorldatWork — Total Rewards framework
