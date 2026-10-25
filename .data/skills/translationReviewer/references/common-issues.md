# Common issues — real failures and how they were caught

Each entry: pattern → example → detection. Use these as search heuristics on any translation PR.

| # | Pattern | Example | How to catch |
| --- | --- | --- | --- |
| 1 | Placeholder name translated | da `{{dato}}`, sv `{{ fullständigt namn }}` for `{{ fullName }}` | checker `placeholder` |
| 2 | Placeholder dropped | pl "Nieznane identyfikatory roztworów DO:" lost `%(ids)s` | checker `placeholder`; string ends with `:` |
| 3 | Placeholder invented | ar "ago" → "منذ %s" | checker `placeholder` (unexpected) |
| 4 | Config value hard-coded | `%(days)s` → "7 days" / "five (5)" in an invitation and an obligation note | checker `number` (hard-codes) |
| 5 | Meaningful digit changed | nl "6-digit code" → "3-cijferige code"; it phone example "+39----------" | checker `number` (numbers differ) |
| 6 | Bulk term swap broke grammar | fr clinique→centre: "centre créée", "le centre existante", "auxquelles"; it "questa centro" | TERM SHIFTS + `case-regression`; grep new term with feminine markers |
| 7 | Bulk swap broke capitals | fr sidebar "centres", errors starting "une prescription…" | `case-regression`, `case` |
| 8 | Same screen, two terms | fr title "Aucune clinique trouvée" + subtitle "Aucun centre à afficher" | read keys of one view together (`--grep`) |
| 9 | Status set mixes genders | es Activo/Caducado vs Aprobada/Rechazada; dialog says "Inactiva", badge "Inactivo" | read the whole `status.*` group side by side |
| 10 | Wrong word sense | "Supply details" → de "Lieferdetails" (delivery); fi "Uusi" for Renew (= New); el "κατ' εξαίρεση" for exception setting | content read; compare with existing term for the same concept |
| 11 | Calque / wrong domain term | pl "przepis" (recipe/regulation) for prescription | glossary in LEARNED.md; native reviewer |
| 12 | Compound split | nl "zorgverleners portaal" | nl/de/sv/da/nb/fi: two nouns with a space |
| 13 | Brand casing | "Brandix" for "brandix" | checker `do-not-translate` with `--keep` |
| 14 | Plural silently dropped by tooling | ar/cs/pl 0 of 4 report plurals; converter skips partial plurals | checker `plural-missing`; read converter |
| 15 | Plural forms mis-mapped | pl msgstr[2] filled from CLDR `other` (fractions) | [plurals.md](plurals.md) |
| 16 | Dead copy, live file empty | push texts added to `.po`, code reads per-app JSON → 10 languages `""` → blank push | checker `not-in-source`; grep the key in code; test the loader |
| 17 | Hand edit to pass a test | "Cliniques" → "centres" in one catalog to match the other | commits after the export touching non-source catalogs |
| 18 | Missing counterpart branch | release PR with no master PR; tooling change only on release | `gh pr list --search <ticket>`; diff branches |
| 19 | Stale test, not stale translation | "untranslated language falls back" test used a language that got translated | read failing test intent before "fixing" strings |
| 20 | Unserved locale dir | fixes only in `locale/no/` while Django serves `nb` | `LANGUAGES` / loader config |
| 21 | Truncation | strings ending in `:` or mid-sentence; length < 40% of source | checker `truncation`, `length` |
| 22 | Whitespace | leading space in a flag name, double spaces, trailing spaces | checker `whitespace` |
| 23 | Separator lost | pl "%(count)s zabiegów  %(unreviewed)s…" dropped "·" | double space between placeholders |
| 24 | Source-language bug | "prescrbed", "updated **for** Customer Service" | read the English of changed keys too |
| 25 | Scope creep | "clinic list" PR shipping 100+ unrelated keys | compare description with changed key prefixes |
