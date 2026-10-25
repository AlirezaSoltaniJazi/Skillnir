# Authoritative Model Sources

**Rule: never answer a model question from memory.** Model IDs are exact strings and the
lineup changes every few months. A remembered ID is the most common way a broken model
reaches the picker.

## Claude (Anthropic) — canonical

The models-overview doc carries the full current table (ID, alias, tier, context, pricing,
retirement date) for every platform.

| What                      | URL                                                                              |
| ------------------------- | -------------------------------------------------------------------------------- |
| Models overview (primary) | `https://platform.claude.com/docs/en/about-claude/models/overview.md`            |
| Model deprecations        | `https://platform.claude.com/docs/en/about-claude/model-deprecations`            |
| Model IDs & versioning    | `https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions` |
| Pricing                   | `https://platform.claude.com/docs/en/about-claude/pricing`                       |

Fetch it with WebFetch and ask for the exact ID strings:

```
WebFetch(
  url="https://platform.claude.com/docs/en/about-claude/models/overview.md",
  prompt="List every current/active Claude model with its exact API model ID string, "
         "display name and tier. Also list legacy/deprecated models with IDs. "
         "Output exact ID strings — do not paraphrase."
)
```

Read from the table:

- **Claude API ID** — what goes in `ModelInfo(id=...)`
- **Claude API alias** — for pre-4.6 models this is a pointer to a dated ID; from 4.6 on the
  dateless ID _is_ its own pinned snapshot and the alias row just repeats it
- **Legacy models (still available)** — keep these listed with versioned aliases; do not delete

If a `claude-agent-sdk` / `claude-api` reference skill is available in the session, it carries a
cached copy of the same table — still prefer the live doc, and treat the cache as a cross-check.

### Live capability lookup (optional)

The Models API returns `max_input_tokens`, `max_tokens` and a `capabilities` object per model:

```python
import anthropic
client = anthropic.Anthropic()
for m in client.models.list():
    print(m.id, m.display_name, m.max_input_tokens, m.max_tokens)
```

Needs a working API key; the docs table is enough for registry edits.

## Cursor

```bash
cursor-agent --list-models    # authoritative for this account
cursor-agent --version
```

If it prints `No models available for this account.` the account has no model access — the
list is **unverifiable**. Record that in LEARNED.md and leave the Cursor entries untouched.

## Gemini

The Gemini CLI has no model-list subcommand (`--list-extensions` / `--list-sessions` exist, not
models). Check Google's model docs for current `gemini-*` IDs.

```bash
gemini --version
gemini --help | grep -i model     # shows -m/--model only
```

## Copilot

`copilot help config` prints the exact `model` IDs this CLI version accepts — no login
needed. IDs use **dotted** versions (`claude-opus-4.8`, not `claude-opus-4-8`). If the CLI
isn't installed, run it through npx without installing:

```bash
npx -y @github/copilot@latest help config   # look for the `model` list
npx -y @github/copilot@latest --version
copilot                                     # interactive alternative: type /model
```

The GitHub docs page (`docs.github.com/en/copilot/reference/ai-models/supported-models`)
lists display names only, and can include models the CLI doesn't offer yet — the CLI list wins.

## Recording the outcome

After every check, append to LEARNED.md which sources were reachable and which were not —
account state and provider tiers differ per machine and change over time.
