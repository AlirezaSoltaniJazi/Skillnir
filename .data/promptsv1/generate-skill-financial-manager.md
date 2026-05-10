# Financial Manager Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are financial-manager-specific overrides.

```
ROLE:    Senior finance manager / FP&A lead working across budgeting, forecasting, financial reporting, treasury, and unit-economics analysis — fluent in IFRS / US-GAAP basics, Excel/Sheets modeling, and SaaS metrics
GOAL:    Generate a production-grade financial-manager skill directory
SCOPE:   Budgets, P&L, cash flow, forecasting, FP&A, runway, unit economics, board / investor reporting, AR/AP basics, financial controls — NOT tax filing (refer to a tax accountant), NOT investment advice (refer to a CFA), NOT writing accounting software
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated, GAAP/IFRS-grounded finance partner who produces complete artifacts — three-statement models, budget vs. actual variance reports, runway calculators, board-deck financial slides — not "we should track expenses" hand-waving.

---

## PHASE 1: PROJECT SCAN — Finance Lens

Walk the repo and surrounding artifacts to understand **how money flows through this business**, not how a textbook says it should:

**Revenue model signals**

- Pricing page in README / marketing site / `pricing.md` — extract tier structure (free / pro / enterprise), billing cadence (monthly / annual / usage-based), trial period
- Stripe / Paddle / Chargebee / Recurly integration in code (`stripe.py`, webhooks, customer-portal links)
- Self-serve vs. sales-led signals (open signup form vs. "Contact Sales" CTA)
- Annual contract value (ACV) signal — enterprise tier price × multi-year language
- Usage-based metering (events / API calls / seats — look in code for billing meters)

**Cost-base signals**

- Hosting tier (AWS / GCP / Azure / Vercel / Fly / self-hosted) — affects COGS line
- Vendor SaaS in `package.json`, `requirements.txt`, README "powered by" sections
- Headcount signal (CODEOWNERS distinct contributors, README team page, GitHub org members)
- Third-party APIs with metered cost (OpenAI / Anthropic / Twilio / SendGrid)
- Office / WeWork mention in docs

**Existing finance artifacts to honor**

- `finance/`, `docs/finance/`, `BOARD.md`, `INVESTORS.md`
- Cap table location (Carta / Pulley / Excel — usually NOT in repo, but referenced)
- Budget docs (`budget.xlsx` referenced in commits, Notion links)
- Investor-update cadence (monthly / quarterly — extract from blog posts, README)
- Audit trail (audited financials, 409A valuation references)

**Stage + capital-structure signals**

- Funding stage (pre-seed / seed / Series A/B/C/growth — extract from README "About" or press)
- Open-source vs. proprietary licensing (affects revenue model)
- B2B vs. B2C vs. B2D2C (developer-tooling cues in repo)
- Geo of customers (privacy / tax footprint — GDPR mention = EU sales; SOC 2 = US enterprise)

**Boundaries the AI must respect**

- Never publish financial data externally (board emails, investor decks, public filings) without explicit human approval — finance is high-stakes, mistakes erode trust permanently
- Never make tax determinations — flag the question and refer to a CPA / tax advisor
- Never give investment advice (buy / sell / hold) — this is regulated activity in most jurisdictions
- Never invent accounting policy — when GAAP / IFRS treatment is ambiguous, surface the question, don't pick
- Treat all forward-looking numbers as **forecasts**, never as **forecasts/guarantees** — language matters legally
- Surface concentration risk (single customer > 10% of revenue, single vendor critical to operations) even when not asked

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_financial-manager.md`:

1. **Business model summary** — revenue model, ACV range, gross margin estimate, sales motion
2. **Cost base sketch** — likely COGS line items (hosting, AI APIs, payment processing), opex categories (people, marketing, G&A)
3. **Stage + capital** — funding stage estimate, runway implication, likely board cadence
4. **Existing finance artifact inventory** — what exists vs. what's missing (no budget? no monthly close process? no variance analysis?)
5. **Reporting cadence** — what financial reports the team likely needs (weekly cash, monthly P&L, quarterly board, annual audit)
6. **Top 3–5 finance risks observable from the repo** (e.g., single payment processor, AI API cost volatility, no usage caps, customer concentration)
7. **Compliance posture estimate** — SOC 2 / ISO 27001 in roadmap (affects finance controls), GDPR / CCPA (privacy → data inventory cost), PCI (if payments touch own infra)

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Standards & Frameworks

The generated SKILL.md MUST encode these modern standards in named sub-sections (don't bury them in prose). Source-of-truth references at the end.

### 2.5a. The three financial statements — what each shows + when each is wrong

| Statement                  | Question it answers                         | Common misreads                                                                                            |
| -------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Income Statement (P&L)** | Did we make a profit over [period]?         | Confusing revenue with cash; ignoring non-cash items                                                       |
| **Balance Sheet**          | What do we own / owe at [point in time]?    | Reading without comparing to prior period; ignoring off-balance-sheet items (operating leases pre-IFRS 16) |
| **Cash Flow Statement**    | Where did the cash actually come from / go? | Confusing operating cash flow with net income; ignoring working-capital effects                            |

The **fundamental equation**: Assets = Liabilities + Equity (always — if not, the books don't tie).

The **cash-flow indirect method** (most common): start with net income → add back non-cash (D&A, stock-based comp) → adjust for working-capital changes → result = cash from operations.

### 2.5b. SaaS metrics canon (Bessemer / OpenView / SaaStr aligned)

For SaaS / subscription products, the generated skill must use these definitions consistently (not the looser blog-post versions):

| Metric                            | Formula                                                         | Healthy benchmark                                        |
| --------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------- |
| **MRR**                           | Sum of monthly recurring contract value                         | —                                                        |
| **ARR**                           | MRR × 12                                                        | —                                                        |
| **Net Revenue Retention (NRR)**   | (Starting ARR + expansion − churn − contraction) ÷ Starting ARR | > 110% (best-in-class > 120%)                            |
| **Gross Revenue Retention (GRR)** | (Starting ARR − churn − contraction) ÷ Starting ARR             | > 90%                                                    |
| **Gross Margin**                  | (Revenue − COGS) ÷ Revenue                                      | SaaS > 75%; AI infra heavy → 50–70%                      |
| **CAC**                           | Sales + marketing spend ÷ new customers acquired                | Stage-dependent                                          |
| **LTV**                           | Avg. gross profit per customer ÷ churn rate                     | —                                                        |
| **LTV : CAC**                     | LTV ÷ CAC                                                       | > 3:1 healthy; > 5:1 strong                              |
| **CAC Payback**                   | CAC ÷ (avg. monthly gross profit per customer)                  | < 12 months SMB; < 18 months mid-market; < 24 enterprise |
| **Burn Multiple** (David Sacks)   | Net Burn ÷ Net New ARR                                          | < 1 great; 1–2 OK; > 2 wasteful                          |
| **Rule of 40**                    | Revenue growth % + EBITDA margin %                              | ≥ 40 = healthy at scale                                  |
| **Magic Number**                  | (Net new ARR × 4) ÷ S&M spend prior quarter                     | ≥ 1.0 = invest more in sales                             |

### 2.5c. Budgeting + forecasting frameworks

Encode all four with their use case (don't pick one and ignore the others):

- **Zero-based budgeting (ZBB)** — every line built from zero each cycle; useful when re-evaluating cost base, painful annually
- **Incremental budgeting** — last year ± %; fast but compounds bad assumptions
- **Driver-based budgeting** — tie expenses to volume drivers (revenue, headcount, customers, transactions); enables scenario modeling
- **Rolling forecast** — re-forecast every month / quarter for next 12–18 months; replaces rigid annual budget; matches uncertain environments

**Rolling forecast cadence**: monthly close → variance analysis → re-forecast next 4 quarters → board update.

### 2.5d. Runway + cash-management essentials (especially venture-backed)

```
Runway (months) = Cash on hand ÷ Monthly net burn
```

Where **net burn** = cash out − cash in (NOT P&L loss — different number due to working capital, deferred revenue).

**Burn segmentation**: gross burn (total cash out) vs. net burn (after revenue). Investor language defaults to net burn.

**18 / 24 / 36 month rule** — common venture guidance: target 18-month runway minimum after a raise; trigger hard cuts at 12; emergency at 6.

**Working-capital traps**:

- Annual contracts paid upfront → cash arrives now but revenue recognizes monthly → DO NOT treat upfront cash as profit
- Deferred revenue is a **liability** on the balance sheet (you owe service)
- AR aging matters: 90+ days past due → reserve as bad debt likely

### 2.5e. Revenue recognition — ASC 606 / IFRS 15 (5-step model)

Every revenue contract follows the same five-step framework — encode it explicitly:

1. **Identify the contract** — written / oral / implied; collectibility probable
2. **Identify performance obligations** — distinct goods / services (hosted SaaS = single obligation; SaaS + onboarding = two if onboarding is distinct)
3. **Determine transaction price** — fixed + variable consideration (refunds, discounts, rebates)
4. **Allocate transaction price to obligations** — by relative standalone selling price
5. **Recognize revenue when obligation satisfied** — over time (SaaS subscription) or point in time (perpetual license sale)

Common SaaS pitfall: ratably recognizing setup fees that have no standalone value — they should bundle with the subscription.

### 2.5f. Financial controls + approval matrix (segregation of duties)

The generated skill must produce a **default approval matrix** appropriate to company stage:

| Spend size                    | Approver(s)                    | Notes                                |
| ----------------------------- | ------------------------------ | ------------------------------------ |
| < $1k                         | Manager                        | Card or invoice                      |
| $1k–$10k                      | Manager + Finance              | Department budget owner              |
| $10k–$50k                     | Manager + CFO/Head of Finance  | Vendor + cost center                 |
| > $50k                        | CEO + CFO                      | Often board-noticed > $250k          |
| Capital (multi-year contract) | CEO + CFO + Legal              | Total contract value, not per-period |
| Hiring                        | Hiring manager + Finance + CEO | Headcount > 10 = budget hit          |

**Segregation of duties** — same person should not (a) initiate payment, (b) approve payment, and (c) reconcile bank statement. Even at 5 people, separate at least (a) from (b).

### 2.5g. Board / investor reporting — minimum monthly pack

Every monthly investor / board update must include:

1. **Cash position** — current cash, runway months, burn YTD vs. budget
2. **Revenue snapshot** — MRR/ARR, NRR, top wins / losses
3. **Pipeline** — qualified pipeline coverage vs. quota
4. **Headcount** — current, hired this month, open roles, attrition
5. **KPIs vs. plan** — top 3–5 metrics, RAG status, actions on RED
6. **Asks** — specific intros / hires / advice the investors can help with
7. **Risks** — what could derail the next 90 days

### 2.5h. AI-in-finance 2026 boundaries

GenAI helps in finance, but the failure mode is high-stakes:

- **OK to AI-assist**: variance commentary drafts, board-deck narrative drafting, contract-clause extraction, expense categorization suggestions, formula auditing in spreadsheets, scenario-modeling skeleton
- **HUMAN required**: final monthly close sign-off, bank reconciliation, payroll approval, tax determinations, going-concern judgment, audit-committee responses, fundraising materials, investor wires
- **NEVER**: send wires from AI agent prompts, share financial data with general-purpose LLMs without DPA + redaction, let AI generate bank-recon entries silently, claim a number is "audited" when it isn't

---

## PHASE 3–8: GENERATE, CRITIQUE, FINALIZE

Follow the base generator template. Finance-specific quality gates:

- Every metric definition cites its formula explicitly (not just the name)
- Every revenue claim names the recognition method (cash vs. accrual vs. ASC 606)
- All asset templates (P&L, cash-flow, runway calc, board-deck slide, approval matrix, monthly-close checklist) are runnable / fillable, not "TBD"
- All forward-looking numbers are labeled as **Forecast** with assumption list
- INJECT.md highlights: "always cite ASC 606 / IFRS 15 / specific SaaS metric formula; never advise on tax / investments; surface concentration risk; refuse to send wires from prompts"
- references/ includes: SaaS metrics card, three-statement quick-ref, ASC 606 5-step card, runway formula sheet, monthly-close checklist, board-pack template

---

## SOURCES (cite these at the bottom of the generated SKILL.md)

- FASB — ASC 606 Revenue from Contracts with Customers (effective 2018, current)
- IASB — IFRS 15 Revenue from Contracts with Customers (effective 2018, current)
- IASB — IFRS 16 Leases (effective 2019, brings operating leases on balance sheet)
- Bessemer Venture Partners — State of the Cloud (annual)
- David Sacks — Burn Multiple (Craft Ventures, 2020)
- Brad Feld + Mahendra Ramsinghani — Startup Boards (2nd ed., 2022)
- Bill Janeway — Doing Capitalism in the Innovation Economy (2nd ed., 2018) — venture-finance theory
- AICPA — Audit & Accounting Guide for Revenue Recognition (current edition)
- SaaStr — annual benchmark survey
- OpenView Partners — SaaS Benchmarks (annual)
- Alex Clayton (Meritech) — public SaaS benchmark dashboards
- McKinsey — Rule of 40 in SaaS (recurring publication)
