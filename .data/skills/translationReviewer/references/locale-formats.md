# Locale formats — numbers, dates, times, currency, lists

Source: Unicode CLDR via Babel 2.18 (`scripts/locale_facts.py`). Re-run it for any locale not listed —
never write a separator or date order from memory. Sample values: number `1234567.891`, percent `0.25`,
currency `1234.5` in the territory's currency, date **7 March 2026** (`2026-03-07`), time **14:05**.

Coverage: the 15 UI languages of a typical EU product (en, de, it, nl, fr, pt, es, fi, cs, nb, sv, da, el,
pl, ar) plus the regional variants that change formatting: de_AT/de_CH, it_CH, nl_BE, fr_BE/fr_CH, en_US,
ar_AE/ar_SA/ar_EG.

| Locale | Decimal | Group | 1234567.891 | 25% | Currency | Short date | Medium date | Time | Week starts |
|---|---|---|---|---|---|---|---|---|---|
| `en_GB` | `.` | , | `1,234,567.891` | `25%` | `£1,234.50` | `07/03/2026` | `7 Mar 2026` | `14:05` | Mon |
| `en_US` | `.` | , | `1,234,567.891` | `25%` | `$1,234.50` | `3/7/26` | `Mar 7, 2026` | `2:05 PM` | Sun |
| `de_DE` | `,` | . | `1.234.567,891` | `25 %` | `1.234,50 €` | `07.03.26` | `07.03.2026` | `14:05` | Mon |
| `de_AT` | `,` | . | `1.234.567,891` | `25 %` | `€ 1.234,50` | `07.03.26` | `07.03.2026` | `14:05` | Mon |
| `de_CH` | `.` | ’ (U+2019) | `1’234’567.891` | `25%` | `CHF 1’234.50` | `07.03.26` | `07.03.2026` | `14:05` | Mon |
| `it_IT` | `,` | . | `1.234.567,891` | `25%` | `1.234,50 €` | `07/03/26` | `7 mar 2026` | `14:05` | Mon |
| `it_CH` | `.` | ’ (U+2019) | `1’234’567.891` | `25%` | `CHF 1’234.50` | `07.03.26` | `7 mar 2026` | `14:05` | Mon |
| `nl_NL` | `,` | . | `1.234.567,891` | `25%` | `€ 1.234,50` | `07-03-2026` | `7 mrt 2026` | `14:05` | Mon |
| `nl_BE` | `,` | . | `1.234.567,891` | `25%` | `€ 1.234,50` | `7/03/2026` | `7 mrt 2026` | `14:05` | Mon |
| `fr_FR` | `,` | NNBSP | `1 234 567,891` | `25 %` | `1 234,50 €` | `07/03/2026` | `7 mars 2026` | `14:05` | Mon |
| `fr_BE` | `,` | NNBSP | `1 234 567,891` | `25 %` | `1 234,50 €` | `7/03/26` | `7 mars 2026` | `14:05` | Mon |
| `fr_CH` | `,` | NNBSP | `1 234 567,891` | `25%` | `1 234,50 CHF` | `07.03.26` | `7 mars 2026` | `14:05` | Mon |
| `pt_PT` | `,` | NBSP | `1 234 567,891` | `25%` | `1 234,50 €` | `07/03/26` | `07/03/2026` | `14:05` | Sun |
| `es_ES` | `,` | . | `1.234.567,891` | `25 %` | `1.234,50 €` | `7/3/26` | `7 mar 2026` | `14:05` | Mon |
| `fi_FI` | `,` | NBSP | `1 234 567,891` | `25 %` | `1 234,50 €` | `7.3.2026` | `7.3.2026` | `14.05` | Mon |
| `cs_CZ` | `,` | NBSP | `1 234 567,891` | `25 %` | `1 234,50 Kč` | `07.03.26` | `7. 3. 2026` | `14:05` | Mon |
| `nb_NO` | `,` | NBSP | `1 234 567,891` | `25 %` | `1 234,50 kr` | `07.03.2026` | `7. mars 2026` | `14:05` | Mon |
| `sv_SE` | `,` | NBSP | `1 234 567,891` | `25 %` | `1 234,50 kr` | `2026-03-07` | `7 mars 2026` | `14:05` | Mon |
| `da_DK` | `,` | . | `1.234.567,891` | `25 %` | `1.234,50 kr.` | `07.03.2026` | `7. mar. 2026` | `14.05` | Mon |
| `el_GR` | `,` | . | `1.234.567,891` | `25%` | `1.234,50 €` | `7/3/26` | `7 Μαρ 2026` | `2:05 μ.μ.` | Mon |
| `pl_PL` | `,` | NBSP | `1 234 567,891` | `25%` | `1 234,50 zł` | `7.03.2026` | `7 mar 2026` | `14:05` | Mon |
| `ar` | `.` | , | `1,234,567.891` | `25%` | `‏1,234.50 €` | `7‏/3‏/2026` | `07‏/03‏/2026` | `2:05 م` | Mon |
| `ar_AE` | `.` | , | `1,234,567.891` | `25%` | `‏1,234.50 د.إ.‏` | `7‏/3‏/2026` | `07‏/03‏/2026` | `2:05 م` | Mon |
| `ar_SA` | `٫` | ٬ | `1٬234٬567٫891` | `25%` | `‏1٬234٫50 ر.س.‏` | `7‏/3‏/2026` | `07‏/03‏/2026` | `2:05 م` | Sun |
| `ar_EG` | `٫` | ٬ | `1٬234٬567٫891` | `25%` | `‏1٬234٫50 ج.م.‏` | `7‏/3‏/2026` | `07‏/03‏/2026` | `2:05 م` | Sat |

NBSP = U+00A0 no-break space, NNBSP = U+202F narrow no-break space. Arabic rows contain U+200F (RLM)
marks around separators; they are part of the CLDR pattern. ar_SA / ar_EG default to Arabic-Indic digits
(`٠١٢٣٤٥٦٧٨٩`, decimal `٫`, group `٬`); Babel prints Latin digits with Arabic separators, ICU (browsers,
Android, iOS) prints the Arabic-Indic digits. Plain `ar` and `ar_AE` default to Latin digits.

## What a reviewer looks for in strings

A translation string must not **contain** a formatted number, date or currency. Values are
formatted by code (`Intl`, Babel, `java.text`, `NSFormatter`, Django `localize`) and injected through a
placeholder. Flag every one of these:

| Smell in a translation | Why it is wrong | Fix |
| --- | --- | --- |
| `1,000.5`, `5.5L` in de/fr/pl/… (comma-decimal locales) | wrong decimal mark for the reader | placeholder + locale-aware formatter; for fixed UI ranges write the localized form (`5,5 l`) |
| `1.000` meaning one thousand in en, or `1,000` meaning one in de | 1000× misreading — dosage, volumes, money | never hard-code; placeholder |
| A hard-coded date `03/07/2026` / `07.03.2026` | DMY vs MDY vs YMD (sv `2026-03-07`) | placeholder with a date formatter |
| `%(days)s` replaced by `7` / "five (5)" | text is right only until config changes | keep the placeholder |
| `€ 10` vs `10 €` written in the string | currency position is locale data (de `10 €`, nl/de_AT `€ 10`) | format currency in code |
| `25%` vs `25 %` | de, fr, es, fi, cs, nb, sv, da put a space (fr: NNBSP) | format percent in code; if literal, match the table |
| `2:05 PM` in a 24-hour locale | only en_US, el, ar default to 12-hour clock | time formatter |
| Month/day names typed into a string | capitalization and case forms differ (below) | date formatter |

## Date-specific traps

- **Order**: DMY almost everywhere in the EU; **MDY** en_US; **YMD** sv (`2026-03-07`), also ISO.
- **Separators**: `/` (en_GB, fr, it, es, pt, el, ar), `.` (de, cs, nb, da, fi, pl, de_CH, fr_CH), `-` (nl_NL).
  cs medium date has spaces: `7. 3. 2026`. fi time uses a dot: `14.05`; da time too: `14.05`.
- **Ordinal dot**: de/da/nb/cs/fi write `7.` for the day (`7. März 2026`). Dropping it is a typo.
- **Genitive months**: "7 March" vs "March 2026" use different word forms in pl (`7 marca` / `marzec 2026`),
  cs (`7. března` / `březen 2026`), fi (`7. maaliskuuta` / `maaliskuu 2026`), el (`7 Μαρτίου` / `Μάρτιος 2026`).
  A string that glues `{{day}} {{monthName}}` from a nominative month list is wrong in these languages.
- **Capitalization**: month and weekday names are lowercase in fr, es, it, pt, nl, sv, da, nb, fi, pl, cs;
  capitalized in en, de (nouns), el. A sentence-initial weekday is capitalized only by sentence rules.
- **Prepositions**: es/pt use `de` (`7 de marzo de 2026`); "on 7 March" becomes `am 7. März` (de), `le 7 mars`
  (fr), `il 7 marzo` (it), `op 7 maart` (nl). A translation without the preposition before `{{date}}` is
  usually missing it ("Demande expirée {{date}}" → "expirée le {{date}}").
- **Week start**: Monday everywhere here except en_US / pt_PT / ar_SA (Sunday) and ar_EG (Saturday).
  Calendar widgets must take it from the locale, not from a translation string.
- **Time zones**: a string must not say "CET" / "GMT"; zone names are locale data.

## Numbers, units, phone numbers

- Space between number and unit: `5 ml`, `10 kg`, `37,5 °C` in all listed languages (en too, except `%`,
  `°`). Unit symbols are not translated (`ml`/`mL`, `kg`, `mmHg`, `mmol/l`); some locales prefer lowercase `l`
  for litre (de/nl/sv/da/nb/fi/cs/pl/fr/es) and `L` (en, it, pt, el). Keep the project's choice consistent.
- Ranges: en `5–10`, many locales prefer `5–10` with an en dash; never a hyphen-minus in medical ranges if
  the house style says en dash. `≤`/`≥` are bidi-mirrored in Arabic (correct; do not "fix" them).
- Example phone numbers in placeholders may be localized (`+30` for el), but must stay a valid pattern
  (`+39----------` is broken) and must not be a real person's number.
- Thousands separator `’` (U+2019) for de_CH/it_CH; fr_CH uses NNBSP; a plain apostrophe `'` is a common
  hand-typed mistake.

## Lists, quotes, names, addresses

- Lists: `A, B and C` (en_GB, no Oxford comma) vs `A, B, and C` (en_US); every other locale here joins the
  last pair with its own conjunction and no comma (`und`, `et`, `e`, `y`, `en`, `ja`, `a`, `og`, `och`,
  `και`, `i`, `و`). Never build a list by `", ".join` plus an English "and".
- Quotation marks (house-style dependent; CLDR primary forms): de/cs `„…“`, pl `„…”`, da varies (`»…«`, `„…“`, `“…”`), fr `« … »` (with
  NBSP inside), it/es/pt/el/nb/de_CH `«…»`, nl/en `“…”` / `‘…’`, sv/fi `”…”`, ar `”…“` (RTL).
- Personal names: family-name-first and name order differ; `{{firstName}} {{lastName}}` hard-coded in a
  string is a smell — prefer one `{{fullName}}` formatted by code.
- Postal codes and addresses differ per country (NL `1234 AB`, PT `1234-567`, CZ `123 45`, PL `12-345`,
  GB alphanumeric); a translation must not hard-code an example address format into validation text.
