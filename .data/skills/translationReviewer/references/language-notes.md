# Language notes — the 15 languages

What a non-native reviewer can still catch per language. Number/date facts are in
[locale-formats.md](locale-formats.md), plurals in [plurals.md](plurals.md). Confirm terminology against
the project glossary in LEARNED.md before flagging a word choice; flag *inconsistency* with confidence,
flag *wrong word* as "confirm with a native reviewer".

## Cross-language checks (do these first, they need no fluency)

1. **Same screen, same term.** The title, subtitle and button of one view must use one word for one
   concept (fr "clinique" title + "centre" subtitle is a bug even if both words are fine).
2. **Bulk find-and-replace damage.** When a term changes across a file (clinique → centre, recepta →
   przepis, clinica → centro), check: sentence-initial capitals (`centre créée…`), gender agreement of
   articles/adjectives/participles (`ce centre … enregistrée`, `questa centro`), and leftovers of the old
   term. `check_catalogs.py` prints a TERM SHIFTS summary and `case-regression` findings for this.
3. **Status labels share gender with their noun.** Badges like Active/Expired/Approved describe one noun
   (prescription, order). In gendered languages all labels of one set must agree with that noun, and a
   dialog that names the status ("will change to Inactive") must use the exact badge text.
4. **Formality is consistent** within the product (below).
5. **Not machine-literal.** Calques of English UI idioms ("Are you sure?", "Oops!", "Hit the button") or a
   wrong word sense (fi "Uusi" = *new* for "Renew"; "Supply details" → "Delivery details") are findings.

## Per language

| Lang | Address form (typical B2B/health UI) | Capitalization | Punctuation & typography | Traps |
| --- | --- | --- | --- | --- |
| **de** | *Sie* (formal); never mix with *du* | all nouns capitalized; title case not used beyond nouns | „…“ quotes; no space before `!?:`; ordinal dot `7.`; `z. B.` | compound nouns written as one word or hyphenated (`Admin-Portal`), never split (`Admin Portal`); verb at end makes truncation obvious |
| **fr** | *vous* | sentence case; months/days lowercase | **NBSP before `; : ! ?` and inside « »** (`Erreur !`); `n°`; decimal comma | gender agreement after term swaps; `0` is singular; `e-mail`/`courriel` consistency; avoid anglicisms in legal text |
| **it** | *Lei* or impersonal/infinitive in UI; product-consistent | sentence case; months lowercase | «» or “”; apostrophe elision (`l'ordine`, `un'ora`) | gender of articles after term swaps (`questo centro`); `Inattivo/a` style slashes are a smell |
| **es** | *usted* (Spain B2B); *tú* only if the product chose it | sentence case; months lowercase | **`¿…?` and `¡…!` opening marks required**; «» | es_ES vs es_419 vocabulary (`ordenador`/`computadora`); gender of status labels |
| **pt** (pt_PT) | *você* can sound impolite in pt_PT formal text — prefer impersonal or 3rd person (`Pode criar…`) | sentence case; months lowercase | «» | **pt_BR leakage**: `tela`→`ecrã`, `arquivo`→`ficheiro`, `usuário`→`utilizador`, `cadastro`→`registo`, gerund `está fazendo`→`está a fazer` |
| **nl** | *u* (formal) | sentence case | `‘…’`/`“…”`; `OK` (not `Oké`) on buttons | **compounds written as one word** (`zorgverlenersportaal`, not `zorgverleners portaal`); `-ie`/`-ië` plurals |
| **sv** | *du* (standard even in B2B) | sentence case; months lowercase | ”…”; space before `%` (`25 %`) | compounds one word (`patientkort`); ISO dates `2026-03-07` |
| **da** | *du* | sentence case; months lowercase | ordinal dot `7.`; time `14.05` | compounds; `Download` is accepted Danish |
| **nb** | *du* | sentence case | «» | Bokmål only — Nynorsk forms (`ikkje`, `eg`) are wrong; locale dir may be `nb` vs legacy `no` (check which one the app serves) |
| **fi** | passive / imperative without pronoun | sentence case | ”…”; time `14.05`; `kt`/`Mt` for KB/MB is valid | 15 cases: brand/abbreviation inflection with colon (`ERP:ssä`, `brandixissa`) is **correct**; placeholders inside inflected words need a neutral phrasing; ambiguous verbs (`Uusi` new/renew) |
| **cs** | *vy* (formal plural, capital *Vy* only in letters) | sentence case; months lowercase | „…“; dates `7. 3. 2026`; NBSP after one-letter prepositions (`v`, `k`, `s`, `z`, `o`, `u`) | 7 cases + gender: placeholders like `{{name}}` force awkward case; 3 plural forms |
| **pl** | *Pan/Pani* is rare in UI — impersonal/infinitive (`Wybierz`, `Kliknij`) or *ty* imperative | sentence case; months lowercase; language names lowercase mid-sentence (`hiszpański`), capitalize as standalone labels | „…”; NBSP after one-letter conjunctions | 7 cases, 3 genders: term swaps of different gender break agreement; `recepta` (drug prescription) vs `przepis` (recipe/regulation) vs `zlecenie`; plural 3rd form = *many* |
| **el** | *εσείς* (formal plural) | sentence case; **no accents on all-caps text** (`ΕΙΣΟΔΟΣ`, not `ΕΊΣΟΔΟΣ`); final sigma `ς` | **question mark is `;`**; «»; decimal comma | `κατ' εξαίρεση` = "exceptionally", not "exception (setting)"; 12-hour clock `μ.μ.` |
| **ar** | formal MSA; masculine generic is common but must be consistent | no case | **RTL**: `؟` `،` `؛`; Latin digits or Arabic-Indic per locale | see RTL below; gender agreement of verbs/adjectives with feminine nouns (الوصفة); dual forms |
| **en** (source) | — | sentence case unless the product uses title case | — | source bugs propagate: typos (`prescrbed`), "for" vs "by", `day(s)` constructs that can't be translated; report them to the source owner |

## RTL (Arabic) checks

- Placeholders and tags stay whole and in logical order in the file (`{{date}}`, `<b>…</b>`); the renderer
  reorders visually. A placeholder split by RTL marks or reversed (`}}date{{`) is broken.
- Mixed-direction values (IDs, emails, phone numbers, `brandix`, units) need bidi isolation in the UI
  (`<bdi>`, `dir="auto"`, `⁨…⁩`). A string that hard-codes LRM/RLM marks is a smell — check it
  renders.
- Mirrored glyphs: `<`, `>`, `≤`, `≥`, `(`, `)`, arrows are mirrored by the renderer; do not "correct" them
  in the file. Ranges written `5–10` stay in that logical order.
- Punctuation: Arabic comma `،`, semicolon `؛`, question mark `؟`. A Latin `?` at the end of an Arabic
  sentence is a typo.
- Latin-digit vs Arabic-Indic digits: never mixed within one screen; follow the product decision.
- Icons with direction (back/forward chevrons, progress) are a UI concern — note them if the PR touches
  layout strings.

## Healthcare / regulated text (extra scrutiny)

- Dosage, volumes, units and thresholds: digits, decimal marks and units must survive exactly.
- Consent, legal, privacy and obligation notes: no hard-coded values, no dropped sentences, same number of
  paragraphs/line breaks, links point to the localized document.
- Alarm/alert/caution texts: severity words stay distinct (alarm ≠ alert ≠ caution ≠ warning) and match the
  device's official localization if one exists.
- Push notifications and emails: also check the *loader* — an empty value may be sent as an empty
  notification rather than falling back (see [consumption-and-fallback.md](consumption-and-fallback.md)).
