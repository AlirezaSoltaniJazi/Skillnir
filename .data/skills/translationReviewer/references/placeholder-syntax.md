# Placeholders and markup — syntax per stack and how they break

Rule: compare each translation with the **source-language string** for the same key, never with the key
(gettext msgids are often keys like `therapy.errors.unknown_ids`, not English). Placeholder **count and
names** must match; **order** may change for grammar (positional `%1$s` / named args allow that, bare `%s`
does not).

| Syntax | Used by | Correct in translation | Typical break |
| --- | --- | --- | --- |
| `{{ name }}` | Angular/ngx-translate, Handlebars, i18next (default), Vue (`{name}` in vue-i18n) | identical ASCII name; spaces inside braces don't matter | name translated (`{{dato}}`, `{{ fullständigt namn }}`) → braces shown literally |
| `{name}`, `{0}` | ICU MessageFormat, Python `str.format`, .NET, Java `MessageFormat`, Flutter ARB | identical name/index | `KeyError`/`IndexError` (Python), literal braces (ICU) |
| `{n, plural, one {…} other {…}}` | ICU (FormatJS, Angular i18n, ARB, Lokalise ICU) | keywords `plural`/`select`/`one`/`other` untranslated; `#` kept; braces balanced; `other` present | translated keyword (`{n, pluriel, …}`), missing `other` → runtime error |
| `%(name)s`, `%(n)d` | Python %-format, Django gettext | same names, same conversion | dropped (info lost silently: `%` with a dict and no specifiers returns the string unchanged), renamed → `KeyError` |
| `%s`, `%d`, `%.1f` | Python, C, PHP, gettext `c-format` | same count, same order | added/removed → `TypeError: not enough arguments` |
| `%1$s`, `%2$d` | Android, Java `String.format`, PHP | same indices; reordering OK | index changed/duplicated |
| `%@`, `%lld`, `%1$@` | iOS/macOS `.strings`, `String(format:)` | same | `%@` dropped → crash or wrong value |
| `%{name}` | Ruby i18n, some custom loaders | same | |
| `${name}` | JS template-like loaders, Lokalise "universal" | same | |
| `<b>`, `<a href="…">`, `<br/>`, `<0>…</0>` | HTML in strings, React `Trans` components | same tags (count + nesting); `href` may be localized (localized PDF/legal URL) | dropped `</a>` breaks layout; injected attributes = XSS risk; `<0>` index changed |
| `\n`, `\t`, `&nbsp;` | everywhere | same line-break count unless the layout allows | lost line break in a multi-paragraph email/legal text |

## Percent signs

- In a string that is %-formatted, a literal percent must be `%%`. `"100% dziennie"` parses `% d` as a
  space-flagged `%d` → `TypeError`/`ValueError` at runtime.
- In a string that is **never** %-formatted (plain label `Typ/%/Ca++`), `%` is fine. Check the call site
  before flagging; Django `{% blocktrans %}` and `gettext()` + `%` are formatted, a plain `{% trans %}` is not.
- Android: `%` in a `<string>` passed to `getString(id, args)` must be `%%`; with `formatted="false"` it is
  literal.

## ICU specifics reviewers miss

- Apostrophe is the ICU escape: `'{'` is a literal brace; `''` is an apostrophe. French/Italian
  apostrophes (`l'heure`) are fine only when not adjacent to `{`/`}`; `'{count}'` stops being a placeholder.
- `select` keys (`male`, `female`, `other`) are code values — never translated.
- `selectordinal` categories differ from cardinal ones (en: one/two/few/other for 1st/2nd/3rd/4th).

## Placeholders that should not exist

- **Added where the source has none** (`"ago"` → `"منذ %s"`): renders a literal `%s` or breaks formatting.
- **Value hard-coded instead of the placeholder** (`%(days)s` → "7 days", "five (5)"): correct only until
  the config changes. Treat as an ERROR in legal/medical/obligation text.
- **Number-like text changed** ("6-digit code" → "3-cijferige code"): not a placeholder, still a bug —
  digits in the source should normally survive into the translation.
- **Example values** (phone `+44 7700 900123`): may be localized, must stay a valid pattern, must not be
  a real number.

## Brand and do-not-translate terms

Keep product names, device names and units exactly as in the source (`brandix`, `FlowKit X`, `mmHg`,
`Ca++`). Case changes count (`Brandix`). Inflection in agglutinative languages is expected and correct
(fi `brandixissa`, `ERP:ssä`; hu, et similar). Medical acronyms may be localized when that is the
standard term in the language (PD → pl `DO`, fr/es/pt `DP`; APD → fr `DPA`; CAPD → fr `DPCA`, pl `CADO`).
