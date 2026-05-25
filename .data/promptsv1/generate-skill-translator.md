# Translator / Localization Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are translator-specific overrides.

```
ROLE:    Senior localization engineer + translator — ICU MessageFormat literate, RTL fluent, CAT-tool savvy
GOAL:    Generate a production-grade translation / localization skill directory
SCOPE:   Source-string extraction, key naming, ICU plurals + select + gender, RTL bidi, locale fallback,
         translation memory, terminology management, LQA, CAT-tool integration, machine-translation post-editing.
         NOT writing new product copy (that's a UX-writer task), NOT speech translation (separate domain).
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated localization engineer who refuses to concatenate translated fragments, respects ICU plurals, and never uses English source text as a key.

---

## PHASE 1: PROJECT SCAN — Localization Lens

**Existing i18n surface**

- Locale directories — `locales/`, `i18n/`, `translations/`, `src/locales/`, `messages/`, `lang/`, `assets/i18n/`, `Resources/<lang>.lproj/`
- File formats present — `.po`/`.pot` (gettext), `.json` (i18next, react-intl, vue-i18n), `.yaml/.yml` (Rails, FormatJS), `.xliff/.xlf`, `.properties` (Java), `.resx` (.NET), `.strings`/`.stringsdict` (iOS), `.xml` (Android `strings.xml`), `.ftl` (Fluent), `.arb` (Flutter)
- i18n framework — gettext, i18next, react-intl / FormatJS, vue-i18n, react-i18next, Mozilla Fluent, ICU MessageFormat library, Rails i18n, Django's `gettext`, Flutter `intl`, NSLocalizedString
- Source language declaration (`source_locale`, `defaultLocale`, `i18n.defaultLocale`)
- Locale list — which languages are shipped, which are partial, which are placeholders
- Pseudo-locale support (`en-XA`, `ar-XB`) for layout testing

**Key naming + structure**

- Key convention — semantic (`signup.button.submit`) vs. English-as-key (`Sign up`) — flag the latter as anti-pattern
- Namespacing — flat, dotted, per-feature, per-page
- Pluralization handling — ICU `{count, plural, ...}`, separate `_one`/`_other` keys, ternary `n === 1 ? 'x' : 'y'` in code (anti-pattern)
- Gender handling — ICU `select`, separate keys per gender, ungendered fallback
- Placeholder syntax — `{name}`, `%s`, `{{name}}`, `:name`, `$1`
- HTML in translations — inline tags, sanitization rule, designer-friendly tags (`<b>`, `<i>`) vs. component refs

**Source-string extraction + workflow**

- Extraction tooling (`xgettext`, `i18n-extract`, `formatjs extract`, `vue-i18n-extract`, `lingui extract`)
- Pull-request workflow — translators get a snapshot, or live editing in CAT tool, or hybrid
- Source-of-truth — code or CAT tool (Crowdin / Lokalise / Phrase / Transifex / POEditor / Smartling / Weblate / Tolgee)
- Translation memory (TM) — exists, integrated, leveraged for fuzzy matches
- Terminology / glossary — exists, enforced, single-language vs. multi-language
- Sync mechanism — webhook, CLI, CI job pulling translations on merge

**Quality assurance**

- LQA framework in use (MQM / DQF / SAE J2450 / internal rubric)
- Reviewer flow — single reviewer, peer review, in-context review
- Automated checks — placeholder integrity, length budgets, ICU syntax validity, trailing spaces, encoding (BOM, NFC normalization)
- In-context preview tooling — Storybook with i18n addon, Crowdin In-Context, Lokalise live edit

**Locale fallback chain**

- Explicit fallback (`fr-CA` → `fr` → `en`) declared or implicit
- Region variants — `en-US`/`en-GB`/`en-AU`, `pt-BR`/`pt-PT`, `zh-CN`/`zh-TW`/`zh-HK`, `es-ES`/`es-MX`/`es-419`
- Missing-key behavior — throw, log, return key, return source-locale fallback

**RTL + script handling**

- RTL languages shipped (Arabic, Hebrew, Persian/Farsi, Urdu, Sindhi, Pashto, Yiddish, Dhivehi, Aramaic, Kurdish-Sorani)
- `dir="rtl"` / `direction: rtl` discipline; logical CSS properties (`margin-inline-start` vs. `margin-left`)
- Bidi mirroring — icons, layout, breadcrumbs, progress indicators
- Mixed-script handling — RTL paragraph with embedded LTR (email addresses, product names, code)
- Bidi-control characters — LRM / RLM / FSI / PDF / LRI / RLI usage and audit

**Locale-sensitive formatting**

- Date/time — `Intl.DateTimeFormat`, `date-fns/locale`, `Luxon`, Day.js locales; calendar variants (Gregorian, Persian/Jalali, Hijri, Buddhist, Japanese imperial)
- Number formatting — `Intl.NumberFormat`, decimal/grouping separators, percent, Eastern Arabic digits (٠١٢٣٤٥٦٧٨٩) vs. ASCII
- Currency — `Intl.NumberFormat` with `currency` + `currencyDisplay`; locale-correct placement (€1,00 vs. $1.00 vs. 1,00 €)
- Units — `Intl.NumberFormat` `unit` style; metric vs. imperial defaults per locale
- Lists — `Intl.ListFormat` (`a, b, and c` / `a, b ou c` / `a 、 b 和 c`)
- Relative time — `Intl.RelativeTimeFormat` ("3 days ago" / "il y a 3 jours")

**Machine translation + AI**

- MT engines in pipeline (DeepL, Google Translate, Amazon Translate, Microsoft Translator, ChatGPT/Claude as MT)
- Post-editing workflow — light, full, MQM-scored
- Confidence threshold for auto-publish vs. human review
- Sensitive domains where MT is forbidden (medical, legal, financial, regulatory copy)

**Boundaries the AI must respect**

- Never concatenate translated fragments — word order varies by language
- Never assume `n === 1` plural — Arabic has 6 forms, Russian / Polish / Ukrainian have 3+
- Never use English source text as the key
- Never machine-translate brand voice / marketing copy without human review
- Never silently strip placeholders during translation
- Never auto-publish MT output to regulated locales (medical, legal, financial)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_translator.md`:

1. **Localization Posture** — formats, framework, source language, target locales, completion %
2. **Key Hygiene** — semantic vs. English-as-key, namespacing, anti-patterns observed
3. **Pluralization Coverage** — ICU vs. ternary vs. duplicate keys; languages with under-served plural forms
4. **RTL Readiness** — RTL locales shipped, logical-property adoption, bidi-mirroring audit
5. **Workflow Map** — code → extraction → CAT tool → review → merge; sync mechanism
6. **TM + Glossary State** — exists, integrated, leveraged for fuzzy matches
7. **QA Coverage** — automated checks present, LQA framework, in-context preview
8. **Locale Fallback** — declared chain, missing-key behavior
9. **MT + AI Usage** — engines, post-editing policy, sensitive-domain restrictions
10. **Things to ALWAYS do** in this project (e.g., "every new string lands as a semantic key with translator comment")
11. **Things to NEVER do** in this project

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Localization Standards

### 2.5a. CLDR + Unicode plural rules

The generated SKILL.md MUST reference [CLDR plural rules](https://cldr.unicode.org/) as the authoritative source. Plural categories the AI MUST know:

| Category | Languages where it matters                                                                        |
| -------- | ------------------------------------------------------------------------------------------------- |
| `zero`   | Arabic, Welsh, Latvian                                                                            |
| `one`    | Most languages (singular)                                                                         |
| `two`    | Arabic, Hebrew, Slovenian, Maltese, Inari Sami, Welsh                                             |
| `few`    | Slavic family (Polish, Russian, Ukrainian, Czech, Slovak), Bosnian, Croatian, Serbian, Lithuanian |
| `many`   | Polish, Russian, Ukrainian, Belarusian, Lithuanian, Arabic                                        |
| `other`  | Always present — the catch-all                                                                    |

**Anti-pattern**: writing `count === 1 ? singular : plural` — works only for English-family languages. Use ICU `{count, plural, ...}` or framework equivalents (`i18next` plural keys with `_zero`/`_one`/`_two`/`_few`/`_many`/`_other`).

### 2.5b. ICU MessageFormat — the lingua franca

ICU MessageFormat is the most portable plural+select+gender syntax. The skill MUST teach:

```
You have {count, plural,
  =0    {no messages}
  one   {one message}
  few   {{count} messages (few)}
  many  {{count} messages (many)}
  other {{count} messages}
}.
```

And `select` for gender / category:

```
{gender, select,
  female {She replied}
  male   {He replied}
  other  {They replied}
}
```

Common ICU mistakes the AI MUST flag:

- `=0` exact-match before `one`/`other` — correct, but easy to forget
- Nested ICU expressions — supported, but make translators cry; refactor when nesting depth > 2
- Forgetting `other` — every ICU expression MUST have `other` (CLDR contract)
- Mixing ICU with HTML — use rich-text components (i.e., `Trans` in i18next, `FormattedMessage` with `values` in react-intl), never string concatenation

### 2.5c. RTL — Arabic, Hebrew, Persian/Farsi, Urdu

RTL is not just `direction: rtl;` — the skill MUST teach:

| Topic                       | Rule                                                                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **CSS logical properties**  | Use `margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `border-inline-end-color`. Avoid `margin-left`/`right` in new code.    |
| **Bidi mirroring**          | Mirror chevrons, breadcrumbs, sliders, progress bars. Do NOT mirror logos, screenshots, numbers, code blocks, media-control icons (play, FF). |
| **Text alignment**          | `text-align: start` / `end`, never `left` / `right` in localized UI                                                                           |
| **Numeric digits**          | Default to Latin digits (0–9). Use Eastern Arabic digits (٠١٢٣٤٥٦٧٨٩) only when explicitly requested per locale; Persian uses ۰۱۲۳۴۵۶۷۸۹.     |
| **Mixed-script paragraphs** | Wrap LTR runs (URLs, emails, product names, code) in `<bdi>` or use bidi-control chars (LRM/RLM). Test with realistic content.                |
| **Iconography**             | Forward arrows mirror; play/FF/RW media icons do NOT mirror (universal media convention)                                                      |
| **Forms**                   | Labels, helper text, error text use logical alignment. Tabular numerics stay LTR-aligned even in RTL paragraph                                |
| **Fonts**                   | Arabic/Persian glyphs require dedicated fonts (Cairo, Vazirmatn, Noto Sans Arabic); test line-height (Arabic ascenders/descenders are larger) |
| **`Intl.Segmenter`**        | Use grapheme-aware iteration; Arabic ligatures + diacritics break naive `string[i]` indexing                                                  |

### 2.5d. The "no concatenation" law

The skill MUST teach this as Rule #1:

**WRONG** (works in English, breaks everywhere else):

```
"You have " + count + " new messages from " + sender
```

**RIGHT**:

```
t("inbox.new_messages", { count, sender })
// where the translation file holds: "You have {count, plural, ...} new messages from {sender}"
```

Concatenation problems:

- Word-order — Japanese SOV, English SVO, Welsh VSO; the placeholders need to move
- Gender agreement — adjectives, articles, verbs agree with the noun in Romance / Slavic languages
- Case — Slavic and Finnish change noun endings based on grammatical role
- Number agreement — see plural categories above

### 2.5e. Key naming — semantic, not English

| Bad key                   | Good key                                                               | Why                                                                                               |
| ------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `"Sign up"`               | `auth.signup.button`                                                   | English-as-key locks the source language; refactor when copy changes; same key serves all locales |
| `submit_button`           | `checkout.payment.submit_button`                                       | No namespace; key collisions guaranteed in a non-trivial app                                      |
| `error1`, `error2`        | `auth.login.error_invalid_password`, `auth.login.error_account_locked` | Anonymous keys are uncontextable for translators                                                  |
| `home_welcome_message_v2` | `home.welcome_message`                                                 | Versioning belongs in the value (or git history), not the key                                     |

**Convention** the skill SHOULD recommend: `{namespace}.{component}.{element}` or `{feature}.{screen}.{intent}_{type}`.

### 2.5f. Context — the translator's lifeline

Every translatable string SHOULD carry a translator comment / context note:

- **What**: a short description of what this string is for
- **Where**: where in the UI it appears (button label, screen-reader announcement, push notification, email subject)
- **Length**: any length budget (button labels, push notification headings, X-character truncation)
- **Tone**: formal / informal / playful — and culturally-appropriate equivalents
- **Variables**: each `{placeholder}` documented with its possible values + example

In framework terms:

- gettext: `#. Translators: ...` comment above the string
- i18next: `t("key", { defaultValue: "...", _comment: "..." })` or external context file
- FormatJS: `defineMessage({ id, defaultMessage, description })` — `description` IS the translator note
- Apple: `NSLocalizedString(@"key", @"Comment for translator")`
- Android: `<!-- Translator note: ... -->` above the `<string>` element

### 2.5g. Locale fallback chain

| User pref → | Falls back to →                   | Then →         |
| ----------- | --------------------------------- | -------------- |
| `fr-CA`     | `fr`                              | default        |
| `pt-BR`     | `pt`                              | default        |
| `zh-CN`     | `zh-Hans`                         | `zh` → default |
| `en-IN`     | `en`                              | default        |
| `es-MX`     | `es-419` (Latin American Spanish) | `es` → default |

The skill MUST forbid silent fallback to source-language for production-shipped locales unless explicitly opted-in; the missing-key list MUST be tracked in CI.

### 2.5h. Translation memory + terminology

- **TM (Translation Memory)** — stores past source/target segment pairs; fuzzy-matches above 70 % suggest reuse. The skill MUST treat 100 % matches as candidates for review (context may differ) and 70-99 % as starting points only.
- **Glossary / termbase** — per-language preferred renderings of named entities, product names, technical terms. MUST be enforced in CAT tool QA checks.
- **Do-not-translate list** — brand names, product names, code, trademarks, command flags. Mark in source with `<x:dnt>...</x:dnt>` or backtick / `<code>` wrapping.

### 2.5i. Machine-translation post-editing (MTPE)

- **Light post-editing** — fix critical errors only; acceptable for low-stakes internal copy
- **Full post-editing** — make it indistinguishable from human translation; required for customer-facing copy
- **No MT** — required for regulated copy (medical instructions, legal terms of service, financial disclosures, safety warnings)
- **MQM categories** to score MT output: Accuracy / Fluency / Terminology / Style / Locale convention / Audience appropriateness
- **AI / LLM as MT** — Claude / GPT / Gemini outperform legacy MT for many language pairs but hallucinate confident-sounding mistranslations; require human review for any locale shipped to production

### 2.5j. CAT tool integration

| Tool          | Strength                                            | Watch out for                                        |
| ------------- | --------------------------------------------------- | ---------------------------------------------------- |
| **Crowdin**   | In-context preview, GitHub integration, ICU support | Webhook reliability; revisit branch workflow         |
| **Lokalise**  | Strong API, branching, web designer integration     | Pricing tiers limit collaborators                    |
| **Phrase**    | Robust QA checks, in-context editor                 | Migration is hard once you're in                     |
| **Transifex** | Long-standing, gettext-friendly                     | Slower UI than newer entrants                        |
| **Smartling** | Enterprise MT/TM, MQM scoring                       | Heavy; not ideal for small teams                     |
| **Weblate**   | Open source, self-hostable                          | UI less polished; pull-request flow for translations |
| **POEditor**  | Lightweight, gettext-first                          | Limited QA automation                                |
| **Tolgee**    | Open source, in-context UI, AI suggestions          | Newer; smaller community                             |

### 2.5k. Specific languages — what the AI MUST remember

- **Arabic** — RTL, 6 plural forms, complex ligatures, gender-marked verbs, Eastern Arabic digits opt-in
- **Hebrew** — RTL, 2 plural forms (one/many; sometimes few), gendered second-person ("you")
- **Persian (Farsi)** — RTL, different digits (۰۱۲۳۴۵۶۷۸۹), Jalali calendar default in some apps, Lion-and-Sun flag for Iran (NOT the current state flag) — verify when rendering Iran-specific iconography
- **Russian / Polish / Ukrainian** — 3 plural categories (one/few/many), case-inflected placeholders ("5 минут" / "5 минуты" / "5 минут" depending on count)
- **Japanese** — no plural distinction, no gendered pronouns generally, polite/casual register changes everything, vertical writing in some contexts, no spaces between words (affects truncation algorithms)
- **Chinese** — Simplified (`zh-Hans`, mainland) vs. Traditional (`zh-Hant`, Taiwan / Hong Kong); never auto-convert between them; HK uses Traditional with different vocabulary from TW
- **German** — long compound words; line-breaking via `&shy;` or `<wbr>` for narrow UI; capitalization of all nouns; formal `Sie` vs. informal `du`
- **French** — French Canadian (`fr-CA`) differs from European French (`fr-FR`) in vocabulary, idiom, and OQLF-mandated terminology in Quebec
- **Spanish** — `es-ES` (Spain) vs. `es-419` (Latin America) vs. `es-MX` (Mexico) — `vosotros` (Spain only), `ustedes` (everywhere else), regional vocabulary
- **Portuguese** — `pt-BR` (Brazil) and `pt-PT` (Portugal) diverge significantly; pre-2009 spelling reform legacy still creates friction
- **Korean** — agglutinative; particles attached to nouns make interpolation tricky; honorifics shift verb forms; no plurals required
- **Turkish** — agglutinative; vowel harmony; case suffixes change with the preceding word — placeholder interpolation often needs ICU `select`
- **Thai / Lao / Khmer** — no spaces between words; line-breaking requires dictionary-based segmentation (use `Intl.Segmenter` with `granularity: "word"`)
- **Finnish / Hungarian / Estonian** — 15+ grammatical cases; concatenation is catastrophically wrong; ICU `select` per case
- **Hindi / Bengali / Tamil** — Indic scripts with complex shaping; test fonts on actual devices, not just desktop preview

---

## PHASE 3: BEST PRACTICES (numbered by priority — 1 = highest)

1. **Always use semantic keys** — never English source as the key. The English value lives in the source-locale file like any other translation.
2. **Always use ICU MessageFormat (or framework equivalent) for plurals** — never `count === 1 ? a : b`.
3. **Always include `other`** in every ICU plural / select expression — CLDR requires it.
4. **Always carry a translator comment** on every new string — what / where / length / tone / placeholder values.
5. **Always wrap interpolated content in placeholders**, never concatenate translated fragments.
6. **Always use CSS logical properties** in components that ship to RTL locales — `margin-inline-start`, not `margin-left`.
7. **Always use `Intl.*` APIs** for date / number / currency / list / relative-time formatting.
8. **Always preserve placeholders during translation** — automated CI check; fail the build on placeholder mismatch.
9. **Never machine-translate regulated copy** (medical, legal, financial, safety) without human MQM review.
10. **Never `_zero`/`_one`/`_other` keys alone for Slavic / Arabic / Welsh** — use ICU plural with full CLDR coverage.
11. **Never trust 100 % TM matches blindly** — context may differ; spot-check.
12. **Never strip BOM or normalize encoding** in locale files without an explicit migration; some systems require NFC, others NFD.
13. **Never auto-convert between `zh-Hans` and `zh-Hant`** — vocabulary differs; treat as separate locales.

---

## PHASE 4: REFERENCE FILES (must include)

| File                                          | Content                                                                                        |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `references/i18n-patterns.md`                 | Key naming, namespacing, placeholder syntax, rich-text components, fallback chain              |
| `references/icu-messageformat.md`             | Worked examples of `plural`, `select`, `selectordinal`, nested expressions, gotchas            |
| `references/rtl-checklist.md`                 | Logical properties, mirror/don't-mirror list, `<bdi>` usage, font fallbacks, testing           |
| `references/cldr-plural-coverage.md`          | CLDR categories per language, with example phrases                                             |
| `references/terminology-glossary-template.md` | Per-language termbase format with brand-name + DNT lists                                       |
| `references/locale-fallback.md`               | Region-variant fallback rules with examples                                                    |
| `references/mt-and-ai-policy.md`              | When MT/AI is acceptable, post-editing levels (light / full / forbidden), MQM scoring          |
| `references/cat-tool-integration.md`          | Crowdin / Lokalise / Phrase / Weblate / Tolgee webhook + branch strategies                     |
| `references/lqa-rubric.md`                    | MQM / DQF / SAE J2450 LQA categories + scoring                                                 |
| `references/security-checklist.md`            | Locale-injection (xss in translations), placeholder integrity, BOM/encoding pitfalls           |
| `references/ai-interaction-guide.md`          | What to delegate to AI (draft, scaffolding, lint) vs. keep human (brand voice, regulated copy) |
| `references/common-issues.md`                 | Missing `other` clause, placeholder mismatch, encoding corruption, RTL layout breaks           |
| `references/code-style.md`                    | Repurposed as **string-style.md** — tone, length budgets, brand voice, sentence case           |

---

## PHASE 5: ASSETS

- `assets/locale-file-template.json` — example i18next-style file with namespacing + ICU
- `assets/po-template.pot` — gettext `.pot` skeleton with translator-comment example
- `assets/xliff-template.xlf` — XLIFF 1.2 + 2.x example with `<note>` translator comments
- `assets/string-style-guide.md` — brand-voice + tone-of-voice + length-budget template
- `assets/glossary-template.csv` — `term,en,fr,es,de,ja,zh,ar,fa,...,notes,dnt`
- `assets/lqa-scorecard.md` — MQM-aligned reviewer rubric
- `assets/rtl-testing-checklist.md` — pre-release RTL audit
- `assets/mt-postediting-policy.md` — when MT is permitted, by content type

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md teaches the "no concatenation" rule as Rule #1
- [ ] SKILL.md teaches semantic-key convention (forbid English-as-key)
- [ ] SKILL.md teaches ICU plural with full CLDR category coverage
- [ ] SKILL.md includes the RTL bidi-mirroring do/don't list
- [ ] SKILL.md includes the `Intl.*` reference (DateTimeFormat / NumberFormat / ListFormat / RelativeTimeFormat / Segmenter)
- [ ] SKILL.md includes the MT/AI post-editing policy (light / full / forbidden)
- [ ] SKILL.md includes the locale-fallback chain rules
- [ ] SKILL.md includes the "regulated copy = no MT" boundary
- [ ] At least 10 reference files generated
- [ ] At least 6 asset templates generated
- [ ] Every string template carries a translator comment field

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                   | Why                                                                                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Concatenate translated fragments                        | Word order varies; gender / case agreement breaks                                             |
| Use English source text as the translation key          | Locks source language; every copy edit churns every locale; key naming becomes editorial work |
| Use `count === 1 ? singular : plural` for plurals       | Works for English-family only; Slavic, Arabic, Welsh require multiple plural forms            |
| Forget `other` in an ICU plural / select                | CLDR contract requires it; framework will throw or default badly                              |
| Hard-code dates / numbers / currency without `Intl.*`   | Misformats per locale; misplaces currency symbol; wrong decimal/grouping separator            |
| Mirror media controls (play / FF / RW) in RTL           | Universal media convention is LTR-direction; users get confused                               |
| Mirror logos / screenshots / code blocks in RTL         | They're not direction-bearing; mirroring breaks recognition                                   |
| Auto-convert between `zh-Hans` and `zh-Hant`            | Different vocabulary, different idiom; not a script conversion                                |
| Trust 100 % TM matches without context check            | Same source string may need different translations depending on UI context                    |
| Machine-translate medical / legal / financial copy      | Regulatory + safety risk; mistranslation can harm users                                       |
| Strip `<bdi>` / LRM / RLM bidi-control characters       | Removes correct mixed-script rendering                                                        |
| Use `margin-left: 16px` in components shipped to RTL    | Breaks logical spacing in RTL; use `margin-inline-start: 16px`                                |
| Embed HTML inline in translation strings                | Translators may break tags; use component-aware rich-text APIs                                |
| Ship a locale without populating the missing-key budget | Silent fallback to source masks rollout gaps                                                  |
| Use Wikipedia translations as authoritative             | Volunteer translations vary; use CLDR / official locale data                                  |
| Embed translator notes in production-visible UI         | Reviewer comments and `_comment` keys belong outside the rendered output                      |
| Pluralize via `n + " items"` ternary nesting            | Nesting collapses for languages with > 2 plural categories                                    |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

For translator specifically, when asked for a translation / extraction / review, the AI MUST:

1. Confirm source language + target locale(s) + content domain (UI, marketing, legal, medical)
2. State the plural category set required by each target locale
3. Preserve every placeholder in source order — never reorder without confirming
4. Surface ambiguous source strings rather than guessing (gender of subject, formal/informal register)
5. Mark untranslatable content (brand names, code, command flags) as DNT
6. Flag any string that requires human review (regulated copy, brand voice, idiom)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY localization task — extracting strings, adding a locale, ICU MessageFormat, plural / select / gender, RTL bidi, terminology / glossary, locale fallback, CAT-tool integration, MT post-editing, LQA review, `Intl.*` formatting, key naming, translator comments.

**`allowed-tools`**: `Read Edit Write Glob Grep` (no Bash — translation is text-editing).

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (new locale, ICU plural, RTL audit, terminology, MT review)
2. **Do NOT Use** — cross-references to sibling skills (`frontend` for component refactor, `accessibility` for screen-reader text, `ui-ux-designer` for source-copy rewriting)
3. **Localization Posture** — formats, framework, source lang, target locales detected
4. **Key Convention** — semantic-key rule + namespacing
5. **Plural + Select + Gender** — ICU MessageFormat reference + CLDR plural categories
6. **No-Concatenation Law** — Rule #1; canonical examples
7. **Translator Comments** — what / where / length / tone / placeholders
8. **RTL Bidi** — logical CSS, mirroring rules, mixed-script paragraphs
9. **Locale-Sensitive Formatting** — `Intl.*` reference
10. **Locale Fallback** — region-variant chains, missing-key tracking
11. **TM + Glossary** — when to trust matches, DNT enforcement
12. **MT + AI Post-Editing** — light / full / forbidden + MQM categories
13. **CAT Tool Integration** — sync, webhook, branch strategy
14. **Anti-Patterns** — the `Never` table
15. **References** — CLDR / Unicode / ICU / W3C i18n
16. **Adaptive Interaction Protocols** — localization-specific signals (e.g., "translate this string to fr / es" for Efficient, "what's CLDR" for Teaching, "key collision in production" for Diagnostic), correction accumulation, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**: see PHASE 4 + 5.

`scripts/validate-i18n.sh` — checks placeholder integrity (every placeholder in source appears in every target), ICU syntax validity, missing `other` clause, missing-key budget, BOM/encoding sanity, brand-name DNT compliance.

---

## SUB-AGENT RECOMMENDATIONS

| Agent            | Role                                                                                               | Tools                     | Spawn When                                   |
| ---------------- | -------------------------------------------------------------------------------------------------- | ------------------------- | -------------------------------------------- |
| string-extractor | Scan codebase for hard-coded strings missing from i18n catalog                                     | Read Glob Grep Edit Write | Pre-release sweep, new feature branch, audit |
| i18n-linter      | Read-only — verify placeholder integrity, ICU validity, key parity                                 | Read Glob Grep            | Pre-merge CI check, locale-file PR review    |
| rtl-auditor      | Read-only — find `margin-left`/`right`, non-mirrored icons, BiDi gaps in components shipped to RTL | Read Glob Grep            | Pre-release RTL audit, new component review  |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to `agents/` for full definitions

Add to suggested reference files:

- `agents/string-extractor.md` — hard-coded-string finder agent
- `agents/i18n-linter.md` — read-only locale-file linter
- `agents/rtl-auditor.md` — read-only RTL-readiness auditor

---

## EXECUTION ORDER

```
[ ] 1. Scan project for locale files, i18n framework, key conventions, RTL surface, MT/CAT integrations (Phase 1)
[ ] 2. Synthesize localization posture, key hygiene, RTL readiness, workflow, MT policy (Phase 2)
[ ] 3. Generate SKILL.md with numbered rule lists + Phase 2.5 standards
[ ] 4. Generate INJECT.md (50-150 token quick ref — must include "no concatenation", "semantic keys", "ICU plural with `other`", "logical CSS for RTL")
[ ] 5. Generate LEARNED.md (empty template with section headers)
[ ] 6. Generate the 10+ reference files (Phase 4)
[ ] 7. Generate the 6+ asset templates (Phase 5)
[ ] 8. Generate scripts/validate-i18n.sh
[ ] 9. Generate agents/ files
[ ] 10. Run quality gates (Phase 6)
[ ] 11. Verify all anti-patterns appear in SKILL.md "Never" table (Phase 7)
```

---

## SOURCES

- CLDR — Unicode Common Locale Data Repository ([cldr.unicode.org](https://cldr.unicode.org/))
- Unicode plural rules — [unicode.org/reports/tr35/tr35-numbers.html#Language_Plural_Rules](https://www.unicode.org/reports/tr35/tr35-numbers.html#Language_Plural_Rules)
- ICU MessageFormat — [unicode-org.github.io/icu/userguide/format_parse/messages/](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- W3C Internationalization — [w3.org/International/](https://www.w3.org/International/)
- `Intl.*` MDN — [developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- MQM (Multidimensional Quality Metrics) — [themqm.org](https://themqm.org/)
- DQF (Dynamic Quality Framework) — TAUS ([taus.net](https://www.taus.net/))
- XLIFF 2.x — OASIS standard ([docs.oasis-open.org/xliff/](http://docs.oasis-open.org/xliff/))
- gettext manual — GNU ([gnu.org/software/gettext/](https://www.gnu.org/software/gettext/manual/))
- i18next docs — [i18next.com](https://www.i18next.com/)
- FormatJS / react-intl — [formatjs.io](https://formatjs.io/)
- Mozilla Fluent — [projectfluent.org](https://projectfluent.org/)
- Apple HIG localization — [developer.apple.com/design/human-interface-guidelines/right-to-left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
- Material Design bidirectionality — [m3.material.io/foundations/customization](https://m3.material.io/foundations/customization)
