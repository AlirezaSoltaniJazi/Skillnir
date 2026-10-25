# Translation PR review checklist (full)

Work top to bottom; sections 1–4 are mostly mechanical (`scripts/check_catalogs.py`), 5–9 need judgment.
Severity: **ERROR** = broken at runtime / wrong information / legal-medical risk · **WARN** = visible
quality bug · **INFO** = context. Tag every finding **NEW** (this PR) or **OLD** (already on base).

## 0. Scope and context
- [ ] Base branch, head SHA, merged/open, CI status (read failing test names — translation PRs break tests
      that hard-code strings or fallbacks).
- [ ] Counterpart PRs: master ↔ release backport/forward-port exists and carries the same content
      (`git diff <prA> <prB> -- '*.po' '*.json'`), including later fix commits.
- [ ] What else the PR touches: tooling (export/import scripts), tests, code. Non-catalog files get a code
      review of their own.
- [ ] Hand edits: commits after the export that touch non-source-language catalogs. Each one must also be
      fixed in the TMS (Lokalise/Crowdin/Phrase) or the next export reverts it.
- [ ] Description matches content (a "clinic list" PR shipping 100 unrelated keys is a scope finding).

## 1. File integrity
- [ ] JSON/ARB valid, no duplicate keys (last wins silently), newline at EOF, same nesting as source.
- [ ] `.po`: `msgfmt -c` clean (header-field warnings are noise); `.mo` recompiled for every changed `.po`;
      no `#, fuzzy` entries that should be live.
- [ ] Android XML well-formed, apostrophes escaped (`\'`), `formatted="false"` where needed.
- [ ] iOS `.strings` every line ends `;`, quotes escaped.
- [ ] No keys missing from the source-language file (typos/renames never render); no source keys deleted.

## 2. Placeholders and markup — [placeholder-syntax.md](placeholder-syntax.md)
- [ ] Count and names identical to the source string (not the key).
- [ ] Nothing translated inside placeholders; no placeholder added, dropped or replaced by a literal value.
- [ ] Literal `%` escaped in %-formatted strings; ICU braces balanced, `other` present, keywords untouched.
- [ ] Same HTML tags; links localized only on purpose; no new attributes.

## 3. Plurals — [plurals.md](plurals.md)
- [ ] `msgstr[n]` count == `nplurals`; every source plural exists in every language.
- [ ] Converter maps categories correctly (pl 3rd form = `many`); partial plurals are not silently dropped.

## 4. Regressions vs base
- [ ] No value that was translated is now empty, English, or removed.
- [ ] No string that started uppercase now starts lowercase (bulk replace).
- [ ] TERM SHIFTS summary reviewed: every systematic word swap is intended and applied consistently.

## 5. Consumption — [consumption-and-fallback.md](consumption-and-fallback.md)
- [ ] Every new key is read by code from **this** catalog; dead copies identified.
- [ ] Empty values: confirm the loader falls back (python-i18n and i18next may return `''`).
- [ ] Served locale directories only (`nb` vs `no`, `pt_PT` vs `pt`).
- [ ] Untranslated keys (still empty) listed once as INFO with the user-visible effect.

## 6. Locale formatting — [locale-formats.md](locale-formats.md)
- [ ] No hard-coded numbers/dates/currency/percent in strings; any literal one matches the locale table.
- [ ] Digits that carry meaning survive (6-digit code, 5 minutes, ≤5.5 L) and are not silently changed.
- [ ] Month/day names, prepositions before dates, 24-hour time, week start.

## 7. Content — [language-notes.md](language-notes.md)
- [ ] German in full (most reviewable), plus 2–3 more languages on the changed strings
      (`scripts/dump_side_by_side.py`); for big PRs, delegate per language group to `language-reviewer`.
- [ ] Meaning matches the source, especially errors, dosage/units, consent/legal, alerts, push/email.
- [ ] Same term for the same concept on one screen and across platforms (web vs server vs app).
- [ ] Gender/number agreement, status-label sets consistent, formality consistent.
- [ ] Brands/units/device names unchanged (case too); accepted inflection (fi) is fine.
- [ ] Punctuation per language (fr NBSP, es ¿¡, el `;`, ar `؟`), no truncation, no double/trailing spaces.
- [ ] RTL: placeholders/tags intact, no stray bidi marks, Arabic punctuation.
- [ ] Source-language bugs (typos, "for" vs "by", untranslatable `day(s)`) reported to the source owner.

## 8. Tooling changes in the same PR
- [ ] Read import/export script diffs like production code: what they skip, overwrite, or drop silently;
      form/category mapping tables; which directories they write (and which they miss).
- [ ] Tests exist for new tooling behaviour; run the tool on the export if available and diff the output.

## 9. Report — [report-template.md](report-template.md)
- [ ] NEW issues inline (key, language, source text, current text, user-visible effect, fix).
- [ ] OLD issues once in the summary or as a follow-up ticket.
- [ ] Every content fix also goes to the TMS; say so explicitly.
