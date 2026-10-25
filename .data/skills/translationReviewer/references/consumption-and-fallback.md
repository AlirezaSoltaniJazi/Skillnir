# Consumption and fallback — what the user actually sees

A translation file is only correct if the code reads it. Before calling a finding harmless ("falls back to
English"), confirm the loader really falls back. Behaviour differs per library and per config, so verify
with a one-line test instead of assuming.

## Questions for every changed catalog

1. **Is this file read at all?** Grep the key in code. Find the loader (`LOCALE_PATHS`, `i18n.load_path`,
   `TranslateHttpLoader`, `i18next-resources-to-backend`, Android `res/`, iOS bundle). A key added to a
   catalog the code never reads is dead; the real catalog may still be empty.
2. **Which locale directory is served?** Django serves the codes in `LANGUAGES` (`nb`, not `no`);
   web apps map `nb` → `no_NO.json` or similar. Fixes that land only in an unserved directory do nothing.
3. **Missing key vs empty value.** These are different code paths:

| Stack | Missing key | Empty string value | Verify with |
| --- | --- | --- | --- |
| Django / GNU gettext | msgid returned (source text if msgids are English, **raw key** if msgids are keys and the `en` catalog lacks it) | empty `msgstr` = untranslated → msgid / `LANGUAGE_CODE` catalog | `python manage.py shell -c "from django.utils import translation as t; t.activate('de'); print(t.gettext('key'))"` |
| gettext fuzzy entries | — | `#, fuzzy` entries are ignored at runtime (compiled out) | `msgfmt --statistics` |
| python-i18n (`i18n.t`) | fallback locale, then `default=`, then key | **returns `''`** — the `default` is not used | `i18n.add_translation('k','',locale='de'); i18n.t('k',locale='de',default='X')` |
| ngx-translate | `MissingTranslationHandler` / default lang / key | check `TranslateService` config — empty may render empty | render the component in that language |
| i18next | fallbackLng → key | `returnEmptyString` (default **true** in most versions) returns `''` | `i18next.t('k', {lng:'de'})` |
| vue-i18n / FormatJS | fallback locale / `defaultMessage` | library- and config-dependent | one test per project |
| Android | default `values/` | empty string shown | lint `MissingTranslation`, run in locale |
| iOS `.strings` | key (or the `value:` argument) — no per-key fallback to the development language | empty string shown | run with `-AppleLanguages (de)` |

4. **Compiled artefacts.** gettext needs `.mo` regenerated for every `.po` change; Android/iOS bundles and
   web builds need a rebuild. A `.po` change without its `.mo` ships nothing.
5. **Placeholder contract at the call site.** Read one call site per changed placeholder string: which
   arguments are passed (`%` with a dict vs tuple, `{{ }}` params object), and whether the string is
   formatted at all (decides if a literal `%` is a bug).
6. **Caching.** Some loaders cache translations at startup (`i18n.load_path` scanned once, CDN-cached JSON);
   a translation fix may need a deploy or cache bust.

## Patterns found in real reviews

- Translations added to a gettext catalog while the feature reads a per-app JSON that the export script
  never writes → 10 languages kept `""` → blank push notification title/body (python-i18n returns `''`).
- Keys present in non-English `.po` files but absent from the English catalog → the English UI shows the raw
  key unless another loader provides it.
- A test asserting "untranslated language falls back to English" broke when the language got translated;
  the fix (switch the test to an unsupported language) was right — the test, not the translation, was stale.
- A consistency test failed because the same key had two values in two catalogs; the "fix" hand-edited one
  catalog to match the broken one. Fix at the source (Lokalise/Crowdin) instead.
