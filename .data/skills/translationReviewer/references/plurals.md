# Plurals

Three systems meet in a review: **CLDR categories** (ICU MessageFormat, i18next, Android `quantity`,
iOS `.stringsdict`, Lokalise/Crowdin exports), **gettext forms** (`msgstr[n]`, ordered by the
`Plural-Forms` formula), and the **tooling** that converts one into the other. Most plural bugs live in
the conversion.

## The 15 languages

CLDR integer categories (fraction-only and compact-number categories omitted) and the gettext header
used in practice (Django / GNU defaults; check the actual `.po` header — it wins).

| Lang | CLDR categories that matter for integers | gettext `Plural-Forms` in common use | msgstr order |
| --- | --- | --- | --- |
| en, de, nl, sv, da, nb, fi, el, it, es, pt | one, other | `nplurals=2; plural=(n != 1);` | one, other |
| fr | one (0 **and** 1), other | `nplurals=2; plural=(n > 1);` | one, other |
| cs | one, few (2–4), other | `nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;` | one, few, other |
| pl | one, few (2–4, 22–24…), **many** (0, 5–21, 25…) | `nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 \|\| n%100>=20) ? 1 : 2);` | one, few, **many** |
| ar | zero, one, two, few (3–10), many (11–99), other | `nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);` | zero, one, two, few, many, other |

Notes:
- CLDR also has `many` for fr/it/es/pt (exact millions: "1 million **de** …") and `many` for cs (fractions).
  Babel's `to_gettext()` therefore emits nplurals=3/4 for those — do **not** copy that into `.po` headers.
- **pl gotcha**: gettext's 3rd Polish form is CLDR `many` (5 zabiegów), not CLDR `other` (fractions,
  1,5 zabiegu). A converter mapping `[one, few, other]` → `msgstr[0..2]` for pl is a bug. cs is the reverse:
  its 3rd form *is* CLDR `other`.
- **fr gotcha**: 0 is singular ("0 jour"). An English-style `n == 1` check in code gives "0 jours".
- **ar**: every Arabic plural needs all 6 forms; tools that skip a plural when any form is empty drop
  Arabic first. The forms differ in noun number and case (dual for 2, plural for 3–10, singular for 11–99
  and 100+), so identical text in all six forms is a finding — ask a native reviewer.
- **pt_PT vs pt_BR**: same plural rules; different vocabulary (`ecrã`/`tela`, `ficheiro`/`arquivo`,
  `utilizador`/`usuário`). A pt_PT file with Brazilian terms is a content finding.

## What to check

- [ ] Count of `msgstr[n]` == `nplurals` in that file's header (`msgfmt -c` fails; at runtime a form is missing).
- [ ] Every plural in the source exists in every language. A missing plural silently renders the source
      language (gettext/Django) or the key.
- [ ] Each form keeps the count placeholder (`%(count)s`, `{count}`, `#` in ICU) — except where the
      language writes the word for 1 ("jeden"/"one") on purpose, and only in the `one` form.
- [ ] ICU: every `plural`/`select` has an `other` branch; categories are valid for the language (`few` in
      German is dead text; `one` with `=1` duplicates are fine).
- [ ] Android: `<plurals>` items use `zero|one|two|few|many|other`; `zero` only fires for languages whose
      CLDR rules have it (ar) — English `zero` is never selected.
- [ ] No plural built by string concatenation in the source (`count + " day(s)"`): flag it to the
      developers; translators can't fix it. `%(days)s day(s)` in English is acceptable only if the
      translations don't have to inflect — Slavic and Arabic do. Polish "%(days)s dni" is wrong for 1.
- [ ] Tooling that writes plurals (export → `.po`/JSON converters): read its form-mapping table and what it
      does with a partial plural (skip? copy `other`? fail?). Silent skip is the worst option.

## Quick test

```bash
# gettext: which form does n pick?
python3 -c "import gettext;t=gettext.GNUTranslations(open('django.mo','rb'));print([t.ngettext('x.singular','x.plural',n) for n in (0,1,2,5,22,25,101)])"
# CLDR category for n in a language
python3 -c "from babel import Locale;l=Locale.parse('pl');print({n:l.plural_form(n) for n in (0,1,2,5,12,22,25,1.5)})"
```
