# Translation Review Skill Generator

> **Base instructions**: The shared base instructions (structure, quality gates, execution order) are already included above this prompt — do NOT attempt to read \_base-skill-generator.md from disk; it does not exist in the target project. Below are translation-review-specific overrides.

```
ROLE:     Senior localization QA engineer who reviews translation PRs for runtime breakage, regressions,
          locale-format errors, and content quality across 15+ locales
GOAL:     Generate a production-grade translation / localization PR review skill directory
SCOPE:    Reviewing translation catalogs and TMS exports (Lokalise, Crowdin, Phrase, Transifex, POEditor):
          gettext .po/.mo, i18n JSON, ARB, Android strings.xml, iOS .strings/.stringsdict, XLIFF —
          placeholders, plurals, regressions vs base, loader fallback, locale formats, content, RTL,
          backport parity, and the review report
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + scripts/ (+ agents/ if warranted)
```

This skill **reviews**; the `translator` scope **produces** translations and manages terminology. The generated skill MUST cross-reference the translator skill in "Do NOT Use" and stay focused on finding problems in someone else's translation change. It MUST work in a repo with no localization tooling beyond the catalogs themselves.

---

## PHASE 1: PROJECT SCAN — Catalogs, Loaders, Tooling

**Catalogs & locales**

- Catalog files: `**/locale/*/LC_MESSAGES/*.po|*.mo`, `**/i18n/**/*.json`, `**/locales/**/*.{json,yml,yaml}`, `*.arb`, `res/values*/strings.xml`, `*.lproj/*.strings|*.stringsdict`, `*.xlf|*.xliff`
- Source language and its file per catalog set (`en.json`, `en_GB.json`, `locale/en/`, `values/`, `Base.lproj`)
- Served languages: Django `LANGUAGES`, Rails `available_locales`, Angular/Next/Nuxt i18n config, `supportedLocales` (Flutter), Android `resConfigs`/`localeFilters`, iOS `knownRegions`
- Legacy or unserved locale directories (e.g. `no` vs `nb`, `pt` vs `pt_PT`, `zh` vs `zh_Hans`)
- Whether gettext msgids are English text or keys (`app.section.label`) — decides what "compare with source" means

**Loaders & fallback**

- Each loader and the catalog path it reads: Django/GNU gettext, python-i18n (`i18n.load_path`), Babel, ngx-translate (`TranslateHttpLoader`), i18next backends, vue-i18n, FormatJS/react-intl, Android resources, iOS bundles
- Fallback configuration (`fallbackLng`, `LANGUAGE_CODE`, `MissingTranslationHandler`, `defaultMessage`) and what an **empty string** returns (python-i18n and i18next `returnEmptyString` return `''`)
- Keys duplicated across loaders (same key in a `.po` and a JSON) — one copy is usually dead

**Tooling & process**

- TMS config: `.lokalise.yml`, `crowdin.yml`, `.tx/config`, `phrase.yml`; export/import scripts (`update_translations.py`, `i18n:sync` npm scripts, Fastlane)
- Existing checkers: translation consistency tests, placeholder linters, `msgfmt -c` in CI, `i18next-parser`, Android lint `MissingTranslation`, project review checklists
- PR conventions for translation updates: title pattern, branches (master + release backports), who reviews
- Glossary / do-not-translate list: brand and product names, device names, units, regulated terms
- Domain risk: medical, financial, legal, safety text (dosage, units, consent, alarms) needs stricter review

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_translation_review.md`:

1. **Catalog Map** — every catalog set: format, source file, languages present, languages served, loader
2. **Fallback Matrix** — per loader: missing key → ?, empty value → ? (verified or INFERRED)
3. **Tooling** — TMS, export script, existing checkers and how to run them; what the export writes and what it misses
4. **Locales in Scope** — the project's languages + regional variants that change formatting
5. **Glossary & Do-Not-Translate** — brands (exact casing), units, accepted localized acronyms
6. **Review Flow** — base branches, backport rule, where findings are reported (PR comments, ticket, artifact)
7. **Things to ALWAYS do** — e.g. compare with the source string, test the loader, tag NEW/OLD
8. **Things to NEVER do** — e.g. hand-edit non-source catalogs, post comments without approval

---

## PHASE 3: BEST PRACTICES (numbered by priority)

1. **Compare with the source-language string, never the key.** gettext msgids are often keys; placeholder diffs vanish otherwise.
2. **Placeholders: same names, same count.** Order may change only with named/positional args. A translated (`{{dato}}`), dropped, invented (`"ago"` → `"منذ %s"`) or hard-coded (`%(days)s` → "7 days") placeholder is an ERROR.
3. **Tag every finding NEW (this PR) or OLD (already on base).** Comment inline only on NEW; list OLD once.
4. **Regressions first.** A value that was translated and is now empty, English, removed, or lowercased is the cheapest high-value catch.
5. **Never say "falls back" without checking the loader.** An empty value can render blank (push notifications, emails).
6. **Plurals are converted, and conversions break.** Check `msgstr[n]` count vs `nplurals`, every source plural present in every language, and the category → form mapping (Polish 3rd gettext form is CLDR `many`).
7. **Locale formats come from CLDR, not memory.** A translation must not contain a formatted number/date/currency; any literal one must match the locale (decimal comma, NNBSP group in fr, `’` in de_CH, YMD in sv, 24-hour clock).
8. **Digits that carry meaning survive.** "6-digit code" → "3-cijferige code" is a bug even though no placeholder broke.
9. **Bulk term swaps break grammar.** When a term changes across a file, check capitals, gender/case agreement, and leftovers in every language with grammatical gender.
10. **One concept, one term — per screen and across platforms.** Title and subtitle of one view must agree; web, server and mobile catalogs must agree.
11. **Content read: German in full + 2–3 languages**, sub-agents per language family for large PRs; meaning, register, punctuation, RTL.
12. **Tooling diffs are production code.** Export/import scripts decide what reaches every language; read what they skip, overwrite, and which directories they write.
13. **Backport parity.** Master and release PRs carry identical catalog content and tooling.
14. **Fix at the source.** Every content fix also goes to the TMS, or the next export reverts it; hand edits to non-source catalogs are findings.
15. **Draft, then post.** Review comments, tickets and messages are drafted for the user; external posting needs explicit approval.

---

## KNOWLEDGE BASE (the generated skill MUST carry this into references/)

### A. Placeholder syntax → `references/placeholder-syntax.md`

| Syntax | Stacks | Typical break |
| --- | --- | --- |
| `{{ name }}` | Angular/ngx-translate, i18next, Handlebars | name translated → braces shown literally |
| `{name}`, `{0}` | ICU, Python `format`, .NET, Java `MessageFormat`, ARB | `KeyError` / literal braces |
| `{n, plural, one {…} other {…}}` | ICU / FormatJS / ARB | keyword translated, `other` missing, braces unbalanced, `#` dropped |
| `%(name)s` | Python %-format, Django | dropped → information silently lost (dict `%` ignores unused keys); renamed → `KeyError` |
| `%s`, `%d`, `%.1f` | C, Python, PHP, gettext `c-format` | count changed → `TypeError` |
| `%1$s` | Android, Java, PHP | index changed |
| `%@`, `%lld` | iOS / macOS | dropped → crash / wrong value |
| `%{name}`, `${name}` | Ruby i18n, custom loaders | renamed |
| `<b>`, `<a href>`, `<0>…</0>` | HTML strings, React `Trans` | tag dropped / attribute injected |

Literal `%` in a %-formatted string must be `%%` (`"100% dziennie"` parses `% d` → `TypeError`). ICU apostrophe escapes braces. `select` keys are code values. Brand inflection in agglutinative languages (fi `kinexuksessa`) and standard localized medical acronyms (PD → fr `DP`, pl `DO`) are correct.

### B. Plurals → `references/plurals.md`

| Lang | CLDR integer categories | gettext header in common use |
| --- | --- | --- |
| en, de, nl, sv, da, nb, fi, el, it, es, pt | one, other | `nplurals=2; plural=(n != 1);` |
| fr | one (0 and 1), other | `nplurals=2; plural=(n > 1);` |
| cs | one, few (2–4), other | `nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;` |
| pl | one, few (2–4, 22–24…), many (0, 5–21, 25…) | `nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 \|\| n%100>=20) ? 1 : 2);` |
| ar | zero, one, two, few (3–10), many (11–99), other (100+) | `nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);` |

CLDR also defines `many` for fr/it/es/pt (exact millions) and cs (fractions) — Babel's `to_gettext()` emits those, but `.po` headers should not. Converters that skip a plural when any form is empty drop Arabic first.

### C. Locale formats → `references/locale-formats.md` (generate with the bundled script, never from memory)

The skill MUST ship `scripts/locale_facts.py` (Babel/CLDR) and a table generated from it for the project's locales. Reference values (CLDR 2026, Babel 2.18):

| Locale | Decimal | Group | Short date (7 Mar 2026) | Time | Percent |
| --- | --- | --- | --- | --- | --- |
| en_GB / en_US | `.` | `,` | `07/03/2026` / `3/7/26` | `14:05` / `2:05 PM` | `25%` |
| de_DE / de_AT | `,` | `.` | `07.03.26` | `14:05` | `25 %` |
| de_CH / it_CH | `.` | `’` (U+2019) | `07.03.26` | `14:05` | `25%` |
| fr_FR / fr_BE / fr_CH | `,` | NNBSP (U+202F) | `07/03/2026` / `7/03/26` / `07.03.26` | `14:05` | `25 %` (fr_CH `25%`) |
| it_IT | `,` | `.` | `07/03/26` | `14:05` | `25%` |
| nl_NL / nl_BE | `,` | `.` | `07-03-2026` / `7/03/2026` | `14:05` | `25%` |
| es_ES | `,` | `.` | `7/3/26` | `14:05` | `25 %` |
| pt_PT | `,` | NBSP | `07/03/26` | `14:05` | `25%` |
| fi_FI | `,` | NBSP | `7.3.2026` | `14.05` | `25 %` |
| cs_CZ | `,` | NBSP | `07.03.26` (medium `7. 3. 2026`) | `14:05` | `25 %` |
| nb_NO | `,` | NBSP | `07.03.2026` | `14:05` | `25 %` |
| sv_SE | `,` | NBSP | `2026-03-07` | `14:05` | `25 %` |
| da_DK | `,` | `.` | `07.03.2026` | `14.05` | `25 %` |
| el_GR | `,` | `.` | `7/3/26` | `2:05 μ.μ.` | `25%` |
| pl_PL | `,` | NBSP | `7.03.2026` | `14:05` | `25%` |
| ar / ar_AE | `.` | `,` | `7‏/3‏/2026` | `2:05 م` | `25%` |
| ar_SA / ar_EG | `٫` | `٬` (Arabic-Indic digits) | `7‏/3‏/2026` | `2:05 م` | `25%` |

Also carry: week start (Mon; Sun for en_US, pt_PT, ar_SA; Sat for ar_EG), genitive month forms (pl `7 marca`/`marzec`, cs `7. března`/`březen`, fi `7. maaliskuuta`/`maaliskuu`, el `7 Μαρτίου`/`Μάρτιος`), lowercase month/day names (fr es it pt nl sv da nb fi pl cs), date prepositions (`am`, `le`, `il`, `op`, `de`), list conjunctions (no Oxford comma outside en_US), space before units, phone/postal patterns, quotation marks per locale (house-style dependent).

### D. Language notes → `references/language-notes.md`

Per language for the project's locales: address form (de *Sie*, fr *vous*, nl *u*, sv/da/nb *du*, es_ES *usted*, pt_PT impersonal, pl impersonal/imperative, cs *vy*, el *εσείς*), capitalization (de nouns; el no accents in all-caps), punctuation (fr NBSP before `; : ! ?` and inside « »; es `¿¡`; el `;` as question mark; ar `؟ ، ؛`), grammar traps (gender agreement after term swaps; Slavic cases; fi inflection; nl/de/sv/da/nb compounds written as one word), variant leakage (pt_BR in pt_PT, Nynorsk in Bokmål), RTL rules (placeholders/tags intact, bidi isolation for IDs/brands, mirrored glyphs are correct), and regulated-text rules (dosage/units/consent/alarms).

### E. Consumption & fallback → `references/consumption-and-fallback.md`

| Stack | Missing key | Empty value |
| --- | --- | --- |
| Django / GNU gettext | msgid (raw key if msgids are keys and `en` lacks it) | untranslated → msgid / `LANGUAGE_CODE` catalog; `#, fuzzy` ignored |
| python-i18n | fallback locale → `default=` → key | **returns `''`** (`default` not used) |
| i18next | fallbackLng → key | `returnEmptyString` (default true) → `''` |
| ngx-translate / vue-i18n / FormatJS | handler / fallback / defaultMessage | config-dependent — test |
| Android | default `values/` | empty shown |
| iOS `.strings` | key or `value:` arg (no per-key dev-language fallback) | empty shown |

Plus: `.mo`/bundle rebuild requirements, served-locale directories, call-site argument contracts, and caching.

### F. Common issues → `references/common-issues.md`

A pattern → example → detection table with at least: translated/dropped/invented/hard-coded placeholders; changed digits; bulk term swap breaking capitals and gender; two terms on one screen; status-label sets with mixed gender and a dialog naming a status differently from its badge; wrong word sense ("Supply details" → "Delivery details", fi "Uusi" = new for Renew); split compounds; brand casing; plurals dropped or mis-mapped by tooling; dead catalog copy with the live file empty (blank push); hand edit to pass a test; missing backport/forward-port; stale fallback test; unserved locale dir; truncation; whitespace; lost separators; source-language bugs; scope creep.

---

## OUTPUT CONTRACT FOR REVIEWS THE SKILL PRODUCES

The generated SKILL.md MUST instruct the consuming AI to:

1. **Scope** the PR (base, head SHA, merge state, CI failures, counterpart PRs, non-catalog files, commits after the export).
2. **Run** the bundled `scripts/validate-catalogs.sh <base> <head> [keep-terms]` (project checker if any + `check_catalogs.py` + `msgfmt -c`).
3. **Verify** every finding at the head ref before reporting; drop false positives (inflection, localized acronyms, spelled-out numbers).
4. **Report** with the template: verdict, scope/checker counts, What passed, blocking issues, fix-in-TMS issues, minor notes, OLD context, next steps. Each finding: key, language, source text, current text, user-visible effect, fix.
5. **Draft** PR comments/tickets in chat; post only after explicit approval. Publish a shareable page only when asked.
6. **Write** new project facts (paths, served locales, glossary decisions) to LEARNED.md.

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY translation review task — "review this translation PR", "Updated Lokalise/Lokalize", "Sync with Crowdin", "check the translations", localization QA, l10n/i18n review, "string shows English / the key / braces / blank in language X", plural problems, number/date format in a language, RTL/Arabic layout text, backport of a translation PR, writing a translation review report.

**`allowed-tools`**: `Read Grep Glob Edit Write Bash(git:*) Bash(gh:*) Bash(python3:*) Bash(msgfmt:*)` — add `Agent` only if agents/ is generated. No network tools: catalogs may contain unreleased or regulated text.

**`metadata.sdlc-phase`**: `review`

**Body sections** (all required in SKILL.md):

1. **Before You Start** — announcement rule, read LEARNED.md, find the project's own translation tooling and checkers
2. **When to Use** — 5 triggers (TMS export PR, feature translations, backport parity, "shows English/key/blank", locale-format audit)
3. **Do NOT Use** — producing translations or glossary work (translator skill), implementing i18n in code (frontend/backend skills), English copywriting
4. **Workflow** — the 8-step flow (scope → mechanical → regressions & tooling → consumption → content → locale formats → verify → report)
5. **Locales in Scope** — the project's languages with a compact formats table (short form of §C) and plural summary
6. **Review Checklist** — 8-12 checks (placeholders, file integrity, regressions, plurals, consumption, locale formats, term consistency, brands/punctuation/RTL, backport parity)
7. **Anti-Patterns** — with WHY (comparing with the key, assuming fallback, hand-editing catalogs, trusting a green checker for content, flagging fi inflection, inline INFO floods, formats from memory, posting unasked)
8. **Communication Style** — per base template
9. **Sub-Agent Delegation** — if agents/ generated
10. **Freedom Levels** — MUST: source-string comparison, NEW/OLD, loader check, verify-before-report, draft-before-post; SHOULD: run all checkers, German in full; CAN: language sample, report format details
11. **Session Protocols** (≤20 lines) — Full review ("review PR", "find all issues"), Quick check ("does it break anything"), Diagnostic ("shows English/braces/blank in X"), Parity ("backport", "same as master?"); self-learning via LEARNED.md
12. **References** — links to references/, scripts/, agents/

**Suggested reference files**:

- `LEARNED.md` — template (Corrections, Preferences, Discovered Conventions); project entries prefixed `[repo]`
- `references/review-checklist.md` — full checklist by section (scope, integrity, placeholders, plurals, regressions, consumption, locale formats, content, tooling, report)
- `references/placeholder-syntax.md` — §A with call-site checks
- `references/plurals.md` — §B with a quick `ngettext` / Babel test snippet
- `references/locale-formats.md` — §C generated by `scripts/locale_facts.py --markdown`, plus date/number/list traps
- `references/language-notes.md` — §D for the project's locales
- `references/consumption-and-fallback.md` — §E with one-line loader tests for this project's stacks
- `references/report-template.md` — summary block, one-finding template, severity guide, PR-comment short form, shareable page outline
- `references/common-issues.md` — §F
- `scripts/check_catalogs.py` — format-agnostic checker (JSON/ARB, `.po`, Android XML, iOS `.strings`): placeholders across syntaxes, ICU structure, stray `%`, plural form counts, missing plurals, emptied/removed/case-regressed strings vs `--base`, digits/decimal marks, punctuation per language, truncation, whitespace, do-not-translate terms (`--keep`), `.po` without `.mo`, and a TERM SHIFTS summary of words removed → added per language; NEW/OLD tags; exit 1 on NEW ERROR
- `scripts/dump_side_by_side.py` — source + all languages + previous values per changed key (`--langs`, `--rewritten-only`, `--grep`) for content reads and sub-agents
- `scripts/locale_facts.py` — CLDR facts via Babel (`--markdown` tables)
- `scripts/validate-catalogs.sh` — one-shot: project checker (if found) + `check_catalogs.py` + `msgfmt -c` on changed `.po`

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation (typically: 5+ languages, large TMS exports, or several loaders), include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent | Role | Tools | Spawn When |
| --- | --- | --- | --- |
| language-reviewer | Content read for 1–4 languages from a side-by-side dump: meaning, terminology, agreement, register, punctuation, formats, RTL | Read Grep Glob | >150 changed strings per language, >5 languages, or term shifts detected |
| consumption-auditor | Traces which loader reads each key and what missing/empty renders; finds dead copies and blank-at-runtime risks | Read Grep Glob (+ read-only Bash) | `not-in-source` keys, push/email/PDF keys, tooling or locale-dir changes |

Both are read-only — only the parent writes reports and LEARNED.md. Split language-reviewer runs by family (Germanic, Romance, Slavic/Greek/Finnic, Arabic) and run them in parallel. Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules (dump first and pass its path; pass LEARNED.md glossary entries; re-verify every agent finding)
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/language-reviewer.md` — read-only per-language content review agent
- `agents/consumption-auditor.md` — read-only loader/fallback/dead-copy audit agent
