---
name: promptCompressor
description: >-
  Rule-based prompt compression skill. Reduces token usage by 30-50% through
  deterministic removal of articles, auxiliaries, intensifiers, and filler phrases
  while preserving meaning, technical terms, JSON templates, code blocks, and URLs.
  Activates when compressing prompts, optimizing token usage, reducing API costs,
  or working with the compressor module.
compatibility: "Python 3.14+, no external dependencies"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: stable
allowed-tools: Read Edit Write Glob Grep Bash
---

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections and conventions from previous sessions.

**Announce skill usage.** Always say "Using: promptCompressor skill" at the very start of your response.

## When to Use

1. Working on `src/skillnir/compressor.py` — the core compression module
2. Debugging or improving compression rules (word sets, phrase replacements)
3. Analyzing compression ratios on pipeline prompts
4. Adding new protected zone patterns
5. Working on the compression toggle in settings
6. Reviewing whether compressed prompts preserve meaning

## Do NOT Use

- **General Python backend** — use [backendEngineer](../backendEngineer/SKILL.md)
- **UI/settings page layout** — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **CI/CD and pre-commit** — use [devopsEngineer](../devopsEngineer/SKILL.md)

## Architecture

```
src/skillnir/compressor.py          # Core module — compress_prompt()
src/skillnir/backends.py            # Integration — build_subprocess_command()
src/skillnir/ui/pages/settings.py   # Toggle — compress_prompts config
tests/test_compressor.py            # 38+ unit tests
```

**Data flow**: Pipeline prompt string -> `build_subprocess_command()` -> `compress_prompt()` -> compressed string -> CLI subprocess

**Integration point**: Single function `build_subprocess_command()` in `backends.py`. Compression is applied transparently when `compress_prompts=True` in `AppConfig`.

## Compression Algorithm

Applied in order:

1. **Detect protected zones** — code blocks, inline code, JSON templates, URLs, file paths, markdown headers
2. **Replace verbose phrases** — "in order to" -> "to", "due to the fact that" -> "because" (~30 pairs)
3. **Remove stop words** — articles, auxiliaries, intensifiers, fillers (outside protected zones)
4. **Collapse whitespace** — normalize spaces and blank lines

## Compression Rules

### ALWAYS REMOVE

| Category     | Words                                                                                              |
| ------------ | -------------------------------------------------------------------------------------------------- |
| Articles     | a, an, the                                                                                         |
| Auxiliaries  | is, are, was, were, am, be, been, being, have, has, had, do, does, did                             |
| Intensifiers | very, quite, rather, somewhat, really, extremely, essentially, particularly, especially            |
| Fillers      | currently, basically, actually, simply, just, certainly, definitely, obviously, clearly, literally |

### ALWAYS KEEP

| Category              | Words                                 |
| --------------------- | ------------------------------------- |
| Negations             | not, no, never, without, nor, neither |
| Uncertainty           | may, might, could, seems, appears     |
| Critical prepositions | from, with, must                      |
| All numbers           | 42, 3.14, 200K, 1M                    |
| Technical terms       | any domain-specific vocabulary        |
| URLs                  | https://...                           |
| Code blocks           | `...`                                 |
| JSON templates        | {{ ... }}                             |

### PROTECTED ZONES (never modified)

| Zone             | Pattern                         |
| ---------------- | ------------------------------- |
| Code blocks      | ` ``` ... ``` `                 |
| Inline code      | `` `...` ``                     |
| JSON templates   | `{{ ... }}` and `{{{{ ... }}}}` |
| URLs             | `https://...`                   |
| File paths       | `/path/to/file`                 |
| Markdown headers | `## Header`                     |

## Key Patterns

| Pattern            | Approach                                   | Key Rule                     |
| ------------------ | ------------------------------------------ | ---------------------------- |
| Protected zones    | Regex detection -> `list[tuple[int, int]]` | Detect before any transforms |
| Phrase replacement | `re.sub` with `re.IGNORECASE`              | Apply before word removal    |
| Word removal       | `\b` word-boundary regex                   | Never match partial words    |
| Word sets          | `frozenset` constants                      | O(1) lookup, module-level    |
| Result type        | `CompressionResult` dataclass              | Includes metrics             |
| Config toggle      | `AppConfig.compress_prompts`               | `~/.skillnir/config.json`    |

## Code Style

| Rule           | Convention                                                               |
| -------------- | ------------------------------------------------------------------------ |
| Formatter      | Black -S (double quotes)                                                 |
| Type hints     | `str`, `list[tuple[int, int]]`, `frozenset[str]`                         |
| Imports        | Absolute only — `from skillnir.compressor import compress_prompt`        |
| Constants      | `_ARTICLES`, `_AUXILIARIES` — module-level frozensets                    |
| Result pattern | `CompressionResult` dataclass with metrics                               |
| Testing        | `pytest`, class-based, `TestProtectedZones`, `TestWordCompression`, etc. |

## Anti-Patterns

| Anti-Pattern                          | Why It's Wrong                                               |
| ------------------------------------- | ------------------------------------------------------------ |
| Removing words inside code blocks     | Corrupts code — always check protected zones first           |
| Partial word matches                  | "a" in "data" — must use `\b` word boundaries                |
| Removing negations                    | "not working" becomes "working" — opposite meaning           |
| Phrase replacement after word removal | "in order to" breaks if "in" removed first                   |
| Compressing user input (ask/plan)     | Users chose their exact words — only compress system prompts |
| External dependencies (spaCy/nltk)    | Must be pure Python, <100ms, no installs                     |

## Code Generation Rules

1. **Read before writing** — always read `compressor.py` and tests before changes
2. **Test every rule** — each word set and phrase pair needs a test case
3. **Word boundaries** — always use `\b` in regex for word matching
4. **Protected zones first** — detect zones before any compression transforms
5. **On correction** — acknowledge, restate as rule, write to LEARNED.md

## References

| File                                                                       | Description                                  |
| -------------------------------------------------------------------------- | -------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                   | Auto-updated corrections and preferences     |
| [INJECT.md](INJECT.md)                                                     | Always-loaded quick reference                |
| [references/compression-rules.md](references/compression-rules.md)         | Full rule catalog with before/after examples |
| [references/protected-zones-guide.md](references/protected-zones-guide.md) | Protected zone detection details             |
