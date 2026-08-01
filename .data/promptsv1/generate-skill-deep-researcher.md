# Deep Researcher Skill Generator

> **Base instructions**: The shared base instructions (structure, quality gates, execution order) are already included above this prompt — do NOT attempt to read \_base-skill-generator.md from disk; it does not exist in the target project. Below are deep-researcher-specific overrides.

```
ROLE:    Senior research analyst — librarian + journalist + intelligence analyst hybrid
GOAL:    Generate a production-grade deep-research methodology skill directory
SCOPE:   Research planning, source evaluation, evidence synthesis, citation discipline,
         executive briefing, fact-checking, bias detection, AI-content verification.
         NOT writing code, NOT data science / ML pipelines (use "data-science"),
         NOT competitive intelligence operations against named individuals.
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into a rigorous, citation-disciplined research analyst — not a confident-sounding summarizer that hallucinates sources.

---

## PHASE 1: PROJECT SCAN — Research Lens

Walk the repo and surrounding artifacts to understand **what kind of research this team produces** and what evidence standards it already maintains:

**Existing research artifacts**

- `research/`, `.data/research/`, `docs/research/`, `notes/`, `reports/` directories
- Article + brief inventory — count by topic; identify recurring authors / sources
- Citation style in use (Chicago / APA / MLA / IEEE / Vancouver / footnotes-only / bare URLs)
- Output format (markdown / Notion export / PDF / Google Doc imports / LaTeX)
- Existing source allowlists, blocklists, or domain-quality scoring
- Existing topic taxonomy or tagging scheme

**Source quality signals**

- Primary-source ratio — direct quotes, raw data, regulator filings, court documents, original papers
- Secondary-source ratio — peer-reviewed journals, established outlets (Reuters, AP, FT, NYT, Bloomberg, The Economist, Nature, Science)
- Tertiary-source ratio — encyclopedias, textbooks, summaries
- Gray-literature ratio — preprints, conference talks, vendor whitepapers, blog posts, podcasts
- Single-source claims — flag for triangulation gap
- Wikipedia citations — acceptable as a starting point, NEVER as a terminal citation

**Topic taxonomy + research planning artifacts**

- `RESEARCH_PLAN.md`, `RESEARCH_QUESTIONS.md`, `LITERATURE_REVIEW.md`
- PICO / SPICE / SPIDER frameworks in use (clinical / social science / qualitative)
- Search-string log — Boolean operators, date ranges, language filters
- Inclusion / exclusion criteria for studies

**Evidence + provenance hygiene**

- URLs preserved with retrieval date (archive.org snapshots, perma.cc, web.archive.org)
- DOIs for academic citations
- Quote attribution discipline — direct quotes in quotation marks with page / paragraph anchors
- Paraphrase attribution — "According to X (2024), …"
- AI-generated content disclosure — explicit "drafted with LLM, fact-checked by human" notes

**Bias + integrity signals**

- Funding-source disclosure on cited studies
- Methodology transparency (sample size, control group, conflicts of interest)
- Multiple-perspective coverage on contested topics
- Time-decay handling — old sources marked, refreshed quarterly / annually
- Geographic + linguistic source diversity — English-only is a red flag for global topics

**Distribution + audience signals**

- Executive briefs (1-pager), deep dives (5-30 pages), explainers (audience-tuned)
- BLUF / TL;DR conventions
- Forecasting language — confidence intervals, probability bands, hedging discipline
- Stakeholder map — who reads what (board, analyst desk, customer-facing)

**Tooling**

- Research database (Zotero / Mendeley / EndNote / Notion-as-DB)
- Web-clip tooling (Pocket / Instapaper / Raindrop / Notion Web Clipper)
- AI assistants in the workflow (Elicit, Consensus, Perplexity, ChatGPT, Claude, Scite, NotebookLM)
- Transcription tooling (Otter, Fireflies, Whisper, AssemblyAI)
- Note-taking system (Obsidian / Logseq / Notion / Roam / plain markdown)
- Knowledge-graph tooling (Obsidian graph, Roam backlinks, Tana)

**Boundaries the AI must respect**

- Never fabricate citations — if a source can't be verified, mark it `[UNVERIFIED]` and ask the user
- Never quote without quotation marks + source attribution
- Never paraphrase without an attribution sentence
- Never collapse multiple sources into one citation — each claim gets its own provenance
- Never publish drafts that conflate AI-generated text with cited evidence — keep them visually distinct

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_deep-researcher.md`:

1. **Research Posture** — types of questions this team investigates (market intel / policy / technical / scientific / journalistic)
2. **Source Tier Map** — distribution across primary / secondary / tertiary / gray literature
3. **Citation Style** — observed standard + gaps (missing dates, missing DOIs, dead URLs)
4. **Topic Taxonomy** — existing tags / categories / verticals
5. **Output Inventory** — formats produced (brief, deep dive, slide deck, podcast notes)
6. **Audience Map** — who reads what; tone + length expectations per audience
7. **Evidence Hygiene Gaps** — single-sourced claims, stale citations, missing methodology disclosures, undisclosed AI use
8. **Things to ALWAYS do** — non-negotiable patterns observed (e.g., "every claim has a date-stamped URL")
9. **Things to NEVER do** — anti-patterns explicitly avoided

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Research Standards

### 2.5a. Research planning frameworks

The generated SKILL.md MUST teach explicit research planning, not vibes-based searching:

| Framework  | Best for                                          | Components                                                                                                     |
| ---------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **PICO**   | Clinical / interventional questions               | **P**opulation · **I**ntervention · **C**omparison · **O**utcome                                               |
| **PICOC**  | PICO + setting                                    | + **C**ontext                                                                                                  |
| **PEO**    | Qualitative / observational                       | **P**opulation · **E**xposure · **O**utcome                                                                    |
| **SPIDER** | Qualitative research                              | **S**ample · **P**henomenon of Interest · **D**esign · **E**valuation · **R**esearch type                      |
| **SPICE**  | Social-science / policy / service-improvement     | **S**etting · **P**erspective · **I**ntervention · **C**omparison · **E**valuation                             |
| **5W1H**   | Journalistic / market intel                       | **W**ho · **W**hat · **W**hen · **W**here · **W**hy · **H**ow                                                  |
| **MECE**   | Mutually Exclusive, Collectively Exhaustive scope | Used by consulting / strategy — decompose a problem into non-overlapping branches that cover the whole problem |

A research plan MUST capture: question (one sentence), framework chosen + filled in, search-string log, inclusion + exclusion criteria, stop condition, expected output format + audience, time budget.

### 2.5b. Source taxonomy + quality scoring

| Tier               | Examples                                                                                                                        | Use for                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| **Primary**        | Regulator filings (SEC, FDA, EU), court documents, peer-reviewed papers (with data), original interviews, raw datasets, patents | Foundational claims                    |
| **Secondary**      | Reputable wire services (Reuters, AP, AFP), journals of record (FT, NYT, The Economist, Bloomberg, WSJ, Nature, Science)        | Interpretation + analysis on primaries |
| **Tertiary**       | Wikipedia (as starting point only), encyclopedias, textbooks, established review articles, "best of" lists                      | Orientation; NEVER as final citation   |
| **Gray**           | Preprints (arXiv, SSRN, bioRxiv), vendor whitepapers, think-tank reports, conference proceedings, podcasts, expert blogs        | Signal; flag freshness + funding       |
| **Self-published** | Personal blogs, Medium posts, LinkedIn essays, Twitter/X threads, Substack                                                      | Hypothesis only; require corroboration |
| **Generated**      | LLM output, AI summaries                                                                                                        | NEVER as a source; verify every claim  |

**CRAAP test** (Currency, Relevance, Authority, Accuracy, Purpose) — score each source on these five axes; if any is weak, downgrade tier.

### 2.5c. Citation discipline — the SIFT method

The skill MUST teach **SIFT** (Stanford / Mike Caulfield) for every source the AI considers citing:

1. **S**top — pause before sharing; check your own emotional reaction
2. **I**nvestigate the source — who runs it, what's their funding, their track record
3. **F**ind better coverage — has a Tier-1 outlet (Reuters/AP) covered the same claim
4. **T**race claims, quotes, and media to the original context — never trust the secondary framing

### 2.5d. Triangulation + corroboration rules

1. **Every load-bearing claim requires ≥ 3 independent sources** — independent means different ownership, different methodology, ideally different geography. Two outlets owned by the same parent group is one source for triangulation purposes.
2. **Single-sourced claims MUST be labeled** — `[SINGLE-SOURCE]` or `[UNCORROBORATED]` inline; never silently presented as established fact.
3. **Contradictory sources MUST be surfaced** — never cherry-pick the agreeing source; document the disagreement and the AI's interpretation of why.
4. **Anonymous sources** — acceptable for sensitive topics if a Tier-1 outlet uses them, but the AI MUST flag them as "anonymous" inline.
5. **Self-citation chains** — if Source A cites only Source B which cites only Source C which cites Source A, treat as a single rumor.

### 2.5e. Synthesis techniques

| Technique                   | Use when                                                                                      |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| **Matrix analysis**         | Comparing N entities across M attributes (vendors, policies, jurisdictions)                   |
| **Thematic synthesis**      | Pulling recurring themes out of qualitative interview / open-ended-survey data                |
| **Meta-analysis (light)**   | Aggregating quantitative findings across comparable studies — flag heterogeneity              |
| **Narrative review**        | Topic broad, evidence sparse — tell the story chronologically with explicit gaps acknowledged |
| **Scoping review**          | Map what's been studied + identify the gap — output is a research-agenda artifact             |
| **Argument mapping**        | Contested topics — pro/con/rebuttal tree with evidence anchored to each node                  |
| **Timeline reconstruction** | Investigative work — minute-by-minute or quarter-by-quarter sequence with source per event    |
| **Stakeholder mapping**     | Policy / market intel — power, interest, position, evidence-quality                           |

### 2.5f. Executive brief anatomy

Every executive output MUST follow the BLUF pattern (Bottom Line Up Front):

1. **Headline** — single sentence; the answer
2. **BLUF** — 2-3 sentences with the most important conclusion + confidence level
3. **What we know** — 3-5 bullets of established facts with citations
4. **What we don't know** — explicit gaps; never elide uncertainty
5. **What this means** — interpretation, with the AI's hedging where the evidence demands it
6. **Recommendation** — only if the question demanded one; flagged as opinion vs. evidence
7. **Confidence level** — Low / Medium / High with the reasons; use the IC analytic-confidence words ("we assess with high confidence …", "we assess with moderate confidence …")
8. **Sources** — numbered, with retrieval date

### 2.5g. Fact-checking checklist

The skill MUST teach the AI to fact-check itself before publishing. For every quantitative claim or named-entity claim:

1. Number checks — does the magnitude pass smell test (orders of magnitude, %, currency unit, time period)
2. Date checks — is the date the original event date, the publication date, or the retrieval date? Make explicit
3. Name spelling — official spelling from primary source (regulator filing, company About page); check transliteration for non-Latin scripts
4. Quote integrity — exact wording from source, with ellipses for omissions, brackets for clarifications
5. URL liveness — does the link resolve; if not, archive.org snapshot
6. Attribution chain — does the cited source actually claim what we're attributing
7. Translation integrity — for non-English sources, note translator + flag any ambiguous renderings

### 2.5h. Bias detection

Active biases the AI MUST watch for in itself and in sources:

- **Confirmation bias** — over-weighting sources that agree with the working hypothesis
- **Recency bias** — over-weighting the most recent source on a slowly-evolving topic
- **Availability bias** — citing sources that came up easily in Google over more authoritative deep sources
- **Survivorship bias** — drawing patterns from winners while invisible losers contradict them
- **Source-funding bias** — vendor reports, advocacy think tanks, captured regulators
- **Geographic + linguistic bias** — English-language sources over-represented on global topics
- **AI-generation bias** — LLMs amplify majority-internet opinion; counter with diverse-source hunt

### 2.5i. AI-generated content verification

In a 2026 baseline, the AI MUST assume some of its inputs are themselves AI-generated and apply skepticism:

- **Hallucinated citations** — LLMs invent plausible-sounding but nonexistent sources; verify every citation independently
- **Fabricated quotes** — verify exact wording in the original; never trust an LLM's quote rendering
- **Synthetic statistics** — confident-sounding numbers without primary-source links are red flags
- **Image / chart provenance** — reverse-image-search before citing visuals
- **Synthetic experts** — AI-generated "Dr. X" with a fictional bio; verify against ORCID / institutional pages
- **Astroturfed consensus** — flood of similarly-worded sources may be AI-generated content farms

### 2.5j. When to stop researching

The skill MUST teach explicit stop conditions; otherwise research expands indefinitely:

| Signal                                                 | Action                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------- |
| Diminishing returns — last 3 sources added nothing new | Stop and synthesize                                                        |
| Triangulation achieved on every load-bearing claim     | Stop and write                                                             |
| Time budget exceeded by > 50%                          | Stop, write what you have, mark open gaps                                  |
| Major contradiction surfaced                           | Continue — investigate the disagreement before publishing                  |
| New regulatory / event news drops mid-research         | Decide: ship and amend, or pause and expand scope (NEVER silently fold in) |

---

## PHASE 3: BEST PRACTICES (numbered by priority)

1. **Always cite every load-bearing claim inline** — `(Author, Year)` or footnote — never put citations only in a bibliography.
2. **Always preserve retrieval date** alongside the URL for web sources; the web mutates.
3. **Always quote in quotation marks** with the exact wording; never silently paraphrase as a quote.
4. **Always disclose AI assistance** at the end of any artifact that used LLM drafting, with the verification methodology applied.
5. **Always state confidence level** on conclusions — IC analytic-confidence words: low / moderate / high.
6. **Always preserve source-language quotes** alongside translations for non-English material.
7. **Never cite Wikipedia as a terminal source** — use it to find the primary; cite the primary.
8. **Never combine multiple claims into one citation** — each claim gets its own provenance.
9. **Never round numbers without flagging the rounding** — "≈" or "approximately" or "rounded from X.Y".
10. **Never present hedged findings as certain** — preserve the original source's confidence language.
11. **Never publish without a fact-check pass** on numbers, dates, names, and quotes.
12. **Never ignore disconfirming evidence** — surface it and reason about it.

---

## PHASE 4: REFERENCE FILES (must include)

| File                                        | Content                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `references/research-methodology.md`        | PICO / SPIDER / SPICE / 5W1H / MECE templates with worked examples                                      |
| `references/source-evaluation-checklist.md` | CRAAP + SIFT + Tier classification + funding-disclosure check                                           |
| `references/citation-style-guide.md`        | Chicago / APA / IEEE / footnote with worked examples + DOI + retrieval-date conventions                 |
| `references/synthesis-techniques.md`        | Matrix / thematic / narrative / scoping / argument-mapping / timeline / stakeholder-map                 |
| `references/fact-checking-protocol.md`      | Number / date / name / quote / URL / attribution / translation checklist                                |
| `references/bias-detection-guide.md`        | Confirmation / recency / availability / survivorship / funding / geographic / AI biases                 |
| `references/ai-content-verification.md`     | Hallucinated-citation, fabricated-quote, synthetic-statistic, astroturf detection                       |
| `references/security-checklist.md`          | OPSEC for sensitive topics (anonymous sources, victim protection, regulator-leaks)                      |
| `references/ai-interaction-guide.md`        | What to delegate to AI (draft, summarize, source-find) vs. keep human (verification, judgment, opinion) |
| `references/common-issues.md`               | Citation drift, link rot, paraphrase plagiarism, scope creep, single-source claims                      |
| `references/code-style.md`                  | Repurposed as **artifact-style.md** — tone, hedging discipline, headline patterns, BLUF                 |

---

## PHASE 5: ASSETS

- `assets/research-brief-template.md` — BLUF + What we know / don't / means / recommend / confidence + Sources
- `assets/research-plan.md` — question, framework, search-string log, inclusion criteria, stop condition, time budget
- `assets/citation-log.csv` — source ID, tier, URL, retrieval date, claim cited, confidence
- `assets/source-tracker.md` — running bibliography with tier classification
- `assets/fact-check-checklist.md` — copy-paste pre-publish checklist
- `assets/executive-summary.md` — 1-pager template
- `assets/deep-dive-template.md` — 5-30 page deep-dive skeleton
- `assets/research-disclosure.md` — AI-assistance disclosure boilerplate

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md includes the SIFT method for every cited source
- [ ] SKILL.md includes the triangulation rule "≥ 3 independent sources for load-bearing claims"
- [ ] SKILL.md includes the source tier table (Primary / Secondary / Tertiary / Gray / Self-published / Generated)
- [ ] SKILL.md includes the BLUF executive-brief anatomy
- [ ] SKILL.md includes the IC analytic-confidence vocabulary (low / moderate / high)
- [ ] SKILL.md includes explicit stop conditions
- [ ] SKILL.md includes the AI-content verification section (hallucinated citations, fabricated quotes)
- [ ] SKILL.md forbids citing Wikipedia as a terminal source
- [ ] At least 10 reference files generated
- [ ] At least 6 asset templates generated
- [ ] Every template includes a retrieval-date field for web sources

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                      | Why                                                                                                |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Cite Wikipedia as the final source                         | Wikipedia is a starting point; use it to find primary sources, then cite those                     |
| Use LLM output as a source                                 | LLMs hallucinate plausible-sounding sources; verify against the actual source independently        |
| Bundle multiple claims into one footnote                   | Loses traceability; the reader can't tell which claim each source supports                         |
| Drop retrieval date on web URLs                            | Web mutates; without date, the citation is unfalsifiable in two years                              |
| Silently mix paraphrase and quote                          | Looks like the source said it that way; either quote exactly or paraphrase with clear attribution  |
| Cite a journalist citing a study without reading the study | Wire-service paraphrases lose nuance and introduce errors; trace to the original                   |
| Present hedged findings as certain                         | "Researchers found X" when the paper says "we observe a correlation suggestive of" is misleading   |
| Cherry-pick the agreeing source                            | Bias amplification; surface the contradictory source and reason about the disagreement             |
| Use anonymous LinkedIn / X posts as sources                | Self-published, unverifiable, vulnerable to astroturf                                              |
| Compose findings without fact-checking quantitative claims | Numbers are the most-frequent source of errors; check magnitude / unit / time period               |
| Ship without disclosing AI assistance                      | Erodes trust; reader needs to know what was drafted by LLM and how it was verified                 |
| Translate non-English sources without preserving original  | Translation errors compound; preserve the source-language quote alongside                          |
| Keep researching past diminishing returns                  | Time-budget collapse; once 3 consecutive sources add nothing, stop and synthesize                  |
| Forecast without a confidence level                        | Conflates "I think" with "the evidence shows"; use IC analytic-confidence words                    |
| Cite a study without checking funding source               | Funded research has predictable findings; surface the funder and let the reader weigh the evidence |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

For deep-researcher specifically, when asked for a brief / synthesis / fact-check, the AI MUST:

1. State the research question being answered (one sentence)
2. State the framework being applied (PICO / 5W1H / MECE) so the lens is visible
3. Cite every load-bearing claim inline with source + retrieval date
4. State a confidence level on every forward-looking statement
5. Surface what we don't know as a peer of what we do know
6. Disclose any AI assistance used in drafting and the verification applied

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY research task — literature review, market scan, competitive intel, policy brief, fact-check, source evaluation, citation cleanup, executive briefing, scoping review, evidence synthesis, deep dive on a topic.

**`allowed-tools`**: `Read Edit Write WebFetch WebSearch Glob Grep` (research requires web tools; explicitly NO Bash — research artifacts are not executed).

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (deep dive, brief, fact-check, source eval, scoping review)
2. **Do NOT Use** — cross-references to sibling skills (data-science for quantitative pipelines, project-manager for tracking the research-as-project, security for OPSEC of sensitive investigations)
3. **Research Posture** — what kinds of questions this user investigates
4. **Source Tier Table** — Primary / Secondary / Tertiary / Gray / Self-published / Generated
5. **Citation Discipline** — SIFT + CRAAP + inline-citation rule + retrieval-date rule
6. **Triangulation + Corroboration** — the ≥ 3-independent-sources rule
7. **Synthesis Techniques** — matrix / thematic / narrative / argument-map / timeline (rule table)
8. **Executive Brief Anatomy** — BLUF + What we know / don't / means / recommend / confidence
9. **Fact-Checking Protocol** — number / date / name / quote / URL / translation
10. **Bias Detection** — confirmation / recency / availability / funding / geographic / AI
11. **AI-Content Verification** — hallucinated citations, fabricated quotes, astroturf
12. **Stop Conditions** — diminishing returns, triangulation achieved, time budget
13. **Anti-Patterns** — the `Never` table
14. **References** — methodology books, citation guides, IC publications
15. **Session Protocols** (≤20 lines) — research-specific signals (e.g., "give me a brief on X" for Efficient, "what does SIFT mean" for Teaching, "this claim feels wrong" for Diagnostic), plus self-learning via LEARNED.md; deeper guidance (proficiency calibration, anti-dependency nudges) goes to references/ai-interaction-guide.md — never into SKILL.md

**Suggested reference files**: see PHASE 4 + 5 above.

`scripts/check-citations.sh` — scans markdown artifacts for `[UNVERIFIED]` tags, dead URLs (basic curl --head), missing retrieval dates, and bare Wikipedia citations.

---

## SUB-AGENT RECOMMENDATIONS

| Agent            | Role                                                             | Tools                   | Spawn When                                        |
| ---------------- | ---------------------------------------------------------------- | ----------------------- | ------------------------------------------------- |
| source-finder    | Read-only — surface primary sources for a claim via web search   | WebSearch WebFetch Read | "find primary source for X", scoping a new topic  |
| fact-checker     | Read-only — verify numbers, dates, names, quotes against sources | WebFetch Read Glob Grep | Pre-publish review, contested claim audit         |
| citation-auditor | Read-only — scan artifacts for citation hygiene + link rot       | Read Glob Grep WebFetch | Pre-publish review, periodic bibliography refresh |

All recommended deep-researcher sub-agents are **read-only**; verification work must not silently rewrite the artifact under review.

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to `agents/` for full definitions

Add to suggested reference files:

- `agents/source-finder.md` — read-only primary-source discovery agent
- `agents/fact-checker.md` — read-only verification agent
- `agents/citation-auditor.md` — read-only citation-hygiene agent

---

## EXECUTION ORDER

```
[ ] 1. Scan project for existing research artifacts, source tier mix, citation style, audience (Phase 1)
[ ] 2. Synthesize research posture, gaps, audience, output formats (Phase 2)
[ ] 3. Generate SKILL.md with numbered rule lists + Phase 2.5 standards
[ ] 4. Generate INJECT.md (50-150 token quick ref — must include "≥3 independent sources", "SIFT every source", "preserve retrieval date", "disclose AI assistance")
[ ] 5. Generate LEARNED.md (empty template with section headers)
[ ] 6. Generate the 10+ reference files (Phase 4)
[ ] 7. Generate the 8+ asset templates (Phase 5)
[ ] 8. Generate scripts/check-citations.sh
[ ] 9. Generate agents/ files (all read-only per research safety boundary)
[ ] 10. Run quality gates (Phase 6)
[ ] 11. Verify all anti-patterns appear in SKILL.md "Never" table (Phase 7)
```

---

## SOURCES

- SIFT method — Mike Caulfield, [hapgood.us](https://hapgood.us/2019/06/19/sift-the-four-moves/)
- CRAAP test — Sarah Blakeslee, Meriam Library at CSU Chico
- IC analytic-confidence words — [ICD 203, Office of the Director of National Intelligence](https://www.dni.gov/files/documents/ICD/ICD%20203%20Analytic%20Standards.pdf)
- PICO + SPIDER — Cochrane Collaboration guidance ([cochrane.org](https://www.cochrane.org/))
- BLUF + analytic writing — US Army FM 6-22 + IC writing standards
- Scoping reviews — [PRISMA-ScR](https://www.prisma-statement.org/Extensions/ScopingReviews)
- AI hallucination + fabricated citations — Stanford HAI ([hai.stanford.edu](https://hai.stanford.edu/))
- News verification — Bellingcat methodology ([bellingcat.com](https://www.bellingcat.com/))
- Web archiving — Wayback Machine, perma.cc, archive.today
- "Calling Bullshit" — Bergstrom + West (data + statistical literacy)
- "Bad Science" — Ben Goldacre (evidence evaluation)
- "Numbers Don't Lie" — Vaclav Smil (quantitative reasoning)
