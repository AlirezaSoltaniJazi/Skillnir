# Report template

Audience: developers who merge the PR and translators/TMS owners who fix strings. Lead with the verdict,
then blocking items, then what to fix in the TMS. Every finding is self-contained so it can be pasted into
a PR comment or ticket.

## Summary block

```markdown
**Verdict:** <Ready to merge | Fix N issues before merge | Merged — N follow-ups in Lokalise>
**Scope:** <N files, N languages, N changed strings (N previously empty)>, base <branch>, head <sha>
**Checker:** <N NEW ERROR · N NEW WARN · N OLD> (`check_catalogs.py --base … --head …`)
**Passed:** <JSON/msgfmt/.mo · no regressions · placeholders · plurals · German read in full>
```

## One finding

```markdown
### <n>. <Plain-language problem, not the check name>  — <ERROR|WARN> · <NEW|OLD> · <langs>
| Key | Source (en) | Current | Should be |
|---|---|---|---|
| `therapy.errors.unknown_ids` | Unknown IDs: %(ids)s | Nieznane identyfikatory: | Nieznane identyfikatory: %(ids)s |

**Effect:** <what the user sees, where (screen, email, push, PDF), for whom>.
**Fix:** <in the TMS / in code / in the export script>. <Why the TMS matters if the repo is generated.>
```

Rules:
- One row per key; group identical problems across languages in one finding with a table.
- Quote strings exactly; mark RTL cells with `dir="rtl"` in HTML reports.
- Say how a claim was verified when it is not obvious ("checked: python-i18n returns `''` for empty").
- Don't pad with "consider"; give the corrected string when you are confident, "confirm with a native
  reviewer" when you are not.

## Severity guide

| ERROR | WARN | INFO |
| --- | --- | --- |
| placeholder dropped/added/renamed, invalid JSON, duplicate keys, `.mo` stale, stray `%`, ICU broken, translated string emptied, blank push/email, wrong digits in medical/OTP text, missing master/release counterpart | wrong term, gender/case agreement, lowercase sentence start, inconsistent term on one screen, brand casing, wrong punctuation, untranslated plural (renders source), hand edit not in TMS | still-empty strings, keys absent in a language, dead keys, legacy locale dirs, scope notes |

## PR comment (short form)

```markdown
**<lang>** `<key>`: <current> → <fix>. <Effect in one sentence.> (Fix in <TMS> too, or the next export reverts it.)
```

## Artifact / shareable page

For large reviews, publish a page with: header pills (state, base, counts), tally strip, "What passed",
blocking issues, TMS fixes, minor notes, context (OLD), next steps, footer with SHAs compared. Keep the
same structure across reviews so readers can compare PRs.
